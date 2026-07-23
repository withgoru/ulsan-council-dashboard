<script lang="ts">
	import SeoHead from '$lib/components/common/SeoHead.svelte';
	import { formatDate } from '$lib/utils/date';
	import NavArrowLeft from '~icons/iconoir/nav-arrow-left';
	import OpenNewWindow from '~icons/iconoir/open-new-window';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
</script>

<SeoHead title="언론이 본 의회" path="/media" />

<main id="main-content" tabindex="-1" class="mx-auto max-w-3xl px-4 py-6">
	<a
		href="/"
		class="mb-4 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
	>
		<NavArrowLeft class="size-4" /> 대시보드로
	</a>

	<h1 class="mb-4 text-xl font-bold tracking-tight sm:text-2xl">언론이 본 의회</h1>

	{#if data.articles.length}
		<p class="mb-2 text-sm text-muted-foreground">총 {data.articles.length}건</p>
		<div>
			{#each data.articles as a (a.url)}
				<article class="flex flex-col gap-1 border-b border-border/70 py-3 last:border-0">
					<div class="flex items-center gap-2 text-xs text-muted-foreground">
						{#if a.publishedAt}<time class="tabular-nums">{formatDate(a.publishedAt)}</time>{/if}
						{#if a.press}<span>· {a.press}</span>{/if}
					</div>
					<a
						href={a.url}
						target="_blank"
						rel="noopener noreferrer"
						class="group inline-flex items-start gap-1 text-sm leading-snug font-medium hover:underline"
					>
						<span>{a.title}</span>
						<OpenNewWindow
							class="mt-0.5 size-3 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100"
						/>
						<span class="sr-only">(새 창)</span>
					</a>
					{#if a.note}<p class="text-xs text-muted-foreground">{a.note}</p>{/if}
				</article>
			{/each}
		</div>
	{:else}
		<p class="py-16 text-center text-sm text-muted-foreground">
			아직 큐레이션된 언론 보도가 없습니다.
		</p>
	{/if}
</main>
