self.addEventListener('install', (e) => { console.log('[SeverOS] Service Worker: Installed'); });
self.addEventListener('fetch', (e) => { e.respondWith(fetch(e.request)); });