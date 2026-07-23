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
		<div class="border-t border-border/60 pt-1.5">
			<div class="flex items-center justify-between text-[0.7rem] text-muted-foreground">
				<span>본회의 출석</span>
				<span class="tabular-nums">
					{attendance.attended}/{attendance.total} ({pct.toFixed(0)}%)
				</span>
			</div>
			<div
				class="mt-1 h-1.5 overflow-hidden rounded-full bg-muted"
				role="meter"
				aria-valuenow={Math.round(pct)}
				aria-valuemin={0}
				aria-valuemax={100}
				aria-label="{member.name} 본회의 출석률 {Math.round(pct)}퍼센트"
			>
				<div
					class="h-full rounded-full"
					style="width: {pct}%; background-color: var(--party-{member.partyId})"
				></div>
			</div>
		</div>
	{/if}
</a>
