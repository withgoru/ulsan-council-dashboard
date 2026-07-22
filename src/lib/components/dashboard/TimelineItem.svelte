<script lang="ts">
	import type { NewsItem } from '$lib/types';
	import { formatDate } from '$lib/utils/date';
	import OpenNewWindow from '~icons/iconoir/open-new-window';

	let { item }: { item: NewsItem } = $props();
</script>

<article class="relative flex flex-col gap-1 pb-4 pl-4">
	<!-- 타임라인 점/선 -->
	<span class="absolute top-1.5 left-0 h-full w-px bg-border" aria-hidden="true"></span>
	<span
		class="absolute top-1 left-[-3px] size-2 rounded-full border-2 border-background bg-foreground/60"
		aria-hidden="true"
	></span>

	<time class="text-xs text-muted-foreground tabular-nums">{formatDate(item.publishedDate)}</time>
	{#if item.sourceUrl}
		<a
			href={item.sourceUrl}
			target="_blank"
			rel="noopener noreferrer"
			class="group inline-flex items-start gap-1 text-sm leading-snug hover:underline"
		>
			<span>{item.title}</span>
			<OpenNewWindow
				class="mt-0.5 size-3 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100"
			/>
			<span class="sr-only">(새 창)</span>
		</a>
	{:else}
		<p class="text-sm leading-snug">{item.title}</p>
	{/if}
	{#if item.author}
		<span class="text-xs text-muted-foreground">{item.author}</span>
	{/if}
</article>
