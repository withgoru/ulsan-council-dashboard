import { getActiveIssues, getEndedIssues } from '$lib/server/media';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = () => {
	return { active: getActiveIssues(), ended: getEndedIssues() };
};
