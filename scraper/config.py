"""스크래퍼 전역 상수.

값의 근거는 PLAN.md 1·3절과 검증 결과 ENDPOINTS.md 참고.
환경변수로 override 가능한 것은 os.environ에서 읽는다(.env는 웹앱과 공유).
"""
from __future__ import annotations

import os
from datetime import date
from pathlib import Path

# ── 임기(대수) ────────────────────────────────────────────────────────────
TERM = 9  # 제9대 울산광역시의회
# 9대 개원일. 이 날짜 이전 게시물/회의록은 이전 대수로 간주해 수집 중단.
TERM_START_DATE = date(2026, 7, 6)

# ── 경로 ──────────────────────────────────────────────────────────────────
SCRAPER_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRAPER_DIR.parent
# 웹앱(SvelteKit)이 빌드 시 읽는 것과 동일한 SQLite. .env의 DATABASE_PATH와 일치시킨다.
DATABASE_PATH = Path(
    os.environ.get("DATABASE_PATH", str(REPO_ROOT / "data" / "council.sqlite3"))
).expanduser()
SCHEMA_PATH = SCRAPER_DIR / "schema.sql"

# ── council.ulsan.kr ────────────────────────────────────────────────────────
COUNCIL_BASE = "https://www.council.ulsan.kr"

# eGovFrame 익명 게시판(목록/상세). 자연키는 (bbsId, nttId).
BOARD_LIST_PATH = "/cop/bbs/anonymous/selectBoardList.do"
BOARD_ARTICLE_PATH = "/cop/bbs/selectBoardArticle.do"

# 게시판 bbsId. ENDPOINTS.md 3절 검증 결과 기준(게시판별 컬럼 구조 상이).
BBS = {
    "free_speech": "freeSpeech",     # 5분자유발언 (위원회 O, 대수 O)
    "municipal_qna": "municipalQna",  # 시정질문답변 (위원회 X, 대수 O)
    "written_qna": "writtenQna",     # 서면질문답변 (위원회 X, 대수 X → 날짜로 필터)
    "press": "press",                # 보도자료 → 뉴스 타임라인
}

# 의안: /kor/bill/list.do (POST 폼 frm), 상세 /kor/bill/view.do.
# ⚠️ PLAN의 receiptBill은 오기 — 접수의안 bbsId는 acceptanceBill (ENDPOINTS.md 2절).
BILL_LIST_PATH = "/kor/bill/list.do"
BILL_VIEW_PATH = "/kor/bill/view.do"
BILL_BBS = {
    "acceptance": "acceptanceBill",  # 접수의안
    "processing": "processingBill",  # 처리의안
    "mooring": "mooringBill",        # 계류의안(이전 대수 이월분 포함 → sDaesu 필터 필수)
}

# 출석률: POST 폼(searchVO). sDaesu=대수, sCate=1(전반기)/2(후반기).
ATTENDANCE_PATH = "/kor/activity/attendanceStatistics.do"
ATTENDANCE_HALVES = {"1": "전반기", "2": "후반기"}

# 의원명단: viewByPerson.do(로스터) + mem/sub/profile.do(약력).
MEMBERS_PATH = "/kor/member/viewByPerson.do"
MEMBER_PROFILE_PATH = "/kor/member/sub/profile.do"

# ── CLIK 지방의정포털 Open API ───────────────────────────────────────────────
CLIK_BASE = "https://clik.nanet.go.kr"
CLIK_MINUTES_PATH = "/openapi/minutes.do"
CLIK_RASMBLY_ID = "052001"          # 울산광역시의회 (rasmblyId 단독 필터는 이슈 #5에서 재확인)
CLIK_RASMBLY_NM = "울산광역시의회"   # searchType=RASMBLY_NM + searchKeyword 조합이 검증된 접근
# 문서 공개 데모 키. 사용자가 정식 키 발급 시 .env의 CLIK_API_KEY로 override.
CLIK_API_KEY = os.environ.get("CLIK_API_KEY", "e1a7f967a146465aaf8721392e50e7a9")

# ── HTTP 클라이언트 동작 ──────────────────────────────────────────────────────
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) ulsan-council-dashboard/0.1 (+https://github.com/withgoru/ulsan-council-dashboard)"
)
REQUEST_TIMEOUT = 20        # 초
REQUEST_DELAY = 0.7         # 연속 요청 사이 지연(초) — 공공 사이트 예의상 rate limit
MAX_RETRIES = 3
RETRY_BACKOFF = 1.5         # 재시도 간 지수 백오프 계수
