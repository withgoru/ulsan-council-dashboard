import { getCuratedArticles } from '$lib/server/media';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = () => {
	return { articles: getCuratedArticles() };
};
