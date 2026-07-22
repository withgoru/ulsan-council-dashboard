<script lang="ts">
	import type { AttendanceRecord, Member } from '$lib/types';
	import type { PartyId } from '$lib/config/parties';
	import AttendanceRow from './AttendanceRow.svelte';

	let { attendance, members }: { attendance: AttendanceRecord[]; members: Member[] } = $props();

	// memCode → 정당/이름 매핑(출석 레코드에는 정당이 없으므로 의원 명단에서 보강).
	const byCode = $derived(new Map(members.map((m) => [m.memCode, m])));

	const rows = $derived(
		attendance.map((a) => {
			const m = a.memCode ? byCode.get(a.memCode) : undefined;
			return {
				key: a.memCode ?? a.memberName,
				name: m?.name ?? a.memberName,
				partyId: (m?.partyId ?? 'etc') as PartyId,
				attended: a.attended,
				total: a.total,
				rate: a.rate
			};
		})
	);

	const label = $derived(attendance[0]?.half ?? '');
</script>

<section aria-labelledby="attendance-heading" class="flex flex-col">
	<div class="mb-2 flex items-baseline justify-between">
		<h2 id="attendance-heading" class="text-sm font-semibold tracking-tight">본회의 출석률</h2>
		{#if label}<span class="text-xs text-muted-foreground">{label}</span>{/if}
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
