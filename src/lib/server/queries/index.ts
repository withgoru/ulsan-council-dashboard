// 쿼리 배럴 + 의원 상세 통합 피드 빌더.
export * from './members';
export * from './attendance';
export * from './activities';
export * from './bills';
export * from './news';
export * from './speeches';

import { getBillsByMember } from './bills';
import { getNewsByMember } from './news';
import { getSegmentsByMember, getSpeechBoardByMember } from './speeches';
import type { MemberFeedItem } from '$lib/types';

/** 의원 상세 페이지용 통합 피드(발언원문/발언게시판/의안/보도자료), 날짜 최신순.
 *  SpeechSegment 는 meetingDate, 나머지는 각자의 날짜 필드로 정렬한다. */
export function getMemberFeed(memCode: string): MemberFeedItem[] {
	const items: MemberFeedItem[] = [
		...getSegmentsByMember(memCode),
		...getSpeechBoardByMember(memCode),
		...getBillsByMember(memCode),
		...getNewsByMember(memCode)
	];
	const dateOf = (it: MemberFeedItem): string => {
		switch (it.kind) {
			case 'speech':
				return it.meetingDate ?? '';
			case 'bill':
				return it.proposedDate ?? '';
			case 'news':
				return it.publishedDate ?? '';
			case 'speech-board':
			case 'activity':
				return it.date ?? '';
		}
	};
	return items.sort((a, b) => dateOf(b).localeCompare(dateOf(a)));
}
