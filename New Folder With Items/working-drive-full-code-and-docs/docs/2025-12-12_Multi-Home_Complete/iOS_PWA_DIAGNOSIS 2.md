# iOS PWA Service Worker Diagnosis

## Issue Summary
**Problem**: White screen when offline, "server stopped responding" when WiFi reconnects
**Date**: January 2, 2026
**Testing Platform**: iOS 18.7, iPhone, Safari

## Symptoms
1. ❌ White screen when opening PWA with WiFi off
2. ❌ "Server stopped responding" when WiFi turned back on
3. ✅ Service worker registers successfully (checkPWAStatus confirms)
4. ✅ PWA installs to home screen
5. ✅ App works perfectly when online

## Root Cause Analysis

### Service Worker Limitations on iOS
Despite iOS 11.3+ supporting service workers in standalone PWA mode, there are **critical limitations over HTTP**:

1. **iOS Safari HTTP Restriction**:
   - Service workers over HTTP only work reliably in **localhost** environment
   - On network IPs (192.168.x.x), iOS may block service worker activation
   - Even in standalone mode, HTTPS is strongly preferred

2. **Broken Pipe Errors**:
   - Server logs show multiple "Broken pipe from 192.168.1.112"
   - iOS aggressively closes connections in standalone mode
   - Service worker fetch events may timeout before server responds

3. **Cache API Reliability**:
   - iOS Cache API works but has quota limitations
   - May clear caches aggressively when low on storage
   - Not guaranteed to persist across app restarts

## Testing Results

### What We Tried (v1.0 → v1.4)
- ✅ v1.1: iOS-specific caching with offline page
- ✅ v1.2: Navigation handler for HTML pages
- ✅ v1.3: clients.claim(), enhanced fallback, 5-second timeout
- ✅ v1.4: Embedded offline HTML, simplified logic, 3-second timeout
- ❌ **Result**: All versions show white screen when offline

### Server Logs Analysis
```
[02/Jan/2026 22:03:14,872] - Broken pipe from ('192.168.1.112', 56144)
[02/Jan/2026 22:03:14,873] - Broken pipe from ('192.168.1.112', 56147)
```
- iOS device (192.168.1.112) making requests
- Connections closed by iOS before completion
- Indicates network instability in standalone mode

## Solutions

### 🚀 Immediate Solution: HTTPS Deployment
**Recommendation**: Deploy to HTTPS staging server

#### Why HTTPS?
- iOS service workers fully supported over HTTPS
- No connection stability issues
- Cache API fully reliable
- Production-ready configuration

#### Implementation:
1. Deploy to GitHub Pages / Netlify / Vercel (free HTTPS)
2. Or use ngrok for instant HTTPS tunnel:
   ```bash
   brew install ngrok
   ngrok http 8000
   # Get HTTPS URL like https://abc123.ngrok.io
   ```
3. Update ALLOWED_HOSTS with HTTPS domain
4. Test PWA installation on iOS using HTTPS URL

### 🔄 Alternative: LocalStorage Fallback (No Service Worker)
**For HTTP-only environments**

Instead of relying on service workers, use:
1. **LocalStorage** to cache critical data
2. **Application Cache** (deprecated but still works on iOS)
3. **IndexedDB** for larger datasets

#### Trade-offs:
- ✅ Works over HTTP
- ✅ No service worker complexity
- ❌ Can't cache HTML pages (only data)
- ❌ Limited offline functionality
- ❌ Doesn't work for full navigation

### 📱 Recommended Path Forward

#### Option A: HTTPS + Full PWA (Best)
1. Deploy to HTTPS (ngrok for testing, proper hosting for production)
2. Keep service worker v1.4
3. Test offline functionality on iOS
4. **Estimated time**: 30 minutes with ngrok

#### Option B: Progressive Enhancement (Pragmatic)
1. Accept HTTP limitations
2. Focus on "online-first" PWA benefits:
   - Home screen icon ✅
   - Standalone mode (no browser UI) ✅
   - Faster loading (browser caching) ✅
   - Install analytics ✅
3. Document offline as "requires HTTPS for production"
4. **Estimated time**: 0 (done)

#### Option C: Hybrid Approach (Balanced)
1. Use HTTPS for production
2. Use HTTP for development (accept no offline)
3. Add localStorage caching for critical user data
4. **Estimated time**: 1 hour

## Technical Details

### Why White Screen Instead of Offline Page?
1. Service worker registers but **doesn't activate** over HTTP on network IP
2. iOS falls back to standard browser behavior
3. No network = no response = white screen
4. Service worker fetch events never fire

### Why "Server Stopped Responding" After WiFi Reconnect?
1. iOS standalone mode doesn't have refresh button
2. Previous request timed out (3-second abort)
3. Reconnecting WiFi doesn't retry automatically
4. User must close and reopen app to trigger new request

### Service Worker Registration vs Activation
```javascript
// Registration: ✅ Works over HTTP
navigator.serviceWorker.register('/sw.js')

// Activation: ❌ Blocked by iOS over HTTP on network IP
// Fetch events never fire, no offline interception
```

## Recommendation

**For Task #2 completion, choose Option A (HTTPS)**:

### Using ngrok (5-minute setup):
```bash
# Terminal 1: Start Django
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
python3 manage.py runserver 8000

# Terminal 2: Create HTTPS tunnel
ngrok http 8000
# Copy HTTPS URL from ngrok output
```

### Update settings.py:
```python
ALLOWED_HOSTS = ['*.ngrok.io', 'localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = ['https://*.ngrok.io']
```

### Test on iOS:
1. Visit ngrok HTTPS URL in Safari
2. Add to Home Screen
3. Test offline mode
4. **Expected**: Purple offline page or cached dashboard ✅

## References
- [iOS PWA Support](https://caniuse.com/serviceworkers) - Shows iOS limitations
- [Apple Safari Release Notes](https://developer.apple.com/safari/release-notes/) - Service worker changes per version
- [MDN Service Worker Security](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API/Using_Service_Workers#security) - HTTPS requirement

## Decision Point

**Choose one**:
1. ⏩ **Try ngrok HTTPS** (5 min) - Likely to fix white screen issue
2. 📝 **Document limitation** (0 min) - Accept online-only for HTTP development
3. 🔧 **Implement localStorage fallback** (1 hour) - Limited offline without service workers

**Recommendation**: Try Option 1 (ngrok) first. If white screen persists even over HTTPS, then iOS may have other restrictions and we should document as known limitation.
