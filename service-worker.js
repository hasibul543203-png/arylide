/* ARYLIDE offline-first app shell. Bump CACHE_NAME when shipping a new release. */
const CACHE_NAME = 'arylide-pwa-v5.0.7';
const APP_SHELL = [
  './',
  './index.html',
  './app.css?v=20261012-meetings-1',
  './app.js?v=20261012-meetings-1',
  './i18n.js',
  './firebase.js',
  './config.js',
  './manifest.webmanifest',
  './SOURCES.md',
  './assets/arylide-logo-crop.jpg',
  './assets/app-icon-192.png',
  './assets/app-icon-512.png',
  './assets/app-icon-maskable-512.png',
  './assets/apple-touch-icon.png',
  './assets/favicon-64.png',
  './assets/green-walkway.jpg',
  './assets/jolshiri-hero.jpg',
  './assets/jolshiri-land-wanted.jpg',
  './assets/purbasha-building.jpg',
  './assets/purbasha-campaign.jpg',
  './assets/residence-interior.jpg',
  './assets/sky-high-living-campaign.jpg',
  './assets/sky-high-tower.jpg',
  './assets/uttara-coming-soon.jpg'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(APP_SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys
        .filter(key => key.startsWith('arylide-pwa-') && key !== CACHE_NAME)
        .map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const requestUrl = new URL(request.url);
  if (requestUrl.origin !== self.location.origin) return;

  // Firebase identifiers are public but may be updated by the owner; prefer fresh config online.
  if (requestUrl.pathname === '/config.js') {
    event.respondWith((async () => {
      const cache = await caches.open(CACHE_NAME);
      try {
        const response = await fetch(request, { cache: 'no-store' });
        if (response && response.ok) await cache.put(request, response.clone());
        return response;
      } catch (error) {
        return await cache.match(request) || new Response('', { status: 503, statusText: 'Config unavailable offline' });
      }
    })());
    return;
  }

  // Never cache admin, auth, or lead API responses: they can contain private contact data.
  if (requestUrl.pathname.startsWith('/admin') || requestUrl.pathname.startsWith('/api/')) {
    event.respondWith(fetch(request).catch(() => new Response('This private feature needs the ARYLIDE server to be running.', {
      status: 503,
      headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' }
    })));
    return;
  }

  if (request.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const response = await fetch(request);
        if (response && response.ok) {
          const cache = await caches.open(CACHE_NAME);
          await cache.put(request, response.clone());
        }
        return response;
      } catch (error) {
        const cachedPage = await caches.match(request);
        if (cachedPage) return cachedPage;
        const appHome = new URL('index.html', self.registration.scope).href;
        const cachedHome = await caches.match(appHome);
        if (cachedHome) return cachedHome;
        return new Response('ARYLIDE is offline. Open the app once while connected to finish saving it for offline use.', {
          status: 503,
          headers: { 'Content-Type': 'text/plain; charset=utf-8' }
        });
      }
    })());
    return;
  }

  event.respondWith((async () => {
    const cached = await caches.match(request);
    if (cached) return cached;

    try {
      const response = await fetch(request);
      if (response && response.ok && response.type === 'basic') {
        const cache = await caches.open(CACHE_NAME);
        await cache.put(request, response.clone());
      }
      return response;
    } catch (error) {
      return new Response('', { status: 503, statusText: 'Offline' });
    }
  })());
});
