"""위원회활동 게시판(committee) → committee_activities.

컬럼: 번호·제목·소관위원회·작성일·첨부파일·조회수.
회차는 제목에서 파싱, 9대 필터는 '작성일 >= TERM_START_DATE' 로 STOP.
"""
from __future__ import annotations

from typing import Any

import config

from .base import (BoardSpec, Verdict, parse_date, parse_session_round,
                   run_as_script, to_int)


def _classify(rec: dict[str, Any]) -> Verdict:
    posted = parse_date(rec.get("작성일"))
    if posted is None:
        return Verdict.SKIP
    return Verdict.KEEP if posted >= config.TERM_START_DATE.isoformat() else Verdict.STOP


def _to_record(rec: dict[str, Any], name_index: dict[str, int]) -> dict[str, Any]:
    title = rec.get("제목")
    return {
        "term": config.TERM,
        "committee_name": rec.get("소관위원회") or None,
        "session_round": parse_session_round(title),
        "title": title,
        "posted_date": parse_date(rec.get("작성일")),
        "view_count": to_int(rec.get("조회수")),
    }


SPEC = BoardSpec(
    name="committee",
    bbs_id=config.BBS["committee"],
    table="committee_activities",
    classify=_classify,
    to_record=_to_record,
    update_cols=["term", "committee_name", "session_round", "title",
                 "posted_date", "view_count", "last_seen_at"],
)

if __name__ == "__main__":
    run_as_script(SPEC)
