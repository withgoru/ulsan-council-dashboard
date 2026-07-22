<script lang="ts">
	import type { PartyId } from '$lib/config/parties';

	let {
		name,
		partyId,
		attended,
		total,
		rate
	}: { name: string; partyId: PartyId; attended: number; total: number; rate: number } = $props();

	const pct = $derived(Math.max(0, Math.min(100, rate)));
</script>

<div class="flex items-center gap-2 py-1.5">
	<span
		class="size-2 shrink-0 rounded-full"
		style="background-color: var(--party-{partyId})"
		aria-hidden="true"
	></span>
	<span class="w-14 shrink-0 truncate text-xs font-medium">{name}</span>
	<!-- 그레이스케일 막대(차트 라이브러리 없이). 점 색으로만 정당 구분. -->
	<div
		class="relative h-2 flex-1 overflow-hidden rounded-full bg-muted"
		role="meter"
		aria-valuenow={Math.round(pct)}
		aria-valuemin={0}
		aria-valuemax={100}
		aria-label="{name} 본회의 출석률 {Math.round(pct)}퍼센트"
	>
		<div class="h-full rounded-full bg-foreground/70" style="width: {pct}%"></div>
	</div>
	<span class="w-20 shrink-0 text-right text-[0.7rem] text-muted-foreground tabular-nums">
		{attended}/{total} ({pct.toFixed(0)}%)
	</span>
</div>
