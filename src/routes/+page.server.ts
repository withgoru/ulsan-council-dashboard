import {
	getActivities,
	getAllMembers,
	getBills,
	getNews,
	getPlenaryAttendance
} from '$lib/server/queries';
import type { Activity, Bill } from '$lib/types';
import type { PageServerLoad } from './$types';

// 대시보드 데이터(빌드 시점 프리렌더). 활동 피드는 본회의/위원회 활동 + 의안을 날짜 최신순 병합.
export const load: PageServerLoad = () => {
	const feed: (Activity | Bill)[] = [...getActivities(), ...getBills()].sort((a, b) => {
		const da = a.kind === 'activity' ? (a.date ?? '') : (a.proposedDate ?? '');
		const db = b.kind === 'activity' ? (b.date ?? '') : (b.proposedDate ?? '');
		return db.localeCompare(da);
	});

	return {
		feed,
		members: getAllMembers(),
		attendance: getPlenaryAttendance(),
		news: getNews()
	};
};
