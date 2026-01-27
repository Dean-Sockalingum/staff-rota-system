# Quick Start: Staffing Template & Demo Access

**Date:** January 26, 2026  
**Your Current Login:** Check which user you're logged in as

---

## 🎯 What You're Looking For

1. **Staffing Template** - Documentation for bulk setup
2. **Demo Home** - Live example of staffing structure
3. **Bulk Upload** - CSV import for staff

---

## 📍 Step 1: Access the TEMPLATE_DEMO Home

The TEMPLATE_DEMO home has been created with 5 care units and 32 staff showing the template in action.

### Option A: Login as Demo Staff (Recommended)
**Credentials:**
- **SAP:** Any number from `950000` to `950031`
- **Password:** `Demo123##`

**Example:**
```
SAP: 950000
Password: Demo123##
```

### Option B: Login as Superuser
- **SAP:** `000541`
- **Password:** `Greenball99##`

---

## 📍 Step 2: Navigate to TEMPLATE_DEMO

Once logged in:

1. **Go to Dashboard** → Look for "Home Selection" or "Care Home" dropdown
2. **Select:** `TEMPLATE_DEMO`
3. You should see:
   - 5 Care Units: Jasmine, Lavender, Magnolia, Orchid, Poppy
   - 1 Management Unit
   - 32 Staff total
   - 1,170 shifts (3 months)

---

## 📍 Step 3: View Staffing Structure

### To See Staff by Unit:
1. Navigate to **Staff** or **Staff Management** menu
2. Filter by Unit (e.g., "Jasmine")
3. You'll see the staffing pattern:
   - 1 SSCW (Senior Social Care Worker - Day)
   - 1 SSCWN (Senior Social Care Worker - Night)
   - 2 Day care staff (SCW or SCA)
   - 2 Night care staff (SCWN or SCAN)
   
### To See Shifts:
1. Navigate to **Rota** or **Shift Schedule**
2. View the 3-week rotation patterns
3. Staff on Teams A, B, C rotating

---

## 📍 Step 4: Download Staffing Template

The complete staffing template is located at:

**File:** `STAFFING_SETUP_TEMPLATE.md`

**What's Inside:**
- Template A: Large Home (120 beds, 8 care units)
- Template B: Medium Home (70 beds, 5 care units)
- CSV Import Format
- Role Definitions
- Shift Patterns
- Quick Setup Wizard

### To Use for New Home Setup:

**Option 1: Use CSV Bulk Upload**

1. Open `STAFFING_SETUP_TEMPLATE.md`
2. Go to section: **"Excel/CSV Import Template"**
3. Copy the CSV format:
   ```csv
   Home Name,Unit Name,SAP,First Name,Last Name,Role,Team,Shift Pattern,Hours,Password
   NEW_HOME,Unit_1,100001,John,Smith,SSCW,A,Pattern_2,35,Password123##
   NEW_HOME,Unit_1,100002,Jane,Doe,SSCWN,B,Pattern_2,35,Password123##
   ```
4. Fill in your staff details
5. Navigate to **Admin** → **Bulk Upload** or **Import Staff**
6. Upload CSV file

**Option 2: Manual Entry Using Template**

1. Reference the staff counts from template:
   - Per 15-bed unit: 6 staff (2 supervisors + 4 care staff)
   - Large home (120 beds): ~179 staff
   - Medium home (70 beds): ~98 staff

2. Create home in system
3. Create units (e.g., 5 units for 75-bed home)
4. Add staff following the template ratios

---

## 📄 Template Files Reference

### Main Documentation:
- **STAFFING_SETUP_TEMPLATE.md** - Full template with all details

### Demo Script (for developers):
- **simple_template_demo.py** - Python script that created TEMPLATE_DEMO

### Accessibility Fixes (just completed):
- **COLOR_CONTRAST_FIXES_JAN26_2026.md** - WCAG compliance updates

---

## 🔍 Finding Features in Your Current View

If you can't see certain features, check your **role permissions**:

### As Superuser (000541):
✅ Full access to all features
✅ Admin panel
✅ Bulk import
✅ All homes and units

### As Demo Staff (950000-950031):
⚠️ Limited to assigned home (TEMPLATE_DEMO)
⚠️ May not see admin features
⚠️ View own shifts and unit information

---

## 🚀 Quick Navigation Paths

### To See Staffing:
```
Dashboard → Staff Management → View All Staff
```
or
```
Dashboard → Units → Select Unit → View Staff
```

### To See Shifts:
```
Dashboard → Rota → Select Date Range
```
or
```
Dashboard → My Shifts (if logged in as staff)
```

### To Bulk Upload (Superuser only):
```
Admin Panel → Import → Staff CSV Upload
```
or
```
Dashboard → Tools → Bulk Operations → Import Staff
```

---

## 💡 What to Look For in TEMPLATE_DEMO

### Staffing Distribution:
- **Management:** 2 staff (OM + SM)
- **Per Care Unit (5 total):** 6 staff each
  * 1 SSCW (day supervisor)
  * 1 SSCWN (night supervisor)
  * 2 day care workers
  * 2 night care workers

### Shift Patterns:
- **Pattern 1:** 2 shifts/week (24-hour contracts)
- **Pattern 2:** 3 shifts/week (35-hour contracts)
- **Pattern 3:** Mon-Fri 9am-5pm (management)

### Teams:
- Team A, B, C rotating on 3-week cycle

---

## ❓ Still Can't Find It?

### Check Current Page URL:
If you're on login page, you should be redirected to dashboard after login.

**Expected URL after login:**
```
http://127.0.0.1:8000/dashboard/
```
or
```
http://127.0.0.1:8000/
```

### Check Menu Items:
Look for menu items like:
- 📊 Dashboard
- 👥 Staff
- 📅 Rota / Shifts
- 🏥 Units / Homes
- ⚙️ Admin (superuser only)

### If Menu Is Empty:
Your user may not have proper permissions. Try logging in as:
- **Superuser:** 000541 / Greenball99##

---

## 📞 Next Steps

1. **Login** with credentials above
2. **Navigate** to TEMPLATE_DEMO home
3. **Explore** the staff structure (32 staff across 6 units)
4. **Reference** STAFFING_SETUP_TEMPLATE.md for creating new homes
5. **Use CSV** format from template for bulk uploads

The staffing template shows exactly how many staff of each role, their shift patterns, and team assignments. The TEMPLATE_DEMO home is a working example you can explore!

---

**Files Created Today:**
- ✅ STAFFING_SETUP_TEMPLATE.md (comprehensive guide)
- ✅ TEMPLATE_DEMO home (live working example)
- ✅ COLOR_CONTRAST_FIXES_JAN26_2026.md (accessibility)
- ✅ This quick start guide

**Server Status:** Running on http://127.0.0.1:8000/  
**TEMPLATE_DEMO ID:** 23
