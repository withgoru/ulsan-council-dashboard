<script lang="ts">
	import { SITE, canonicalUrl } from '$lib/config/site';

	// 라우트별 <svelte:head> 공통화: 제목/설명/canonical/OG/Twitter 카드.
	let {
		title,
		description = SITE.description,
		path = '/',
		type = 'website',
		image = SITE.ogImage
	}: {
		title?: string;
		description?: string;
		path?: string;
		type?: 'website' | 'article' | 'profile';
		image?: string;
	} = $props();

	// 하위 페이지는 "제목 · 사이트명", 홈은 사이트명 단독.
	const fullTitle = $derived(title ? `${title} · ${SITE.shortName}` : SITE.name);
	const canonical = $derived(canonicalUrl(path));
	const imageUrl = $derived(image.startsWith('http') ? image : `${SITE.url}${image}`);
</script>

<svelte:head>
	<title>{fullTitle}</title>
	<meta name="description" content={description} />
	<link rel="canonical" href={canonical} />

	<meta property="og:type" content={type} />
	<meta property="og:site_name" content={SITE.name} />
	<meta property="og:locale" content={SITE.locale} />
	<meta property="og:title" content={fullTitle} />
	<meta property="og:description" content={description} />
	<meta property="og:url" content={canonical} />
	<meta property="og:image" content={imageUrl} />

	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content={fullTitle} />
	<meta name="twitter:description" content={description} />
	<meta name="twitter:image" content={imageUrl} />
</svelte:head>
