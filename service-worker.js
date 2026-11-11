/* ARYLIDE offline-first app shell. Bump CACHE_NAME when shipping a new release. */
const CACHE_NAME = 'arylide-pwa-v6.0.0';
const APP_SHELL = [
  './',
  './index.html',
  './admin.html',
  './app.css?v=20261012-meetings-1',
  './app.js?v=20261012-meetings-1',
  './admin-cloud.js?v=20261104-1',
  './i18n.js',
  './firebase.js',
  './config.js',
  './cms-seed.js',
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
      .then(async cache => {
        const results = await Promise.allSettled(
          APP_SHELL.map(url => cache.add(url).catch(err => console.warn('[SW] Could not cache:', url, err)))
        );
        return results;
      })
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.map(key => {
        if (key !== CACHE_NAME) {
          return caches.delete(key);
        }
      })
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const requestUrl = new URL(request.url);

  // Firestore / Google APIs / Firebase Auth traffic: always network
  if (requestUrl.hostname.includes('firebase') ||
      requestUrl.hostname.includes('googleapis.com') ||
      requestUrl.hostname.includes('gstatic.com') ||
      requestUrl.hostname.includes('identitytoolkit')) {
    return;
  }

  // Admin routes: serve network-first with graceful offline fallback (never show server-required error)
  if (requestUrl.pathname.startsWith('/admin')) {
    event.respondWith(
      fetch(request).catch(() => caches.match('/admin.html').then(res => res || caches.match('./admin.html')))
    );
    return;
  }

  // API endpoints: network with JSON fallback
  if (requestUrl.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request).catch(() => new Response(JSON.stringify({ ok: false, error: 'Offline' }), {
        status: 503,
        headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' }
      }))
    );
    return;
  }

  // Static assets & navigation: stale-while-revalidate or cache-first
  event.respondWith(
    caches.match(request).then(cachedResponse => {
      const fetchPromise = fetch(request).then(networkResponse => {
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(request, responseToCache);
          });
        }
        return networkResponse;
      }).catch(() => {
        if (request.mode === 'navigate') {
          return caches.match('./index.html') || caches.match('/index.html');
        }
      });
      return cachedResponse || fetchPromise;
    })
  );
});
