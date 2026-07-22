<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import Building from '~icons/iconoir/building';

	// 부트스트랩 확인용 임시 랜딩. 실제 대시보드는 이슈 #9에서 구현.
</script>

<main class="mx-auto flex min-h-svh max-w-2xl flex-col items-center justify-center gap-6 p-6">
	<Building class="size-12 text-muted-foreground" />
	<h1 class="text-center text-2xl font-bold tracking-tight sm:text-3xl">
		울산광역시의회 의정활동 대시보드
	</h1>
	<p class="text-center text-muted-foreground">
		제9대 울산광역시의회의 본회의·위원회 활동, 의원 발언, 의안, 출석률을 한눈에.
	</p>
	<Button href="https://www.council.ulsan.kr" target="_blank" rel="noopener noreferrer">
		울산광역시의회 바로가기
	</Button>
</main>
