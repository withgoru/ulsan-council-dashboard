import {
	getActivities,
	getAllMembers,
	getAttendance,
	getAvailableYears,
	getBills,
	getNews
} from '$lib/server/queries';
import { getCuratedArticles } from '$lib/server/media';
import type { Activity, Bill } from '$lib/types';
import type { PageServerLoad } from './$types';

// 대시보드 데이터(빌드 시점 프리렌더). 활동 피드 = 본회의/위원회 활동 + 의안(날짜 최신순).
// 연도 필터는 클라이언트에서 처리하므로 전체를 넘기고, 화면에는 선택 연도 상위 10건만 렌더한다.
export const load: PageServerLoad = () => {
	const feed: (Activity | Bill)[] = [...getActivities(), ...getBills()].sort((a, b) => {
		const da = a.kind === 'activity' ? (a.date ?? '') : (a.proposedDate ?? '');
		const db = b.kind === 'activity' ? (b.date ?? '') : (b.proposedDate ?? '');
		return db.localeCompare(da);
	});

	return {
		feed,
		news: getNews(),
		members: getAllMembers(),
		attendance: getAttendance(),
		years: getAvailableYears(),
		media: getCuratedArticles()
	};
};
