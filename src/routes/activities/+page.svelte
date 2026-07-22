<script lang="ts">
	import ActivityFeedItem from '$lib/components/dashboard/ActivityFeedItem.svelte';
	import SeoHead from '$lib/components/common/SeoHead.svelte';
	import YearSelect from '$lib/components/common/YearSelect.svelte';
	import { feedItemYear } from '$lib/utils/year';
	import { page } from '$app/state';
	import { browser } from '$app/environment';
	import NavArrowLeft from '~icons/iconoir/nav-arrow-left';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const year = $derived(
		browser ? Number(page.url.searchParams.get('year')) || data.years[0] : data.years[0]
	);
	const items = $derived(data.feed.filter((it) => feedItemYear(it) === year));
</script>

<SeoHead title="본회의·위원회 활동 / 의안" path="/activities" />

<main id="main-content" tabindex="-1" class="mx-auto max-w-3xl px-4 py-6">
	<a
		href="/"
		class="mb-4 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
	>
		<NavArrowLeft class="size-4" /> 대시보드로
	</a>

	<div class="mb-4 flex items-end justify-between gap-3">
		<h1 class="text-xl font-bold tracking-tight sm:text-2xl">본회의·위원회 활동 / 의안</h1>
		<YearSelect years={data.years} />
	</div>

	{#if items.length}
		<p class="mb-2 text-sm text-muted-foreground">{year}년 · 총 {items.length}건</p>
		<ul>
			{#each items as item (item.id)}
				<li><ActivityFeedItem {item} /></li>
			{/each}
		</ul>
	{:else}
		<p class="py-16 text-center text-sm text-muted-foreground">{year}년 활동 기록이 없습니다.</p>
	{/if}
</main>
