// 사이트 전역 메타데이터(SEO/OG 공통값). 배포 도메인은 이슈 #13에서 확정 시 url 갱신.
export const SITE = {
	name: '울산광역시의회 의정활동 대시보드',
	shortName: '울산시의회 대시보드',
	description:
		'제9대 울산광역시의회의 본회의·위원회 활동, 의원별 발언 원문, 의안, 회의 출석률, 보도자료를 한눈에 볼 수 있는 공개 대시보드입니다.',
	// 프로덕션 canonical 기준 URL(끝 슬래시 없음). Cloudflare Pages 연결 후 실제 도메인으로 교체.
	url: 'https://ulsan-council-dashboard.pages.dev',
	locale: 'ko_KR',
	ogImage: '/og-default.png' // static/og-default.png (없으면 크롤러가 무시)
} as const;

/** 경로를 절대 canonical URL 로 변환. */
export function canonicalUrl(path: string): string {
	if (!path.startsWith('/')) path = `/${path}`;
	return `${SITE.url}${path === '/' ? '' : path}`;
}
