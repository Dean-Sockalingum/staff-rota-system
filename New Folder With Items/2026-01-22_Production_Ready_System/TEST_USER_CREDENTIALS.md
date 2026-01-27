# Test User Credentials - Senior Leadership Roles
## Created: 22 January 2026

---

## 🔐 Login Credentials

### Head of Service (HOS)
- **Name:** Helen Morrison
- **SAP:** `900001`
- **Password:** `TestHOS123!`
- **Email:** helen.morrison@test.glasgowcc.gov.uk
- **Permissions:** ✅ Full portfolio-wide access

### Improvement, Development & Innovation Manager (IDI)
- **Name:** David Chen  
- **SAP:** `900002`
- **Password:** `TestIDI123!`
- **Email:** david.chen@test.glasgowcc.gov.uk
- **Permissions:** ✅ Full portfolio-wide access

### Service Managers (SM)
#### SM #1
- **Name:** Sarah MacLeod
- **SAP:** `900003`
- **Password:** `TestSM123!`
- **Email:** sarah.macleod@test.glasgowcc.gov.uk
- **Permissions:** ✅ Full portfolio-wide access

#### SM #2
- **Name:** James Patterson
- **SAP:** `900004`
- **Password:** `TestSM123!`
- **Email:** james.patterson@test.glasgowcc.gov.uk
- **Permissions:** ✅ Full portfolio-wide access

### Operations Managers (OM)
#### OM #1
- **Name:** Rachel Foster
- **SAP:** `900005`
- **Password:** `TestOM123!`
- **Email:** rachel.foster@test.glasgowcc.gov.uk
- **Permissions:** ✅ Full portfolio-wide access

#### OM #2
- **Name:** Michael Johnson
- **SAP:** `900006`
- **Password:** `TestOM123!`
- **Email:** michael.johnson@test.glasgowcc.gov.uk
- **Permissions:** ✅ Full portfolio-wide access

---

## ✅ Expected Access for ALL Senior Leadership Roles

All six test users should have **EQUAL ACCESS** to:

### Strategic Features
- ✅ Executive/Strategic Dashboard
- ✅ Portfolio-wide view of all 5 care homes
- ✅ Multi-home performance comparison
- ✅ Organizational improvement plans

### Care Inspectorate Integration
- ✅ CI inspection reports for all homes
- ✅ Quality Framework ratings (all homes)
- ✅ Requirements tracking (portfolio)
- ✅ Automated annual report imports

### Service Improvement Planning
- ✅ ML-generated improvement plans
- ✅ Action tracking across all homes
- ✅ Progress monitoring
- ✅ Evidence linking

### Operational Management
- ✅ Full rota management (all homes)
- ✅ Smart rota generation
- ✅ Shift pattern library access
- ✅ Leave approval configuration
- ✅ Leave calendar (all homes)

### Financial Management
- ✅ Budget tracking (portfolio + all homes)
- ✅ Agency cost analysis
- ✅ Overtime monitoring
- ✅ Cost per shift analysis
- ✅ Budget forecasting

### Compliance & Quality
- ✅ Training compliance (portfolio)
- ✅ Supervision tracking (all homes)
- ✅ WTD compliance monitoring
- ✅ Care plan reviews (portfolio)
- ✅ Incident tracking (portfolio)

### Analytics & Reporting
- ✅ All strategic reports
- ✅ All operational reports
- ✅ Benchmarking tools
- ✅ Trend analysis
- ✅ PDF exports

### AI & Automation
- ✅ AI assistant queries
- ✅ Auto-leave approval configuration
- ✅ Smart staff matching
- ✅ ML forecasting
- ✅ Automated alerts

---

## 🧪 Testing Checklist

### Login Testing
- [ ] Login as Helen Morrison (HOS) - SAP: 900001
- [ ] Login as David Chen (IDI) - SAP: 900002
- [ ] Login as Sarah MacLeod (SM) - SAP: 900003
- [ ] Login as Rachel Foster (OM) - SAP: 900005

### Dashboard Access
- [ ] Verify executive dashboard is visible
- [ ] Confirm portfolio view shows all 5 homes
- [ ] Check strategic metrics are displayed
- [ ] Verify CI integration data appears

### Permission Verification
- [ ] Test rota creation for all homes
- [ ] Test leave approval across homes
- [ ] Test budget report access
- [ ] Test service improvement plan creation
- [ ] Test AI assistant access
- [ ] Test report generation

### Equality Verification
- [ ] Confirm HOS sees same data as SM
- [ ] Confirm IDI sees same data as OM
- [ ] Confirm all 4 roles have identical menus
- [ ] Confirm no features are role-restricted

---

## 🚀 Quick Start Testing

### 1. Start the Server
```bash
cd "/Users/deansockalingum/Desktop/Staff_Rota_Backups/New Folder With Items/2026-01-22_Production_Ready_System"
./venv/bin/python manage.py runserver
```

### 2. Navigate to Login
```
http://localhost:8000/login
```

### 3. Test Each Role
Login with each SAP number and verify full access

### 4. Key URLs to Test
- `/` - Home dashboard
- `/senior-dashboard/` - Executive dashboard
- `/rota/` - Rota management
- `/ci-reports/` - Care Inspectorate integration
- `/improvement-plans/` - Service improvement planning
- `/budget/` - Budget tracking
- `/ai-assistant/` - AI assistant

---

## 🔍 Verification Commands

### List All Test Users
```bash
./venv/bin/python manage.py shell -c "from scheduling.models import User; users = User.objects.filter(sap__startswith='900').select_related('role'); [print(f'{u.sap}: {u.full_name} - {u.role.name}') for u in users]"
```

### Check Permissions
```bash
./venv/bin/python manage.py shell -c "from scheduling.models import User; u = User.objects.get(sap='900001'); print(f'HOS User: {u.full_name}'); print(f'  Can View All Homes: {u.can_view_all_homes}'); print(f'  Is Senior Leadership: {u.is_senior_leadership}'); print(f'  Can Access Executive Dashboard: {u.can_access_executive_dashboard}')"
```

### Delete Test Users (If Needed)
```bash
./venv/bin/python manage.py shell -c "from scheduling.models import User; User.objects.filter(sap__startswith='900').delete(); print('✅ All test users deleted')"
```

### Recreate Test Users
```bash
./venv/bin/python create_test_users.py
```

---

## 📝 Notes

- All test users have `is_staff=True` for admin access
- All test users have `is_active=True`
- SAP numbers start with `900` to distinguish from real users
- Passwords follow format: `Test[ROLE]123!`
- Email domain: `@test.glasgowcc.gov.uk`

---

## ⚠️ Security Notes

**IMPORTANT:** These are test credentials only!

- **DO NOT** use these credentials in production
- **DO NOT** commit passwords to version control
- **DELETE** test users before production deployment
- **CHANGE** all passwords in production environment

---

## 🎯 Success Criteria

✅ All 6 test users created successfully  
✅ All users have correct roles assigned  
✅ All users have SMT=True flag  
✅ All users have can_view_all_homes=True  
✅ All users have can_access_executive_dashboard=True  
✅ HOS, IDI, SM, OM have equal permissions  
✅ All roles can login successfully  
✅ Executive dashboard accessible to all 4 roles  

---

**Created:** 22 January 2026  
**Location:** `/Users/deansockalingum/Desktop/Staff_Rota_Backups/New Folder With Items/2026-01-22_Production_Ready_System/`  
**Script:** `create_test_users.py`

