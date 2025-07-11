// Service Worker for PWA functionality - PRODUCTION DEPLOYMENT READY
const CACHE_NAME = 'buildyoursmartcart-v101-production-deployment-ready';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json'
];

// Install event - FORCE DELETE ALL OLD CACHES
self.addEventListener('install', (event) => {
  console.log('🚀 PRODUCTION DEPLOYMENT - CLEARING ALL CACHES...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      console.log('🗑️ CLEARING ALL OLD CACHES:', cacheNames);
      return Promise.all(
        cacheNames.map(cacheName => {
          console.log('💥 DELETING CACHE:', cacheName);
          return caches.delete(cacheName);
        })
      );
    }).then(() => {
      console.log('✅ ALL OLD CACHES DELETED - CREATING NEW CACHE');
      return caches.open(CACHE_NAME);
    }).then(() => {
      console.log('🎉 NEW CACHE v101 CREATED FOR PRODUCTION');
      return self.skipWaiting();
    })
  );
});

// Activate event - TAKE CONTROL IMMEDIATELY
self.addEventListener('activate', (event) => {
  console.log('🚀 PRODUCTION SERVICE WORKER ACTIVATING - TAKING CONTROL');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(cacheName => {
          return cacheName !== CACHE_NAME;
        }).map(cacheName => {
          console.log('🗑️ DELETING OLD CACHE:', cacheName);
          return caches.delete(cacheName);
        })
      );
    }).then(() => {
      console.log('✅ ALL OLD CACHES DELETED - TAKING CONTROL');
      return self.clients.claim();
    })
  );
});

// Fetch event - Normal caching behavior (no forced reloads)
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // Always fetch fresh for HTML, JS, and CSS files
  if (url.pathname.endsWith('.html') || 
      url.pathname.endsWith('.js') || 
      url.pathname.endsWith('.css') ||
      url.pathname === '/') {
    event.respondWith(
      fetch(event.request.clone(), {
        cache: 'no-store'
      }).catch(() => {
        // Fallback to cache only if network fails
        return caches.match(event.request);
      })
    );
    return;
  }
  
  // For other resources, use normal caching
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        return response || fetch(event.request);
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