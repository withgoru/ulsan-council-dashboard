import { getActivities, getAvailableYears, getBills } from '$lib/server/queries';
import type { Activity, Bill } from '$lib/types';
import type { PageServerLoad } from './$types';

// 활동·의안 전체 목록(연도 필터는 클라이언트에서 ?year 로 처리).
export const load: PageServerLoad = () => {
	const feed: (Activity | Bill)[] = [...getActivities(), ...getBills()].sort((a, b) => {
		const da = a.kind === 'activity' ? (a.date ?? '') : (a.proposedDate ?? '');
		const db = b.kind === 'activity' ? (b.date ?? '') : (b.proposedDate ?? '');
		return db.localeCompare(da);
	});
	return { feed, years: getAvailableYears() };
};
