# TODO: System Access Level Implementation
## Date Created: 22 January 2026

## Overview
Update the Staff Rota system to implement equalized access levels for HOS, IDI, SM, and OM roles as documented in SYSTEM_CAPABILITIES_WIIFM.md v1.2

## Current State
- Documentation updated: Feature Comparison Matrix now shows HOS, IDI, SM, and OM with same access levels
- System code: Needs updating to match new documentation

## Required Changes

### 1. Django Permissions & Groups
**File:** `scheduling/models.py` or permissions configuration

**Action Items:**
- [ ] Create/update Django permission groups for HOS, IDI, SM, OM roles
- [ ] Ensure all four groups have identical base permissions
- [ ] Verify IDI role exists in User model (may need to add if not present)

**Details:**
All four roles (HOS, IDI, SM, OM) should have access to:
- Portfolio-wide data (all 5 homes)
- All homes' rota views and management
- Executive dashboard
- Strategic and operational reports
- Complete CI integration features
- Full service improvement planning
- Complete financial management
- All analytics and reporting features
- All AI and automation features

### 2. View-Level Access Control
**Files to update:**
- [ ] `scheduling/views.py` - Main rota and shift views
- [ ] `scheduling/views_senior_dashboard.py` - Executive dashboards
- [ ] `scheduling/views_ai_assistant.py` - AI assistant access
- [ ] `scheduling/views_reports.py` - Report generation
- [ ] `scheduling/views_budget.py` - Budget tracking and forecasting

**Changes needed:**
```python
# Example current code (hypothetical):
@user_passes_test(lambda u: u.role == 'HOS')
def executive_dashboard(request):
    # ...

# Should become:
@user_passes_test(lambda u: u.role in ['HOS', 'IDI', 'SM', 'OM'])
def executive_dashboard(request):
    # ...
```

**Specific views to update:**
- [ ] Executive dashboard access
- [ ] Multi-home rota view (portfolio view)
- [ ] CI inspection reports (all homes)
- [ ] Service improvement plans (organizational + all homes)
- [ ] Budget tracking (portfolio + all homes)
- [ ] Strategic reports access
- [ ] Benchmarking features
- [ ] ML forecasting views

### 3. Template-Level Conditionals
**Files to update:**
- [ ] `scheduling/templates/scheduling/base.html` - Navigation menu
- [ ] `scheduling/templates/scheduling/dashboard.html` - Dashboard rendering
- [ ] `scheduling/templates/scheduling/senior_dashboard.html` - Executive features
- [ ] All report templates that check user role

**Changes needed:**
```django
{# Example current code (hypothetical): #}
{% if user.role == 'HOS' %}
    <a href="{% url 'executive_dashboard' %}">Executive Dashboard</a>
{% endif %}

{# Should become: #}
{% if user.role in 'HOS,IDI,SM,OM' %}
    <a href="{% url 'executive_dashboard' %}">Executive Dashboard</a>
{% endif %}
```

### 4. API Endpoint Permissions
**Files to update:**
- [ ] `scheduling/api_views.py` or REST framework views
- [ ] API permission classes

**Action Items:**
- [ ] Update API permission decorators to include IDI, SM, OM alongside HOS
- [ ] Test all API endpoints with each role
- [ ] Verify portfolio-wide data access for all four roles

### 5. Database Query Filters
**Files to review:**
- [ ] All views that filter data by home/unit based on user role

**Changes needed:**
- Remove restrictive filters like `unit=user.unit` for SM/OM
- Ensure HOS, IDI, SM, OM all query across all homes
- Keep staff-level filters intact (staff only see their own data)

**Example:**
```python
# Current code (hypothetical):
if user.role == 'HOS':
    homes = Unit.objects.all()
elif user.role == 'SM':
    homes = Unit.objects.filter(id=user.unit_id)
# ...

# Should become:
if user.role in ['HOS', 'IDI', 'SM', 'OM']:
    homes = Unit.objects.all()  # All roles get all homes
# ...
```

### 6. Frontend JavaScript Filters
**Files to update:**
- [ ] `scheduling/static/js/rota_management.js`
- [ ] `scheduling/static/js/dashboard.js`
- [ ] Any JavaScript that filters UI elements by role

### 7. Testing Requirements
**Test cases needed:**
- [ ] Create test users for HOS, IDI, SM, OM roles
- [ ] Verify each role can access executive dashboard
- [ ] Verify each role sees all 5 homes in rota view
- [ ] Verify each role can view CI reports for all homes
- [ ] Verify each role can create/view improvement plans
- [ ] Verify each role has full budget tracking access
- [ ] Verify each role can run strategic reports
- [ ] Test leave approval configuration across all roles
- [ ] Test AI assistant access for all roles
- [ ] Verify Staff role restrictions remain intact

### 8. Documentation Updates
**Files to update:**
- [ ] User manual or admin guide
- [ ] Role configuration documentation
- [ ] API documentation (if separate from code)

## Migration Plan

### Phase 1: Database & Permissions (Week 1)
1. Add IDI role to User model if not present
2. Create/update permission groups
3. Run Django migrations
4. Create test users for each role

### Phase 2: Backend Code Updates (Week 2-3)
1. Update all view decorators and permission checks
2. Update database query filters
3. Update API endpoint permissions
4. Run unit tests after each file update

### Phase 3: Frontend Updates (Week 4)
1. Update all template conditionals
2. Update JavaScript role checks
3. Test UI rendering for each role

### Phase 4: Testing & Validation (Week 5)
1. Manual testing with each role
2. Automated test suite execution
3. User acceptance testing with actual HOS/IDI/SM/OM users
4. Fix any issues found

### Phase 5: Deployment (Week 6)
1. Backup production database
2. Deploy to staging environment
3. Final testing on staging
4. Deploy to production (demo.therota.co.uk)
5. Monitor for issues

## Risk Assessment

**Low Risk:**
- Adding IDI to existing permission checks (doesn't affect current users)
- Template updates (cosmetic changes)

**Medium Risk:**
- Database query changes (could impact performance if not optimized)
- API permission changes (need thorough testing)

**High Risk:**
- Removing filters for SM/OM (must ensure data security is maintained)
- Ensure staff-level users don't gain unintended access

## Rollback Plan
If issues arise:
1. Restore database backup
2. Revert code to previous Git commit
3. Redeploy previous version
4. Document issues encountered

## Success Criteria
✅ All four roles (HOS, IDI, SM, OM) have identical access to:
- Portfolio views
- All homes data
- Executive dashboard
- CI integration
- Service improvement planning
- Financial management
- Analytics and reporting

✅ Staff role remains restricted (only own data)
✅ No security vulnerabilities introduced
✅ System performance unchanged or improved
✅ All automated tests pass
✅ User acceptance testing confirms correct access

## Notes
- This implementation brings the system in line with documented capabilities in SYSTEM_CAPABILITIES_WIIFM.md v1.2
- Priority: Medium (not urgent but should be completed within 6 weeks)
- Assigned to: Development team
- Contact: Dean.sockalingum@sw.glasgow.gov.uk

---
**Document Status:** TODO - Implementation not yet started
**Created:** 22 January 2026
**Last Updated:** 22 January 2026
