"""의안 게시판(bill/list.do) → bills.

접수(acceptanceBill)/처리(processingBill)/계류(mooringBill) 3개 보드를 각각
POST 폼(sDaesu=9)으로 페이지네이션. 세 보드가 bill_number 로 겹치므로
[접수 → 계류 → 처리] 순으로 수집해 status 가 가장 구체적인 값으로 수렴한다.

목록의 '제안자'는 유형(의장/의원/시장…)만 주므로, 의원 발의건만 상세(view.do)의
'제안의원'을 추가로 읽어 실제 발의 의원명·member_id 를 채운다(ENDPOINTS.md 2절).

실행: uv run python -m boards.bills
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

from .base import cell_text, clean, parse_date

_FNVIEW_RE = re.compile(r"fnView\('([^']+)'\)")

# 수집 순서: 뒤에 오는 보드가 status 를 덮어써 더 구체적인 상태로 수렴.
_BOARDS = [
    ("acceptance", config.BILL_BBS["acceptance"]),
    ("mooring", config.BILL_BBS["mooring"]),
    ("processing", config.BILL_BBS["processing"]),
]
_UPDATE_COLS = ["detail_idx", "bill_name", "proposer_type", "proposer_name",
                "committee", "term", "session_round", "proposed_date", "status",
                "result", "member_id", "source_url", "last_seen_at"]


def _parse_list(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """의안 목록 표 → [{의안번호, 의안명, 제안자, 소관상임위, 본회의처리결과, 제안일자, _idx}]."""
    table = soup.find("table")
    if table is None:
        return []
    thead = table.find("thead")
    headers = [clean(th.get_text()) for th in (thead.find_all("th") if thead else table.find_all("th"))]
    body = table.find("tbody") or table
    out: list[dict[str, Any]] = []
    for tr in body.find_all("tr"):
        tds = tr.find_all("td")
        # 데이터 행만: 셀 수가 헤더 수와 일치. ('검색된 의안이 없습니다' 등 colspan 안내행 제외)
        if len(tds) != len(headers):
            continue
        rec: dict[str, Any] = dict(zip(headers, (cell_text(td) for td in tds)))  # type: ignore[arg-type]
        link = tr.find("a", onclick=_FNVIEW_RE.search)
        if link is not None:
            m = _FNVIEW_RE.search(link.get("onclick", ""))
            rec["_idx"] = m.group(1) if m else None
        out.append(rec)
    return out


def _fetch_proposer(client: EgovBoardClient, bbs_id: str, idx: str) -> str | None:
    """상세(view.do)의 '제안의원' 텍스트. 의장/시장 발의는 '-' → None."""
    soup = client.post_soup(
        config.BILL_VIEW_PATH,
        data={"bbsId": bbs_id, "idx": idx, "pageIndex": "1"},
    )
    for row in soup.find_all(["tr", "div"]):
        th = row.find("th")
        if th and "제안의원" in clean(th.get_text()):
            td = row.find("td")
            val = clean(td.get_text()) if td else ""
            return val if val and val != "-" else None
    return None


def _bill_url(idx: str | None) -> str | None:
    return f"{config.COUNCIL_BASE}{config.BILL_VIEW_PATH}?idx={idx}" if idx else None


def scrape(conn: sqlite3.Connection, client: EgovBoardClient,
           name_index: dict[str, int], *, max_pages: int = 50) -> int:
    new_total = 0
    for status, bbs_id in _BOARDS:
        for page in range(1, max_pages + 1):
            soup = client.post_soup(
                config.BILL_LIST_PATH,
                data={"bbsId": bbs_id, "pageIndex": str(page), "sDaesu": str(config.TERM)},
            )
            rows = _parse_list(soup)
            if not rows:
                break
            page_new = 0
            for rec in rows:
                bill_number = rec.get("의안번호")
                if not bill_number:
                    continue
                idx = rec.get("_idx")
                proposer_type = rec.get("제안자")
                proposer_name = None
                member_id = None
                if proposer_type and "의원" in proposer_type and idx:
                    proposer_name = _fetch_proposer(client, bbs_id, idx)
                    # 공동발의는 '공진혁, 김기환, …' 명단 → 대표발의자(첫 이름)로 매칭.
                    if proposer_name:
                        first = re.split(r"[,·]", proposer_name)[0].strip()
                        member_id = match_member_id(name_index, first)

                record = {
                    "bill_number": bill_number,
                    "detail_idx": idx,
                    "bill_name": rec.get("의안명"),
                    "proposer_type": proposer_type,
                    "proposer_name": proposer_name,
                    "committee": rec.get("소관상임위") or None,
                    "term": config.TERM,
                    "session_round": None,
                    "proposed_date": parse_date(rec.get("제안일자")),
                    "status": status,
                    "result": rec.get("본회의처리결과") or None,
                    "member_id": member_id,
                    "source_url": _bill_url(idx),
                }
                existed = db.exists(conn, "bills", bill_number=bill_number)
                db.upsert(conn, "bills", record,
                          conflict=["bill_number"], update=_UPDATE_COLS)
                if not existed:
                    page_new += 1
            conn.commit()
            new_total += page_new
            # 조기 종료를 두지 않는다: 세 보드가 bill_number 로 겹쳐, 앞 보드가 넣은 행이
            # 뒤 보드에서 '기존'으로 보이므로 page_new==0 로는 중단할 수 없다.
            # sDaesu=9 서버 필터로 행 수가 적어 빈 페이지에서 자연 종료된다.
    return new_total


if __name__ == "__main__":
    with db.session() as conn, EgovBoardClient() as client:
        name_index = load_name_index(conn)
        log_id = db.start_log(conn, "bills")
        try:
            n = scrape(conn, client, name_index)
            db.finish_log(conn, log_id, new_rows=n)
            print(f"[bills] new rows: {n} | table 'bills' total: {db.count_rows(conn, 'bills')}")
            for r in conn.execute(
                "SELECT status, COUNT(*) c FROM bills GROUP BY status"
            ):
                print(f"   status={r['status']}: {r['c']}")
        except Exception as exc:  # noqa: BLE001
            db.finish_log(conn, log_id, new_rows=0, status="error", error_msg=str(exc))
            raise
