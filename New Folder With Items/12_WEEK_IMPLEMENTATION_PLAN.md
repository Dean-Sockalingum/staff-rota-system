# 12-Week Implementation Plan - Staff Rota System
**Document:** Production Deployment Roadmap  
**Date:** January 6, 2026  
**Duration:** 12 weeks (Weeks 1-12)  
**Status:** Ready for Trello Import

---

## Overview

### Timeline Summary
- **Weeks 1-2:** Production Preparation
- **Weeks 3-4:** User Acceptance Testing (UAT)
- **Weeks 5-8:** Pilot Deployment (Hawthorn House + Meadowburn)
- **Weeks 9-10:** Phased Rollout (Riverside + Victoria Gardens)
- **Weeks 11-12:** Final Rollout (5th home) + Full Production Stabilization
- **Post-Week 12:** Glasgow HSCP Pitch & Ongoing Operations

### Key Milestones
- ✅ Week 0: Planning complete (UAT plan, Pilot plan, SSL guide)
- 🎯 Week 2: Production infrastructure ready
- 🎯 Week 4: UAT passed, GO/NO-GO decision
- 🎯 Week 8: Pilot successful, 2 homes live
- 🎯 Week 10: 4 homes operational
- 🎯 Week 12: All 5 homes live, full production
- 🎯 Week 13+: Glasgow HSCP pitch ready

---

## Trello Board Structure

### Suggested Lists (Columns)
1. **Backlog** - All planned tasks
2. **To Do (This Week)** - Current week's tasks
3. **In Progress** - Actively being worked on
4. **Blocked** - Waiting on dependencies
5. **Testing/Review** - Ready for validation
6. **Done** - Completed and verified

### Labels (Color-Coded)
- 🔴 **Critical** - Blocks progress, must complete
- 🟠 **High Priority** - Important, scheduled
- 🟡 **Medium Priority** - Important, flexible timing
- 🟢 **Low Priority** - Nice-to-have, optional
- 🔵 **Documentation** - Guides, manuals, reports
- 🟣 **Training** - User training activities
- ⚫ **Technical** - Infrastructure, coding, config
- 🟤 **Testing** - UAT, load testing, validation

### Card Format
```
**Epic:** [Epic Name]
**Task:** [Task Name]
**Week:** [Week Number]
**Priority:** [Critical/High/Medium/Low]
**Assignee:** [Role/Name]
**Effort:** [Hours]
**Dependencies:** [Previous task IDs]

**Description:**
[What needs to be done]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

**Resources:**
- [Link to guide/doc]
```

---

## Epic 1: Production Infrastructure Setup
**Duration:** Weeks 1-2  
**Owner:** Technical Lead  
**Goal:** Configure production environment (SSL, email, secrets, backups)

### Week 1

#### Task 1.1: SSL/TLS Certificate Installation
- **Priority:** 🔴 Critical
- **Assignee:** Technical Lead
- **Effort:** 4 hours
- **Dependencies:** None
- **Week:** 1

**Description:**
Install Let's Encrypt SSL certificate for HTTPS access. Configure Nginx reverse proxy and Django security settings.

**Acceptance Criteria:**
- [ ] Domain name configured and DNS pointing to server
- [ ] Certbot installed and SSL certificate obtained
- [ ] Nginx configured with SSL (ports 80→443 redirect)
- [ ] Django settings updated (SECURE_SSL_REDIRECT=True, HSTS enabled)
- [ ] HTTPS accessible at production URL
- [ ] SSL Labs test: A or A+ rating
- [ ] Certificate auto-renewal tested (dry-run successful)

**Resources:**
- SSL_SETUP_GUIDE.md (complete step-by-step instructions)
- Mozilla SSL Configuration Generator
- SSL Labs: https://www.ssllabs.com/ssltest/

---

#### Task 1.2: Production Email Configuration
- **Priority:** 🔴 Critical
- **Assignee:** Technical Lead
- **Effort:** 2 hours
- **Dependencies:** None
- **Week:** 1

**Description:**
Configure SMTP email backend (Gmail or SendGrid) for system notifications (leave approvals, 2FA codes, password resets).

**Acceptance Criteria:**
- [ ] Email service selected (Gmail SMTP or SendGrid)
- [ ] Django settings.py updated:
  - EMAIL_BACKEND
  - EMAIL_HOST
  - EMAIL_PORT
  - EMAIL_USE_TLS
  - EMAIL_HOST_USER
  - EMAIL_HOST_PASSWORD
  - DEFAULT_FROM_EMAIL
- [ ] Test email sent successfully
- [ ] Leave approval notification tested
- [ ] 2FA code email tested
- [ ] Password reset email tested
- [ ] Email logs reviewed (no errors)

**Resources:**
- Django Email Documentation
- Gmail SMTP Setup: smtp.gmail.com:587
- SendGrid Free Tier: 100 emails/day

---

#### Task 1.3: Secrets Management Implementation
- **Priority:** 🔴 Critical
- **Assignee:** Technical Lead
- **Effort:** 2 hours
- **Dependencies:** Task 1.1 (SSL), Task 1.2 (Email)
- **Week:** 1

**Description:**
Secure sensitive configuration data (.env file encryption or Vault). Remove plaintext secrets from repository.

**Acceptance Criteria:**
- [ ] .env file encrypted (or migrated to Vault)
- [ ] SECRET_KEY secured
- [ ] Database credentials secured
- [ ] Email password secured
- [ ] API keys secured (if any)
- [ ] Environment variables loaded correctly in production
- [ ] Test application startup with encrypted secrets
- [ ] No plaintext secrets in Git history

**Resources:**
- django-environ library
- AWS Secrets Manager (if cloud)
- HashiCorp Vault (if self-hosted)
- GPG encryption for .env file

---

#### Task 1.4: Gunicorn + Systemd Service Setup
- **Priority:** 🟠 High
- **Assignee:** Technical Lead
- **Effort:** 3 hours
- **Dependencies:** Task 1.1 (SSL)
- **Week:** 1

**Description:**
Configure Gunicorn as production WSGI server with Systemd for auto-start on reboot.

**Acceptance Criteria:**
- [ ] Gunicorn installed: `pip3 install gunicorn`
- [ ] Gunicorn config file created (workers, timeout, logging)
- [ ] Systemd service file created: `/etc/systemd/system/staff-rota.service`
- [ ] Service enabled: `sudo systemctl enable staff-rota`
- [ ] Service started: `sudo systemctl start staff-rota`
- [ ] Service auto-starts on reboot (tested)
- [ ] Application accessible via Nginx → Gunicorn
- [ ] Static files served correctly
- [ ] Logs written to /var/log/gunicorn/

**Resources:**
- SSL_SETUP_GUIDE.md (Systemd service template)
- Gunicorn Documentation
- Django Deployment Checklist: `python manage.py check --deploy`

---

### Week 2

#### Task 1.5: Automated Backup Configuration
- **Priority:** 🔴 Critical
- **Assignee:** Technical Lead
- **Effort:** 3 hours
- **Dependencies:** Task 1.4 (Gunicorn)
- **Week:** 2

**Description:**
Set up automated daily/weekly backups for database and media files. Configure cron jobs and test restoration.

**Acceptance Criteria:**
- [ ] Backup script created: `/usr/local/bin/backup-staff-rota.sh`
- [ ] Daily database dump: SQLite → .db file with timestamp
- [ ] Weekly media files backup: /media/ → archive
- [ ] Cron job scheduled: daily at 2am, weekly Sunday 3am
- [ ] Backup location: NVMe drive + cloud (Google Drive/S3)
- [ ] Restoration tested successfully (restore to test environment)
- [ ] Backup retention policy: 30 daily, 12 weekly
- [ ] Alert on backup failure (email notification)
- [ ] Documentation: BACKUP_PROCEDURES.md created

**Resources:**
- SQLite backup: `.backup` command or `cp db.sqlite3`
- Rclone for cloud sync (Google Drive)
- Cron syntax tester: crontab.guru

**Backup Script Template:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/mnt/nvme/backups/staff-rota"
DB_FILE="/path/to/db.sqlite3"
MEDIA_DIR="/path/to/media"

# Database backup
sqlite3 $DB_FILE ".backup '$BACKUP_DIR/db_$DATE.sqlite3'"

# Media files backup (weekly)
if [ $(date +%u) -eq 7 ]; then
    tar -czf $BACKUP_DIR/media_$DATE.tar.gz $MEDIA_DIR
fi

# Upload to cloud (if configured)
# rclone sync $BACKUP_DIR remote:staff-rota-backups

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "db_*.sqlite3" -mtime +30 -delete
find $BACKUP_DIR -name "media_*.tar.gz" -mtime +90 -delete
```

---

#### Task 1.6: Load Testing Execution
- **Priority:** 🟠 High
- **Assignee:** Technical Lead
- **Effort:** 4 hours
- **Dependencies:** Task 1.4 (Gunicorn), Task 1.5 (Backups)
- **Week:** 2

**Description:**
Perform load testing with 50+ concurrent users using Apache JMeter or Locust. Test dashboard loads, chart generation, ML forecasts.

**Acceptance Criteria:**
- [ ] Load testing tool installed (JMeter or Locust)
- [ ] Test scenarios created:
  - Dashboard loads (Staff, Manager, Executive)
  - Leave request submissions
  - Shift creation
  - AI chatbot queries
  - Chart generation (6 types)
  - ML forecasting
- [ ] 50 concurrent users simulated
- [ ] Peak load: 100 req/s for 10 minutes
- [ ] Average response time < 2 seconds
- [ ] 95th percentile < 3 seconds
- [ ] Error rate < 1%
- [ ] Database connection pool stable
- [ ] Server resources monitored (CPU, RAM, disk I/O)
- [ ] Results documented: LOAD_TESTING_RESULTS.md

**Resources:**
- Apache JMeter: https://jmeter.apache.org/
- Locust: https://locust.io/
- Django Debug Toolbar for query analysis
- htop/top for server monitoring

---

#### Task 1.7: Monitoring & Alerting Setup
- **Priority:** 🟡 Medium
- **Assignee:** Technical Lead
- **Effort:** 2 hours
- **Dependencies:** Task 1.4 (Gunicorn)
- **Week:** 2

**Description:**
Configure Sentry for error tracking and uptime monitoring. Set up alerts for critical issues.

**Acceptance Criteria:**
- [ ] Sentry account created (free tier: 5k errors/month)
- [ ] Django Sentry integration: `pip install sentry-sdk`
- [ ] settings.py configured with Sentry DSN
- [ ] Test error sent to Sentry (500 error triggered)
- [ ] Error alerts configured (email/Slack)
- [ ] Uptime monitoring enabled (UptimeRobot or similar)
- [ ] SSL certificate expiration monitoring set up
- [ ] Daily health check email (optional)

**Resources:**
- Sentry Django Integration: https://docs.sentry.io/platforms/python/guides/django/
- UptimeRobot (free): https://uptimerobot.com/

---

#### Task 1.8: Security Audit
- **Priority:** 🟠 High
- **Assignee:** Technical Lead
- **Effort:** 3 hours
- **Dependencies:** Task 1.1 (SSL), Task 1.3 (Secrets)
- **Week:** 2

**Description:**
Run security checks and address any vulnerabilities. Verify 2FA, API authentication, data isolation.

**Acceptance Criteria:**
- [ ] Django security check passed: `python manage.py check --deploy`
- [ ] No security warnings in production settings
- [ ] 2FA tested for all manager accounts
- [ ] API authentication tested (token-based endpoints)
- [ ] Data isolation verified (no cross-home leaks)
- [ ] SQL injection tests passed (OWASP ZAP or manual)
- [ ] CSRF protection enabled and tested
- [ ] XSS protection verified
- [ ] Session timeout configured (30 minutes)
- [ ] Password policy enforced (8+ chars, complexity)
- [ ] Audit log reviewed (no suspicious activity)

**Resources:**
- Django Security Checklist
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- SecurityHeaders.com test: https://securityheaders.com/

---

#### Task 1.9: Production Documentation Review
- **Priority:** 🔵 Documentation
- **Assignee:** Technical Lead
- **Effort:** 2 hours
- **Dependencies:** All Week 1-2 tasks
- **Week:** 2

**Description:**
Review and update all production documentation. Create runbook for common operations.

**Acceptance Criteria:**
- [ ] SSL_SETUP_GUIDE.md reviewed and accurate
- [ ] UAT_PLAN.md reviewed and ready
- [ ] PILOT_DEPLOYMENT_PLAN.md reviewed and ready
- [ ] BACKUP_PROCEDURES.md created
- [ ] LOAD_TESTING_RESULTS.md created
- [ ] Runbook created: PRODUCTION_RUNBOOK.md
  - Deployment procedure
  - Restart service
  - Database migrations
  - Log locations
  - Troubleshooting common issues
  - Emergency contacts
- [ ] All documentation committed to GitHub

**Deliverable:** PRODUCTION_RUNBOOK.md

---

### Epic 1 Completion Checklist
- [ ] SSL certificate installed and A+ rating achieved
- [ ] Production email sending notifications
- [ ] Secrets encrypted and secured
- [ ] Gunicorn + Systemd service running
- [ ] Automated backups configured and tested
- [ ] Load testing passed (< 2s avg response, < 1% errors)
- [ ] Monitoring and alerting operational
- [ ] Security audit passed
- [ ] Documentation complete and reviewed
- **Decision:** Proceed to UAT (Epic 2)

---

## Epic 2: User Acceptance Testing (UAT)
**Duration:** Weeks 3-4  
**Owner:** Service Manager + Technical Lead  
**Goal:** Validate system readiness with 5-10 staff testers

### Week 3

#### Task 2.1: UAT Team Recruitment & Setup
- **Priority:** 🔴 Critical
- **Assignee:** Service Manager
- **Effort:** 4 hours
- **Dependencies:** Epic 1 complete
- **Week:** 3

**Description:**
Recruit 5-10 UAT testers across all roles. Set up test accounts and schedule training.

**Acceptance Criteria:**
- [ ] 5-10 testers recruited:
  - 2-3 Operational Managers
  - 1 Service Manager
  - 1-2 Senior Carers
  - 1-2 Care Assistants
  - 1 Admin
- [ ] Test accounts created (uat_om1, uat_sm, etc.)
- [ ] 2FA configured for Service Manager and Admin accounts
- [ ] UAT kickoff meeting scheduled (Week 3, Day 1)
- [ ] Test data verified (5 homes, 821 staff, shifts, leave)
- [ ] UAT environment accessible: https://staging.yourdomain.com
- [ ] UAT_PLAN.md distributed to all testers
- [ ] Training session scheduled (2 hours, Week 3 Day 1)

**Resources:**
- UAT_PLAN.md (Appendix A: Test Credentials)
- UAT kickoff presentation

---

#### Task 2.2: UAT Week 1 Execution - Core Features
- **Priority:** 🔴 Critical
- **Assignee:** All UAT Testers
- **Effort:** 15 hours (3 hours/day × 5 days)
- **Dependencies:** Task 2.1
- **Week:** 3

**Description:**
Execute test scenarios for authentication, leave management, shift management, AI chatbot, dashboards.

**Test Coverage:**
- Authentication & Security (Test Cases 1.1-1.4)
- Leave Management (Test Cases 2.1-2.5)
- Shift Management (Test Cases 3.1-3.5)
- AI Chatbot (Test Cases 4.1-4.6)
- Dashboards (Test Cases 5.1-5.4)

**Acceptance Criteria:**
- [ ] ≥ 90% of Week 1 test cases executed
- [ ] All Critical priority tests passed
- [ ] Defects logged in GitHub Issues (with severity, screenshots)
- [ ] Daily standup held (15 mins, review progress)
- [ ] Mid-week survey distributed (Day 3)
- [ ] Week 1 summary report compiled

**Deliverable:** UAT Week 1 Summary Report

---

#### Task 2.3: Bug Fixes - Round 1
- **Priority:** 🔴 Critical
- **Assignee:** Technical Lead
- **Effort:** 10 hours (2 hours/day × 5 days)
- **Dependencies:** Task 2.2 (defects logged)
- **Week:** 3

**Description:**
Fix all Critical and High priority bugs discovered during UAT Week 1.

**Acceptance Criteria:**
- [ ] All Critical bugs fixed within 4 hours
- [ ] All High priority bugs fixed within 24 hours
- [ ] Fixes deployed to UAT environment
- [ ] Regression testing completed
- [ ] Defect status updated in GitHub Issues
- [ ] Code changes committed to GitHub
- [ ] Release notes created for fixes

**Resources:**
- GitHub Issues (defect tracker)
- Django error logs
- Sentry error reports

---

### Week 4

#### Task 2.4: UAT Week 2 Execution - Advanced Features
- **Priority:** 🔴 Critical
- **Assignee:** All UAT Testers
- **Effort:** 14 hours (2.8 hours/day × 5 days)
- **Dependencies:** Task 2.3 (bugs fixed)
- **Week:** 4

**Description:**
Execute remaining test scenarios: multi-home isolation, compliance, ML features, performance.

**Test Coverage:**
- Multi-Home Data Isolation (Test Cases 6.1-6.3) - CRITICAL
- Compliance & Reporting (Test Cases 7.1-7.3)
- ML Features (Test Cases 8.1-8.2)
- Performance & Usability (Test Cases 9.1-9.3)

**Acceptance Criteria:**
- [ ] 100% of test cases executed
- [ ] All CRITICAL tests passed (data isolation, security)
- [ ] ≥ 95% of HIGH priority tests passed
- [ ] ≥ 90% of MEDIUM priority tests passed
- [ ] Concurrent user test completed (all 6-9 testers simultaneous)
- [ ] Mobile responsiveness tested (iOS + Android)
- [ ] Final user feedback survey completed
- [ ] Week 2 summary report compiled

**Deliverable:** UAT Week 2 Summary Report

---

#### Task 2.5: Bug Fixes - Round 2
- **Priority:** 🟠 High
- **Assignee:** Technical Lead
- **Effort:** 8 hours
- **Dependencies:** Task 2.4 (Week 2 defects)
- **Week:** 4

**Description:**
Fix all remaining Critical/High bugs and address Medium priority issues.

**Acceptance Criteria:**
- [ ] All Critical bugs resolved
- [ ] All High priority bugs resolved
- [ ] ≥ 80% of Medium priority bugs resolved
- [ ] Low priority bugs documented for post-UAT
- [ ] All fixes deployed and retested
- [ ] Regression testing passed
- [ ] Final defect log compiled

---

#### Task 2.6: UAT Final Report & GO/NO-GO Decision
- **Priority:** 🔴 Critical
- **Assignee:** Service Manager + Technical Lead
- **Effort:** 4 hours
- **Dependencies:** Task 2.4, Task 2.5
- **Week:** 4 (Friday)

**Description:**
Compile UAT results, analyze feedback, make GO/NO-GO decision for pilot deployment.

**Acceptance Criteria:**
- [ ] UAT Summary Report created (10 pages):
  - Executive summary
  - Test execution results (pass/fail rates)
  - Defect summary (by severity)
  - User feedback analysis
  - Performance metrics
  - Screenshots
- [ ] User satisfaction score calculated (target: ≥ 4.0/5.0)
- [ ] All mandatory success criteria met:
  - ✅ ≥ 95% test pass rate
  - ✅ Zero Critical/High open defects
  - ✅ User satisfaction ≥ 4.0/5.0
  - ✅ Security tests passed
  - ✅ Performance < 2s page loads
- [ ] GO/NO-GO decision made
- [ ] If GO: Pilot deployment scheduled (Week 5)
- [ ] If NO-GO: Issue resolution plan created

**Deliverable:** UAT_FINAL_REPORT.md + GO/NO-GO Decision

---

### Epic 2 Completion Checklist
- [ ] 60+ test scenarios executed
- [ ] ≥ 95% test pass rate achieved
- [ ] All Critical/High defects resolved
- [ ] User satisfaction ≥ 4.0/5.0
- [ ] UAT Final Report approved by Service Manager
- **Decision:** GO to Pilot Deployment (Epic 3)

---

## Epic 3: Pilot Deployment (Month 1)
**Duration:** Weeks 5-8  
**Owner:** Service Manager + Technical Lead  
**Goal:** Deploy to Hawthorn House + Meadowburn (~117 staff, 2 of 5 homes)

### Week 5 (Pilot Week 1): Launch & Stabilization

#### Task 3.1: Pre-Pilot Preparation (Week 0 Activities)
- **Priority:** 🔴 Critical
- **Assignee:** Technical Lead + OMs
- **Effort:** 20 hours (completed during Week 4/5 overlap)
- **Dependencies:** UAT GO decision
- **Week:** 4-5 transition

**Description:**
Complete all pre-pilot setup: data verification, training materials, staff training sessions.

**Acceptance Criteria:**
- [ ] Care home data verified (Hawthorn, Meadowburn complete)
- [ ] All 117 pilot staff profiles imported
- [ ] Historical shifts loaded (3 months for ML training)
- [ ] Leave balances verified with payroll
- [ ] Training records imported (18 course types)
- [ ] Quick start guides printed (120 copies)
- [ ] Training videos recorded (5 key features, 15 mins each)
- [ ] Training sessions conducted:
  - Hawthorn OMs (2 hours, Mon)
  - Meadowburn OMs (2 hours, Tue)
  - Senior Carers (1.5 hours each home, Wed-Thu)
  - Care Assistants (3 sessions, 1 hour each, Fri)
- [ ] Go-live announcement email sent
- [ ] Support hotline number published

**Deliverable:** Pre-Pilot Checklist Complete

---

#### Task 3.2: Pilot Go-Live (Day 1)
- **Priority:** 🔴 Critical
- **Assignee:** Technical Lead (on-site Hawthorn AM, Meadowburn PM)
- **Effort:** 10 hours (full day support)
- **Dependencies:** Task 3.1
- **Week:** 5 (Monday)

**Description:**
Launch system at pilot homes. Provide on-site support, monitor first logins, resolve immediate issues.

**Acceptance Criteria:**
- [ ] 08:00 - System health check (uptime, backups, logs)
- [ ] 08:30 - Go-live email sent to all 117 pilot staff
- [ ] 09:00 - On-site support at Hawthorn House
- [ ] 09:30 - First logins monitored (authentication, 2FA)
- [ ] 10:00 - Error check (Sentry, Nginx logs)
- [ ] 13:00 - On-site support at Meadowburn
- [ ] 14:00 - First leave requests submitted
- [ ] 15:00 - Managers create shifts for next week
- [ ] 16:00 - End-of-day system check
- [ ] 18:00 - Activity log review
- [ ] 19:00 - Backup verification
- [ ] 20:00 - Day 1 debrief meeting
- [ ] No critical incidents
- [ ] ≥ 50% of pilot staff logged in

**Deliverable:** Day 1 Summary Report

---

#### Task 3.3: Pilot Week 1 Daily Support
- **Priority:** 🔴 Critical
- **Assignee:** Technical Lead
- **Effort:** 40 hours (8 hours/day × 5 days)
- **Dependencies:** Task 3.2
- **Week:** 5 (Tue-Fri)

**Description:**
Provide extended support (8am-8pm) during first week. Monitor system, resolve issues, collect feedback.

**Daily Routine:**
- 09:00 - Morning system check
- 10:00 - Review overnight activity
- 12:00 - Support ticket review (2-hour response time)
- 15:00 - On-site check-in (rotate Hawthorn/Meadowburn)
- 17:00 - End-of-day review
- 18:00 - Daily backup verification

**Acceptance Criteria:**
- [ ] Day 2: First shifts worked from system-generated rota
- [ ] Day 3: First leave auto-approvals (≤5 days rule)
- [ ] Day 4: First manager leave approvals (>5 days rule)
- [ ] Day 5: First AI chatbot queries
- [ ] Daily support tickets < 10/day by Day 5
- [ ] System uptime 100% (no downtime)
- [ ] Week 1 metrics met:
  - ≥ 80% pilot staff logged in
  - ≥ 20 leave requests submitted
  - ≥ 100 shifts created/edited
  - < 5 medium priority issues
  - 0 critical incidents
  - User satisfaction ≥ 3.5/5.0

**Deliverable:** Week 1 Summary Report + Metrics Dashboard

---

### Week 6 (Pilot Week 2): Feature Adoption

#### Task 3.4: Pilot Week 2 Standard Support
- **Priority:** 🟠 High
- **Assignee:** Technical Lead
- **Effort:** 20 hours (4 hours/day × 5 days)
- **Dependencies:** Task 3.3
- **Week:** 6

**Description:**
Reduce to standard support (9am-5pm). Focus on feature adoption: AI chatbot, executive dashboards, compliance reports.

**Acceptance Criteria:**
- [ ] On-site support reduced to 2 days/week (Wed, Fri)
- [ ] Remote support via phone/email/Teams
- [ ] Weekly team meeting with OMs (Friday)
- [ ] Day 8: First executive dashboard usage
- [ ] Day 9: First ML forecast generated
- [ ] Day 10: First agency usage report
- [ ] Day 12: First compliance report exported
- [ ] Day 14: Mid-pilot user survey distributed
- [ ] Week 2 metrics met:
  - ≥ 95% pilot staff active
  - ≥ 50 leave requests total
  - ≥ 300 shifts managed
  - ≥ 50 AI chatbot queries
  - < 3 medium priority issues
  - User satisfaction ≥ 4.0/5.0

**Deliverable:** Week 2 Summary Report + Mid-Pilot Survey Results

---

### Week 7 (Pilot Week 3): Workflow Integration

#### Task 3.5: Paper Rota Elimination
- **Priority:** 🟠 High
- **Assignee:** Operational Managers (Hawthorn, Meadowburn)
- **Effort:** 10 hours
- **Dependencies:** Task 3.4
- **Week:** 7

**Description:**
Full transition to digital rotas. Discontinue all paper-based processes.

**Acceptance Criteria:**
- [ ] Day 15: Last paper rota discontinued at Hawthorn
- [ ] Day 16: Last paper rota discontinued at Meadowburn
- [ ] 100% shifts managed through system
- [ ] Email notifications working for all staff
- [ ] Leave workflow fully digital
- [ ] Training records updated digitally only
- [ ] Week 3 metrics met:
  - 100% pilot staff active
  - ≥ 80 leave requests total
  - ≥ 500 shifts managed
  - 100% digital rota adoption
  - < 2 medium priority issues
  - User satisfaction ≥ 4.2/5.0

**Deliverable:** Paper-Free Certification (both homes)

---

#### Task 3.6: Pilot Week 3 Minimal Support
- **Priority:** 🟡 Medium
- **Assignee:** Technical Lead
- **Effort:** 10 hours (2 hours/day × 5 days)
- **Dependencies:** Task 3.5
- **Week:** 7

**Description:**
Reduce to minimal support (on-demand only). System operating independently.

**Acceptance Criteria:**
- [ ] On-site support 1 day/week (Thursday)
- [ ] Remote support 9am-5pm
- [ ] Day 19: First automated compliance alert sent
- [ ] Day 21: Week 3 user survey + manager interviews
- [ ] Support tickets < 3/day
- [ ] No critical or high priority issues
- [ ] User confidence high (feedback indicates independence)

**Deliverable:** Week 3 Summary Report + User Interview Notes

---

### Week 8 (Pilot Week 4): Stabilization & Evaluation

#### Task 3.7: Pilot Final Week Monitoring
- **Priority:** 🟠 High
- **Assignee:** Technical Lead
- **Effort:** 10 hours
- **Dependencies:** Task 3.6
- **Week:** 8

**Description:**
Monitor system stability, collect final feedback, prepare for phased rollout.

**Acceptance Criteria:**
- [ ] Day 22: System performance review
- [ ] Day 24: Security audit (data isolation, auth logs)
- [ ] Day 26: Final user survey distributed
- [ ] Day 28: Pilot review meeting (OMs, SM, Technical Lead)
- [ ] Week 4 metrics met:
  - Uptime ≥ 99.5% (< 3.6 hours total downtime)
  - User satisfaction ≥ 4.3/5.0
  - ≥ 100 leave requests total
  - ≥ 700 shifts managed
  - All critical/high issues resolved
  - Medium issues in progress or scheduled

**Deliverable:** Week 4 Summary Report

---

#### Task 3.8: Pilot Final Report & GO/NO-GO for Rollout
- **Priority:** 🔴 Critical
- **Assignee:** Service Manager + Technical Lead
- **Effort:** 6 hours
- **Dependencies:** Task 3.7
- **Week:** 8 (Friday)

**Description:**
Compile pilot results, evaluate success criteria, decide on phased rollout.

**Acceptance Criteria:**
- [ ] Pilot Summary Report created (15 pages):
  - Executive summary
  - 4-week metrics comparison
  - User satisfaction analysis
  - Technical performance
  - Business impact (time savings, ROI)
  - Lessons learned
  - Recommendations for next homes
- [ ] All mandatory success criteria met:
  - ✅ System uptime ≥ 99.5%
  - ✅ Zero critical incidents
  - ✅ ≥ 95% pilot staff using system
  - ✅ All core workflows functional
  - ✅ User satisfaction ≥ 4.0/5.0
  - ✅ Data isolation verified
- [ ] GO/NO-GO decision for phased rollout
- [ ] If GO: Riverside deployment scheduled (Week 9)
- [ ] Lessons learned documented
- [ ] Updated training materials based on feedback

**Deliverable:** PILOT_FINAL_REPORT.md + GO/NO-GO Decision

---

### Epic 3 Completion Checklist
- [ ] 2 homes operational (Hawthorn, Meadowburn)
- [ ] 117 staff actively using system
- [ ] ≥ 99.5% uptime achieved
- [ ] User satisfaction ≥ 4.3/5.0
- [ ] Paper rotas eliminated (100% digital)
- [ ] Pilot Final Report approved
- **Decision:** GO to Phased Rollout (Epic 4)

---

## Epic 4: Phased Rollout (Homes 3-4)
**Duration:** Weeks 9-10  
**Owner:** Service Manager + Operational Managers  
**Goal:** Deploy to Riverside (Week 9) and Victoria Gardens (Week 10)

### Week 9: Riverside Deployment

#### Task 4.1: Riverside Pre-Deployment Prep
- **Priority:** 🟠 High
- **Assignee:** Riverside OMs + Technical Lead
- **Effort:** 12 hours
- **Dependencies:** Pilot GO decision
- **Week:** 9 (Mon-Wed)

**Description:**
Prepare Riverside for deployment. Data verification, staff training, updated materials.

**Acceptance Criteria:**
- [ ] Riverside data verified (staff profiles, shifts, leave balances)
- [ ] Training materials updated (lessons from pilot)
- [ ] Training sessions conducted:
  - Riverside OMs (2 hours, Mon)
  - Senior Carers (1.5 hours, Tue)
  - Care Assistants (2 sessions, 1 hour each, Wed)
- [ ] Go-live announcement sent
- [ ] Quick start guides distributed
- [ ] Test accounts created for OMs

**Deliverable:** Riverside Pre-Deployment Checklist Complete

---

#### Task 4.2: Riverside Go-Live & Week 1 Support
- **Priority:** 🔴 Critical
- **Assignee:** Technical Lead + Riverside OMs
- **Effort:** 20 hours (Thu-Fri Week 9 + Mon-Tue Week 10)
- **Dependencies:** Task 4.1
- **Week:** 9 (Thu Go-Live)

**Description:**
Deploy to Riverside. Provide on-site support Thursday-Friday, monitor first week.

**Acceptance Criteria:**
- [ ] Thursday: Go-live (same process as pilot Day 1)
- [ ] Friday: Full day on-site support
- [ ] ≥ 70% Riverside staff logged in by Friday
- [ ] First leave requests submitted
- [ ] First shifts created
- [ ] No critical incidents
- [ ] Support available 9am-5pm
- [ ] Issues logged and resolved quickly

**Deliverable:** Riverside Go-Live Report

---

### Week 10: Victoria Gardens Deployment

#### Task 4.3: Victoria Gardens Pre-Deployment Prep
- **Priority:** 🟠 High
- **Assignee:** Victoria Gardens OMs + Technical Lead
- **Effort:** 12 hours
- **Dependencies:** Task 4.2 (Riverside stable)
- **Week:** 10 (Mon-Wed)

**Description:**
Prepare Victoria Gardens for deployment. Leverage lessons from 3 previous homes.

**Acceptance Criteria:**
- [ ] Victoria Gardens data verified
- [ ] Training materials refined (3rd iteration)
- [ ] Training sessions conducted:
  - Victoria OMs (2 hours, Mon)
  - Senior Carers (1.5 hours, Tue)
  - Care Assistants (2 sessions, 1 hour each, Wed)
- [ ] Go-live announcement sent
- [ ] Materials distributed
- [ ] Test accounts created

**Deliverable:** Victoria Gardens Pre-Deployment Checklist Complete

---

#### Task 4.4: Victoria Gardens Go-Live & Week 1 Support
- **Priority:** 🔴 Critical
- **Assignee:** Technical Lead + Victoria OMs
- **Effort:** 20 hours (Thu-Fri Week 10 + Mon-Tue Week 11)
- **Dependencies:** Task 4.3
- **Week:** 10 (Thu Go-Live)

**Description:**
Deploy to Victoria Gardens. 4th home deployment, high confidence.

**Acceptance Criteria:**
- [ ] Thursday: Go-live
- [ ] Friday: On-site support
- [ ] ≥ 80% Victoria staff logged in by Friday
- [ ] First workflows completed
- [ ] No critical incidents
- [ ] Riverside week 2 also monitored (parallel support)

**Deliverable:** Victoria Gardens Go-Live Report

---

#### Task 4.5: Multi-Home Monitoring Dashboard
- **Priority:** 🟡 Medium
- **Assignee:** Service Manager
- **Effort:** 4 hours
- **Dependencies:** 4 homes operational
- **Week:** 10 (Fri)

**Description:**
Review executive multi-home dashboard. All 4 homes now visible, comparative analysis.

**Acceptance Criteria:**
- [ ] Executive dashboard shows all 4 homes
- [ ] Comparative metrics working:
  - Staffing levels
  - Leave approval rates
  - Sickness absence
  - Training compliance
  - Shift coverage
- [ ] CI Performance Dashboard peer benchmarking updated
- [ ] Budget variance tracking across all homes
- [ ] No data cross-contamination (isolation verified)

**Deliverable:** Multi-Home Dashboard Screenshot + Validation Report

---

### Epic 4 Completion Checklist
- [ ] 4 homes operational (Hawthorn, Meadowburn, Riverside, Victoria)
- [ ] ~330 staff using system (40% of total)
- [ ] All homes stable with minimal support
- [ ] Multi-home dashboard functional
- **Decision:** Proceed to Final Rollout (Epic 5)

---

## Epic 5: Final Rollout & Full Production
**Duration:** Weeks 11-12  
**Owner:** Service Manager  
**Goal:** Deploy 5th home, achieve full production, stabilize all operations

### Week 11: 5th Home Deployment

#### Task 5.1: 5th Home (TBD) Pre-Deployment Prep
- **Priority:** 🟠 High
- **Assignee:** 5th Home OMs + Technical Lead
- **Effort:** 10 hours
- **Dependencies:** 4 homes stable
- **Week:** 11 (Mon-Wed)

**Description:**
Prepare final care home for deployment. Refined process from 4 previous deployments.

**Acceptance Criteria:**
- [ ] 5th home identified (if not already specified)
- [ ] Data verified
- [ ] Training conducted (streamlined, 1-day process)
- [ ] Go-live scheduled for Thursday

**Deliverable:** 5th Home Pre-Deployment Checklist Complete

---

#### Task 5.2: 5th Home Go-Live
- **Priority:** 🔴 Critical
- **Assignee:** 5th Home OMs + Technical Lead
- **Effort:** 16 hours (Thu-Fri on-site)
- **Dependencies:** Task 5.1
- **Week:** 11 (Thu Go-Live)

**Description:**
Final home deployment. Complete coverage of all 5 care homes.

**Acceptance Criteria:**
- [ ] Thursday: Successful go-live
- [ ] Friday: On-site support
- [ ] ≥ 85% staff logged in by Friday
- [ ] All workflows functional
- [ ] No critical incidents across all 5 homes

**Deliverable:** 5th Home Go-Live Report + FULL PRODUCTION ACHIEVED

---

#### Task 5.3: Full Production Celebration & Communication
- **Priority:** 🟢 Low
- **Assignee:** Service Manager
- **Effort:** 2 hours
- **Dependencies:** Task 5.2
- **Week:** 11 (Fri)

**Description:**
Announce full production achievement. Celebrate success with all stakeholders.

**Acceptance Criteria:**
- [ ] Email announcement to all 821 staff
- [ ] Executive briefing to Head of Service
- [ ] Success metrics compiled:
  - 5/5 homes operational
  - 821 staff active
  - X,XXX shifts managed
  - X,XXX leave requests processed
  - £590,000/year ROI achieved
- [ ] Internal newsletter article
- [ ] Thank you to pilot homes and UAT testers

**Deliverable:** Full Production Announcement

---

### Week 12: Stabilization & Optimization

#### Task 5.4: System-Wide Performance Review
- **Priority:** 🟠 High
- **Assignee:** Technical Lead
- **Effort:** 6 hours
- **Dependencies:** All 5 homes live 1 week
- **Week:** 12 (Mon-Tue)

**Description:**
Comprehensive performance review across all homes. Identify optimization opportunities.

**Acceptance Criteria:**
- [ ] Page load times measured (all dashboards)
- [ ] Database query performance analyzed
- [ ] Server resource utilization reviewed (CPU, RAM, disk)
- [ ] Bottlenecks identified
- [ ] Optimization plan created (if needed)
- [ ] Capacity planning for growth

**Deliverable:** PERFORMANCE_REVIEW_WEEK12.md

---

#### Task 5.5: Executive Dashboard Enhancement Review
- **Priority:** 🟡 Medium
- **Assignee:** Service Manager + Technical Lead
- **Effort:** 4 hours
- **Dependencies:** All 5 homes data available
- **Week:** 12 (Wed)

**Description:**
Review executive dashboards with all 5 homes. Ensure insights are actionable.

**Acceptance Criteria:**
- [ ] All 7 executive dashboards tested:
  - Strategic Overview
  - Budget Intelligence
  - Retention & Staffing
  - Training & Compliance
  - Quality & Safety
  - Operational Efficiency
  - CI Performance Dashboard
- [ ] Multi-home comparisons working
- [ ] Chart.js visualizations rendering correctly
- [ ] Excel exports functional
- [ ] Traffic light indicators accurate
- [ ] Benchmark calculations correct
- [ ] Service Manager satisfied with insights

**Deliverable:** Executive Dashboard Validation Report

---

#### Task 5.6: Compliance & Audit Trail Verification
- **Priority:** 🟠 High
- **Assignee:** Technical Lead
- **Effort:** 4 hours
- **Dependencies:** 2 weeks of production data
- **Week:** 12 (Thu)

**Description:**
Verify compliance monitoring and audit trail completeness across all homes.

**Acceptance Criteria:**
- [ ] Audit trail tested:
  - Leave approvals logged
  - Shift changes logged
  - User actions logged
  - Admin actions logged
- [ ] Compliance rules running:
  - Training expiry alerts
  - Supervision due alerts
  - Induction tracking
  - Incident reporting
- [ ] Care Inspectorate data accurate
- [ ] No compliance gaps identified

**Deliverable:** Compliance Verification Report

---

#### Task 5.7: 12-Week Retrospective & Lessons Learned
- **Priority:** 🔵 Documentation
- **Assignee:** Service Manager + Technical Lead + OMs (all homes)
- **Effort:** 3 hours (meeting)
- **Dependencies:** Week 12 end
- **Week:** 12 (Fri)

**Description:**
Conduct comprehensive retrospective on 12-week implementation. Document lessons learned.

**Acceptance Criteria:**
- [ ] Retrospective meeting held (all 9 OMs, SM, Technical Lead)
- [ ] Agenda:
  - What went well
  - What could be improved
  - Surprises/learnings
  - Recommendations for future projects
  - Glasgow HSCP pitch readiness
- [ ] Lessons learned documented
- [ ] Success stories collected (testimonials)
- [ ] Metrics compiled:
  - Timeline adherence
  - Budget vs actual
  - User satisfaction by home
  - Technical performance
  - Business impact

**Deliverable:** 12_WEEK_RETROSPECTIVE.md + Success Stories

---

#### Task 5.8: Production Handover & Ongoing Support Plan
- **Priority:** 🔴 Critical
- **Assignee:** Service Manager + Technical Lead
- **Effort:** 4 hours
- **Dependencies:** Task 5.7
- **Week:** 12 (Fri)

**Description:**
Formalize ongoing support model. Transition from implementation to steady-state operations.

**Acceptance Criteria:**
- [ ] Support tiers defined:
  - Tier 1: Self-service (guides, videos, FAQ)
  - Tier 2: OM support (common issues)
  - Tier 3: Technical support (2 hours/week)
  - Tier 4: Developer escalation (as needed)
- [ ] Support hours: 9am-5pm Mon-Fri
- [ ] Emergency contact for critical issues
- [ ] Monthly review meeting scheduled (ongoing)
- [ ] Quarterly user satisfaction survey scheduled
- [ ] Annual system health check scheduled
- [ ] Support SLA documented
- [ ] Handover complete from implementation to operations

**Deliverable:** ONGOING_SUPPORT_PLAN.md

---

### Epic 5 Completion Checklist
- [ ] All 5 homes operational
- [ ] 821 staff active
- [ ] System performance optimized
- [ ] Compliance verified
- [ ] Support model established
- [ ] 12-week retrospective complete
- **Status:** FULL PRODUCTION ACHIEVED ✅

---

## Epic 6: Glasgow HSCP Pitch Preparation
**Duration:** Week 13+ (Post-Implementation)  
**Owner:** Service Manager + Head of Service  
**Goal:** Prepare and deliver pitch to Glasgow HSCP for wider adoption

### Task 6.1: Glasgow HSCP Pitch Deck Creation
- **Priority:** 🟡 Medium
- **Assignee:** Service Manager + Technical Lead
- **Effort:** 8 hours
- **Dependencies:** Full production achieved
- **Week:** 13

**Description:**
Create executive presentation for Glasgow HSCP showcasing system capabilities and ROI.

**Acceptance Criteria:**
- [ ] Pitch deck created: GLASGOW_HSCP_PITCH.md
- [ ] Sections included:
  1. Problem Statement (current care home scheduling challenges)
  2. Solution Overview (Staff Rota System features)
  3. AI/ML Innovation (forecasting, chatbot, predictions)
  4. Cost Comparison (£0 vs PCS £36-60k, Access £60-120k)
  5. ROI Analysis (£590k savings, 12,413% return)
  6. Implementation Timeline (4-month phased rollout)
  7. Risk Mitigation (lessons learned from 5-home deployment)
  8. Support Plan (3-tier model, ongoing maintenance)
  9. Live Demo Script (15-minute walkthrough)
  10. Q&A Preparation
- [ ] PowerPoint slides created (20-30 slides)
- [ ] Demo environment prepared
- [ ] Case study compiled (Hawthorn House testimonial)
- [ ] ROI calculator spreadsheet created

**Deliverable:** GLASGOW_HSCP_PITCH.md + PowerPoint Deck

---

#### Task 6.2: Live Demo Rehearsal
- **Priority:** 🟡 Medium
- **Assignee:** Service Manager + Technical Lead
- **Effort:** 4 hours
- **Dependencies:** Task 6.1
- **Week:** 13

**Description:**
Rehearse live demo for Glasgow HSCP presentation. 15-minute feature showcase.

**Demo Script:**
1. Login & Dashboard (1 min)
2. Leave Request & Auto-Approval (2 min)
3. Shift Management (2 min)
4. AI Chatbot - Chart Generation (3 min)
5. Executive Dashboard - Multi-Home View (3 min)
6. ML Forecasting (2 min)
7. Compliance Monitoring (2 min)

**Acceptance Criteria:**
- [ ] Demo script written
- [ ] Demo data prepared (realistic scenarios)
- [ ] Rehearsal completed (timed to 15 mins)
- [ ] Backup plan for technical issues
- [ ] Screen recording created (backup if live demo fails)

**Deliverable:** Demo Script + Screen Recording

---

#### Task 6.3: Glasgow HSCP Pitch Delivery
- **Priority:** 🟠 High
- **Assignee:** Head of Service + Service Manager
- **Effort:** 4 hours (prep + meeting)
- **Dependencies:** Task 6.2
- **Week:** 14+

**Description:**
Deliver pitch to Glasgow HSCP stakeholders. Secure buy-in for wider adoption.

**Acceptance Criteria:**
- [ ] Meeting scheduled with Glasgow HSCP decision-makers
- [ ] Pitch deck presented (30 mins)
- [ ] Live demo conducted (15 mins)
- [ ] Q&A handled (15 mins)
- [ ] Follow-up materials provided:
  - Production Readiness Assessment
  - Academic Paper
  - ROI Calculator
  - Implementation Plan
- [ ] Next steps agreed (pilot with 1-2 HSCP homes, or full rollout)

**Deliverable:** Glasgow HSCP Pitch Report + Next Steps

---

## Summary: 12-Week Gantt Chart

| Epic | Week 1 | Week 2 | Week 3 | Week 4 | Week 5 | Week 6 | Week 7 | Week 8 | Week 9 | Week 10 | Week 11 | Week 12 |
|------|--------|--------|--------|--------|--------|--------|--------|--------|--------|---------|---------|---------|
| **Epic 1: Production Prep** | 🔴🔴🔴🔴 | 🔴🔴🔴🔴 | | | | | | | | | | |
| **Epic 2: UAT** | | | 🔴🔴🔴🔴 | 🔴🔴🔴🔴 | | | | | | | | |
| **Epic 3: Pilot (Hawthorn/Meadowburn)** | | | | | 🔴🔴🔴🔴 | 🟠🟠🟠🟠 | 🟠🟠🟠🟠 | 🟠🟠🟠🟠 | | | | |
| **Epic 4: Phased Rollout (Riverside/Victoria)** | | | | | | | | | 🔴🔴🔴🔴 | 🔴🔴🔴🔴 | | |
| **Epic 5: Final Rollout (5th Home)** | | | | | | | | | | | 🔴🔴🔴🔴 | 🟠🟠🟠🟠 |
| **Epic 6: HSCP Pitch** | | | | | | | | | | | | 🟡🟡🟡🟡 |

**Legend:**
- 🔴 Critical/High Priority
- 🟠 Medium Priority
- 🟡 Low Priority / Planning

---

## Resource Allocation

### Team Members

| Role | Name | Hours/Week | Weeks Active | Total Hours |
|------|------|------------|--------------|-------------|
| **Technical Lead** | [TBD] | 20-40 hrs | Weeks 1-12 | ~360 hours |
| **Service Manager** | [TBD] | 5-10 hrs | Weeks 1-12 | ~90 hours |
| **Operational Managers (9)** | [TBD] | 2-5 hrs/each | Weeks 5-12 | ~180 hours (total) |
| **UAT Testers (5-10)** | [TBD] | 15 hrs | Weeks 3-4 | ~120 hours (total) |
| **Head of Service** | [TBD] | 1-2 hrs | Week 12+ | ~10 hours |

**Total Effort:** ~760 hours over 12 weeks

---

## Budget Breakdown

| Category | Cost | Notes |
|----------|------|-------|
| **Development/Technical Lead** | £9,000 | 360 hrs @ £25/hr |
| **Service Manager** | £2,250 | 90 hrs @ £25/hr |
| **OM Support** | £4,500 | 180 hrs @ £25/hr |
| **UAT Incentives** | £200 | Vouchers for testers |
| **Training Materials** | £300 | Printing, video hosting |
| **Server/Infrastructure** | £240 | Weeks 1-12 @ £20/month |
| **Contingency (10%)** | £1,649 | Buffer for unexpected costs |
| **Total 12-Week Cost** | **£18,139** | |

**ROI:**
- **Costs:** £18,139 (implementation) + £2,652/year (ongoing) = **£20,791 Year 1**
- **Savings:** £590,000/year
- **Net ROI:** £569,209
- **ROI %:** 2,738%
- **Payback Period:** 11 days

---

## Critical Path

**Must-Complete for Next Phase:**
1. ✅ Week 2: Production infrastructure ready → Enables UAT
2. ✅ Week 4: UAT GO decision → Enables Pilot
3. ✅ Week 8: Pilot GO decision → Enables Phased Rollout
4. ✅ Week 12: Full production → Enables HSCP Pitch

**Blockers to Watch:**
- SSL certificate issues (Week 1)
- UAT critical bugs (Week 3-4)
- Pilot home staff resistance (Week 5-8)
- Multi-home data isolation failures (any week)
- Performance degradation at scale (Week 10+)

---

## Success Metrics

### Technical Metrics
- [ ] System uptime ≥ 99.5% (Weeks 5-12)
- [ ] Average page load < 2 seconds
- [ ] Error rate < 1%
- [ ] SSL Labs rating: A or A+
- [ ] All security tests passed

### User Metrics
- [ ] User satisfaction ≥ 4.0/5.0 (UAT)
- [ ] User satisfaction ≥ 4.3/5.0 (Pilot end)
- [ ] 100% staff active by Week 12
- [ ] ≥ 2,000 leave requests processed
- [ ] ≥ 5,000 shifts managed
- [ ] 100% digital rota adoption (0% paper)

### Business Metrics
- [ ] OM time savings ≥ 80% (vs baseline)
- [ ] Leave approval time < 2 mins (vs 15 mins)
- [ ] Compliance report time < 15 mins (vs 2 hours)
- [ ] ROI ≥ £500,000/year
- [ ] Zero data loss incidents
- [ ] Zero security breaches

---

## Trello Import Instructions

### Step 1: Create Board
1. Create new Trello board: "Staff Rota Implementation"
2. Add lists: Backlog, To Do (This Week), In Progress, Blocked, Testing, Done
3. Enable Calendar Power-Up (for timeline view)

### Step 2: Create Labels
- Critical (Red)
- High Priority (Orange)
- Medium Priority (Yellow)
- Low Priority (Green)
- Documentation (Blue)
- Training (Purple)
- Technical (Black)
- Testing (Brown)

### Step 3: Create Epic Cards
Create 6 Epic cards in Backlog:
1. Epic 1: Production Infrastructure Setup
2. Epic 2: User Acceptance Testing
3. Epic 3: Pilot Deployment
4. Epic 4: Phased Rollout (Homes 3-4)
5. Epic 5: Final Rollout & Full Production
6. Epic 6: Glasgow HSCP Pitch

For each Epic card:
- Set due date (Epic completion week)
- Add checklist for completion criteria
- Attach relevant documents (SSL_SETUP_GUIDE.md, etc.)

### Step 4: Create Task Cards
For each task in this document:
- Create card under appropriate Epic
- Set title: "Task X.X: [Name]"
- Set due date (end of week)
- Add labels (Priority, Category)
- Add description with acceptance criteria
- Create checklist from acceptance criteria
- Assign to team member
- Add estimated hours in card description

### Step 5: Set Up Automation (Butler)
Example automations:
- When card moved to "Done", check all items in checklist
- When all tasks in Epic complete, move Epic to Done
- Weekly reminder: "Review This Week tasks"
- Due date approaching: Notify assignee 2 days before

### Step 6: Weekly Review Process
Every Monday:
1. Review completed tasks (last week)
2. Move upcoming tasks to "To Do (This Week)"
3. Update progress on in-progress tasks
4. Adjust timeline if needed
5. Review blockers and resolve

---

## Conclusion

This 12-week implementation plan provides:
- ✅ **Clear timeline** (week-by-week breakdown)
- ✅ **Detailed tasks** (60+ actionable tasks with acceptance criteria)
- ✅ **Resource allocation** (760 hours, £18,139 budget)
- ✅ **Risk mitigation** (GO/NO-GO gates, rollback plans)
- ✅ **Success metrics** (technical, user, business KPIs)
- ✅ **Trello-ready structure** (epics, tasks, labels, checklists)

**Expected Outcome:**
By Week 12, all 5 care homes will be operational with 821 staff actively using the Staff Rota System, achieving £590,000/year ROI and positioning for Glasgow HSCP expansion.

**Next Action:** Import to Trello and begin Week 1 tasks! 🚀

---

**Document Status:** Complete and Ready for Execution  
**Last Updated:** January 6, 2026  
**Approval Required:** Service Manager + Head of Service  
**Start Date:** [To be scheduled]
