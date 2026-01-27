# Care Home Staffing Setup Template
**Purpose**: Bulk configuration template for new care home setup  
**Last Updated**: January 26, 2026  
**Version**: 1.0

---

## Overview

This template provides a **drag-and-drop** style configuration for setting up staffing in new care homes. Use this as a reference when importing staff data or configuring a new home in the system.

---

## Quick Reference: Home Size Templates

### Template A: Large Home (120 beds, ~179 staff)
**Examples**: Orchard Grove, Riverside, Meadowburn, Hawthorn House

| Component | Quantity |
|-----------|----------|
| **Care Units** | 8 units (15 beds each) |
| **Management Unit** | 1 unit |
| **Management Staff** | 2 staff (1 OM + 1 SM) |
| **Total Staff** | 179 |
| **Shifts (6 months)** | ~12,000 |

### Template B: Medium Home (70 beds, ~98 staff)
**Examples**: Victoria Gardens

| Component | Quantity |
|-----------|----------|
| **Care Units** | 5 units (4×15 beds + 1×10 beds) |
| **Management Unit** | 1 unit |
| **Management Staff** | 2 staff (1 OM + 1 SM) |
| **Total Staff** | 98 |
| **Shifts (6 months)** | ~6,700 |

---

## Staffing Roles & Definitions

### Role Codes
| Code | Full Name | Shift Type | Contract Hours | Shifts/Week |
|------|-----------|------------|----------------|-------------|
| **OM** | Operations Manager | Day (8hrs) | 37.5 hrs/week | 5 (Mon-Fri) |
| **SM** | Service Manager | Day (8hrs) | 37.5 hrs/week | 5 (Mon-Fri) |
| **SSCW** | Senior Social Care Worker (Day) | Day (12hrs) | 24 or 35 hrs/week | 2 or 3 |
| **SSCWN** | Senior Social Care Worker (Night) | Night (12hrs) | 24 or 35 hrs/week | 2 or 3 |
| **SCW** | Social Care Worker (Day) | Day (12hrs) | 24 or 35 hrs/week | 2 or 3 |
| **SCWN** | Social Care Worker (Night) | Night (12hrs) | 24 or 35 hrs/week | 2 or 3 |
| **SCA** | Social Care Assistant (Day) | Day (12hrs) | 24 or 35 hrs/week | 2 or 3 |
| **SCAN** | Social Care Assistant (Night) | Night (12hrs) | 24 or 35 hrs/week | 2 or 3 |

### Role Hierarchy
```
Management (Supernumerary)
├── Operations Manager (OM)
└── Service Manager (SM)

Unit Supervision (Supernumerary)
├── Senior Social Care Worker - Day (SSCW)
└── Senior Social Care Worker - Night (SSCWN)

Care Staff (Counted in Ratios)
├── Social Care Worker - Day (SCW)
├── Social Care Worker - Night (SCWN)
├── Social Care Assistant - Day (SCA)
└── Social Care Assistant - Night (SCAN)
```

---

## Template A: Large Home (120 beds)

### Management Unit Configuration

| Role | Quantity | Shifts/Week Each | Total Weekly Shifts |
|------|----------|------------------|---------------------|
| OM | 1-2 | 3-5 | 5-8 |
| SM | 1 | 5 | 5 |
| **TOTAL** | **2** | **-** | **10-13** |

**Note**: Management staff are supernumerary (not counted in unit coverage ratios)

---

### Care Unit Configuration (Per Unit)

**Each care unit typically has**:
- **15 beds** (8 units × 15 beds = 120 beds)
- **20-22 staff total** (including SSCW supervisors)
- **Day staff**: 10-11 including 1 SSCW supervisor
- **Night staff**: 10-11 including 1 SSCWN supervisor

#### Standard Care Unit Staffing Model

**Management (Supernumerary)**
| Role | Quantity | Shifts/Week | Status |
|------|----------|-------------|--------|
| SSCW (Day Supervisor) | 1 | 2-3 | Supernumerary |
| SSCWN (Night Supervisor) | 1 | 2-3 | Supernumerary |
| **Subtotal** | **2** | **4-6** | **Not counted in ratios** |

**Day Staff (Home Staff)**
| Role | Quantity | Shifts/Week Each | Total Weekly Shifts |
|------|----------|------------------|---------------------|
| SCW | 4-5 | 2-3 | 10-12 |
| SCA | 8-10 | 2-3 | 18-24 |
| **Day Subtotal** | **12-15** | **-** | **28-36** |

**Night Staff (Home Staff)**
| Role | Quantity | Shifts/Week Each | Total Weekly Shifts |
|------|----------|------------------|---------------------|
| SCWN | 3-4 | 2-3 | 7-10 |
| SCAN | 9-11 | 2-3 | 20-28 |
| **Night Subtotal** | **12-15** | **-** | **27-38** |

**Total Per Unit**: 20-22 staff (18-20 home staff + 2 SSCW supervisors)

---

### Large Home Complete Breakdown

**8 Care Units × Average 22 Staff = 176 Staff + 2 Management = 178 Total**

| Component | Staff Count | Beds | Notes |
|-----------|-------------|------|-------|
| **Management Unit** | 2 | 0 | OM + SM |
| **Care Unit 1** | 20-22 | 15 | Inc. 2 SSCW supervisors |
| **Care Unit 2** | 20-22 | 15 | Inc. 2 SSCW supervisors |
| **Care Unit 3** | 20-22 | 15 | Inc. 2 SSCW supervisors |
| **Care Unit 4** | 20-22 | 15 | Inc. 2 SSCW supervisors |
| **Care Unit 5** | 20-22 | 15 | Inc. 2 SSCW supervisors |
| **Care Unit 6** | 20-22 | 15 | Inc. 2 SSCW supervisors |
| **Care Unit 7** | 20-22 | 15 | Inc. 2 SSCW supervisors |
| **Care Unit 8** | 20-22 | 15 | Inc. 2 SSCW supervisors |
| **TOTAL** | **176-180** | **120** | **Typical: 179 (8 care units + 1 mgmt)** |

---

### Large Home Role Distribution Summary

| Role | Total Across Home | % of Total |
|------|-------------------|------------|
| OM | 1 | 0.6% |
| SM | 1 | 0.6% |
| SSCW | 8 | 4.5% |
| SSCWN | 8 | 4.5% |
| SCW | 32-40 | 20% |
| SCWN | 24-32 | 15% |
| SCA | 40-48 | 25% |
| SCAN | 48-56 | 30% |
| **TOTAL** | **~179** | **100%** |

**Key Ratios**:
- Day Staff : Night Staff ≈ **52% : 48%**
- SCW : SCA ≈ **1 : 2** (Day shifts)
- SCWN : SCAN ≈ **1 : 3** (Night shifts)
- Supervisors (SSCW/SSCWN) : Home Staff ≈ **7% supernumerary**

---

## Template B: Medium Home (70 beds)

### Management Unit Configuration
**Same as Large Home** - 2 staff (1 OM + 1 SM)

---

### Care Unit Configuration (Per Unit - Medium Home)

**Smaller units have**:
- **14-15 beds** (or 1 unit with 10 beds)
- **18-20 staff total** (including SSCW supervisors)
- **Day staff**: 9-10 including 1 SSCW supervisor
- **Night staff**: 9-10 including 1 SSCWN supervisor

#### Medium Unit Staffing Model

**Management (Supernumerary)**
| Role | Quantity | Shifts/Week | Status |
|------|----------|-------------|--------|
| SSCW (Day Supervisor) | 1 | 2-3 | Supernumerary |
| SSCWN (Night Supervisor) | 1 | 2-3 | Supernumerary |
| **Subtotal** | **2** | **4-6** | **Not counted** |

**Day Staff (Home Staff)**
| Role | Quantity | Shifts/Week Each | Total Weekly Shifts |
|------|----------|------------------|---------------------|
| SCW | 3-4 | 2-3 | 7-10 |
| SCA | 5-6 | 2-3 | 12-15 |
| **Day Subtotal** | **8-10** | **-** | **19-25** |

**Night Staff (Home Staff)**
| Role | Quantity | Shifts/Week Each | Total Weekly Shifts |
|------|----------|------------------|---------------------|
| SCWN | 2-3 | 2-3 | 5-7 |
| SCAN | 6-7 | 2-3 | 14-18 |
| **Night Subtotal** | **8-10** | **-** | **19-25** |

**Total Per Unit**: 18-22 staff (16-20 home staff + 2 SSCW supervisors)

---

### Medium Home Complete Breakdown (Victoria Gardens Example)

**5 Care Units × Average 20 Staff = 100 Total Staff**

| Component | Staff Count | Beds | Notes |
|-----------|-------------|------|-------|
| **Management** | 2 | 0 | OM + SM |
| **Care Unit 1 (Rose)** | 23 | 15 | Inc. 2 SSCW supervisors |
| **Care Unit 2 (Lily)** | 19 | 15 | Inc. 2 SSCW supervisors |
| **Care Unit 3 (Daisy)** | 19 | 15 | Inc. 2 SSCW supervisors |
| **Care Unit 4 (Azalea)** | 18 | 15 | Inc. 2 SSCW supervisors |
| **Care Unit 5 (Tulip)** | 17 | 10 | Inc. 2 SSCW supervisors (smaller unit) |
| **TOTAL** | **98** | **70** | **5 care units + mgmt** |

---

### Medium Home Role Distribution Summary

| Role | Total Across Home | % of Total |
|------|-------------------|------------|
| OM | 1 | 1% |
| SM | 1 | 1% |
| SSCW | 5 | 5% |
| SSCWN | 5 | 5% |
| SCW | 16 | 16% |
| SCWN | 11 | 11% |
| SCA | 31 | 32% |
| SCAN | 28 | 29% |
| **TOTAL** | **98** | **100%** |

---

## Shift Pattern Templates

### 3-Week Rotation Cycle

All staff follow a **3-week repeating rotation pattern**. Staff are divided into **Teams A, B, and C** to ensure continuous coverage.

#### Pattern 1: 2 Shifts Per Week (Part-Time)
**~16 hours/week | ~800 hours/year**

| Week | Team A | Team B | Team C |
|------|--------|--------|--------|
| Week 1 | ✅ ✅ | ✅ ✅ | ✅ ✅ |
| Week 2 | ✅ - | - ✅ | ✅ ✅ |
| Week 3 | - ✅ | ✅ ✅ | ✅ - |

**Weekly Pattern**: 2 - 1 - 1 shifts (repeating every 3 weeks)

---

#### Pattern 2: 3 Shifts Per Week (Full-Time)
**~24 hours/week | ~1,200 hours/year**

| Week | Team A | Team B | Team C |
|------|--------|--------|--------|
| Week 1 | ✅ ✅ ✅ | ✅ ✅ ✅ | ✅ ✅ ✅ |
| Week 2 | ✅ ✅ - | - ✅ ✅ | ✅ ✅ ✅ |
| Week 3 | - ✅ ✅ | ✅ ✅ ✅ | ✅ ✅ - |

**Weekly Pattern**: 3 - 2 - 2 shifts (repeating every 3 weeks)

---

#### Pattern 3: 5 Shifts Per Week (Management Only)
**37.5 hours/week | 1,950 hours/year**

| Week | All Weeks |
|------|-----------|
| Mon-Fri | ✅ ✅ ✅ ✅ ✅ |

**Weekly Pattern**: 5 shifts consistently (Mon-Fri, 9am-5pm, 8-hour days)

---

## Shift Times Reference

| Shift Code | Start Time | End Time | Duration | Type |
|------------|------------|----------|----------|------|
| DAY_0800_2000 | 08:00 | 20:00 | 12 hours | Care Staff |
| NIGHT_2000_0800 | 20:00 | 08:00 | 12 hours | Care Staff |
| MGMT_DAY | 09:00 | 17:00 | 8 hours | Management (Mon-Fri) |

---

## Minimum Coverage Requirements

### Large Home (120 beds, 8 units)

**Day Shift Minimums**:
- Minimum **18 staff** on duty
- Including **1+ SSCW** supervisors
- Minimum **3 staff per unit** (average)

**Night Shift Minimums**:
- Minimum **18 staff** on duty
- Including **1+ SSCWN** supervisors
- Minimum **3 staff per unit** (average)

---

### Medium Home (70 beds, 5 units)

**Day Shift Minimums**:
- Minimum **10 staff** on duty
- Including **1+ SSCW** supervisors
- Minimum **2 staff per unit**

**Night Shift Minimums**:
- Minimum **10 staff** on duty
- Including **1+ SSCWN** supervisors
- Minimum **2 staff per unit**

---

## Team Distribution Guidelines

### Team Assignment Rules

Within each unit, staff are distributed across **3 teams (A, B, C)** to ensure:
1. **Balanced coverage** across the 3-week cycle
2. **Skill mix** on every shift (mix of SCW and SCA)
3. **Consistent team familiarity** for residents

**Recommended Distribution**:
- **Team A**: 30-35% of staff
- **Team B**: 30-35% of staff
- **Team C**: 30-40% of staff

**Example** (Unit with 12 day staff):
- Team A: 4 staff (1 SCW + 3 SCA)
- Team B: 4 staff (1 SCW + 3 SCA)
- Team C: 4 staff (2 SCW + 2 SCA)

---

## Bulk Setup Process (Drag & Drop Guide)

### Step 1: Define Home Structure
```yaml
HOME_NAME: [Your Home Name]
BEDS: [70 or 120]
TEMPLATE: [A-Large or B-Medium]
```

### Step 2: Create Units
```yaml
CARE_UNITS:
  - name: [Unit 1 Name]
    beds: [15 or 20]
  - name: [Unit 2 Name]
    beds: [15 or 20]
  # ... repeat for all units
  
MANAGEMENT_UNIT:
  - name: [Home Name]_Mgmt
    beds: 0
```

### Step 3: Define Role Quantities (Per Unit)

**Copy this block for each care unit**:

```yaml
UNIT_NAME: [e.g., "Rose Unit"]

SUPERVISORS (Supernumerary):
  - role: SSCW
    quantity: 1
    shifts_per_week: 3
    team: A
  - role: SSCWN
    quantity: 1
    shifts_per_week: 3
    team: A

DAY_STAFF:
  Team_A:
    - role: SCW
      quantity: 1
      shifts_per_week: 2
    - role: SCA
      quantity: 2
      shifts_per_week: 3
  Team_B:
    - role: SCW
      quantity: 1
      shifts_per_week: 2
    - role: SCA
      quantity: 2
      shifts_per_week: 3
  Team_C:
    - role: SCW
      quantity: 2
      shifts_per_week: 3
    - role: SCA
      quantity: 2
      shifts_per_week: 2

NIGHT_STAFF:
  Team_A:
    - role: SCWN
      quantity: 1
      shifts_per_week: 2
    - role: SCAN
      quantity: 2
      shifts_per_week: 3
  Team_B:
    - role: SCWN
      quantity: 1
      shifts_per_week: 3
    - role: SCAN
      quantity: 2
      shifts_per_week: 2
  Team_C:
    - role: SCWN
      quantity: 1
      shifts_per_week: 2
    - role: SCAN
      quantity: 3
      shifts_per_week: 3
```

### Step 4: Generate Staff List

Use the quantities above to create staff import file:

```csv
sap,first_name,last_name,email,role,unit,shifts_per_week,team
000001,John,Doe,000001@home.care,OM,[HOME]_Mgmt,5,A
000002,Jane,Smith,000002@home.care,SM,[HOME]_Mgmt,5,A
000003,Staff,Name,000003@home.care,SSCW,[UNIT1],3,A
000004,Staff,Name,000004@home.care,SSCWN,[UNIT1],3,A
000005,Staff,Name,000005@home.care,SCW,[UNIT1],2,A
# ... continue for all staff
```

### Step 5: Validate Totals

**Use this checklist**:

✅ **Management**: 2 staff (1 OM + 1 SM)  
✅ **SSCW Day Supervisors**: 1 per care unit  
✅ **SSCWN Night Supervisors**: 1 per care unit  
✅ **Total Staff Count**: Matches template (179 for large, 98 for medium)  
✅ **Role Ratios**: Day SCW:SCA ≈ 1:2, Night SCWN:SCAN ≈ 1:3  
✅ **Team Distribution**: Each unit has balanced A/B/C teams  
✅ **Shift Patterns**: Mix of 2 and 3 shifts/week (no 4-shift patterns)  

---

## Excel/CSV Import Template

### Required Columns

| Column | Description | Example | Required |
|--------|-------------|---------|----------|
| `sap` | Unique staff ID (6 digits) | 000123 | ✅ Yes |
| `first_name` | First name | John | ✅ Yes |
| `last_name` | Last name | Doe | ✅ Yes |
| `email` | Email address | 000123@home.care | ✅ Yes |
| `role` | Role code | SCW | ✅ Yes |
| `unit` | Unit name | ORCHARD_GROVE_Rose | ✅ Yes |
| `shifts_per_week` | 2, 3, or 5 | 3 | ✅ Yes |
| `team` | Team assignment | A | ✅ Yes |
| `password` | Temporary password | Temp123## | Optional |

### Sample CSV (Download Template)

```csv
sap,first_name,last_name,email,role,unit,shifts_per_week,team
000001,Thomas,Anderson,000001@newho me.care,OM,NEWHOME_Mgmt,5,A
000002,Les,Dorson,000002@newhome.care,SM,NEWHOME_Mgmt,5,A
000003,Morag,Henderson,000003@newhome.care,SSCW,NEWHOME_Rose,3,A
000004,Elaine,Martinez,000004@newhome.care,SSCWN,NEWHOME_Rose,3,A
000005,Ella,Ward,000005@newhome.care,SCW,NEWHOME_Rose,2,A
000006,Megan,Howard,000006@newhome.care,SCA,NEWHOME_Rose,3,A
000007,Victor,Watson,000007@newhome.care,SCA,NEWHOME_Rose,2,A
```

**To bulk import**:
1. Save as `staff_import.csv`
2. Use system's bulk import feature
3. System will:
   - Create all staff records
   - Assign to correct units and roles
   - Generate 6-month shift schedules automatically
   - Apply 3-week rotation patterns based on team assignments

---

## Quick Setup Wizard (Recommended for New Users)

### Option 1: Clone Existing Home
**Fastest method** - Duplicate an existing home's structure

1. Select source home (e.g., "Orchard Grove")
2. Specify new home name
3. Adjust bed count if needed
4. System auto-generates:
   - All units with proportional staffing
   - Role distribution
   - Team assignments
   - 6-month shift schedule

**Time**: ~5 minutes

---

### Option 2: Template-Based Setup
**Most common** - Use predefined templates

1. Choose template:
   - Template A: Large Home (120 beds, 179 staff)
   - Template B: Medium Home (70 beds, 98 staff)
2. Customize unit names
3. Upload staff CSV (system provides template)
4. Review and confirm

**Time**: ~15 minutes

---

### Option 3: Manual Configuration
**Most flexible** - Build from scratch

1. Define home details (name, beds, location)
2. Create care units (specify beds per unit)
3. Add management unit
4. Define role quantities per unit
5. Import staff or create individually
6. Assign teams and shift patterns
7. Generate shift schedule

**Time**: ~45-60 minutes

---

## Validation Rules

The system will automatically validate:

### Coverage Rules
✅ **Day shifts**: Minimum 10+ staff (medium) or 18+ staff (large)  
✅ **Night shifts**: Minimum 10+ staff (medium) or 18+ staff (large)  
✅ **Per-unit**: Minimum 2 staff per unit on days and nights  
✅ **Supervisors**: At least 1 SSCW on days, 1 SSCWN on nights  

### Staffing Rules
✅ **Role codes**: Must be valid (OM, SM, SSCW, SSCWN, SCW, SCWN, SCA, SCAN)  
✅ **Shifts per week**: Must be 2, 3, or 5 only  
✅ **Team assignments**: Must be A, B, or C  
✅ **SAP numbers**: Must be unique across system  

### Ratio Rules
⚠️ **Warning if**:
- Day SCW:SCA ratio outside 1:1.5 to 1:3 range
- Night SCWN:SCAN ratio outside 1:2 to 1:4 range
- SSCW supervisors < 5% of total staff
- Total staff count varies >10% from template

---

## Common Mistakes to Avoid

❌ **Don't**: Create units with <10 beds (too small for efficient staffing)  
✅ **Do**: Use 15-bed units for large homes, 10-15 bed units for medium homes

❌ **Don't**: Assign 4 shifts/week (not supported in 3-week rotation)  
✅ **Do**: Use only 2, 3, or 5 shifts/week

❌ **Don't**: Count SSCW supervisors in minimum coverage calculations  
✅ **Do**: Treat SSCW/SSCWN as supernumerary (additional to minimums)

❌ **Don't**: Create unbalanced teams (e.g., Team A has 50% of staff)  
✅ **Do**: Distribute evenly across Teams A, B, C (30-35% each)

❌ **Don't**: Mix day and night roles in same team  
✅ **Do**: Keep day and night staffing separate with own teams

---

## Support & Resources

### Documentation Files
- `ORCHARD_GROVE_STAFFING_MODEL_MASTER.md` - Detailed reference for large home
- `fix_victoria_gardens.py` - Example script for medium home setup
- `verify_complete_implementation.py` - Validation script

### Quick Calculations

**Large Home (120 beds)**:
- Staff needed: ~179 (1.5 staff per bed)
- Units needed: 8 care units + 1 mgmt = 9 total
- Care unit size: 15 beds each
- Shifts (6 months): ~12,000

**Medium Home (70 beds)**:
- Staff needed: ~98 (1.4 staff per bed)
- Units needed: 5 care units + 1 mgmt = 6 total
- Care unit sizes: 4 units @ 15 beds + 1 unit @ 10 beds
- Shifts (6 months): ~6,700

**Staff-to-Bed Ratios**:
- Large home: **1.49 staff per bed**
- Medium home: **1.40 staff per bed**
- Typical range: **1.35-1.55 staff per bed**

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 26, 2026 | Initial template created with Large and Medium home models |

---

**END OF STAFFING SETUP TEMPLATE**
