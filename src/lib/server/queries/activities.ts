import { all } from '$lib/server/db';
import { toActivity, type ActivityRow } from '$lib/server/mappers';
import type { Activity } from '$lib/types';

const PLENARY = `SELECT id, title, session_round, posted_date, view_count, source_url
	FROM plenary_activities`;
const COMMITTEE = `SELECT id, committee_name, title, session_round, posted_date, view_count, source_url
	FROM committee_activities`;

export function getPlenaryActivities(): Activity[] {
	return all<ActivityRow>(`${PLENARY} ORDER BY posted_date DESC, id DESC`).map((r) =>
		toActivity(r, '본회의')
	);
}

export function getCommitteeActivities(): Activity[] {
	return all<ActivityRow>(`${COMMITTEE} ORDER BY posted_date DESC, id DESC`).map((r) =>
		toActivity(r, '위원회')
	);
}

/** 본회의+위원회 활동 통합, 최신순. */
export function getActivities(limit?: number): Activity[] {
	const merged = [...getPlenaryActivities(), ...getCommitteeActivities()].sort((a, b) =>
		(b.date ?? '').localeCompare(a.date ?? '')
	);
	return limit ? merged.slice(0, limit) : merged;
}
