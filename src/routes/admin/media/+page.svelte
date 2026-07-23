<script lang="ts">
	import { onMount } from 'svelte';
	import { formatDate } from '$lib/utils/date';

	// 개발 전용 큐레이션 페이지. `npm run dev` 에서만 동작(Vite 미들웨어 /__curation/* 사용).
	// 후보(media_articles)를 보고 노출 여부·메모를 정해 media-curation.json 에 저장 → 커밋 → 재배포.
	type Candidate = {
		url: string;
		title: string;
		description: string | null;
		press: string | null;
		publishedAt: string | null;
	};
	type Curated = {
		url: string;
		title: string;
		press: string | null;
		publishedAt: string | null;
		note: string | null;
	};

	let candidates = $state<Candidate[]>([]);
	let approved = $state<Record<string, boolean>>({});
	let notes = $state<Record<string, string>>({});
	let loading = $state(true);
	let error = $state<string | null>(null);
	let saveMsg = $state<string | null>(null);

	onMount(async () => {
		try {
			const res = await fetch('/__curation/candidates');
			if (!res.ok)
				throw new Error(`후보 조회 실패 (${res.status}). npm run dev 로 실행 중인지 확인하세요.`);
			const data = await res.json();
			candidates = data.candidates ?? [];
			for (const c of (data.curated ?? []) as Curated[]) {
				approved[c.url] = true;
				if (c.note) notes[c.url] = c.note;
			}
		} catch (e) {
			error = String(e);
		} finally {
			loading = false;
		}
	});

	const approvedCount = $derived(Object.values(approved).filter(Boolean).length);

	async function save() {
		saveMsg = null;
		const articles: Curated[] = candidates
			.filter((c) => approved[c.url])
			.map((c) => ({
				url: c.url,
				title: c.title,
				press: c.press,
				publishedAt: c.publishedAt,
				note: notes[c.url]?.trim() || null
			}));
		try {
			const res = await fetch('/__curation/save', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ articles })
			});
			if (!res.ok) throw new Error(`저장 실패 (${res.status})`);
			const r = await res.json();
			saveMsg = `저장 완료: ${r.count}건. 커밋 후 배포하면 반영됩니다.`;
		} catch (e) {
			saveMsg = `오류: ${e}`;
		}
	}
</script>

<svelte:head><title>큐레이션 · 언론이 본 의회 (dev)</title></svelte:head>

<main id="main-content" tabindex="-1" class="mx-auto max-w-3xl px-4 py-6">
	<h1 class="text-xl font-bold tracking-tight">
		언론 기사 큐레이션 <span class="text-sm font-normal text-muted-foreground">(개발 전용)</span>
	</h1>
	<p class="mt-1 text-sm text-muted-foreground">
		노출할 기사를 선택하고 저장하세요. 저장 결과는 <code>src/lib/data/media-curation.json</code>에
		기록되며, 커밋·배포해야 공개됩니다.
	</p>

	{#if loading}
		<p class="py-10 text-center text-sm text-muted-foreground">불러오는 중…</p>
	{:else if error}
		<p class="mt-4 rounded-lg border border-destructive/40 bg-destructive/10 p-4 text-sm">
			{error}
		</p>
	{:else if !candidates.length}
		<p class="py-10 text-center text-sm text-muted-foreground">
			후보가 없습니다. 먼저 <code>cd scraper && uv run python media.py</code> 로 기사를 수집하세요.
		</p>
	{:else}
		<div
			class="sticky top-0 z-10 mt-4 flex items-center justify-between border-b bg-background/90 py-2 backdrop-blur"
		>
			<span class="text-sm">후보 {candidates.length}건 · 선택 <b>{approvedCount}</b>건</span>
			<button
				type="button"
				onclick={save}
				class="rounded-md bg-foreground px-3 py-1.5 text-sm font-medium text-background"
			>
				저장
			</button>
		</div>
		{#if saveMsg}<p class="mt-2 text-sm text-muted-foreground">{saveMsg}</p>{/if}

		<ul class="mt-2">
			{#each candidates as c (c.url)}
				<li class="flex gap-3 border-b border-border/70 py-3">
					<input
						type="checkbox"
						checked={approved[c.url] ?? false}
						onchange={(e) => (approved[c.url] = e.currentTarget.checked)}
						class="mt-1 size-4 shrink-0"
						aria-label="노출 선택: {c.title}"
					/>
					<div class="flex min-w-0 flex-1 flex-col gap-1">
						<div class="flex items-center gap-2 text-xs text-muted-foreground">
							{#if c.publishedAt}<time>{formatDate(c.publishedAt)}</time>{/if}
							{#if c.press}<span>· {c.press}</span>{/if}
						</div>
						<a
							href={c.url}
							target="_blank"
							rel="noopener noreferrer"
							class="text-sm font-medium hover:underline"
						>
							{c.title}
						</a>
						{#if c.description}<p class="line-clamp-2 text-xs text-muted-foreground">
								{c.description}
							</p>{/if}
						{#if approved[c.url]}
							<input
								type="text"
								placeholder="편집자 메모(선택)"
								value={notes[c.url] ?? ''}
								oninput={(e) => (notes[c.url] = e.currentTarget.value)}
								class="mt-1 rounded-md border border-border px-2 py-1 text-xs"
							/>
						{/if}
					</div>
				</li>
			{/each}
		</ul>
	{/if}
</main>
