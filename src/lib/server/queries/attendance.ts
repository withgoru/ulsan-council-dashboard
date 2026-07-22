import { all } from '$lib/server/db';
import { toAttendance, type AttendanceRow } from '$lib/server/mappers';
import type { AttendanceRecord } from '$lib/types';

const SELECT = `
	SELECT m.member_code AS member_code, a.member_name, a.half, a.meeting_type,
	       a.attended, a.total, a.pct
	FROM attendance_records a
	LEFT JOIN members m ON a.member_id = m.id`;

/** 전체 출석 레코드(의원×반기×회의종류). */
export function getAttendance(): AttendanceRecord[] {
	return all<AttendanceRow>(`${SELECT} ORDER BY a.member_id, a.meeting_type`).map(toAttendance);
}

/** 대시보드 출석 패널용: 본회의 출석률만(의원 번호순). */
export function getPlenaryAttendance(): AttendanceRecord[] {
	return all<AttendanceRow>(`${SELECT} WHERE a.meeting_type = '본회의' ORDER BY a.member_id`).map(
		toAttendance
	);
}

/** 특정 의원의 모든 출석 레코드. */
export function getAttendanceByMember(memCode: string): AttendanceRecord[] {
	return all<AttendanceRow>(
		`${SELECT} WHERE m.member_code = ? ORDER BY a.half, a.meeting_type`,
		memCode
	).map(toAttendance);
}
