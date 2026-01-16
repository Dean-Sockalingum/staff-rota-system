# Multi-Home Care Management Setup

**Date**: December 12, 2025  
**Status**: Phase 1 Complete - 5 Homes Initialized

## Overview

Successfully initialized 5 care homes in the system to support multi-home operations with centralized senior management oversight.

## Care Homes Created

### 1. **Orchard Grove** (Main Home)
- **Location**: 123 Orchard Grove, Edinburgh EH12 7XY
- **Capacity**: 60 beds (57 occupied - 95.0%)
- **Care Inspectorate ID**: CS2023012345
- **Registration**: REG-2023-OG
- **Current Status**: Fully operational with 8 active units
- **Units Assigned**: 
  - DEMENTIA
  - BLUE
  - GREEN  
  - ROSE
  - VIOLET
  - ORANGE
  - PEACH
  - GRAPE
  - MGMT (Management)

### 2. **Meadowburn**
- **Location**: 45 Meadowburn Road, Glasgow G12 9QQ
- **Capacity**: 45 beds (42 occupied - 93.3%)
- **Care Inspectorate ID**: CS2023012346
- **Registration**: REG-2023-MB
- **Current Status**: Home record created, units not yet assigned
- **Focus**: Residential care with respite and long-term care

### 3. **Hawthorn House**
- **Location**: 78 Hawthorn Lane, Aberdeen AB10 1XX
- **Capacity**: 38 beds (35 occupied - 92.1%)
- **Care Inspectorate ID**: CS2023012347
- **Registration**: REG-2023-HH
- **Current Status**: Home record created, units not yet assigned
- **Focus**: Smaller residential home with palliative care

### 4. **Riverside**
- **Location**: 91 Riverside Drive, Dundee DD1 4HH
- **Capacity**: 52 beds (48 occupied - 92.3%)
- **Care Inspectorate ID**: CS2023012348
- **Registration**: REG-2023-RS
- **Current Status**: Home record created, units not yet assigned
- **Focus**: Physical disability support

### 5. **Victoria Gardens**
- **Location**: 156 Victoria Gardens, Perth PH1 5LU
- **Capacity**: 40 beds (38 occupied - 95.0%)
- **Care Inspectorate ID**: CS2023012349
- **Registration**: REG-2023-VG
- **Current Status**: Home record created, units not yet assigned
- **Focus**: Learning disability support

## Organization-Wide Statistics

- **Total Capacity**: 235 beds across 5 homes
- **Total Occupancy**: 220 residents
- **Overall Occupancy Rate**: 93.6%
- **Active Units**: 9 (all currently assigned to Orchard Grove)
- **Total Staff**: 181 users

## Current System Architecture

### Database Models

**CareHome Model** (`scheduling/models_multi_home.py`)
- ✅ Tracks individual care home details
- ✅ Capacity and occupancy management
- ✅ Location and regulatory information
- ✅ Financial budgets (agency/overtime)
- ✅ Home manager assignment capability

### Current Dashboard Structure

**Manager Dashboard** (`/dashboard/`)
- Single-home view
- Widgets:
  - Manual review required (leave requests)
  - Staff reallocations needed
  - Today's staffing snapshot
  - Coverage summary for rota period

**Staff Dashboard** (`/my-rota/`)
- Individual staff member view
- Shift schedules
- Leave requests
- Shift swap functionality

**Specialized Dashboards**
- Reports Dashboard (`/reports/`)
- Leave Approval Dashboard (`/leave-approvals/`)
- Audit Dashboard (`/audit/`)
- Compliance Dashboard (`/audit/compliance/`)
- Care Plan Manager Dashboard (link needed)
- Staffing Dashboard (`/staffing/dashboard/`)

## Next Steps

### 1. Unit-to-Home Assignment (Priority: HIGH)

**Current Limitation**: The `Unit` model doesn't have a `care_home` foreign key field.

**Required Actions**:
1. Create migration to add `care_home` field to `Unit` model
2. Default all existing units (DEMENTIA, BLUE, GREEN, etc.) to Orchard Grove
3. Create units for the other 4 homes
4. Update models to filter by care_home where appropriate

**Recommended Unit Structure** per home (example):
```python
# Meadowburn (45 beds)
- GROUND_FLOOR (22 beds)
- FIRST_FLOOR (23 beds)

# Hawthorn House (38 beds)  
- MAIN_WING (20 beds)
- WEST_WING (18 beds)

# Riverside (52 beds)
- NORTH_UNIT (26 beds)
- SOUTH_UNIT (26 beds)

# Victoria Gardens (40 beds)
- EAST_WING (20 beds)
- WEST_WING (20 beds)
```

### 2. Senior Management Dashboard (Priority: HIGH)

**Requirements**:
- Aggregated view across all 5 homes
- Key metrics:
  - Overall occupancy rates by home
  - Staff shortage alerts across homes
  - Budget status (agency/OT spend by home)
  - Cross-home reallocation opportunities
  - Compliance violations by home
  - Today's staffing levels by home
  
**Suggested URL**: `/senior-dashboard/` or `/multi-home-dashboard/`

**Access Control**: Restrict to senior management roles (Operations Director, Regional Manager, etc.)

### 3. Home-Specific Manager Dashboards (Priority: MEDIUM)

**Enhancement Needed**: Current manager dashboard should be scoped to specific home

**Proposed Changes**:
1. Add home selector/filter to existing dashboard
2. Allow home managers to only see their home
3. Allow senior management to view all homes
4. Add breadcrumb navigation (All Homes → Orchard Grove → BLUE Unit)

### 4. Staff Assignment to Homes (Priority: MEDIUM)

**Current**: Staff assigned to Units only  
**Needed**: Staff primary home assignment

**Options**:
a) Infer from `home_unit` field (already exists in User model)
b) Add explicit `primary_care_home` field
c) Use `home_unit.care_home` relationship (requires step 1)

### 5. Cross-Home Reallocation (Priority: LOW)

**Future Enhancement**: Enable staff reallocation between care homes

**Considerations**:
- Travel time/distance between homes
- Staff willingness to work at multiple locations
- Different rates of pay per home
- Training/competency requirements per home

## Files Created/Modified

### Management Commands
- ✅ `/scheduling/management/commands/initialize_care_homes.py`
  - Creates 5 care home records
  - Sets capacity, occupancy, location
  - Configures regulatory IDs
  - Usage: `python3 manage.py initialize_care_homes [--reset]`

### Documentation
- ✅ `ROTA_CORRECTIONS_DEC2025.md` - Documents recent shift corrections
- ✅ `MULTI_HOME_SETUP.md` (this file) - Multi-home initialization guide

### Models
- ✅ `scheduling/models_multi_home.py` - CareHome model (existing)

### Templates (Needed)
- ⚠️ Senior management dashboard template (not yet created)
- ⚠️ Multi-home selector component (not yet created)

### Views (Needed)
- ⚠️ `senior_management_dashboard` view function
- ⚠️ Home filtering logic for existing dashboards

## Recommended Implementation Order

1. **Week 1: Database Schema**
   - Add `care_home` FK to Unit model
   - Create migration
   - Assign existing units to Orchard Grove
   - Create units for other 4 homes

2. **Week 2: Home-Specific Views**
   - Add home filtering to manager dashboard
   - Update unit queries to respect care_home
   - Add home selector UI component
   - Test with Orchard Grove data

3. **Week 3: Senior Dashboard**
   - Create senior_management_dashboard view
   - Build aggregated metrics queries
   - Design multi-home overview template
   - Add cross-home comparison charts

4. **Week 4: Staff Assignment**
   - Review home_unit field usage
   - Add staff-home relationship logic
   - Update staff search/allocation to consider home
   - Test cross-home scenarios

## Testing Considerations

- Verify all existing functionality with Orchard Grove
- Test home filtering doesn't break existing workflows
- Ensure data isolation between homes
- Validate cross-home aggregations
- Test role-based access (home managers vs senior management)

## Security & Access Control

**Role Levels**:
1. **Staff**: See own data only
2. **Home Manager**: See single home data
3. **Operations Manager**: See all homes
4. **Senior Management**: See all homes with strategic view
5. **Admin**: Full access

**Current Limitation**: No home-based permission filtering yet

## Budget Configuration

All homes initialized with default budgets:
- **Agency Budget**: £9,000/month per home
- **Overtime Budget**: £5,000/month per home
- **Total Monthly Budget**: £70,000 (£14,000 × 5 homes)

These can be adjusted per home via Django admin or management commands.

## Data Integrity

All 5 homes created in a single atomic transaction. If creation fails, no partial data is left in the database.

## Support & Maintenance

For questions or issues:
1. Check this document first
2. Review `scheduling/models_multi_home.py` for model structure
3. Run `python3 manage.py initialize_care_homes --reset` to recreate homes
4. Check Care Inspectorate IDs are unique

---

**Last Updated**: December 12, 2025  
**Author**: System  
**Status**: ✅ Phase 1 Complete - Ready for Phase 2 (Unit Assignment)
