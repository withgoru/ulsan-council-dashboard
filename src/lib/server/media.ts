// 큐레이션 승인 기사 로더. data/media-curation.json(커밋됨)을 읽어 표시 순서대로 반환.
// 후보 풀(media_articles, SQLite)은 큐레이션 페이지에서만 쓰고, 공개 빌드는 이 JSON만 본다.
import curation from '$lib/data/media-curation.json';
import type { CuratedArticle } from '$lib/types';

export function getCuratedArticles(): CuratedArticle[] {
	const list = (curation.articles ?? []) as CuratedArticle[];
	// 최신 보도일 우선(동일/누락 시 원래 순서 유지).
	return [...list].sort((a, b) => (b.publishedAt ?? '').localeCompare(a.publishedAt ?? ''));
}
