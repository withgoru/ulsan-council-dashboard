<script lang="ts">
	import PartyBadge from '$lib/components/common/PartyBadge.svelte';
	import type { Member } from '$lib/types';

	let { member }: { member: Member } = $props();

	// 대표 위원회(첫 항목)만 카드에 노출. 전체는 상세 페이지(이슈 #10)에서.
	const primaryCommittee = $derived(member.committees[0]);
</script>

<!-- 카드 전체가 실제 <a>(div+onclick 금지, 접근성). 상세 라우트는 이슈 #10. -->
<a
	href="/members/{member.slug}"
	class="flex items-center gap-3 rounded-lg border border-border bg-card p-2.5 transition-colors hover:bg-accent focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
>
	<img
		src={member.photoUrl}
		alt=""
		loading="lazy"
		width="44"
		height="50"
		class="h-[50px] w-[44px] shrink-0 rounded bg-muted object-cover"
	/>
	<div class="flex min-w-0 flex-col gap-1">
		<div class="flex items-center gap-1.5">
			<span class="text-sm font-semibold">{member.name}</span>
			<PartyBadge partyId={member.partyId} partyName={member.partyName} size="xs" />
		</div>
		{#if member.district}
			<span class="truncate text-xs text-muted-foreground">{member.district}</span>
		{/if}
		{#if primaryCommittee}
			<span class="truncate text-[0.7rem] text-muted-foreground">
				{primaryCommittee.name}
				{primaryCommittee.role}
			</span>
		{/if}
	</div>
</a>
