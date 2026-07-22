<script lang="ts">
	import type { NewsItem } from '$lib/types';
	import TimelineItem from './TimelineItem.svelte';
	import NavArrowRight from '~icons/iconoir/nav-arrow-right';

	let {
		items,
		title = '보도자료 타임라인',
		moreHref
	}: { items: NewsItem[]; title?: string; moreHref?: string } = $props();
</script>

<section aria-label={title} class="flex flex-col">
	<h2 class="mb-2 text-sm font-semibold tracking-tight">{title}</h2>
	{#if items.length}
		<div>
			{#each items as item (item.id)}
				<TimelineItem {item} />
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
		<p class="py-8 text-center text-sm text-muted-foreground">해당 연도 보도자료가 없습니다.</p>
	{/if}
</section>
