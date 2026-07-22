# ulsan-council-dashboard

울산광역시의회(https://www.council.ulsan.kr) 제9대(9기) 의정활동을 시각화하는 공개 대시보드입니다.

## 개요

- **목적**: 본회의/위원회 활동, 의원별 회의출석률, 의원명단, 의안 접수/처리, 의정 관련 뉴스 타임라인, 그리고 의원별로 실제 발언 내용을 모아 보여주는 개별 페이지를 제공합니다.
- **데이터 수집**: Python 스크래퍼(`scraper/`)가 council.ulsan.kr 게시판과 국회도서관 CLIK 지방의회 회의록 Open API(https://clik.nanet.go.kr)를 주기적으로 스크래핑해 로컬 SQLite(`data/council.sqlite3`)에 누적 저장합니다. 9대 임기(2026-07-06 개원)가 진행되는 4년간 반복 실행하며 데이터를 쌓아가는 구조입니다.
- **웹앱**: SvelteKit(`src/`)이 빌드 시점에 SQLite를 읽어 정적 사이트로 생성되고, Cloudflare Pages에 배포됩니다. 런타임 서버나 DB 접속이 없습니다.

## 기술 스택

- Frontend: SvelteKit, Svelte, Tailwind CSS, shadcn-svelte, iconoir-svelte
- Data: Python(requests, BeautifulSoup4) + SQLite
- Deploy: Cloudflare Pages (`@sveltejs/adapter-static`)
- 다크모드 지원, 모바일 퍼스트, SEO/웹 접근성(WCAG) 준수, 그레이스케일 UI + 정당 고유 컬러 포인트

## 문서

- 기획안 및 아키텍처 상세: [PLAN.md](./PLAN.md)
- 작업 규칙(GitHub 워크플로우 등): [PROMPT.md](./PROMPT.md)

## 개발 시작하기

```bash
# 스크래퍼 (uv 사용). 최초 1회: cp .env.example .env
cd scraper
uv run python run.py          # 전체 수집(멱등 — 재실행 시 신규분만 추가)
# 개별 단계: uv run python members.py / uv run python -m boards.bills / uv run python minutes.py

# 웹앱
npm install
npm run dev
```

> CLIK 회의록 전량 수집에는 정식 API 키가 필요합니다(공개 데모 키는 최신 5건만 반환).
> clik.nanet.go.kr에서 발급 후 `.env`의 `CLIK_API_KEY`에 설정하세요. 상세: [scraper/ENDPOINTS.md](./scraper/ENDPOINTS.md).
