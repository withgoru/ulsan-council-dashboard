<script lang="ts">
	import type { AttendanceRecord, Member } from '$lib/types';
	import MemberCard from './MemberCard.svelte';

	// 의원 명단 + 본회의 출석률 통합. 각 카드 하단에 출석 프로그레스 바.
	let { members, attendance }: { members: Member[]; attendance: AttendanceRecord[] } = $props();

	// memCode → 본회의 출석 레코드.
	const byCode = $derived(
		new Map(attendance.filter((a) => a.memCode).map((a) => [a.memCode as string, a]))
	);

	type SortMode = 'default' | 'desc' | 'asc';
	const sortOptions: { id: SortMode; label: string }[] = [
		{ id: 'default', label: '번호순' },
		{ id: 'desc', label: '출석 높은순' },
		{ id: 'asc', label: '출석 낮은순' }
	];
	let sort = $state<SortMode>('default');

	const rows = $derived.by(() => {
		const list = members.map((m, i) => ({
			member: m,
			order: i,
			att: byCode.get(m.memCode) ?? null
		}));
		if (sort === 'desc')
			list.sort((a, b) => (b.att?.rate ?? -1) - (a.att?.rate ?? -1) || a.order - b.order);
		else if (sort === 'asc')
			list.sort((a, b) => (a.att?.rate ?? 999) - (b.att?.rate ?? 999) || a.order - b.order);
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
			<li><MemberCard member={row.member} attendance={row.att} /></li>
		{/each}
	</ul>
</section>
