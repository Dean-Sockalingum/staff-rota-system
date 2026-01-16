# Chart Issues Troubleshooting Guide

**Created:** January 14, 2026  
**Purpose:** Debug and fix common Chart.js issues in the Staff Rota system

## Quick Diagnosis Checklist

When charts aren't working, check these in order:

1. ☐ Does the chart container exist in HTML? (Check browser Elements tab)
2. ☐ Is Chart.js library loaded? (Check browser Console for errors)
3. ☐ Is chart-config.js loaded? (Check Console for version log)
4. ☐ Is data being fetched from API? (Check Network tab)
5. ☐ Are there JavaScript errors? (Check Console tab)

---

## Common Issues & Solutions

### Issue 1: TypeError: hex.slice is not a function

**Symptoms:**
```javascript
TypeError: hex.slice is not a function at hexToRgba (chart-config.js:89:32)
```

**Root Cause:**  
Chart datasets using function-based colors instead of string hex values:

```javascript
backgroundColor: function(context) {
    return condition ? 'red' : 'green';  // Function, not string
}
```

**Solution:**  
Add type checking in color helper functions:

```javascript
function hexToRgba(hex, alpha = 1) {
    // Type checking - if not a string, return as-is
    if (typeof hex !== 'string') {
        return hex;  // Preserve functions
    }
    
    // Also check if already formatted
    if (hex.startsWith('rgba') || hex.startsWith('rgb')) {
        return hex;
    }
    
    // Convert hex to rgba
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}
```

**Prevention:**  
Always check input types before calling string methods like `.slice()`, `.substring()`, etc.

**Fixed In:** Commit efea9d3 (Jan 13, 2026)

---

### Issue 2: Chart Not Appearing After Code Update

**Symptoms:**
- Fixed the code
- Hard refreshed browser (Cmd+Shift+R)
- Chart still broken
- Console shows same error

**Root Cause:**  
Browser aggressively caches JavaScript files, serving old buggy version even after refresh.

**Solution:**  
Bump the version parameter in your template:

```html
<!-- Old -->
<script src="{% static 'js/chart-config.js' %}?v=2.0"></script>

<!-- New -->
<script src="{% static 'js/chart-config.js' %}?v=2.1"></script>
```

**Why It Works:**  
Changing the URL parameter forces browser to fetch the new file instead of using cache.

**Alternative Solutions:**
1. Open incognito/private window
2. Clear all browser cache for localhost
3. Use different browser
4. Add `console.log('version 2.1')` to verify which version loads

**Prevention:**  
Always bump version parameters when updating JavaScript files. See [docs/JS_VERSIONING_CONVENTION.md](docs/JS_VERSIONING_CONVENTION.md).

**Fixed In:** Commit 5f0ffe3 (Jan 13, 2026)

---

### Issue 3: Chart Shows "No Data Available"

**Symptoms:**
- Chart container renders
- Message says "No data available"
- No JavaScript errors

**Diagnosis Steps:**

1. **Check API endpoint:**
```javascript
// Open browser console
fetch('/api/chart-data/')
    .then(r => r.json())
    .then(console.log)
```

2. **Check data format:**
```javascript
// Expected format
{
    labels: ['Jan', 'Feb', 'Mar'],
    datasets: [{
        label: 'Sales',
        data: [10, 20, 30]
    }]
}
```

3. **Check for empty datasets:**
```javascript
// In your view
if not queryset.exists():
    return JsonResponse({'labels': [], 'datasets': []})
```

**Common Causes:**
- Empty database (run `python manage.py populate_pdsa_data`)
- Date filters excluding all data
- Wrong queryset filters
- API endpoint returning 404/500

**Solution:**  
Populate sample data or adjust filters to include data.

---

### Issue 4: Charts Work Locally But Not In Production

**Symptoms:**
- Charts render perfectly on localhost:8001
- Production shows blank charts or errors
- Different behavior between environments

**Diagnosis:**

1. **Check static files collected:**
```bash
python manage.py collectstatic
```

2. **Verify static URLs in production:**
```html
<!-- Should show production CDN/static URL -->
<script src="/static/js/chart-config.js?v=2.1"></script>
```

3. **Check browser console in production:**
- Look for 404 errors on .js files
- Check for CORS errors
- Verify Chart.js CDN loads

**Common Causes:**
- Static files not collected
- STATIC_URL misconfigured
- CDN blocked by firewall
- Different Chart.js versions

**Solution:**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Verify settings
DEBUG = False
STATIC_URL = '/static/'
STATIC_ROOT = '/path/to/staticfiles/'
```

---

### Issue 5: Chart Colors Not Applying

**Symptoms:**
- Chart renders with default colors
- Custom colors ignored
- Console shows no errors

**Check 1: Color Format**
```javascript
// ✅ Good - Hex
backgroundColor: '#66DBA3'

// ✅ Good - RGBA
backgroundColor: 'rgba(102, 219, 163, 0.8)'

// ✅ Good - Function
backgroundColor: function(context) {
    return context.dataIndex > 5 ? 'red' : 'green';
}

// ❌ Bad - Invalid hex
backgroundColor: '66DBA3'  // Missing #

// ❌ Bad - Typo
backgroundColor: 'rgba(102, 219, 163, 0.8'  // Missing )
```

**Check 2: Chart Type Compatibility**
Some color properties only work with certain chart types:

```javascript
// Line charts
borderColor: '#66DBA3',
backgroundColor: 'rgba(102, 219, 163, 0.2)',  // Fill under line

// Bar charts
backgroundColor: '#66DBA3',  // Bar fill color
borderColor: '#4CAF50',      // Bar border

// Pie charts
backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56']  // Array of colors
```

**Solution:**  
Verify color format matches chart type requirements.

---

### Issue 6: Responsive Charts Not Resizing

**Symptoms:**
- Chart fixed size
- Doesn't resize with window
- Overflows container

**Solution:**  
Ensure responsive options enabled:

```javascript
const config = {
    type: 'line',
    data: chartData,
    options: {
        responsive: true,
        maintainAspectRatio: false  // Allow height adjustment
    }
};
```

**HTML Container:**
```html
<div style="position: relative; height: 400px;">
    <canvas id="myChart"></canvas>
</div>
```

---

## Debugging Workflow

### Step 1: Browser Console
```javascript
// Check Chart.js loaded
typeof Chart !== 'undefined'  // Should be true

// Check chart-config.js loaded
typeof createBarChart !== 'undefined'  // Should be true

// Check data fetch
fetch('/api/dashboard-stats/')
    .then(r => r.json())
    .then(console.log)
```

### Step 2: Network Tab
- Verify all .js files load (200 status)
- Check API endpoints return data
- Look for CORS errors
- Verify version parameters in URLs

### Step 3: Elements Tab
- Find `<canvas id="yourChart">`
- Check if it has width/height
- Verify parent container exists
- Check for CSS hiding elements

### Step 4: Django Shell
```python
# Test data queries
python manage.py shell

from quality_audits.models import PDSAProject
print(PDSAProject.objects.count())  # Should be > 0

from scheduling.views import get_dashboard_stats
# Test view logic
```

---

## Prevention Best Practices

### 1. Always Use Try-Catch for Chart Creation
```javascript
try {
    const chart = new Chart(ctx, config);
} catch (error) {
    console.error('Chart creation failed:', error);
    document.getElementById('chartContainer').innerHTML = 
        '<p class="text-danger">Error loading chart</p>';
}
```

### 2. Validate Data Before Charting
```javascript
function createChart(data) {
    if (!data || !data.labels || !data.datasets) {
        console.warn('Invalid chart data:', data);
        return null;
    }
    
    if (data.labels.length === 0) {
        console.info('No data to display');
        return null;
    }
    
    // Create chart...
}
```

### 3. Add Console Logging
```javascript
console.log('chart-config.js v2.1 loaded');

function createBarChart(canvasId, data, options) {
    console.log('Creating bar chart:', canvasId, data);
    // ...
}
```

### 4. Version Your JavaScript Files
See [docs/JS_VERSIONING_CONVENTION.md](docs/JS_VERSIONING_CONVENTION.md)

### 5. Test in Multiple Browsers
- Chrome (most common)
- Safari (macOS)
- Firefox (good debugging tools)
- Edge (Windows users)

---

## Chart.js Version Compatibility

### Current Setup
- Chart.js: 4.4.0 (from CDN)
- Bootstrap: 5.3.2
- jQuery: 3.6.0

### Known Issues
- Chart.js v3 → v4: Breaking changes in options structure
- Older browsers: May need polyfills
- Mobile Safari: Sometimes requires explicit height

### Upgrade Path
If upgrading Chart.js:
1. Check migration guide
2. Test all charts
3. Update chart-config.js
4. Bump version parameter
5. Test in production

---

## Emergency Fixes

### Quick Fix: Disable Chart
If chart is completely broken and blocking work:

```html
<!-- Temporarily comment out -->
<!-- <canvas id="budgetChart"></canvas> -->
<p class="text-muted">Chart temporarily disabled</p>
```

### Quick Fix: Bypass Cache
Add random parameter:

```html
<script src="{% static 'js/chart-config.js' %}?v=2.1&t=<?= time() ?>"></script>
```

---

## Getting Help

### Useful Resources
- Chart.js Docs: https://www.chartjs.org/docs/latest/
- MDN Canvas API: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API
- Bootstrap Grid: https://getbootstrap.com/docs/5.3/layout/grid/

### Session Checkpoints
Check previous debugging sessions:
- `SESSION_CHECKPOINT_JAN13_NIGHT.md` - Chart TypeError fix
- Future checkpoints will be documented here

### Code Examples
- `scheduling/static/js/chart-config.js` - Helper functions
- `quality_audits/static/js/charts.js` - PDSA charts
- `scheduling/templates/scheduling/executive_dashboard.html` - Complex charts example

---

**Last Updated:** January 14, 2026  
**Lessons Learned:** 2 major chart bugs fixed (Jan 13, 2026)  
**Success Rate:** 100% of issues documented here have known solutions
