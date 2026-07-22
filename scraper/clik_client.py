"""CLIK 지방의정포털 Open API 클라이언트 (회의록 minutes.do).

목록: displayType=list, searchType=RASMBLY_NM, searchKeyword=울산광역시의회.
      날짜(MTG_DE) 내림차순. 응답은 [{RESULT_CODE, TOTAL_COUNT, LIST:[{ROW:{...}}]}].
상세: displayType=detail, docid=<DOCID> (⚠️ 파라미터명 소문자 'docid').
      최상위 obj 에 MINTS_HTML 등 필드가 들어온다(LIST/ROW 아님).

9대 필터: RASMBLY_NUMPR=='9' 이고 MTG_DE >= TERM_START_DATE.
검증 결과는 ENDPOINTS.md 참고. API 키는 config.CLIK_API_KEY(데모 키 기본).
"""
from __future__ import annotations

import time
from typing import Any, Iterator

import requests

import config


class ClikError(RuntimeError):
    pass


class ClikClient:
    def __init__(
        self,
        *,
        api_key: str = config.CLIK_API_KEY,
        delay: float = config.REQUEST_DELAY,
        timeout: int = config.REQUEST_TIMEOUT,
        max_retries: int = config.MAX_RETRIES,
    ) -> None:
        self.api_key = api_key
        self.delay = delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": config.USER_AGENT})
        self._last_at = 0.0

    def __enter__(self) -> "ClikClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.session.close()

    # ── 저수준 ───────────────────────────────────────────────────────────────
    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_at
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

    def _get_json(self, params: dict[str, Any]) -> dict[str, Any]:
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            self._throttle()
            try:
                r = self.session.get(
                    f"{config.CLIK_BASE}{config.CLIK_MINUTES_PATH}",
                    params=params, timeout=self.timeout,
                )
                self._last_at = time.monotonic()
                r.raise_for_status()
                data = r.json()
                obj = data[0] if isinstance(data, list) else data
                if obj.get("RESULT_CODE") != "SUCCESS":
                    raise ClikError(obj.get("RESULT_MESSAGE", "unknown CLIK error"))
                return obj
            except (requests.RequestException, ValueError) as exc:
                last_exc = exc
                self._last_at = time.monotonic()
                if attempt < self.max_retries:
                    time.sleep(self.delay * (config.RETRY_BACKOFF ** (attempt - 1)))
        raise ClikError(f"CLIK request failed after {self.max_retries} attempts: {last_exc}")

    # ── 목록 ─────────────────────────────────────────────────────────────────
    def list_page(self, *, start: int = 0, count: int = 100) -> tuple[list[dict[str, Any]], int]:
        """한 페이지의 ROW 리스트와 TOTAL_COUNT 반환."""
        obj = self._get_json({
            "key": self.api_key, "type": "json", "displayType": "list",
            "searchType": "RASMBLY_NM", "searchKeyword": config.CLIK_RASMBLY_NM,
            "startCount": str(start), "listCount": str(count),
        })
        rows = [item.get("ROW", {}) for item in obj.get("LIST", [])]
        return rows, int(obj.get("TOTAL_COUNT", 0))

    def iter_term_minutes(self, *, term: int = config.TERM, page_size: int = 100) -> Iterator[dict[str, Any]]:
        """대수·날짜 조건을 만족하는 회의록 메타 ROW 를 최신순으로 순회.

        MTG_DE 내림차순이므로, RASMBLY_NUMPR!=term 이거나 MTG_DE < 개원일인 행을
        만나면 이후는 모두 이전 대수 → 중단.

        ⚠️ 공개 데모 키는 startCount/listCount 를 무시하고 항상 최신 5건만 돌려준다
        (ENDPOINTS.md). 그래서 페이지가 새 DOCID 를 하나도 주지 않으면 중단한다 —
        이 가드는 데모 키에선 1페이지 후 종료시키고, 정식 키에선 정상 페이지네이션된다.
        """
        start_de = config.TERM_START_DATE.strftime("%Y%m%d")
        seen: set[str] = set()
        start = 0
        while True:
            rows, total = self.list_page(start=start, count=page_size)
            if not rows:
                return
            new_in_page = 0
            for row in rows:
                docid = str(row.get("DOCID", "")).strip()
                numpr = str(row.get("RASMBLY_NUMPR", "")).strip()
                mtg_de = str(row.get("MTG_DE", "")).strip()
                if numpr != str(term) or mtg_de < start_de:
                    return
                if docid in seen:
                    continue
                seen.add(docid)
                new_in_page += 1
                yield row
            if new_in_page == 0:   # 페이지가 진행되지 않음(데모 키) → 중단
                return
            start += page_size
            if start >= total:
                return

    # ── 상세 ─────────────────────────────────────────────────────────────────
    def fetch_detail(self, docid: str) -> dict[str, Any]:
        """회의록 상세(MINTS_HTML 포함). 파라미터명은 소문자 'docid'."""
        return self._get_json({
            "key": self.api_key, "type": "json", "displayType": "detail",
            "docid": docid,
        })


if __name__ == "__main__":
    # uv run python clik_client.py — 9대 회의록 메타 목록만 출력(상세 미조회).
    with ClikClient() as c:
        rows = list(c.iter_term_minutes())
        print(f"9대 회의록 {len(rows)}건 (최신순):")
        for r in rows:
            print(f"  {r['MTG_DE']} {r['MTGNM']:12s} 제{r['RASMBLY_SESN']}회 "
                  f"{r['MINTS_ODR']}차  {r['DOCID']}")
