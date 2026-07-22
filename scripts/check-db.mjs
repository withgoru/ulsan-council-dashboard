// prebuild 가드: 빌드가 읽을 SQLite(DATABASE_PATH)가 존재하고 읽을 수 있는지 확인한다.
// 정적 사이트는 빌드 시점에 DB를 읽어 프리렌더되므로, DB가 없으면 조용히 빈 사이트가
// 나오는 대신 여기서 명확히 실패시켜 원인을 빨리 드러낸다.
import { accessSync, constants, statSync } from 'node:fs';
import { resolve } from 'node:path';
import process from 'node:process';

const dbPath = resolve(process.env.DATABASE_PATH ?? './data/council.sqlite3');

try {
	accessSync(dbPath, constants.R_OK);
	const { size } = statSync(dbPath);
	if (size === 0) throw new Error('파일 크기가 0입니다');
	console.log(`✓ DB 확인: ${dbPath} (${(size / 1024).toFixed(0)} KB)`);
} catch (err) {
	console.error(
		`\n✗ 빌드 중단: SQLite DB를 읽을 수 없습니다.\n  경로: ${dbPath}\n  사유: ${err.message}`
	);
	console.error(
		'\n  스크래퍼를 먼저 실행해 DB를 생성하세요:\n' +
			'    cd scraper && uv run python run.py\n' +
			'  또는 DATABASE_PATH 환경변수로 올바른 경로를 지정하세요.\n'
	);
	process.exit(1);
}
