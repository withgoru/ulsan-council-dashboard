"""5분자유발언 게시판(freeSpeech) → speeches(kind='free_speech').

컬럼: 번호·회/차·제목·위원회·대수·의원명·작성일·조회수 (위원회 O, 대수 O).
대수 필터: 행의 '대수' 값이 9가 아니면 STOP(최신순 정렬 전제).
"""
from __future__ import annotations

from typing import Any

import config
from members import match_member_id

from .base import BoardSpec, Verdict, parse_date, run_as_script, to_int


def _classify(rec: dict[str, Any]) -> Verdict:
    return Verdict.KEEP if (rec.get("대수") or "").strip() == str(config.TERM) else Verdict.STOP


def _to_record(rec: dict[str, Any], name_index: dict[str, int]) -> dict[str, Any]:
    name = rec.get("의원명")
    return {
        "kind": "free_speech",
        "term": config.TERM,
        "session_round": rec.get("회/차"),
        "committee": rec.get("위원회") or None,
        "member_name": name,
        "member_id": match_member_id(name_index, name),
        "title": rec.get("제목"),
        "posted_date": parse_date(rec.get("작성일")),
        "view_count": to_int(rec.get("조회수")),
    }


SPEC = BoardSpec(
    name="free_speech",
    bbs_id=config.BBS["free_speech"],
    table="speeches",
    classify=_classify,
    to_record=_to_record,
    update_cols=["kind", "term", "session_round", "committee", "member_name",
                 "member_id", "title", "posted_date", "view_count", "last_seen_at"],
)

if __name__ == "__main__":
    run_as_script(SPEC)
