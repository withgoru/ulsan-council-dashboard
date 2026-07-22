<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import DarkModeToggle from '$lib/components/common/DarkModeToggle.svelte';

	let { children } = $props();
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<!-- 스킵 링크: 키보드 포커스 시에만 노출, 본문으로 바로 이동(WCAG 2.4.1) -->
<a
	href="#main-content"
	class="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50 focus:rounded-lg focus:border focus:bg-background focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:ring-2 focus:ring-ring"
>
	본문으로 건너뛰기
</a>

<!-- 전역 다크모드 토글(우상단 고정) -->
<div class="fixed top-3 right-3 z-50">
	<DarkModeToggle />
</div>

{@render children()}
