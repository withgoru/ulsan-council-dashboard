<script lang="ts">
	import type { NewsItem } from '$lib/types';
	import TimelineItem from './TimelineItem.svelte';

	let { items, title = '보도자료 타임라인' }: { items: NewsItem[]; title?: string } = $props();
</script>

<section aria-label={title} class="flex flex-col">
	<h2 class="mb-2 text-sm font-semibold tracking-tight">{title}</h2>
	{#if items.length}
		<div>
			{#each items as item (item.id)}
				<TimelineItem {item} />
			{/each}
		</div>
	{:else}
		<p class="py-8 text-center text-sm text-muted-foreground">아직 보도자료가 없습니다.</p>
	{/if}
</section>
