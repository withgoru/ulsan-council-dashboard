import {
	getAllMembers,
	getActivities,
	getBills,
	getNews,
	getPlenaryAttendance
} from '$lib/server/queries';
import type { PageServerLoad } from './$types';

// 데이터 레이어 동작 검증용 요약 로드(빌드 시점, better-sqlite3).
// 실제 대시보드 UI 는 이슈 #9에서 이 데이터를 사용해 구성한다.
export const load: PageServerLoad = () => {
	const members = getAllMembers();
	return {
		counts: {
			members: members.length,
			activities: getActivities().length,
			bills: getBills().length,
			news: getNews().length,
			attendance: getPlenaryAttendance().length
		},
		sampleMember: members[0] ?? null
	};
};
