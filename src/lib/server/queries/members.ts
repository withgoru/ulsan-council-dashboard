import { all, get } from '$lib/server/db';
import { toMember, type MemberRow } from '$lib/server/mappers';
import type { Member } from '$lib/types';

const COLS = `member_code, name, party, district, committee, birth_year, phone, email, bio, profile_url, photo_url`;

/** 전체 의원(번호순). */
export function getAllMembers(): Member[] {
	return all<MemberRow>(`SELECT ${COLS} FROM members ORDER BY id`).map(toMember);
}

/** slug(=member_code)로 단일 의원. */
export function getMemberBySlug(slug: string): Member | null {
	const row = get<MemberRow>(`SELECT ${COLS} FROM members WHERE member_code = ?`, slug);
	return row ? toMember(row) : null;
}

/** 프리렌더 엔트리 생성용 slug 목록. */
export function getMemberSlugs(): string[] {
	return all<{ member_code: string }>(`SELECT member_code FROM members ORDER BY id`).map(
		(r) => r.member_code
	);
}
