# 울산광역시의회 의정활동 대시보드

## Context

울산광역시의회(https://www.council.ulsan.kr)는 2026-07-06 개원한 제9대(9기) 임기 정보를 공개하고 있지만, 정작 회의 "내용"(누가 무슨 말을 했는지)은 게시판에 제목만 노출하고 실제 회의록은 hwpx 첨부파일로만 제공한다. 이 프로젝트는 (1) 공개된 의정활동 데이터를 주기적으로 스크래핑해 로컬 SQLite에 누적 저장하고, (2) 그 데이터를 정적 SvelteKit 대시보드로 시각화해 Cloudflare Pages에 배포하는 것이 목표다. 9기(9대)의 임기가 막 시작된 시점이라 데이터가 거의 없으므로, 스크래퍼는 앞으로 4년간 반복 실행되며 데이터를 쌓아가는 것을 전제로 설계한다.

핵심 발견: 국회도서관 CLIK(지방의정포털, https://clik.nanet.go.kr)이 전국 지방의회 회의록 Open API를 제공하며, 상세 조회 시 **발언자별로 태깅된 회의록 전문(全文) HTML**을 반환한다. 이는 council.ulsan.kr 자체 게시판(제목만 있고 본문은 hwpx 첨부)보다 압도적으로 우수한 소스이므로, "의원이 실제로 한 말"을 모으는 핵심 기능은 CLIK API를 1차 소스로 사용한다.

프로젝트 위치는 기존 `gantt-app`(무관한 Next.js 프로젝트)이 있는 현재 디렉토리가 아니라, 이미 git 저장소(원격 `github.com/withgoru/ulsan-council-dashboard`)로 초기화되어 있는 `/Users/ulgoon/Documents/dev/antigravity/ulsan-council-dashboard`에 새로 만든다.

---

## 1. 리포지토리 구조

```
ulsan-council-dashboard/            (기존 git repo, README.md만 있음)
├── src/                            # SvelteKit 앱 (repo 루트에 위치 — Cloudflare Pages 기본 빌드 설정과 맞음)
│   ├── app.html / app.css / app.d.ts
│   ├── lib/
│   │   ├── components/{ui,dashboard,member,common}/
│   │   ├── server/{db.ts, queries/*, mappers/*}   # better-sqlite3, Node-only, 빌드타임 전용
│   │   ├── types/{member,activity,bill,attendance,news,speech}.ts
│   │   ├── config/{parties.ts, site.ts}
│   │   ├── utils/{date,slug,seo,cn}.ts
│   │   └── stores/theme.ts
│   └── routes/
│       ├── +layout.svelte, +layout.ts (prerender = true)
│       ├── +page.svelte / +page.server.ts          # 대시보드
│       ├── members/[slug]/+page.svelte / +page.server.ts
│       ├── sitemap.xml/+server.ts
│       └── robots.txt/+server.ts
├── static/                          # favicon, og-default.png, _headers, images/members/{memCode}.jpg
├── scripts/check-db.mjs             # prebuild: DATABASE_PATH 존재/읽기 검증
├── svelte.config.js / tailwind.config.ts / components.json
├── scraper/                          # Python 스크래퍼 (독립 실행, SvelteKit과 별개)
│   ├── config.py                     # TERM=9, TERM_START_DATE=2026-07-06, CLIK_RASMBLY_ID=052001 등
│   ├── db.py, schema.sql
│   ├── http_client.py                # EgovBoardClient (council.ulsan.kr 게시판 POST 페이지네이션)
│   ├── clik_client.py                # CLIK OpenAPI 클라이언트
│   ├── boards/{members,plenary,committee,free_speech,municipal_qna,written_qna,press,bills,attendance}.py
│   ├── minutes.py                    # CLIK 회의록 수집 + 화자별 세그먼트 파싱
│   ├── run.py
│   └── requirements.txt
├── data/council.sqlite3              # 스크래퍼 산출물 (.gitignore, DATABASE_PATH env로 참조)
└── .env                               # DATABASE_PATH=./data/council.sqlite3, CLIK_API_KEY=...
```

---

## 2. 데이터 소스 배분

| 데이터 | 소스 | 비고 |
|---|---|---|
| 회의록 전문(全文), 발언자별 발언 내용 | **CLIK Open API** (`minutes.do`) | 본회의/위원회 회의 중 실제 발언(5분자유발언, 시정질문 구두답변, 토론 등) 전체를 발언자 태그와 함께 제공 |
| 본회의/위원회 활동 목록(일자·회차·위원회) | CLIK API 목록(1차) + council.ulsan.kr 게시판(첨부파일·조회수 보강, 선택) | CLIK 목록만으로 날짜/회차/위원회명 충분 |
| 의원명단(정당·선거구·위원회 직책·사진·연락처·약력) | council.ulsan.kr (`viewByPerson.do` + `mem/sub/profile.do`) | CLIK에 없음 |
| 의원별 회의출석률 | council.ulsan.kr (`activity/attendanceStatistics.do`) | CLIK에 없음 |
| 의안 접수/처리 | council.ulsan.kr (`kor/bill/list.do?bbsId=acceptanceBill\|processingBill\|mooringBill`) | 구조화된 표, CLIK보다 상세. ⚠️ `receiptBill`은 오기 — 실제 접수의안 bbsId는 `acceptanceBill`. 검증 결과는 [scraper/ENDPOINTS.md](./scraper/ENDPOINTS.md) 참고 |
| 서면질문답변(문서 기반, 회의장 발언 아님) | council.ulsan.kr (`bbsId=writtenQna`) | CLIK 회의록에 안 잡힘, 제목/날짜만 |
| 보도자료(뉴스 타임라인) | council.ulsan.kr (`bbsId=press`) | CLIK에 없음 |

## 3. Python 스크래퍼 설계

**의존성**: `requests`, `beautifulsoup4`, `lxml`, `python-dateutil` — 전 구간이 서버 렌더링 HTML/JSON이라 Selenium/Playwright 불필요.

**council.ulsan.kr 접근 방식**: eGovFrame 표준 게시판. 목록은 `POST /cop/bbs/anonymous/selectBoardList.do` (`bbsId`, `pageIndex`, `searchCnd`, `searchWrd` 등 폼 필드), 상세는 `GET /cop/bbs/selectBoardArticle.do?bbsId=&nttId=`. `(bbs_id, nttId)`가 유일하고 변하지 않는 자연키이므로 모든 게시판 테이블의 dedup 기준으로 사용한다. 페이지네이션은 이미 저장된 nttId만 나오는 페이지를 만나면 중단(신규 실행마다 1~2페이지만 확인하면 되는 구조).

**CLIK 접근 방식**: `GET https://clik.nanet.go.kr/openapi/minutes.do?key=&type=json&displayType=list&searchType=RASMBLY_NM&searchKeyword=울산광역시의회&startCount=&listCount=` 로 날짜 내림차순 페이지네이션 (`rasmblyId` 단독 필터는 동작 확인 안 됨 — `searchType=RASMBLY_NM`+`searchKeyword` 조합만 검증됨, 구현 시작 시 재확인). `RASMBLY_NUMPR != 9` 또는 `MTG_DE < 2026-07-06`을 만나면 중단. 각 항목의 `DOCID`로 `displayType=detail` 상세 조회 → `MINTS_HTML` 저장 및 파싱.
API 키는 문서에 공개된 데모 키(`e1a7f967a146465aaf8721392e50e7a9`, 개발/검증 확인 완료)로 우선 개발하되, **사용자가 clik.nanet.go.kr에 직접 회원가입 후 "인증키신청" 메뉴에서 정식 키를 발급받아야 함** (계정 생성은 대행 불가 — 사용자 액션 필요).

**대수(9) 필터링 규칙**:
- `freeSpeech`/`municipalQna`/`writtenQna`/`bills`: 행에 명시된 `대수`/`(9대)` 값으로 필터, 9가 아닌 첫 행에서 페이지네이션 중단.
- `plenary`/`committee`/`press`: 명시 컬럼 없음 → `posted_date >= 2026-07-06` 기준 필터 겸 중단 조건.
- CLIK: `RASMBLY_NUMPR == 9` 필드로 직접 필터 가능(가장 신뢰도 높음).

**회원명 매칭**: 22명 로스터를 먼저 스크랩해 `{정규화된 이름: member_id}` 캐시를 만들고, 이후 모든 보드(연설/보도자료/의안 발의자/CLIK 발언자)는 정확 일치로만 매칭 — 인원이 22명뿐이라 퍼지 매칭은 오히려 위험. 매칭 실패 시(시청 공무원 발언 등) `member_id`는 NULL로 남겨 "일반 뉴스/타 발언자"로 구분.

**멱등성**: 모든 테이블에 `UNIQUE(bbs_id, ntt_id)` 또는 `UNIQUE(clik_docid)` / `UNIQUE(bill_number)` 제약 + `INSERT ... ON CONFLICT DO UPDATE`로 `last_seen_at`/조회수만 갱신, `first_seen_at`은 최초 삽입 시에만 기록. 스크립트를 몇 번을 다시 실행해도 중복 없이 신규분만 추가된다.

### SQLite 스키마 (요지)

```sql
CREATE TABLE members (
  id INTEGER PRIMARY KEY, member_code TEXT NOT NULL, term INTEGER NOT NULL,
  name TEXT NOT NULL, party TEXT, district TEXT, committee TEXT,
  birth_year INTEGER, phone TEXT, email TEXT, bio TEXT, profile_url TEXT,
  UNIQUE (member_code, term)
);

CREATE TABLE plenary_activities ( ... UNIQUE (bbs_id, ntt_id) );  -- 본회의활동 게시글
CREATE TABLE committee_activities ( ... committee_name, UNIQUE (bbs_id, ntt_id) );

CREATE TABLE bills (
  id INTEGER PRIMARY KEY, bill_number TEXT NOT NULL UNIQUE, bill_name TEXT NOT NULL,
  proposer_type TEXT, proposer_name TEXT, committee TEXT, term INTEGER,
  proposed_date DATE, status TEXT CHECK(status IN ('received','processed')),
  result TEXT, member_id INTEGER REFERENCES members(id), source_url TEXT
);

CREATE TABLE attendance_records (
  member_id INTEGER REFERENCES members(id), term INTEGER, half TEXT,
  meeting_type TEXT, attended INTEGER, total INTEGER, pct REAL,
  UNIQUE (member_id, term, half, meeting_type)
);

CREATE TABLE speeches (   -- 5분자유발언/시정질문/서면질문 게시판 메타(제목 인덱스)
  id INTEGER PRIMARY KEY, bbs_id TEXT, ntt_id TEXT, kind TEXT
    CHECK(kind IN ('free_speech','municipal_qna','written_qna')),
  term INTEGER, session_round TEXT, committee TEXT,
  member_name TEXT NOT NULL, member_id INTEGER REFERENCES members(id),
  title TEXT, posted_date DATE, source_url TEXT, UNIQUE (bbs_id, ntt_id)
);

CREATE TABLE news_items (  -- 보도자료 → 타임라인
  id INTEGER PRIMARY KEY, bbs_id TEXT DEFAULT 'press', ntt_id TEXT,
  title TEXT NOT NULL, author_raw TEXT, member_id INTEGER REFERENCES members(id),
  posted_date DATE NOT NULL, source_url TEXT, UNIQUE (bbs_id, ntt_id)
);

-- CLIK 회의록 전문 + 발언 세그먼트 (핵심 신규 테이블)
CREATE TABLE minutes (
  id INTEGER PRIMARY KEY, clik_docid TEXT NOT NULL UNIQUE, term INTEGER NOT NULL,
  session_no TEXT, round_no TEXT, meeting_type TEXT NOT NULL, meeting_date DATE NOT NULL,
  agenda_summary TEXT, raw_html TEXT, fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE speech_segments (
  id INTEGER PRIMARY KEY, minutes_id INTEGER NOT NULL REFERENCES minutes(id),
  seq INTEGER NOT NULL, speaker_role TEXT, speaker_name TEXT,
  member_id INTEGER REFERENCES members(id),   -- NULL이면 시청 공무원 등 비의원 발언
  agenda_item TEXT, text TEXT NOT NULL,
  UNIQUE (minutes_id, seq)
);
CREATE INDEX idx_segments_member ON speech_segments(member_id);

CREATE TABLE scrape_log (id INTEGER PRIMARY KEY, board TEXT, started_at TIMESTAMP,
  finished_at TIMESTAMP, new_rows INTEGER, status TEXT, error_msg TEXT);
```

`minutes.py`의 `MINTS_HTML` 파싱: `div.contents-block.speaker-block` 요소마다 `<strong>` 안의 역할/이름(때로 `<a class="member_profile">`로 감싸짐)을 추출해 로스터와 이름 매칭, 직전에 지나온 `item-in-contents`(의사일정 항목)를 `agenda_item`으로 태깅, 나머지 텍스트를 `text`로 저장.

**구현 착수 전 실제 확인 필요한 것** (미검증 항목): ~~`attendanceStatistics.do`의 대수/전후반기 전환이 GET 쿼리인지 POST인지, `receiptBill`/`processingBill`의 정확한 공유 컬럼셋과 요청 방식, `municipalQna`/`writtenQna`가 `freeSpeech`와 완전히 동일한 행 구조인지~~ → **이슈 #1에서 검증 완료, [scraper/ENDPOINTS.md](./scraper/ENDPOINTS.md) 참고** (출석률=POST `sDaesu`/`sCate`, 접수의안=`acceptanceBill`, 발의 의원명은 `view.do` 상세, qna 3개 게시판 컬럼 구조 상이). CLIK도 이슈 #5에서 검증 완료: 상세 파라미터명은 소문자 `docid`, **공개 데모 키는 페이지네이션 무시·최신 5건만 반환**(정식 키 발급 필요). `rasmblyId` 단독 필터는 데모 키 제한으로 확인 불가 — `searchType=RASMBLY_NM`+`searchKeyword` 조합 사용.

---

## 4. SvelteKit 프론트엔드 설계

**어댑터**: `@sveltejs/adapter-static`. 모든 라우트(대시보드 1개 + 의원 상세 ~22개)가 빌드 시점에 이미 결정되는 정적 사이트이므로 런타임 서버가 필요 없다. `better-sqlite3`는 `src/lib/server/`(SvelteKit이 클라이언트 번들에서 자동 제외)에서 빌드 시점에만 사용. `svelte.config.js`에 `strict: true`로 프리렌더 누락을 빌드 실패로 잡는다. Cloudflare Pages는 빌드 명령 `npm run build`, 출력 디렉토리 `build`로 설정.

**스타일링 스택**: Tailwind (`darkMode: 'class'`), shadcn-svelte(`neutral` 프리셋으로 init — 기본 blue accent를 절대 쓰지 않기 위함), iconoir-svelte(개별 아이콘 import, `color`는 항상 `currentColor` 상속). 한글 폰트는 Pretendard 자체 호스팅(`@fontsource-variable/pretendard`).

**다크모드**: `app.html`의 인라인 블로킹 스크립트가 `localStorage`/`prefers-color-scheme`을 읽어 hydration 전에 `.dark` 클래스 적용(FOUC 방지), `DarkModeToggle` 컴포넌트가 토글 + 영속화.

**대시보드 레이아웃** (데스크톱 3열 → 모바일 4단): 단일 CSS Grid, `grid-template-areas`로 `"activity" "roster" "attendance" "timeline"` (모바일) → `lg:` (1024px) 브레이크포인트에서 `"activity center timeline"` 3열(대략 25%/50%/25%, `minmax(280px,1fr) minmax(480px,2fr) minmax(280px,1fr)`)로 전환, `center` 영역 내부는 `flex-col`로 의원명단(위)/출석율(아래) 분할. DOM 중복 없이 동일 4개 `<section>`이 그리드 영역만 바뀌는 방식. 좌측(활동)·우측(타임라인) 컬럼은 데스크톱에서 `sticky` + `overflow-y-auto`로 내부 스크롤. 모바일 스택 순서는 확정된 대로 **활동 → 의원명단 → 출석율 → 타임라인**.

**컴포넌트**: `ActivityFeed`/`ActivityFeedItem`(본회의/위원회 배지 + 의안 접수/처리 항목), `MemberRoster`/`MemberCard`(카드 전체가 실제 `<a>`, 정당 배지), `AttendancePanel`/`AttendanceRow`(차트 라이브러리 없이 그레이스케일 막대 + 정당색 점), `Timeline`/`TimelineItem`(내부 스크롤 영역, `role="region" aria-label`, 최신순), 의원 상세 페이지의 `MemberHeader` + `MemberActivityTabs`(전체/5분자유발언/시정질문/서면질문/의안/보도자료 탭 — CLIK `speech_segments`에서 가져온 실제 발언 원문이 핵심 콘텐츠).

**색상 시스템**: 전체 그레이스케일, 정당색만 예외. 국민의힘(`#E61E2B`)과 진보당 브랜드색(`#D6001C`)이 색상 충돌 위험이 있어 진보당을 `#C81E45`(색상 회전)로 구분, OKLCH 공간에서 라이트/다크 모드별 텍스트-세이프 변형을 도출(예: culori 패키지로 L값 조정). 정당 배지는 색상뿐 아니라 항상 텍스트(정당명)를 함께 표시(WCAG 1.4.1 대응). CSS custom property로 `:root`/`.dark`에 각각 선언해 컴포넌트는 `var(--party-{id}-brand)`만 참조.

**SEO**: 라우트별 `<svelte:head>`(제목/설명/OG/Twitter카드/canonical) 공통화한 `SeoHead.svelte`, `<html lang="ko">`, 빌드 시 정적 파일로 떨어지는 `sitemap.xml`/`robots.txt` 라우트(`+server.ts` + `prerender=true`), 시맨틱 랜드마크(`nav`/`main`/`section aria-labelledby`/`article`).

**접근성**: 카드는 실제 `<a>`(div+onclick 금지), 전역 `focus-visible` 링, 그레이스케일 텍스트는 gray-600 이하로 대비 확보, 아이콘 전용 버튼에 동적 `aria-label`, skip-to-content 링크, `motion-safe`/`motion-reduce` 분기, 타임라인 스크롤 영역에 `role="region"`+`tabindex="0"`, 외부 링크에 `target="_blank" rel="noopener noreferrer"` + 스크린리더용 안내.

### 데이터 계약 (TS 타입, 요지)

```typescript
interface Member { memCode: string; slug: string; name: string; partyId: PartyId;
  district: string; photoUrl: string|null; committees: {committeeName:string; role:string}[];
  bio: string[]; contact?: {phone?:string; email?:string}; }
interface AttendanceRecord { memCode: string; totalSessions: number; attended: number; rate: number; periodLabel: string; }
interface PlenaryOrCommitteeActivity { id:string; kind:'activity'; type:'본회의'|'위원회'; committeeName?:string;
  title:string; date:string; sourceUrl?:string; }
interface Bill { id:string; kind:'bill'; billNo:string; title:string; proposedDate:string;
  status:'received'|'processed'; statusLabel:string; proposers:{memCode:string; name:string}[]; }
interface NewsItem { id:string; kind:'news'; title:string; publishedDate:string; sourceUrl:string; relatedMemCodes?:string[]; }
interface SpeechSegment { id:string; kind:'speech'; memCode:string; meetingType:string; agendaItem:string;
  date:string; text:string; minutesSourceUrl?:string; }
type MemberFeedItem = SpeechSegment | Bill | NewsItem | PlenaryOrCommitteeActivity;
```

---

## 5. 구현 순서 (제안)

1. `scraper/`: council.ulsan.kr 미검증 엔드포인트(출석률/의안/qna) 실제 요청 형태 확인 → `members.py` → `attendance.py`/`bills.py`/게시판류 → `clik_client.py` + `minutes.py`(파싱 포함) → `run.py` 통합, `data/council.sqlite3` 최초 생성.
2. SvelteKit 프로젝트 부트스트랩(`npx sv create .`, TypeScript) → Tailwind/shadcn-svelte/iconoir 세팅 → `lib/server/db.ts` + 쿼리 레이어(스키마 확정 후).
3. 대시보드 4개 패널 컴포넌트 → 레이아웃 그리드 → 의원 상세 페이지 → 다크모드/정당색 시스템 → SEO/A11y 마무리.
4. Cloudflare Pages 연결(GitHub 저장소 이미 존재), 빌드 확인.

## 6. 검증 방법

- 스크래퍼: `python scraper/run.py` 1회 실행 후 SQLite에 각 테이블 행 수 확인, 동일 명령 재실행 시 `new_rows=0`(또는 신규 게시물만) 확인해 멱등성 검증.
- 프론트엔드: `npm run dev`로 로컬 구동 → 브라우저로 대시보드 4패널 확인, 모바일 뷰포트(375px)에서 스택 순서 확인, 다크모드 토글, 의원 카드 클릭 → 상세 페이지 이동, 상세 페이지에서 실제 발언 텍스트 노출 확인.
- `npm run build` (adapter-static) 성공 여부 + `build/sitemap.xml`/`robots.txt` 생성 확인.
- Lighthouse(SEO/접근성 카테고리)로 기본 점검.
