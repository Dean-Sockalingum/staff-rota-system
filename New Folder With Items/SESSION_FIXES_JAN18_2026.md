# Production Fixes - Session January 18-19, 2026

## Summary
This session focused on fixing production deployment issues including browser caching, template rendering, compliance dashboard errors, and rota health scoring bugs.

---

## 1. Browser Caching Prevention ✅

### Issue
- Old data displayed until hard refresh
- Changes reverted when navigating between pages
- Aggressive browser caching preventing fresh data display

### Solution
**File: `scheduling/views.py`**
- Added `@never_cache` decorator to manager_dashboard (line 118)
- Added `@never_cache` decorator to rota_view (line 782)
- Added explicit cache-control headers to responses:
  ```python
  response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
  response['Pragma'] = 'no-cache'
  response['Expires'] = '0'
  ```

**File: `scheduling/middleware_cache.py`**
- Created NoCacheMiddleware class
- Applies cache prevention headers to all HTML responses
- Removes ETag headers to prevent 304 Not Modified responses

**File: `rotasystems/settings.py`**
- Added NoCacheMiddleware to MIDDLEWARE list

### Result
Cache prevention working globally - all pages serve fresh data on every request.

---

## 2. Weekly Schedule Sorting ✅

### Issue
- Management staff not sorted properly (SM should appear before OM)
- Supernumerary staff (SSCW/SSCWN) not in alphabetical order

### Solution
**File: `scheduling/views.py`**
- Lines 924-929: Added SM priority sorting for management
  ```python
  day_management.sort(key=lambda s: (0 if role=='SM' else 1, last_name, first_name))
  ```
- Lines 933-937: Added alphabetical sorting for day supernumerary
- Lines 942-946: Added alphabetical sorting for night supernumerary

### Result
SM appears before OM, all SSCW staff sorted alphabetically by last name.

---

## 3. Template Corruption Fix ✅

### Issue
- Production template had 2617 lines vs 2272 clean lines
- ANY modification caused 430-495MB memory leaks and worker SIGKILL
- Template became corrupted during previous modification attempts

### Solution
**Source:** `/Volumes/Working dri/Current Work/Staff_Rota_Production_Ready_2025-12-21/`
**File: `scheduling/templates/scheduling/rota_view.html`**
- Restored clean template from Dec 21 2025 backup (2272 lines)
- Created backups: rota_view.html.corrupted_jan18, rota_view.html.backup_stable_jan18

### Result
Memory stable at 76.3M (peak 76.6M) - template modifications now FORBIDDEN.

---

## 4. Banner & Navbar Full-Width Extension ✅

### Issue
- Orange DEMO banner and blue navbar not extending edge-to-edge
- White space visible on right side
- Poor text contrast on navbar links

### Solution
**File: `scheduling/templates/scheduling/base.html`**

Added CSS styling:
```html
<style>
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden !important;
        width: 100% !important;
    }
    
    .navbar-dark .navbar-nav .nav-link {
        color: #ffffff !important;
        font-weight: 500 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
    }
    
    .navbar-dark .navbar-nav .nav-link:hover {
        color: #ffeb3b !important;
        font-weight: 600 !important;
    }
</style>
```

Modified banner styling:
- Demo banner: `background-color: #ff6b00; color: #000000; font-weight: 800`
- Production banner: `background-color: #dc3545; color: #ffffff`
- Navbar: `background-color: #0056b3` with white text
- All elements: `width: 100%; box-sizing: border-box`

### Result
Banners extend full width, excellent contrast with white navbar text and yellow hover states.

---

## 5. Compliance Dashboard Fixes ✅

### Issue 1: Template Not Found
**Error:** `TemplateDoesNotExist: base.html`

**File: `scheduling/templates/scheduling/compliance_dashboard_new.html`**
- Line 1: Changed `{% extends 'base.html' %}` to `{% extends 'scheduling/base.html' %}`

### Issue 2: StaffCertification Table Missing
**Error:** `FieldError: Cannot resolve keyword 'care_home' for ForeignKey`

**File: `scheduling/views.py`**
- Line 14545: Disabled StaffCertification query - set to `[]`
- Line 14550: Changed `.count()` to `len(expiring_certifications)`
- Line 14561: Fixed RegulatoryCheck filter from `care_home=care_home` to `unit__care_home=care_home`

### Root Cause
StaffCertification table exists in models.py but was never created in production database during migration.

### Result
Compliance dashboard loads successfully with disabled certification queries.

---

## 6. Training Courses Added ✅

### Issue
Training compliance page showed 0 courses available.

### Solution
**File: `add_mandatory_training_courses.py`**
Ran script with virtual environment Python:
```bash
/home/staff-rota-system/venv/bin/python add_mandatory_training_courses.py
```

### Added 22 Mandatory Courses:
**Health & Safety (6):**
- Manual Handling, Fire Safety, First Aid
- Infection Prevention & Control, Food Hygiene, H&S Awareness

**Clinical (6):**
- Medication Management, Dementia Awareness, Mental Health
- Pressure Area Care, Nutrition & Hydration, End of Life Care

**Safeguarding (2):**
- Adult Support & Protection, Safeguarding Adults

**Professional (3):**
- Equality & Diversity, Dignity & Respect, Human Rights in Care

**Compliance (3):**
- Data Protection & Confidentiality, Record Keeping, Whistleblowing

**Induction (2):**
- Induction Training, Care Certificate (or SVQ equivalent)

### Result
All 22 Care Inspectorate required training courses now available in system.

---

## 7. Rota Health Scoring Fixes ✅

### Issue 1: Missing is_overtime Field
**Error:** `FieldError: Cannot resolve keyword 'is_overtime' into field`

**File: `scheduling/utils_rota_health_scoring.py`**
- Line 265: Disabled overtime shift filtering - set to `self.shifts.none()`
- Line 306: Disabled overtime count - set to `0`
- Line 339: Disabled overtime fairness calculation

### Issue 2: Missing duration_hours Field
**Error:** `FieldError: Cannot resolve keyword 'duration_hours' into field`

**File: `scheduling/utils_rota_health_scoring.py`**
- Line 388-390: Disabled long shift compliance check - set to `self.shifts.none()`

### Issue 3: Incorrect Function Arguments
**Error:** `TypeError: fromisoformat: argument must be str`

**File: `scheduling/views_ai_dashboards.py`**
- Line 176: Fixed argument order in score_rota call
- Changed FROM: `score_rota(care_home, hist_start, hist_end)`
- Changed TO: `score_rota(hist_start, hist_end, care_home)`

**Root Cause:** Function signature is `score_rota(start_date, end_date, care_home=None, unit=None)` but was being called with arguments in wrong order.

### Result
Rota health dashboard loads successfully with disabled overtime/duration calculations.

---

## Production Database Schema Issues

### Missing Fields Identified:
1. **Shift model:**
   - `is_overtime` - used for overtime shift tracking
   - `duration_hours` - used for WTD compliance checking

2. **Missing Table:**
   - `StaffCertification` - exists in models.py but table not created

### Available Shift Fields (Production):
- agency_company, agency_company_id, agency_hourly_rate, agency_requests
- agency_staff_name, alert_response, attendance_records, cover_requests
- created_at, created_by, created_by_id, custom_end_time, custom_start_time
- date, id, message, notes, notification, ot_offers, post_shift_admin
- reallocation_targets, reallocations_from, shift_classification, shift_pattern
- shift_type, shift_type_id, sickness_absences, status, swap_requests_from
- swap_requests_to, systemactivity, unit, unit_id, updated_at, user, user_id

### Recommendation
Run proper Django migrations to add missing fields:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## System Health Status

### Memory Usage
- **Stable:** 76.3M (peak 76.6M)
- **Healthy baseline maintained**
- No memory leaks after template restoration

### Service Status
- **Active:** Running without crashes
- **Port:** Listening on unix:/home/staff-rota-system/staffrota.sock
- **Worker:** Gunicorn with 1 worker process

### Warnings
- ⚠️ **Template Fragility:** ANY modification to rota_view.html causes memory leaks
- ⚠️ **Database Incomplete:** Multiple fields and tables missing from production
- ⚠️ **Feature Degradation:** Overtime and duration features disabled

---

## Files Modified

### On Production Server:
1. `/home/staff-rota-system/2025-12-12_Multi-Home_Complete/scheduling/views.py`
2. `/home/staff-rota-system/2025-12-12_Multi-Home_Complete/scheduling/middleware_cache.py`
3. `/home/staff-rota-system/2025-12-12_Multi-Home_Complete/rotasystems/settings.py`
4. `/home/staff-rota-system/2025-12-12_Multi-Home_Complete/scheduling/templates/scheduling/base.html`
5. `/home/staff-rota-system/2025-12-12_Multi-Home_Complete/scheduling/templates/scheduling/rota_view.html`
6. `/home/staff-rota-system/2025-12-12_Multi-Home_Complete/scheduling/templates/scheduling/compliance_dashboard_new.html`
7. `/home/staff-rota-system/2025-12-12_Multi-Home_Complete/scheduling/utils_rota_health_scoring.py`
8. `/home/staff-rota-system/2025-12-12_Multi-Home_Complete/scheduling/views_ai_dashboards.py`

### Scripts Created:
- `/tmp/fix_navbar.py` - Banner/navbar width fixes
- `/tmp/fix_banner_complete.py` - Contrast improvements
- `/tmp/fix_banner_final.py` - Full-width and contrast final fix
- `/tmp/fix_rota_health.py` - is_overtime field fix
- `/tmp/fix_rota_health_complete.py` - duration_hours field fix
- `/tmp/fix_score_rota_call.py` - Argument order fix

---

## Next Steps for Tomorrow

### High Priority:
1. **Database Migration:** Add missing fields (is_overtime, duration_hours) to Shift model
2. **Create StaffCertification Table:** Run migration to create missing table
3. **Test Full Features:** Re-enable overtime and duration features after migration
4. **Backup Current State:** Create full database backup before migrations

### Medium Priority:
1. **Layout Improvements:** Investigate safe way to improve rota view alignment
2. **Service Worker:** Review caching strategy for static assets
3. **Error Logging:** Improve error capture for silent failures

### Low Priority:
1. **Favicon:** Add missing favicon.ico file
2. **ALLOWED_HOSTS:** Add 'therota.co.uk' to settings
3. **Template Optimization:** Investigate root cause of template memory leak

---

## Testing Checklist

### ✅ Verified Working:
- [x] Browser cache prevention active
- [x] Weekly schedule displays fresh data
- [x] SM appears before OM in management section
- [x] SSCW staff sorted alphabetically
- [x] Banner and navbar extend full width
- [x] Navbar has white text with good contrast
- [x] Compliance dashboard loads (with limited features)
- [x] Training breakdown shows 22 courses
- [x] Rota health dashboard loads (with disabled features)
- [x] Memory stable at 76.3M

### ⚠️ Limited Functionality:
- [ ] Overtime tracking disabled (field missing)
- [ ] Shift duration compliance disabled (field missing)
- [ ] Staff certification tracking disabled (table missing)

### ❌ Known Issues:
- Template modifications cause memory leaks (CRITICAL - do not modify)
- Database schema incomplete vs code expectations
- Some AI features degraded due to missing data

---

## Contact & Support

**Production Server:** root@159.65.18.80  
**Service:** staffrota.service  
**Logs:** `journalctl -u staffrota -n 100 --no-pager`  
**Memory:** `systemctl status staffrota | grep Memory`  
**Restart:** `systemctl restart staffrota`

---

*Session completed: January 19, 2026, 01:40 UTC*  
*Status: Production stable with documented limitations*  
*Next session: Resume with database migration planning*
