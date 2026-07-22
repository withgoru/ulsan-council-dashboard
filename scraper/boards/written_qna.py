"""서면질문답변 게시판(writtenQna) → speeches(kind='written_qna').

컬럼: 번호·회/차·질문제목·질문의원·작성일·조회수 (위원회 X, 대수 X).
대수 컬럼이 없으므로 '작성일 >= TERM_START_DATE' 로만 9대 필터·STOP (ENDPOINTS.md 3절).
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
    name = rec.get("질문의원")
    return {
        "kind": "written_qna",
        "term": config.TERM,
        "session_round": rec.get("회/차"),
        "committee": None,
        "member_name": name,
        "member_id": match_member_id(name_index, name),
        "title": rec.get("질문제목"),
        "posted_date": parse_date(rec.get("작성일")),
        "view_count": to_int(rec.get("조회수")),
    }


SPEC = BoardSpec(
    name="written_qna",
    bbs_id=config.BBS["written_qna"],
    table="speeches",
    classify=_classify,
    to_record=_to_record,
    update_cols=["kind", "term", "session_round", "committee", "member_name",
                 "member_id", "title", "posted_date", "view_count", "last_seen_at"],
)

if __name__ == "__main__":
    run_as_script(SPEC)
