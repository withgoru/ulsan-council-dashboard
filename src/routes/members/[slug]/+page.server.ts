import {
	getAttendanceByMember,
	getBillsByMember,
	getMemberBySlug,
	getMemberFeed,
	getMemberSlugs,
	getNewsByMember,
	getSegmentsByMember,
	getSpeechBoardByMember
} from '$lib/server/queries';
import { error } from '@sveltejs/kit';
import type { EntryGenerator, PageServerLoad } from './$types';

// 프리렌더 엔트리: 전체 의원 slug.
export const entries: EntryGenerator = () => getMemberSlugs().map((slug) => ({ slug }));

export const load: PageServerLoad = ({ params }) => {
	const member = getMemberBySlug(params.slug);
	if (!member) error(404, '의원을 찾을 수 없습니다');

	const code = member.memCode;
	return {
		member,
		attendance: getAttendanceByMember(code),
		feed: getMemberFeed(code), // 전체 탭(발언·게시판·의안·보도자료 통합, 최신순)
		segments: getSegmentsByMember(code), // 회의록 실제 발언 원문(핵심)
		speechBoard: getSpeechBoardByMember(code), // 5분자유발언/시정질문/서면질문 메타
		bills: getBillsByMember(code),
		news: getNewsByMember(code)
	};
};
