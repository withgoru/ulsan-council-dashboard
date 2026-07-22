-- 울산광역시의회 대시보드 SQLite 스키마
-- PLAN.md 3절 기반. 모든 테이블은 멱등 수집을 위해 자연키 UNIQUE 제약 +
-- ON CONFLICT DO UPDATE(last_seen_at/조회수 등만 갱신)로 재실행 시 중복이 없다.
-- 실행: db.py init_db() 가 이 파일을 executescript 로 적용(IF NOT EXISTS 안전).

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ── 의원명단 ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS members (
  id           INTEGER PRIMARY KEY,
  member_code  TEXT    NOT NULL,          -- council.ulsan.kr 내부 의원 식별자
  term         INTEGER NOT NULL,          -- 대수 (9)
  name         TEXT    NOT NULL,
  party        TEXT,
  district     TEXT,
  committee    TEXT,                       -- 대표 소속 위원회(직책 상세는 별도 필요 시 확장)
  birth_year   INTEGER,
  phone        TEXT,
  email        TEXT,
  bio          TEXT,                        -- 약력(줄바꿈 구분 원문)
  profile_url  TEXT,
  photo_url    TEXT,
  first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_seen_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (member_code, term)
);

-- ── 본회의 활동 게시글 ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS plenary_activities (
  id           INTEGER PRIMARY KEY,
  bbs_id       TEXT    NOT NULL,
  ntt_id       TEXT    NOT NULL,
  term         INTEGER,
  session_round TEXT,                       -- "265회 4차" 등
  title        TEXT    NOT NULL,
  posted_date  DATE,
  view_count   INTEGER,
  source_url   TEXT,
  first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_seen_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (bbs_id, ntt_id)
);

-- ── 위원회 활동 게시글 ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS committee_activities (
  id           INTEGER PRIMARY KEY,
  bbs_id       TEXT    NOT NULL,
  ntt_id       TEXT    NOT NULL,
  term         INTEGER,
  committee_name TEXT,
  session_round TEXT,
  title        TEXT    NOT NULL,
  posted_date  DATE,
  view_count   INTEGER,
  source_url   TEXT,
  first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_seen_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (bbs_id, ntt_id)
);

-- ── 의안(접수/처리/계류) ────────────────────────────────────────────────────
-- 목록엔 제안자 "유형"만, 실제 발의 의원명은 view.do 상세의 제안의원 필드(ENDPOINTS.md 2절).
CREATE TABLE IF NOT EXISTS bills (
  id            INTEGER PRIMARY KEY,
  bill_number   TEXT    NOT NULL UNIQUE,    -- 화면 의안번호
  detail_idx    TEXT,                        -- view.do 내부 idx (fnView 인자)
  bill_name     TEXT    NOT NULL,
  proposer_type TEXT,                        -- 의장/의원/시장/교육감/위원장/기타
  proposer_name TEXT,                        -- 상세에서 취득한 실제 발의자명(있으면)
  committee     TEXT,                        -- 소관상임위
  term          INTEGER,
  session_round TEXT,                        -- "9대 / 265회"
  proposed_date DATE,
  status        TEXT CHECK (status IN ('acceptance', 'processing', 'mooring')),
  result        TEXT,                         -- 본회의처리결과(원안가결/철회/보류 등)
  member_id     INTEGER REFERENCES members(id),
  source_url    TEXT,
  first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_seen_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── 출석률 ──────────────────────────────────────────────────────────────────
-- attendanceStatistics.do POST(sDaesu, sCate). meeting_type 은 표 헤더에서 읽은 위원회명.
CREATE TABLE IF NOT EXISTS attendance_records (
  id           INTEGER PRIMARY KEY,
  member_id    INTEGER REFERENCES members(id),
  member_name  TEXT    NOT NULL,             -- 매칭 실패 대비 원문 이름 보존
  term         INTEGER NOT NULL,
  half         TEXT    NOT NULL,             -- 전반기/후반기
  meeting_type TEXT    NOT NULL,             -- 본회의/운영위/행자위/...
  attended     INTEGER,
  total        INTEGER,
  pct          REAL,
  last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (member_id, term, half, meeting_type)
);

-- ── 5분자유발언/시정질문/서면질문 게시판 메타(제목 인덱스) ───────────────────
CREATE TABLE IF NOT EXISTS speeches (
  id           INTEGER PRIMARY KEY,
  bbs_id       TEXT    NOT NULL,
  ntt_id       TEXT    NOT NULL,
  kind         TEXT    NOT NULL CHECK (kind IN ('free_speech', 'municipal_qna', 'written_qna')),
  term         INTEGER,
  session_round TEXT,
  committee    TEXT,                          -- free_speech 만 채워짐(나머지 NULL)
  member_name  TEXT    NOT NULL,
  member_id    INTEGER REFERENCES members(id),
  title        TEXT,
  posted_date  DATE,
  view_count   INTEGER,
  source_url   TEXT,
  first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_seen_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (bbs_id, ntt_id)
);

-- ── 보도자료 → 뉴스 타임라인 ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS news_items (
  id           INTEGER PRIMARY KEY,
  bbs_id       TEXT    NOT NULL DEFAULT 'press',
  ntt_id       TEXT    NOT NULL,
  title        TEXT    NOT NULL,
  author_raw   TEXT,
  member_id    INTEGER REFERENCES members(id),
  posted_date  DATE    NOT NULL,
  view_count   INTEGER,
  source_url   TEXT,
  first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_seen_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (bbs_id, ntt_id)
);

-- ── CLIK 회의록 전문 ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS minutes (
  id            INTEGER PRIMARY KEY,
  clik_docid    TEXT    NOT NULL UNIQUE,
  term          INTEGER NOT NULL,
  session_no    TEXT,                         -- 회기(회)
  round_no      TEXT,                         -- 차수(차)
  meeting_type  TEXT    NOT NULL,             -- 본회의/위원회명
  meeting_date  DATE    NOT NULL,
  agenda_summary TEXT,
  raw_html      TEXT,                          -- MINTS_HTML 원문 보존
  fetched_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── CLIK 발언 세그먼트(화자별) ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS speech_segments (
  id           INTEGER PRIMARY KEY,
  minutes_id   INTEGER NOT NULL REFERENCES minutes(id),
  seq          INTEGER NOT NULL,
  speaker_role TEXT,                           -- 의장/위원장/의원/시장 등 역할 텍스트
  speaker_name TEXT,
  member_id    INTEGER REFERENCES members(id), -- NULL이면 시청 공무원 등 비의원 발언
  agenda_item  TEXT,                            -- 직전 의사일정 항목 태그
  text         TEXT    NOT NULL,
  UNIQUE (minutes_id, seq)
);
CREATE INDEX IF NOT EXISTS idx_segments_member ON speech_segments(member_id);
CREATE INDEX IF NOT EXISTS idx_segments_minutes ON speech_segments(minutes_id);

-- ── 외부 언론 기사 후보 풀(네이버 뉴스 검색) ────────────────────────────────
-- 자동 수집된 후보. 실제 공개는 큐레이션(data/media-curation.json)에서 승인한 것만.
CREATE TABLE IF NOT EXISTS media_articles (
  id           INTEGER PRIMARY KEY,
  url          TEXT    NOT NULL UNIQUE,   -- 원문 링크(dedup 자연키)
  title        TEXT    NOT NULL,          -- HTML 태그 제거된 제목
  description  TEXT,                       -- 요약(태그 제거)
  press        TEXT,                       -- 언론사(추출 가능 시)
  published_at DATE,                        -- 보도일(pubDate)
  query        TEXT,                        -- 어떤 검색어로 걸렸는지
  first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_seen_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_media_published ON media_articles(published_at);

-- ── 스크랩 실행 로그 ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS scrape_log (
  id           INTEGER PRIMARY KEY,
  board        TEXT,
  started_at   TIMESTAMP,
  finished_at  TIMESTAMP,
  new_rows     INTEGER,
  status       TEXT,                            -- ok / error
  error_msg    TEXT
);
