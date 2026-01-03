/**
 * Service Worker for Staff Rota Management System
 * Provides offline functionality, caching, and background sync
 * Version: 1.4.0 - Simplified Offline Fix
 */

const CACHE_VERSION = 'staff-rota-v1.4';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`;
const OFFLINE_PAGE = '/offline/';
const OFFLINE_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Offline - Staff Rota</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 20px;
        }
        .container { max-width: 400px; }
        h1 { font-size: 4em; margin-bottom: 0.2em; }
        h2 { font-size: 1.8em; margin-bottom: 0.5em; }
        p { font-size: 1.1em; opacity: 0.9; line-height: 1.6; margin-bottom: 1em; }
        button {
            background: white;
            color: #667eea;
            border: none;
            padding: 12px 24px;
            font-size: 1em;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 20px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📡</h1>
        <h2>You're Offline</h2>
        <p>This page isn't available without an internet connection.</p>
        <p>Please connect to WiFi and try again.</p>
        <button onclick="location.reload()">Try Again</button>
    </div>
</body>
</html>`;

// Static assets to cache on install (iOS-optimized)
const STATIC_ASSETS = [
    '/',
    '/offline/',  // Critical: Cache offline page
    '/static/css/design-system.css',
    '/static/css/modern-theme.css',
    '/static/css/mobile-responsive.min.css',
    '/static/css/ui-polish.min.css',
    '/static/css/wcag-color-compliance.css',
    '/static/css/responsive-tables.css',
    '/static/js/chart-config.js',
    '/static/js/skeleton-loader.js',
    '/static/manifest.json',
    '/static/images/favicon.ico',
    '/static/images/favicon-16x16.png',
    '/static/images/favicon-32x32.png',
    '/static/images/icon-72x72.png',
    '/static/images/icon-96x96.png',
    '/static/images/icon-120x120.png',
    '/static/images/icon-128x128.png',
    '/static/images/icon-144x144.png',
    '/static/images/icon-152x152.png',
    '/static/images/icon-180x180.png',
    '/static/images/icon-192x192.png',
    '/static/images/icon-384x384.png',
    '/static/images/icon-512x512.png'
];

// CDN assets to cache (external resources)
const CDN_ASSETS = [
    'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// URLs that should always fetch from network (no caching)
const NETWORK_ONLY = [
    '/admin/',
    '/api/live-updates/',
    '/api/notifications/'
];

// URLs that need network-first strategy (API endpoints)
const NETWORK_FIRST = [
    '/api/',
    '/rota/api/',
    '/leave/api/',
    '/staff/api/'
];

/**
 * Install Event - Cache static assets (iOS Enhanced)
 */
self.addEventListener('install', (event) => {
    console.log('🔧 [SW] INSTALLING version:', CACHE_VERSION);
    console.log('📋 [SW] Will cache', STATIC_ASSETS.length, 'static assets');
    console.log('🌐 [SW] Will cache', CDN_ASSETS.length, 'CDN assets');
    const installStart = performance.now();
    
    event.waitUntil(
        Promise.all([
            // Cache local static assets
            caches.open(STATIC_CACHE).then((cache) => {
                console.log('📦 [SW] Opening static cache:', STATIC_CACHE);
                return cache.addAll(STATIC_ASSETS)
                    .then(() => {
                        console.log('✅ [SW] Static assets cached successfully!');
                    })
                    .catch((error) => {
                        console.error('❌ [SW] Batch cache failed:', error);
                        console.log('🔄 [SW] Trying individual caching (iOS fallback)...');
                        // Cache assets individually if batch fails (iOS Safari issue)
                        return Promise.all(
                            STATIC_ASSETS.map((url, index) => 
                                cache.add(url)
                                    .then(() => console.log(`  ✅ [${index+1}/${STATIC_ASSETS.length}] Cached:`, url))
                                    .catch(err => console.warn(`  ❌ [${index+1}/${STATIC_ASSETS.length}] Failed:`, url, err))
                            )
                        );
                    });
            }),
            // Cache CDN assets separately for better error handling
            caches.open(STATIC_CACHE).then((cache) => {
                console.log('🌐 [SW] Caching CDN assets...');
                return Promise.all(
                    CDN_ASSETS.map((url, index) => 
                        cache.add(url)
                            .then(() => console.log(`  ✅ CDN [${index+1}/${CDN_ASSETS.length}] Cached:`, url))
                            .catch(err => console.warn(`  ⚠️ CDN [${index+1}/${CDN_ASSETS.length}] Failed:`, url, err))
                    )
                );
            })
        ]).then(() => {
            const installTime = (performance.now() - installStart).toFixed(2);
            console.log(`🎉 [SW] Installation COMPLETE in ${installTime}ms`);
            console.log('⚡ [SW] Activating immediately (skipWaiting)...');
            return self.skipWaiting(); // Activate immediately
        }).catch((error) => {
            console.error('❌ [SW] Installation FAILED:', error);
            console.log('🔄 [SW] Continuing with partial cache...');
            // Continue with partial cache rather than failing completely
            return self.skipWaiting();
        })
    );
});

/**
 * Activate Event - Clean up old caches and take control
 */
self.addEventListener('activate', (event) => {
    console.log('⚡ [SW] ACTIVATING version:', CACHE_VERSION);
    
    event.waitUntil(
        caches.keys()ALL network requests
 */
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    console.log('🌐 [SW] Fetch:', request.mode, url.pathname);
    
    // Skip cross-origin requests except for CDN assets
    if (url.origin !== location.origin && !isCDNAsset(url.href)) {
        console.log('⏭️ [SW] Skipping cross-origin:', url.href);
        return;
    }
    
    // Network-only URLs (admin, live updates)
    if (isNetworkOnly(url.pathname)) {
        console.log('🚫 [SW] Network-only:', url.pathname);
        event.respondWith(networkOnly(request));
        return;
    }
    
    // HTML pages (navigation): Use simplified handler
    if (request.mode === 'navigate' || 
        request.destination === 'document' || 
        request.headers.get('accept')?.includes('text/html')) {
        console.log('📄 [SW] HTML Navigation:', url.pathname);
        event.respondWith(handleNavigation(request));
        return;
    }
    
    // Network-first strategy for API calls
    if (isNetworkFirst(url.pathname)) {
        console.log('🔄 [SW] Network-first (API):', url.pathname);
        event.respondWith(networkFirst(request));
        return;
    }
    
    // Cache-first strategy for static assets
    console.log('💾 [SW] Cache-first:', url.pathname);cacheName);
                    })
                );
            })
            .then(() => {
                console.log('[Service Worker] Activation complete. Claiming clients...');
                return self.clients.claim(); // Take control immediately
            })
            .then(() => {
                console.log('[Service Worker] All clients claimed. Ready to serve.');
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
    
    // HTML pages (navigation): Network-first with aggressive caching
    if (request.mode === 'navigate' || request.destination === 'document' || 
        request.headers.get('accept')?.includes('text/html')) {
        console.log('🔵 [SW] Navigation request:', url.pathname);
        event.respondWith(navigationHandler(request));
        return;
    }
    
    // Network-first strategy for API calls
    if (isNetworkFirst(url.pathname)) {
        event.respondWith(networkFirst(request));
        return;
   Simplified Navigation Handler - Offline First with Fallback
 */
async function handleNavigation(request) {
    const url = new URL(request.url);
    console.log('📱 [SW] Handling navigation:', url.pathname);
    
    try {
        // Try network first with 3 second timeout
        console.log('🌐 [SW] Trying network...');
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        
        const response = await fetch(request, { signal: controller.signal });
        clearTimeout(timeoutId);
        
        if (response.ok) {
            console.log('✅ [SW] Got response from network');
            // Cache for offline use
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, response.clone()).catch(err => 
                console.warn('⚠️ [SW] Cache failed:', err)
            );
            return response;
        }
        
        throw new Error(`HTTP ${response.status}`);
        
    } catch (error) {
        console.warn('⚠️ [SW] Network unavailable:', error.message);
        console.log('🔍 [SW] Checking cache...');
        
        // Try cache
        const cached = await caches.match(request);
        if (cached) {
            console.log('✅ [SW] Serving from cache');
            return cached;
        }
        
        // Return offline HTML
        console.log('📄 [SW] Serving offline page');
        return new Response(OFFLINE_HTML, {
            status: 200ble offline yet.</p>
                    <p>Please reconnect to the internet and try again.</p>
                </div>
            </body>
            </html>
        `, {
            status: 503,
            statusText: 'Service Unavailable',
            headers: new Headers({
                'Content-Type': 'text/html; charset=utf-8'
            })
        });
    }
}

/**
 * Cache-First Strategy (iOS Enhanced)
 * Try cache first, fall back to network, cache the response
 */
async function cacheFirst(request) {
    try {
        // Try cache first
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            console.log('[Service Worker] ✅ Serving from cache:', request.url);
            return cachedResponse;
        }
        
        // If not in cache, fetch from network
        console.log('[Service Worker] 🌐 Fetching from network:', request.url);
        const networkResponse = await fetch(request);
        
        // Cache the response for future use (only successful responses)
        if (networkResponse && networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            // Clone the response before caching (iOS requires this)
            cache.put(request, networkResponse.clone()).catch(err => {
                console.warn('[Service Worker] Failed to cache response:', err);
            });
        }
        
        return networkResponse;
        
    } catch (error) {
        console.error('[Service Worker] ❌ Cache-first failed:', error);
        
        // If both cache and network fail, return offline page for navigation requests
        if (request.mode === 'navigate' || request.destination === 'document') {
            const offlinePage = await caches.match(OFFLINE_PAGE);
            if (offlinePage) {
                console.log('[Service Worker] 📄 Serving offline page');
                return offlinePage;
            }
        }
        
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
        
        // Cache the response for future use (only successful responses)
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
        
    } catch (error) {
        console.error('[Service Worker] Cache-first failed:', error);
        
        // If both cache and network fail, return offline page for navigation requests
        if (request.mode === 'navigate') {
            const offlinePage = await caches.match(OFFLINE_PAGE);
            if (offlinePage) {
                return offlinePage;
            }
        }
        
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
        console.error('[Service Worker] Network-only failed:', error);
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
