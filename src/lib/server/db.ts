// better-sqlite3 읽기 전용 연결. src/lib/server/ 아래라 클라이언트 번들에서 자동 제외되며,
// adapter-static 특성상 빌드(프리렌더) 시점에만 실행된다. 런타임 DB 접속은 없다.
import Database from 'better-sqlite3';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import process from 'node:process';

let _db: Database.Database | null = null;

/** 프로세스 내 단일 연결을 지연 생성해 재사용. */
export function getDb(): Database.Database {
	if (_db) return _db;
	const dbPath = resolve(process.env.DATABASE_PATH ?? './data/council.sqlite3');
	if (!existsSync(dbPath)) {
		throw new Error(
			`SQLite DB를 찾을 수 없습니다: ${dbPath}\n` +
				`스크래퍼를 먼저 실행하세요: cd scraper && uv run python run.py`
		);
	}
	_db = new Database(dbPath, { readonly: true, fileMustExist: true });
	_db.pragma('journal_mode = WAL');
	return _db;
}

/** 파라미터 바인딩 후 전체 행 반환. */
export function all<T = unknown>(sql: string, ...params: unknown[]): T[] {
	return getDb()
		.prepare(sql)
		.all(...params) as T[];
}

/** 파라미터 바인딩 후 단일 행(없으면 undefined). */
export function get<T = unknown>(sql: string, ...params: unknown[]): T | undefined {
	return getDb()
		.prepare(sql)
		.get(...params) as T | undefined;
}
