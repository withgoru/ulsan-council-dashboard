// DB 행(snake_case) → 프론트 타입(camelCase) 변환. member_code 를 slug 로 그대로 사용한다.
import { toPartyId } from '$lib/config/parties';
import type {
	Activity,
	AttendanceRecord,
	Bill,
	BillStatus,
	Committee,
	Member,
	NewsItem,
	SpeechBoardItem,
	SpeechKind,
	SpeechSegment
} from '$lib/types';

// ── DB 행 타입 ────────────────────────────────────────────────────────────
export interface MemberRow {
	member_code: string;
	name: string;
	party: string | null;
	district: string | null;
	committee: string | null;
	birth_year: number | null;
	phone: string | null;
	email: string | null;
	bio: string | null;
	profile_url: string | null;
	photo_url: string | null;
}

export interface AttendanceRow {
	member_code: string | null;
	member_name: string;
	half: string;
	meeting_type: string;
	attended: number | null;
	total: number | null;
	pct: number | null;
}

export interface ActivityRow {
	id: number;
	committee_name?: string | null;
	title: string;
	session_round: string | null;
	posted_date: string | null;
	view_count: number | null;
	source_url: string | null;
}

export interface BillRow {
	id: number;
	bill_number: string;
	bill_name: string;
	proposer_type: string | null;
	proposer_name: string | null;
	proposer_mem_code: string | null;
	committee: string | null;
	proposed_date: string | null;
	status: string;
	result: string | null;
	source_url: string | null;
}

export interface NewsRow {
	id: number;
	title: string;
	author_raw: string | null;
	member_code: string | null;
	posted_date: string | null;
	view_count: number | null;
	source_url: string | null;
}

export interface SpeechBoardRow {
	id: number;
	kind: string;
	title: string | null;
	member_code: string | null;
	member_name: string;
	committee: string | null;
	session_round: string | null;
	posted_date: string | null;
	view_count: number | null;
	source_url: string | null;
}

export interface SpeechSegmentRow {
	id: number;
	member_code: string | null;
	speaker_name: string | null;
	speaker_role: string | null;
	meeting_type: string;
	meeting_date: string | null;
	session_no: string | null;
	round_no: string | null;
	agenda_item: string | null;
	text: string;
	clik_docid: string;
}

// ── 헬퍼 ──────────────────────────────────────────────────────────────────
/** "의회운영(부위원장) · 행정자치(위원)" → [{name, role}] */
export function parseCommittees(raw: string | null): Committee[] {
	if (!raw) return [];
	return raw
		.split('·')
		.map((s) => s.trim())
		.filter(Boolean)
		.map((chunk) => {
			const m = chunk.match(/^(.*?)\(([^)]+)\)$/);
			return m ? { name: m[1].trim(), role: m[2].trim() } : { name: chunk, role: '위원' };
		});
}

const BILL_STATUS_LABEL: Record<BillStatus, string> = {
	acceptance: '접수',
	processing: '처리',
	mooring: '계류'
};

const SPEECH_KIND_LABEL: Record<SpeechKind, string> = {
	free_speech: '5분자유발언',
	municipal_qna: '시정질문답변',
	written_qna: '서면질문답변'
};

// ── 매퍼 ──────────────────────────────────────────────────────────────────
export function toMember(r: MemberRow): Member {
	return {
		memCode: r.member_code,
		slug: r.member_code,
		name: r.name,
		partyId: toPartyId(r.party),
		partyName: r.party ?? '무소속·기타',
		district: r.district,
		photoUrl: r.photo_url,
		committees: parseCommittees(r.committee),
		birthYear: r.birth_year,
		contact: { phone: r.phone, email: r.email },
		bio: (r.bio ?? '')
			.split('\n')
			.map((s) => s.trim())
			.filter(Boolean),
		profileUrl: r.profile_url
	};
}

export function toAttendance(r: AttendanceRow): AttendanceRecord {
	return {
		memCode: r.member_code,
		memberName: r.member_name,
		half: r.half,
		meetingType: r.meeting_type,
		attended: r.attended ?? 0,
		total: r.total ?? 0,
		rate: r.pct ?? 0
	};
}

export function toActivity(r: ActivityRow, type: '본회의' | '위원회'): Activity {
	return {
		id: `activity-${type === '본회의' ? 'p' : 'c'}-${r.id}`,
		kind: 'activity',
		type,
		committeeName: r.committee_name ?? null,
		title: r.title,
		sessionRound: r.session_round,
		date: r.posted_date,
		viewCount: r.view_count,
		sourceUrl: r.source_url
	};
}

export function toBill(r: BillRow): Bill {
	const status = (
		['acceptance', 'processing', 'mooring'].includes(r.status) ? r.status : 'acceptance'
	) as BillStatus;
	return {
		id: `bill-${r.id}`,
		kind: 'bill',
		billNo: r.bill_number,
		title: r.bill_name,
		proposedDate: r.proposed_date,
		status,
		statusLabel: BILL_STATUS_LABEL[status],
		proposerType: r.proposer_type,
		proposerName: r.proposer_name,
		proposerMemCode: r.proposer_mem_code,
		committee: r.committee,
		result: r.result,
		sourceUrl: r.source_url
	};
}

export function toNews(r: NewsRow): NewsItem {
	return {
		id: `news-${r.id}`,
		kind: 'news',
		title: r.title,
		publishedDate: r.posted_date,
		author: r.author_raw,
		memCode: r.member_code,
		sourceUrl: r.source_url
	};
}

export function toSpeechBoard(r: SpeechBoardRow): SpeechBoardItem {
	const speechKind = r.kind as SpeechKind;
	return {
		id: `speech-board-${r.id}`,
		kind: 'speech-board',
		speechKind,
		speechKindLabel: SPEECH_KIND_LABEL[speechKind] ?? r.kind,
		title: r.title,
		memCode: r.member_code,
		memberName: r.member_name,
		committee: r.committee,
		sessionRound: r.session_round,
		date: r.posted_date,
		viewCount: r.view_count,
		sourceUrl: r.source_url
	};
}

export function toSpeechSegment(r: SpeechSegmentRow): SpeechSegment {
	return {
		id: `segment-${r.id}`,
		kind: 'speech',
		memCode: r.member_code,
		speakerName: r.speaker_name,
		speakerRole: r.speaker_role,
		meetingType: r.meeting_type,
		meetingDate: r.meeting_date,
		sessionNo: r.session_no,
		roundNo: r.round_no,
		agendaItem: r.agenda_item,
		text: r.text,
		minutesDocId: r.clik_docid
	};
}
