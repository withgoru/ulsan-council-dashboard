import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/** Tailwind 클래스 병합 헬퍼(shadcn-svelte 표준). */
export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}

// shadcn-svelte 컴포넌트들이 참조하는 타입 헬퍼.
export type WithElementRef<T, U extends HTMLElement = HTMLElement> = T & { ref?: U | null };
export type WithoutChild<T> = T extends { child?: unknown } ? Omit<T, 'child'> : T;
export type WithoutChildren<T> = T extends { children?: unknown } ? Omit<T, 'children'> : T;
export type WithoutChildrenOrChild<T> = WithoutChildren<WithoutChild<T>>;
