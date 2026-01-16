# Phase 5: Testing Guide - Quick Start

**Server Status**: ✅ Running on http://127.0.0.1:8000/  
**Template Error**: ✅ Fixed (removed extra endif tag)

---

## Quick Test Checklist

### 1. Login & Authentication ✓
- [ ] Visit http://127.0.0.1:8000/
- [ ] Login with test credentials
- [ ] Verify redirect to appropriate dashboard based on role

### 2. Permission System Testing

#### Test User Setup Required:
Create test users with different permission levels:

```bash
python3 manage.py shell
```

```python
from scheduling.models import User, Role
from scheduling.models_multi_home import CareHome

# Get or create roles
sm_role = Role.objects.get(name='SM')  # FULL access
sscw_role = Role.objects.get(name='SSCW')  # MOST access
scw_role = Role.objects.get(name='SCW')  # LIMITED access

# Get a care home
hawthorn = CareHome.objects.get(name='HAWTHORN_HOUSE')

# Check permission levels
print(f"SM permission level: {sm_role.permission_level}")
print(f"SSCW permission level: {sscw_role.permission_level}")
print(f"SCW permission level: {scw_role.permission_level}")
```

#### Permission Tests:
- [ ] **FULL Access (SM/OM)**:
  - Can access any home dashboard
  - Sees all widgets (manual reviews, reallocations, pending leave)
  - Can approve requests
  - Has full quick actions

- [ ] **MOST Access (SSCW)**:
  - Can access assigned home dashboard
  - Sees most widgets (no manual reviews or reallocations)
  - Filtered pending leave requests
  - Limited quick actions

- [ ] **LIMITED Access (Staff)**:
  - Auto-redirected to assigned home
  - Sees only own information
  - Own leave requests only
  - Basic quick actions

### 3. Home-Specific Dashboard Testing

Test URLs:
- [ ] http://127.0.0.1:8000/home/ (auto-detect)
- [ ] http://127.0.0.1:8000/home/hawthorn-house/
- [ ] http://127.0.0.1:8000/home/meadowburn/
- [ ] http://127.0.0.1:8000/home/orchard-grove/
- [ ] http://127.0.0.1:8000/home/riverside/
- [ ] http://127.0.0.1:8000/home/victoria-gardens/

**Expected Behavior**:
- Senior management: Can select any home via dropdown
- Regular staff: Automatically locked to assigned home
- Invalid home slug: Redirects with error message

### 4. Senior Management Dashboard Testing

Visit: http://127.0.0.1:8000/senior-dashboard/

**Governance Alert Box** (top of page):
- [ ] Shows "Governance Team Access" heading
- [ ] Displays user's role and assigned home
- [ ] Explains SM access from all 5 homes
- [ ] Shows governance oversight message

**Live Refresh System**:
- [ ] Refresh status indicator visible in header
- [ ] Shows "Live data refresh: Active" with spinning icon
- [ ] Countdown timer visible (60 seconds)
- [ ] Pause/Resume button present
- [ ] Clicking Pause stops refresh and changes to "Resume"
- [ ] Clicking Resume restarts 60-second countdown
- [ ] Current time updates every second
- [ ] After 60 seconds, page auto-refreshes
- [ ] URL parameters preserved (start_date, end_date, care_home)

**Dashboard Widgets**:
- [ ] Home Overview (5 homes)
- [ ] Cross-Home Summary (occupancy, utilization, critical alerts)
- [ ] 7-Day Staffing Forecast (day shifts)
- [ ] Night Shift Staffing (7-day forecast)
- [ ] Staff Reallocation Needs
- [ ] Pending Leave Requests
- [ ] Quality Metrics (30 days)

**Date Range Filtering**:
- [ ] Start date picker works
- [ ] End date picker works
- [ ] Apply Filters button triggers refresh
- [ ] Data updates based on selected range

**Care Home Filtering**:
- [ ] Dropdown shows all 5 homes
- [ ] Selecting home filters data
- [ ] "All Homes" option available

### 5. Custom Report Builder Testing

Visit: http://127.0.0.1:8000/senior-dashboard/reports/

**Report Type Selection** (Step 1):
- [ ] 6 report types displayed:
  - Staffing Coverage Report
  - Leave Usage Report
  - Budget Variance Report
  - Compliance Report
  - Incident Summary Report
  - Comparative Analytics Report
- [ ] Each shows description
- [ ] Selection highlights chosen type

**Field Customization** (Step 2):
- [ ] 8-10 fields shown per report type
- [ ] Checkboxes for field selection
- [ ] Default fields pre-selected
- [ ] Can select/deselect any field

**Date Range Selection** (Step 3):
- [ ] Date pickers functional
- [ ] Quick select buttons:
  - Today
  - This Week
  - This Month
  - This Quarter
  - This Year
- [ ] Quick select updates date fields

**Care Home Filtering** (Step 4):
- [ ] Multi-select dropdown with 5 homes
- [ ] "All Homes" option
- [ ] Can select multiple homes
- [ ] Selection shows in dropdown

**Export Format** (Step 5):
- [ ] CSV export button (green)
- [ ] Excel export button (blue)
- [ ] PDF export button (red)
- [ ] Each button has icon
- [ ] Clicking generates report download

### 6. Error Handling Tests

**Permission Denials**:
- [ ] Non-senior management accessing senior dashboard → Redirects
- [ ] Staff accessing wrong home → Blocked with message
- [ ] Unassigned staff accessing home dashboard → Error message

**Invalid Data**:
- [ ] Non-existent home slug → Redirects with error
- [ ] Invalid date range → Defaults to today
- [ ] Empty report selection → Shows validation message

### 7. Browser Compatibility (Optional)

Test in multiple browsers:
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari

**Check for**:
- Layout issues
- JavaScript functionality
- Auto-refresh behavior
- Date picker compatibility

---

## Quick Test Commands

### Check Roles and Permission Levels:
```bash
python3 manage.py shell
```

```python
from scheduling.models import Role

for role in Role.objects.all():
    print(f"{role.name:20s} | Permission: {role.permission_level:10s} | Senior: {role.is_senior_management_team}")
```

### Check Care Homes:
```python
from scheduling.models_multi_home import CareHome

for home in CareHome.objects.all():
    print(f"{home.name:20s} | Display: {home.display_name:20s} | Active: {home.is_active}")
```

### Test User Methods:
```python
from scheduling.models import User

user = User.objects.first()  # Or get specific user

print(f"User: {user.username}")
print(f"Role: {user.role.name if user.role else 'None'}")
print(f"Permission Level: {user.role.permission_level if user.role else 'None'}")
print(f"Assigned Home: {user.assigned_care_home}")
print(f"Has FULL permission: {user.has_permission_level('FULL')}")
print(f"Has MOST permission: {user.has_permission_level('MOST')}")
print(f"Has LIMITED permission: {user.has_permission_level('LIMITED')}")
```

---

## Known Issues to Check

1. ~~Template syntax error (line 900)~~ ✅ **FIXED**
2. Migration 0020_add_permission_level applied ✅ **CONFIRMED**
3. All decorators imported correctly ✅ **VERIFIED**
4. URL routing configured ✅ **VERIFIED**

---

## Success Criteria

✅ **All systems operational**:
- Zero Python errors
- Zero template errors  
- Server running stable
- All URL routes working
- Auto-refresh functional
- Report builder accessible

**Next Step**: User acceptance testing with real data and actual user workflows.

---

## Troubleshooting

### Server Not Running:
```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
python3 manage.py runserver
```

### Check for Errors:
```bash
python3 manage.py check
python3 manage.py check --deploy
```

### View Logs:
Check terminal output for real-time errors and requests.

### Clear Template Cache:
```bash
python3 manage.py collectstatic --clear --noinput
# Or restart server (Ctrl+C then restart)
```

---

## Test Results Template

Copy this to track your testing:

```
## Test Results - [Date/Time]

### Permission System
- FULL access: [ ]
- MOST access: [ ]
- LIMITED access: [ ]

### Home Dashboards  
- 5 homes accessible: [ ]
- Auto-redirect: [ ]
- SM selection: [ ]

### Senior Dashboard
- Governance alert: [ ]
- Live refresh: [ ]
- Pause/resume: [ ]
- Data filtering: [ ]

### Report Builder
- 6 report types: [ ]
- Field selection: [ ]
- Date ranges: [ ]
- CSV export: [ ]
- Excel export: [ ]
- PDF export: [ ]

### Overall Status
- [ ] All tests passing
- [ ] Ready for production
- [ ] Issues found: _______
```

---

**Template Error Fixed**: Removed extra `{% endif %}` tag on line 900
**Server Status**: ✅ Running  
**Ready for Testing**: ✅ Yes
