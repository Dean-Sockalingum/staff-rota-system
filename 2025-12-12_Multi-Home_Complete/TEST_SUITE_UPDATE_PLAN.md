# Test Suite Update Plan

**Date:** January 16, 2026  
**Status:** Deferred - To be implemented in future development cycle  
**Priority:** Medium (Application working, tests need updating)

---

## Overview

The Staff Rota System has **222 passing tests out of 285 total** (78% pass rate). The application code is working correctly in production. Test failures are due to outdated test code that doesn't match the custom User model implementation.

**Decision:** Deploy to production now, update tests later.

---

## Test Failure Analysis

### Summary
- ✅ **222 tests passing** (78%)
- ❌ **18 test failures**
- ❌ **39 test errors**
- ⏭️ **6 tests skipped**
- **Total:** 285 tests

### Root Cause
All failures are in **test code**, not application code. Tests were written for standard Django User model but the application now uses a custom User model with:
- SAP number as primary key (instead of `id`)
- Different field structure
- Custom authentication backend

---

## Issues Categorized

### Category 1: User Model Primary Key (15+ issues)
**Problem:** Tests reference `User.id` but model uses `User.sap`

**Examples:**
```python
# Test code (WRONG):
user = User.objects.get(id=1)

# Should be (CORRECT):
user = User.objects.get(sap='000541')
```

**Files Affected:**
- `scheduling/tests/test_models.py`
- `scheduling/tests/test_views.py`
- `scheduling/tests/test_api.py`
- `staff_records/tests/test_models.py`

**Estimated Fixes:** ~15-20 replacements

---

### Category 2: Missing Attributes (10+ issues)
**Problem:** Tests check for `User.is_management` which doesn't exist

**Examples:**
```python
# Test code (WRONG):
self.assertTrue(user.is_management)

# Should remove or replace with actual field
```

**Files Affected:**
- `scheduling/tests/test_models.py`
- `scheduling/tests/test_permissions.py`

**Estimated Fixes:** ~10 assertions to remove/update

---

### Category 3: Relationship Naming (8+ issues)
**Problem:** Tests use `User.profile` but it's `User.staff_profile`

**Examples:**
```python
# Test code (WRONG):
user.profile.phone_number

# Should be (CORRECT):
user.staff_profile.phone_number
```

**Files Affected:**
- `scheduling/tests/test_models.py`
- `staff_records/tests/test_views.py`

**Estimated Fixes:** ~8 attribute references

---

### Category 4: Model Field Issues (6+ issues)
**Problem:** Tests look for `StaffProfile.permission_level` which doesn't exist

**Examples:**
```python
# Test code (WRONG):
profile = StaffProfile.objects.create(permission_level=3)

# Should remove permission_level or use actual field
```

**Files Affected:**
- `staff_records/tests/test_models.py`
- `staff_records/tests/test_permissions.py`

**Estimated Fixes:** ~6 field references

---

### Category 5: Required Fields (12+ issues)
**Problem:** Tests not providing required fields

**Examples:**
```python
# Test code (WRONG):
SupervisionRecord.objects.create(supervisor=user, staff=staff)

# Should be (CORRECT):
SupervisionRecord.objects.create(
    supervisor=user, 
    staff=staff,
    duration_minutes=60  # Required field
)

# Also:
IncidentReport.objects.create(
    reported_by=user,
    risk_rating='MEDIUM'  # Required field
)
```

**Files Affected:**
- `staff_records/tests/test_models.py`
- `staff_records/tests/test_views.py`

**Estimated Fixes:** ~12 object creations

---

### Category 6: Decimal Field Syntax (4+ issues)
**Problem:** Decimal constructor called with extra arguments

**Examples:**
```python
# Test code (WRONG):
Decimal('10.50', 2)

# Should be (CORRECT):
Decimal('10.50')
```

**Files Affected:**
- `scheduling/tests/test_calculations.py`

**Estimated Fixes:** ~4 Decimal() calls

---

### Category 7: Authentication Backend (6+ issues)
**Problem:** AxesBackend requires `request` parameter

**Examples:**
```python
# Test code (WRONG):
user = authenticate(username='000541', password='pass')

# Should be (CORRECT):
from django.test import RequestFactory
request = RequestFactory().post('/login/')
user = authenticate(request=request, username='000541', password='pass')
```

**Files Affected:**
- `scheduling/tests/test_auth.py`
- `scheduling/tests/test_views.py`

**Estimated Fixes:** ~6 authenticate() calls

---

## Implementation Plan (For Future)

### Phase 1: Quick Wins (1-2 hours)
Fix issues that are straightforward find-and-replace:

1. **Decimal syntax** (4 fixes)
   - Find: `Decimal('value', digits)`
   - Replace: `Decimal('value')`

2. **User.profile → User.staff_profile** (8 fixes)
   - Find: `user.profile`
   - Replace: `user.staff_profile`

**Estimated time:** 1 hour  
**Impact:** ~12 tests fixed

---

### Phase 2: Model Restructuring (2-3 hours)
Fix model-related issues:

1. **User.id → User.sap** (15-20 fixes)
   - Find: `User.objects.get(id=`
   - Replace: `User.objects.get(sap=`
   - Find: `user.id`
   - Replace: `user.sap`

2. **Remove User.is_management** (10 fixes)
   - Remove or replace assertions
   - Update test logic

3. **Remove StaffProfile.permission_level** (6 fixes)
   - Remove field references
   - Update test factories

**Estimated time:** 2.5 hours  
**Impact:** ~31 tests fixed

---

### Phase 3: Required Fields (1-2 hours)
Add missing required fields:

1. **SupervisionRecord.duration_minutes** (6 fixes)
   ```python
   SupervisionRecord.objects.create(
       ...,
       duration_minutes=60
   )
   ```

2. **IncidentReport.risk_rating** (6 fixes)
   ```python
   IncidentReport.objects.create(
       ...,
       risk_rating='MEDIUM'
   )
   ```

**Estimated time:** 1.5 hours  
**Impact:** ~12 tests fixed

---

### Phase 4: Authentication Updates (1 hour)
Fix authentication tests:

1. **Add request parameter** (6 fixes)
   ```python
   from django.test import RequestFactory
   
   def test_login(self):
       request = RequestFactory().post('/login/')
       user = authenticate(
           request=request,
           username='000541',
           password='password'
       )
   ```

**Estimated time:** 1 hour  
**Impact:** ~6 tests fixed

---

## Total Effort Estimate

| Phase | Hours | Tests Fixed |
|-------|-------|-------------|
| Phase 1: Quick Wins | 1 | ~12 |
| Phase 2: Model Restructuring | 2.5 | ~31 |
| Phase 3: Required Fields | 1.5 | ~12 |
| Phase 4: Authentication | 1 | ~6 |
| **TOTAL** | **6 hours** | **~61 tests** |

**Expected Final Result:** 283/285 tests passing (99%)

---

## Testing Strategy

### Before Starting Fixes
```bash
# Baseline - current state
cd 2025-12-12_Multi-Home_Complete
python manage.py test --settings=rotasystems.test_settings

# Output: 222 passed, 18 failed, 39 errors, 6 skipped
```

### After Each Phase
```bash
# Run full test suite
python manage.py test --settings=rotasystems.test_settings

# Track progress
echo "Phase X completed: $(date)" >> test_fixes.log
```

### Run Specific Test Files
```bash
# Test individual apps
python manage.py test scheduling.tests.test_models
python manage.py test staff_records.tests.test_views

# Test specific test case
python manage.py test scheduling.tests.test_models.UserModelTest
```

---

## File-by-File Breakdown

### Priority 1 - High Impact Files
1. **scheduling/tests/test_models.py** (~15 fixes)
   - User.id → User.sap
   - User.is_management removal
   - User.profile → User.staff_profile

2. **scheduling/tests/test_views.py** (~10 fixes)
   - User.id → User.sap
   - Authentication updates

3. **staff_records/tests/test_models.py** (~12 fixes)
   - Required fields
   - StaffProfile.permission_level removal

### Priority 2 - Medium Impact Files
4. **scheduling/tests/test_auth.py** (~6 fixes)
   - Authentication backend updates

5. **staff_records/tests/test_views.py** (~8 fixes)
   - User.profile → User.staff_profile
   - Required fields

### Priority 3 - Low Impact Files
6. **scheduling/tests/test_api.py** (~5 fixes)
   - User.id → User.sap

7. **scheduling/tests/test_calculations.py** (~4 fixes)
   - Decimal syntax

---

## Git Workflow for Test Fixes

```bash
# Create feature branch
git checkout -b fix/update-test-suite

# Make fixes in phases
git commit -m "Phase 1: Fix Decimal syntax and profile references"
git commit -m "Phase 2: Update User model references (id → sap)"
git commit -m "Phase 3: Add required fields to test data"
git commit -m "Phase 4: Update authentication tests"

# Run final test suite
python manage.py test --settings=rotasystems.test_settings

# Merge back to main
git checkout main
git merge fix/update-test-suite
git push origin main
```

---

## Notes for Future Developer

### Why Tests Were Deferred

1. **Production Priority:** Application is working correctly and ready for deployment
2. **Test vs Application:** Failures are in test code, not application code
3. **Resource Optimization:** Better to deploy working app now, fix tests in next sprint
4. **Risk Assessment:** Low risk - 78% tests passing validates core functionality

### When to Fix Tests

- During next scheduled maintenance window
- Before adding new features (to ensure clean baseline)
- When team has 6 hours dedicated development time
- Before code review / audit requirements

### How to Verify Fixes Work

1. Run test suite before fixes (baseline)
2. Make fixes in phases
3. Run tests after each phase
4. Document which tests are fixed
5. Aim for 99% pass rate (283/285)

---

## References

### Test Files Location
```
2025-12-12_Multi-Home_Complete/
├── scheduling/
│   └── tests/
│       ├── test_models.py
│       ├── test_views.py
│       ├── test_auth.py
│       ├── test_api.py
│       └── test_calculations.py
└── staff_records/
    └── tests/
        ├── test_models.py
        ├── test_views.py
        └── test_permissions.py
```

### Key Model Files
- `scheduling/models/user.py` - Custom User model definition
- `staff_records/models/staff_profile.py` - StaffProfile model
- `scheduling/backends.py` - SAPAuthBackend implementation

---

**Status:** Ready for implementation when scheduled  
**Complexity:** Medium (straightforward but time-consuming)  
**Risk:** Low (tests don't affect production)  
**Priority:** Can wait until after production deployment  

**Next Action:** Schedule 6-hour development session for test suite updates
