<script lang="ts">
	import IssueTimeline from '$lib/components/dashboard/IssueTimeline.svelte';
	import SeoHead from '$lib/components/common/SeoHead.svelte';
	import NavArrowLeft from '~icons/iconoir/nav-arrow-left';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
</script>

<SeoHead title="의회 이슈" path="/issues" />

<main id="main-content" tabindex="-1" class="mx-auto max-w-3xl px-4 py-6">
	<a
		href="/"
		class="mb-4 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
	>
		<NavArrowLeft class="size-4" /> 대시보드로
	</a>

	<h1 class="mb-1 text-xl font-bold tracking-tight sm:text-2xl">의회 이슈</h1>
	<p class="mb-5 text-sm text-muted-foreground">
		이슈별로 관련 기사·영상 등 외부 미디어를 모아 보여줍니다.
	</p>

	{#if data.active.length}
		<IssueTimeline issues={data.active} heading="진행 중" showDescription />
	{:else}
		<p class="py-10 text-center text-sm text-muted-foreground">진행 중인 이슈가 없습니다.</p>
	{/if}

	{#if data.ended.length}
		<div class="mt-8 border-t pt-6">
			<IssueTimeline issues={data.ended} heading="지난 이슈" showDescription />
		</div>
	{/if}
</main>
