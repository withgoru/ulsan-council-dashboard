<script lang="ts">
	import type { AttendanceRecord, Member } from '$lib/types';
	import type { PartyId } from '$lib/config/parties';
	import AttendanceRow from './AttendanceRow.svelte';

	let { attendance, members }: { attendance: AttendanceRecord[]; members: Member[] } = $props();

	// memCode → 정당/이름 매핑(출석 레코드에는 정당이 없으므로 의원 명단에서 보강).
	const byCode = $derived(new Map(members.map((m) => [m.memCode, m])));

	type SortMode = 'default' | 'desc' | 'asc';
	const sortOptions: { id: SortMode; label: string }[] = [
		{ id: 'default', label: '번호순' },
		{ id: 'desc', label: '높은순' },
		{ id: 'asc', label: '낮은순' }
	];
	let sort = $state<SortMode>('default');

	const rows = $derived.by(() => {
		const mapped = attendance.map((a, i) => {
			const m = a.memCode ? byCode.get(a.memCode) : undefined;
			return {
				key: a.memCode ?? a.memberName,
				order: i, // 원본 순서(번호순)
				name: m?.name ?? a.memberName,
				partyId: (m?.partyId ?? 'etc') as PartyId,
				attended: a.attended,
				total: a.total,
				rate: a.rate
			};
		});
		if (sort === 'desc') mapped.sort((a, b) => b.rate - a.rate || a.order - b.order);
		else if (sort === 'asc') mapped.sort((a, b) => a.rate - b.rate || a.order - b.order);
		return mapped;
	});

	const label = $derived(attendance[0]?.half ?? '');
</script>

<section aria-labelledby="attendance-heading" class="flex flex-col">
	<div class="mb-2 flex flex-wrap items-baseline justify-between gap-2">
		<h2 id="attendance-heading" class="text-sm font-semibold tracking-tight">
			본회의 출석률
			{#if label}<span class="ml-1 text-xs font-normal text-muted-foreground">{label}</span>{/if}
		</h2>
		{#if rows.length}
			<div role="group" aria-label="출석률 정렬" class="flex gap-0.5">
				{#each sortOptions as opt (opt.id)}
					<button
						type="button"
						aria-pressed={sort === opt.id}
						onclick={() => (sort = opt.id)}
						class="rounded px-1.5 py-0.5 text-[0.7rem] font-medium transition-colors focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none {sort ===
						opt.id
							? 'bg-foreground text-background'
							: 'text-muted-foreground hover:bg-muted'}"
					>
						{opt.label}
					</button>
				{/each}
			</div>
		{/if}
	</div>
	{#if rows.length}
		<div>
			{#each rows as row (row.key)}
				<AttendanceRow
					name={row.name}
					partyId={row.partyId}
					attended={row.attended}
					total={row.total}
					rate={row.rate}
				/>
			{/each}
		</div>
	{:else}
		<p class="py-8 text-center text-sm text-muted-foreground">아직 출석 데이터가 없습니다.</p>
	{/if}
</section>
