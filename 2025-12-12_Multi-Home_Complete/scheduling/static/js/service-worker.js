/**
 * Service Worker for Staff Rota Management System
 * Provides offline functionality, caching, and background sync
 * Version: 1.7.0
 */

const CACHE_VERSION = 'staff-rota-v1.7';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`;

// Static assets to cache on install (only essential assets that are guaranteed to exist)
const STATIC_ASSETS = [
    '/static/css/design-system.css',
    '/static/css/modern-theme.css',
    '/static/js/chart-config.js',
    '/static/manifest.json'
];

// URLs that should always fetch from network (no caching)
const NETWORK_ONLY = [
    '/admin/',
    '/api/live-updates/',
    '/api/notifications/',
    '/login/',
    '/logout/',
    '/search/',
    '/search/advanced/',
    '/staff-search-rota/',
    '/overtime/'
];

// URLs that need network-first strategy (API endpoints)
const NETWORK_FIRST = [
    '/api/',
    '/rota/api/',
    '/leave/api/',
    '/staff/api/',
    '/rota-view/'
];

/**
 * Install Event - Cache static assets
 */
self.addEventListener('install', (event) => {
    console.log('[Service Worker] Installing...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('[Service Worker] Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('[Service Worker] Installation complete');
                return self.skipWaiting(); // Activate immediately
            })
            .catch((error) => {
                console.error('[Service Worker] Installation failed:', error);
            })
    );
});

/**
 * Activate Event - Clean up old caches
 */
self.addEventListener('activate', (event) => {
    console.log('[Service Worker] Activating...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames
                        .filter((cacheName) => {
                            // Delete old cache versions
                            return cacheName.startsWith('staff-rota-') && 
                                   cacheName !== STATIC_CACHE && 
                                   cacheName !== DYNAMIC_CACHE;
                        })
                        .map((cacheName) => {
                            console.log('[Service Worker] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        })
                );
            })
            .then(() => {
                console.log('[Service Worker] Activation complete');
                return self.clients.claim(); // Take control immediately
            })
    );
});

/**
 * Fetch Event - Intercept network requests
 */
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip cross-origin requests except for CDN assets
    if (url.origin !== location.origin && !isCDNAsset(url.href)) {
        return;
    }
    
    // Network-only URLs (admin, live updates)
    if (isNetworkOnly(url.pathname)) {
        event.respondWith(networkOnly(request));
        return;
    }
    
    // Network-first strategy for API calls
    if (isNetworkFirst(url.pathname)) {
        event.respondWith(networkFirst(request));
        return;
    }
    
    // Cache-first strategy for static assets
    event.respondWith(cacheFirst(request));
});

/**
 * Cache-First Strategy
 * Try cache first, fall back to network, cache the response
 */
async function cacheFirst(request) {
    try {
        // Try cache first
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            console.log('[Service Worker] Serving from cache:', request.url);
            return cachedResponse;
        }
        
        // If not in cache, fetch from network
        console.log('[Service Worker] Fetching from network:', request.url);
        const networkResponse = await fetch(request);
        
        // Cache the response for future use (only successful responses)
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
        
    } catch (error) {
        console.error('[Service Worker] Cache-first failed:', error);
        
        // Return a custom offline response
        return new Response('Offline - Content not available', {
            status: 503,
            statusText: 'Service Unavailable',
            headers: new Headers({
                'Content-Type': 'text/plain'
            })
        });
    }
}

/**
 * Network-First Strategy
 * Try network first, fall back to cache if offline
 */
async function networkFirst(request) {
    try {
        // Try network first
        console.log('[Service Worker] Network-first fetch:', request.url);
        const networkResponse = await fetch(request);
        
        // Cache successful API responses (for offline fallback)
        if (networkResponse.ok && request.method === 'GET') {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
        
    } catch (error) {
        console.warn('[Service Worker] Network failed, trying cache:', request.url);
        
        // If network fails, try cache
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            console.log('[Service Worker] Serving stale data from cache');
            return cachedResponse;
        }
        
        // Both network and cache failed
        return new Response(JSON.stringify({
            error: 'Offline',
            message: 'Unable to fetch data. Please check your connection.'
        }), {
            status: 503,
            statusText: 'Service Unavailable',
            headers: new Headers({
                'Content-Type': 'application/json'
            })
        });
    }
}

/**
 * Network-Only Strategy
 * Always fetch from network, never cache
 */
async function networkOnly(request) {
    try {
        return await fetch(request);
    } catch (error) {
        // Only log errors for non-common failures
        const url = request.url || '';
        if (!url.includes('well-known') && !url.includes('screenshot')) {
            console.warn('[Service Worker] Network request failed:', url, error.message);
        }
        return new Response('Network request failed', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}

/**
 * Background Sync - Queue failed requests for retry
 */
self.addEventListener('sync', (event) => {
    console.log('[Service Worker] Background sync triggered:', event.tag);
    
    if (event.tag === 'sync-leave-requests') {
        event.waitUntil(syncLeaveRequests());
    }
    
    if (event.tag === 'sync-shift-swaps') {
        event.waitUntil(syncShiftSwaps());
    }
});

/**
 * Sync queued leave requests
 */
async function syncLeaveRequests() {
    try {
        const cache = await caches.open(DYNAMIC_CACHE);
        const requests = await cache.keys();
        
        // Find pending leave requests
        const pendingRequests = requests.filter(req => 
            req.url.includes('/leave/request/') && req.method === 'POST'
        );
        
        // Retry each request
        for (const request of pendingRequests) {
            try {
                await fetch(request.clone());
                await cache.delete(request);
                console.log('[Service Worker] Synced leave request:', request.url);
            } catch (error) {
                console.error('[Service Worker] Failed to sync leave request:', error);
            }
        }
        
    } catch (error) {
        console.error('[Service Worker] Background sync failed:', error);
        throw error; // Retry sync later
    }
}

/**
 * Sync queued shift swaps
 */
async function syncShiftSwaps() {
    try {
        const cache = await caches.open(DYNAMIC_CACHE);
        const requests = await cache.keys();
        
        const pendingSwaps = requests.filter(req => 
            req.url.includes('/shift/swap/') && req.method === 'POST'
        );
        
        for (const request of pendingSwaps) {
            try {
                await fetch(request.clone());
                await cache.delete(request);
                console.log('[Service Worker] Synced shift swap:', request.url);
            } catch (error) {
                console.error('[Service Worker] Failed to sync shift swap:', error);
            }
        }
        
    } catch (error) {
        console.error('[Service Worker] Shift swap sync failed:', error);
        throw error;
    }
}

/**
 * Push Notifications
 */
self.addEventListener('push', (event) => {
    console.log('[Service Worker] Push notification received');
    
    const data = event.data ? event.data.json() : {};
    const title = data.title || 'Staff Rota Update';
    const options = {
        body: data.body || 'You have a new notification',
        icon: '/static/images/icon-192x192.png',
        badge: '/static/images/icon-96x96.png',
        data: data.url || '/',
        vibrate: [200, 100, 200],
        tag: data.tag || 'default',
        requireInteraction: data.requireInteraction || false
    };
    
    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

/**
 * Notification Click Handler
 */
self.addEventListener('notificationclick', (event) => {
    console.log('[Service Worker] Notification clicked:', event.notification.tag);
    
    event.notification.close();
    
    const urlToOpen = event.notification.data || '/';
    
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then((clientList) => {
                // Check if app is already open
                for (const client of clientList) {
                    if (client.url === urlToOpen && 'focus' in client) {
                        return client.focus();
                    }
                }
                // If not open, open new window
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});

/**
 * Message Handler - Communicate with main app
 */
self.addEventListener('message', (event) => {
    console.log('[Service Worker] Message received:', event.data);
    
    if (event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data.type === 'CLEAR_CACHE') {
        event.waitUntil(
            caches.keys().then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => caches.delete(cacheName))
                );
            })
        );
    }
    
    if (event.data.type === 'GET_VERSION') {
        event.ports[0].postMessage({ version: CACHE_VERSION });
    }
});

/**
 * Helper Functions
 */

function isNetworkOnly(pathname) {
    return NETWORK_ONLY.some(pattern => pathname.startsWith(pattern));
}

function isNetworkFirst(pathname) {
    return NETWORK_FIRST.some(pattern => pathname.startsWith(pattern));
}

function isCDNAsset(url) {
    return url.includes('googleapis.com') ||
           url.includes('jsdelivr.net') ||
           url.includes('cdnjs.cloudflare.com') ||
           url.includes('bootstrapcdn.com');
}

console.log('[Service Worker] Script loaded, version:', CACHE_VERSION);
