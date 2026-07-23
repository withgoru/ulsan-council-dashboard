<script lang="ts">
	import type { AttendanceRecord, Member } from '$lib/types';
	import MemberCard from './MemberCard.svelte';

	// 의원 명단 + 출석률(본회의/상임위) 통합. 각 카드 하단에 두 개의 프로그레스 바.
	let { members, attendance }: { members: Member[]; attendance: AttendanceRecord[] } = $props();

	type Bar = { attended: number; total: number; rate: number } | null;

	// memCode → { 본회의, 상임위(소속 위원회 합산) }.
	const byMember = $derived.by(() => {
		const map = new Map<string, { plenary: Bar; committee: Bar }>();
		for (const m of members) map.set(m.memCode, { plenary: null, committee: null });
		const comm = new Map<string, { attended: number; total: number }>();
		for (const a of attendance) {
			if (!a.memCode) continue;
			const e = map.get(a.memCode);
			if (!e) continue;
			if (a.meetingType === '본회의') {
				e.plenary = { attended: a.attended, total: a.total, rate: a.rate };
			} else {
				const c = comm.get(a.memCode) ?? { attended: 0, total: 0 };
				c.attended += a.attended;
				c.total += a.total;
				comm.set(a.memCode, c);
			}
		}
		for (const [code, c] of comm) {
			const e = map.get(code);
			if (e && c.total > 0) {
				e.committee = { attended: c.attended, total: c.total, rate: (c.attended / c.total) * 100 };
			}
		}
		return map;
	});

	type SortMode = 'default' | 'desc' | 'asc';
	const sortOptions: { id: SortMode; label: string }[] = [
		{ id: 'default', label: '번호순' },
		{ id: 'desc', label: '출석 높은순' },
		{ id: 'asc', label: '출석 낮은순' }
	];
	let sort = $state<SortMode>('default');

	const rows = $derived.by(() => {
		const list = members.map((m, i) => ({ member: m, order: i, att: byMember.get(m.memCode)! }));
		// 정렬 기준은 본회의 출석률.
		if (sort === 'desc')
			list.sort(
				(a, b) => (b.att.plenary?.rate ?? -1) - (a.att.plenary?.rate ?? -1) || a.order - b.order
			);
		else if (sort === 'asc')
			list.sort(
				(a, b) => (a.att.plenary?.rate ?? 999) - (b.att.plenary?.rate ?? 999) || a.order - b.order
			);
		return list;
	});
</script>

<section aria-labelledby="roster-heading" class="flex flex-col">
	<div class="mb-2 flex flex-wrap items-center justify-between gap-2">
		<h2 id="roster-heading" class="text-sm font-semibold tracking-tight">
			의원 명단 <span class="text-xs font-normal text-muted-foreground">{members.length}명</span>
		</h2>
		<div role="group" aria-label="정렬" class="flex gap-0.5">
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
	</div>
	<ul class="grid grid-cols-1 gap-2 sm:grid-cols-2">
		{#each rows as row (row.member.memCode)}
			<li>
				<MemberCard member={row.member} plenary={row.att.plenary} committee={row.att.committee} />
			</li>
		{/each}
	</ul>
</section>
