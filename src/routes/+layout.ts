// 전 라우트 정적 프리렌더(adapter-static). 런타임 서버 없이 빌드 시점에 SQLite를 읽어
// 정적 HTML을 생성한다. 새 라우트도 기본 프리렌더되며, 누락 시 strict 모드가 빌드를 실패시킨다.
export const prerender = true;
