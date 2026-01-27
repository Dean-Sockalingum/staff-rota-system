# Rota Corrections - December 2025

## Summary

Fixed data entry errors in night shift rotas for Teams A, B, and C. All teams now follow the correct pattern:
- **35-hour staff**: Work Tuesday, Wednesday, Thursday (3 shifts/week)
- **24-hour staff**: Work Wednesday, Thursday (2 shifts/week)

## Changes Made

### 1. Management Commands Created

Created three management commands to automate rota corrections:

- **`fix_week3_rota.py`** - Team A Week 3 (Dec 16-18, 2025)
- **`fix_teamb_week2.py`** - Team B Week 2 (Dec 9-11, 2025)
- **`fix_teamc_week1.py`** - Team C Week 1 (Dec 2-4, 2025)

**Location**: `scheduling/management/commands/`

**Usage**:
```bash
# Preview changes (dry-run mode)
python3 manage.py fix_week3_rota

# Apply changes
python3 manage.py fix_week3_rota --commit
```

### 2. Execution Results

**Team A Week 3** (Dec 16-18, 2025):
- Added 13 Tuesday shifts for 35-hour staff
- Result: 67 total shifts (13 Tue + 27 Wed + 27 Thu)
- Staff: SCW1080-1093 (35hr), SCA1094-1107 (24hr)

**Team B Week 2** (Dec 9-11, 2025):
- Added 2 Tuesday shifts (SCW1110, SCW1111)
- Removed 2 incorrect Tuesday shifts (SCA1121, SCA1122)
- Result: 67 total shifts (13 Tue + 27 Wed + 27 Thu)
- Staff: SCW1108-1111 + SCA1112-1120 (35hr), SCA1121-1134 (24hr)

**Team C Week 1** (Dec 2-4, 2025):
- Added 13 Thursday shifts for 35-hour staff
- Removed 14 incorrect Tuesday shifts from 24-hour staff
- Result: 67 total shifts (13 Tue + 27 Wed + 27 Thu)
- Staff: SCW1135-1140 + SCA1141-1147 (35hr), SCA1148-1161 (24hr)

**Total**: 44 shift corrections across all three teams

### 3. Shift Status Standardization

**Issue**: New shifts were created with `status='ACTIVE'` while existing shifts used `status='SCHEDULED'`, causing dashboard display inconsistencies.

**Fix Applied**:
1. Updated 28 shifts from ACTIVE to SCHEDULED status via Django shell
2. Modified all three management commands to use `status='SCHEDULED'` by default

**Verification**: Dashboard and rota views now display correctly

## Team Structure

### Team A
- **SAP Range**: SCW1080-1093, SCA1094-1107
- **Week 3**: December 16-18, 2025 (Tue/Wed/Thu)
- **Total Staff**: 27 (13 × 35hr, 14 × 24hr)

### Team B
- **SAP Range**: SCW1108-1111, SCA1112-1134
- **Week 2**: December 9-11, 2025 (Tue/Wed/Thu)
- **Total Staff**: 27 (13 × 35hr, 14 × 24hr)

### Team C
- **SAP Range**: SCW1135-1140, SCA1141-1161
- **Week 1**: December 2-4, 2025 (Tue/Wed/Thu)
- **Total Staff**: 27 (13 × 35hr, 14 × 24hr)

## Verification

All corrections verified on December 12, 2025:
- ✅ 201 total shifts (67 × 3 teams) with correct dates
- ✅ All shifts have `status='SCHEDULED'`
- ✅ Dashboard displaying accurately
- ✅ Rota view showing correct pattern
- ✅ 100% test pass rate maintained (29/29 tests)

## Technical Details

### Common Command Features
- **Dry-run mode**: Default behavior shows preview without making changes
- **Transaction safety**: Uses `Transaction.atomic()` for data integrity
- **Comprehensive reporting**: Shows correct/to-add/to-remove counts
- **Error handling**: Validates staff exist before making changes
- **Preview mode**: Shows first 10 changes with pagination for larger sets

### Key Corrections
1. **Date range**: Fixed 2024→2025 year errors
2. **Field names**: Corrected `sap_number`→`sap`, `get_full_name()`→`full_name`
3. **ShiftType query**: Changed `.get()` to `.filter().first()` to avoid MultipleObjectsReturned
4. **Unit field**: Added `unit=user.unit` to Shift creation
5. **Status consistency**: Standardized on `status='SCHEDULED'`

## Files Modified

- `scheduling/management/commands/fix_week3_rota.py` (created)
- `scheduling/management/commands/fix_teamb_week2.py` (created)
- `scheduling/management/commands/fix_teamc_week1.py` (created)
- Database: 72 operations (44 shift corrections + 28 status updates)

## Next Steps

1. ✅ All rota corrections completed
2. ✅ Dashboard displaying correctly
3. ✅ Management commands ready for future use
4. **Next**: Senior management dashboard and other 4 homes interfaces

---

*Documentation Date: December 12, 2025*
*Author: System*
*Status: Completed & Verified*
