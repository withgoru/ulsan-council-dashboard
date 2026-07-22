"""SQLite 연결 · 스키마 초기화 · 멱등 upsert 헬퍼.

웹앱(SvelteKit)이 빌드 시 읽는 것과 동일한 파일(config.DATABASE_PATH).
모든 upsert 는 ON CONFLICT DO UPDATE 로 재실행 시 신규분만 추가하고
기존 행은 last_seen_at(과 조회수 등)만 갱신한다.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Iterable, Iterator, Mapping, Sequence

import config


def connect(db_path=None) -> sqlite3.Connection:
    """설정된 경로로 SQLite 연결을 연다(디렉토리 자동 생성, FK/Row 활성화)."""
    path = db_path or config.DATABASE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """schema.sql 을 적용한다. CREATE ... IF NOT EXISTS 라 재실행에 안전."""
    conn.executescript(config.SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()


@contextmanager
def session(db_path=None) -> Iterator[sqlite3.Connection]:
    """init 된 연결을 컨텍스트로 제공하고 정상 종료 시 커밋한다."""
    conn = connect(db_path)
    try:
        init_db(conn)
        yield conn
        conn.commit()
    finally:
        conn.close()


def upsert(
    conn: sqlite3.Connection,
    table: str,
    row: Mapping[str, Any],
    *,
    conflict: Sequence[str],
    update: Sequence[str] | None = None,
) -> None:
    """단일 행 INSERT ... ON CONFLICT(conflict) DO UPDATE.

    - conflict: 충돌 판정에 쓰는 자연키 컬럼들(해당 테이블 UNIQUE 제약과 일치해야 함).
    - update: 충돌 시 갱신할 컬럼들. None 이면 conflict 를 제외한 나머지 전부를 갱신.
      명시적으로 [] 를 주면 '아무것도 갱신 안 함(DO NOTHING 상당)'.
    """
    cols = list(row.keys())
    placeholders = ", ".join(f":{c}" for c in cols)
    col_list = ", ".join(cols)

    if update is None:
        update = [c for c in cols if c not in conflict]

    if update:
        set_clause = ", ".join(f"{c} = excluded.{c}" for c in update)
        conflict_action = f"DO UPDATE SET {set_clause}"
    else:
        conflict_action = "DO NOTHING"

    sql = (
        f"INSERT INTO {table} ({col_list}) VALUES ({placeholders}) "
        f"ON CONFLICT ({', '.join(conflict)}) {conflict_action}"
    )
    conn.execute(sql, dict(row))


def upsert_many(
    conn: sqlite3.Connection,
    table: str,
    rows: Iterable[Mapping[str, Any]],
    *,
    conflict: Sequence[str],
    update: Sequence[str] | None = None,
) -> int:
    """여러 행 upsert. 처리한 행 수를 반환한다(신규/갱신 구분 없이 시도 건수)."""
    n = 0
    for row in rows:
        upsert(conn, table, row, conflict=conflict, update=update)
        n += 1
    return n


def count_rows(conn: sqlite3.Connection, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"]


def exists(conn: sqlite3.Connection, table: str, **keys: Any) -> bool:
    """자연키로 행 존재 여부 확인(페이지네이션 중단 판정용)."""
    where = " AND ".join(f"{k} = :{k}" for k in keys)
    sql = f"SELECT 1 FROM {table} WHERE {where} LIMIT 1"
    return conn.execute(sql, keys).fetchone() is not None


# ── 스크랩 실행 로그 헬퍼 ─────────────────────────────────────────────────────
def start_log(conn: sqlite3.Connection, board: str) -> int:
    cur = conn.execute(
        "INSERT INTO scrape_log (board, started_at, status) VALUES (?, ?, 'running')",
        (board, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    return cur.lastrowid


def finish_log(
    conn: sqlite3.Connection,
    log_id: int,
    *,
    new_rows: int,
    status: str = "ok",
    error_msg: str | None = None,
) -> None:
    conn.execute(
        "UPDATE scrape_log SET finished_at = ?, new_rows = ?, status = ?, error_msg = ? "
        "WHERE id = ?",
        (datetime.now().isoformat(timespec="seconds"), new_rows, status, error_msg, log_id),
    )
    conn.commit()


if __name__ == "__main__":
    # `uv run python db.py` — 스키마만 생성하고 테이블별 행 수를 출력(스모크 테스트).
    with session() as conn:
        tables = [
            "members", "plenary_activities", "committee_activities", "bills",
            "attendance_records", "speeches", "news_items", "minutes",
            "speech_segments", "scrape_log",
        ]
        print(f"DB: {config.DATABASE_PATH}")
        for t in tables:
            print(f"  {t:22s} {count_rows(conn, t):>6d} rows")
