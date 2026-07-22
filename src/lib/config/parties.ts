// 정당 식별자·표시명 매핑. 브랜드 색상(CSS 변수)은 이슈 #11에서 확장한다.
// DB 의 members.party 에 저장된 한글 정당명을 안정적인 id 로 정규화한다.

export type PartyId = 'ppp' | 'dpk' | 'jinbo' | 'etc';

export interface Party {
	id: PartyId;
	name: string; // 공식 표기명
}

export const PARTIES: Record<PartyId, Party> = {
	ppp: { id: 'ppp', name: '국민의힘' },
	dpk: { id: 'dpk', name: '더불어민주당' },
	jinbo: { id: 'jinbo', name: '진보당' },
	etc: { id: 'etc', name: '무소속·기타' }
};

const NAME_TO_ID: Record<string, PartyId> = {
	국민의힘: 'ppp',
	더불어민주당: 'dpk',
	진보당: 'jinbo'
};

/** DB 의 한글 정당명 → PartyId. 미매칭은 'etc'. */
export function toPartyId(partyName: string | null | undefined): PartyId {
	if (!partyName) return 'etc';
	return NAME_TO_ID[partyName.trim()] ?? 'etc';
}
