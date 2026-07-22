<script lang="ts">
	import ActivityFeed from '$lib/components/dashboard/ActivityFeed.svelte';
	import MemberRoster from '$lib/components/dashboard/MemberRoster.svelte';
	import AttendancePanel from '$lib/components/dashboard/AttendancePanel.svelte';
	import Timeline from '$lib/components/dashboard/Timeline.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
</script>

<div class="mx-auto flex min-h-svh max-w-[1400px] flex-col px-4 py-4 lg:h-svh lg:py-6">
	<header class="mb-4 shrink-0">
		<p class="text-xs font-medium text-muted-foreground">제9대 울산광역시의회</p>
		<h1 class="text-xl font-bold tracking-tight sm:text-2xl">의정활동 대시보드</h1>
	</header>

	<!-- 데스크톱 3열(활동 / 센터[명단·출석] / 타임라인), 모바일 4단(활동→명단→출석→타임라인). -->
	<div class="dashboard-grid min-h-0 flex-1 gap-6">
		<div class="area-activity flex min-h-0 flex-col rounded-xl border p-4">
			<ActivityFeed items={data.feed} />
		</div>

		<div class="area-center flex min-h-0 flex-col gap-6 lg:overflow-y-auto">
			<div class="rounded-xl border p-4">
				<MemberRoster members={data.members} />
			</div>
			<div class="rounded-xl border p-4">
				<AttendancePanel attendance={data.attendance} members={data.members} />
			</div>
		</div>

		<div class="area-timeline flex min-h-0 flex-col rounded-xl border p-4">
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

	/* lg(1024px)↑: 3열 25% / 50% / 25%. 각 컬럼이 뷰포트 높이 안에서 독립 스크롤. */
	@media (min-width: 1024px) {
		.dashboard-grid {
			grid-template-columns: minmax(280px, 1fr) minmax(480px, 2fr) minmax(280px, 1fr);
			grid-template-areas: 'activity center timeline';
		}
	}
</style>
