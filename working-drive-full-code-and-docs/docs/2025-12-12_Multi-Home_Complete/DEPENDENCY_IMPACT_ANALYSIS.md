# Dependency Impact Analysis
**Date:** January 5, 2026  
**Status:** ✅ BOTH PACKAGES INSTALLED

---

## Installation Status

### ✅ WeasyPrint - INSTALLED
- **Purpose:** PDF export functionality for reports and cost analysis
- **Installation:** Completed successfully
- **Status:** Ready to use

### ✅ Elasticsearch - INSTALLED
- **Purpose:** Full-text search across staff, shifts, leave requests, and care homes
- **Components Installed:**
  - `elasticsearch` - Python client library
  - `elasticsearch-dsl` - Django integration (DSL = Domain Specific Language)
- **Status:** Client libraries installed
- **Note:** Requires Elasticsearch server running for full functionality

---

## Impacted Views & Features

### 1️⃣ Analytics Views (analytics.py Classes MISSING)

**File:** `scheduling/views_analytics.py`

#### COMMENTED OUT IMPORTS (Lines 20-27):
```python
# from .analytics import (
#     StaffPerformanceAnalytics,
#     UnitAnalytics,
#     CareHomeAnalytics,
#     TrendAnalytics,
#     PredictiveAnalytics,
#     DashboardAggregator
# )
```

**PROBLEM:** These classes **DO NOT EXIST** in `analytics.py`
- `analytics.py` only contains **standalone functions**, not classes
- Views expect class-based API (e.g., `DashboardAggregator.get_executive_dashboard()`)
- Current `analytics.py` provides: `get_dashboard_summary()`, `calculate_*()` functions

#### BROKEN VIEWS (Cannot Load):

| View Function | Line | Uses Missing Class | Impact |
|---------------|------|-------------------|--------|
| `executive_dashboard()` | 48 | `DashboardAggregator.get_executive_dashboard()` | ❌ BROKEN |
| `executive_dashboard()` | 51 | `TrendAnalytics.get_weekly_shift_trends()` | ❌ BROKEN |
| `manager_dashboard()` | 94 | `DashboardAggregator.get_manager_dashboard()` | ❌ BROKEN |
| `staff_performance_view()` | 126 | `StaffPerformanceAnalytics.get_staff_attendance_rate()` | ❌ BROKEN |
| `staff_performance_view()` | 130 | `StaffPerformanceAnalytics.get_staff_punctuality_score()` | ❌ BROKEN |
| `staff_performance_view()` | 134 | `StaffPerformanceAnalytics.get_staff_overtime_hours()` | ❌ BROKEN |
| `staff_performance_view()` | 138 | `StaffPerformanceAnalytics.get_staff_leave_summary()` | ❌ BROKEN |
| `unit_analytics_view()` | 172 | `UnitAnalytics.get_unit_staffing_levels()` | ❌ BROKEN |
| `unit_analytics_view()` | 176 | `UnitAnalytics.get_unit_shift_coverage()` | ❌ BROKEN |
| `unit_analytics_view()` | 181 | `PredictiveAnalytics.predict_staffing_needs()` | ❌ BROKEN |
| `api_dashboard_summary()` | 288 | `DashboardAggregator.get_executive_dashboard()` | ❌ BROKEN |

#### AFFECTED URLS:
- `/analytics/executive-dashboard/` - ❌ Executive Dashboard
- `/analytics/manager-dashboard/` - ❌ Manager Dashboard  
- `/analytics/staff-performance/<sap>/` - ❌ Individual Staff Performance
- `/analytics/unit/<unit_id>/` - ❌ Unit Analytics
- `/api/analytics/dashboard/` - ❌ Dashboard API

**ROOT CAUSE:** Expected analytics classes were never implemented. Current `analytics.py` provides different function-based API.

---

### 2️⃣ PDF Export Views (WeasyPrint NOW INSTALLED ✅)

**File:** `scheduling/views_cost_analysis.py` (Line 22)

#### BEFORE:
```python
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError as e:
    WEASYPRINT_AVAILABLE = False
    print(f"WeasyPrint not available in views_cost_analysis: {e}")
```

#### STATUS: ✅ NOW WORKS
- WeasyPrint successfully installed
- PDF export functionality now available

#### AFFECTED FEATURES:
| Feature | Status | Notes |
|---------|--------|-------|
| Cost Analysis PDF Export | ✅ NOW WORKS | `views_cost_analysis.py` |
| Report PDF Export | ✅ NOW WORKS | `utils/exports.py` |

---

### 3️⃣ Search Views (Elasticsearch - PARTIAL)

**Files:** 
- `scheduling/documents.py` (Elasticsearch document definitions)
- `scheduling/views_search.py` (Search views)

#### INSTALLED:
- ✅ `elasticsearch` - Python client
- ✅ `elasticsearch_dsl` - Django integration
- ✅ `django_elasticsearch_dsl` - Document indexing

#### STILL REQUIRED:
- ⚠️ **Elasticsearch Server** - Not running
  - Need to install Elasticsearch server (via Homebrew or Docker)
  - Default: `http://localhost:9200`
  - Without server: Search features will fail with connection errors

#### AFFECTED FEATURES:

| Feature | File | Status | Notes |
|---------|------|--------|-------|
| Staff Search (Full-Text) | `views_search.py` | ⚠️ REQUIRES SERVER | UserDocument indexed |
| Shift Search | `views_search.py` | ⚠️ REQUIRES SERVER | ShiftDocument indexed |
| Leave Request Search | `views_search.py` | ⚠️ REQUIRES SERVER | LeaveRequestDocument indexed |
| Care Home Search | `views_search.py` | ⚠️ REQUIRES SERVER | CareHomeDocument indexed |
| Autocomplete | `views_search.py` | ⚠️ REQUIRES SERVER | Multi-field matching |

#### DEFINED DOCUMENTS:
```python
# scheduling/documents.py
@registry.register_document
class UserDocument(Document):  # Staff search with role, care home
@registry.register_document  
class ShiftDocument(Document):  # Shift search with staff, dates, types
@registry.register_document
class LeaveRequestDocument(Document):  # Leave search with status, dates
@registry.register_document
class CareHomeDocument(Document):  # Care home search
```

**URL:** `/search/` (Task 49: Advanced Search with Elasticsearch)

---

## Summary of Impacts

### ✅ FIXED (WeasyPrint Installed)
- **PDF Exports:** Cost analysis PDFs, report exports now work
- **Files Affected:** 2
  - `scheduling/views_cost_analysis.py`
  - `scheduling/utils/exports.py`

### ⚠️ PARTIAL (Elasticsearch Client Installed, Server Needed)
- **Search Features:** Client ready, but needs Elasticsearch server running
- **Files Affected:** 2
  - `scheduling/documents.py` (4 document types defined)
  - `scheduling/views_search.py` (search views ready)
- **Action Needed:** Install Elasticsearch server
  ```bash
  brew install elasticsearch
  brew services start elasticsearch
  ```

### ❌ BROKEN (Missing Analytics Classes)
- **Analytics Views:** 11 view functions broken, classes never implemented
- **Files Affected:** 1
  - `scheduling/views_analytics.py` (5 views, 4 API endpoints)
- **Root Cause:** Mismatch between expected class-based API vs actual function-based implementation
- **Action Needed:** Either:
  1. **Option A:** Refactor `analytics.py` to provide class-based API (6 classes needed)
  2. **Option B:** Refactor `views_analytics.py` to use existing functions from `analytics.py`
  3. **Option C:** Disable analytics URLs until classes implemented

---

## Recommendations

### Immediate Actions

#### 1. Install Elasticsearch Server (Optional - Only if search needed)
```bash
# Install via Homebrew
brew install elasticsearch

# Start service
brew services start elasticsearch

# Verify running
curl http://localhost:9200

# Index Django models
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
python3 manage.py search_index --rebuild
```

#### 2. Fix Analytics Views (CRITICAL - Blocks 5 Views)

**Option A: Quick Fix - Use Existing Functions**
Replace class calls with function calls in `views_analytics.py`:

```python
# Change from:
dashboard_data = DashboardAggregator.get_executive_dashboard(care_home)

# To:
from .analytics import get_dashboard_summary
dashboard_data = get_dashboard_summary(care_home=care_home)
```

**Option B: Implement Missing Classes**
Create class wrappers in `analytics.py`:

```python
class DashboardAggregator:
    @staticmethod
    def get_executive_dashboard(care_home=None):
        return get_dashboard_summary(care_home=care_home, date_range='month')
    
    @staticmethod
    def get_manager_dashboard(care_home):
        return get_dashboard_summary(care_home=care_home, date_range='week')

class StaffPerformanceAnalytics:
    @staticmethod
    def get_staff_attendance_rate(staff, start_date, end_date):
        # Implementation needed
        pass
    
    # ... etc for 5 more classes
```

**Option C: Disable Analytics URLs**
Comment out broken analytics URLs in `urls.py` until fixed.

---

## HSCP Demo Impact

### CAN DEMONSTRATE (Working):
- ✅ Core scheduling (shift management, leave approval)
- ✅ Compliance Dashboard (Task 56)
- ✅ Activity Feed (Task 55)
- ✅ Leave Calendar (Task 59)
- ✅ AI Assistant (natural language queries)
- ✅ **PDF Exports** (NOW WORKING with WeasyPrint)
- ✅ Basic analytics (if using function-based APIs directly)

### AVOID IN DEMO (Broken):
- ❌ Executive Dashboard (`/analytics/executive-dashboard/`)
- ❌ Manager Dashboard (`/analytics/manager-dashboard/`)
- ❌ Staff Performance View
- ❌ Unit Analytics View
- ❌ Advanced Search (Elasticsearch server not running)

### WORKAROUND FOR DEMO:
- Focus on **operational features** (scheduling, compliance, leave)
- Show **AI Assistant** for analytics queries instead of broken dashboards
- Mention analytics as "in development" if asked

---

## Updated Todo List Priority

### NEW HIGH PRIORITY:
- **Fix Analytics Views** - 11 broken functions blocking 5 URLs (CRITICAL for demo)
  - Time: 2-3 hours (Option A) or 6-8 hours (Option B)
  - Impact: Enables executive/manager dashboards for HSCP demo

### OPTIONAL (Demo Not Affected):
- **Install Elasticsearch Server** - Search features nice-to-have, not critical
  - Time: 30 minutes
  - Impact: Enables advanced search (Task 49)

### COMPLETED:
- ✅ **WeasyPrint Installation** - PDF exports now work
- ✅ **Elasticsearch Client Installation** - Ready for server connection

---

## Next Steps

1. **Decide on Analytics Fix Strategy:**
   - Quick fix (Option A): Refactor views to use existing functions
   - Complete fix (Option B): Implement missing classes
   - Defer (Option C): Comment out analytics URLs

2. **Elasticsearch Server Decision:**
   - Install now if search demo needed
   - Skip if focusing on core scheduling for HSCP demo

3. **Update HSCP Demo Checklist:**
   - Mark PDF exports as ✅ WORKING
   - Mark advanced search as ⚠️ REQUIRES SERVER
   - Mark analytics dashboards as ❌ BROKEN (unless fixed)

4. **Test After Fixes:**
   - Verify PDF export works
   - Test analytics views if refactored
   - Test search if server installed

---

**Files Updated This Session:**
- ✅ System Python packages: `weasyprint`, `elasticsearch`, `elasticsearch-dsl`
- ✅ Ready for testing: PDF exports
- ⏳ Pending: Analytics class implementation or refactoring
- ⏳ Pending: Elasticsearch server installation (optional)
