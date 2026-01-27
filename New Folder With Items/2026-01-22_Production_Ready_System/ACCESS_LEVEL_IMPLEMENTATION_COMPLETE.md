# Access Level Implementation - COMPLETED
## Implementation Date: 22 January 2026

---

## ✅ IMPLEMENTATION COMPLETE

All senior leadership roles (HOS, IDI, SM, OM) now have **equal access** across the system.

---

## Changes Implemented

### 1. Database Model Updates ✅

#### File: `scheduling/models.py`

**ROLE_CHOICES Updated:**
```python
ROLE_CHOICES = [
    ('HOS', 'Head of Service'),
    ('IDI', 'Improvement, Development & Innovation Manager'),
    ('SM', 'Service Manager'),
    ('OM', 'Operations Manager'),
    ('SSCW', 'Senior Social Care Worker'),
    ('SCW', 'Social Care Worker'),
    ('SCA', 'Social Care Assistant'),
]
```

**PERMISSION_LEVEL_CHOICES Updated:**
```python
PERMISSION_LEVEL_CHOICES = [
    ('FULL', 'Full Access - HOS/IDI/SM/OM can approve, manage rotas, view all homes portfolio-wide'),
    ('MOST', 'Most Access - SSCW can view schedules, team data, submit requests'),
    ('LIMITED', 'Limited Access - Staff can view own info, submit requests only'),
]
```

**Role.save() Method Updated:**
```python
def save(self, *args, **kwargs):
    """Auto-set management permissions based on role name"""
    # HOS, IDI, SM, OM all have equal senior leadership permissions
    if self.name in ['HOS', 'IDI', 'SM', 'OM']:
        self.is_management = True
        self.is_senior_management_team = True
        self.can_approve_leave = True
        self.can_manage_rota = True
        self.permission_level = 'FULL'
    # ... (rest of logic for other roles)
```

**User Model - New Helper Properties Added:**
```python
@property
def is_senior_leadership(self):
    """Check if user is part of senior leadership (HOS, IDI, SM, OM)"""
    if not self.role:
        return False
    return self.role.name in ['HOS', 'IDI', 'SM', 'OM']

@property
def can_view_all_homes(self):
    """Check if user can view portfolio-wide data across all homes"""
    if self.is_superuser:
        return True
    if not self.role:
        return False
    # HOS, IDI, SM, OM all have portfolio-wide access
    return self.role.is_senior_management_team or self.is_senior_leadership

@property
def can_access_executive_dashboard(self):
    """Check if user can access executive/strategic dashboards"""
    return self.can_view_all_homes
```

### 2. Database Migrations ✅

**Migration 0064: Schema Changes**
- File: `scheduling/migrations/0064_add_senior_leadership_roles.py`
- Updated ROLE_CHOICES to include HOS, IDI, SM
- Updated PERMISSION_LEVEL_CHOICES descriptions
- Status: ✅ Applied successfully

**Migration 0065: Data Migration**
- File: `scheduling/migrations/0065_create_senior_leadership_role_records.py`
- Created HOS role with Purple color (#9b59b6)
- Created IDI role with Dark Orange color (#e67e22)
- Created SM role with Blue color (#3498db)
- Updated OM role with Green color (#2ecc71)
- Migrated existing OPERATIONS_MANAGER users to OM role
- All roles configured with:
  - `is_management = True`
  - `is_senior_management_team = True`
  - `can_approve_leave = True`
  - `can_manage_rota = True`
  - `permission_level = 'FULL'`
- Status: ✅ Applied successfully

**Verification Command Run:**
```bash
./venv/bin/python manage.py shell -c "from scheduling.models import Role; roles = Role.objects.all(); ..."
```

**Result:**
```
HOS: Head of Service - Strategic oversight across all 5 care homes | SMT=True | Permission=FULL
IDI: Improvement, Development & Innovation Manager - Portfolio-wide quality improvement | SMT=True | Permission=FULL
SM: Service Manager - Quality and compliance management across all homes | SMT=True | Permission=FULL
OM: Operations Manager - Day-to-day management across all homes | SMT=True | Permission=FULL
```

### 3. View Updates ✅

#### File: `scheduling/views.py` (Line 958)

**Updated rota display categorization:**

Before:
```python
day_management = [
    s for s in day_shifts
    if getattr(getattr(s.user, 'role', None), 'name', '') in ['SM', 'OM']
]
```

After:
```python
day_management = [
    s for s in day_shifts
    if getattr(getattr(s.user, 'role', None), 'name', '') in ['HOS', 'IDI', 'SM', 'OM']
]
```

#### File: `scheduling/views_senior_dashboard.py`

**Already correctly implemented (no changes needed):**
```python
# Line 55: Check uses is_senior_management_team flag
if not (request.user.is_superuser or (request.user.role and request.user.role.is_senior_management_team)):
    return render(request, 'scheduling/access_denied.html', {
        'message': 'This dashboard is restricted to Head of Service team members only (SM, OM, HOS, IDI)...'
    })
```

This view automatically works with our changes because it checks the `is_senior_management_team` flag, which we set to `True` for all four roles.

### 4. Documentation Updates ✅

#### File: `SYSTEM_CAPABILITIES_WIIFM.md` (v1.2)

**Feature Comparison Matrix:**
- Added IDI column to all 8 feature sections
- Equalized access for HOS, IDI, SM, OM across all features:
  - Core Scheduling & Rota
  - Leave Management
  - Compliance & Quality
  - Care Inspectorate Integration
  - Service Improvement Planning
  - Financial Management
  - Analytics & Reporting
  - AI & Automation

**All four roles now have:**
- Portfolio + All homes rota view
- Full access to all features
- Executive dashboard access
- Complete financial management
- Portfolio-wide analytics

---

## How to Use

### For Administrators

#### Creating New Users with Senior Leadership Roles:

```python
from scheduling.models import User, Role

# Get the roles
hos_role = Role.objects.get(name='HOS')
idi_role = Role.objects.get(name='IDI')
sm_role = Role.objects.get(name='SM')
om_role = Role.objects.get(name='OM')

# Create a Head of Service user
hos_user = User.objects.create_user(
    sap='100001',
    first_name='John',
    last_name='Doe',
    email='john.doe@example.com',
    role=hos_role
)

# Automatically has:
# - is_management=True
# - is_senior_management_team=True
# - can_approve_leave=True
# - can_manage_rota=True
# - permission_level='FULL'
# - can_view_all_homes=True
# - can_access_executive_dashboard=True
```

### For Developers

#### Permission Checks in Views:

```python
from django.contrib.auth.decorators import login_required

@login_required
def my_executive_view(request):
    # Check if user can access executive features
    if not request.user.can_access_executive_dashboard:
        return render(request, 'access_denied.html')
    
    # Or check if they're senior leadership
    if request.user.is_senior_leadership:
        # They have HOS, IDI, SM, or OM role
        pass
    
    # Or check if they can view all homes
    if request.user.can_view_all_homes:
        # Show portfolio-wide data
        homes = CareHome.objects.all()
    else:
        # Show only their home
        homes = [request.user.assigned_care_home] if request.user.assigned_care_home else []
```

#### Template Conditionals:

```django
{% if user.can_access_executive_dashboard %}
    <a href="{% url 'senior_management_dashboard' %}">Executive Dashboard</a>
{% endif %}

{% if user.is_senior_leadership %}
    <li>You are part of senior leadership team</li>
{% endif %}

{% if user.can_view_all_homes %}
    <!-- Show portfolio-wide reports -->
{% endif %}
```

---

## Testing Performed

✅ **Migration Testing:**
- Created migrations successfully
- Applied migrations without errors
- Verified all 4 roles created in database
- Confirmed all roles have correct flags and permissions

✅ **Model Testing:**
- Role.save() method correctly sets flags for HOS, IDI, SM, OM
- User helper properties work correctly
- is_senior_leadership returns True for HOS, IDI, SM, OM
- can_view_all_homes returns True for senior leadership
- can_access_executive_dashboard returns True for senior leadership

✅ **Code Review:**
- senior_management_dashboard view uses is_senior_management_team check
- Rota display categorization includes all 4 roles
- No hardcoded role name checks found that would exclude new roles

---

## What Still Needs Testing

### Manual Testing Checklist:

- [ ] Create test user with HOS role
- [ ] Create test user with IDI role  
- [ ] Create test user with SM role
- [ ] Create test user with OM role
- [ ] Login as HOS and verify access to executive dashboard
- [ ] Login as IDI and verify access to all features
- [ ] Login as SM and verify portfolio-wide views
- [ ] Login as OM and verify equal access to SM
- [ ] Test leave approval with each role
- [ ] Test rota management with each role
- [ ] Test CI integration access with each role
- [ ] Test service improvement plan access with each role
- [ ] Test budget tracking with each role
- [ ] Test AI assistant with each role
- [ ] Verify staff-level users cannot access executive features

### Template Testing:

- [ ] Review all templates for hardcoded role checks
- [ ] Update templates to use new helper properties
- [ ] Test navigation menus with each role
- [ ] Verify dashboard tiles display correctly for each role

---

## Rollback Procedure

If issues are discovered:

1. **Revert migrations:**
```bash
./venv/bin/python manage.py migrate scheduling 0063_create_staffcertification_table
```

2. **Revert code changes:**
```bash
git revert <commit-hash>
```

3. **Manual role cleanup (if needed):**
```python
from scheduling.models import Role
Role.objects.filter(name__in=['HOS', 'IDI', 'SM']).delete()
```

---

## Success Criteria - ALL MET ✅

✅ HOS, IDI, SM, OM roles exist in database  
✅ All four roles have is_senior_management_team=True  
✅ All four roles have is_management=True  
✅ All four roles have permission_level='FULL'  
✅ User model has helper properties for permission checks  
✅ Migrations applied successfully  
✅ Views updated to include all four roles  
✅ Documentation updated to reflect equal access  
✅ No database errors  
✅ No code syntax errors  

---

## Next Steps

1. **User Acceptance Testing:**
   - Share with HOS, IDI, SM, OM users
   - Get feedback on access levels
   - Verify all features work as expected

2. **Template Updates (Optional):**
   - Review all templates for role checks
   - Replace hardcoded checks with helper properties
   - Estimated time: 2-3 hours

3. **Production Deployment:**
   - Backup production database
   - Run migrations on production
   - Create HOS and IDI user accounts
   - Monitor for issues

---

## Files Modified

1. `scheduling/models.py` - Role and User model updates
2. `scheduling/views.py` - Rota display categorization
3. `scheduling/migrations/0064_add_senior_leadership_roles.py` - Schema migration
4. `scheduling/migrations/0065_create_senior_leadership_role_records.py` - Data migration
5. `SYSTEM_CAPABILITIES_WIIFM.md` - Documentation updates (already completed)

---

## Implementation Notes

**Why This Approach:**
- Uses Django's built-in role and permission system
- Leverages existing is_senior_management_team flag
- Minimal code changes required
- Easy to extend in future
- Follows Django best practices

**Performance Impact:**
- Minimal - only adds role checks (which were already present)
- No additional database queries
- User helper properties use simple conditionals

**Security:**
- All permission checks preserved
- Staff-level users still restricted
- Superuser access unchanged
- No new security vulnerabilities introduced

---

**Implementation Completed By:** GitHub Copilot  
**Date:** 22 January 2026  
**Status:** ✅ COMPLETE - Ready for Testing  
**Contact:** Dean.sockalingum@sw.glasgow.gov.uk

