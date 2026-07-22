"""익명 게시판(eGovFrame) 공통 파서 + 페이지네이션 러너.

council.ulsan.kr 의 `selectBoardList.do` 계열 게시판은 목록 표 구조가 동일해
(caption + thead 헤더 + tbody 행), 여기서 헤더→셀 딕셔너리로 파싱하는 공통 로직을 둔다.
각 보드 모듈은 BoardSpec 을 정의하고 run_board() 로 실행한다.

대수(9) 필터/중단 규칙은 보드마다 다르므로(ENDPOINTS.md 3절) classify 콜백으로 주입한다.
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Callable

from bs4 import BeautifulSoup, Tag

import config
import db
from http_client import EgovBoardClient, article_url

_WS_RE = re.compile(r"\s+")
_NTTID_RE = re.compile(r"nttId=(\d+)")
# 제목의 "제265회 ... 제4차" → 회기/차수
_SESSION_RE = re.compile(r"제?\s*(\d+)\s*회.*?제?\s*(\d+)\s*차")


def clean(text: str) -> str:
    return _WS_RE.sub(" ", text or "").strip()


def cell_text(td: Tag) -> str:
    """td 값 추출: span.tds 우선, 없으면 add-head 라벨 제거 후 텍스트."""
    tds = td.select_one("span.tds")
    if tds is not None:
        return clean(tds.get_text())
    ah = td.select_one("span.add-head")
    if ah is not None:
        ah.extract()
    return clean(td.get_text())


def to_int(text: str | None) -> int | None:
    """'1,032' 같은 숫자 텍스트 → int. 실패 시 None."""
    if not text:
        return None
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else None


def parse_date(text: str | None) -> str | None:
    """'2026-07-20' → ISO date 문자열. 파싱 실패 시 None."""
    if not text:
        return None
    m = re.search(r"(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})", text)
    if not m:
        return None
    y, mo, d = (int(g) for g in m.groups())
    try:
        return date(y, mo, d).isoformat()
    except ValueError:
        return None


def parse_session_round(title: str | None) -> str | None:
    """'제265회 ... 제4차 본회의 결과' → '265회 4차'."""
    if not title:
        return None
    m = _SESSION_RE.search(title)
    return f"{m.group(1)}회 {m.group(2)}차" if m else None


def parse_list_rows(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """게시판 목록 표를 [{헤더: 값, ..., _ntt_id, _source_url}] 로 파싱.

    잘못된 bbsId(예: JS alert 리다이렉트)면 표가 없으므로 빈 리스트를 반환한다.
    """
    table = soup.find("table")
    if table is None:
        return []
    thead = table.find("thead")
    headers = [clean(th.get_text()) for th in (thead.find_all("th") if thead else table.find_all("th"))]
    body = table.find("tbody") or table
    rows: list[dict[str, Any]] = []
    for tr in body.find_all("tr"):
        tds = tr.find_all("td")
        if not tds:
            continue
        rec: dict[str, Any] = dict(zip(headers, (cell_text(td) for td in tds)))
        link = tr.find("a", href=lambda h: h and "selectBoardArticle" in h)
        if link is not None:
            m = _NTTID_RE.search(link["href"])
            rec["_ntt_id"] = m.group(1) if m else None
        rows.append(rec)
    return rows


class Verdict(Enum):
    KEEP = "keep"   # 저장 대상(9대)
    SKIP = "skip"   # 이 행은 건너뛰되 페이지네이션은 계속
    STOP = "stop"   # 대수/날짜 경계 → 이 행부터 이후 전부 중단


@dataclass
class BoardSpec:
    """익명 게시판 스크랩 명세."""
    name: str                                   # scrape_log 용 이름
    bbs_id: str
    table: str
    # (파싱행 rec) → Verdict. 대수/날짜 필터·중단 규칙.
    classify: Callable[[dict[str, Any]], Verdict]
    # (rec, name_index) → DB 행 dict. bbs_id/ntt_id/source_url 은 러너가 채워줌.
    to_record: Callable[[dict[str, Any], dict[str, int]], dict[str, Any]]
    conflict: tuple[str, ...] = ("bbs_id", "ntt_id")
    update_cols: list[str] | None = None        # None이면 conflict/first_seen_at 제외 전부
    max_pages: int = 50


def run_board(
    conn: sqlite3.Connection,
    client: EgovBoardClient,
    spec: BoardSpec,
    name_index: dict[str, int],
) -> int:
    """spec 에 따라 페이지네이션하며 upsert. 신규 저장 행 수를 반환.

    중단 조건: (1) classify 가 STOP 을 준 행을 만남, (2) 빈 페이지,
    (3) 한 페이지의 KEEP 행이 전부 기존 행(신규 0)일 때 — 재실행 시 조기 종료.
    """
    total_new = 0
    for page in range(1, spec.max_pages + 1):
        soup = client.board_list(spec.bbs_id, page=page)
        rows = parse_list_rows(soup)
        if not rows:
            break

        stop = False
        kept = 0
        page_new = 0
        for rec in rows:
            verdict = spec.classify(rec)
            if verdict is Verdict.STOP:
                stop = True
                break
            if verdict is Verdict.SKIP:
                continue
            kept += 1
            ntt_id = rec.get("_ntt_id")
            if not ntt_id:
                continue
            record = spec.to_record(rec, name_index)
            record.setdefault("bbs_id", spec.bbs_id)
            record.setdefault("ntt_id", ntt_id)
            record.setdefault("source_url", article_url(spec.bbs_id, ntt_id))
            existed = db.exists(conn, spec.table, bbs_id=spec.bbs_id, ntt_id=ntt_id)
            db.upsert(conn, spec.table, record,
                      conflict=list(spec.conflict), update=spec.update_cols)
            if not existed:
                page_new += 1
        conn.commit()
        total_new += page_new

        if stop:
            break
        # 재실행 조기 종료: 이 페이지에 유지 대상은 있었으나 전부 기존 행이면 이후도 기존.
        if kept > 0 and page_new == 0:
            break
    return total_new


def run_as_script(spec: BoardSpec) -> None:
    """모듈 단독 실행 진입점: uv run python -m boards.<name>."""
    from members import load_name_index

    with db.session() as conn, EgovBoardClient() as client:
        name_index = load_name_index(conn)
        log_id = db.start_log(conn, spec.name)
        try:
            n = run_board(conn, client, spec, name_index)
            db.finish_log(conn, log_id, new_rows=n)
            print(f"[{spec.name}] new rows: {n} | table '{spec.table}' total: "
                  f"{db.count_rows(conn, spec.table)}")
        except Exception as exc:  # noqa: BLE001
            db.finish_log(conn, log_id, new_rows=0, status="error", error_msg=str(exc))
            raise
