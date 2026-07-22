// 프론트엔드 데이터 계약. DB(snake_case) 는 mappers 를 거쳐 이 camelCase 타입으로 변환된다.
// MemberFeedItem 은 kind 판별 유니온으로 의원 상세 페이지의 통합 피드를 구성한다.
import type { PartyId } from '$lib/config/parties';

export interface Committee {
	name: string; // 예: 의회운영
	role: string; // 예: 위원장 / 부위원장 / 위원
}

export interface Member {
	memCode: string;
	slug: string; // 라우팅 키(= memCode)
	name: string;
	partyId: PartyId;
	partyName: string;
	district: string | null;
	photoUrl: string | null;
	committees: Committee[];
	birthYear: number | null;
	contact: { phone: string | null; email: string | null };
	bio: string[];
	profileUrl: string | null;
}

export interface AttendanceRecord {
	memCode: string | null;
	memberName: string;
	half: string; // 전반기 / 후반기
	meetingType: string; // 본회의 / 운영위 / ...
	attended: number;
	total: number;
	rate: number; // 0~100
}

export interface Activity {
	id: string;
	kind: 'activity';
	type: '본회의' | '위원회';
	committeeName: string | null;
	title: string;
	sessionRound: string | null;
	date: string | null; // ISO
	viewCount: number | null;
	sourceUrl: string | null;
}

export type BillStatus = 'acceptance' | 'processing' | 'mooring';

export interface Bill {
	id: string;
	kind: 'bill';
	billNo: string;
	title: string;
	proposedDate: string | null;
	status: BillStatus;
	statusLabel: string; // 접수 / 처리 / 계류
	proposerType: string | null; // 의원 / 의장 / 시장 ...
	proposerName: string | null; // 대표발의자(+공동) 원문
	proposerMemCode: string | null;
	committee: string | null;
	result: string | null; // 본회의처리결과
	sourceUrl: string | null;
}

export interface NewsItem {
	id: string;
	kind: 'news';
	title: string;
	publishedDate: string | null;
	author: string | null;
	memCode: string | null;
	sourceUrl: string | null;
}

export type SpeechKind = 'free_speech' | 'municipal_qna' | 'written_qna';

/** 발언류 게시판 메타(제목 인덱스). 실제 발언 원문은 SpeechSegment. */
export interface SpeechBoardItem {
	id: string;
	kind: 'speech-board';
	speechKind: SpeechKind;
	speechKindLabel: string; // 5분자유발언 / 시정질문답변 / 서면질문답변
	title: string | null;
	memCode: string | null;
	memberName: string;
	committee: string | null;
	sessionRound: string | null;
	date: string | null;
	viewCount: number | null;
	sourceUrl: string | null;
}

/** CLIK 회의록의 발언자별 실제 발언 원문(핵심 콘텐츠). */
export interface SpeechSegment {
	id: string;
	kind: 'speech';
	memCode: string | null;
	speakerName: string | null;
	speakerRole: string | null;
	meetingType: string; // 본회의 / 위원회명
	meetingDate: string | null;
	sessionNo: string | null;
	roundNo: string | null;
	agendaItem: string | null;
	text: string;
	minutesDocId: string;
}

export type MemberFeedItem = Activity | Bill | NewsItem | SpeechBoardItem | SpeechSegment;

export type { PartyId, Party } from '$lib/config/parties';
