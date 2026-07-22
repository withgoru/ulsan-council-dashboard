import type { Activity, Bill, MemberFeedItem, NewsItem } from '$lib/types';

/** ISO 날짜 문자열에서 연도(4자리) 추출. 실패 시 null. */
export function yearOf(iso: string | null | undefined): number | null {
	if (!iso) return null;
	const m = iso.match(/^(\d{4})/);
	return m ? Number(m[1]) : null;
}

/** 활동/의안 피드 항목의 연도. */
export function feedItemYear(item: Activity | Bill): number | null {
	return yearOf(item.kind === 'activity' ? item.date : item.proposedDate);
}

export function newsYear(item: NewsItem): number | null {
	return yearOf(item.publishedDate);
}

export function memberFeedYear(item: MemberFeedItem): number | null {
	switch (item.kind) {
		case 'speech':
			return yearOf(item.meetingDate);
		case 'bill':
			return yearOf(item.proposedDate);
		case 'news':
			return yearOf(item.publishedDate);
		default:
			return yearOf(item.date);
	}
}
