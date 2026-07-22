import { all } from '$lib/server/db';
import { toNews, type NewsRow } from '$lib/server/mappers';
import type { NewsItem } from '$lib/types';

const SELECT = `
	SELECT n.id, n.title, n.author_raw, m.member_code AS member_code,
	       n.posted_date, n.view_count, n.source_url
	FROM news_items n
	LEFT JOIN members m ON n.member_id = m.id`;

/** 보도자료 타임라인(최신순). */
export function getNews(limit?: number): NewsItem[] {
	const rows = all<NewsRow>(`${SELECT} ORDER BY n.posted_date DESC, n.id DESC`).map(toNews);
	return limit ? rows.slice(0, limit) : rows;
}

/** 특정 의원 관련 보도자료. */
export function getNewsByMember(memCode: string): NewsItem[] {
	return all<NewsRow>(
		`${SELECT} WHERE m.member_code = ? ORDER BY n.posted_date DESC, n.id DESC`,
		memCode
	).map(toNews);
}
