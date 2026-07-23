<script lang="ts">
	import PartyBadge from '$lib/components/common/PartyBadge.svelte';
	import type { Member } from '$lib/types';
	import Phone from '~icons/iconoir/phone';
	import Mail from '~icons/iconoir/mail';
	import OpenNewWindow from '~icons/iconoir/open-new-window';

	let { member }: { member: Member } = $props();
</script>

<header class="flex flex-col gap-5 sm:flex-row sm:items-start">
	<img
		src={member.photoUrl}
		alt={member.name}
		width="120"
		height="136"
		class="h-34 w-30 shrink-0 self-center rounded-lg bg-muted object-cover sm:self-start"
	/>

	<div class="flex min-w-0 flex-1 flex-col gap-3">
		<div class="flex flex-wrap items-center gap-2">
			<h1 class="text-2xl font-bold tracking-tight">{member.name}</h1>
			<PartyBadge partyId={member.partyId} partyName={member.partyName} />
		</div>

		{#if member.district}
			<p class="text-sm text-muted-foreground">{member.district}</p>
		{/if}

		{#if member.committees.length}
			<ul class="flex flex-wrap gap-1.5">
				{#each member.committees as c (c.name + c.role)}
					<li class="rounded-md border border-border px-2 py-0.5 text-xs">
						{c.name}
						<span class="text-muted-foreground">{c.role}</span>
					</li>
				{/each}
			</ul>
		{/if}

		<!-- 연락처 -->
		<div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
			{#if member.contact.phone}
				<a
					href="tel:{member.contact.phone}"
					class="inline-flex items-center gap-1 text-muted-foreground"
				>
					<Phone class="size-3.5" />{member.contact.phone}
				</a>
			{/if}
			{#if member.contact.email}
				<a
					href="mailto:{member.contact.email}"
					class="inline-flex items-center gap-1 text-muted-foreground"
				>
					<Mail class="size-3.5" />{member.contact.email}
				</a>
			{/if}
			{#if member.profileUrl}
				<a
					href={member.profileUrl}
					target="_blank"
					rel="noopener noreferrer"
					class="inline-flex items-center gap-1 text-muted-foreground hover:underline"
				>
					의회 프로필 <OpenNewWindow class="size-3" />
				</a>
			{/if}
		</div>

		{#if member.bio.length}
			<div class="flex flex-col gap-0.5 text-sm text-muted-foreground">
				{#each member.bio as line (line)}<p>{line}</p>{/each}
			</div>
		{/if}
	</div>
</header>
