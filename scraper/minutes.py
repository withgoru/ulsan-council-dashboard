"""CLIK 회의록 상세(MINTS_HTML) 파싱 → minutes / speech_segments.

이 프로젝트의 핵심: "의원이 실제로 회의장에서 한 말"을 발언자별로 저장한다.

MINTS_HTML 구조(ENDPOINTS.md/검증):
- `div.contents-block.speaker-block`: 한 발언. `<strong>` 안에 역할(○의장/○경제부시장…)과,
  의원이면 `<a class="member_profile">이름</a>`. 그 뒤 텍스트(<br/> 구분)가 발언 내용.
- `strong.item-in-contents`: 의사일정 항목 헤더. 문서 순서상 speaker-block 사이에 위치 →
  직전 항목을 그 발언의 agenda_item 으로 태깅.

의원 매칭은 CLIK 자체 코드(data-member_code)가 아니라 이름(members 로스터)으로 한다.
매칭 실패(시청 공무원 등)는 member_id=NULL.

실행: uv run python -m minutes  (또는 python minutes.py)
"""
from __future__ import annotations

import re
import sqlite3
from datetime import date
from typing import Any

from bs4 import BeautifulSoup, Tag

import config
import db
from clik_client import ClikClient
from members import load_name_index, match_member_id

_WS_RE = re.compile(r"\s+")


def clean(text: str) -> str:
    return _WS_RE.sub(" ", (text or "").replace("\xa0", " ")).strip()


def _mtg_date(mtg_de: str | None) -> str | None:
    """'20260720' → '2026-07-20'."""
    if not mtg_de or len(mtg_de) != 8 or not mtg_de.isdigit():
        return None
    try:
        return date(int(mtg_de[:4]), int(mtg_de[4:6]), int(mtg_de[6:])).isoformat()
    except ValueError:
        return None


def _parse_speaker(strong: Tag) -> tuple[str | None, str | None]:
    """<strong> → (역할, 이름). 의원은 a.member_profile 이름 우선."""
    a = strong.find("a", class_="member_profile")
    if a is not None:
        name = clean(a.get_text())
        role = clean(strong.get_text().replace(a.get_text(), "")).lstrip("○ ").strip()
        return (role or None), (name or None)
    raw = clean(strong.get_text()).lstrip("○ ").strip()
    if not raw:
        return None, None
    # 비의원: '경제부시장 신민식' → 마지막 토큰을 이름으로, 앞을 역할로.
    parts = raw.rsplit(" ", 1)
    if len(parts) == 2 and parts[1]:
        return parts[0], parts[1]
    return raw, None  # 역할만 있고 이름 없음


def _speech_text(block: Tag) -> str:
    """speaker-block 에서 strong/hr 을 제거하고 남은 발언 텍스트."""
    clone = BeautifulSoup(str(block), "lxml")
    for tag in clone.find_all(["strong", "hr"]):
        tag.extract()
    return clean(clone.get_text(" "))


def parse_segments(html: str) -> list[dict[str, Any]]:
    """MINTS_HTML → 발언 세그먼트 리스트(seq/역할/이름/의사일정/텍스트)."""
    soup = BeautifulSoup(html, "lxml")
    nodes = soup.select("div.speaker-block, strong.item-in-contents")
    current_item: str | None = None
    segments: list[dict[str, Any]] = []
    seq = 0
    for node in nodes:
        classes = node.get("class") or []
        if "item-in-contents" in classes:
            raw = clean(node.get("title") or node.get_text())
            # CLIK 는 번호 없는 항목 앞에 불릿 '0' 을 붙인다('0신임…', '0 5분자유발언…').
            # 실제 번호 항목은 '1.','2.' 로 시작하므로 선행 '0' 하나만 제거.
            current_item = re.sub(r"^0\s*", "", raw) or None
            continue
        strong = node.find("strong")
        if strong is None:
            continue
        role, name = _parse_speaker(strong)
        text = _speech_text(node)
        if not text:
            continue
        segments.append({
            "seq": seq,
            "speaker_role": role,
            "speaker_name": name,
            "agenda_item": current_item,
            "text": text,
        })
        seq += 1
    return segments


def _insert_minutes(conn: sqlite3.Connection, meta: dict[str, Any], detail: dict[str, Any]) -> int:
    cur = conn.execute(
        """INSERT INTO minutes
           (clik_docid, term, session_no, round_no, meeting_type, meeting_date,
            agenda_summary, raw_html)
           VALUES (:clik_docid, :term, :session_no, :round_no, :meeting_type,
                   :meeting_date, :agenda_summary, :raw_html)
           ON CONFLICT(clik_docid) DO UPDATE SET
             term=excluded.term, session_no=excluded.session_no,
             round_no=excluded.round_no, meeting_type=excluded.meeting_type,
             meeting_date=excluded.meeting_date, agenda_summary=excluded.agenda_summary,
             raw_html=excluded.raw_html""",
        {
            "clik_docid": meta["DOCID"],
            "term": int(meta.get("RASMBLY_NUMPR") or config.TERM),
            "session_no": meta.get("RASMBLY_SESN"),
            "round_no": meta.get("MINTS_ODR"),
            "meeting_type": meta.get("MTGNM") or "본회의",
            "meeting_date": _mtg_date(meta.get("MTG_DE")),
            "agenda_summary": clean(detail.get("MTR_SJ", "")) or None,
            "raw_html": detail.get("MINTS_HTML"),
        },
    )
    row = conn.execute(
        "SELECT id FROM minutes WHERE clik_docid = ?", (meta["DOCID"],)
    ).fetchone()
    return row["id"]


def scrape(conn: sqlite3.Connection, client: ClikClient,
           name_index: dict[str, int]) -> tuple[int, int]:
    """새 회의록만 상세 조회·파싱·저장. (신규 회의록 수, 신규 발언 세그먼트 수) 반환."""
    new_minutes = 0
    new_segments = 0
    for meta in client.iter_term_minutes():
        docid = meta["DOCID"]
        if db.exists(conn, "minutes", clik_docid=docid):
            continue  # 이미 수집 → 상세 재조회 생략(멱등)
        detail = client.fetch_detail(docid)
        minutes_id = _insert_minutes(conn, meta, detail)
        for seg in parse_segments(detail.get("MINTS_HTML", "")):
            member_id = match_member_id(name_index, seg["speaker_name"])
            db.upsert(
                conn, "speech_segments",
                {
                    "minutes_id": minutes_id,
                    "seq": seg["seq"],
                    "speaker_role": seg["speaker_role"],
                    "speaker_name": seg["speaker_name"],
                    "member_id": member_id,
                    "agenda_item": seg["agenda_item"],
                    "text": seg["text"],
                },
                conflict=["minutes_id", "seq"],
                update=["speaker_role", "speaker_name", "member_id", "agenda_item", "text"],
            )
            new_segments += 1
        conn.commit()
        new_minutes += 1
    return new_minutes, new_segments


if __name__ == "__main__":
    with db.session() as conn, ClikClient() as client:
        name_index = load_name_index(conn)
        log_id = db.start_log(conn, "minutes")
        try:
            nm, ns = scrape(conn, client, name_index)
            db.finish_log(conn, log_id, new_rows=nm)
            print(f"[minutes] 신규 회의록 {nm}건, 발언 세그먼트 {ns}개")
            print(f"   minutes total: {db.count_rows(conn, 'minutes')}, "
                  f"speech_segments total: {db.count_rows(conn, 'speech_segments')}")
            matched = conn.execute(
                "SELECT COUNT(*) t, COUNT(member_id) m FROM speech_segments"
            ).fetchone()
            print(f"   발언자 member 매칭: {matched['m']}/{matched['t']}")
        except Exception as exc:  # noqa: BLE001
            db.finish_log(conn, log_id, new_rows=0, status="error", error_msg=str(exc))
            raise
