import { getAvailableYears, getNews } from '$lib/server/queries';
import type { PageServerLoad } from './$types';

// 보도자료 전체 목록(연도 필터는 클라이언트에서 ?year 로 처리).
export const load: PageServerLoad = () => {
	return { news: getNews(), years: getAvailableYears() };
};
