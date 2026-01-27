# Production Site Health Check - demotherota.co.uk

**Date**: 27 January 2026  
**Environment**: PRODUCTION (Ubuntu Server)  
**Site**: https://demotherota.co.uk  
**Purpose**: Comprehensive system health review before deploying new features

---

## 🎯 OBJECTIVES

1. **Verify all existing functionality is working correctly**
2. **Identify any production issues or errors**
3. **Check system performance and stability**
4. **Document current production state**
5. **Create action plan for any remediation needed**

---

## 📋 HEALTH CHECK CHECKLIST

### 1. INFRASTRUCTURE & ACCESSIBILITY

- [ ] **Site Accessible**
  - [ ] HTTPS working (SSL certificate valid)
  - [ ] Domain resolves correctly
  - [ ] No DNS issues
  - [ ] Page loads without timeout

- [ ] **Server Health**
  - [ ] SSH login successful
  - [ ] Disk space sufficient (< 80% full)
  - [ ] Memory usage acceptable
  - [ ] CPU load normal
  - [ ] No process crashes

- [ ] **Database**
  - [ ] PostgreSQL/MySQL running
  - [ ] Database connections successful
  - [ ] No table corruption
  - [ ] Backup systems active
  - [ ] Last backup timestamp recent

---

### 2. AUTHENTICATION & USERS

- [ ] **Login System**
  - [ ] Login page loads
  - [ ] Successful authentication works
  - [ ] Failed login handled correctly
  - [ ] Password reset functional
  - [ ] Session management working
  - [ ] Logout works properly

- [ ] **User Management**
  - [ ] User list accessible
  - [ ] User creation works
  - [ ] User editing works
  - [ ] Permissions enforced correctly
  - [ ] Role-based access working

---

### 3. CORE SCHEDULING FUNCTIONS

- [ ] **Rota Management**
  - [ ] Rota page loads without errors
  - [ ] Shifts display correctly
  - [ ] Shift creation works
  - [ ] Shift editing works
  - [ ] Shift deletion works
  - [ ] No missing data or blank cells

- [ ] **Pattern Overview**
  - [ ] Page loads without errors
  - [ ] 3-week view displays correctly
  - [ ] Unit colors showing properly
  - [ ] Filtering works (home, unit, date range)
  - [ ] Unit reassignment functional
  - [ ] **NOTE**: Leave integration NOT yet deployed (testing required)

- [ ] **Staff Assignment**
  - [ ] Staff-to-unit assignments correct
  - [ ] Primary care homes set correctly
  - [ ] No orphaned staff records
  - [ ] Staff profiles complete

---

### 4. LEAVE MANAGEMENT

- [ ] **Leave Requests**
  - [ ] Leave request form works
  - [ ] Submit request successful
  - [ ] Approval workflow functional
  - [ ] Leave balance calculations accurate
  - [ ] Calendar display correct

- [ ] **Leave Balances**
  - [ ] Annual leave allowance showing
  - [ ] Leave taken tracking accurate
  - [ ] Remaining leave correct
  - [ ] Carryover calculations working

---

### 5. ABSENCE MANAGEMENT

- [ ] **Sickness Records**
  - [ ] Sickness reporting works
  - [ ] Bradford Factor calculating
  - [ ] Return-to-work triggers active
  - [ ] Sickness patterns tracking
  - [ ] Reports generating correctly

- [ ] **Absence Workflow**
  - [ ] Automated cover requests working
  - [ ] Shift reallocation attempting
  - [ ] OT offers being sent
  - [ ] Agency escalation functional
  - [ ] Manager notifications sending

---

### 6. NOTIFICATIONS

- [ ] **System Notifications**
  - [ ] Notifications displaying in UI
  - [ ] Notification counts accurate
  - [ ] Read/unread status working
  - [ ] Notification priorities correct
  - [ ] Action links functional

- [ ] **Email Notifications**
  - [ ] Email queue processing
  - [ ] Emails being sent
  - [ ] Email templates correct
  - [ ] No emails stuck in queue
  - [ ] Unsubscribe links working

- [ ] **SMS Notifications** (if enabled)
  - [ ] SMS integration active
  - [ ] SMS sending successfully
  - [ ] Opt-in/opt-out working

---

### 7. INCIDENT MANAGEMENT

- [ ] **Incident Reporting**
  - [ ] Incident form accessible
  - [ ] Incident submission works
  - [ ] Reference numbers generating
  - [ ] Incident list displaying

- [ ] **Incident Workflows**
  - [ ] Investigation workflows active
  - [ ] RCA (Root Cause Analysis) working
  - [ ] Safety action plans functional
  - [ ] Trend analysis displaying

---

### 8. QUALITY & AUDITS

- [ ] **Quality Audits**
  - [ ] Audit forms accessible
  - [ ] Audit submission works
  - [ ] Scoring calculations correct
  - [ ] Reports generating

- [ ] **Compliance**
  - [ ] CQC compliance tracking active
  - [ ] Mandatory training tracking working
  - [ ] Document management functional

---

### 9. REPORTING

- [ ] **Standard Reports**
  - [ ] Staff reports generating
  - [ ] Shift reports accurate
  - [ ] Absence reports working
  - [ ] Financial reports calculating

- [ ] **AI Assistant Reports**
  - [ ] AI chatbot accessible
  - [ ] Report generation working
  - [ ] Data queries accurate
  - [ ] Export functionality working

---

### 10. PERFORMANCE & ERRORS

- [ ] **Page Load Times**
  - [ ] Home page: < 3 seconds
  - [ ] Rota page: < 5 seconds
  - [ ] Reports: < 10 seconds
  - [ ] No timeout errors

- [ ] **Error Logs**
  - [ ] Check Django error log
  - [ ] Check Nginx/Apache error log
  - [ ] Check database error log
  - [ ] No critical errors in last 7 days

- [ ] **Database Performance**
  - [ ] Query execution times acceptable
  - [ ] No slow queries (> 5 seconds)
  - [ ] Indexes optimized
  - [ ] No table locks

---

## 🔍 DETAILED INVESTIGATION AREAS

### A. Database Integrity

Commands to run:
```bash
# SSH to server
ssh user@demotherota.co.uk

# Check Django database state
cd /path/to/project
source venv/bin/activate
python manage.py check
python manage.py migrate --check

# Check for orphaned records
python manage.py shell
>>> from scheduling.models import User, Shift, Unit, CareHome
>>> # Check for staff without units
>>> User.objects.filter(unit__isnull=True).count()
>>> # Check for shifts without staff
>>> Shift.objects.filter(user__isnull=True).count()
```

### B. Log Analysis

```bash
# Django logs
tail -100 /var/log/django/production.log
grep -i "error\|critical\|exception" /var/log/django/production.log | tail -50

# Nginx logs
tail -100 /var/log/nginx/error.log
grep "500\|502\|503\|504" /var/log/nginx/access.log | tail -50

# System logs
dmesg | tail -50
journalctl -u django -n 100
```

### C. Performance Analysis

```bash
# Check server resources
htop
df -h
free -m

# Database queries
# (PostgreSQL example)
sudo -u postgres psql rota_db
SELECT * FROM pg_stat_activity WHERE state = 'active';
SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 20;
```

---

## 🐛 ISSUE TRACKING

### Issues Found:

| # | Category | Severity | Description | Status |
|---|----------|----------|-------------|--------|
| 1 |          |          |             |        |
| 2 |          |          |             |        |
| 3 |          |          |             |        |

### Severity Levels:
- **CRITICAL**: System down, data loss, security breach
- **HIGH**: Major functionality broken, affects many users
- **MEDIUM**: Feature partially working, workaround exists
- **LOW**: Minor UI issue, edge case, cosmetic

---

## 📊 SYSTEM STATISTICS

### Current Production State:

**Users**:
- Total staff: _____
- Active users: _____
- Care homes: _____
- Units: _____

**Data Volume**:
- Shifts (last 30 days): _____
- Leave requests (pending): _____
- Sickness absences (active): _____
- Incidents (last 30 days): _____

**Performance**:
- Average page load: _____ seconds
- Database size: _____ GB
- Disk usage: _____ %
- Memory usage: _____ %

**Errors**:
- Critical errors (7 days): _____
- Warnings (7 days): _____
- 500 errors (24 hours): _____

---

## ✅ SIGN-OFF

**Health Check Completed By**: _________________  
**Date/Time**: _________________  
**Overall Status**: [ ] HEALTHY  [ ] NEEDS ATTENTION  [ ] CRITICAL ISSUES  

**Summary**:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

**Action Items**:
1. _________________________________________________________________
2. _________________________________________________________________
3. _________________________________________________________________

**Safe for New Deployments**: [ ] YES  [ ] NO  [ ] WITH CAUTIONS

---

## 🚀 POST-REVIEW NEXT STEPS

### If HEALTHY:
1. Schedule UAT for leave integration
2. Plan deployment window
3. Prepare rollback plan
4. Notify stakeholders

### If NEEDS ATTENTION:
1. Prioritize issues (Critical → High → Medium)
2. Create tickets for each issue
3. Assign developers
4. Set remediation timeline
5. Re-test after fixes

### If CRITICAL ISSUES:
1. **DO NOT DEPLOY** any new features
2. Focus 100% on fixing critical issues
3. Escalate to senior developers
4. Consider rollback to last known good state
5. Implement hotfixes immediately

---

**Document Version**: 1.0  
**Last Updated**: 27 January 2026  
**Next Review Due**: After production check complete
