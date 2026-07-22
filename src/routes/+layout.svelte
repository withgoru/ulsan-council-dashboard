<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import DarkModeToggle from '$lib/components/common/DarkModeToggle.svelte';

	let { children } = $props();
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<!-- 전역 다크모드 토글(우상단 고정) -->
<div class="fixed top-3 right-3 z-50">
	<DarkModeToggle />
</div>

{@render children()}
