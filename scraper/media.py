"""외부 언론 기사 후보 수집 — 네이버 뉴스 검색 API → media_articles.

'언론이 본 의회' 패널의 후보 풀. 실제 공개는 큐레이션(data/media-curation.json)에서
승인한 것만 노출한다. 여기서는 후보를 폭넓게 모으기만 한다(멱등, URL dedup).

키(NAVER_CLIENT_ID/SECRET)가 없으면 조용히 건너뛴다.
실행: uv run python media.py
"""
from __future__ import annotations

import html
import re
import sqlite3
import time

import requests
from dateutil import parser as dateparser

import config
import db

_TAG_RE = re.compile(r"<[^>]+>")


def _clean(text: str) -> str:
    """네이버 응답의 <b> 태그·HTML 엔티티 제거."""
    return html.unescape(_TAG_RE.sub("", text or "")).strip()


def _pub_date(pub: str | None) -> str | None:
    if not pub:
        return None
    try:
        return dateparser.parse(pub).date().isoformat()
    except (ValueError, TypeError, OverflowError):
        return None


def _press_from_url(url: str) -> str | None:
    """원문 링크 도메인에서 언론사 힌트 추출(네이버는 언론사명을 직접 주지 않음)."""
    m = re.search(r"https?://(?:www\.)?([^/]+)", url or "")
    return m.group(1) if m else None


def _search(session: requests.Session, query: str) -> list[dict]:
    resp = session.get(
        config.NAVER_SEARCH_URL,
        params={"query": query, "display": config.NAVER_DISPLAY, "sort": "date", "format": "json"},
        timeout=config.REQUEST_TIMEOUT,
    )
    if not resp.ok:
        # API 오류 사유를 그대로 노출(401 인증/구독 문제 등 진단에 필요).
        raise RuntimeError(f"네이버 API {resp.status_code}: {resp.text[:200]}")
    return resp.json().get("items", [])


def scrape(conn: sqlite3.Connection) -> int:
    if not (config.NAVER_API_KEY_ID and config.NAVER_API_KEY):
        print("[media] NAVER_API_KEY_ID/NAVER_API_KEY 미설정 → 수집 건너뜀")
        return 0

    session = requests.Session()
    # NCP API Hub 인증 헤더.
    session.headers.update(
        {
            "X-NCP-APIGW-API-KEY-ID": config.NAVER_API_KEY_ID,
            "X-NCP-APIGW-API-KEY": config.NAVER_API_KEY,
            "User-Agent": config.USER_AGENT,
        }
    )

    new_total = 0
    for query in config.NAVER_QUERIES:
        items = _search(session, query)
        for it in items:
            url = it.get("originallink") or it.get("link")
            title = _clean(it.get("title", ""))
            if not url or not title:
                continue
            record = {
                "url": url,
                "title": title,
                "description": _clean(it.get("description", "")),
                "press": _press_from_url(url),
                "published_at": _pub_date(it.get("pubDate")),
                "query": query,
            }
            existed = db.exists(conn, "media_articles", url=url)
            db.upsert(
                conn, "media_articles", record,
                conflict=["url"],
                update=["title", "description", "press", "published_at", "query", "last_seen_at"],
            )
            if not existed:
                new_total += 1
        conn.commit()
        time.sleep(config.REQUEST_DELAY)
    return new_total


if __name__ == "__main__":
    with db.session() as conn:
        log_id = db.start_log(conn, "media")
        try:
            n = scrape(conn)
            db.finish_log(conn, log_id, new_rows=n)
            print(f"[media] 신규 후보 {n}건 | media_articles 총 {db.count_rows(conn, 'media_articles')}")
        except Exception as exc:  # noqa: BLE001
            db.finish_log(conn, log_id, new_rows=0, status="error", error_msg=str(exc))
            raise
