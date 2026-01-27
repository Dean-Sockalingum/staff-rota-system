# Pilot Deployment Plan - Staff Rota System
**Document:** Month 1 Pilot Strategy  
**Date:** January 6, 2026  
**Status:** Ready for Execution  
**Duration:** 4 weeks (Month 1)

---

## Executive Summary

### Pilot Objectives
1. Validate system readiness in real-world production environment
2. Train staff and gather operational feedback
3. Identify and resolve deployment issues before full rollout
4. Build confidence and momentum for wider adoption

### Pilot Scope
- **Care Homes:** 2 of 5 homes (Hawthorn House + 1 other)
- **Staff:** ~165 staff members (~20% of total 821)
- **Duration:** 4 weeks (Month 1)
- **Features:** All core features + AI/ML + Executive dashboards

### Success Criteria
- ✅ Zero critical incidents
- ✅ System uptime ≥ 99.5% (< 3.6 hours downtime)
- ✅ User satisfaction ≥ 4.0/5.0
- ✅ All workflows completed successfully
- ✅ Ready for phased rollout to remaining homes

---

## 1. Pilot Home Selection

### 1.1 Recommended Homes

#### Primary Pilot: Hawthorn House
**Rationale:**
- ✅ Largest home (likely highest staff count)
- ✅ Operational Manager engaged and tech-savvy
- ✅ Good mix of staff roles and shift patterns
- ✅ Central location for easy support visits
- ✅ Strong track record of process adoption

**Staff Profile:**
- Operational Managers: 2
- Senior Carers: ~12
- Care Assistants: ~45
- Support Staff: ~8
- **Total:** ~67 staff

#### Secondary Pilot: Meadowburn OR Orchard Grove
**Option A: Meadowburn**
- Medium-sized home
- Different shift patterns than Hawthorn
- Provides geographic diversity
- ~50 staff

**Option B: Orchard Grove**
- Similar size to Meadowburn
- Different care model (specialist vs general)
- Tests system flexibility
- ~48 staff

**Recommendation:** **Meadowburn** (diverse shift patterns, strong OM leadership)

### 1.2 Homes NOT in Pilot (Month 1)
- **Riverside:** Deploy Month 2 (Week 5-6)
- **Victoria Gardens:** Deploy Month 2 (Week 7-8)
- **Remaining Home:** Deploy Month 3 (Week 9-10)

**Rationale for Phasing:**
- Manageable support load (2 homes vs 5)
- Allows learning and iteration
- Reduces risk of widespread issues
- Builds success stories for remaining homes

---

## 2. Pre-Pilot Preparation (Week 0: Days -7 to -1)

### 2.1 Technical Readiness Checklist

#### Server & Infrastructure
- [ ] SSL certificate installed and tested (HTTPS working)
- [ ] Production domain configured (e.g., https://rota.yourdomain.com)
- [ ] Gunicorn service running and auto-starts on reboot
- [ ] Nginx reverse proxy configured
- [ ] Firewall rules configured (ports 80, 443 open)
- [ ] Server monitoring enabled (uptime, CPU, memory, disk)
- [ ] Daily automated backups configured (database + media files)
- [ ] Backup restoration tested successfully

#### Application
- [ ] Latest code deployed (commit: 72f956a or later)
- [ ] Database migrations applied
- [ ] Static files collected (`collectstatic`)
- [ ] Production settings active (`DEBUG=False`, `ALLOWED_HOSTS` set)
- [ ] Email notifications configured (SMTP with Gmail/SendGrid)
- [ ] Secrets management implemented (encrypted .env or Vault)
- [ ] Error logging configured (Sentry or file-based)
- [ ] Audit trail enabled

#### Data
- [ ] Care home data verified (Hawthorn, Meadowburn complete)
- [ ] Staff profiles imported (all 117 staff)
- [ ] Historical shifts loaded (previous 3 months for ML training)
- [ ] Leave balances accurate (verified with payroll)
- [ ] Training records imported (18 course types, compliance dates)
- [ ] Care Inspectorate data updated (CS numbers, ratings, dates)

#### Security
- [ ] 2FA enabled for all Operational Managers and Service Managers
- [ ] API authentication tested
- [ ] Role-based access control verified (RBAC)
- [ ] Data isolation tested (no cross-home data leaks)
- [ ] Password policies enforced (8+ chars, complexity)
- [ ] Session timeout configured (30 minutes idle)

### 2.2 Training Materials Preparation

#### Documentation
- [ ] User guides updated (50+ existing guides reviewed)
- [ ] Quick start guide created (1-page cheat sheet)
- [ ] Video walkthrough recorded (15-minute overview)
- [ ] FAQ document prepared (20+ common questions)
- [ ] Troubleshooting guide created (10 common issues + solutions)

#### Training Sessions Scheduled
| Date | Audience | Duration | Location | Trainer |
|------|----------|----------|----------|---------|
| **Week 0, Mon** | Hawthorn OMs (2) | 2 hours | Hawthorn House | Technical Lead |
| **Week 0, Tue** | Meadowburn OMs (2) | 2 hours | Meadowburn | Technical Lead |
| **Week 0, Wed** | Hawthorn Senior Carers (12) | 1.5 hours | Hawthorn House | Hawthorn OM |
| **Week 0, Thu** | Meadowburn Senior Carers (10) | 1.5 hours | Meadowburn | Meadowburn OM |
| **Week 0, Fri** | Care Assistants (both homes) | 1 hour × 3 sessions | On-site | OMs + Tech Lead |

**Total Training:** 15 hours over 5 days

#### Training Content
1. **System Overview** (15 mins)
   - Purpose and benefits
   - Key features tour
   - Demo mode walkthrough

2. **Authentication** (10 mins)
   - Login process
   - 2FA setup (if applicable)
   - Password reset

3. **Core Features by Role** (30-60 mins)
   - **Care Assistants:**
     - View my shifts
     - Request leave
     - Check leave balance
     - Update training records
   
   - **Senior Carers:**
     - All CA features +
     - View team shifts
     - Report sickness/absence
     - Access AI chatbot
   
   - **Operational Managers:**
     - All above +
     - Create/edit shifts
     - Approve leave requests
     - Run compliance reports
     - Executive dashboards
     - ML forecasting

4. **AI Chatbot** (15 mins)
   - How to access
   - Example queries (20+ patterns)
   - Chart generation
   - Interpreting responses

5. **Support & Help** (10 mins)
   - Help documentation location
   - Support contact (phone, email, Teams)
   - Escalation process
   - Known issues and workarounds

6. **Q&A** (15-30 mins)
   - Open questions
   - Hands-on practice
   - Confidence building

### 2.3 Communication Plan

#### Announcement Email (Week -2)
**To:** All staff at Hawthorn House and Meadowburn  
**From:** Service Manager  
**Subject:** New Staff Rota System Launching [Date]

**Content:**
- Introduction to new system
- Benefits (time savings, easier leave requests, better visibility)
- Training schedule
- Go-live date
- Support contact information
- Encouragement and excitement

#### Reminder Email (Week -1)
**To:** All pilot home staff  
**Subject:** Training This Week - Staff Rota System

**Content:**
- Training session details (date, time, location)
- What to bring (laptop/tablet if available)
- Login credentials (distributed securely)
- Questions welcome

#### Go-Live Email (Day 1 of Week 1)
**To:** All pilot home staff  
**Subject:** Staff Rota System is LIVE!

**Content:**
- System is now live
- Login URL: https://rota.yourdomain.com
- Quick start guide attached
- Support hotline open
- Celebrate the launch!

---

## 3. Pilot Execution (Weeks 1-4)

### Week 1: Launch & Stabilization

#### Day 1 (Monday) - Go-Live
**Morning:**
- [ ] 08:00 - Final system health check (uptime, backups, logs)
- [ ] 08:30 - Send go-live email to all pilot staff
- [ ] 09:00 - On-site support at Hawthorn House (Technical Lead + OM)
- [ ] 09:30 - Monitor first logins (authentication, 2FA setup)
- [ ] 10:00 - Check for errors (Sentry dashboard, Nginx logs)

**Afternoon:**
- [ ] 13:00 - On-site support at Meadowburn
- [ ] 14:00 - First leave requests submitted (test auto-approval)
- [ ] 15:00 - Managers create shifts for next week
- [ ] 16:00 - End-of-day system check

**Evening:**
- [ ] 18:00 - Review activity logs (user count, features used)
- [ ] 19:00 - Backup verification
- [ ] 20:00 - Day 1 debrief (what went well, what needs fixing)

#### Day 2-5 (Tue-Fri) - Daily Operations
**Daily Routine:**
- **09:00** - Morning system check (uptime, errors, performance)
- **10:00** - Review overnight activity (shifts created, leave requests)
- **12:00** - Check support tickets (respond within 2 hours)
- **15:00** - On-site check-in (rotate between Hawthorn/Meadowburn)
- **17:00** - End-of-day review (user feedback, issues log)
- **18:00** - Daily backup verification

**Key Milestones:**
- [ ] Day 2: First shifts worked from system-generated rota
- [ ] Day 3: First leave auto-approvals (≤5 days rule)
- [ ] Day 4: First manager leave approvals (>5 days rule)
- [ ] Day 5: First AI chatbot queries (staffing, charts, reports)

**End of Week 1 Review:**
- [ ] User count: Target ≥ 80% of pilot staff logged in
- [ ] Leave requests: Target ≥ 20 submitted, 90% processed
- [ ] Shifts: Target ≥ 100 created/edited
- [ ] Issues: Target < 5 medium priority, 0 critical
- [ ] Satisfaction: Target ≥ 3.5/5.0 (early adoption phase)

---

### Week 2: Feature Adoption & Optimization

**Focus Areas:**
1. **Leave Management:** Encourage all staff to use system for leave requests
2. **Shift Visibility:** Train staff to check shifts daily (reduce paper rotas)
3. **AI Chatbot:** Promote usage among managers (queries, charts, reports)
4. **Compliance:** Test training compliance reports, supervision tracking

**Daily Activities:**
- On-site support reduced to 2 days/week (Wed, Fri)
- Remote support via phone/email/Teams
- Weekly team meeting (OMs + Technical Lead)

**Key Milestones:**
- [ ] Day 8: First executive dashboard usage (Service Manager)
- [ ] Day 9: First ML forecast generated (30-day staffing prediction)
- [ ] Day 10: First agency usage report run
- [ ] Day 12: First compliance report exported to Excel
- [ ] Day 14: Week 2 user survey (mid-pilot feedback)

**End of Week 2 Review:**
- [ ] User count: Target ≥ 95% of pilot staff active
- [ ] Leave requests: Target ≥ 50 total, 95% processed
- [ ] Shifts: Target ≥ 300 managed through system
- [ ] AI queries: Target ≥ 50 chatbot interactions
- [ ] Issues: Target < 3 medium priority, 0 critical/high
- [ ] Satisfaction: Target ≥ 4.0/5.0

---

### Week 3: Workflow Integration

**Focus Areas:**
1. **Abandon Paper Rotas:** Full transition to digital shifts
2. **Email Notifications:** Verify all notifications working (leave approvals, shift changes)
3. **Executive Dashboards:** Service Manager using all 7 dashboards weekly
4. **Compliance Monitoring:** Automated compliance checks running daily

**Daily Activities:**
- On-site support 1 day/week (Thu)
- Phone/email support during business hours (9am-5pm)
- Monitor system proactively (alerts, performance, errors)

**Key Milestones:**
- [ ] Day 15: Last paper rota discontinued at Hawthorn
- [ ] Day 16: Last paper rota discontinued at Meadowburn
- [ ] Day 19: First automated compliance alert sent (training expiry)
- [ ] Day 21: Week 3 user survey + manager interviews

**End of Week 3 Review:**
- [ ] User count: Target 100% of pilot staff active
- [ ] Leave requests: Target ≥ 80 total, 98% processed
- [ ] Shifts: Target ≥ 500 managed, 100% digital
- [ ] Compliance: Target ≥ 5 automated reports run
- [ ] Issues: Target < 2 medium priority, 0 critical/high
- [ ] Satisfaction: Target ≥ 4.2/5.0

---

### Week 4: Stabilization & Planning

**Focus Areas:**
1. **System Stability:** Ensure uptime, performance, reliability
2. **User Confidence:** Staff using system independently
3. **Phased Rollout Planning:** Prepare for Riverside deployment (Month 2)
4. **Final Feedback:** Comprehensive user survey

**Daily Activities:**
- On-site support on-demand only
- Remote support available (9am-5pm)
- Focus on documentation and lessons learned

**Key Milestones:**
- [ ] Day 22: System performance review (page loads, database queries)
- [ ] Day 24: Security audit (data isolation, authentication logs)
- [ ] Day 26: Final user survey distributed (all pilot staff)
- [ ] Day 28: Pilot review meeting (OMs, Service Manager, Technical Lead)

**End of Week 4 Review:**
- [ ] Uptime: Target ≥ 99.5% (< 3.6 hours downtime total)
- [ ] User satisfaction: Target ≥ 4.3/5.0
- [ ] Leave requests: Target ≥ 100 total, 99% processed
- [ ] Shifts: Target ≥ 700 managed
- [ ] Issues: All critical/high resolved, medium in progress
- [ ] **GO/NO-GO Decision:** Proceed to phased rollout

---

## 4. Support Model

### 4.1 Support Tiers

#### Tier 1: Self-Service
- User guides (50+ documents)
- FAQ (20+ questions)
- Video tutorials (5-10 videos)
- Demo mode (practice environment)
- **Response Time:** Immediate

#### Tier 2: Operational Manager Support
- OM trained on common issues
- OM resolves basic user questions
- OM escalates to Tier 3 if needed
- **Response Time:** Same day

#### Tier 3: Technical Support (Technical Lead)
- Phone: [Support number]
- Email: support@yourdomain.com
- Teams: [Teams channel]
- **Response Time:** 
  - Critical: < 1 hour
  - High: < 4 hours
  - Medium: < 1 business day
  - Low: < 3 business days

#### Tier 4: Developer Escalation
- Code fixes required
- Database issues
- Infrastructure problems
- **Response Time:** < 4 hours for critical issues

### 4.2 Support Hours
- **Week 1-2:** Extended support (8am-8pm, Mon-Fri)
- **Week 3-4:** Standard support (9am-5pm, Mon-Fri)
- **Emergency:** On-call phone number for critical issues (24/7)

### 4.3 Issue Tracking
- **Tool:** GitHub Issues or Jira
- **Categories:** Bug, Feature Request, Question, Training
- **Priority:** Critical, High, Medium, Low
- **Update Frequency:** Daily status updates on all open issues

---

## 5. Metrics & Monitoring

### 5.1 System Metrics (Daily)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| **Uptime** | ≥ 99.5% | _____ | 🟢/🟡/🔴 |
| **Active Users (Daily)** | ≥ 80% of pilot staff | _____ | 🟢/🟡/🔴 |
| **Average Page Load** | < 2 seconds | _____ | 🟢/🟡/🔴 |
| **Error Rate** | < 1% | _____ | 🟢/🟡/🔴 |
| **Leave Requests (Total)** | ≥ 100 by Week 4 | _____ | 🟢/🟡/🔴 |
| **Auto-Approvals** | ≥ 60% of leave requests | _____ | 🟢/🟡/🔴 |
| **Shifts Managed** | ≥ 700 by Week 4 | _____ | 🟢/🟡/🔴 |
| **AI Chatbot Queries** | ≥ 100 by Week 4 | _____ | 🟢/🟡/🔴 |

### 5.2 User Metrics (Weekly)

| Metric | Week 1 | Week 2 | Week 3 | Week 4 | Target |
|--------|--------|--------|--------|--------|--------|
| **Logins (Unique Users)** | _____ | _____ | _____ | _____ | 100% by Week 4 |
| **Leave Requests** | _____ | _____ | _____ | _____ | ≥ 100 total |
| **Shifts Created** | _____ | _____ | _____ | _____ | ≥ 700 total |
| **Reports Generated** | _____ | _____ | _____ | _____ | ≥ 50 total |
| **Support Tickets** | _____ | _____ | _____ | _____ | Decreasing trend |
| **User Satisfaction** | _____ | _____ | _____ | _____ | ≥ 4.0/5.0 |

### 5.3 Business Metrics (Week 4)

| Metric | Baseline (Pre-Pilot) | Week 4 Actual | Improvement | Target |
|--------|----------------------|---------------|-------------|--------|
| **OM Time on Rota (hrs/week)** | 25 hours | _____ | _____ | < 5 hours (80% reduction) |
| **Leave Approval Time (mins/request)** | 15 mins | _____ | _____ | < 2 mins (87% reduction) |
| **Paper Rota Usage** | 100% | _____ | _____ | 0% (100% digital) |
| **Compliance Report Time (hrs)** | 2 hours | _____ | _____ | < 15 mins (87% reduction) |
| **Staff Satisfaction (Rota Process)** | 2.5/5.0 | _____ | _____ | ≥ 4.0/5.0 |

---

## 6. Risk Management

### 6.1 Identified Risks

| Risk | Probability | Impact | Mitigation | Contingency |
|------|-------------|--------|------------|-------------|
| **System Downtime (>1 hour)** | Low | Critical | Daily backups, monitoring alerts | Revert to paper rotas, restore from backup |
| **Data Loss** | Very Low | Critical | Automated hourly backups, NVMe + cloud | Restore from most recent backup (< 1 hour data loss) |
| **User Resistance** | Medium | High | Extensive training, OM champions | One-on-one sessions, extended support |
| **Performance Issues** | Low | Medium | Load testing pre-pilot, server monitoring | Scale server resources (CPU, RAM) |
| **Security Breach** | Very Low | Critical | 2FA, audit logs, penetration testing | Immediate lockdown, password resets, forensic analysis |
| **Critical Bug Discovered** | Medium | High | UAT before pilot, daily monitoring | Hotfix deployment, rollback if needed |
| **Staff Overwhelm** | Medium | Medium | Gradual rollout, training materials | Reduce feature set, extend pilot duration |

### 6.2 Rollback Plan

**Trigger:** Critical system failure, data corruption, or unanimous pilot failure

**Steps:**
1. **Immediate:**
   - Disable system access (redirect to maintenance page)
   - Notify all pilot staff (email, phone)
   - Revert to paper rotas temporarily
   
2. **Within 4 Hours:**
   - Diagnose root cause (logs, database, code)
   - Restore from backup if data corrupted
   - Fix critical issue or prepare rollback
   
3. **Within 24 Hours:**
   - Decision: Fix forward or full rollback
   - Communicate decision to stakeholders
   - If rollback: Extract data for manual processing
   
4. **Within 1 Week:**
   - Post-mortem analysis
   - Implement fixes
   - Reschedule pilot (if full rollback)

**Data Preservation:**
- All leave requests: Export to Excel before rollback
- All shifts: Export to CSV
- All user accounts: Preserve for re-deployment

---

## 7. Success Evaluation

### 7.1 Pilot Success Criteria (GO/NO-GO)

#### Mandatory (Must Pass All)
- [ ] ✅ System uptime ≥ 99.5% (< 3.6 hours downtime)
- [ ] ✅ Zero critical incidents (data loss, security breach)
- [ ] ✅ ≥ 95% of pilot staff successfully using system
- [ ] ✅ All core workflows functional (leave, shifts, compliance)
- [ ] ✅ User satisfaction ≥ 4.0/5.0
- [ ] ✅ Data isolation verified (no cross-home leaks)

#### Desirable (80% Required)
- [ ] 🎯 User satisfaction ≥ 4.3/5.0
- [ ] 🎯 OM time savings ≥ 70% (vs baseline)
- [ ] 🎯 100% digital rota adoption (0% paper)
- [ ] 🎯 AI chatbot usage ≥ 100 queries
- [ ] 🎯 Executive dashboards used weekly by Service Manager
- [ ] 🎯 All medium priority issues resolved

### 7.2 Decision Matrix

| Criteria Met | Decision | Action |
|--------------|----------|--------|
| **All Mandatory + ≥80% Desirable** | **GO** | Proceed to phased rollout (Riverside, Month 2) |
| **All Mandatory + <80% Desirable** | **GO with Caution** | Address desirable gaps, proceed with monitoring |
| **6/7 Mandatory** | **Conditional GO** | Fix remaining mandatory item, retest, then proceed |
| **<6/7 Mandatory** | **NO-GO** | Extend pilot duration, fix issues, re-evaluate |
| **Critical Incident Occurred** | **NO-GO** | Full investigation, fixes, restart pilot |

### 7.3 Lessons Learned Session (Week 4, Day 28)

**Attendees:**
- Hawthorn OMs (2)
- Meadowburn OMs (2)
- Service Manager
- Technical Lead
- Sample Senior Carers (2-3)
- Sample Care Assistants (2-3)

**Agenda:**
1. **What Went Well** (30 mins)
   - Features users loved
   - Training effectiveness
   - Support responsiveness
   
2. **What Needs Improvement** (30 mins)
   - Pain points
   - Feature gaps
   - Usability issues
   
3. **Recommendations for Next Homes** (30 mins)
   - Training adjustments
   - Communication improvements
   - Support model refinements
   
4. **Phased Rollout Planning** (30 mins)
   - Timeline for Riverside (Weeks 5-6)
   - Timeline for Victoria Gardens (Weeks 7-8)
   - Timeline for final home (Weeks 9-10)

**Deliverable:** Lessons Learned Report (circulated to all stakeholders)

---

## 8. Phased Rollout Preview (Months 2-3)

### Month 2: Homes 3 & 4

#### Weeks 5-6: Riverside
- **Advantage:** Learn from pilot mistakes
- **Training:** 1 week (based on pilot feedback)
- **Go-Live:** Week 5, Monday
- **Support:** Standard model (9am-5pm)
- **Review:** Week 6, Friday

#### Weeks 7-8: Victoria Gardens
- **Advantage:** 3 homes operational, proven track record
- **Training:** 1 week
- **Go-Live:** Week 7, Monday
- **Support:** Standard model
- **Review:** Week 8, Friday

### Month 3: Home 5

#### Weeks 9-10: [Final Home]
- **Advantage:** 4 homes successful, high confidence
- **Training:** 1 week
- **Go-Live:** Week 9, Monday
- **Support:** Standard model
- **Review:** Week 10, Friday

### Month 4: Full Production

#### Week 11-12: Stabilization
- All 5 homes operational
- System-wide performance monitoring
- Cross-home compliance reporting
- Executive dashboard optimization

#### Week 13-16: Optimization
- Feature enhancements based on feedback
- Performance tuning
- Advanced ML features (if applicable)
- Glasgow HSCP pitch preparation

---

## 9. Communication Cadence

### Week 1-2 (High Touch)
- **Daily:** Email update to Service Manager (end of day)
- **Daily:** Issue log shared with OMs
- **Weekly:** Video call with all OMs (Friday, 30 mins)

### Week 3-4 (Standard)
- **Weekly:** Email update to Service Manager (Friday)
- **Weekly:** Issue log shared with OMs
- **Bi-Weekly:** Video call with OMs (Friday, 30 mins)

### Post-Pilot
- **Monthly:** System performance report
- **Quarterly:** User satisfaction survey
- **Ad-Hoc:** Critical issue alerts (immediate)

---

## 10. Budget & Resources

### 10.1 Pilot Costs

| Item | Cost | Notes |
|------|------|-------|
| **Training (5 sessions, 15 hours)** | £375 | Technical Lead @ £25/hour |
| **On-Site Support (Week 1-2, 30 hours)** | £750 | Technical Lead @ £25/hour |
| **Remote Support (Week 3-4, 20 hours)** | £500 | Technical Lead @ £25/hour |
| **User Survey Incentives** | £200 | £20 Amazon vouchers × 10 participants |
| **Training Materials Printing** | £50 | Quick start guides × 120 copies |
| **Contingency (10%)** | £188 | For unexpected costs |
| **Total Pilot Cost** | **£2,063** | One-time investment |

### 10.2 Ongoing Costs (Post-Pilot)

| Item | Monthly Cost | Annual Cost |
|------|--------------|-------------|
| **Server Hosting (VPS)** | £20 | £240 |
| **Domain Name** | £1 | £12 |
| **SSL Certificate (Let's Encrypt)** | £0 | £0 |
| **Email Service (SendGrid Free)** | £0 | £0 |
| **Monitoring (Sentry Free Tier)** | £0 | £0 |
| **Support & Maintenance (2 hrs/week)** | £200 | £2,400 |
| **Total Ongoing** | **£221/month** | **£2,652/year** |

**ROI Calculation (Year 1):**
- **Costs:** £2,063 (pilot) + £2,652 (annual) = **£4,715**
- **Savings:** £590,000 (from production assessment)
- **Net ROI:** £585,285
- **ROI %:** 12,413%

---

## 11. Deliverables

### End of Week 4 (Pilot Completion)

1. **Pilot Summary Report** (10 pages)
   - Executive summary
   - Metrics achieved vs targets
   - User satisfaction results
   - Issues encountered and resolved
   - Lessons learned
   - GO/NO-GO recommendation

2. **User Feedback Report** (5 pages)
   - Survey results (quantitative)
   - User testimonials (qualitative)
   - Feature requests
   - Usability improvements

3. **Technical Performance Report** (5 pages)
   - Uptime statistics
   - Page load times
   - Error logs
   - Database performance
   - Server resource utilization

4. **Lessons Learned Document** (3 pages)
   - What worked well
   - What needs improvement
   - Recommendations for next homes

5. **Phased Rollout Plan (Updated)** (10 pages)
   - Riverside deployment plan
   - Victoria Gardens deployment plan
   - Final home deployment plan
   - Glasgow HSCP pitch timeline

---

## 12. Approval & Sign-Off

**Prepared By:**  
Name: _____________________  
Title: Technical Lead  
Date: January 6, 2026

**Reviewed By:**  
Name: _____________________  
Title: Service Manager  
Date: _____________________

**Approved By:**  
Name: _____________________  
Title: Head of Service  
Date: _____________________

---

**Pilot Start Date:** [To be scheduled after UAT completion]  
**Pilot End Date:** [Start date + 4 weeks]  
**GO/NO-GO Decision Date:** [End of Week 4]  
**Next Phase (Riverside):** [Week 5, pending GO decision]

---

## Appendix A: Quick Wins for Pilot Success

1. **Week 1 Momentum:**
   - Celebrate first 10 logins
   - Share success stories daily
   - Quick win: Leave request auto-approved in seconds

2. **Week 2 Adoption:**
   - Highlight time savings (OM reporting 70% reduction)
   - Showcase AI chatbot power (charts, insights)
   - Quick win: Digital rota replaced paper

3. **Week 3 Confidence:**
   - User testimonials from OMs
   - Executive dashboard demo to Service Manager
   - Quick win: Compliance report in 15 mins vs 2 hours

4. **Week 4 Momentum:**
   - Final survey shows 4.3/5.0 satisfaction
   - Zero critical incidents
   - Quick win: Ready for wider rollout

## Appendix B: Emergency Contacts

| Role | Name | Phone | Email | Availability |
|------|------|-------|-------|--------------|
| **Technical Lead** | [Name] | [Phone] | [Email] | 24/7 (Week 1-2), 9am-5pm (Week 3-4) |
| **Service Manager** | [Name] | [Phone] | [Email] | 9am-5pm Mon-Fri |
| **Hawthorn OM 1** | [Name] | [Phone] | [Email] | 9am-5pm Mon-Fri |
| **Hawthorn OM 2** | [Name] | [Phone] | [Email] | 9am-5pm Mon-Fri |
| **Meadowburn OM 1** | [Name] | [Phone] | [Email] | 9am-5pm Mon-Fri |
| **Meadowburn OM 2** | [Name] | [Phone] | [Email] | 9am-5pm Mon-Fri |
| **Server Admin** | [Name] | [Phone] | [Email] | On-call for critical issues |

**Escalation Path:**
1. User → Operational Manager (Tier 2)
2. OM → Technical Lead (Tier 3)
3. Technical Lead → Developer/Server Admin (Tier 4)

**Critical Issue Hotline:** [Phone number] (24/7 Week 1-2)

---

**Document Status:** Ready for Approval and Execution  
**Next Action:** Schedule UAT completion, set pilot start date  
**Dependencies:** UAT successful GO decision, SSL configuration complete
