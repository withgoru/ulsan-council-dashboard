# 작업 규칙

이 저장소에서 작업할 때는 아래 규칙을 반드시 따른다.

## 1. 이슈 우선 (Issue First)

- 어떤 작업이든 시작하기 전에 **먼저 GitHub 이슈를 생성**한다. 이슈 없이 코드를 작성하지 않는다.
- 백로그는 [PLAN.md](./PLAN.md) 내용을 기준으로 생성한다. PLAN.md가 갱신되면 백로그(이슈)도 함께 갱신한다.
- 이슈에는 적절한 라벨(아래 라벨 체계 참고)을 붙인다.

## 2. GitHub Flow

- 이슈마다 `main`에서 새 브랜치를 만든다. 브랜치명 규칙: `issue-<번호>-<짧은-설명>` (예: `issue-3-scraper-members`).
- 해당 브랜치에서만 작업하고 커밋한다. `main`에 직접 커밋하지 않는다.
- 작업이 끝나면 PR을 연다. PR 설명에 관련 이슈를 `Closes #<번호>` 형식으로 링크한다.
- **PR 리뷰/머지는 사용자(저장소 소유자)가 직접 수행한다.** 스스로 PR을 머지하지 않는다.
- PR이 머지된 것이 확인되면, 해당 작업에 사용한 **로컬 브랜치와 원격(origin) 브랜치를 모두 삭제**한다.

## 3. 라벨 체계

| 라벨 | 용도 |
|---|---|
| `area:frontend` | SvelteKit/UI 작업 |
| `area:scraper` | Python 스크래퍼 작업 |
| `area:data` | SQLite 스키마/데이터 모델 작업 |
| `area:infra` | 빌드/배포/Cloudflare Pages/CI 작업 |
| `area:a11y-seo` | 접근성/SEO 작업 |
| `priority:high` / `priority:medium` / `priority:low` | 우선순위 |
| `bug`, `enhancement`, `documentation`, `question` | GitHub 기본 라벨, 이슈 성격 분류 |

## 4. 커밋/PR 컨벤션

- 커밋 메시지는 "무엇"보다 "왜"를 짧게 설명한다.
- PR은 하나의 이슈(하나의 논리적 작업 단위)에 대응하도록 작게 유지한다.
