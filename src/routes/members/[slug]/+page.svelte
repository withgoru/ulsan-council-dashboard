<script lang="ts">
	import MemberHeader from '$lib/components/member/MemberHeader.svelte';
	import MemberActivityTabs from '$lib/components/member/MemberActivityTabs.svelte';
	import NavArrowLeft from '~icons/iconoir/nav-arrow-left';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
</script>

<main class="mx-auto max-w-3xl px-4 py-6">
	<a
		href="/"
		class="mb-5 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
	>
		<NavArrowLeft class="size-4" /> 대시보드로
	</a>

	<MemberHeader member={data.member} attendance={data.attendance} />

	<div class="mt-8">
		<MemberActivityTabs
			feed={data.feed}
			segments={data.segments}
			speechBoard={data.speechBoard}
			bills={data.bills}
			news={data.news}
		/>
	</div>
</main>
