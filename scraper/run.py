"""스크래퍼 오케스트레이터.

실행 순서(의존성 기준):
  members → attendance → plenary/committee → speeches(3) → bills → press → CLIK minutes

members 를 먼저 돌려 이름→member_id 매칭 캐시를 만든 뒤, 나머지 보드가 이를 공유한다.
각 단계는 scrape_log 에 기록되고, 한 단계가 실패해도 다음 단계는 계속 진행한다
(공공 사이트 일시 오류에 전체 수집이 무너지지 않도록).

실행: uv run python run.py   (또는 python run.py)
연속 2회 실행 시 두 번째는 신규 0 이어야 한다(멱등성).
"""
from __future__ import annotations

import sqlite3
import traceback
from typing import Callable

import config
import db
import media
import members
import minutes
from boards import (attendance, bills, committee, free_speech, municipal_qna,
                    plenary, press, written_qna)
from boards.base import run_board
from clik_client import ClikClient
from http_client import EgovBoardClient


def _run_step(conn: sqlite3.Connection, name: str, fn: Callable[[], int]) -> tuple[int, str]:
    """한 단계를 scrape_log 로 감싸 실행. (신규행수, 상태) 반환. 예외는 삼켜 다음 단계 진행."""
    log_id = db.start_log(conn, name)
    try:
        new_rows = fn()
        db.finish_log(conn, log_id, new_rows=new_rows)
        print(f"  ✓ {name:16s} 신규 {new_rows}")
        return new_rows, "ok"
    except Exception as exc:  # noqa: BLE001
        db.finish_log(conn, log_id, new_rows=0, status="error", error_msg=str(exc))
        print(f"  ✗ {name:16s} 실패: {exc}")
        traceback.print_exc()
        return 0, "error"


def run() -> dict[str, tuple[int, str]]:
    results: dict[str, tuple[int, str]] = {}
    with db.session() as conn, EgovBoardClient() as web, ClikClient() as clik:
        # 1) 의원명단 — 이후 모든 매칭의 기반
        results["members"] = _run_step(conn, "members", lambda: members.scrape(conn, web))
        name_index = members.load_name_index(conn)

        # 2) 출석률
        results["attendance"] = _run_step(
            conn, "attendance", lambda: attendance.scrape(conn, web, name_index))

        # 3) 본회의/위원회 활동
        for spec in (plenary.SPEC, committee.SPEC):
            results[spec.name] = _run_step(
                conn, spec.name, lambda s=spec: run_board(conn, web, s, name_index))

        # 4) 발언류(5분자유발언/시정질문/서면질문)
        for spec in (free_speech.SPEC, municipal_qna.SPEC, written_qna.SPEC):
            results[spec.name] = _run_step(
                conn, spec.name, lambda s=spec: run_board(conn, web, s, name_index))

        # 5) 의안
        results["bills"] = _run_step(conn, "bills", lambda: bills.scrape(conn, web, name_index))

        # 6) 보도자료 → 뉴스 타임라인
        results[press.SPEC.name] = _run_step(
            conn, press.SPEC.name, lambda: run_board(conn, web, press.SPEC, name_index))

        # 7) CLIK 회의록 발언(핵심 소스)
        results["minutes"] = _run_step(
            conn, "minutes", lambda: minutes.scrape(conn, clik, name_index)[0])

        # 8) 외부 언론 기사 후보(네이버). 키 없으면 스킵.
        results["media"] = _run_step(conn, "media", lambda: media.scrape(conn))

        _print_summary(conn, results)
    return results


def _print_summary(conn: sqlite3.Connection, results: dict[str, tuple[int, str]]) -> None:
    total_new = sum(n for n, _ in results.values())
    errors = [k for k, (_, s) in results.items() if s == "error"]
    print("\n" + "=" * 48)
    print(f"완료: 총 신규 {total_new}행" + (f", 실패 {len(errors)}건: {errors}" if errors else ""))
    print("-" * 48)
    print(f"DB: {config.DATABASE_PATH}")
    for table in ("members", "attendance_records", "plenary_activities",
                  "committee_activities", "speeches", "bills", "news_items",
                  "minutes", "speech_segments"):
        print(f"  {table:22s} {db.count_rows(conn, table):>6d}")


if __name__ == "__main__":
    run()
