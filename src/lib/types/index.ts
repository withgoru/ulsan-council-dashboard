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

// ── 이슈 타임라인(태그 기반 멀티미디어) ──────────────────────────────────────
export type MediaType = 'article' | 'video' | 'release' | 'sns';

export const MEDIA_TYPE_LABEL: Record<MediaType, string> = {
	article: '기사',
	video: '영상',
	release: '보도자료',
	sns: 'SNS'
};

/** 큐레이션된 미디어 항목(기사·영상 등). data/media-curation.json 의 items 풀. */
export interface MediaItem {
	url: string;
	type: MediaType;
	title: string;
	source: string | null; // 언론사/채널명
	publishedAt: string | null; // ISO date
	note: string | null; // 편집자 메모(선택)
}

export type IssueStatus = 'active' | 'ended' | 'hidden';

/** 이슈(태그): 관련 미디어를 묶는 주제. itemUrls 로 items 를 N:N 참조. */
export interface Issue {
	id: string;
	title: string;
	description: string | null;
	status: IssueStatus;
	pinned: boolean;
	order: number;
	startDate: string | null;
	endDate: string | null;
	keywords: string[]; // 하이브리드 태깅용 추천 키워드
	itemUrls: string[]; // 소속 미디어 url (items 참조)
}

/** 렌더용: 이슈 + 해석된 미디어 목록(최신순). */
export interface ResolvedIssue extends Omit<Issue, 'itemUrls'> {
	items: MediaItem[];
}

export type { PartyId, Party } from '$lib/config/parties';
