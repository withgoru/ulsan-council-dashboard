<script lang="ts">
	import type { Activity, Bill } from '$lib/types';
	import ActivityFeedItem from './ActivityFeedItem.svelte';
	import NavArrowRight from '~icons/iconoir/nav-arrow-right';

	let { items, moreHref }: { items: (Activity | Bill)[]; moreHref?: string } = $props();
</script>

<section aria-labelledby="activity-heading" class="flex flex-col">
	<h2 id="activity-heading" class="mb-2 text-sm font-semibold tracking-tight">
		본회의·위원회 활동 / 의안
	</h2>
	{#if items.length}
		<ul>
			{#each items as item (item.id)}
				<li><ActivityFeedItem {item} /></li>
			{/each}
		</ul>
		{#if moreHref}
			<a
				href={moreHref}
				class="mt-3 inline-flex items-center gap-0.5 self-start text-xs font-medium text-muted-foreground hover:text-foreground hover:underline"
			>
				전체 보기 <NavArrowRight class="size-3.5" />
			</a>
		{/if}
	{:else}
		<p class="py-8 text-center text-sm text-muted-foreground">아직 등록된 활동이 없습니다.</p>
	{/if}
</section>
