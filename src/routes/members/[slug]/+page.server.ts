import { getMemberBySlug, getMemberSlugs } from '$lib/server/queries';
import { error } from '@sveltejs/kit';
import type { EntryGenerator, PageServerLoad } from './$types';

// 프리렌더 엔트리: 전체 의원 slug. (adapter-static 이 정적 페이지로 생성)
export const entries: EntryGenerator = () => getMemberSlugs().map((slug) => ({ slug }));

export const load: PageServerLoad = ({ params }) => {
	const member = getMemberBySlug(params.slug);
	if (!member) error(404, '의원을 찾을 수 없습니다');
	// 상세 콘텐츠(발언 원문·탭 등)는 이슈 #10에서 확장.
	return { member };
};
