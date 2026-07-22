<script lang="ts">
	import MemberHeader from '$lib/components/member/MemberHeader.svelte';
	import MemberActivityTabs from '$lib/components/member/MemberActivityTabs.svelte';
	import SeoHead from '$lib/components/common/SeoHead.svelte';
	import NavArrowLeft from '~icons/iconoir/nav-arrow-left';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const m = $derived(data.member);
	const seoDescription = $derived(
		[m.name, `${m.partyName}`, m.district, '제9대 울산광역시의회 의원의 발언·의정활동']
			.filter(Boolean)
			.join(' · ')
	);
</script>

<SeoHead
	title={data.member.name}
	description={seoDescription}
	path="/members/{data.member.slug}"
	type="profile"
/>

<main id="main-content" tabindex="-1" class="mx-auto max-w-3xl px-4 py-6">
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
