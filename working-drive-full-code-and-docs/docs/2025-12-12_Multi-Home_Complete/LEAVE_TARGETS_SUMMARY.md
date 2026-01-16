# ✅ Leave Usage Targets System - COMPLETE

## What You Asked For

> "I would like to create a guide that supports managers by setting a target and a view of how far off or behind target the leave is"

## What's Been Delivered

### 1. 📊 **Interactive Dashboard** 
**URL**: `/reports/leave-targets/`

Shows managers at a glance:
- ✅ Who's on target (Green)
- ⚠️ Who's slightly behind (Amber)  
- 🔴 Who's significantly behind (Red)
- Exact days ahead/behind target
- Required usage rate for rest of year

### 2. 🎯 **The 40-Week Target**
Based on your question about what target would use all leave in 40 weeks:

| Entitlement | Weekly Target | Monthly Target |
|-------------|---------------|----------------|
| 40 days | **~1.0 day/week** | **~4.3 days/month** |
| 35 days | **~0.9 day/week** | **~3.8 days/month** |
| 30 days | **~0.8 day/week** | **~3.3 days/month** |

**Simple rule**: Staff should take approximately **1 day off per week** over 40 working weeks

### 3. 📋 **Management Guide** (`LEAVE_USAGE_TARGETS.md`)
- Complete strategy documentation
- Traffic light monitoring system
- Quarterly checkpoint targets
- Manager conversation templates
- 2026 implementation plan

### 4. 📖 **Staff Guidance Document**
- Quick reference for managers
- Common issues & solutions
- Implementation checklist
- Accessible via Staff Guidance menu

---

## How It Works

### Traffic Light System

**✅ GREEN** = On Target (≥90% of expected)
- No action needed
- Staff is using leave regularly

**⚠️ AMBER** = Slightly Behind (75-90% of expected)
- Send gentle reminder
- Check if leave is planned

**🔴 RED** = Significantly Behind (<75% of expected)
- **Action required**
- Schedule formal discussion
- Mandatory leave booking

### Expected Usage by Quarter

For full-time staff (40 days):

| Quarter | Weeks | Expected Days | % of Total |
|---------|-------|---------------|------------|
| **Q1** (End of March) | 13 | 13 days | 33% |
| **Q2** (End of June) | 26 | 26 days | 65% |
| **Q3** (End of September) | 39 | 39 days | 98% |
| **Q4** (End of December) | 52 | 40 days | 100% |

---

## Access the Dashboard

### Option 1: Via Reports Menu
1. Click **Reports** in navigation
2. Find **"Leave Usage Targets"** card (with 🎯 icon)
3. Click **"View Dashboard"**

### Option 2: Direct URL
```
http://127.0.0.1:8000/reports/leave-targets/
```

### Features:
- Filter by year (2024-2027)
- Filter by unit
- Sort by status (red shown first)
- Click staff name to view full record
- See team totals and statistics

---

## Example: What You'll See

```
Staff Member: John Smith
SAP: SCA1041
Entitlement: 39.7 days
Used: 15.0 days (by Week 26 - end of June)
Expected: 25.9 days
Variance: -10.9 days ⚠️
Status: AMBER - Slightly Behind (58% of target)
Action: Send reminder about leave plans
```

vs.

```
Staff Member: Sarah Jones  
SAP: SCA1052
Entitlement: 39.7 days
Used: 27.0 days (by Week 26)
Expected: 25.9 days
Variance: +1.1 days ✅
Status: GREEN - On Target (104% of target)
Action: None needed
```

---

## 2026 Implementation Plan

### January 2026 - Launch
✅ Week 1-2: Communicate 40-week strategy to all staff
✅ Week 3-4: Review entitlements and set baseline

### Throughout 2026 - Monitor
✅ **Monthly**: Review dashboard, identify issues
✅ **Quarterly**: Formal checkpoint reviews
✅ **Ongoing**: Send reminders to amber/red staff

### Quarterly Checkpoints:
- **End of March**: Target 33% used (~13 days)
- **End of June**: Target 65% used (~26 days)
- **End of September**: Target 98% used (~39 days)

---

## Manager Quick Actions

### Monthly Review (5 minutes)
```
1. Open /reports/leave-targets/
2. Check status summary (how many red/amber)
3. Email any red status staff
4. Note amber status staff for next month
```

### Quarterly Deep Dive (30 minutes)
```
1. Review each staff member individually
2. Schedule 1-on-1 with red status staff
3. Update team coverage plans
4. Document actions taken
```

### Using AI Assistant
```
Ask: "How much leave does ADMIN001 have remaining?"
Get: Instant leave balance with urgency level
```

---

## Files Created

1. **`LEAVE_USAGE_TARGETS.md`** - Full management guide (450+ lines)
2. **`LEAVE_TARGETS_IMPLEMENTATION.md`** - This summary
3. **`docs/staff_guidance/LEAVE_USAGE_TARGETS_GUIDE.md`** - Quick reference
4. **Dashboard View** - `scheduling/views.py::leave_usage_targets()`
5. **Dashboard Template** - `scheduling/templates/scheduling/leave_usage_targets.html`
6. **URL Route** - `/reports/leave-targets/`

---

## Success Metrics for 2026

By implementing this system, you should achieve:

✅ **80%+ of staff in green status by June 2026**
✅ **90%+ of staff in green status by September 2026**  
✅ **95%+ staff use full entitlement by year-end**
✅ **<10% require carryover to 2027**
✅ **No year-end leave rush**
✅ **Better staff wellbeing** (regular breaks)
✅ **Predictable service coverage**

---

## Quick Reference Card

**THE NUMBERS:**
- Target: ~1 day/week over 40 weeks
- Or: ~4-5 days/month consistently
- Traffic Light (June): Green = 55-75% used, Amber = 40-55%, Red = <40%

**MANAGER TASKS:**
- [ ] Monthly dashboard review
- [ ] Email amber status staff
- [ ] Meet with red status staff  
- [ ] Quarterly checkpoint reviews

**DASHBOARD:**
- Access: Reports → Leave Usage Targets
- Filters: Year, Unit
- Shows: Status, variance, targets
- Action: View staff details, send reminders

---

## 🎉 System Ready!

Everything is **fully implemented and ready to use** for 2026 onwards!

**Next Steps:**
1. ✅ Test dashboard with 2025 data
2. ✅ Review documentation
3. ✅ Prepare 2026 entitlements
4. ✅ Communicate strategy to staff in January 2026

**Dashboard**: http://127.0.0.1:8000/reports/leave-targets/  
**Guide**: LEAVE_USAGE_TARGETS.md  
**Quick Ref**: Staff Guidance → Leave Usage Targets Guide

---

*Created: November 29, 2025*  
*Ready for production: January 2026*  
*Target: Prevent year-end leave build-up through 40-week strategy*
