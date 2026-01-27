# Leave Usage Targets System - Implementation Complete

## ✅ What's Been Created

### 1. **Management Guide** (`LEAVE_USAGE_TARGETS.md`)
- Complete 40-week strategy explanation
- Traffic light monitoring system (Green/Amber/Red)
- Monthly checkpoint targets
- Manager conversation templates
- 2026 implementation plan
- Success metrics and KPIs

### 2. **Leave Usage Targets Dashboard** (New Feature)
- **URL**: http://127.0.0.1:8000/reports/leave-targets/
- **Access**: Management only
- **Features**:
  - Traffic light status for all staff (✅⚠️🔴)
  - Shows actual vs. expected leave usage
  - Calculates variance (days ahead/behind)
  - Filters by year and unit
  - Sortable table (red status shown first)
  - Links to individual staff records
  - Team-level statistics

### 3. **Staff Guidance Document**
- Located: `docs/staff_guidance/LEAVE_USAGE_TARGETS_GUIDE.md`
- Quick reference for managers
- Conversation templates
- Common issues & solutions
- Implementation checklist

---

## 🎯 The 40-Week Strategy

### Core Principle
Staff should use annual leave **evenly over 40 working weeks** to prevent year-end build-up.

### Targets by Entitlement

| Entitlement | Days/Week | Days/Month |
|-------------|-----------|------------|
| **Full-time (39.67 days)** | ~1.0 day | ~4.3 days |
| **Part-time (35 days)** | ~0.9 day | ~3.8 days |
| **Reduced (30 days)** | ~0.8 day | ~3.3 days |
| **Enhanced (45 days)** | ~1.1 days | ~4.9 days |

**Simple rule**: Take approximately **1 day off per week** for 40 weeks

---

## 📊 Dashboard Features

### Traffic Light System

**✅ Green (On Target)**
- Staff has used ≥90% of expected leave
- No action required

**⚠️ Amber (Slightly Behind)**
- Staff has used 75-90% of expected leave  
- Gentle reminder needed

**🔴 Red (Significantly Behind)**
- Staff has used <75% of expected leave
- Intervention required

### What the Dashboard Shows

For each staff member:
- Total entitlement (days)
- Leave used to date
- Expected usage (based on weeks elapsed)
- Variance (ahead/behind)
- Percentage of target achieved
- Remaining days
- Required weekly rate for rest of year
- Traffic light status
- Quick action links

---

## 🚀 How to Access

### For Managers:

1. **Navigate to Dashboard**:
   - Go to **Reports** in main navigation
   - Click **"Leave Usage Targets"** card
   - Or direct link: http://127.0.0.1:8000/reports/leave-targets/

2. **Filter and View**:
   - Select year (2024-2027)
   - Optionally filter by unit
   - Review staff status (red shown first)
   - Click "View" to see staff details

3. **Take Action**:
   - Green: No action needed
   - Amber: Send reminder
   - Red: Schedule formal discussion

---

## 📅 2026 Implementation Timeline

### January 2026
**Week 1-2**: Launch & Communication
- Introduce 40-week strategy to all staff
- Share management guide
- Set expectations

**Week 3-4**: Baseline Setup
- Review each staff member's 2026 entitlement
- Confirm all data loaded in system
- Initial status check

### February 2026 Onwards
**Monthly Tasks**:
- Review dashboard statistics
- Identify amber/red status staff
- Send reminders via email
- Document actions taken

**Quarterly Reviews**:
- End of March: 33% target checkpoint
- End of June: 65% target checkpoint
- End of September: 98% target checkpoint
- December: Year-end review

---

## 📈 Expected Outcomes

### By Implementation:

✅ **Immediate Benefits**:
- Clear visibility of leave usage across team
- Data-driven approach to leave management
- Early warning system for problems
- Consistent monitoring framework

✅ **Q2 2026 Goals**:
- 80%+ of staff in green status
- Fewer urgent leave requests
- Better service coverage planning
- Reduced manager workload

✅ **Year-End 2026 Goals**:
- 95%+ staff use full entitlement
- <10% require carryover
- No year-end leave rush
- Improved staff wellbeing

---

## 💡 Quick Tips for Managers

### Monthly Review (5 minutes)
1. Open Leave Usage Targets dashboard
2. Check red status count
3. Review amber status staff
4. Send reminders to those behind target

### Quarterly Deep Dive (30 minutes)
1. Review all staff individually
2. Schedule discussions with red status staff
3. Update team coverage plans
4. Adjust strategies if needed

### Using the AI Assistant
- "How much leave does [name] have remaining?"
- "Search for staff in [unit]"
- Get instant leave balances without opening dashboard

---

## 📚 Documentation Files

1. **`LEAVE_USAGE_TARGETS.md`**
   - Full management guide (450+ lines)
   - Detailed strategies and templates
   - Implementation plan

2. **`docs/staff_guidance/LEAVE_USAGE_TARGETS_GUIDE.md`**
   - Quick reference guide
   - Viewable in Staff Guidance section
   - Printable for managers

3. **Dashboard Template**
   - `scheduling/templates/scheduling/leave_usage_targets.html`
   - Responsive design
   - Real-time calculations

4. **View Function**
   - `scheduling/views.py` → `leave_usage_targets()`
   - Processes entitlements
   - Calculates targets and status
   - Applies traffic light rules

---

## 🔧 Technical Details

### URL Pattern
```
/reports/leave-targets/
```

### URL Parameters
- `?year=2026` - Filter by year
- `?unit=ROSE` - Filter by unit
- Combine: `?year=2026&unit=ROSE`

### Permissions
- Management access only
- Checks `request.user.role.is_management`
- Redirects staff to staff dashboard

### Data Source
- `staff_records.models.AnnualLeaveEntitlement`
- Filters by `leave_year_start__year`
- Calculates expected usage based on weeks elapsed
- Applies 40-week formula

### Traffic Light Logic
```python
if percent_of_expected >= 90:
    status = 'green'  # On target
elif percent_of_expected >= 75:
    status = 'amber'  # Slightly behind
else:
    status = 'red'    # Significantly behind
```

---

## ✅ Testing Checklist

- [x] View created and working
- [x] URL added to routing
- [x] Template created with styling
- [x] Dashboard card added to Reports
- [x] Management guide written
- [x] Staff guidance document created
- [x] Traffic light calculation tested
- [x] Filtering by year works
- [x] Filtering by unit works
- [x] Table sorting (red first) works
- [x] Links to staff records work
- [x] Statistics calculated correctly
- [x] Responsive design confirmed

---

## 🎉 System Ready!

The Leave Usage Targets system is **fully implemented and ready for use**!

### Next Steps:

1. **Test the dashboard**:
   - Navigate to Reports → Leave Usage Targets
   - Try different years and unit filters
   - Verify calculations are correct

2. **Review documentation**:
   - Read LEAVE_USAGE_TARGETS.md
   - Share with management team
   - Plan 2026 rollout

3. **Prepare for 2026**:
   - Ensure all 2026 entitlements loaded
   - Communicate strategy to staff
   - Set calendar reminders for quarterly reviews

**Dashboard URL**: http://127.0.0.1:8000/reports/leave-targets/

**Guide Location**: LEAVE_USAGE_TARGETS.md

**Staff Guidance**: Reports → Staff Guidance → Leave Usage Targets Guide

---

*System implemented: November 29, 2025*  
*Ready for production use: January 2026*
