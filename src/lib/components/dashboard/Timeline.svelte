<script lang="ts">
	import type { NewsItem } from '$lib/types';
	import TimelineItem from './TimelineItem.svelte';

	let { items }: { items: NewsItem[] } = $props();
</script>

<section aria-labelledby="timeline-heading" class="flex min-h-0 flex-1 flex-col">
	<h2 id="timeline-heading" class="mb-2 shrink-0 text-sm font-semibold tracking-tight">
		보도자료 타임라인
	</h2>
	{#if items.length}
		<!-- 데스크톱에서 내부 스크롤. 스크롤 영역은 키보드 접근을 위해 region+tabindex=0(WCAG 권장). -->
		<!-- svelte-ignore a11y_no_noninteractive_tabindex -->
		<div
			class="min-h-0 flex-1 lg:overflow-y-auto lg:pr-1"
			role="region"
			aria-label="보도자료 타임라인 (최신순)"
			tabindex="0"
		>
			{#each items as item (item.id)}
				<TimelineItem {item} />
			{/each}
		</div>
	{:else}
		<p class="py-8 text-center text-sm text-muted-foreground">아직 보도자료가 없습니다.</p>
	{/if}
</section>
