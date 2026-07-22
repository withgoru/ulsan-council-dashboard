import { all } from '$lib/server/db';
import { toBill, type BillRow } from '$lib/server/mappers';
import type { Bill } from '$lib/types';

// bills.member_id(대표발의 의원) → members.member_code 조인.
const SELECT = `
	SELECT b.id, b.bill_number, b.bill_name, b.proposer_type, b.proposer_name,
	       m.member_code AS proposer_mem_code, b.committee, b.proposed_date,
	       b.status, b.result, b.source_url
	FROM bills b
	LEFT JOIN members m ON b.member_id = m.id`;

/** 전체 의안(제안일 최신순). */
export function getBills(limit?: number): Bill[] {
	const rows = all<BillRow>(`${SELECT} ORDER BY b.proposed_date DESC, b.id DESC`).map(toBill);
	return limit ? rows.slice(0, limit) : rows;
}

/** 특정 의원이 대표발의한 의안. */
export function getBillsByMember(memCode: string): Bill[] {
	return all<BillRow>(
		`${SELECT} WHERE m.member_code = ? ORDER BY b.proposed_date DESC, b.id DESC`,
		memCode
	).map(toBill);
}
