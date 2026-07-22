import { all } from '$lib/server/db';

/** 활동/의안/보도자료의 게시일에서 추출한 사용 가능한 연도(내림차순). 연도 필터 옵션. */
export function getAvailableYears(): number[] {
	const rows = all<{ y: string }>(`
		SELECT DISTINCT substr(posted_date, 1, 4) AS y FROM plenary_activities WHERE posted_date IS NOT NULL
		UNION SELECT DISTINCT substr(posted_date, 1, 4) FROM committee_activities WHERE posted_date IS NOT NULL
		UNION SELECT DISTINCT substr(proposed_date, 1, 4) FROM bills WHERE proposed_date IS NOT NULL
		UNION SELECT DISTINCT substr(posted_date, 1, 4) FROM news_items WHERE posted_date IS NOT NULL
	`);
	return rows
		.map((r) => Number(r.y))
		.filter((y) => Number.isFinite(y))
		.sort((a, b) => b - a);
}
