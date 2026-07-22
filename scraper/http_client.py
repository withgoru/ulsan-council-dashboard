"""council.ulsan.kr eGovFrame 게시판 HTTP 클라이언트.

재시도·요청 간 지연·User-Agent 를 공통 처리하고, 게시판 목록/상세의
GET·POST 를 얇게 감싼다. HTML 파싱은 각 boards/*.py 파서가 담당한다.

의존: requests, beautifulsoup4, lxml (config 의 상수 사용).
"""
from __future__ import annotations

import time
from typing import Any, Mapping

import requests
from bs4 import BeautifulSoup

import config


class HttpError(RuntimeError):
    """재시도 소진 후에도 실패한 요청."""


class EgovBoardClient:
    """council.ulsan.kr 요청 세션.

    사용 예:
        with EgovBoardClient() as c:
            soup = c.board_list("freeSpeech", page=1)
            soup = c.board_article("freeSpeech", ntt_id="122169")
    """

    def __init__(
        self,
        base_url: str = config.COUNCIL_BASE,
        *,
        delay: float = config.REQUEST_DELAY,
        timeout: int = config.REQUEST_TIMEOUT,
        max_retries: int = config.MAX_RETRIES,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.delay = delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": config.USER_AGENT,
                "Accept-Language": "ko,en;q=0.9",
            }
        )
        self._last_request_at = 0.0

    # ── 컨텍스트 매니저 ──────────────────────────────────────────────────────
    def __enter__(self) -> "EgovBoardClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self.session.close()

    # ── 저수준 요청 (지연 + 재시도) ──────────────────────────────────────────
    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        data: Mapping[str, Any] | None = None,
    ) -> requests.Response:
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            self._throttle()
            try:
                resp = self.session.request(
                    method, url, params=params, data=data, timeout=self.timeout
                )
                self._last_request_at = time.monotonic()
                resp.raise_for_status()
                # eGov 사이트는 잘못된 경로에도 200 + JS alert 리다이렉트를 준다.
                # (예: bbsId=receiptBill → "잘못된 경로입니다.") 호출부가 감지하도록
                #  본문은 그대로 반환하되, 파서가 테이블 부재로 판단한다.
                return resp
            except (requests.RequestException,) as exc:  # noqa: PERF203
                last_exc = exc
                self._last_request_at = time.monotonic()
                if attempt < self.max_retries:
                    time.sleep(self.delay * (config.RETRY_BACKOFF ** (attempt - 1)))
        raise HttpError(f"{method} {url} failed after {self.max_retries} attempts: {last_exc}")

    # ── 고수준 헬퍼 ──────────────────────────────────────────────────────────
    def get_soup(
        self, path: str, *, params: Mapping[str, Any] | None = None
    ) -> BeautifulSoup:
        resp = self._request("GET", path, params=params)
        return BeautifulSoup(resp.text, "lxml")

    def post_soup(
        self, path: str, *, data: Mapping[str, Any] | None = None
    ) -> BeautifulSoup:
        resp = self._request("POST", path, data=data)
        return BeautifulSoup(resp.text, "lxml")

    def board_list(
        self,
        bbs_id: str,
        *,
        page: int = 1,
        search_cnd: str | None = None,
        search_wrd: str | None = None,
        extra: Mapping[str, Any] | None = None,
    ) -> BeautifulSoup:
        """익명 게시판 목록 페이지. council 목록은 GET 쿼리로 동작한다."""
        params: dict[str, Any] = {"bbsId": bbs_id, "pageIndex": page}
        if search_cnd is not None:
            params["searchCnd"] = search_cnd
        if search_wrd is not None:
            params["searchWrd"] = search_wrd
        if extra:
            params.update(extra)
        return self.get_soup(config.BOARD_LIST_PATH, params=params)

    def board_article(self, bbs_id: str, *, ntt_id: str) -> BeautifulSoup:
        """익명 게시판 상세 글. 자연키 (bbsId, nttId)."""
        return self.get_soup(
            config.BOARD_ARTICLE_PATH, params={"bbsId": bbs_id, "nttId": ntt_id}
        )


def article_url(bbs_id: str, ntt_id: str) -> str:
    """게시글 상세 정규 URL(source_url 저장용)."""
    return f"{config.COUNCIL_BASE}{config.BOARD_ARTICLE_PATH}?bbsId={bbs_id}&nttId={ntt_id}"


if __name__ == "__main__":
    # `uv run python http_client.py` — 5분자유발언 목록 1페이지를 받아 첫 글 제목 출력.
    with EgovBoardClient() as client:
        soup = client.board_list(config.BBS["free_speech"], page=1)
        table = soup.find("table")
        caption = table.find("caption") if table else None
        print("caption:", caption.get_text(strip=True) if caption else None)
        body = table.find("tbody") if table else None
        first = body.find("tr") if body else None
        if first:
            cells = [c.get_text(" ", strip=True) for c in first.find_all("td")]
            print("first row:", cells)
