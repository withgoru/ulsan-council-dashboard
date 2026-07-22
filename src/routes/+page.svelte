<script lang="ts">
	import Building from '~icons/iconoir/building';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	const counts = $derived(data.counts);
	const sampleMember = $derived(data.sampleMember);
</script>

<main class="mx-auto flex min-h-svh max-w-2xl flex-col items-center justify-center gap-6 p-6">
	<Building class="size-12 text-muted-foreground" />
	<h1 class="text-center text-2xl font-bold tracking-tight sm:text-3xl">
		울산광역시의회 의정활동 대시보드
	</h1>
	<p class="text-center text-muted-foreground">제9대 울산광역시의회 · 데이터 레이어 검증</p>

	<!-- 데이터 접근 레이어가 빌드 시점에 SQLite 를 읽었음을 보여주는 임시 요약. UI 는 이슈 #9. -->
	<dl class="grid grid-cols-2 gap-3 text-center sm:grid-cols-5">
		{#each Object.entries(counts) as [key, value] (key)}
			<div class="rounded-lg bg-muted/40 p-3">
				<dt class="text-xs text-muted-foreground">{key}</dt>
				<dd class="text-xl font-semibold tabular-nums">{value}</dd>
			</div>
		{/each}
	</dl>

	{#if sampleMember}
		<p class="text-sm text-muted-foreground">
			예: {sampleMember.name} ({sampleMember.partyName}) · {sampleMember.committees
				.map((c) => `${c.name}(${c.role})`)
				.join(', ')}
		</p>
	{/if}
</main>
