<script lang="ts">
	import type { Bill, MemberFeedItem, NewsItem, SpeechBoardItem, SpeechSegment } from '$lib/types';
	import { formatDate } from '$lib/utils/date';
	import OpenNewWindow from '~icons/iconoir/open-new-window';

	let {
		feed,
		segments,
		speechBoard,
		bills,
		news
	}: {
		feed: MemberFeedItem[];
		segments: SpeechSegment[];
		speechBoard: SpeechBoardItem[];
		bills: Bill[];
		news: NewsItem[];
	} = $props();

	const freeSpeech = $derived(speechBoard.filter((s) => s.speechKind === 'free_speech'));
	const municipalQna = $derived(speechBoard.filter((s) => s.speechKind === 'municipal_qna'));
	const writtenQna = $derived(speechBoard.filter((s) => s.speechKind === 'written_qna'));

	type TabId = 'all' | 'speech' | 'free' | 'municipal' | 'written' | 'bill' | 'news';
	const allTabs: { id: TabId; label: string; items: MemberFeedItem[] }[] = $derived([
		{ id: 'all', label: '전체', items: feed },
		{ id: 'speech', label: '발언', items: segments },
		{ id: 'free', label: '5분자유발언', items: freeSpeech },
		{ id: 'municipal', label: '시정질문', items: municipalQna },
		{ id: 'written', label: '서면질문', items: writtenQna },
		{ id: 'bill', label: '의안', items: bills },
		{ id: 'news', label: '보도자료', items: news }
	]);
	// 전체는 항상, 나머지는 항목이 있을 때만 노출.
	const tabs = $derived(allTabs.filter((t) => t.id === 'all' || t.items.length > 0));

	let active = $state<TabId>('all');
	const current = $derived(tabs.find((t) => t.id === active) ?? tabs[0]);
</script>

{#snippet segmentCard(s: SpeechSegment)}
	<article class="rounded-lg border border-border bg-muted/30 p-4">
		<div class="mb-2 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted-foreground">
			<span class="rounded border bg-background px-1.5 py-0.5 font-medium text-foreground">
				{s.meetingType}
			</span>
			{#if s.sessionNo}<span class="tabular-nums">제{s.sessionNo}회 {s.roundNo}차</span>{/if}
			<time class="tabular-nums">{formatDate(s.meetingDate)}</time>
			{#if s.speakerRole}<span>· {s.speakerRole}</span>{/if}
		</div>
		{#if s.agendaItem}
			<p class="mb-1 text-xs font-medium text-muted-foreground">🗂 {s.agendaItem}</p>
		{/if}
		<p class="text-sm leading-relaxed whitespace-pre-line">{s.text}</p>
	</article>
{/snippet}

{#snippet linkRow(title: string, href: string | null, meta: string, badge?: string)}
	<article class="flex flex-col gap-1 border-b border-border/70 py-3 last:border-0">
		<div class="flex items-center gap-2">
			{#if badge}
				<span
					class="rounded border border-border px-1.5 py-0.5 text-[0.65rem] font-semibold text-muted-foreground"
				>
					{badge}
				</span>
			{/if}
			{#if meta}<span class="text-xs text-muted-foreground tabular-nums">{meta}</span>{/if}
		</div>
		{#if href}
			<a
				{href}
				target="_blank"
				rel="noopener noreferrer"
				class="group inline-flex items-start gap-1 text-sm leading-snug font-medium hover:underline"
			>
				<span>{title}</span>
				<OpenNewWindow
					class="mt-0.5 size-3 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100"
				/>
				<span class="sr-only">(새 창)</span>
			</a>
		{:else}
			<p class="text-sm leading-snug font-medium">{title}</p>
		{/if}
	</article>
{/snippet}

{#snippet feedItem(item: MemberFeedItem)}
	{#if item.kind === 'speech'}
		{@render segmentCard(item)}
	{:else if item.kind === 'speech-board'}
		{@render linkRow(
			item.title ?? '(제목 없음)',
			item.sourceUrl,
			[item.committee, item.sessionRound, formatDate(item.date)].filter(Boolean).join(' · '),
			item.speechKindLabel
		)}
	{:else if item.kind === 'bill'}
		{@render linkRow(
			item.title,
			item.sourceUrl,
			[item.billNo ? `의안 ${item.billNo}호` : null, item.result, formatDate(item.proposedDate)]
				.filter(Boolean)
				.join(' · '),
			`의안 · ${item.statusLabel}`
		)}
	{:else if item.kind === 'news'}
		{@render linkRow(item.title, item.sourceUrl, formatDate(item.publishedDate), '보도자료')}
	{/if}
{/snippet}

<section aria-label="의정활동">
	<!-- 탭 -->
	<div role="tablist" class="flex flex-wrap gap-1 border-b pb-2">
		{#each tabs as tab (tab.id)}
			<button
				type="button"
				role="tab"
				aria-selected={active === tab.id}
				onclick={() => (active = tab.id)}
				class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none {active ===
				tab.id
					? 'bg-foreground text-background'
					: 'text-muted-foreground hover:bg-muted'}"
			>
				{tab.label}
				<span class="tabular-nums opacity-70">{tab.items.length}</span>
			</button>
		{/each}
	</div>

	<!-- 콘텐츠 -->
	<div class="mt-4">
		{#if current && current.items.length}
			<div class="flex flex-col gap-3">
				{#each current.items as item (item.id)}
					{@render feedItem(item)}
				{/each}
			</div>
		{:else}
			<p class="py-10 text-center text-sm text-muted-foreground">해당 항목이 아직 없습니다.</p>
		{/if}
	</div>
</section>
