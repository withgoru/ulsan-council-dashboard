<script lang="ts">
	import type { Activity, Bill } from '$lib/types';
	import { formatDate } from '$lib/utils/date';
	import OpenNewWindow from '~icons/iconoir/open-new-window';

	let { item }: { item: Activity | Bill } = $props();

	// 종류별 배지 텍스트(활동: 본회의/위원회, 의안: 접수/처리/계류).
	const badge = $derived(item.kind === 'activity' ? item.type : item.statusLabel);
	const meta = $derived(
		item.kind === 'activity'
			? [item.committeeName, item.sessionRound].filter(Boolean).join(' · ')
			: [item.billNo ? `의안 ${item.billNo}호` : null, item.result].filter(Boolean).join(' · ')
	);
	const date = $derived(item.kind === 'activity' ? item.date : item.proposedDate);
</script>

<article class="flex flex-col gap-1.5 border-b border-border/70 py-3 last:border-0">
	<div class="flex items-center gap-2">
		<span
			class="rounded border px-1.5 py-0.5 text-[0.65rem] font-semibold {item.kind === 'bill'
				? 'border-foreground/20 text-foreground/70'
				: 'border-border text-muted-foreground'}"
		>
			{item.kind === 'activity' ? '활동' : '의안'} · {badge}
		</span>
		<time class="text-xs text-muted-foreground tabular-nums">{formatDate(date)}</time>
	</div>

	{#if item.sourceUrl}
		<a
			href={item.sourceUrl}
			target="_blank"
			rel="noopener noreferrer"
			class="group inline-flex items-start gap-1 text-sm leading-snug font-medium hover:underline"
		>
			<span>{item.title}</span>
			<OpenNewWindow
				class="mt-0.5 size-3 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100"
			/>
			<span class="sr-only">(새 창)</span>
		</a>
	{:else}
		<p class="text-sm leading-snug font-medium">{item.title}</p>
	{/if}

	{#if meta}
		<p class="text-xs text-muted-foreground">{meta}</p>
	{/if}
</article>
