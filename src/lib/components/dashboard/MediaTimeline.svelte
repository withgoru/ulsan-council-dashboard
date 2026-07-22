<script lang="ts">
	import Journal from '~icons/iconoir/journal';

	// "언론이 본 의회": 외부 언론의 의회 보도 타임라인.
	// 외부 기사 데이터는 아직 수집하지 않으므로 지금은 빈 상태 슬롯만 제공(추후 스크래퍼 연결).
</script>

<section aria-labelledby="media-heading" class="flex min-h-0 flex-1 flex-col">
	<h2 id="media-heading" class="mb-2 shrink-0 text-sm font-semibold tracking-tight">
		언론이 본 의회
	</h2>
	<div
		class="flex flex-1 flex-col items-center justify-center gap-2 rounded-lg border border-dashed p-6 text-center text-muted-foreground"
	>
		<Journal class="size-8 opacity-60" />
		<p class="text-sm font-medium">외부 언론 보도 타임라인</p>
		<p class="text-xs leading-relaxed">
			의회를 다룬 외부 언론 기사를 모아 보여줄 예정입니다.<br />데이터 수집 준비 중입니다.
		</p>
	</div>
</section>
