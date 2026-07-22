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
		const root = document.documentElement;
		// 테마 전환 순간 모든 transition 을 잠시 끈다 → 요소별 색 전환 속도차로 인한 깜박임 방지.
		root.classList.add('theme-switching');
		root.classList.toggle('dark', t === 'dark');
		// 강제 리플로우 후 다음 프레임에 transition 복원.
		void root.offsetHeight;
		requestAnimationFrame(() => root.classList.remove('theme-switching'));
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
