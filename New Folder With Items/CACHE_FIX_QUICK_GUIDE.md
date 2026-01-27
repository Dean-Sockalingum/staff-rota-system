# QUICK FIX GUIDE - Caching Issue

## What Was Wrong
- Browser/Cloudflare was caching the rota HTML page
- Old empty data was being served from cache
- Hard refresh (Cmd+Shift+R) temporarily bypassed cache
- Navigating away and back served cached empty page again

## What Was Fixed
✅ Added `@never_cache` decorator to rota_view and manager_dashboard
✅ Added explicit cache-prevention headers to responses:
   - `Cache-Control: no-cache, no-store, must-revalidate, max-age=0`
   - `Pragma: no-cache`
   - `Expires: 0`
✅ Deployed to production (17 Jan 2026 23:40 UTC)

## WHAT YOU NEED TO DO NOW

### Step 1: Clear Cloudflare Cache (IMPORTANT!)

**Option A - Manual (Easiest):**
1. Go to https://dash.cloudflare.com
2. Select your domain: `therota.co.uk`
3. Click **Caching** → **Configuration**
4. Click **"Purge Everything"** button
5. Confirm and wait 30 seconds

**Option B - Selective:**
1. Same as above, but click **"Custom Purge"**
2. Add these URLs:
   - `https://demo.therota.co.uk/rota/`
   - `https://demo.therota.co.uk/manager-dashboard/`
3. Click **"Purge"**

### Step 2: Clear Your Browser Cache

**One of these methods:**

1. **Hard Refresh:**
   - Mac: `Cmd + Shift + R`
   - Windows: `Ctrl + Shift + R`

2. **Clear Cache:**
   - Chrome: Settings → Privacy → Clear browsing data → Cached images and files
   - Safari: Develop → Empty Caches
   - Firefox: Settings → Privacy → Clear Data → Cached Web Content

### Step 3: Test

1. Navigate to: `https://demo.therota.co.uk/rota/`
2. Select **Hawthorn House** from dropdown
3. **Weekly Schedule should display immediately** - no blank table
4. **Daily Staffing Summary should show real numbers** - not "0/18"
5. Navigate away (click Dashboard) then back to Rota
6. **Data should still be there** - no hard refresh needed!

## Expected Results

✅ **Before fix:** Blank → Hard refresh → Data appears → Navigate away → Blank again
✅ **After fix:** Data appears immediately, persists through navigation

## If Still Not Working

1. **Check Cloudflare:** Did you purge the cache?
2. **Check Browser:** Try incognito/private window (has no cache)
3. **Check Network Tab:** 
   - Open browser DevTools (F12)
   - Go to Network tab
   - Reload page
   - Look for the rota page request
   - Check Response Headers - should see `Cache-Control: no-cache, no-store`
4. **Check Status Code:** Should be `200 OK` not `304 Not Modified`

## Long-term Prevention

**Set up Cloudflare Page Rule:**
1. Cloudflare Dashboard → **Rules** → **Page Rules**
2. Create rule:
   - URL: `demo.therota.co.uk/rota/*`
   - Setting: **Cache Level** → **Bypass**
3. Save and Deploy

This prevents Cloudflare from caching dynamic pages in the future.

## Contact
If this still doesn't work after following all steps, we may need to:
- Check Cloudflare SSL/Cache settings
- Add Vary headers to responses
- Implement versioned URLs with cache busting parameters
