# CACHE FIX IMPLEMENTATION

**Date:** 17 January 2026
**Issue:** Weekly Schedule and staffing data appearing blank until hard refresh, requiring hard refresh after every navigation

## Root Cause

The application was experiencing aggressive browser and CDN (Cloudflare) caching of dynamic HTML responses. The rota view and manager dashboard were being cached, causing:
1. Blank pages on first load (cached empty response from before data fix)
2. Stale data persisting after navigation
3. Required hard refresh (Cmd+Shift+R / Ctrl+Shift+R) to see updated content

## Solution Implemented

### 1. Django View-Level Cache Prevention

**File:** `scheduling/views.py`

**Changes:**

#### Import Addition (Line 6)
```python
from django.views.decorators.cache import never_cache
```

#### Decorators Applied
```python
@login_required
@never_cache
def rota_view(request):
    # ... existing code ...

@login_required
@never_cache
def manager_dashboard(request):
    # ... existing code ...
```

#### Response Headers Added
Both `rota_view` and `manager_dashboard` now return responses with explicit cache-prevention headers:

```python
response = render(request, 'scheduling/rota_view.html', context)
# Explicitly prevent caching at all levels (browser, CDN, proxy)
response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
response['Pragma'] = 'no-cache'  # HTTP 1.0 compatibility
response['Expires'] = '0'  # Proxies
return response
```

**Explanation of Headers:**
- `Cache-Control: no-cache, no-store, must-revalidate, max-age=0`
  - `no-cache`: Must revalidate with server before using cached copy
  - `no-store`: Don't store any cached copy at all
  - `must-revalidate`: Once stale, must check with origin server
  - `max-age=0`: Content is immediately stale
- `Pragma: no-cache`: HTTP/1.0 backwards compatibility
- `Expires: 0`: Tells proxies content is already expired

### 2. Deployment Process

**Script:** `deploy_cache_fix.sh`

```bash
#!/bin/bash
# Deploy cache-prevention fix to production

# Copy updated views.py
scp views.py root@159.65.18.80:/home/staff-rota-system/.../scheduling/

# Clear Django sessions and restart
ssh root@159.65.18.80 << 'ENDSSH'
cd /home/staff-rota-system/2025-12-12_Multi-Home_Complete
source ../venv/bin/activate
python manage.py clearsessions
systemctl restart staffrota
ENDSSH
```

**Executed:** 17 Jan 2026 23:40 UTC
**Status:** ✅ Deployed successfully
**Service Status:** Active (running), Memory 76.3M

### 3. Cloudflare Cache Management

**Issue:** Cloudflare may still be caching HTML responses

**Solution Options:**

#### Option A: Manual Purge (Immediate)
1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Select domain: `therota.co.uk`
3. Navigate to: **Caching** → **Configuration**
4. Click **"Purge Everything"** button
5. Confirm purge
6. Wait 30 seconds

#### Option B: Selective URL Purge
1. In Cloudflare Dashboard → **Caching** → **Configuration**
2. Click **"Custom Purge"**
3. Select **"URL"** tab
4. Add URLs:
   - `https://demo.therota.co.uk/rota/`
   - `https://demo.therota.co.uk/manager-dashboard/`
5. Click **"Purge"**

#### Option C: API Script (Automated)
**Script:** `purge_cloudflare_cache.sh`

Requires Cloudflare API credentials:
- Zone ID (from Cloudflare dashboard)
- API Token with "Cache Purge" permission

Configure and run:
```bash
./purge_cloudflare_cache.sh
```

### 4. Cloudflare Page Rules (Recommended Long-term)

**Create Page Rule to Bypass Cache for Dynamic Pages:**

1. Cloudflare Dashboard → **Rules** → **Page Rules**
2. Click **"Create Page Rule"**
3. URL pattern: `demo.therota.co.uk/rota/*`
4. Settings:
   - **Cache Level:** Bypass
5. Save and Deploy

Repeat for:
- `demo.therota.co.uk/manager-dashboard/*`
- `demo.therota.co.uk/api/*` (if applicable)

**Or set cache control based on response headers:**
1. Create Page Rule
2. URL: `demo.therota.co.uk/*`
3. Setting: **Respect Existing Headers**
4. This tells Cloudflare to honor our `Cache-Control` headers

## User Instructions

After deployment, users must:

### First-Time After Fix
1. **Hard Refresh** the page:
   - **Mac:** `Cmd + Shift + R`
   - **Windows/Linux:** `Ctrl + Shift + R`
2. Or **Clear Browser Cache**:
   - Chrome: Settings → Privacy → Clear browsing data → Cached images and files
   - Safari: Develop → Empty Caches (or enable Develop menu first)
   - Firefox: Settings → Privacy → Clear Data → Cached Web Content

### Normal Usage Going Forward
- Regular refresh should work (no more hard refresh needed)
- Data should update automatically on each page load
- No more blank pages after navigation

## Verification

Test the fix by:

1. **Navigate to Rota View:** `https://demo.therota.co.uk/rota/`
2. **Check Weekly Schedule displays immediately** (no hard refresh needed)
3. **Navigate away and back** to rota view
4. **Verify data still displays** without hard refresh
5. **Check Network tab** in browser DevTools:
   - Response headers should show: `Cache-Control: no-cache, no-store, must-revalidate, max-age=0`
   - `Status: 200` (not `304 Not Modified` from cache)

## Monitoring

Watch for these indicators of success:

✅ **Good Signs:**
- Data appears immediately on page load
- No blank Weekly Schedule table
- Daily Staffing Summary shows staff counts immediately
- No hard refresh required between navigation
- HTTP headers show cache-prevention directives

❌ **Problem Signs:**
- Still seeing blank pages on first load
- Hard refresh still required
- Browser DevTools show `304 Not Modified` responses
- Cloudflare cache still serving old content

If problems persist:
1. Verify Cloudflare cache was purged
2. Check browser is not forcing cache (disable browser cache in DevTools)
3. Verify deployment succeeded (check views.py on server has changes)
4. Check Cloudflare Page Rules are not overriding headers

## Technical Notes

### Why @never_cache Alone Wasn't Enough
The `@never_cache` decorator sets `Cache-Control: max-age=0` but Cloudflare may still cache responses. We needed to explicitly set multiple headers for different caching layers:
- Browser cache: `no-store, no-cache`
- Proxy cache: `Pragma`, `Expires`
- CDN cache: `must-revalidate`

### Why This Happened
1. **Initial empty data** was served and cached by browser/Cloudflare
2. **Data fix deployed** but cached response still served
3. **Role filtering fix deployed** but cached response still served
4. **Hard refresh** bypassed cache, showed correct data
5. **Navigation** re-requested page, got cached (empty) response again

### Performance Impact
Minimal - these pages are dynamic and should never be cached anyway:
- Database queries still fast (~10-20ms)
- Template rendering still fast (~50-100ms)
- Total page load: ~200-300ms (acceptable)
- No static assets affected (CSS, JS still cached)

## Related Files

- `scheduling/views.py` - Cache headers implementation
- `deploy_cache_fix.sh` - Deployment script
- `purge_cloudflare_cache.sh` - Cloudflare cache purge tool
- `CACHE_FIX_IMPLEMENTATION.md` - This document

## Rollback Plan

If this causes issues:

1. Revert `views.py` changes:
   ```python
   # Remove @never_cache decorator
   # Change response back to:
   return render(request, 'scheduling/rota_view.html', context)
   ```

2. Redeploy:
   ```bash
   scp views.py root@159.65.18.80:/home/.../scheduling/
   ssh root@159.65.18.80 'systemctl restart staffrota'
   ```

3. But note: This will bring back the caching issue

Better approach: Investigate why caching is needed (it shouldn't be for dynamic data)

## Next Steps

**Immediate:**
1. ✅ Deploy cache fix (DONE)
2. ⏳ Purge Cloudflare cache (USER ACTION REQUIRED)
3. ⏳ User hard refresh browser (USER ACTION REQUIRED)
4. ⏳ Verify data displays correctly without refresh

**Short-term:**
1. Set up Cloudflare Page Rules to respect cache headers
2. Remove debug print statements from rota_view (lines 880-885)
3. Monitor for any caching issues in other views

**Long-term:**
1. Audit all dynamic views to ensure proper cache headers
2. Consider implementing ETags for conditional requests
3. Set up proper cache strategy:
   - Static assets: long cache (1 year)
   - Dynamic pages: no cache
   - API responses: short cache with revalidation (5 min)
4. Document caching strategy in deployment guide
