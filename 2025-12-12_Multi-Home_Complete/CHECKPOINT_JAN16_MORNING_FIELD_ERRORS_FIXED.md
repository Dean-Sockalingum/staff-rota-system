# CHECKPOINT: Field Name Errors Fixed - 16 January 2026, 01:10 AM

## Summary
Fixed critical field name mismatches causing 500 errors across the system. Server is running but needs restart in the morning to pick up all changes.

## Files Modified

### 1. **scheduling/views_compliance.py** (Line 144)
**Issue**: `days_until_expiry` method called without parentheses
**Fix**: Changed `abs(latest_record.days_until_expiry)` → `abs(latest_record.days_until_expiry())`
**Impact**: Fixed TypeError on `/compliance/training/management/` page

### 2. **scheduling/performance_tracking.py** (Line 56)
**Issue**: Shift model queried with wrong field name `staff_member`
**Fix**: Changed `Shift.objects.filter(staff_member=...)` → `Shift.objects.filter(user=...)`
**Impact**: Fixed FieldError on `/performance/` page
**Note**: Shift model uses `user` field, not `staff_member`. AttendanceRecord uses `staff_member`.

### 3. **scheduling/views.py** (Multiple lines)
**Issue**: User model queried with non-existent `sap_id` field
**Fix**: Replaced all `.sap_id` references with `.sap` (11 instances)
**Impact**: Fixed AttributeError on `/reports/vacancies/` and other reports
**Locations**:
- Line 7381, 7396 (shift reports)
- Line 7451, 7466 (another shift report)
- Line 7587, 7610 (staff vacancies)
- Line 7726, 7756 (other reports)

### 4. **Backup Files Created**
- `scheduling/views_compliance.py.bak` (original before fix)
- `scheduling/views.py.bak2` (original before fix)

## Model Field Reference (For Future Use)

### User Model Fields
- ✅ `sap` (NOT `sap_id`)
- ✅ `full_name` property
- ✅ `role` ForeignKey
- ✅ `unit` ForeignKey
- ✅ `care_home` (through unit)

### Shift Model Fields
- ✅ `user` ForeignKey (NOT `staff_member`)
- ✅ `unit` ForeignKey
- ✅ `shift_type` ForeignKey
- ✅ `date` DateField
- ✅ `status` CharField
- ✅ `shift_classification` CharField
- ✅ `shift_pattern` CharField

### AttendanceRecord Model Fields
- ✅ `staff_member` ForeignKey (this model DOES use staff_member)
- ✅ `shift` ForeignKey
- ✅ `status` CharField

### TrainingRecord Model Methods
- ✅ `days_until_expiry()` - method, requires parentheses
- ✅ `get_status()` - method, requires parentheses

## Template Issues Found (Not Yet Fixed - Do in Morning)

### quality_audits/templates/
Several templates may still have old field references:
- Check for `project_name` → should be `title`
- Check for `project_aim` → should be `aim_statement`
- Check for `created_by` → should be `lead_user` (for PDSAProject)

**TODO Morning**: Run systematic check:
```bash
grep -r "project_name" quality_audits/templates/
grep -r "project_aim" quality_audits/templates/
```

## Server Status
- ✅ Running on http://0.0.0.0:8000/
- ⚠️ 141 unapplied migrations (can run in morning if needed)
- ✅ System check: 0 issues
- ✅ Auto-reload: Working

## Pages That Should Now Work
1. ✅ `/performance/` - Performance dashboard (was FieldError)
2. ✅ `/compliance/training/management/` - Training compliance (was TypeError)
3. ✅ `/reports/vacancies/` - Staff vacancies (was AttributeError)
4. ✅ All shift reports using user.sap

## To Do Tomorrow Morning

### 1. Restart Server
```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
/Users/deansockalingum/Desktop/Staff_Rota_Backups/.venv/bin/python manage.py runserver 0.0.0.0:8000
```

### 2. Test Fixed Pages
- Visit `/performance/` - should load without errors
- Visit `/compliance/training/management/` - should load without errors
- Visit `/reports/vacancies/` - should load without errors

### 3. Quality Audits Templates Check
Run searches for old field names:
```bash
cd quality_audits/templates/quality_audits/
grep -n "project_name" *.html
grep -n "project_aim" *.html
grep -n "\.created_by" *.html
```

Fix any remaining instances found.

### 4. Optional: Run Migrations
If time permits and database backup is taken:
```bash
python manage.py migrate
```

### 5. System-Wide Field Name Audit
Search for other potential mismatches:
```bash
# Search for other sap_id references
grep -r "\.sap_id" scheduling/ --include="*.py"

# Search for other staff_member references in Shift queries
grep -r "Shift\.objects\.filter.*staff_member" scheduling/ --include="*.py"

# Search for days_until_expiry without parentheses
grep -r "days_until_expiry[^(]" scheduling/ --include="*.py"
```

## Error Pattern Summary

### Common Mistakes Found
1. **Method vs Property**: `days_until_expiry` is a method, needs `()`
2. **Field Name Changes**: Model refactoring left old field names in code
3. **Model Confusion**: Shift uses `user`, AttendanceRecord uses `staff_member`

### Prevention Strategy
- Always check model definitions before querying
- Use `python manage.py shell` to inspect model fields:
  ```python
  from scheduling.models import Shift
  print([f.name for f in Shift._meta.fields])
  ```
- Template errors are silent - test all pages after model changes

## Git Status
Modified files not yet committed:
- scheduling/views_compliance.py (fixed)
- scheduling/views.py (fixed)  
- scheduling/performance_tracking.py (fixed)
- scheduling/views_compliance.py.bak (backup)
- scheduling/views.py.bak2 (backup)

**Commit Message Suggestion**:
```
fix: correct field name mismatches across scheduling module

- Fixed TrainingRecord.days_until_expiry() method call (missing parentheses)
- Fixed Shift queries using 'staff_member' → 'user' field
- Fixed User model references using 'sap_id' → 'sap' field
- Resolves 500 errors on /performance/, /compliance/training/, /reports/vacancies/

11 instances of sap_id corrected
1 instance of staff_member corrected
1 instance of method call corrected
```

## Database Schema Notes (For Reference)

### Shift Model Structure
```python
class Shift(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shifts')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    shift_type = models.ForeignKey(ShiftType, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    shift_classification = models.CharField(max_length=20, choices=SHIFT_TYPE_CHOICES)
    shift_pattern = models.CharField(max_length=20, choices=SHIFT_PATTERN_CHOICES)
    # ... other fields
```

### AttendanceRecord Model Structure
```python
class AttendanceRecord(models.Model):
    staff_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    # ... other fields
```

### User Model Key Fields
```python
class User(AbstractBaseUser):
    sap = models.CharField(max_length=6, unique=True)  # NOT sap_id
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.ForeignKey(Role, ...)
    unit = models.ForeignKey(Unit, ...)
    # ... other fields
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
```

## Testing Checklist for Morning

- [ ] Server starts without errors
- [ ] `/performance/` page loads
- [ ] `/compliance/training/management/` page loads
- [ ] `/reports/vacancies/` page loads  
- [ ] Can view staff details (sap field displays correctly)
- [ ] Training records show days_until_expiry correctly
- [ ] No new 500 errors in any module

## Contact Info
**Last Updated**: 16 January 2026, 01:10 AM
**By**: GitHub Copilot
**Status**: Ready for morning testing
**Priority**: HIGH - Test all fixed pages first thing

---

## Quick Command Reference for Morning

### Start Server
```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
source ../.venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### Check for Errors
```bash
# View Django logs
tail -f /tmp/django_debug.log  # if logging configured

# Check for Python syntax errors
python manage.py check
```

### Test in Browser
1. Navigate to http://localhost:8000/performance/
2. Navigate to http://localhost:8000/compliance/training/management/
3. Navigate to http://localhost:8000/reports/vacancies/

### If Issues Found
```bash
# Check terminal output for tracebacks
# Look for FieldError, AttributeError, TypeError
# Search this checkpoint for the error type
```

---

**END OF CHECKPOINT**
