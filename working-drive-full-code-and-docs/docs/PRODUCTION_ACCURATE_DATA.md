# Production-Accurate Data for Demo Deployment
**Source:** Academic Paper v1.md + PRODUCTION_READINESS_REVIEW_DEC2025.md + User-provided shift schedules
**Date:** January 8, 2026
**Purpose:** Authoritative reference for setting up demo.therota.co.uk with accurate capacities, staffing, and unit structures

---

## Shift Schedule Configuration

### Standard Shift Types (3 Total)

1. **Day Shift**
   - **Hours:** 08:00 - 20:00 (12 hours)
   - **Roles:** SCA, SCW, SSCW
   - **Applicable to:** All care units
   - **Break entitlement:** 1 hour unpaid lunch + 2×15min paid breaks

2. **Night Shift**
   - **Hours:** 20:00 - 08:00 (12 hours)
   - **Roles:** SCA, SCW, SSCW
   - **Applicable to:** All care units
   - **Break entitlement:** 1 hour unpaid meal break + 2×15min paid breaks

3. **Management Shift**
   - **Hours:** 09:00 - 17:00 (8 hours)
   - **Roles:** OM, SM, Admin, HR
   - **Applicable to:** MGMT units only
   - **Break entitlement:** 1 hour unpaid lunch

**Note:** No twilight, long day, or sleep-in shifts in production system.

---

## Care Homes Configuration

### 1. Orchard Grove
- **Code:** `ORCHARD_GROVE`
- **Bed Capacity:** 60 beds
- **Occupancy:** 95% (57 residents)
- **Location:** Maryhill, Glasgow
- **Care Inspectorate ID:** CS2014333831
- **Units (8 + MGMT):**
  1. Bramley (fruit-themed)
  2. Cherry
  3. Grape
  4. Orange
  5. Peach
  6. Pear
  7. Plum
  8. Strawberry
  9. MGMT (Management unit)
- **Total Capacity:** 120 beds (8 units × 15 beds)
- **Theme:** Fruit names

### 2. Meadowburn House
- **Code:** `MEADOWBURN`
- **Bed Capacity:** 45 beds
- **Occupancy:** 93.3% (42 residents)
- **Location:** Glasgow
- **Care Inspectorate ID:** CS2018371804
- **Units (8 + MGMT):**
  1. Aster (flower-themed)
  2. Bluebell
  3. Cornflower
  4. Daisy
  5. Foxglove
  6. Honeysuckle
  7. Marigold
  8. Poppy SRD (Short-term Residential Dementia)
  9. MGMT
- **Total Capacity:** 120 beds (8 units × 15 beds)
- **Theme:** Flower names

### 3. Hawthorn House
- **Code:** `HAWTHORN_HOUSE`
- **Bed Capacity:** 38 beds
- **Occupancy:** 92.1% (35 residents)
- **Location:** Glasgow
- **Care Inspectorate ID:** CS2003001025
- **Units (8 + MGMT):**
  1. Bluebell (flower-themed)
  2. Daisy
  3. Heather
  4. Iris
  5. Primrose
  6. Snowdrop SRD (Short-term Residential Dementia)
  7. Thistle SRD
  8. Violet
  9. MGMT
- **Total Capacity:** 120 beds (8 units × 15 beds)
- **Theme:** Flower names

### 4. Riverside
- **Code:** `RIVERSIDE`
- **Bed Capacity:** 52 beds
- **Occupancy:** 92.3% (48 residents)
- **Location:** Govan, Glasgow
- **Care Inspectorate ID:** CS2014333834
- **Units (8 + MGMT):**
  1. Daffodil (flower-themed)
  2. Heather
  3. Jasmine
  4. Lily
  5. Lotus
  6. Maple
  7. Orchid
  8. Rose
  9. MGMT
- **Total Capacity:** 120 beds (8 units × 15 beds)
- **Theme:** Flower names

### 5. Victoria Gardens
- **Code:** `VICTORIA_GARDENS`
- **Bed Capacity:** 40 beds
- **Occupancy:** 95% (38 residents)
- **Location:** Partick, Glasgow
- **Care Inspectorate ID:** CS2018371437
- **Units (5 + MGMT):**
  1. Azalea (flower-themed)
  2. Crocus
  3. Lily
  4. Rose
  5. Tulip
  6. MGMT
- **Total Capacity:** 70 beds (4 units × 15 beds + 1 unit × 10 beds)
- **Theme:** Flower names

---

## System Totals

### Capacity Overview
- **Total Care Homes:** 5
- **Total Units:** 42 active units (37 care units + 5 MGMT units)
- **Total Bed Capacity:** 235 beds (academic paper) or 550 beds (production data - using unit calculation)
- **Overall Occupancy:** 93.6% (220/235 beds occupied)
- **Total Staff:** 821 staff members
- **Shift Types:** Multiple (Day 07:00-19:00, Night 19:00-07:00, Long Day 07:00-20:00)

### Unit Naming Convention
- **Format:** `{HOME_ABBREV}_{UNIT_NAME}`
- **Examples:**
  - `OG_BRAMLEY` (Orchard Grove - Bramley)
  - `MB_ASTER` (Meadowburn - Aster)
  - `HH_VIOLET` (Hawthorn House - Violet)
  - `RS_LOTUS` (Riverside - Lotus)
  - `VG_TULIP` (Victoria Gardens - Tulip)

### Staff Distribution by Role (Typical)
Based on PRODUCTION_READINESS_REVIEW data:

1. **HOS/Exec** - Head of Service (1 person)
2. **Service Manager** - 5 managers (1 per home)
3. **Operations Manager** - 9 managers (1-2 per home)
   - 4 homes with 2 OMs each
   - 1 home with 1 OM
4. **IDI Team** - Information, Data, Intelligence (3 staff)
5. **Senior Social Care Worker (Night)** - Night shift supervisors
6. **Senior Social Care Worker** - Day shift supervisors
7. **Social Care Worker (Night)** - Night shift workers
8. **Social Care Worker** - Day shift workers
9. **Social Care Assistant** - Support staff

**Total Operational Managers:** 9 OMs across 5 homes

---

## Time Savings Evidence

### Current Manual System (Pre-Implementation)
- **OM Daily Burden:** 4-6 hours/day (average: 5 hours)
  - Manual rota creation: 15 hrs/week
  - Leave approval: 3 hrs/week
  - Absence tracking: 4 hrs/week
  - Training compliance: 2 hrs/week

- **Annual OM Burden:** 
  - 5 hours/day × 5 days/week × 52 weeks = 1,300 hours/year per OM
  - 9 OMs × 1,300 hours = **11,700 hours/year**
  - Cost: £292,500 at £25/hour

- **Service Manager Burden:**
  - 5 SMs × 8 hours/week × 52 weeks = **2,080 hours/year**
  - Scrutiny and report gathering

- **IDI Team Burden:**
  - 3 staff × 2 hours/day × 260 days = **1,560 hours/year**
  - Gathering information from emails, calls, intranet

- **Head of Service Burden:**
  - 1 HOS × 8 hours/week × 52 weeks = **416 hours/year**
  - Interpreting fragmented reports

**Total Organizational Burden:** 15,756 hours/year (£587,340)

### Post-Implementation Savings
- **88% workload reduction** across all 18 staff
- **13,863 hours/year saved**
- **£590,000 annual ROI** across 6 categories:
  1. Budget optimization: £280K
  2. Retention improvements: £120K
  3. Training efficiency: £85K
  4. Compliance savings: £55K
  5. Operational insights: £30K
  6. Communication: £20K

---

## Pilot Rollout Plan

### Phase 1: Initial Pilot (Months 1-3)
- **Homes:** Orchard Grove + Meadowburn House
- **Purpose:** Validate core functionality
- **Staff:** ~330 users (40% of total)

### Phase 2: Expansion (Month 4)
- **Homes:** Hawthorn House + Riverside
- **Additional Staff:** ~330 users

### Phase 3: Full Production (Month 5)
- **Homes:** Victoria Gardens
- **Total Coverage:** All 5 homes, 821 staff, 42 units

---

## Machine Learning Performance

### Prophet Forecasting
- **Average MAPE:** 25.1% across all units
- **Stable Units:** 14.2% MAPE (Residential Care - excellent)
- **High Variance Units:** 31.5% MAPE (Dementia Units - acceptable)
- **Nursing Units:** 22.8% MAPE (good)
- **Forecast Period:** 30 days ahead
- **Confidence Intervals:** 80%

### Unit-Specific Performance Examples
| Unit Type | History | MAPE | Rating |
|-----------|---------|------|--------|
| Residential Care (Stable) | 2+ years | 14.2% | Excellent |
| Nursing Unit | 18 months | 22.8% | Good |
| Dementia Unit (High Turnover) | 1.5 years | 31.5% | Moderate |

### Linear Programming Optimization
- **Cost Reduction:** 12.6% through optimal staff allocation
- **Constraints:** Qualifications, WTD compliance, staff preferences

---

## Demo Data Requirements

### For Realistic Demo (demo.therota.co.uk)
1. **Care Homes:** 5 (with accurate CS numbers, bed capacities)
2. **Units:** 42 units (37 care + 5 MGMT)
3. **Users:** 250+ across 7 roles
4. **Historical Shifts:** 6 months back (for ML training)
5. **Leave Requests:** Mix of pending/approved/rejected
6. **Shift Swaps:** Active swap market (18% weekly rate)
7. **Training Records:** 18 courses, 6,778 records
8. **Compliance Data:** Supervision, induction, incidents

### Minimum Viable Demo
1. **Care Homes:** 5 (current setup complete ✅)
2. **Units:** 1-2 per home initially (5-10 total)
3. **Users:** 50-100 (spread across roles)
4. **Shifts:** 2-3 months historical data
5. **Basic leave/swap data**

---

## Care Inspectorate Integration

### CI Performance Dashboard Data
Each home has official Care Inspectorate inspection data:

**4-Theme Ratings (1-6 scale):**
1. Care & Support
2. Staffing
3. Environment
4. Management & Leadership

**Inspection Schedule:**
- Homes inspected annually or biannually
- Ratings publicly available on Care Inspectorate website
- CS numbers are official registration identifiers

**Operational Metrics Tracked (6-month trends):**
1. Training Compliance: ≥95% target
2. Supervision Completion: ≥90% target
3. Incident Frequency: ≤2.0 target
4. Turnover Rate: ≤15% target
5. Staffing Level: ≥100% target
6. Care Plan Reviews: ≥95% target

---

## Production Configuration Commands

### Create Care Homes (CORRECT DATA)
```python
from scheduling.models import CareHome, Unit

# Delete any test data first
CareHome.objects.all().delete()

# Create homes with ACCURATE capacities from academic paper
homes_data = [
    {
        'name': 'Orchard Grove',
        'bed_capacity': 60,  # Production capacity
        'care_inspectorate_id': 'CS2014333831',
        'location_address': 'Maryhill, Glasgow',
        'care_home_code': 'ORCHARD_GROVE'
    },
    {
        'name': 'Meadowburn House',
        'bed_capacity': 45,
        'care_inspectorate_id': 'CS2018371804',
        'location_address': 'Glasgow',
        'care_home_code': 'MEADOWBURN'
    },
    {
        'name': 'Hawthorn House',
        'bed_capacity': 38,
        'care_inspectorate_id': 'CS2003001025',
        'location_address': 'Glasgow',
        'care_home_code': 'HAWTHORN_HOUSE'
    },
    {
        'name': 'Riverside',
        'bed_capacity': 52,
        'care_inspectorate_id': 'CS2014333834',
        'location_address': 'Govan, Glasgow',
        'care_home_code': 'RIVERSIDE'
    },
    {
        'name': 'Victoria Gardens',
        'bed_capacity': 40,
        'care_inspectorate_id': 'CS2018371437',
        'location_address': 'Partick, Glasgow',
        'care_home_code': 'VICTORIA_GARDENS'
    }
]

for home_data in homes_data:
    home = CareHome.objects.create(**home_data, is_active=True)
    print(f"✓ Created: {home.name} - {home.bed_capacity} beds - {home.care_inspectorate_id}")
```

### Create Units (Full 42-Unit Structure)
```python
# Orchard Grove - 9 units (8 + MGMT)
og_units = ['Bramley', 'Cherry', 'Grape', 'Orange', 'Peach', 'Pear', 'Plum', 'Strawberry', 'MGMT']
og = CareHome.objects.get(name='Orchard Grove')
for unit_name in og_units:
    Unit.objects.create(
        name=f'{unit_name}',
        care_home=og,
        unit_code=f'OG_{unit_name.upper()}',
        capacity=15 if unit_name != 'MGMT' else 0,
        is_active=True
    )

# Meadowburn - 9 units
mb_units = ['Aster', 'Bluebell', 'Cornflower', 'Daisy', 'Foxglove', 'Honeysuckle', 'Marigold', 'Poppy SRD', 'MGMT']
mb = CareHome.objects.get(name='Meadowburn House')
for unit_name in mb_units:
    Unit.objects.create(
        name=f'{unit_name}',
        care_home=mb,
        unit_code=f'MB_{unit_name.replace(" ", "_").upper()}',
        capacity=15 if unit_name != 'MGMT' else 0,
        is_active=True
    )

# Hawthorn House - 9 units
hh_units = ['Bluebell', 'Daisy', 'Heather', 'Iris', 'Primrose', 'Snowdrop SRD', 'Thistle SRD', 'Violet', 'MGMT']
hh = CareHome.objects.get(name='Hawthorn House')
for unit_name in hh_units:
    Unit.objects.create(
        name=f'{unit_name}',
        care_home=hh,
        unit_code=f'HH_{unit_name.replace(" ", "_").upper()}',
        capacity=15 if unit_name != 'MGMT' else 0,
        is_active=True
    )

# Riverside - 9 units
rs_units = ['Daffodil', 'Heather', 'Jasmine', 'Lily', 'Lotus', 'Maple', 'Orchid', 'Rose', 'MGMT']
rs = CareHome.objects.get(name='Riverside')
for unit_name in rs_units:
    Unit.objects.create(
        name=f'{unit_name}',
        care_home=rs,
        unit_code=f'RS_{unit_name.upper()}',
        capacity=15 if unit_name != 'MGMT' else 0,
        is_active=True
    )

# Victoria Gardens - 6 units (5 + MGMT)
vg_units = ['Azalea', 'Crocus', 'Lily', 'Rose', 'Tulip', 'MGMT']
vg = CareHome.objects.get(name='Victoria Gardens')
for unit_name in vg_units:
    Unit.objects.create(
        name=f'{unit_name}',
        care_home=vg,
        unit_code=f'VG_{unit_name.upper()}',
        capacity=15 if unit_name not in ['Tulip', 'MGMT'] else (10 if unit_name == 'Tulip' else 0),
        is_active=True
    )

print(f"✓ Total units created: {Unit.objects.count()}")
```

---

## Next Steps for Production Demo

### ✅ Completed
1. Care homes with accurate CS numbers
2. Basic unit structure (5 main units)
3. Roles and permissions
4. User with HOS/Exec access

### 🔲 Remaining Tasks
1. **Expand units** - Create full 42-unit structure using commands above
2. **Populate demo users** - 250+ users across 7 roles
3. **Historical shifts** - 6 months of shift data for ML training
4. **Leave requests** - Mix of approved/pending/rejected
5. **Training records** - Sample 18 courses with compliance data
6. **Test dashboards** - Verify all 7 executive dashboards load
7. **Load testing** - Validate 300 concurrent users (777ms target)
8. **Auto-reset script** - Nightly 2 AM reset for demo freshness

---

## References
- Academic Paper v1.md - Lines 1-6940 (full system documentation)
- PRODUCTION_READINESS_REVIEW_DEC2025.md - Lines 50-150 (capacity data)
- Care Inspectorate official CS numbers
- DEMO_WALKTHROUGH_UPDATE_DEC29_2025.md (demo requirements)

---

**Last Updated:** January 8, 2026 11:30 GMT
**Status:** Authoritative reference for demo.therota.co.uk deployment
