<script lang="ts">
	import PartyBadge from '$lib/components/common/PartyBadge.svelte';
	import NavArrowLeft from '~icons/iconoir/nav-arrow-left';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	const m = $derived(data.member);
</script>

<!-- 최소 상세 페이지(스텁). 발언 원문·활동 탭 등 본 콘텐츠는 이슈 #10에서 구현. -->
<main class="mx-auto max-w-3xl px-4 py-6">
	<a
		href="/"
		class="mb-4 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
	>
		<NavArrowLeft class="size-4" /> 대시보드로
	</a>

	<div class="flex items-center gap-4">
		<img
			src={m.photoUrl}
			alt=""
			width="88"
			height="100"
			class="h-[100px] w-[88px] shrink-0 rounded bg-muted object-cover"
		/>
		<div class="flex flex-col gap-2">
			<div class="flex items-center gap-2">
				<h1 class="text-2xl font-bold tracking-tight">{m.name}</h1>
				<PartyBadge partyId={m.partyId} partyName={m.partyName} />
			</div>
			{#if m.district}<p class="text-sm text-muted-foreground">{m.district}</p>{/if}
			{#if m.committees.length}
				<p class="text-sm text-muted-foreground">
					{m.committees.map((c) => `${c.name} ${c.role}`).join(' · ')}
				</p>
			{/if}
		</div>
	</div>
</main>
