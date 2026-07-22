// 날짜 포맷 유틸. 데이터는 ISO 문자열(YYYY-MM-DD) 기준.

/** '2026-07-20' → '2026.07.20'. 파싱 불가 시 원문/빈문자열. */
export function formatDate(iso: string | null | undefined): string {
	if (!iso) return '';
	const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})/);
	return m ? `${m[1]}.${m[2]}.${m[3]}` : iso;
}

/** '2026-07-20' → '7월 20일' (같은 해 타임라인용 간결 표기). */
export function formatMonthDay(iso: string | null | undefined): string {
	if (!iso) return '';
	const m = iso.match(/^\d{4}-(\d{2})-(\d{2})/);
	return m ? `${Number(m[1])}월 ${Number(m[2])}일` : iso;
}
