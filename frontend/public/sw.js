// Service Worker for PWA functionality - PERSISTENT AUTH FIX
const CACHE_NAME = 'buildyoursmartcart-v109-persistent-auth-fix';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json'
];

// Install event - DEPLOYED URL FIX
self.addEventListener('install', (event) => {
  console.log('🔄 DEPLOYED URL FIX - CLEARING ALL CACHES...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      console.log('🗑️ DELETING OLD CACHES FOR NEW DEPLOYED URL:', cacheNames);
      return Promise.all(
        cacheNames.map(cacheName => {
          console.log('💥 DELETING CACHE:', cacheName);
          return caches.delete(cacheName);
        })
      );
    }).then(() => {
      console.log('✅ CACHES DELETED - CREATING DEPLOYED URL CACHE');
      return caches.open(CACHE_NAME);
    }).then(() => {
      console.log('🎉 DEPLOYED URL CACHE v108 CREATED');
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