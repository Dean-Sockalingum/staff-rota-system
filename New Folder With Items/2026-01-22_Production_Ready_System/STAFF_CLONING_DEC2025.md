# Multi-Home Staff Cloning - December 12, 2025

## Summary

Successfully cloned Orchard Grove staff structure to three new care homes:
- **Meadowburn** (120 beds, 9 units)
- **Hawthorn House** (120 beds, 9 units)  
- **Riverside** (120 beds, 9 units)

## Execution Results

✅ **531 new staff members created**
- Meadowburn: 177 staff
- Hawthorn House: 177 staff
- Riverside: 177 staff

### SAP Number Range
- Starting SAP: `SSCWN1162`
- Final SAP: `SSCWN1692`
- Next available: `SSCWN1693`

## Capacity Update

Updated bed capacities to correct values:

| Care Home | Beds | Staff | Occupancy |
|-----------|------|-------|-----------|
| Orchard Grove | 120 | 177 | 57 (47.5%) |
| Meadowburn | 120 | 177 | 42 (35.0%) |
| Hawthorn House | 120 | 177 | 35 (29.2%) |
| Riverside | 120 | 177 | 48 (40.0%) |
| Victoria Gardens | 70 | 0 | 38 (54.3%) |
| **TOTAL** | **550** | **712** | **220 (40.0%)** |

**Staff to bed ratio:** 1:0.77 (excluding Victoria Gardens)

## Unit Mapping

Each home received identical staff distribution mapped to equivalent units:

### Orchard Grove → Meadowburn
- DEMENTIA → MEADOW_RED (26 staff)
- BLUE → MEADOW_BLUE (23 staff)
- GREEN → MEADOW_GREEN (19 staff)
- ROSE → MEADOW_YELLOW (22 staff)
- VIOLET → MEADOW_PURPLE (20 staff)
- ORANGE → MEADOW_ORANGE (23 staff)
- PEACH → MEADOW_PINK (21 staff)
- GRAPE → MEADOW_WHITE (23 staff)
- MGMT → MEADOW_MGMT (0 staff - OG has no MGMT staff)

### Orchard Grove → Hawthorn House
- DEMENTIA → HAWTHORN_AMBER (26 staff)
- BLUE → HAWTHORN_BIRCH (23 staff)
- GREEN → HAWTHORN_CEDAR (19 staff)
- ROSE → HAWTHORN_ELDER (22 staff)
- VIOLET → HAWTHORN_HOLLY (20 staff)
- ORANGE → HAWTHORN_MAPLE (23 staff)
- PEACH → HAWTHORN_OAK (21 staff)
- GRAPE → HAWTHORN_WILLOW (23 staff)
- MGMT → HAWTHORN_MGMT (0 staff)

### Orchard Grove → Riverside
- DEMENTIA → RIVERSIDE_NORTH1 (26 staff)
- BLUE → RIVERSIDE_NORTH2 (23 staff)
- GREEN → RIVERSIDE_NORTH3 (19 staff)
- ROSE → RIVERSIDE_SOUTH1 (22 staff)
- VIOLET → RIVERSIDE_SOUTH2 (20 staff)
- ORANGE → RIVERSIDE_SOUTH3 (23 staff)
- PEACH → RIVERSIDE_EAST (21 staff)
- GRAPE → RIVERSIDE_WEST (23 staff)
- MGMT → RIVERSIDE_MGMT (0 staff)

## Staff Generation Details

### Name Generation
- **First names:** 60 common UK names (Emma, James, Olivia, William, etc.)
- **Last names:** 60 common UK surnames (Smith, Jones, Taylor, Brown, etc.)
- Names cycled through lists to create 531 unique combinations

### Account Details
- **Email:** `firstname.lastname.sapnumber@example.com`
- **Password:** `changeme123` (all accounts)
- **Phone:** Fictional UK mobile numbers (07...)
- **Annual Leave:** Copied from source staff (fresh used=0)
- **Role/Team:** Identical to source staff
- **Shift Preference:** Identical to source staff

## Technical Implementation

### Management Command
**File:** `scheduling/management/commands/clone_staff_to_homes.py`

**Key Features:**
- Transactional safety (atomic per home)
- Dry-run mode for preview
- Unit mapping dictionary
- Name generator with rotation
- Consecutive SAP numbering

**Usage:**
```bash
python manage.py clone_staff_to_homes --dry-run  # Preview
python manage.py clone_staff_to_homes            # Execute
```

## Victoria Gardens - Pending

Victoria Gardens (70 beds, 6 units) remains unstaffed by design:
- Will be staffed separately later
- Different capacity (70 vs 120 beds)
- May require different staffing model

## Next Steps

1. ✅ Staff cloning complete for 3 homes
2. ⏳ Clone December 2025 rota to new homes  
3. ⏳ Test automated workflow across homes
4. ⏳ Staff Victoria Gardens (separate task)
5. ⏳ Train home managers on multi-home dashboard

## Verification Queries

```python
# Total staff by home
from scheduling.models import User
from scheduling.models_multi_home import CareHome

for home in CareHome.objects.all():
    count = User.objects.filter(unit__care_home=home, is_active=True).count()
    print(f"{home.get_name_display()}: {count}")
```

## Database Impact

- **Before:** 181 users (177 active OG + 4 admin)
- **After:** 712 users (708 active staff + 4 admin)
- **Increase:** +531 staff members (+293%)

---

**Created:** December 12, 2025  
**Command:** `clone_staff_to_homes`  
**Status:** ✅ Complete  
**Validated:** All 531 staff created and assigned correctly
