<script lang="ts">
	import { theme } from '$lib/stores/theme';
	import SunLight from '~icons/iconoir/sun-light';
	import HalfMoon from '~icons/iconoir/half-moon';
</script>

<button
	type="button"
	onclick={theme.toggle}
	aria-label={$theme === 'dark' ? '라이트 모드로 전환' : '다크 모드로 전환'}
	class="inline-flex size-9 items-center justify-center rounded-lg border border-border bg-background/80 text-muted-foreground backdrop-blur transition-colors hover:bg-muted hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
>
	{#if $theme === 'dark'}
		<SunLight class="size-4" />
	{:else}
		<HalfMoon class="size-4" />
	{/if}
</button>
