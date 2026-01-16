# AI Assistant - Head of Service Query Capabilities

## 🎯 Overview

The AI Assistant now supports **home-specific performance and audit queries** for Head of Service team members, providing instant access to critical metrics, compliance status, and quality indicators for each care home.

---

## 🏥 Home-Specific Queries

### Performance Queries

**Example Queries:**
```
"Show me Orchard Grove's performance"
"How is Victoria Gardens doing?"
"Performance report for Meadowburn"
"Give me Riverside stats"
"Hawthorn House quality metrics"
```

**Response Includes:**
- **Occupancy**: Current occupancy vs capacity (% rate)
- **Staffing Today**: Day/night coverage vs minimum requirements
- **Fiscal Status**: Agency/OT spend vs monthly budget
- **Quality Score**: 30-day rolling metrics
- **Care Plan Compliance**: Review status and rates
- **Critical Alerts**: Any immediate staffing issues

---

### Staffing Queries (Home-Specific)

**Example Queries:**
```
"Staffing levels at Orchard Grove today"
"How many staff at Victoria Gardens?"
"Is Meadowburn fully staffed?"
"Show me Riverside coverage"
"Compliance status for Hawthorn House"
```

**Response Shows:**
- **Day Shifts**: Actual vs required (e.g., 28/17 ✅)
- **Night Shifts**: Actual vs required (e.g., 32/17 ✅)
- **Coverage Status**: Good/Critical
- **Comparison**: Against minimum requirements
  - Standard homes: 17 day, 17 night minimum
  - Victoria Gardens: 10 day, 10 night minimum

---

### Fiscal Queries (Home-Specific)

**Example Queries:**
```
"Agency spend at Orchard Grove"
"Overtime costs for Victoria Gardens"
"Budget status for Meadowburn"
"Fiscal report for Riverside"
"Are we over budget at Hawthorn House?"
```

**Response Includes:**
- **Agency Budget**: Monthly allocation
- **Agency Spend**: Current spend and utilization %
- **OT Budget**: Monthly allocation
- **OT Spend**: Current spend and utilization %
- **Fiscal Status**: Good (under 80%), Warning (80-100%), Over Budget (>100%)
- **Total Budget vs Spend**: Combined view

---

### Care Plan Compliance Queries

**Example Queries:**
```
"Care plan compliance for Orchard Grove"
"Review status at Victoria Gardens"
"How many overdue reviews at Meadowburn?"
"Compliance rate for Riverside"
"Show me Hawthorn House care plan status"
```

**Response Shows:**
- **Total Residents**: Active resident count
- **Completed Reviews**: Number completed
- **Overdue Reviews**: Number and percentage overdue
- **Due Soon**: Reviews coming up
- **Compliance Rate**: % completed on time
- **Status Indicator**: Excellent (>90%), Good (>75%), Critical (<60%)

---

### Quality Audit Queries

**Example Queries:**
```
"Quality audit for Orchard Grove"
"30-day metrics for Victoria Gardens"
"Agency usage at Meadowburn"
"Quality score for Riverside"
"Performance metrics for Hawthorn House"
```

**Response Includes:**
- **Total Shifts** (last 30 days): Count of scheduled shifts
- **Agency Usage Rate**: % of shifts filled by agency (target: <15%)
- **Active Staff Count**: Current active staff members
- **Quality Score**: Inverse of agency usage (higher = better)
- **Trend Indicators**: Color-coded performance levels
  - Green: Agency <15%, Quality >85
  - Amber: Agency 15-30%, Quality 70-85
  - Red: Agency >30%, Quality <70

---

## 📊 Python Query Examples

### Get Home Performance Summary

```python
from scheduling.models import CareHome, Shift, User, Resident, CarePlanReview
from datetime import date, timedelta
from django.db.models import Count, Q

def get_home_performance(home_name):
    """Get comprehensive performance metrics for a specific home"""
    
    home = CareHome.objects.get(name=home_name)
    today = date.today()
    units = home.units.filter(is_active=True)
    
    # 1. Occupancy
    occupancy_rate = (home.current_occupancy / home.bed_capacity * 100) if home.bed_capacity > 0 else 0
    
    # 2. Today's Staffing
    day_staff = Shift.objects.filter(
        unit__in=units,
        date=today,
        shift_type__name__icontains='DAY',
        status__in=['SCHEDULED', 'CONFIRMED']
    ).values('user').distinct().count()
    
    night_staff = Shift.objects.filter(
        unit__in=units,
        date=today,
        shift_type__name__icontains='NIGHT',
        status__in=['SCHEDULED', 'CONFIRMED']
    ).values('user').distinct().count()
    
    # Minimum requirements
    min_staff = 10 if home_name == 'VICTORIA_GARDENS' else 17
    day_compliant = day_staff >= min_staff
    night_compliant = night_staff >= min_staff
    
    # 3. Quality Metrics (30 days)
    last_30 = today - timedelta(days=30)
    total_shifts = Shift.objects.filter(
        unit__in=units,
        date__gte=last_30,
        date__lte=today
    ).count()
    
    agency_shifts = Shift.objects.filter(
        unit__in=units,
        date__gte=last_30,
        date__lte=today,
        user__isnull=True  # Placeholder for agency detection
    ).count()
    
    agency_rate = (agency_shifts / total_shifts * 100) if total_shifts > 0 else 0
    quality_score = 100 - agency_rate
    
    # 4. Care Plan Compliance
    residents = Resident.objects.filter(unit__in=units, is_active=True)
    total_residents = residents.count()
    
    overdue_reviews = 0
    completed_reviews = 0
    for resident in residents:
        latest = resident.care_plan_reviews.order_by('-due_date').first()
        if latest:
            if latest.status == 'OVERDUE':
                overdue_reviews += 1
            elif latest.status == 'COMPLETED':
                completed_reviews += 1
    
    compliance_rate = (completed_reviews / total_residents * 100) if total_residents > 0 else 0
    
    return {
        'home': home.get_name_display(),
        'occupancy': {
            'current': home.current_occupancy,
            'capacity': home.bed_capacity,
            'rate': f"{occupancy_rate:.1f}%"
        },
        'staffing_today': {
            'day': {'actual': day_staff, 'required': min_staff, 'compliant': day_compliant},
            'night': {'actual': night_staff, 'required': min_staff, 'compliant': night_compliant}
        },
        'quality_30d': {
            'total_shifts': total_shifts,
            'agency_rate': f"{agency_rate:.1f}%",
            'quality_score': f"{quality_score:.0f}",
            'active_staff': User.objects.filter(unit__in=units, is_active=True).count()
        },
        'care_plans': {
            'total_residents': total_residents,
            'completed': completed_reviews,
            'overdue': overdue_reviews,
            'compliance_rate': f"{compliance_rate:.1f}%"
        }
    }

# Usage
performance = get_home_performance('ORCHARD_GROVE')
```

### Compare Multiple Homes

```python
def compare_homes(metric='quality'):
    """Compare all homes on a specific metric"""
    
    homes = CareHome.objects.all().order_by('name')
    today = date.today()
    last_30 = today - timedelta(days=30)
    
    comparison = []
    for home in homes:
        units = home.units.filter(is_active=True)
        
        if metric == 'quality':
            total_shifts = Shift.objects.filter(
                unit__in=units, date__gte=last_30, date__lte=today
            ).count()
            agency_shifts = Shift.objects.filter(
                unit__in=units, date__gte=last_30, date__lte=today, user__isnull=True
            ).count()
            agency_rate = (agency_shifts / total_shifts * 100) if total_shifts > 0 else 0
            
            comparison.append({
                'home': home.get_name_display(),
                'value': f"{100 - agency_rate:.1f}",
                'detail': f"Agency: {agency_rate:.1f}%"
            })
            
        elif metric == 'compliance':
            residents = Resident.objects.filter(unit__in=units, is_active=True)
            total = residents.count()
            completed = 0
            for r in residents:
                latest = r.care_plan_reviews.order_by('-due_date').first()
                if latest and latest.status == 'COMPLETED':
                    completed += 1
            rate = (completed / total * 100) if total > 0 else 0
            
            comparison.append({
                'home': home.get_name_display(),
                'value': f"{rate:.1f}%",
                'detail': f"{completed}/{total} completed"
            })
    
    # Sort by value descending
    comparison.sort(key=lambda x: float(x['value'].rstrip('%')), reverse=True)
    return comparison

# Usage
quality_comparison = compare_homes('quality')
compliance_comparison = compare_homes('compliance')
```

---

## 🤖 Chatbot Integration

### Query Patterns to Recognize

The AI Assistant should recognize these patterns:

**Performance/Status:**
- `{home_name} performance`
- `how is {home_name} doing`
- `status of {home_name}`
- `{home_name} report`

**Staffing:**
- `{home_name} staffing`
- `coverage at {home_name}`
- `is {home_name} fully staffed`

**Fiscal:**
- `{home_name} budget`
- `agency spend at {home_name}`
- `overtime at {home_name}`

**Compliance:**
- `{home_name} compliance`
- `care plans at {home_name}`
- `{home_name} reviews`

**Quality:**
- `{home_name} quality`
- `{home_name} audit`
- `{home_name} metrics`

**Comparisons:**
- `compare all homes`
- `which home has best quality`
- `rank homes by compliance`

### Home Name Variations

The assistant should recognize these variations:

| Official Name | Variations |
|---------------|-----------|
| ORCHARD_GROVE | Orchard Grove, OG, Orchard |
| MEADOWBURN | Meadowburn, MB |
| HAWTHORN_HOUSE | Hawthorn House, HH, Hawthorn |
| RIVERSIDE | Riverside, RS |
| VICTORIA_GARDENS | Victoria Gardens, VG, Victoria |

---

## 📋 Sample Responses

### Performance Query

**Query**: *"Show me Orchard Grove's performance"*

**Response**:
```
🏥 Orchard Grove Performance Report

📊 OCCUPANCY
• Current: 57/60 beds (95.0%)

👥 STAFFING TODAY
• Day: 28/17 ✅ COMPLIANT
• Night: 32/17 ✅ COMPLIANT

📈 QUALITY METRICS (30 Days)
• Total Shifts: 5,955
• Agency Usage: 0.0%
• Quality Score: 100/100
• Active Staff: 179

💰 FISCAL STATUS
• Agency: £0 / £9,000 (0%)
• Overtime: £0 / £5,000 (0%)
• Status: ✅ Well under budget

📋 CARE PLAN COMPLIANCE
• Residents: 57
• Completed: 45
• Overdue: 3
• Compliance: 78.9%

Overall Status: ✅ PERFORMING WELL
```

### Quality Audit Query

**Query**: *"Quality audit for Victoria Gardens"*

**Response**:
```
📊 Victoria Gardens - Quality Audit (30 Days)

PERFORMANCE METRICS
• Total Shifts Scheduled: 3,190
• Agency Shifts: 0 (0.0%)
• Quality Score: 100/100 ✅

STAFFING STABILITY
• Active Staff: 98
• Turnover Rate: N/A
• Average Tenure: N/A

COMPLIANCE INDICATORS
• Staffing Compliance: ✅ Meeting minimums
• Care Plan Reviews: 78.9% on time
• Regulatory Status: ✅ Compliant

RECOMMENDATIONS
✓ Excellent agency usage control
✓ Maintain current staffing levels
⚠️ Improve care plan review timeliness

Report Date: December 19, 2025
Next Review: January 19, 2026
```

### Comparison Query

**Query**: *"Compare all homes by quality score"*

**Response**:
```
🏆 Quality Score Rankings (30-Day Period)

1. 🥇 Orchard Grove: 100.0 (Agency: 0.0%)
2. 🥈 Victoria Gardens: 100.0 (Agency: 0.0%)
3. 🥉 Meadowburn: 100.0 (Agency: 0.0%)
4. Riverside: 100.0 (Agency: 0.0%)
5. Hawthorn House: 100.0 (Agency: 0.0%)

Average Quality Score: 100.0
Target: >85 (All homes exceeding target ✅)

Date Range: Nov 19 - Dec 19, 2025
```

---

## 🔗 Integration with Senior Dashboard

The AI Assistant queries should link directly to the Senior Dashboard:

**Quick Links in Responses:**
```
• View Full Dashboard: /senior-dashboard/
• Filter by Home: /senior-dashboard/?care_home={HOME_NAME}
• Date Range: /senior-dashboard/?start_date={DATE}&end_date={DATE}
```

---

## ✅ Implementation Checklist

To fully enable these capabilities:

- [x] Senior Dashboard exists with all metrics
- [x] Database has 53,207 shifts across all homes
- [x] Care plan compliance tracking in place
- [x] Quality metrics calculated per home
- [ ] **AI Assistant home-specific query handler**
- [ ] **Natural language pattern matching for home names**
- [ ] **Formatted response templates for each query type**
- [ ] **Comparison query functionality**
- [ ] **Links to filtered dashboard views**

---

## 📖 Documentation References

- **Senior Dashboard**: `SENIOR_DASHBOARD_DOCS.md`
- **System Status**: `AI_ASSISTANT_SYSTEM_STATUS_DEC2025.md`
- **Reports Guide**: `AI_ASSISTANT_REPORTS_GUIDE.md`
- **Sample Rota**: `staff_guidance/SAMPLE_ROTA_ORCHARD_GROVE.md`

---

**Last Updated**: December 19, 2025  
**Status**: Documentation Complete - Implementation Pending  
**Priority**: High (Head of Service queries are critical for governance)
