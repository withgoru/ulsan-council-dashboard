// 이슈 타임라인 로더. data/media-curation.json(커밋됨)을 읽어 이슈별로 미디어를 해석.
// 후보 풀(media_articles, SQLite)은 큐레이션 페이지에서만 쓰고, 공개 빌드는 이 JSON만 본다.
import curation from '$lib/data/media-curation.json';
import type { Issue, MediaItem, ResolvedIssue } from '$lib/types';

function itemsMap(): Map<string, MediaItem> {
	const items = (curation.items ?? []) as MediaItem[];
	return new Map(items.map((it) => [it.url, it]));
}

/** 이슈를 해석(itemUrls → items, 최신순). 태깅된 항목만 노출된다. */
function resolve(issue: Issue, map: Map<string, MediaItem>): ResolvedIssue {
	const items = issue.itemUrls
		.map((u) => map.get(u))
		.filter((x): x is MediaItem => Boolean(x))
		.sort((a, b) => (b.publishedAt ?? '').localeCompare(a.publishedAt ?? ''));
	const { itemUrls: _drop, ...rest } = issue;
	void _drop;
	return { ...rest, items };
}

function sortIssues(a: ResolvedIssue, b: ResolvedIssue): number {
	if (a.pinned !== b.pinned) return a.pinned ? -1 : 1;
	if (a.order !== b.order) return a.order - b.order;
	// 최신 미디어가 있는 이슈 우선.
	return (b.items[0]?.publishedAt ?? '').localeCompare(a.items[0]?.publishedAt ?? '');
}

function load(): ResolvedIssue[] {
	const map = itemsMap();
	return ((curation.issues ?? []) as Issue[])
		.filter((i) => i.status !== 'hidden')
		.map((i) => resolve(i, map))
		.filter((i) => i.items.length > 0);
}

/** 진행 중 이슈(pinned→order→최신순). */
export function getActiveIssues(): ResolvedIssue[] {
	return load()
		.filter((i) => i.status === 'active')
		.sort(sortIssues);
}

/** 종료(아카이브) 이슈. */
export function getEndedIssues(): ResolvedIssue[] {
	return load()
		.filter((i) => i.status === 'ended')
		.sort(sortIssues);
}
