# PWA Testing Session - January 2, 2026

## ✅ Server Status
- **Running**: http://0.0.0.0:8000
- **Local IP**: 192.168.1.125
- **Started**: January 2, 2026 08:53

---

## 📱 Quick Testing Steps

### **Desktop Testing (Current Browser)**
1. ✅ Server running at: http://localhost:8000
2. Open browser console (F12 or Cmd+Option+I)
3. Wait 5 seconds for install banner to appear
4. Check console for analytics logs:
   ```
   [PWA Analytics] install_prompt_available
   [PWA Analytics] install_banner_shown
   ```
5. Click "Install" button if banner appears
6. Run in console: `viewPWAAnalytics()`

### **Mobile Testing (iPhone/iPad/Android)**
📱 Connect device to same Wi-Fi network

**On Mobile Browser:**
1. Navigate to: **http://192.168.1.125:8000**
2. Login with your credentials
3. **iOS Safari**: Tap Share (⬆️) → "Add to Home Screen"
4. **Android Chrome**: Wait for banner OR Menu (⋮) → "Install app"
5. Check home screen for app icon
6. Tap icon to launch in standalone mode

---

## 🧪 Tests to Run

### **1. Installation Test**
- [ ] Install banner shows after 5 seconds (Desktop/Android)
- [ ] Install button works
- [ ] App icon appears on home screen
- [ ] App launches in standalone mode (no browser UI)

### **2. Offline Test**
- [ ] Visit dashboard while online
- [ ] Turn off Wi-Fi
- [ ] Refresh page - should load from cache
- [ ] Check console for "[Service Worker] Serving from cache"

### **3. Analytics Test**
Open console and run:
```javascript
viewPWAAnalytics()
```

Expected events:
- `install_prompt_available`
- `install_banner_shown`
- `install_button_clicked`
- `install_prompt_response` (outcome: "accepted")
- `app_installed_successfully`
- `app_launched_as_pwa` OR `app_launched_in_browser`

### **4. Service Worker Test**
In DevTools → Application tab:
- [ ] Service Worker shows as "activated and is running"
- [ ] Cache Storage has `staff-rota-v1-static` 
- [ ] Cache Storage has `staff-rota-v1-dynamic`
- [ ] Check cached files (Chart.js, Bootstrap, CSS)

---

## 🐛 If Issues Found

### **Banner Not Showing:**
```javascript
// Clear previous dismissal
localStorage.removeItem('pwa-install-dismissed');
location.reload();
```

### **Service Worker Not Working:**
```javascript
// Check registration
navigator.serviceWorker.getRegistrations().then(r => console.log(r));
```

### **Clear Everything (Fresh Test):**
```javascript
// Clear all caches and storage
caches.keys().then(keys => keys.forEach(k => caches.delete(k)));
localStorage.clear();
location.reload();
```

---

## 📊 Console Commands Reference

| Command | Purpose |
|---------|---------|
| `viewPWAAnalytics()` | View all PWA events tracked |
| `localStorage.getItem('pwa-analytics')` | Get raw analytics JSON |
| `localStorage.removeItem('pwa-install-dismissed')` | Re-enable install banner |
| `navigator.serviceWorker.getRegistrations()` | Check SW registration |

---

## ✅ Success Criteria

PWA is working correctly when:
1. ✅ Install banner appears (Desktop/Android)
2. ✅ Manual install works (iOS)
3. ✅ App runs in standalone mode
4. ✅ Offline pages load from cache
5. ✅ Analytics track all events
6. ✅ Service worker logs appear in console

---

## 📝 Notes During Testing

**Observed Behaviors:**
- (Add notes here as you test)

**Issues Found:**
- (Document any bugs or unexpected behavior)

**Analytics Events Captured:**
- (Paste results from `viewPWAAnalytics()`)

---

## 🎯 Next Steps After Testing

Once testing complete:
1. Document any bugs in this file
2. Fix critical issues
3. Commit changes with test results
4. Mark Task #2 as complete
5. Begin Task #3: Enhanced Loading States

---

**Testing Started**: January 2, 2026  
**Tester**: Dean Sockalingum  
**Status**: 🚀 Ready to Test
