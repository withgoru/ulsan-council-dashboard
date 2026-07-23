<script lang="ts">
	import PartyBadge from '$lib/components/common/PartyBadge.svelte';
	import type { Member } from '$lib/types';

	// attendance: 본회의 출석(있으면 카드 하단에 프로그레스 바로 표시).
	let {
		member,
		attendance
	}: {
		member: Member;
		attendance?: { attended: number; total: number; rate: number } | null;
	} = $props();

	const primaryCommittee = $derived(member.committees[0]);
	const pct = $derived(attendance ? Math.max(0, Math.min(100, attendance.rate)) : 0);
</script>

<!-- 카드 전체가 실제 <a>. 하단에 본회의 출석률 바(정당색 채움). -->
<a
	href="/members/{member.slug}"
	class="flex flex-col gap-2 rounded-lg border border-border bg-card p-2.5 transition-colors hover:bg-accent focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
>
	<div class="flex items-center gap-3">
		<img
			src={member.photoUrl}
			alt=""
			loading="lazy"
			width="44"
			height="50"
			class="h-12.5 w-11 shrink-0 rounded bg-muted object-cover"
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
	</div>

	{#if attendance}
		<!-- 공간 절약: 출석 횟수·출석율 텍스트는 감추고 마우스 오버(title) 시 노출. -->
		<div
			class="mt-0.5 h-1.5 overflow-hidden rounded-full bg-muted"
			role="meter"
			aria-valuenow={Math.round(pct)}
			aria-valuemin={0}
			aria-valuemax={100}
			aria-label="{member.name} 본회의 출석 {attendance.attended}/{attendance.total} ({Math.round(
				pct
			)}%)"
			title="본회의 출석 {attendance.attended}/{attendance.total} ({pct.toFixed(0)}%)"
		>
			<div
				class="h-full rounded-full"
				style="width: {pct}%; background-color: var(--party-{member.partyId})"
			></div>
		</div>
	{/if}
</a>
