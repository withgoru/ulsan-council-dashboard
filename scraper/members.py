"""의원명단 수집 — 로스터(viewByPerson.do) + 프로필 상세(profile.do) → members 테이블.

이후 모든 스크래퍼(게시판/의안/CLIK 발언)가 쓰는 이름→member_id 매칭 캐시의 기반.
로스터가 22명뿐이라 이름 매칭은 정확 일치만 사용한다(퍼지 매칭은 오히려 위험).

실행:  uv run python members.py
"""
from __future__ import annotations

import re
import sqlite3
from typing import Any

from bs4 import BeautifulSoup, Tag

import config
import db
from http_client import EgovBoardClient

_MEMCODE_RE = re.compile(r"memCode=([0-9A-Za-z]+)")
_WS_RE = re.compile(r"\s+")
# 긴 접미사를 먼저 매칭해야 '부위원장'이 '위원장'으로 오분리되지 않는다.
_ROLE_SUFFIXES = ("부위원장", "부의장", "위원장", "의장", "간사", "위원")


def _clean(text: str) -> str:
    """연속 공백/개행을 단일 공백으로 접는다(카드 HTML에 탭·개행이 많음)."""
    return _WS_RE.sub(" ", text).strip()


def normalize_name(name: str) -> str:
    """이름 매칭 키 정규화: 모든 공백 제거."""
    return _WS_RE.sub("", name)


def _parse_committee(raw: str) -> str:
    """'의회운영 위원장' 같은 항목을 '의회운영(위원장)'으로 정리."""
    text = _clean(raw)
    for suf in _ROLE_SUFFIXES:
        if text.endswith(suf):
            name = text[: -len(suf)].strip()
            return f"{name}({suf})" if name else suf
    return text


def parse_roster(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """로스터 페이지에서 22명 카드 파싱 → memCode/이름/정당/선거구/위원회/사진."""
    members: list[dict[str, Any]] = []
    for btn in soup.select("a.btn-profile"):
        m = _MEMCODE_RE.search(btn.get("onclick", ""))
        if not m:
            continue
        member_code = m.group(1)
        card = btn.find_parent("li")
        if not isinstance(card, Tag):
            continue

        name_el = card.select_one(".name")
        img = card.find("img")
        name = _clean(name_el.get_text()) if name_el else (
            _clean(img.get("alt", "")) if img else ""
        )

        items = [ _clean(li.get_text()) for li in card.select("ul.etc_list > li") ]
        district = items[0] if len(items) > 0 else None
        party = items[1] if len(items) > 1 else None
        committees = [_parse_committee(li.get_text()) for li in card.select("ul.etc_list > li")[2:]]
        committee = " · ".join(c for c in committees if c) or None

        photo_url = None
        if img and img.get("src"):
            src = img["src"]
            photo_url = src if src.startswith("http") else f"{config.COUNCIL_BASE}{src}"

        members.append({
            "member_code": member_code,
            "name": name,
            "party": party,
            "district": district,
            "committee": committee,
            "photo_url": photo_url,
        })
    return members


def _profile_url(member_code: str) -> str:
    return (f"{config.COUNCIL_BASE}{config.MEMBER_PROFILE_PATH}"
            f"?city={config.MEMBER_PROFILE_CITY}&daesu={config.TERM}&memCode={member_code}")


def parse_profile(soup: BeautifulSoup) -> dict[str, Any]:
    """프로필 상세(dt/dd 또는 th/td)에서 출생연도/정당/선거구/연락처/약력 추출.

    데스크톱·모바일 중복 렌더링이라 같은 라벨이 여러 번 나오면 첫 값만 취한다.
    """
    fields: dict[str, str] = {}
    for row in soup.find_all(["tr", "div", "li"]):
        label_el = row.find(["th", "dt"])
        value_el = row.find(["td", "dd"])
        if label_el and value_el:
            label = _clean(label_el.get_text())
            value = _clean(value_el.get_text())
            if label and value and label not in fields:
                fields[label] = value

    def pick(*labels: str) -> str | None:
        for lab in labels:
            for key, val in fields.items():
                if lab in key:
                    return val
        return None

    birth_raw = pick("출생", "생년")
    birth_year = None
    if birth_raw:
        bm = re.search(r"(\d{4})", birth_raw)
        birth_year = int(bm.group(1)) if bm else None

    bio_raw = pick("약력", "경력", "주요경력")

    return {
        "party": pick("소속정당", "정당"),
        "district": pick("선거구"),
        "birth_year": birth_year,
        "phone": pick("핸드폰", "휴대폰", "연락처", "전화"),
        "email": pick("이메일", "메일"),
        "bio": bio_raw,
    }


def scrape(conn: sqlite3.Connection, client: EgovBoardClient) -> int:
    """로스터+프로필을 수집해 members 에 upsert. 신규로 삽입된 의원 수 반환."""
    roster_soup = client.get_soup(config.MEMBERS_PATH)
    roster = parse_roster(roster_soup)

    new_count = 0
    for base in roster:
        code = base["member_code"]
        profile = client.get_soup(
            config.MEMBER_PROFILE_PATH,
            params={"city": config.MEMBER_PROFILE_CITY, "daesu": config.TERM, "memCode": code},
        )
        detail = parse_profile(profile)

        row = {
            "member_code": code,
            "term": config.TERM,
            "name": base["name"],
            # 프로필의 정당/선거구가 더 상세(동 목록 포함) → 있으면 우선, 없으면 로스터값.
            "party": detail["party"] or base["party"],
            "district": detail["district"] or base["district"],
            "committee": base["committee"],
            "birth_year": detail["birth_year"],
            "phone": detail["phone"],
            "email": detail["email"],
            "bio": detail["bio"],
            "profile_url": _profile_url(code),
            "photo_url": base["photo_url"],
        }
        existed = db.exists(conn, "members", member_code=code, term=config.TERM)
        db.upsert(
            conn, "members", row,
            conflict=["member_code", "term"],
            # first_seen_at 은 최초 삽입값 유지. last_seen_at 은 excluded 기본값
            # (INSERT 후보행의 CURRENT_TIMESTAMP)으로 갱신되어 매 실행마다 갱신된다.
            update=["name", "party", "district", "committee", "birth_year",
                    "phone", "email", "bio", "profile_url", "photo_url", "last_seen_at"],
        )
        if not existed:
            new_count += 1
    conn.commit()
    return new_count


def load_name_index(conn: sqlite3.Connection, term: int = config.TERM) -> dict[str, int]:
    """이름(정규화)→member_id 매칭 캐시. 다른 스크래퍼가 발언자/발의자 매칭에 사용."""
    rows = conn.execute(
        "SELECT id, name FROM members WHERE term = ?", (term,)
    ).fetchall()
    return {normalize_name(r["name"]): r["id"] for r in rows}


def match_member_id(name_index: dict[str, int], name: str | None) -> int | None:
    """이름으로 member_id 조회(정확 일치). 실패 시 None(비의원 발언 등)."""
    if not name:
        return None
    return name_index.get(normalize_name(name))


if __name__ == "__main__":
    with db.session() as conn, EgovBoardClient() as client:
        log_id = db.start_log(conn, "members")
        try:
            n = scrape(conn, client)
            db.finish_log(conn, log_id, new_rows=n)
            print(f"new members: {n}. total in DB: {db.count_rows(conn, 'members')}")
            print("\nname → member_id index:")
            for name, mid in sorted(load_name_index(conn).items(), key=lambda x: x[1]):
                print(f"  {mid:>3d}  {name}")
        except Exception as exc:  # noqa: BLE001
            db.finish_log(conn, log_id, new_rows=0, status="error", error_msg=str(exc))
            raise
