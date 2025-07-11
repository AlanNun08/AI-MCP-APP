// Service Worker for PWA functionality - AUTH PERSISTENCE VERSION
const CACHE_NAME = 'buildyoursmartcart-v106-auth-persistence';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json'
];

// Install event - NEW URL CACHE CLEAR
self.addEventListener('install', (event) => {
  console.log('🔄 NEW PREVIEW URL - CLEARING ALL CACHES...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      console.log('🗑️ DELETING ALL OLD CACHES FOR NEW URL:', cacheNames);
      return Promise.all(
        cacheNames.map(cacheName => {
          console.log('💥 DELETING CACHE:', cacheName);
          return caches.delete(cacheName);
        })
      );
    }).then(() => {
      console.log('✅ ALL CACHES DELETED - CREATING NEW URL CACHE');
      return caches.open(CACHE_NAME);
    }).then(() => {
      console.log('🎉 NEW URL CACHE v105 CREATED');
      return self.skipWaiting();
    })
  );
});

// Activate event - IMMEDIATE CONTROL
self.addEventListener('activate', (event) => {
  console.log('🚀 CLEAN SERVICE WORKER ACTIVATING');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(cacheName => {
          return cacheName !== CACHE_NAME;
        }).map(cacheName => {
          console.log('🗑️ FINAL CLEANUP:', cacheName);
          return caches.delete(cacheName);
        })
      );
    }).then(() => {
      console.log('✅ COMPLETE CLEANUP DONE');
      return self.clients.claim();
    })
  );
});

// Fetch event - CLEAN HANDLING
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      })
  );
});

// Push notification event
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'New notification',
    icon: '/icon-192x192.png',
    badge: '/badge-72x72.png'
  };

  event.waitUntil(
    self.registration.showNotification('AI Chef', options)
  );
});