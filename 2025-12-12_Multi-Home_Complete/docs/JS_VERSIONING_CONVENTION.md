# JavaScript File Versioning Convention

**Created:** January 14, 2026  
**Purpose:** Prevent browser caching issues when updating JavaScript files

## The Problem

When you update a JavaScript file (like `chart-config.js`), browsers aggressively cache the old version. Even hard refreshes (Cmd+Shift+R) don't always work, leading to users seeing old buggy code instead of your fixes.

## The Solution: Version Parameters

Add a version parameter to all JavaScript file references in HTML templates:

```html
<!-- Before -->
<script src="{% static 'js/chart-config.js' %}"></script>

<!-- After -->
<script src="{% static 'js/chart-config.js' %}?v=2.1"></script>
```

## Version Numbering System

Use semantic versioning: `MAJOR.MINOR`

### When to Bump MAJOR Version (1.0 → 2.0)
- Complete rewrite of the file
- Breaking changes that affect multiple pages
- Major feature additions

### When to Bump MINOR Version (2.0 → 2.1)
- Bug fixes (most common)
- Small feature additions
- Code refactoring
- Any change that needs to force browser refresh

## Where to Version

### ✅ Always Version These Files:
- `chart-config.js` - Chart helper functions
- `charts.js` - PDSA chart visualizations  
- Any custom JavaScript libraries you create
- Files that change frequently during development

### ⚠️ Consider Versioning:
- Third-party libraries (if you modify them)
- API client scripts
- Form validation scripts

### ❌ No Need to Version:
- External CDN libraries (Bootstrap, jQuery, Chart.js from CDN)
- Files that never change
- Static images, CSS (use different methods for CSS)

## Implementation Examples

### Example 1: Chart Configuration Fix (Jan 13, 2026)
**File:** `scheduling/templates/scheduling/base.html`

```html
<!-- Before fix -->
<script src="{% static 'js/chart-config.js' %}?v=2.0"></script>

<!-- After fixing function-based colors bug -->
<script src="{% static 'js/chart-config.js' %}?v=2.1"></script>
```

**Why:** Fixed TypeError with function-based colors. Browser was serving cached v2.0 with the bug.

### Example 2: New Feature Addition
```html
<!-- Before -->
<script src="{% static 'js/pdsa-charts.js' %}?v=1.2"></script>

<!-- After adding export to PNG feature -->
<script src="{% static 'js/pdsa-charts.js' %}?v=1.3"></script>
```

## Best Practices

### 1. Track Versions in Comments
Add version history at the top of your JS files:

```javascript
/**
 * Chart Configuration Helpers
 * 
 * Version History:
 * v2.1 (2026-01-13): Fixed function-based color handling
 * v2.0 (2026-01-10): Added hexToRgba helper
 * v1.0 (2025-12-15): Initial creation
 */
```

### 2. Update All References
When you bump a version, update ALL templates that reference the file:
- `base.html`
- `dashboard.html`
- Any other templates using that script

### 3. Document Changes
In your git commit message, mention the version bump:

```bash
git commit -m "fix(cache): Bump chart-config.js to v2.1

- Fixed TypeError with function-based colors
- Version bump forces browser cache refresh
- Updated base.html script reference"
```

### 4. Test in Incognito Mode
After versioning, always test in an incognito/private window to verify the new version loads.

## Alternative: Automated Cache Busting

For production deployments, consider automated cache busting using file hashes:

```python
# In Django settings.py (future enhancement)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
```

This auto-generates hashed filenames like `chart-config.a3f5b2c.js` but requires collectstatic on every deployment.

## Troubleshooting

### "I bumped the version but still seeing old code"
1. Check you updated ALL templates referencing the file
2. Run `python manage.py collectstatic` if using static file collection
3. Clear browser cache AND cookies for localhost
4. Try a different browser
5. Check browser dev tools Network tab to see what URL is being requested

### "How do I know what version is currently loaded?"
Add a console log at the top of your JS file:

```javascript
console.log('chart-config.js v2.1 loaded');
```

Check the browser console to see which version loaded.

## When NOT to Use This

- **Production with CDN:** Use proper cache-control headers instead
- **Files that never change:** Unnecessary overhead
- **CSS files:** Use Django's `{% static %}` with ManifestStaticFilesStorage

## Lessons Learned (Jan 13, 2026)

**Situation:** Fixed chart TypeError but browser kept serving old code  
**Failed:** Hard refresh (Cmd+Shift+R)  
**Failed:** Force reload without cache  
**Worked:** Bumped ?v=2.0 → ?v=2.1  
**Takeaway:** Version parameters are MORE reliable than cache-control headers for local development

---

**Next Steps After Versioning:**
1. Test the fix in browser
2. Verify new version loads (check Network tab)
3. Commit the version bump
4. Document the change
5. Update this convention if you find better approaches
