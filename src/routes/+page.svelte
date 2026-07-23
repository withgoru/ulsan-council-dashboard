<script lang="ts">
	import ActivityFeed from '$lib/components/dashboard/ActivityFeed.svelte';
	import MemberRoster from '$lib/components/dashboard/MemberRoster.svelte';
	import AttendancePanel from '$lib/components/dashboard/AttendancePanel.svelte';
	import Timeline from '$lib/components/dashboard/Timeline.svelte';
	import MediaTimeline from '$lib/components/dashboard/MediaTimeline.svelte';
	import SeoHead from '$lib/components/common/SeoHead.svelte';
	import YearSelect from '$lib/components/common/YearSelect.svelte';
	import { feedItemYear, newsYear } from '$lib/utils/year';
	import { page } from '$app/state';
	import { browser } from '$app/environment';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const DASHBOARD_LIMIT = 10; // 우측 언론 패널
	// 왼쪽 컬럼은 활동+보도자료 2개 패널이 한 화면에 함께 들어가도록 소수만 노출.
	// 활동 항목이 보도자료보다 커서 상한을 다르게 둔다. 넘치는 항목은 각 패널의
	// '전체 보기'(→ /activities, /press)로 이동.
	const LEFT_ACTIVITY_LIMIT = 3;
	const LEFT_PRESS_LIMIT = 3;

	// 선택 연도(URL ?year, 기본 최신). 프리렌더 시엔 기본값, 클라이언트에서 URL 반영.
	const year = $derived(
		browser ? Number(page.url.searchParams.get('year')) || data.years[0] : data.years[0]
	);
	const yearFeed = $derived(
		data.feed.filter((it) => feedItemYear(it) === year).slice(0, LEFT_ACTIVITY_LIMIT)
	);
	const yearNews = $derived(
		data.news.filter((it) => newsYear(it) === year).slice(0, LEFT_PRESS_LIMIT)
	);
	const yearQuery = $derived(year ? `?year=${year}` : '');

	// 모바일 세그먼트 탭(데스크톱은 3열 동시 표시라 무시).
	type PanelId = 'activity' | 'press' | 'attendance' | 'roster' | 'media';
	const tabs: { id: PanelId; label: string }[] = [
		{ id: 'activity', label: '활동' },
		{ id: 'press', label: '보도자료' },
		{ id: 'attendance', label: '출석' },
		{ id: 'roster', label: '명단' },
		{ id: 'media', label: '언론' }
	];
	let active = $state<PanelId>('activity');
</script>

<SeoHead />

<main
	id="main-content"
	tabindex="-1"
	class="mx-auto flex min-h-svh max-w-350 flex-col px-4 py-4 lg:h-svh lg:py-6"
>
	<header class="mb-4 flex shrink-0 items-end justify-between gap-3">
		<div>
			<p class="text-xs font-medium text-muted-foreground">제9대 울산광역시의회</p>
			<h1 class="text-xl font-bold tracking-tight sm:text-2xl">의정활동 대시보드</h1>
		</div>
		<YearSelect years={data.years} />
	</header>

	<!-- 모바일 전용 세그먼트 탭(가로 스크롤). 데스크톱(lg↑)에서는 3열 동시 표시라 숨김. -->
	<nav
		aria-label="대시보드 패널 선택"
		class="sticky top-0 z-10 mb-4 flex shrink-0 gap-1 overflow-x-auto rounded-lg border bg-background/80 p-1 backdrop-blur lg:hidden"
	>
		{#each tabs as tab (tab.id)}
			<button
				type="button"
				aria-pressed={active === tab.id}
				onclick={() => (active = tab.id)}
				class="shrink-0 rounded-md px-3 py-1.5 text-sm font-medium whitespace-nowrap transition-colors focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none {active ===
				tab.id
					? 'bg-foreground text-background'
					: 'text-muted-foreground hover:bg-muted'}"
			>
				{tab.label}
			</button>
		{/each}
	</nav>

	<!-- 데스크톱 3열: 왼쪽(활동+보도자료) / 가운데(출석+명단) / 오른쪽(언론). 컬럼 단위 스크롤. -->
	<div class="dashboard-grid gap-6 lg:min-h-0 lg:flex-1" data-active={active}>
		<div class="col col-left flex flex-col gap-6 lg:min-h-0 lg:overflow-y-auto lg:pr-1">
			<div class="panel rounded-xl border p-4" data-panel="activity">
				<ActivityFeed items={yearFeed} moreHref="/activities{yearQuery}" />
			</div>
			<div class="panel rounded-xl border p-4" data-panel="press">
				<Timeline items={yearNews} title="보도자료 타임라인" moreHref="/press{yearQuery}" />
			</div>
		</div>

		<div class="col col-center flex flex-col gap-6 lg:min-h-0 lg:overflow-y-auto lg:pr-1">
			<div class="panel rounded-xl border p-4" data-panel="attendance">
				<AttendancePanel attendance={data.attendance} members={data.members} />
			</div>
			<div class="panel rounded-xl border p-4" data-panel="roster">
				<MemberRoster members={data.members} />
			</div>
		</div>

		<div class="col col-right flex flex-col gap-6 lg:min-h-0 lg:overflow-y-auto lg:pr-1">
			<div class="panel flex flex-col rounded-xl border p-4" data-panel="media">
				<MediaTimeline articles={data.media.slice(0, DASHBOARD_LIMIT)} moreHref="/media" />
			</div>
		</div>
	</div>
</main>

<style>
	.dashboard-grid {
		display: grid;
		grid-template-columns: 1fr;
		grid-template-areas: 'left' 'center' 'right';
	}
	.col-left {
		grid-area: left;
	}
	.col-center {
		grid-area: center;
	}
	.col-right {
		grid-area: right;
	}

	/* 모바일(<lg): 컬럼을 contents 로 풀어 선택된 탭의 패널 하나만 표시.
	   패널은 자연 높이라 메뉴-컨텐츠 사이 빈 공간이 생기지 않는다. */
	@media (max-width: 1023px) {
		.col {
			display: contents;
		}
		.panel {
			display: none;
		}
		.dashboard-grid[data-active='activity'] .panel[data-panel='activity'],
		.dashboard-grid[data-active='press'] .panel[data-panel='press'],
		.dashboard-grid[data-active='attendance'] .panel[data-panel='attendance'],
		.dashboard-grid[data-active='roster'] .panel[data-panel='roster'],
		.dashboard-grid[data-active='media'] .panel[data-panel='media'] {
			display: block;
		}
		.dashboard-grid[data-active='media'] .panel[data-panel='media'] {
			display: flex;
			min-height: 16rem;
		}
	}

	/* lg(1024px)↑: 3열. 왼쪽/오른쪽보다 가운데(명단 2열)를 넓게. */
	@media (min-width: 1024px) {
		.dashboard-grid {
			grid-template-columns: minmax(300px, 1fr) minmax(400px, 1.3fr) minmax(280px, 1fr);
			grid-template-areas: 'left center right';
		}
	}
</style>
