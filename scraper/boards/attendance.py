"""의원별 회의출석률(attendanceStatistics.do) → attendance_records.

POST 폼(sDaesu=대수, sCate=1 전반기/2 후반기). 표는 2행 헤더:
  [번호, 의원명, 본회의, 상임위원회(colspan)] / [운영위, 행자위, ...]
colspan>1 인 그룹헤더(상임위원회)를 제외한 leaf 헤더가 데이터 컬럼과 1:1 대응한다.
셀 값 'N/M (P%)' 를 attended/total/pct 로 분해. 빈 셀(비소속 위원회)은 건너뛴다.

실행: uv run python -m boards.attendance
"""
from __future__ import annotations

import re
import sqlite3
from typing import Any

from bs4 import BeautifulSoup

import config
import db
from http_client import EgovBoardClient
from members import load_name_index, match_member_id

from .base import cell_text, clean

# 'N/M (P%)' 또는 'N/M' 형태
_RATE_RE = re.compile(r"(\d+)\s*/\s*(\d+)(?:\s*\(([\d.]+)%?\))?")
_UPDATE_COLS = ["member_id", "member_name", "attended", "total", "pct", "last_seen_at"]


def _leaf_headers(table) -> list[str]:
    """colspan>1 그룹헤더를 제외한 leaf 컬럼 헤더(문서 순서)."""
    thead = table.find("thead")
    ths = thead.find_all("th") if thead else table.find_all("th")
    return [clean(th.get_text()) for th in ths if int(th.get("colspan", 1)) == 1]


def _parse_rate(text: str) -> tuple[int, int, float] | None:
    m = _RATE_RE.search(text or "")
    if not m:
        return None
    attended, total = int(m.group(1)), int(m.group(2))
    pct = float(m.group(3)) if m.group(3) else (
        round(attended / total * 100, 1) if total else 0.0
    )
    return attended, total, pct


def parse_table(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """(의원명, 회의종류, attended, total, pct) 레코드들로 분해."""
    table = soup.find("table")
    if table is None:
        return []
    headers = _leaf_headers(table)
    # 앞 두 컬럼(번호, 의원명)을 제외한 나머지가 회의종류.
    meeting_cols = headers[2:]
    body = table.find("tbody") or table

    records: list[dict[str, Any]] = []
    for tr in body.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) != len(headers):
            continue
        cells = [cell_text(td) for td in tds]  # add-head 라벨 제거, span.tds 우선
        member_name = cells[1]
        if not member_name:
            continue
        for col_name, cell in zip(meeting_cols, cells[2:]):
            rate = _parse_rate(cell)
            if rate is None:
                continue  # 비소속 위원회(빈 셀)
            attended, total, pct = rate
            records.append({
                "member_name": member_name,
                "meeting_type": col_name,
                "attended": attended,
                "total": total,
                "pct": pct,
            })
    return records


def scrape(conn: sqlite3.Connection, client: EgovBoardClient,
           name_index: dict[str, int], *, term: int = config.TERM) -> int:
    new_total = 0
    for cate, half in config.ATTENDANCE_HALVES.items():
        soup = client.post_soup(
            config.ATTENDANCE_PATH, data={"sDaesu": str(term), "sCate": cate}
        )
        for rec in parse_table(soup):
            member_id = match_member_id(name_index, rec["member_name"])
            row = {
                "member_id": member_id,
                "member_name": rec["member_name"],
                "term": term,
                "half": half,
                "meeting_type": rec["meeting_type"],
                "attended": rec["attended"],
                "total": rec["total"],
                "pct": rec["pct"],
            }
            existed = db.exists(
                conn, "attendance_records",
                member_id=member_id, term=term, half=half, meeting_type=rec["meeting_type"],
            )
            db.upsert(conn, "attendance_records", row,
                      conflict=["member_id", "term", "half", "meeting_type"],
                      update=_UPDATE_COLS)
            if not existed:
                new_total += 1
        conn.commit()
    return new_total


if __name__ == "__main__":
    with db.session() as conn, EgovBoardClient() as client:
        name_index = load_name_index(conn)
        log_id = db.start_log(conn, "attendance")
        try:
            n = scrape(conn, client, name_index)
            db.finish_log(conn, log_id, new_rows=n)
            print(f"[attendance] new rows: {n} | table 'attendance_records' total: "
                  f"{db.count_rows(conn, 'attendance_records')}")
            for r in conn.execute(
                "SELECT half, COUNT(*) c, COUNT(member_id) matched "
                "FROM attendance_records GROUP BY half"
            ):
                print(f"   {r['half']}: {r['c']} rows, {r['matched']} member-matched")
        except Exception as exc:  # noqa: BLE001
            db.finish_log(conn, log_id, new_rows=0, status="error", error_msg=str(exc))
            raise
