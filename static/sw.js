// ✅ Service Worker لتطبيق Socialite
const CACHE_NAME = 'socialite-v1';
const urlsToCache = [
  '/',
  '/static/style.css',
  '/static/script.js'
];

// ✅ تثبيت الـ Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('✅ تم فتح الكاش');
        return cache.addAll(urlsToCache);
      })
      .catch(err => console.error('❌ خطأ في التثبيت:', err))
  );
});

// ✅ تفعيل الـ Service Worker
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('🗑️ حذف الكاش القديم:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// ✅ معالجة طلبات الشبكة (Offline First)
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // ✅ إذا وجد في الكاش، ارجعه
        if (response) {
          return response;
        }
        // ✅ وإلا، اطلبه من الشبكة
        return fetch(event.request)
          .then(response => {
            // ✅ خزنه في الكاش للمرة القادمة
            if (response && response.status === 200) {
              const responseClone = response.clone();
              caches.open(CACHE_NAME)
                .then(cache => {
                  cache.put(event.request, responseClone);
                });
            }
            return response;
          })
          .catch(() => {
            // ✅ صفحة offline
            return new Response('❌ غير متصل بالإنترنت', {
              status: 503,
              statusText: 'Service Unavailable'
            });
          });
      })
  );
});

console.log('✅ Service Worker جاهز');
