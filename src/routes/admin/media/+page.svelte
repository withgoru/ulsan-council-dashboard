<script lang="ts">
	import { onMount } from 'svelte';
	import { formatDate } from '$lib/utils/date';
	import { MEDIA_TYPE_LABEL, type MediaType } from '$lib/types';

	// 개발 전용 이슈 큐레이션. `npm run dev` 에서만 동작(Vite 미들웨어 /__curation/*).
	// 이슈(태그)를 만들고 미디어를 N:N 으로 태깅 → media-curation.json 저장 → 커밋·배포.
	type Item = {
		url: string;
		type: MediaType;
		title: string;
		source: string | null;
		publishedAt: string | null;
		note: string | null;
	};
	type IssueMeta = {
		id: string;
		title: string;
		description: string | null;
		status: 'active' | 'ended' | 'hidden';
		pinned: boolean;
		keywords: string[];
	};

	let pool = $state<Item[]>([]);
	let issues = $state<IssueMeta[]>([]);
	let membership = $state<Record<string, string[]>>({}); // url → issueId[]
	let loading = $state(true);
	let error = $state<string | null>(null);
	let saveMsg = $state<string | null>(null);
	let search = $state('');

	// 수동 추가 폼
	let mUrl = $state('');
	let mType = $state<MediaType>('video');
	let mTitle = $state('');
	let mSource = $state('');
	let mDate = $state('');

	const types: MediaType[] = ['article', 'video', 'release', 'sns'];

	onMount(async () => {
		try {
			const res = await fetch('/__curation/candidates');
			if (!res.ok) throw new Error(`후보 조회 실패 (${res.status}). npm run dev 확인.`);
			const data = await res.json();
			const byUrl = new Map<string, Item>();
			// 기존 큐레이션 items 우선
			for (const it of (data.curation?.items ?? []) as Item[]) byUrl.set(it.url, it);
			// DB 후보(기사) 병합
			for (const c of data.candidates ?? []) {
				if (!byUrl.has(c.url))
					byUrl.set(c.url, {
						url: c.url,
						type: 'article',
						title: c.title,
						source: c.source ?? null,
						publishedAt: c.publishedAt ?? null,
						note: null
					});
			}
			pool = [...byUrl.values()];
			issues = ((data.curation?.issues ?? []) as (IssueMeta & { itemUrls: string[] })[]).map(
				({ itemUrls, ...meta }) => {
					for (const u of itemUrls) membership[u] = [...(membership[u] ?? []), meta.id];
					return meta;
				}
			);
		} catch (e) {
			error = String(e);
		} finally {
			loading = false;
		}
	});

	const filtered = $derived(
		search.trim() ? pool.filter((p) => p.title.includes(search.trim())) : pool
	);
	const assignedCount = $derived(Object.values(membership).filter((a) => a.length).length);

	function addIssue() {
		const id = 'issue-' + crypto.randomUUID().slice(0, 8);
		issues = [
			...issues,
			{ id, title: '새 이슈', description: null, status: 'active', pinned: false, keywords: [] }
		];
	}
	function removeIssue(id: string) {
		issues = issues.filter((i) => i.id !== id);
		for (const u of Object.keys(membership))
			membership[u] = (membership[u] ?? []).filter((x) => x !== id);
	}
	function toggle(url: string, id: string) {
		const cur = membership[url] ?? [];
		membership[url] = cur.includes(id) ? cur.filter((x) => x !== id) : [...cur, id];
	}
	function suggests(issue: IssueMeta, item: Item) {
		return issue.keywords.some((k) => k && item.title.includes(k));
	}
	function addManual() {
		if (!mUrl.trim() || !mTitle.trim()) return;
		if (!pool.some((p) => p.url === mUrl.trim())) {
			pool = [
				{
					url: mUrl.trim(),
					type: mType,
					title: mTitle.trim(),
					source: mSource.trim() || null,
					publishedAt: mDate || null,
					note: null
				},
				...pool
			];
		}
		mUrl = mTitle = mSource = mDate = '';
	}

	async function save() {
		saveMsg = null;
		const items = pool.filter((p) => (membership[p.url] ?? []).length > 0);
		const out = issues.map((i, idx) => ({
			...i,
			order: idx,
			startDate: null,
			endDate: null,
			itemUrls: items.filter((p) => (membership[p.url] ?? []).includes(i.id)).map((p) => p.url)
		}));
		try {
			const res = await fetch('/__curation/save', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ items, issues: out })
			});
			if (!res.ok) throw new Error(`저장 실패 (${res.status})`);
			const r = await res.json();
			saveMsg = `저장 완료: 이슈 ${r.issues}개, 미디어 ${r.items}건. 커밋·배포하면 반영됩니다.`;
		} catch (e) {
			saveMsg = `오류: ${e}`;
		}
	}
</script>

<svelte:head><title>이슈 큐레이션 (dev)</title></svelte:head>

<main id="main-content" tabindex="-1" class="mx-auto max-w-4xl px-4 py-6">
	<div class="mb-4 flex items-center justify-between gap-3">
		<h1 class="text-xl font-bold tracking-tight">
			이슈 큐레이션 <span class="text-sm font-normal text-muted-foreground">(개발 전용)</span>
		</h1>
		<button
			type="button"
			onclick={save}
			class="rounded-md bg-foreground px-3 py-1.5 text-sm font-medium text-background"
		>
			저장
		</button>
	</div>
	{#if saveMsg}<p class="mb-3 text-sm text-muted-foreground">{saveMsg}</p>{/if}

	{#if loading}
		<p class="py-10 text-center text-sm text-muted-foreground">불러오는 중…</p>
	{:else if error}
		<p class="rounded-lg border border-destructive/40 bg-destructive/10 p-4 text-sm">{error}</p>
	{:else}
		<!-- 이슈 관리 -->
		<section class="mb-6">
			<div class="mb-2 flex items-center justify-between">
				<h2 class="text-sm font-semibold">이슈 {issues.length}개</h2>
				<button
					type="button"
					onclick={addIssue}
					class="rounded-md border border-border px-2 py-1 text-xs"
				>
					+ 새 이슈
				</button>
			</div>
			<div class="flex flex-col gap-2">
				{#each issues as issue (issue.id)}
					<div class="flex flex-wrap items-center gap-2 rounded-lg border border-border p-2">
						<input
							bind:value={issue.title}
							placeholder="이슈명"
							class="min-w-40 flex-1 rounded border border-border px-2 py-1 text-sm font-medium"
						/>
						<select
							bind:value={issue.status}
							class="rounded border border-border px-2 py-1 text-xs"
						>
							<option value="active">진행중</option>
							<option value="ended">종료</option>
							<option value="hidden">숨김</option>
						</select>
						<label class="flex items-center gap-1 text-xs text-muted-foreground">
							<input type="checkbox" bind:checked={issue.pinned} /> 고정
						</label>
						<input
							value={issue.keywords.join(', ')}
							oninput={(e) =>
								(issue.keywords = e.currentTarget.value
									.split(',')
									.map((s) => s.trim())
									.filter(Boolean))}
							placeholder="추천 키워드(쉼표)"
							class="w-48 rounded border border-border px-2 py-1 text-xs"
						/>
						<button
							type="button"
							onclick={() => removeIssue(issue.id)}
							class="text-xs text-muted-foreground hover:underline"
						>
							삭제
						</button>
					</div>
				{/each}
			</div>
		</section>

		<!-- 수동 미디어 추가 -->
		<section class="mb-6 rounded-lg border border-border p-3">
			<h2 class="mb-2 text-sm font-semibold">미디어 직접 추가 (영상·링크 등)</h2>
			<div class="flex flex-wrap items-center gap-2">
				<select bind:value={mType} class="rounded border border-border px-2 py-1 text-xs">
					{#each types as t (t)}<option value={t}>{MEDIA_TYPE_LABEL[t]}</option>{/each}
				</select>
				<input
					bind:value={mTitle}
					placeholder="제목"
					class="min-w-40 flex-1 rounded border border-border px-2 py-1 text-sm"
				/>
				<input
					bind:value={mUrl}
					placeholder="URL"
					class="min-w-40 flex-1 rounded border border-border px-2 py-1 text-sm"
				/>
				<input
					bind:value={mSource}
					placeholder="출처/채널"
					class="w-28 rounded border border-border px-2 py-1 text-xs"
				/>
				<input
					bind:value={mDate}
					type="date"
					class="rounded border border-border px-2 py-1 text-xs"
				/>
				<button
					type="button"
					onclick={addManual}
					class="rounded-md bg-muted px-2 py-1 text-xs font-medium">추가</button
				>
			</div>
		</section>

		<!-- 미디어 태깅 -->
		<section>
			<div class="mb-2 flex items-center justify-between gap-2">
				<h2 class="text-sm font-semibold">미디어 {pool.length}건 · 태깅됨 {assignedCount}건</h2>
				<input
					bind:value={search}
					placeholder="제목 검색"
					class="w-48 rounded border border-border px-2 py-1 text-xs"
				/>
			</div>
			<ul class="flex flex-col">
				{#each filtered as item (item.url)}
					<li class="flex flex-col gap-1.5 border-b border-border/70 py-2.5">
						<div class="flex items-center gap-1.5 text-[0.7rem] text-muted-foreground">
							<span class="rounded bg-muted px-1 text-[0.6rem]">{MEDIA_TYPE_LABEL[item.type]}</span>
							{#if item.publishedAt}<time>{formatDate(item.publishedAt)}</time>{/if}
							{#if item.source}<span>· {item.source}</span>{/if}
						</div>
						<a
							href={item.url}
							target="_blank"
							rel="noopener noreferrer"
							class="text-sm font-medium hover:underline"
						>
							{item.title}
						</a>
						{#if issues.length}
							<div class="flex flex-wrap gap-1">
								{#each issues as issue (issue.id)}
									{@const on = (membership[item.url] ?? []).includes(issue.id)}
									<button
										type="button"
										onclick={() => toggle(item.url, issue.id)}
										class="rounded-full border px-2 py-0.5 text-[0.7rem] transition-colors {on
											? 'border-foreground bg-foreground text-background'
											: suggests(issue, item)
												? 'border-foreground/40 text-foreground'
												: 'border-border text-muted-foreground'}"
										title={suggests(issue, item) && !on ? '키워드 추천' : ''}
									>
										{on ? '# ' : suggests(issue, item) ? '+ ' : ''}{issue.title}
									</button>
								{/each}
							</div>
						{/if}
					</li>
				{/each}
			</ul>
		</section>
	{/if}
</main>
