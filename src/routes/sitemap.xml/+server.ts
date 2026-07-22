import { canonicalUrl } from '$lib/config/site';
import { getMemberSlugs } from '$lib/server/queries';
import type { RequestHandler } from './$types';

export const prerender = true;

// 대시보드 + 의원 상세 22개 정적 sitemap.
export const GET: RequestHandler = () => {
	const paths = ['/', ...getMemberSlugs().map((slug) => `/members/${slug}`)];
	const urls = paths.map((p) => `\t<url><loc>${canonicalUrl(p)}</loc></url>`).join('\n');
	const body = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>`;
	return new Response(body, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};
