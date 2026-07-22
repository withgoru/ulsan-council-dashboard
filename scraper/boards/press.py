"""보도자료 게시판(press) → news_items (뉴스 타임라인 소스).

컬럼: 번호·제목·작성자·작성일·첨부·조회수.
작성자는 의원명 또는 부서명(총무담당관 등) — 의원이면 member_id 매칭, 아니면 NULL.
9대 필터는 '작성일 >= TERM_START_DATE' 로 STOP.
"""
from __future__ import annotations

from typing import Any

import config
from members import match_member_id

from .base import BoardSpec, Verdict, parse_date, run_as_script, to_int


def _classify(rec: dict[str, Any]) -> Verdict:
    posted = parse_date(rec.get("작성일"))
    if posted is None:
        return Verdict.SKIP
    return Verdict.KEEP if posted >= config.TERM_START_DATE.isoformat() else Verdict.STOP


def _to_record(rec: dict[str, Any], name_index: dict[str, int]) -> dict[str, Any]:
    author = rec.get("작성자")
    return {
        "title": rec.get("제목"),
        "author_raw": author,
        "member_id": match_member_id(name_index, author),
        "posted_date": parse_date(rec.get("작성일")),
        "view_count": to_int(rec.get("조회수")),
    }


SPEC = BoardSpec(
    name="press",
    bbs_id=config.BBS["press"],
    table="news_items",
    classify=_classify,
    to_record=_to_record,
    update_cols=["title", "author_raw", "member_id", "posted_date",
                 "view_count", "last_seen_at"],
)

if __name__ == "__main__":
    run_as_script(SPEC)
