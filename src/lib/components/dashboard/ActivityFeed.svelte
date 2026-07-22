<script lang="ts">
	import type { Activity, Bill } from '$lib/types';
	import ActivityFeedItem from './ActivityFeedItem.svelte';

	let { items }: { items: (Activity | Bill)[] } = $props();
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
	{:else}
		<p class="py-8 text-center text-sm text-muted-foreground">아직 등록된 활동이 없습니다.</p>
	{/if}
</section>
