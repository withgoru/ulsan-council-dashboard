import tailwindcss from '@tailwindcss/vite';
import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, type PluginOption } from 'vite';
import Icons from 'unplugin-icons/vite';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const CURATION_PATH = resolve('src/lib/data/media-curation.json');
const DB_PATH = resolve(process.env.DATABASE_PATH ?? 'data/council.sqlite3');

// 개발 전용 큐레이션 API. `vite dev` 에서만 동작(configureServer)하고 정적 빌드엔 포함되지 않는다.
//  GET  /__curation/candidates → media_articles 후보 + 현재 큐레이션({items, issues})
//  POST /__curation/save       → src/lib/data/media-curation.json 저장(커밋 대상)
function curationApi(): PluginOption {
	return {
		name: 'media-curation-dev-api',
		apply: 'serve',
		configureServer(server) {
			server.middlewares.use('/__curation/candidates', async (_req, res) => {
				try {
					const { default: Database } = await import('better-sqlite3');
					const dbc = new Database(DB_PATH, { readonly: true, fileMustExist: true });
					const candidates = dbc
						.prepare(
							`SELECT url, title, description, press AS source, published_at AS publishedAt
							 FROM media_articles ORDER BY published_at DESC, id DESC`
						)
						.all();
					dbc.close();
					const curation = JSON.parse(readFileSync(CURATION_PATH, 'utf-8'));
					res.setHeader('Content-Type', 'application/json');
					res.end(JSON.stringify({ candidates, curation }));
				} catch (err) {
					res.statusCode = 500;
					res.end(JSON.stringify({ error: String(err) }));
				}
			});

			server.middlewares.use('/__curation/save', (req, res) => {
				if (req.method !== 'POST') {
					res.statusCode = 405;
					res.end();
					return;
				}
				let body = '';
				req.on('data', (c) => (body += c));
				req.on('end', () => {
					try {
						const parsed = JSON.parse(body);
						const items = Array.isArray(parsed.items) ? parsed.items : [];
						const issues = Array.isArray(parsed.issues) ? parsed.issues : [];
						writeFileSync(CURATION_PATH, JSON.stringify({ items, issues }, null, '\t') + '\n');
						res.setHeader('Content-Type', 'application/json');
						res.end(JSON.stringify({ ok: true, items: items.length, issues: issues.length }));
					} catch (err) {
						res.statusCode = 400;
						res.end(JSON.stringify({ error: String(err) }));
					}
				});
			});
		}
	};
}

export default defineConfig({
	plugins: [
		tailwindcss(),
		// iconoir 아이콘을 개별 Svelte 컴포넌트로 import (예: `~icons/iconoir/menu`).
		// currentColor 를 상속하므로 색은 부모 텍스트 색을 따른다(PLAN 4절).
		Icons({ compiler: 'svelte' }),
		curationApi(),
		sveltekit({
			compilerOptions: {
				// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			adapter: adapter()
		})
	]
});
