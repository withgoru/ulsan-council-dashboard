<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { browser } from '$app/environment';

	// 연도 필터. 선택값을 URL ?year= 에 반영해 공유·뒤로가기 가능하게 한다.
	// 프리렌더 시에는 searchParams 접근이 금지되므로 기본값(최신 연도)을 쓰고, 클라이언트에서만 URL 반영.
	let { years }: { years: number[] } = $props();

	const current = $derived(
		browser ? Number(page.url.searchParams.get('year')) || years[0] : years[0]
	);

	function change(e: Event) {
		const year = (e.currentTarget as HTMLSelectElement).value;
		const url = new URL(page.url);
		url.searchParams.set('year', year);
		goto(url, { replaceState: true, keepFocus: true, noScroll: true });
	}
</script>

{#if years.length > 1}
	<label class="inline-flex items-center gap-1.5 text-sm">
		<span class="sr-only">연도 선택</span>
		<select
			value={current}
			onchange={change}
			class="rounded-md border border-border bg-background px-2 py-1 text-sm font-medium focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
		>
			{#each years as year (year)}
				<option value={year}>{year}년</option>
			{/each}
		</select>
	</label>
{:else if years.length === 1}
	<span class="text-sm font-medium text-muted-foreground">{years[0]}년</span>
{/if}
