<script lang="ts">
	import type { CuratedArticle } from '$lib/types';
	import { formatDate } from '$lib/utils/date';
	import Journal from '~icons/iconoir/journal';
	import OpenNewWindow from '~icons/iconoir/open-new-window';
	import NavArrowRight from '~icons/iconoir/nav-arrow-right';

	// '언론이 본 의회': 큐레이션으로 승인된 외부 언론 기사만 노출(승인제).
	let { articles, moreHref }: { articles: CuratedArticle[]; moreHref?: string } = $props();
</script>

<section aria-labelledby="media-heading" class="flex min-h-0 flex-1 flex-col">
	<h2 id="media-heading" class="mb-2 shrink-0 text-sm font-semibold tracking-tight">
		언론이 본 의회
	</h2>

	{#if articles.length}
		<div>
			{#each articles as a (a.url)}
				<article class="flex flex-col gap-1 border-b border-border/70 py-3 last:border-0">
					<div class="flex items-center gap-2 text-xs text-muted-foreground">
						{#if a.publishedAt}<time class="tabular-nums">{formatDate(a.publishedAt)}</time>{/if}
						{#if a.press}<span>· {a.press}</span>{/if}
					</div>
					<a
						href={a.url}
						target="_blank"
						rel="noopener noreferrer"
						class="group inline-flex items-start gap-1 text-sm leading-snug font-medium hover:underline"
					>
						<span>{a.title}</span>
						<OpenNewWindow
							class="mt-0.5 size-3 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100"
						/>
						<span class="sr-only">(새 창)</span>
					</a>
					{#if a.note}<p class="text-xs text-muted-foreground">{a.note}</p>{/if}
				</article>
			{/each}
		</div>
		{#if moreHref}
			<a
				href={moreHref}
				class="mt-3 inline-flex items-center gap-0.5 self-start text-xs font-medium text-muted-foreground hover:text-foreground hover:underline"
			>
				전체 보기 <NavArrowRight class="size-3.5" />
			</a>
		{/if}
	{:else}
		<div
			class="flex flex-1 flex-col items-center justify-center gap-2 rounded-lg border border-dashed p-6 text-center text-muted-foreground"
		>
			<Journal class="size-8 opacity-60" />
			<p class="text-sm font-medium">외부 언론 보도 타임라인</p>
			<p class="text-xs leading-relaxed">아직 큐레이션된 기사가 없습니다.</p>
		</div>
	{/if}
</section>
