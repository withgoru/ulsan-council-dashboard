<script lang="ts">
	import { PARTIES, type PartyId } from '$lib/config/parties';

	// 정당 배지: 색상뿐 아니라 항상 정당명 텍스트를 함께 표시(WCAG 1.4.1).
	// 색상은 좌측 점으로만 쓰고 텍스트/배경은 그레이스케일 유지(색약 대응).
	let {
		partyId,
		partyName,
		size = 'sm'
	}: { partyId: PartyId; partyName?: string; size?: 'sm' | 'xs' } = $props();

	const label = $derived(partyName ?? PARTIES[partyId].name);
</script>

<span
	class="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted/50 font-medium text-muted-foreground {size ===
	'xs'
		? 'px-1.5 py-0.5 text-[0.65rem]'
		: 'px-2 py-0.5 text-xs'}"
>
	<span
		class="size-2 shrink-0 rounded-full"
		style="background-color: var(--party-{partyId})"
		aria-hidden="true"
	></span>
	{label}
</span>
