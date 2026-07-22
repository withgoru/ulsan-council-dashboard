<script lang="ts">
	import ActivityFeed from '$lib/components/dashboard/ActivityFeed.svelte';
	import MemberRoster from '$lib/components/dashboard/MemberRoster.svelte';
	import AttendancePanel from '$lib/components/dashboard/AttendancePanel.svelte';
	import Timeline from '$lib/components/dashboard/Timeline.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	// 모바일에서만 쓰는 패널 전환 상태(데스크톱은 3열 동시 표시라 무시됨).
	type PanelId = 'activity' | 'roster' | 'attendance' | 'timeline';
	const tabs: { id: PanelId; label: string }[] = [
		{ id: 'activity', label: '활동' },
		{ id: 'roster', label: '명단' },
		{ id: 'attendance', label: '출석' },
		{ id: 'timeline', label: '뉴스' }
	];
	let active = $state<PanelId>('activity');
</script>

<div class="mx-auto flex min-h-svh max-w-[1400px] flex-col px-4 py-4 lg:h-svh lg:py-6">
	<header class="mb-4 shrink-0">
		<p class="text-xs font-medium text-muted-foreground">제9대 울산광역시의회</p>
		<h1 class="text-xl font-bold tracking-tight sm:text-2xl">의정활동 대시보드</h1>
	</header>

	<!-- 모바일 전용 세그먼트 탭. 데스크톱(lg↑)에서는 3열을 모두 보여주므로 숨김. -->
	<nav
		aria-label="대시보드 패널 선택"
		class="sticky top-0 z-10 mb-4 grid shrink-0 grid-cols-4 gap-1 rounded-lg border bg-background/80 p-1 backdrop-blur lg:hidden"
	>
		{#each tabs as tab (tab.id)}
			<button
				type="button"
				aria-pressed={active === tab.id}
				onclick={() => (active = tab.id)}
				class="rounded-md px-2 py-1.5 text-sm font-medium transition-colors focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none {active ===
				tab.id
					? 'bg-foreground text-background'
					: 'text-muted-foreground hover:bg-muted'}"
			>
				{tab.label}
			</button>
		{/each}
	</nav>

	<!-- 데스크톱 3열(활동 / 센터[명단·출석] / 타임라인), 모바일은 탭으로 한 패널씩. -->
	<div class="dashboard-grid min-h-0 flex-1 gap-6" data-active={active}>
		<div
			class="panel area-activity flex min-h-0 flex-col rounded-xl border p-4"
			data-panel="activity"
		>
			<ActivityFeed items={data.feed} />
		</div>

		<div class="area-center flex min-h-0 flex-col gap-6 lg:overflow-y-auto">
			<div class="panel rounded-xl border p-4" data-panel="roster">
				<MemberRoster members={data.members} />
			</div>
			<div class="panel rounded-xl border p-4" data-panel="attendance">
				<AttendancePanel attendance={data.attendance} members={data.members} />
			</div>
		</div>

		<div
			class="panel area-timeline flex min-h-0 flex-col rounded-xl border p-4"
			data-panel="timeline"
		>
			<Timeline items={data.news} />
		</div>
	</div>
</div>

<style>
	.dashboard-grid {
		display: grid;
		grid-template-columns: 1fr;
		grid-template-areas: 'activity' 'center' 'timeline';
	}
	.area-activity {
		grid-area: activity;
	}
	.area-center {
		grid-area: center;
	}
	.area-timeline {
		grid-area: timeline;
	}

	/* 모바일(<lg): 선택된 탭의 패널 하나만 표시 → 페이지 길이를 한 패널 분량으로 제한.
	   area-center 를 contents 로 풀어 roster/attendance 를 개별 패널로 제어한다. */
	@media (max-width: 1023px) {
		.area-center {
			display: contents;
		}
		.panel {
			display: none;
		}
		.dashboard-grid[data-active='activity'] .panel[data-panel='activity'],
		.dashboard-grid[data-active='roster'] .panel[data-panel='roster'],
		.dashboard-grid[data-active='attendance'] .panel[data-panel='attendance'],
		.dashboard-grid[data-active='timeline'] .panel[data-panel='timeline'] {
			display: flex;
		}
	}

	/* lg(1024px)↑: 3열 25% / 50% / 25%. 각 컬럼이 뷰포트 높이 안에서 독립 스크롤. */
	@media (min-width: 1024px) {
		.dashboard-grid {
			grid-template-columns: minmax(280px, 1fr) minmax(480px, 2fr) minmax(280px, 1fr);
			grid-template-areas: 'activity center timeline';
		}
	}
</style>
