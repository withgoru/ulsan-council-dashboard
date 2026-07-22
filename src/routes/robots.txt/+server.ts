import { SITE } from '$lib/config/site';
import type { RequestHandler } from './$types';

export const prerender = true;

// 전체 크롤 허용 + sitemap 위치 안내.
export const GET: RequestHandler = () => {
	const body = `User-agent: *
Allow: /

Sitemap: ${SITE.url}/sitemap.xml
`;
	return new Response(body, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
