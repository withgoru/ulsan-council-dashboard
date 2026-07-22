import { all } from '$lib/server/db';
import {
	toSpeechBoard,
	toSpeechSegment,
	type SpeechBoardRow,
	type SpeechSegmentRow
} from '$lib/server/mappers';
import type { SpeechBoardItem, SpeechSegment } from '$lib/types';

// 발언류 게시판 메타(제목 인덱스): speeches 테이블.
const BOARD_SELECT = `
	SELECT s.id, s.kind, s.title, m.member_code AS member_code, s.member_name,
	       s.committee, s.session_round, s.posted_date, s.view_count, s.source_url
	FROM speeches s
	LEFT JOIN members m ON s.member_id = m.id`;

export function getSpeechBoardByMember(memCode: string): SpeechBoardItem[] {
	return all<SpeechBoardRow>(
		`${BOARD_SELECT} WHERE m.member_code = ? ORDER BY s.posted_date DESC, s.id DESC`,
		memCode
	).map(toSpeechBoard);
}

// CLIK 회의록 실제 발언 원문: speech_segments + minutes 조인.
const SEGMENT_SELECT = `
	SELECT sg.id, m.member_code AS member_code, sg.speaker_name, sg.speaker_role,
	       mn.meeting_type, mn.meeting_date, mn.session_no, mn.round_no,
	       sg.agenda_item, sg.text, mn.clik_docid
	FROM speech_segments sg
	JOIN minutes mn ON sg.minutes_id = mn.id
	LEFT JOIN members m ON sg.member_id = m.id`;

/** 특정 의원의 실제 발언 원문(최신 회의순, 회의 내 순서 유지). */
export function getSegmentsByMember(memCode: string): SpeechSegment[] {
	return all<SpeechSegmentRow>(
		`${SEGMENT_SELECT} WHERE m.member_code = ? ORDER BY mn.meeting_date DESC, sg.seq ASC`,
		memCode
	).map(toSpeechSegment);
}

/** 특정 회의록의 전체 발언(순서대로). */
export function getSegmentsByMinutes(docId: string): SpeechSegment[] {
	return all<SpeechSegmentRow>(
		`${SEGMENT_SELECT} WHERE mn.clik_docid = ? ORDER BY sg.seq ASC`,
		docId
	).map(toSpeechSegment);
}
