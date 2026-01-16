# Executive Dashboards Access Guide
**Created:** Dec 30, 2025  
**For:** Crisis Friday Demo Practice

## Login Information

**Manager/Admin Access Required:**
- Username: `admin` or any manager account
- Standard staff accounts (like 000541) have limited access - they see their own staff dashboard only

**To access executive features, you need:**
- Manager role permissions (`can_manage_rota = True`)
- Or Admin superuser access

## Executive Dashboard URLs

Once logged in as manager/admin, access these URLs directly:

### 1. **Budget Dashboard** (£590K Efficiency Tracking)
```
http://localhost:8080/executive/budget/
```
- **Features:** Traffic lights (🔴🟡🟢🔵), 0-100 efficiency score, Chart.js trends
- **Demo Points:** Show £100 saved, 87/100 efficiency score

### 2. **Early Warning System** (14-Day Heatmap)
```
http://localhost:8080/executive/early-warning/
```
- **Features:** 14-day shortage predictions, 4-level escalation tracking
- **Demo Points:** Show tonight's shortage detected 14 days ago, 3 staff accepted OT automatically

### 3. **Retention Predictor** (Turnover Prevention)
```
http://localhost:8080/executive/retention/
```
- **Features:** Health score (0-100), intervention plans, risk factor analysis
- **Demo Points:** Show Alice Smith at 24hrs OT (🔴 high risk), intervention plan

### 4. **Training Compliance** (Matrix View) ✅ **AVAILABLE**
```
http://localhost:8080/compliance/training/management/
```
- **Features:** Staff×Training matrix (✅❌), compliance tracking, record management
- **Demo Points:** Show compliance percentage, expiring certifications
- **Status:** Working - uses existing compliance system

### 5. **Auto-Roster Generator** (Quality Scoring) ✅ **NOW AVAILABLE**
```
http://localhost:8080/executive/auto-roster/
```
- **Features:** Quality (0-100), fairness (0-100), constraint validation, staff distribution
- **Demo Points:** Show automated roster with 94/100 quality, fairness analysis
- **Status:** Working - full UI created

### 6. **CI Performance Dashboard** (Inspectorate Rating) ✅ **NOW AVAILABLE**
```
http://localhost:8080/executive/ci-performance/
```
- **Features:** Rating 0-100, peer benchmarking, 6-month trends, improvement areas
- **Demo Points:** Show rating 82/100, rank #3 of 8 homes, trending upward
- **Status:** Working - full UI created

### 7. **Predictive Budget** (Scenario Modeling) ✅ **NOW AVAILABLE**
```
http://localhost:8080/executive/predictive-budget/
```
- **Features:** Forecast accuracy (87%), scenario analysis, ROI metrics, cost projections
- **Demo Points:** Show £12K savings opportunity, 172% ROI, quarterly forecasts
- **Status:** Working - full UI created

## Navigation from Main Menu

After logging in as manager, you can access dashboards through:

1. **Main Dashboard** → Look for "Executive Dashboards" section
2. **Top Navigation** → "Analytics" or "Reports" menu
3. **Direct URLs** → Bookmark the URLs above

## Common Issues & Solutions

### Issue 1: "Page Not Found" Error
**Solution:** Make sure you're logged in as **manager/admin**, not regular staff (000541 is a staff member)

### Issue 2: Rota Incomplete from 4/1/26
**Solution:** Generate shifts for missing dates:
```python
# In Django shell
python3 manage.py shell
from scheduling.utils_auto_roster import generate_auto_rota
from datetime import date
generate_auto_rota(date(2026, 1, 4), date(2026, 1, 31), save_to_db=True)
```

### Issue 3: NoReverseMatch Error (Fixed)
**Solution:** ✅ Fixed in code - changed `manage_overtime_preferences` → `overtime_preferences_list`

## Crisis Friday Demo Sequence

**Recommended walkthrough order:**

1. **Early Warning** (27 sec) - "14 days ago, system detected tonight's shortage"
2. **Automated Escalation** (35 sec) - "L1: OT offers → L2: Agency contact → Done"
3. **Budget Dashboard** (45 sec) - "£100 saved (agency £280 → OT £180)"
4. **Retention** (40 sec) - "Alice at risk → Intervention plan created"
5. **CI Performance** (30 sec) - "Rating 82/100, rank #3, improving trend"
6. **Training** (30 sec) - "87% compliant, 8 sessions auto-scheduled"
7. **Auto-Roster** (30 sec) - "Quality 94/100, zero manager time"

**Total:** 4.5 minutes

## Manager Login Credentials

If you need manager access, try these accounts:

1. **Superuser:** `admin` / `admin123`
2. **Service Manager:** Usually firstname.lastname format
3. **Create New Manager:**
   ```python
   python3 manage.py createsuperuser
   ```

## Quick Test

### ✅ **All Executive Dashboards Now Working**:
1. **Budget:** http://localhost:8080/executive/budget/
2. **Early Warning:** http://localhost:8080/executive/early-warning/
3. **Retention:** http://localhost:8080/executive/retention/
4. **Training Compliance:** http://localhost:8080/compliance/training/management/
5. **Auto-Roster Generator:** http://localhost:8080/executive/auto-roster/
6. **CI Performance:** http://localhost:8080/executive/ci-performance/
7. **Predictive Budget:** http://localhost:8080/executive/predictive-budget/

**What You Should See:**
- ✅ Page loads without 404 error
- ✅ Filters render (care home, date range)
- ✅ Data displays or "No data available" message
- ✅ Export button present

**If you see errors:**
- **403 Forbidden:** Login as manager/admin
- **404 Not Found:** Check URL exactly matches above
- **500 Server Error:** Check Django logs - may need sample data

## Summary

**✅ All 7 Executive Dashboards Complete!**

All dashboards now have full UI with:
- Interactive filters (care home, date ranges)
- Real-time data visualization
- Export functionality (CSV/Excel)
- Manager-only access control
- Responsive design
- Color-coded status indicators

**Implementation Details:**
- 6 dashboards under `/executive/` prefix
- 1 dashboard under `/compliance/` (Training)
- All use existing backend analytics functions
- Permission checks: Manager, Head of Service, Admin only

---

**Need Help?**
- Server running: `http://localhost:8080`
- Admin interface: `http://localhost:8080/admin/`
- Staff view vs Manager view: Different permissions show different features
