/**
 * PWA Testing Guide for Staff Rota Management System
 * Created: January 2, 2026
 * 
 * This guide provides step-by-step instructions for testing the PWA implementation
 * across different platforms and scenarios.
 */

# PWA Testing Guide

## 🎯 Testing Objectives

1. ✅ Verify PWA installation works on iOS, Android, and Desktop
2. ✅ Confirm offline functionality with service worker caching
3. ✅ Test "Add to Home Screen" prompts appear correctly
4. ✅ Validate analytics tracking for install behavior
5. ✅ Ensure smooth app updates and cache management

---

## 📱 Platform-Specific Testing

### **iOS Testing (Safari on iPhone/iPad)**

#### Installation Test:
1. Open Safari on iPhone/iPad
2. Navigate to: `http://your-server-ip:8000` (or production URL)
3. Look for install banner after 5 seconds
4. **Alternative**: Tap Share button (⬆️) → "Add to Home Screen"
5. Confirm app icon appears on home screen
6. Tap icon to launch as PWA

#### Verification:
- ✅ App opens in standalone mode (no Safari UI)
- ✅ Status bar color matches theme (#0066FF)
- ✅ App icons display correctly
- ✅ Splash screen shows on launch

#### Known iOS Limitations:
- ⚠️ Install prompts may not trigger automatically (use manual "Add to Home Screen")
- ⚠️ Service worker caching is limited on iOS < 15
- ⚠️ Background sync not supported on iOS

---

### **Android Testing (Chrome/Edge)**

#### Installation Test:
1. Open Chrome on Android device
2. Navigate to: `http://your-server-ip:8000`
3. Wait 5 seconds for install banner to appear
4. Tap "Install" button on custom banner
5. **Alternative**: Tap ⋮ menu → "Add to Home screen" or "Install app"
6. Confirm app icon appears in app drawer

#### Verification:
- ✅ Install banner shows with gradient styling
- ✅ App installs to app drawer (not just home screen shortcut)
- ✅ App opens in standalone mode
- ✅ Theme color (#0066FF) shows in status bar
- ✅ Offline functionality works

#### Analytics Check:
Open Chrome DevTools → Console → Run:
```javascript
viewPWAAnalytics()
```

Expected events:
- `install_prompt_available`
- `install_banner_shown`
- `install_button_clicked`
- `install_prompt_response` (outcome: "accepted")
- `app_installed_successfully`

---

### **Desktop Testing (Chrome/Edge on macOS/Windows)**

#### Installation Test:
1. Open Chrome/Edge on desktop
2. Navigate to: `http://localhost:8000`
3. Look for install banner OR install icon in address bar (⊕ icon)
4. Click "Install" on banner or address bar icon
5. App opens in separate window

#### Verification:
- ✅ App runs in standalone window (no browser chrome)
- ✅ Window has custom title bar
- ✅ App appears in OS app launcher
- ✅ Separate taskbar/dock icon

#### Uninstall Test:
- Right-click app icon → "Uninstall"
- Verify clean removal

---

## 🔌 Offline Testing

### **Test Offline Functionality:**

1. **Start server and open app:**
   ```bash
   python manage.py runserver
   ```

2. **Navigate through app while online:**
   - Visit dashboard
   - View rota page
   - Check reports
   - View staff list

3. **Disconnect from internet:**
   - Turn off Wi-Fi OR
   - In DevTools: Network tab → "Offline" throttling

4. **Test cached pages:**
   - Refresh dashboard (should load from cache)
   - Try to load new API data (should show offline message)
   - Check static assets load (CSS, JS, images)

5. **Expected behavior:**
   - ✅ Previously visited pages load instantly
   - ✅ Static assets (CSS, fonts, Chart.js) work
   - ✅ API calls fail gracefully with error messages
   - ✅ Offline page shows for uncached routes

---

## 🧪 Service Worker Testing

### **Cache Verification:**

1. **Open Chrome DevTools:**
   - Application tab → Cache Storage
   - Should see:
     - `staff-rota-v1-static` (CSS, JS, fonts, CDN libraries)
     - `staff-rota-v1-dynamic` (API responses, pages)

2. **Check cached assets:**
   - Expand `staff-rota-v1-static`
   - Verify Chart.js, Bootstrap, Font Awesome are cached
   - Verify local CSS/JS files are cached

3. **Test cache update:**
   - Modify `service-worker.js` (change CACHE_VERSION to 'v2')
   - Reload app
   - Old caches should be deleted
   - New cache version should appear

---

## 📊 Analytics Testing

### **View Install Analytics:**

Open browser console and run:
```javascript
// View all PWA analytics events
viewPWAAnalytics()

// Check specific events
const analytics = JSON.parse(localStorage.getItem('pwa-analytics'));
console.table(analytics);
```

### **Expected Analytics Events:**

| Event | When Fired | Data Captured |
|-------|-----------|---------------|
| `install_prompt_available` | Browser ready to install | userAgent, timestamp |
| `install_banner_shown` | Custom banner displayed | userAgent, standalone |
| `install_button_clicked` | User clicks Install | timestamp |
| `install_prompt_response` | User accepts/dismisses | outcome (accepted/dismissed) |
| `app_installed_successfully` | App installed | timestamp |
| `app_launched_as_pwa` | App opened in standalone mode | userAgent |
| `app_launched_in_browser` | App opened in browser | userAgent |
| `pwa_visibility_change` | App switched/minimized | visible (true/false) |

### **Clear Analytics:**
```javascript
localStorage.removeItem('pwa-analytics');
localStorage.removeItem('pwa-install-dismissed');
```

---

## 🐛 Debugging Common Issues

### **Install Banner Not Showing:**

**Possible causes:**
1. User previously dismissed banner
   - **Fix**: Clear localStorage: `localStorage.removeItem('pwa-install-dismissed')`

2. App already installed
   - **Fix**: Uninstall app first

3. Browser doesn't support PWA
   - **Fix**: Test on Chrome/Edge (Firefox limited support)

4. Not served over HTTPS (production)
   - **Fix**: Use localhost for dev OR deploy with HTTPS

5. Manifest.json errors
   - **Fix**: Check DevTools → Application → Manifest for errors

### **Service Worker Not Registering:**

**Check DevTools → Console for errors:**

1. Verify service worker registration:
   ```javascript
   navigator.serviceWorker.getRegistrations().then(registrations => {
       console.log('Registered SWs:', registrations);
   });
   ```

2. Check for registration errors in console

3. Verify service-worker.js is accessible:
   - Navigate to: `http://localhost:8000/static/js/service-worker.js`
   - Should return JavaScript file (not 404)

### **Offline Mode Not Working:**

1. Check service worker is active:
   - DevTools → Application → Service Workers
   - Status should be "activated and is running"

2. Verify caches exist:
   - Application → Cache Storage
   - Should see `staff-rota-v1-static` and `staff-rota-v1-dynamic`

3. Check network strategy:
   - Open Network tab
   - Look for "(from ServiceWorker)" in Size column

---

## 📋 Testing Checklist

### **Installation Testing:**
- [ ] iOS Safari - Manual "Add to Home Screen" works
- [ ] Android Chrome - Install banner shows after 5s
- [ ] Android Chrome - Install button works
- [ ] Desktop Chrome - Install icon in address bar
- [ ] Desktop Edge - Install works via banner
- [ ] App icons display correctly on all platforms
- [ ] Standalone mode works (no browser UI)

### **Offline Testing:**
- [ ] Service worker registers successfully
- [ ] Static cache populated on install
- [ ] Previously visited pages load offline
- [ ] CSS/JS/fonts work offline
- [ ] API calls fail gracefully offline
- [ ] Offline page shows for uncached routes

### **Analytics Testing:**
- [ ] Install prompt events tracked
- [ ] Banner shown/dismissed tracked
- [ ] Install acceptance/rejection tracked
- [ ] App launch mode tracked (PWA vs browser)
- [ ] Visibility changes tracked
- [ ] viewPWAAnalytics() function works

### **Update Testing:**
- [ ] New service worker activates on refresh
- [ ] Old caches deleted automatically
- [ ] Update notification shows (if implemented)
- [ ] No errors during cache migration

---

## 🚀 Production Testing Checklist

Before deploying to production:

1. **HTTPS Required:**
   - [ ] Production server has valid SSL certificate
   - [ ] All assets served over HTTPS
   - [ ] Mixed content errors resolved

2. **Manifest Validation:**
   - [ ] Icons exist and are correct sizes (192x192, 512x512)
   - [ ] start_url is correct
   - [ ] Theme colors match design system
   - [ ] No console errors for manifest

3. **Performance:**
   - [ ] Service worker doesn't block main thread
   - [ ] Cache size is reasonable (<50MB)
   - [ ] Install time is fast (<3 seconds)

4. **Cross-Browser:**
   - [ ] Chrome (desktop & mobile)
   - [ ] Edge (desktop & mobile)
   - [ ] Safari (iOS)
   - [ ] Firefox (limited PWA support)

---

## 🔧 Quick Testing Commands

### **Start Development Server:**
```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
python manage.py runserver 0.0.0.0:8000
```

### **Test on Mobile (Same Network):**
1. Find Mac IP: `ifconfig | grep "inet " | grep -v 127.0.0.1`
2. On mobile: Navigate to `http://YOUR_MAC_IP:8000`

### **Clear All Caches (Fresh Test):**
```javascript
// In browser console
caches.keys().then(keys => {
    keys.forEach(key => caches.delete(key));
});
localStorage.clear();
location.reload();
```

### **Force Service Worker Update:**
```javascript
navigator.serviceWorker.getRegistrations().then(registrations => {
    registrations.forEach(reg => reg.update());
});
```

---

## 📈 Success Criteria

PWA implementation is successful when:

✅ **Installation:**
- Install banner shows on Android Chrome within 5 seconds
- Manual install works on iOS via "Add to Home Screen"
- Desktop install works via address bar icon
- App appears in OS app launcher

✅ **Offline Functionality:**
- Previously visited pages load instantly offline
- Static assets (CSS, JS, fonts) cached correctly
- Graceful error handling for API calls when offline

✅ **Analytics:**
- All install events tracked correctly
- Analytics viewable via console
- User journey traceable (banner shown → clicked → installed)

✅ **User Experience:**
- Standalone mode works (no browser UI)
- Theme colors match design system
- App icons display correctly
- No console errors

---

## 🎓 Next Steps After Testing

Once PWA testing is complete:

1. **Document any bugs found** in SESSION_CHECKPOINT
2. **Fix critical issues** before moving to next phase
3. **Mark Task #2 as complete** in todo list
4. **Begin Task #3**: Enhanced Loading States (Week 2)

---

**Testing Started:** January 2, 2026  
**Estimated Completion:** January 6-8, 2026 (3-5 days)  
**Current Status:** 🚀 Ready to test
