<script lang="ts">
	import PartyBadge from '$lib/components/common/PartyBadge.svelte';
	import type { Member } from '$lib/types';

	type Bar = { attended: number; total: number; rate: number } | null;

	// plenary=본회의, committee=상임위(소속 위원회 합산). 각각 프로그레스 바로 표시.
	let { member, plenary, committee }: { member: Member; plenary?: Bar; committee?: Bar } = $props();

	const clamp = (r: number) => Math.max(0, Math.min(100, r));
</script>

{#snippet bar(label: string, data: Bar)}
	{#if data}
		<div
			class="flex items-center gap-1.5"
			title="{label} 출석 {data.attended}/{data.total} ({clamp(data.rate).toFixed(0)}%)"
		>
			<span class="w-7 shrink-0 text-[0.6rem] text-muted-foreground">{label}</span>
			<div
				class="h-1.5 flex-1 overflow-hidden rounded-full bg-muted"
				role="meter"
				aria-valuenow={Math.round(clamp(data.rate))}
				aria-valuemin={0}
				aria-valuemax={100}
				aria-label="{member.name} {label} 출석 {data.attended}/{data.total} ({Math.round(
					clamp(data.rate)
				)}%)"
			>
				<div
					class="h-full rounded-full"
					style="width: {clamp(data.rate)}%; background-color: var(--party-{member.partyId})"
				></div>
			</div>
		</div>
	{/if}
{/snippet}

<!-- 카드 전체가 실제 <a>. 하단에 본회의/상임위 출석률 바(정당색, 수치는 hover). -->
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
			{#if member.committees.length}
				<span class="truncate text-[0.7rem] text-muted-foreground">
					{member.committees[0].name}
					{member.committees[0].role}
				</span>
			{/if}
		</div>
	</div>

	{#if plenary || committee}
		<div class="flex flex-col gap-1">
			{@render bar('본회의', plenary ?? null)}
			{@render bar('상임위', committee ?? null)}
		</div>
	{/if}
</a>
