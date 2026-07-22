# council.ulsan.kr 엔드포인트 검증 결과 (이슈 #1)

PLAN.md 3절의 미검증 항목을 2026-07-22 실제 요청/응답으로 확인한 결과다.
이후 스크래퍼 파서 설계(`bills.py`, `attendance.py`, 게시판류)는 이 문서를 기준으로 한다.

검증 방식: `requests`로 실제 GET/POST를 보내 응답 HTML의 폼 필드·테이블 컬럼·행 구조를 확인.

---

## 1. 출석률 — `attendanceStatistics.do`

- **경로**: `/kor/activity/attendanceStatistics.do`
- **대수·전후반기 전환은 POST 폼**이다 (GET 쿼리 아님).
  - 폼: `name="searchVO"`, `action="/kor/activity/attendanceStatistics.do"`, `method="post"`
  - `sDaesu`: `9`(9대) / `8`(8대)
  - `sCate`: `1`(전반기) / `2`(후반기)
  - GET으로 접근하면 기본값(9대·전반기 추정) 페이지가 뜨지만, 대수/반기 전환은 반드시 POST로 위 두 필드를 보내야 한다.
- **9대 전반기 데이터 이미 존재** (개원 2026-07-06 직후이지만 본회의 4/4 등 집계됨).
- **테이블 구조**: `<caption>의원별 출석률</caption>`, 컬럼 = `번호 | 의원명 | 본회의 | 상임위원회(그룹헤더) | 운영위 | 행자위 | 문복환위 | 산건위 | 교육위`
  - 각 셀 형식: `"N/M (P%)"` (예: `37/39 (94.9%)`). 해당 위원회 소속이 아니면 셀이 비어 있음.
  - `<td>` 안에 접근성용 라벨 span이 있어 텍스트 추출 시 헤더어가 섞여 나올 수 있음 → 숫자/퍼센트만 정규식으로 뽑을 것.
  - 위원회 컬럼은 **대수별로 위원회 명칭·개수가 달라질 수 있으므로** 헤더(th)를 동적으로 읽어 컬럼→위원회 매핑을 만들 것 (하드코딩 금지).

**결론**: PLAN의 `attendance.py`는 `sDaesu`×`sCate` 조합(9대×{1,2}, 필요 시 8대)으로 POST 반복. 스키마 `attendance_records(member_id, term, half, meeting_type, attended, total, pct)`의 `half`는 `sCate`, `meeting_type`은 헤더에서 읽은 위원회명.

---

## 2. 의안 — `/kor/bill/list.do`

### ⚠️ PLAN 정정: `receiptBill` bbsId는 존재하지 않음

`bbsId=receiptBill`로 요청하면 `alert('잘못된 경로입니다.')` 후 `/`로 리다이렉트(응답 len≈110). **PLAN.md의 `receiptBill`은 오기(誤記)다.**

실제 의안 게시판 bbsId (의안 메뉴 네비게이션에서 확인):

| 메뉴 | bbsId | 상태 |
|---|---|---|
| 접수의안 | `acceptanceBill` | ✅ 동작 (PLAN의 receiptBill을 대체) |
| 처리의안 | `processingBill` | ✅ 동작 |
| 계류의안 | `mooringBill` | ✅ 동작 (이전 대수 이월분 포함) |
| 상세검색 | `advancedSearch` | (검색 폼) |

### 공유 컬럼셋 (acceptance/processing/mooring 3개 동일)

`<caption>{접수|처리|계류}의안 게시물목록</caption>`, 컬럼:

```
의안번호 | 의안명 | 제안자 | 소관상임위 | 본회의처리결과 | 제안일자
```

- 셀 구조: `<td><span class="add-head">라벨</span><span class="tds">값</span></td>` → **`span.tds`만 추출**.
- `제안자`는 **유형**만 표시(`의장`/`의원`/`시장`/`교육감`/`위원장` 등) — 실제 발의 의원명 아님.

### 요청 파라미터 (POST 폼 `name="frm"` → `action="/kor/bill/list.do"`)

숨은 필드: `pageIndex`, `idx`, `bbsId`, `checkedIdxs`, `checkedSeqs`
검색 필드(모두 선택):

| 필드 | 의미 | 값 예 |
|---|---|---|
| `sDaesu` | 대수 | `0`(전체)/`9`/`8`/... |
| `sTh` | 회기 | `0`(전체)/`265`/`264`/... |
| `sBillCate` | 의안종류 | `B100`(조례안)/`B201`(예산안)/`B251`(동의안)/... |
| `sProp` | 제안자 | `A101`(시장)/`A201`(교육감)/`A310`(의장)/`A320`(위원장)/`A330`(의원)/`A999`(기타) |
| `sCommCode` | 소관위원회 | `9-A011`(본회의)/`9-C101`(운영위)/`9-C601`(행자위)/`9-C701`(문복환위)/`9-C501`(산건위)/`9-C801`(교육위)/`9-E011`(예결특위) |
| `sBillDiv` | 발의구분 | `D1`(1인발의)/`D2`(대표발의)/`D3`(공동발의) |
| `sBillDaepyo` | 대표발의자명(텍스트) | |
| `searchCnd` | 검색조건 | `1`(의안명)/`2`(대표발의자) |
| `searchWrd` | 검색어 | |

- **9대 필터**: `sDaesu=9` POST로 확인됨. 계류의안(`mooringBill`)은 이전 대수 이월분(제안일 2026-06-01 등)이 섞여 있으므로 `sDaesu=9` 필터 필수.

### 상세 페이지 — `/kor/bill/view.do`

- 목록의 상세 링크는 `onclick="fnView('41220')"` → `frm.idx = 41220; frm.action="/kor/bill/view.do"; frm.submit()`.
  - `41220`은 **내부 idx**(화면의 의안번호 `21`과 다름). dedup 자연키로 이 idx 또는 `(bbsId,의안번호)` 사용.
- POST `/kor/bill/view.do` (`bbsId`, `idx`, `pageIndex`) 응답에 3개 상세 테이블:
  - **기본정보**: 안건명/의안번호, 의안종류, 제안일 / 제안자유형 / `9대 / 265회`(대수·회기)
  - **위원회 처리사항**: 회부일/처리결과 등
  - **본회의 처리사항**: 상정일/처리결과, **원안파일(.hwpx)**, 검토보고서, 심사보고서, **제안의원**(← 실제 발의 의원명. 의장/시장 발의는 `-`)
- **의원명(member_id 매칭)은 목록에 없고 상세의 `제안의원` 필드에서 취득**. 대량 수집 시 목록→상세 2단계 필요.

---

## 3. 5분자유발언 / 시정질문 / 서면질문 게시판

셋 다 목록 `/cop/bbs/anonymous/selectBoardList.do?bbsId=X` (GET), 상세 `/cop/bbs/selectBoardArticle.do?bbsId=X&nttId=Y`. 자연키 `(bbsId, nttId)`.

### ⚠️ PLAN 정정: 세 게시판 행 구조는 **동일하지 않다**

| bbsId | caption | 컬럼 | 위원회 | 대수 |
|---|---|---|---|---|
| `freeSpeech` | 5분자유발언 게시물목록 | 번호·회/차·제목·**위원회**·**대수**·의원명·작성일·조회수 | ✅ | ✅ |
| `municipalQna` | 시정질문답변 게시물목록 | 번호·회/차·제목·**대수**·의원명·작성일·조회수 | ❌ | ✅ |
| `writtenQna` | 서면질문답변 게시물목록 | 번호·회/차·**질문제목**·**질문의원**·작성일·조회수 | ❌ | ❌ |

- `municipalQna`는 `freeSpeech`에서 **위원회 컬럼이 빠진** 구조.
- `writtenQna`는 **위원회·대수 컬럼 모두 없고**, 컬럼명도 `제목→질문제목`, `의원명→질문의원`으로 다름.

### 대수(9) 필터링 규칙 (게시판별로 다름)

- `freeSpeech`, `municipalQna`: **행의 `대수` 컬럼 값으로 필터**. 값이 `9`가 아닌 첫 행에서 페이지네이션 중단.
  - (관측) 현재 `municipalQna` 최신글은 8대(2025~2024)뿐 → 9대 시정질문 아직 없음. `freeSpeech`는 9대 다수 존재.
- `writtenQna`: **대수 컬럼이 없으므로 `작성일 >= 2026-07-06`(TERM_START_DATE)로만 필터·중단**. (현재 페이지에 9대 2건 + 8대가 날짜 내림차순으로 섞여 있음.)

**결론**: 세 게시판을 하나의 파서로 뭉치지 말 것. 컬럼 인덱스를 caption/헤더 기준으로 게시판별로 매핑하고, 대수 필터는 위 규칙대로 분기. `speeches` 테이블의 `committee`는 `freeSpeech`에만 채워지고 나머지는 NULL.

---

## 4. CLIK 회의록 Open API (`clik.nanet.go.kr/openapi/minutes.do`) — 이슈 #5 검증

핵심 소스. `type=json` 응답은 `[{RESULT_CODE, RESULT_MESSAGE, TOTAL_COUNT, LIST_COUNT, LIST:[...]}]` 배열.

### 목록 (`displayType=list`)

- 파라미터: `key`, `type=json`, `displayType=list`, `searchType=RASMBLY_NM`, `searchKeyword=울산광역시의회`, `startCount`, `listCount`.
- `LIST[].ROW` 필드: `DOCID`, `RASMBLY_SESN`(회기 265), `RASMBLY_ID`(052001), `MTG_DE`(YYYYMMDD), `RASMBLY_NM`, **`RASMBLY_NUMPR`(대수)**, `MINTS_ODR`(차수), `MTGNM`(본회의/위원회명).
- **MTG_DE 내림차순** 정렬. 9대 필터: `RASMBLY_NUMPR=='9'` 이고 `MTG_DE >= 20260706`. 조건 위반 행에서 중단.
- ⚠️ `rasmblyId` 단독 필터는 확인 불가(아래 데모 키 제한 때문). `searchType=RASMBLY_NM`+`searchKeyword` 조합만 검증됨.

### ⚠️ 공개 데모 키(`e1a7f9…`)의 하드 제한 — **정식 키 발급 필요**

- 데모 키는 `startCount`/`listCount`/`pageNo` 등 **모든 페이지네이션 파라미터를 무시**하고 **항상 최신 5건만** 반환한다(`TOTAL_COUNT`는 6640으로 보고되지만 실제 반환은 5건 고정).
- 따라서 데모 키로는 9대 회의록 5건까지만 수집 가능. 전량 수집은 **사용자가 clik.nanet.go.kr 회원가입 → "인증키신청"으로 정식 키 발급** 후 `.env`의 `CLIK_API_KEY`에 설정해야 한다(계정 생성은 대행 불가).
- 코드는 정식 키에서 정상 페이지네이션되도록 구현하되, "새 DOCID가 없는 페이지를 만나면 중단"하는 가드로 데모 키에서 무한 루프를 방지한다.

### 상세 (`displayType=detail`)

- 파라미터: `key`, `type=json`, `displayType=detail`, **`docid=<DOCID>`** (⚠️ 소문자 `docid`. `docId`/`DOCID`는 "상세아이디 값이 유효하지 않습니다" 오류).
- 필드는 **최상위 obj**에 위치(LIST/ROW 아님): `MINTS_HTML`(회의록 전문 HTML), `MTR_SJ`(의사일정 요약), `ORGINL_FILE_URL`, 기타 목록과 동일한 메타.
- `MINTS_HTML` 파싱: `div.contents-block.speaker-block` = 발언 1건. `<strong>` 안에 역할(○의장/○경제부시장…), 의원이면 `<a class="member_profile">이름</a>`. 그 뒤 텍스트(`<br/>` 구분)가 발언 내용. `strong.item-in-contents`(의사일정 항목, 불릿 '0' 접두)가 문서 순서상 발언 사이에 위치 → 직전 항목을 agenda_item 으로 태깅. 의원 매칭은 `data-member_code`(CLIK 자체 코드)가 아니라 **이름**으로.

---

## PLAN.md 반영 필요 사항 요약

1. `receiptBill` → **`acceptanceBill`**로 교체. `mooringBill`(계류의안) 추가 검토.
2. 출석률 대수/반기 전환은 **POST(`sDaesu`,`sCate`)** 명시.
3. 의안 발의 의원명은 **상세 `view.do`의 `제안의원`** 필드에서 취득(목록엔 유형만).
4. `municipalQna`/`writtenQna`는 `freeSpeech`와 **컬럼 구조가 다름**. `writtenQna`는 대수 컬럼이 없어 **날짜 기준 필터**.
5. CLIK 상세 파라미터명은 소문자 **`docid`**, 필드는 최상위 obj. **공개 데모 키는 5건 제한** → 정식 키 발급이 전량 수집의 전제.
