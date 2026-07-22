<script lang="ts">
	import type { Member } from '$lib/types';
	import MemberCard from './MemberCard.svelte';

	let { members }: { members: Member[] } = $props();
</script>

<section aria-labelledby="roster-heading" class="flex flex-col">
	<div class="mb-2 flex items-baseline justify-between">
		<h2 id="roster-heading" class="text-sm font-semibold tracking-tight">의원 명단</h2>
		<span class="text-xs text-muted-foreground">{members.length}명</span>
	</div>
	<ul class="grid grid-cols-1 gap-2 sm:grid-cols-2">
		{#each members as member (member.memCode)}
			<li><MemberCard {member} /></li>
		{/each}
	</ul>
</section>
