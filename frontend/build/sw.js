// Service Worker for PWA functionality with aggressive cache clearing
const CACHE_NAME = 'ai-chef-v50-force-production-url-fix-2024';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json'
];

// Install event - clear all old caches immediately
self.addEventListener('install', (event) => {
  console.log('Installing new service worker v50 - FORCE PRODUCTION URL FIX...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      console.log('Found existing caches:', cacheNames);
      return Promise.all(
        cacheNames.map(cacheName => {
          console.log('FORCE DELETING cache:', cacheName);
          return caches.delete(cacheName);
        })
      );
    }).then(() => {
      console.log('ALL CACHES FORCE DELETED, creating new cache...');
      return caches.open(CACHE_NAME);
    }).then(cache => {
      console.log('New cache v50 created successfully');
      // Don't cache anything initially - force fresh fetch
      return Promise.resolve();
    })
  );
  // Force the new service worker to become active immediately
  self.skipWaiting();
});

// Activate event - take control immediately
self.addEventListener('activate', (event) => {
  console.log('Activating streamlined options service worker...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Streamlined options service worker activated');
      return self.clients.claim();
    })
  );
});

// Fetch event - NEVER cache, always fetch fresh from network
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // FORCE FRESH FETCH for ALL resources to bypass any caching issues
  event.respondWith(
    fetch(event.request.clone(), {
      cache: 'no-store',
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    }).catch((error) => {
      console.error('Fetch failed:', error);
      // Only fallback to cache if absolutely necessary
      return caches.match(event.request);
    })
  );
});

// Background sync for offline functionality
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(syncData());
  }
});

async function syncData() {
  // Handle background sync when user comes back online
  console.log('Background sync triggered');
}

// Push notifications (for future use)
self.addEventListener('push', (event) => {
  const options = {
    body: 'New recipe suggestion available!',
    icon: '/icon-192x192.png',
    badge: '/icon-192x192.png'
  };

  event.waitUntil(
    self.registration.showNotification('AI Chef', options)
  );
});