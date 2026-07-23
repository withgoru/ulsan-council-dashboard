<script lang="ts">
	import type { PartyId } from '$lib/config/parties';
	import type { AttendanceRecord } from '$lib/types';

	// 본회의·위원회별 출석률을 반기 그룹으로 막대 그래프 + 출석횟수 표기.
	let { attendance, partyId }: { attendance: AttendanceRecord[]; partyId: PartyId } = $props();

	const clamp = (r: number) => Math.max(0, Math.min(100, r));
	const rank = (t: string) => (t === '본회의' ? 0 : 1); // 본회의 먼저

	// 반기별 그룹(전반기/후반기), 각 그룹은 본회의→위원회 순.
	const groups = $derived.by(() => {
		const map = new Map<string, AttendanceRecord[]>();
		for (const a of attendance) {
			const arr = map.get(a.half) ?? [];
			arr.push(a);
			map.set(a.half, arr);
		}
		for (const arr of map.values())
			arr.sort(
				(x, y) =>
					rank(x.meetingType) - rank(y.meetingType) || x.meetingType.localeCompare(y.meetingType)
			);
		return [...map.entries()];
	});
</script>

{#if attendance.length}
	<section aria-labelledby="att-heading">
		<h2 id="att-heading" class="mb-3 text-sm font-semibold tracking-tight">출석 현황</h2>
		<div class="flex flex-col gap-5">
			{#each groups as [half, records] (half)}
				<div>
					<h3 class="mb-2 text-xs font-medium text-muted-foreground">{half}</h3>
					<div class="flex flex-col gap-2.5">
						{#each records as a (a.meetingType)}
							<div class="flex items-center gap-3">
								<span class="w-16 shrink-0 text-xs font-medium">{a.meetingType}</span>
								<div
									class="h-2 flex-1 overflow-hidden rounded-full bg-muted"
									role="meter"
									aria-valuenow={Math.round(clamp(a.rate))}
									aria-valuemin={0}
									aria-valuemax={100}
									aria-label="{a.half} {a.meetingType} 출석 {a.attended}/{a.total} ({Math.round(
										clamp(a.rate)
									)}%)"
								>
									<div
										class="h-full rounded-full"
										style="width: {clamp(a.rate)}%; background-color: var(--party-{partyId})"
									></div>
								</div>
								<span class="w-24 shrink-0 text-right text-xs tabular-nums">
									{a.attended}/{a.total}
									<span class="text-muted-foreground">({clamp(a.rate).toFixed(0)}%)</span>
								</span>
							</div>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	</section>
{/if}
