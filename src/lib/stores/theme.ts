import { browser } from '$app/environment';
import { writable } from 'svelte/store';

export type Theme = 'light' | 'dark';

// app.html 의 인라인 스크립트가 이미 .dark 클래스를 세팅했으므로, 초기값은 DOM 에서 읽는다.
function createTheme() {
	const initial: Theme =
		browser && document.documentElement.classList.contains('dark') ? 'dark' : 'light';
	const { subscribe, set } = writable<Theme>(initial);

	function apply(t: Theme) {
		if (!browser) return;
		document.documentElement.classList.toggle('dark', t === 'dark');
		try {
			localStorage.setItem('theme', t);
		} catch {
			/* localStorage 불가(사생활 모드 등) 시 무시 */
		}
		set(t);
	}

	let current: Theme = initial;
	subscribe((t) => (current = t));

	return {
		subscribe,
		set: apply,
		toggle: () => apply(current === 'dark' ? 'light' : 'dark')
	};
}

export const theme = createTheme();
