import tailwindcss from '@tailwindcss/vite';
import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import Icons from 'unplugin-icons/vite';

export default defineConfig({
	plugins: [
		tailwindcss(),
		// iconoir 아이콘을 개별 Svelte 컴포넌트로 import (예: `~icons/iconoir/menu`).
		// currentColor 를 상속하므로 색은 부모 텍스트 색을 따른다(PLAN 4절).
		Icons({ compiler: 'svelte' }),
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
