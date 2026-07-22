<script lang="ts">
	import type { Activity, Bill } from '$lib/types';
	import ActivityFeedItem from './ActivityFeedItem.svelte';

	let { items }: { items: (Activity | Bill)[] } = $props();
</script>

<section aria-labelledby="activity-heading" class="flex min-h-0 flex-1 flex-col">
	<h2 id="activity-heading" class="mb-2 shrink-0 text-sm font-semibold tracking-tight">
		본회의·위원회 활동 / 의안
	</h2>
	{#if items.length}
		<ul class="min-h-0 flex-1 lg:overflow-y-auto lg:pr-1">
			{#each items as item (item.id)}
				<li><ActivityFeedItem {item} /></li>
			{/each}
		</ul>
	{:else}
		<p class="py-8 text-center text-sm text-muted-foreground">아직 등록된 활동이 없습니다.</p>
	{/if}
</section>
