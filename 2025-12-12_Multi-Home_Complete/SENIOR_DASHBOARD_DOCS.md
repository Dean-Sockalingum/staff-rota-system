# Senior Management Dashboard
## Multi-Home Oversight System

**Created:** December 12, 2025  
**URL:** `/senior-dashboard/`  
**Purpose:** Aggregated dashboard for senior leadership providing quality assurance, fiscal monitoring, and strategic oversight across all 5 care homes.

---

## 🎯 Purpose & Scope

The Senior Management Dashboard provides executive-level oversight across:
- **Orchard Grove** (60 beds, 9 units)
- **Meadowburn** (45 beds, 9 units)
- **Hawthorn House** (38 beds, 9 units)
- **Riverside** (52 beds, 9 units)
- **Victoria Gardens** (40 beds, 6 units)

**Total:** 235 beds, 42 units, 220 residents (93.6% occupancy)

---

## 📊 Dashboard Sections

### 1. Organization Summary Cards
Real-time KPIs across all homes:
- **Overall Occupancy**: Percentage and bed count
- **Budget Utilization**: Agency + OT spend vs budget
- **Open Alerts**: Critical staffing alerts requiring attention
- **Unfilled Cover Requests**: Active coverage gaps

### 2. Care Home Overview
Per-home occupancy metrics:
- Current occupancy vs capacity
- Occupancy rate percentage
- Active units count
- Physical location

### 3. Today's Staffing Levels
Real-time staffing coverage by home:
- Day shift: Actual vs required
- Night shift: Actual vs required
- Coverage percentages
- Status indicators (Good/Warning/Critical)

### 4. Fiscal Monitoring
Monthly budget tracking by home:
- **Agency Budget**: £9,000/month per home
- **OT Budget**: £5,000/month per home
- Current spend vs budget
- Utilization percentages
- Over-budget alerts

**Budget Thresholds:**
- ✅ Good: <80% utilization
- ⚠️ Warning: 80-100% utilization
- 🚨 Critical: >100% utilization (over budget)

### 5. Critical Staffing Alerts
Oldest 20 alerts across all homes:
- Home and unit identification
- Alert severity (LOW/MEDIUM/HIGH/CRITICAL)
- Date and shift type
- Age in hours (prioritized by oldest)

### 6. Pending Management Actions
Items requiring leadership attention:
- Manual review leave requests (by home)
- Pending staff reallocations
- Unfilled cover requests

### 7. Quality Metrics (30-Day Rolling)
Performance indicators by home:
- Total shifts scheduled
- Agency usage rate (target: <15%)
- Active staff count
- Quality score (inverse of agency usage)

---

## 🔐 Access Control

**Role Requirements:**
- User must be authenticated
- User must have management role (`is_management=True`)
- Currently enforced via decorator check

**Future Enhancement:**
Consider adding specific "senior management" role separate from home managers.

---

## 🗂️ Implementation Files

### 1. View Function
**File:** `scheduling/views_senior_dashboard.py`  
**Function:** `senior_management_dashboard()`

**Key Queries:**
- `CareHome.objects.all()` - All 5 care homes
- `Unit.objects.filter(care_home=home)` - Units per home
- `Shift.objects.filter(date=today)` - Today's shifts
- `AgencyBooking.objects.filter(shift__date__gte=month_start)` - Monthly agency spend
- `StaffingAlert.objects.filter(status__in=['OPEN', 'IN_PROGRESS'])` - Open alerts

**Context Variables:**
```python
{
    'home_overview': [...],          # Per-home capacity
    'staffing_today': [...],          # Today's coverage
    'fiscal_summary': [...],          # Budget tracking
    'critical_alerts': [...],         # Open alerts
    'pending_by_home': {...},         # Leave requests
    'quality_metrics': [...],         # 30-day metrics
}
```

### 2. Template
**File:** `scheduling/templates/scheduling/senior_management_dashboard.html`  
**Base:** Extends `scheduling/base.html`

**Design Features:**
- Responsive grid layout
- Color-coded status indicators
- Progress bars for visual metrics
- Sortable tables
- Executive summary cards

**Color Scheme:**
- ✅ Green (#10b981): Good status
- ⚠️ Amber (#f59e0b): Warning status
- 🚨 Red (#ef4444): Critical status
- 💜 Purple gradient header (#667eea → #764ba2)

### 3. URL Configuration
**File:** `scheduling/urls.py`

```python
from .views_senior_dashboard import senior_management_dashboard

path('senior-dashboard/', senior_management_dashboard, 
     name='senior_management_dashboard'),
```

---

## 📈 Data Aggregation Logic

### Occupancy Calculation
```python
occupancy_rate = (current_occupancy / bed_capacity * 100)
```

### Staff Coverage
```python
day_coverage = (actual_day_shifts / total_required_day * 100)
night_coverage = (actual_night_shifts / total_required_night * 100)
```

### Fiscal Utilization
```python
agency_utilization = (agency_spend / agency_budget * 100)
ot_utilization = (ot_spend / ot_budget * 100)
```

### Quality Score
```python
quality_score = 100 - agency_rate
# Higher score = less agency dependency = better quality
```

---

## 🎨 Status Indicators

### Staffing Status
- **Good**: Day ≥100% AND Night ≥100%
- **Warning**: Day ≥80% AND Night ≥80%
- **Critical**: Below warning thresholds

### Fiscal Status
- **Good**: Agency <80% AND OT <80%
- **Warning**: Agency <100% AND OT <100%
- **Over Budget**: Either exceeds 100%

### Occupancy Status
- **Good**: ≥90%
- **Warning**: 75-89%
- **Critical**: <75%

---

## 🔄 Future Enhancements

### Phase 2 Features
1. **Drill-Down Capability**
   - Click home card → filter to that home's detail view
   - Link to individual home dashboard

2. **Trend Analysis**
   - Week-over-week comparisons
   - Month-over-month budget trends
   - Staff shortage patterns

3. **Export Functionality**
   - PDF reports for board meetings
   - CSV export for analysis
   - Email alerts for critical issues

4. **Predictive Analytics**
   - Forecast budget overruns
   - Predict staffing shortages
   - Suggest reallocation opportunities

5. **Compliance Tracking**
   - Care Inspectorate reports
   - Regulatory violations by home
   - Action item tracking

### Phase 3 Features
1. **Mobile Optimization**
   - Responsive cards for tablet/phone
   - Progressive Web App (PWA)
   - Push notifications for alerts

2. **Real-Time Updates**
   - WebSocket integration
   - Live dashboard refresh
   - Instant alert notifications

3. **Custom Reports**
   - Configurable date ranges
   - Saved report templates
   - Scheduled email reports

---

## 🧪 Testing Recommendations

### Test Cases
1. **Access Control**
   - Non-management users cannot access
   - Redirect to access denied page

2. **Data Accuracy**
   - Verify occupancy calculations
   - Validate budget aggregations
   - Confirm staff count accuracy

3. **Performance**
   - Load time with 24,180 shifts
   - Query optimization for aggregations
   - Caching strategy for expensive queries

4. **Edge Cases**
   - Home with 0 occupancy
   - Budget spend > 200% (extreme overrun)
   - All alerts critical severity
   - No pending actions

---

## 📋 Usage Guidelines

### For Senior Management
1. **Daily Review** (5 minutes)
   - Check overall occupancy
   - Review critical alerts
   - Monitor budget status

2. **Weekly Deep Dive** (15 minutes)
   - Compare homes against each other
   - Identify trends in staffing/fiscal
   - Review quality metrics

3. **Monthly Board Report** (30 minutes)
   - Export fiscal summary
   - Analyze budget utilization
   - Prepare improvement recommendations

### Key Metrics to Monitor
- **Occupancy**: Target ≥90% across all homes
- **Budget**: Target <80% utilization
- **Agency Usage**: Target <15% of total shifts
- **Critical Alerts**: Target <5 open at any time

---

## 🏗️ Architecture Notes

### Separation of Concerns
- **views_senior_dashboard.py**: Isolated from main views.py (6224 lines)
- **Dedicated template**: Specialized layout for executive needs
- **Aggregation logic**: Centralized in view function

### Query Optimization Opportunities
1. Use `select_related()` for FK lookups
2. Cache home list (changes rarely)
3. Consider materialized views for expensive aggregations
4. Index on `shift.date` and `shift.status` fields

### Scalability Considerations
- Current design handles 5 homes efficiently
- If expanding beyond 10 homes, consider:
  - Pagination of home cards
  - Lazy loading of detailed metrics
  - Background jobs for complex aggregations

---

## 📝 Change Log

### Version 1.0 (December 12, 2025)
- ✅ Initial dashboard creation
- ✅ 7 main sections implemented
- ✅ Multi-home aggregation
- ✅ Fiscal monitoring with budget tracking
- ✅ Quality assurance metrics
- ✅ Real-time staffing levels
- ✅ Critical alerts prioritization

### Known Limitations
1. **OT Cost Estimation**: Currently rough estimate (£25/hr × 12hr)
   - Future: Use actual pay rates from staff records
2. **Quality Score**: Simple inverse of agency rate
   - Future: Incorporate incident reports, inspections
3. **Alert Age**: Based on creation time only
   - Future: Track resolution attempts and escalations

---

## 🎓 Business Value

### Strategic Decision Support
- **Reallocation**: Identify homes with surplus/shortage
- **Budget Planning**: Forecast overruns before month-end
- **Quality Focus**: Target homes needing support
- **Risk Mitigation**: Early warning for critical issues

### Compliance & Governance
- **Audit Trail**: All data backed by database records
- **Transparency**: Clear visibility into operations
- **Accountability**: Per-home metrics for managers
- **Regulatory**: Support Care Inspectorate requirements

### Financial Management
- **Cost Control**: Track agency/OT against budget
- **Variance Analysis**: Identify outlier homes
- **Forecasting**: Predict end-of-month spend
- **ROI**: Optimize staff allocation across homes

---

## 🔗 Related Documentation

- `MULTI_HOME_SETUP.md` - Multi-home architecture
- `DATABASE_SCHEMA.md` - CareHome and Unit models
- `ROTA_CORRECTIONS_DEC2025.md` - Data integrity work
- `README.md` - Overall project documentation

---

**Status:** ✅ Production Ready  
**Version:** 1.0  
**Last Updated:** December 12, 2025  
**Next Review:** January 2026 (post-launch feedback)
