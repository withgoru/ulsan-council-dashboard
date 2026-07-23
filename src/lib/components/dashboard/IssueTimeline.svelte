<script lang="ts">
	import { MEDIA_TYPE_LABEL, type MediaItem, type ResolvedIssue } from '$lib/types';
	import { formatDate } from '$lib/utils/date';
	import OpenNewWindow from '~icons/iconoir/open-new-window';
	import NavArrowRight from '~icons/iconoir/nav-arrow-right';
	import Journal from '~icons/iconoir/journal';

	// 이슈(태그)별로 미디어를 묶어 보여준다. compact(대시보드)면 이슈당 itemLimit 개만.
	let {
		issues,
		itemLimit = 0,
		moreHref,
		heading = '의회 이슈',
		showDescription = false
	}: {
		issues: ResolvedIssue[];
		itemLimit?: number;
		moreHref?: string;
		heading?: string;
		showDescription?: boolean;
	} = $props();

	const shown = (items: MediaItem[]) => (itemLimit > 0 ? items.slice(0, itemLimit) : items);
</script>

{#snippet mediaRow(item: MediaItem)}
	<a
		href={item.url}
		target="_blank"
		rel="noopener noreferrer"
		class="group flex flex-col gap-0.5 border-b border-border/60 py-1.5 last:border-0"
	>
		<div class="flex items-center gap-1.5 text-[0.7rem] text-muted-foreground">
			<span class="rounded border border-border px-1 py-px text-[0.6rem] font-medium">
				{MEDIA_TYPE_LABEL[item.type]}
			</span>
			{#if item.publishedAt}<time class="tabular-nums">{formatDate(item.publishedAt)}</time>{/if}
			{#if item.source}<span class="truncate">· {item.source}</span>{/if}
		</div>
		<span class="inline-flex items-start gap-1 text-sm leading-snug group-hover:underline">
			<span>{item.title}</span>
			<OpenNewWindow
				class="mt-0.5 size-3 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100"
			/>
		</span>
		{#if item.note}<span class="text-xs text-muted-foreground">{item.note}</span>{/if}
	</a>
{/snippet}

<section aria-labelledby="issue-heading" class="flex min-h-0 flex-1 flex-col">
	<h2 id="issue-heading" class="mb-2 shrink-0 text-sm font-semibold tracking-tight">{heading}</h2>

	{#if issues.length}
		<div class="flex flex-col gap-4">
			{#each issues as issue (issue.id)}
				<div>
					<div class="flex items-baseline gap-1.5">
						<h3 class="text-sm font-semibold">{issue.title}</h3>
						<span class="text-[0.7rem] text-muted-foreground tabular-nums"
							>{issue.items.length}</span
						>
						{#if issue.status === 'ended'}
							<span class="rounded border border-border px-1 text-[0.6rem] text-muted-foreground">
								종료
							</span>
						{/if}
					</div>
					{#if showDescription && issue.description}
						<p class="mt-0.5 mb-1 text-xs text-muted-foreground">{issue.description}</p>
					{/if}
					<div>
						{#each shown(issue.items) as item (item.url)}
							{@render mediaRow(item)}
						{/each}
					</div>
					{#if itemLimit > 0 && issue.items.length > itemLimit}
						<span class="text-[0.7rem] text-muted-foreground">
							외 {issue.items.length - itemLimit}건
						</span>
					{/if}
				</div>
			{/each}
		</div>
		{#if moreHref}
			<a
				href={moreHref}
				class="mt-3 inline-flex items-center gap-0.5 self-start text-xs font-medium text-muted-foreground hover:text-foreground hover:underline"
			>
				전체 보기 <NavArrowRight class="size-3.5" />
			</a>
		{/if}
	{:else}
		<div
			class="flex flex-1 flex-col items-center justify-center gap-2 rounded-lg border border-dashed p-6 text-center text-muted-foreground"
		>
			<Journal class="size-8 opacity-60" />
			<p class="text-sm font-medium">진행 중인 이슈</p>
			<p class="text-xs leading-relaxed">등록된 이슈가 없습니다.</p>
		</div>
	{/if}
</section>
