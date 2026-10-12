// 휴대폰 가계부를 오프라인에서도 열 수 있도록 핵심 파일을 보관하는 서비스 워커
// v1은 사이트 전체 페이지를 캐시 우선으로 붙잡아 홈 등이 갱신되지 않았다. v2는 가계부 파일만, 네트워크 우선으로 다룬다.
const CACHE_NAME = 'daily-ledger-v2';
const APP_FILES = ['/daily-ledger.html', '/daily-ledger.webmanifest'];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(APP_FILES)));
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key)))));
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin || !APP_FILES.includes(url.pathname)) return;
  event.respondWith(fetch(event.request).then(response => {
    const copy = response.clone();
    caches.open(CACHE_NAME).then(cache => cache.put(event.request, copy));
    return response;
  }).catch(() => caches.match(event.request)));
});
