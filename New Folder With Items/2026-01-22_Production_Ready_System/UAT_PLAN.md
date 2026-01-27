# User Acceptance Testing (UAT) Plan
**Document:** Staff Rota System UAT  
**Date:** January 6, 2026  
**Status:** Ready for Execution  
**Duration:** 1-2 weeks

---

## 1. Overview

### 1.1 Purpose
Validate the Staff Rota System meets user requirements and is ready for production deployment across all 5 care homes.

### 1.2 Scope
- All core features (shifts, leave, sickness, training, compliance)
- AI/ML features (forecasting, chatbot, chart generation)
- Dashboards (Staff, Manager, Head of Service, Executive)
- Security (2FA, API authentication, role-based access)
- Multi-home data isolation
- Performance under realistic load

### 1.3 Success Criteria
- ✅ 95%+ of test scenarios pass
- ✅ No critical or high-priority bugs
- ✅ User satisfaction score ≥ 4/5
- ✅ All security tests pass
- ✅ Performance meets targets (< 2 second page loads)

---

## 2. Test Team

### 2.1 UAT Participants (Target: 5-10 staff)

| Role | Number | Responsibilities | Care Home |
|------|--------|------------------|-----------|
| **Operational Manager** | 2-3 | Test rota management, staff allocation, reporting | Hawthorn House, Meadowburn |
| **Service Manager** | 1 | Test executive dashboards, compliance monitoring, multi-home views | All homes |
| **Senior Carer** | 1-2 | Test shift management, leave requests, training records | Orchard Grove, Riverside |
| **Care Assistant** | 1-2 | Test basic functionality, leave requests, shift viewing | Victoria Gardens, Hawthorn |
| **Admin Staff** | 1 | Test user management, document uploads, system setup | Central Office |

**Total:** 6-9 testers across all user roles

### 2.2 UAT Coordinator
- **Name:** [To be assigned]
- **Responsibilities:**
  - Schedule testing sessions
  - Distribute test scripts
  - Collect feedback
  - Log defects
  - Compile UAT report

### 2.3 Technical Support
- **Developer:** Available for bug fixes and clarifications
- **Availability:** Daily during UAT period (9am-5pm)
- **Contact:** [Email/Phone]

---

## 3. Test Environment

### 3.1 Server Configuration
- **URL:** https://staging.yourdomain.com (or test server)
- **Database:** Copy of production data (anonymized if needed)
- **Version:** Latest main branch (commit: 72f956a)
- **SSL:** Enabled (HTTPS)

### 3.2 Test Data
- **Care Homes:** All 5 homes (Hawthorn, Meadowburn, Orchard, Riverside, Victoria)
- **Staff:** 821 active staff members
- **Shifts:** Historical data + future shifts (next 30 days)
- **Leave Requests:** Mix of pending, approved, rejected
- **Training Records:** Mix of current and expired
- **Compliance Data:** Care Inspectorate ratings, incidents, supervisions

### 3.3 Test Accounts

| Username | Password | Role | Care Home | 2FA |
|----------|----------|------|-----------|-----|
| `uat_om1` | [Provided] | Operational Manager | Hawthorn House | Optional |
| `uat_om2` | [Provided] | Operational Manager | Meadowburn | Optional |
| `uat_sm` | [Provided] | Service Manager | All homes | Enabled |
| `uat_senior1` | [Provided] | Senior Carer | Orchard Grove | Optional |
| `uat_senior2` | [Provided] | Senior Carer | Riverside | Optional |
| `uat_ca1` | [Provided] | Care Assistant | Victoria Gardens | Optional |
| `uat_ca2` | [Provided] | Care Assistant | Hawthorn House | Optional |
| `uat_admin` | [Provided] | Admin | Central Office | Enabled |

**Note:** All test accounts have 2FA optional except Service Manager and Admin (mandatory for testing 2FA flow)

---

## 4. Test Scenarios

### 4.1 Authentication & Security (Priority: CRITICAL)

#### Test Case 1.1: Standard Login
- **Tester:** All
- **Steps:**
  1. Navigate to login page
  2. Enter username and password
  3. Click "Login"
- **Expected:** Successful login, redirect to dashboard
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 1.2: Two-Factor Authentication (2FA)
- **Tester:** Service Manager, Admin
- **Steps:**
  1. Login with username/password
  2. Scan QR code with Google Authenticator
  3. Enter 6-digit code
  4. Verify backup codes displayed
- **Expected:** 2FA setup successful, backup codes saved
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 1.3: Failed Login Attempts
- **Tester:** Any
- **Steps:**
  1. Enter incorrect password 3 times
  2. Check if account locked
  3. Wait 15 minutes or request password reset
- **Expected:** Account locked after 3 attempts, unlock email sent
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 1.4: Password Reset
- **Tester:** Any
- **Steps:**
  1. Click "Forgot Password"
  2. Enter email address
  3. Check email for reset link
  4. Set new password
- **Expected:** Password reset email received, password changed successfully
- **Pass/Fail:** _____ | **Notes:** _____

---

### 4.2 Leave Management (Priority: HIGH)

#### Test Case 2.1: Submit Leave Request
- **Tester:** Care Assistant, Senior Carer
- **Steps:**
  1. Navigate to Leave → Request Leave
  2. Select dates (e.g., 3 days next month)
  3. Select leave type (Annual Leave)
  4. Add note (optional)
  5. Submit request
- **Expected:** Request submitted, confirmation message, manager notified
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 2.2: Auto-Approval (≤5 days, sufficient balance)
- **Tester:** Care Assistant
- **Steps:**
  1. Request 3 days annual leave
  2. Ensure leave balance > 3 days
  3. Check if auto-approved
- **Expected:** Request auto-approved within seconds, status shows "Approved"
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 2.3: Manual Approval Required (>5 days)
- **Tester:** Care Assistant → Operational Manager
- **Steps:**
  1. CA requests 7 days leave
  2. OM receives notification
  3. OM navigates to Leave Approvals
  4. Reviews request and approves
- **Expected:** Request pending approval, OM sees in approval queue, approval successful
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 2.4: Leave Rejection
- **Tester:** Operational Manager
- **Steps:**
  1. Navigate to Leave Approvals
  2. Select pending request
  3. Add rejection reason
  4. Click "Reject"
- **Expected:** Request rejected, staff member notified with reason
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 2.5: Insufficient Leave Balance
- **Tester:** Care Assistant (with low balance)
- **Steps:**
  1. Request 10 days leave when balance is 5 days
  2. Submit request
- **Expected:** Error message "Insufficient leave balance", request blocked
- **Pass/Fail:** _____ | **Notes:** _____

---

### 4.3 Shift Management (Priority: HIGH)

#### Test Case 3.1: View Shifts (Personal)
- **Tester:** All
- **Steps:**
  1. Navigate to Dashboard
  2. Check "My Shifts" widget
  3. Navigate to Shifts → My Shifts
  4. View shifts for next 7 days
- **Expected:** All assigned shifts displayed with dates, times, units
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 3.2: Create Shift (Manager)
- **Tester:** Operational Manager
- **Steps:**
  1. Navigate to Shifts → Create Shift
  2. Select care home, unit, date
  3. Select shift type (Day, Night, Long Day)
  4. Assign staff member
  5. Save shift
- **Expected:** Shift created, staff member notified
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 3.3: Edit Existing Shift
- **Tester:** Operational Manager
- **Steps:**
  1. Navigate to Shifts → All Shifts
  2. Select shift to edit
  3. Change shift type or assigned staff
  4. Save changes
- **Expected:** Shift updated, affected staff notified
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 3.4: Delete Shift
- **Tester:** Operational Manager
- **Steps:**
  1. Select shift to delete
  2. Click "Delete"
  3. Confirm deletion
- **Expected:** Shift deleted, staff member notified
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 3.5: Shift Coverage Report
- **Tester:** Operational Manager
- **Steps:**
  1. Navigate to Reports → Shift Coverage
  2. Select date range (next 7 days)
  3. Generate report
- **Expected:** Report shows all shifts, assigned/unassigned, coverage percentage
- **Pass/Fail:** _____ | **Notes:** _____

---

### 4.4 AI Chatbot (Priority: HIGH)

#### Test Case 4.1: Basic Query (Staffing)
- **Tester:** All
- **Steps:**
  1. Navigate to AI Assistant (chatbot icon)
  2. Type: "How many staff do Hawthorn House have?"
  3. Submit query
- **Expected:** Response with total staff count, breakdown by role, sorted by count
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 4.2: Chart Generation (Staffing Trend)
- **Tester:** Service Manager, Operational Manager
- **Steps:**
  1. Open AI Assistant
  2. Type: "Show me a staffing trend chart"
  3. Submit query
- **Expected:** Chart.js visualization with 90-day staffing trend, line chart, responsive
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 4.3: Night Shift Coverage
- **Tester:** Operational Manager
- **Steps:**
  1. AI Assistant query: "Who is on night shift tonight?"
  2. Review response
- **Expected:** List of staff on night shift (names, SAP numbers, units), sorted by unit
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 4.4: Agency Usage Report
- **Tester:** Service Manager
- **Steps:**
  1. Query: "Agency usage this month"
  2. Check response
- **Expected:** Total agency shifts, percentage, breakdown by company and home
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 4.5: Care Plan Reviews
- **Tester:** Operational Manager
- **Steps:**
  1. Query: "Care plan reviews due"
  2. Review list
- **Expected:** List of residents with reviews due/overdue, sorted by urgency
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 4.6: Multiple Chart Types
- **Tester:** Service Manager
- **Steps:**
  1. Test all chart queries:
     - "Sickness comparison chart"
     - "Incident severity chart"
     - "Leave patterns chart"
     - "Staff distribution chart"
     - "ML forecast chart"
  2. Verify each renders correctly
- **Expected:** All 6 chart types display with correct data, responsive design
- **Pass/Fail:** _____ | **Notes:** _____

---

### 4.5 Dashboards (Priority: HIGH)

#### Test Case 5.1: Staff Dashboard
- **Tester:** Care Assistant, Senior Carer
- **Steps:**
  1. Login and view dashboard
  2. Check widgets:
     - My Shifts (next 7 days)
     - Leave Balance
     - Training Status
     - Upcoming Training
- **Expected:** All widgets display correct data, quick actions work
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 5.2: Manager Dashboard
- **Tester:** Operational Manager
- **Steps:**
  1. View dashboard
  2. Check widgets:
     - Shift Coverage
     - Leave Approvals (pending count)
     - Staff on Leave Today
     - Training Compliance
     - Sickness Absences
- **Expected:** All widgets accurate, click-through to detail pages works
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 5.3: Head of Service Dashboard
- **Tester:** Service Manager
- **Steps:**
  1. View dashboard
  2. Check widgets:
     - Multi-Home Summary (all 5 homes)
     - Compliance Status (traffic lights)
     - Budget Variance
     - Incident Trends
- **Expected:** Multi-home view correct, data isolated per home, no cross-home data leaks
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 5.4: Executive Dashboard
- **Tester:** Service Manager
- **Steps:**
  1. Navigate to Executive Dashboards
  2. Test all 7 dashboards:
     - Strategic Overview
     - Budget Intelligence
     - Retention & Staffing
     - Training & Compliance
     - Quality & Safety
     - Operational Efficiency
     - CI Performance Dashboard
  3. Check Chart.js visualizations
  4. Test Excel export
- **Expected:** All dashboards load < 2 seconds, charts interactive, Excel export works
- **Pass/Fail:** _____ | **Notes:** _____

---

### 4.6 Multi-Home Data Isolation (Priority: CRITICAL)

#### Test Case 6.1: Operational Manager (Single Home)
- **Tester:** Hawthorn OM
- **Steps:**
  1. Login as Hawthorn OM
  2. View staff list
  3. View shifts
  4. View leave requests
- **Expected:** Only Hawthorn House data visible, no Meadowburn/Orchard/Riverside/Victoria data
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 6.2: Service Manager (Multi-Home)
- **Tester:** Service Manager
- **Steps:**
  1. Login as Service Manager
  2. View multi-home dashboard
  3. Check all 5 homes appear
  4. Filter by specific home
- **Expected:** All 5 homes visible, filtering works, data accurate per home
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 6.3: Cross-Home Data Leak Test
- **Tester:** Hawthorn OM
- **Steps:**
  1. Attempt to access Meadowburn staff profile via direct URL
  2. Try to edit Orchard Grove shift
  3. Attempt to approve Riverside leave request
- **Expected:** All attempts blocked with "Permission Denied" or redirect to own home
- **Pass/Fail:** _____ | **Notes:** _____

---

### 4.7 Compliance & Reporting (Priority: MEDIUM)

#### Test Case 7.1: Training Compliance Report
- **Tester:** Operational Manager
- **Steps:**
  1. Navigate to Reports → Training Compliance
  2. Generate report for care home
  3. Check for expired certifications
- **Expected:** Report lists all staff, 18 training courses, expiration dates, red/green status
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 7.2: CI Performance Dashboard
- **Tester:** Service Manager
- **Steps:**
  1. Navigate to Executive → CI Performance
  2. Check actual Care Inspectorate data:
     - CS numbers
     - 4 theme ratings (1-6 scale)
     - Inspection dates
  3. View peer benchmarking table
- **Expected:** All 5 homes displayed, ratings accurate, sorted by overall score
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 7.3: Incident Report
- **Tester:** Operational Manager, Service Manager
- **Steps:**
  1. Navigate to Reports → Incidents
  2. Generate report (last 30 days)
  3. Check breakdown by severity (Low, Medium, High, Critical)
- **Expected:** All incidents listed, severity distribution chart, downloadable
- **Pass/Fail:** _____ | **Notes:** _____

---

### 4.8 Machine Learning Features (Priority: MEDIUM)

#### Test Case 8.1: 30-Day Staffing Forecast
- **Tester:** Service Manager, Operational Manager
- **Steps:**
  1. Navigate to ML → Staffing Forecast
  2. Select care unit
  3. Generate 30-day forecast
  4. Check MAPE (Mean Absolute Percentage Error)
- **Expected:** Forecast chart with Prophet predictions, 80% confidence intervals, MAPE < 30%
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 8.2: Leave Approval Prediction
- **Tester:** Operational Manager
- **Steps:**
  1. View pending leave request
  2. Check "AI Prediction" indicator (if shown)
  3. Compare prediction to actual decision
- **Expected:** AI prediction shown (Approve/Reject with confidence %), 90% accuracy
- **Pass/Fail:** _____ | **Notes:** _____

---

### 4.9 Performance & Usability (Priority: HIGH)

#### Test Case 9.1: Page Load Times
- **Tester:** All
- **Steps:**
  1. Measure load time for:
     - Dashboard
     - Staff List
     - Shift Calendar
     - Executive Dashboard
     - AI Chatbot
  2. Use browser DevTools (Network tab)
- **Expected:** All pages load < 2 seconds on standard broadband
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 9.2: Concurrent Users
- **Tester:** All (simultaneous login)
- **Steps:**
  1. All 6-9 testers login simultaneously
  2. Perform actions (view shifts, submit leave, generate reports)
  3. Check for errors or slowdowns
- **Expected:** System responsive, no errors, no data conflicts
- **Pass/Fail:** _____ | **Notes:** _____

#### Test Case 9.3: Mobile Responsiveness
- **Tester:** Any (with mobile device)
- **Steps:**
  1. Access system on mobile browser (iOS/Android)
  2. Test key features:
     - Login
     - View shifts
     - Request leave
     - AI chatbot
  3. Check layout and usability
- **Expected:** Responsive design, all features accessible, no horizontal scrolling
- **Pass/Fail:** _____ | **Notes:** _____

---

## 5. Defect Logging

### 5.1 Defect Severity Levels

| Severity | Definition | Example | Response Time |
|----------|------------|---------|---------------|
| **Critical** | System crash, data loss, security breach | Cannot login, database corruption | Immediate (< 4 hours) |
| **High** | Major feature broken, workaround difficult | Leave approval fails, shifts not saving | 1 business day |
| **Medium** | Feature issue, workaround available | Chart not displaying, formatting issue | 3 business days |
| **Low** | Cosmetic issue, minor inconvenience | Typo, alignment issue, color inconsistency | Next release |

### 5.2 Defect Template

**Defect ID:** [Auto-generated]  
**Reported By:** [Tester name]  
**Date/Time:** [Timestamp]  
**Severity:** [Critical/High/Medium/Low]  
**Test Case:** [Reference]  
**Summary:** [One-line description]  
**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Result:** [What should happen]  
**Actual Result:** [What actually happened]  
**Screenshots:** [Attach if applicable]  
**Browser/Device:** [Chrome 120, Safari iOS 17, etc.]  
**Workaround:** [If available]  
**Status:** [New/In Progress/Fixed/Closed]

### 5.3 Defect Tracking
- **Tool:** GitHub Issues or spreadsheet
- **Update Frequency:** Daily during UAT
- **Retest:** All fixed defects retested before closure

---

## 6. User Feedback Survey

### 6.1 Survey Questions (1-5 scale)

**Functionality:**
1. The system meets my daily work requirements (1=Strongly Disagree, 5=Strongly Agree)
2. All features I need are available and working correctly
3. The system is reliable and consistent

**Usability:**
4. The system is easy to navigate and use
5. I can complete tasks quickly and efficiently
6. The interface is intuitive and well-organized

**AI/ML Features:**
7. The AI chatbot provides helpful responses to my queries
8. Chart visualizations are useful for decision-making
9. ML forecasts help with planning

**Performance:**
10. Pages load quickly
11. The system responds without delays
12. I experienced no technical issues

**Overall Satisfaction:**
13. I am satisfied with the Staff Rota System
14. I would recommend this system to colleagues
15. The system is better than our previous process

**Open-Ended:**
16. What features do you like most?
17. What improvements would you suggest?
18. Any other comments or concerns?

### 6.2 Target Scores
- **Individual Questions:** Average ≥ 4.0/5.0
- **Overall Satisfaction:** Average ≥ 4.2/5.0
- **Would Recommend:** ≥ 80% (4-5 rating)

---

## 7. UAT Schedule

### Week 1: Core Features

| Day | Focus Area | Testers | Duration |
|-----|------------|---------|----------|
| **Mon** | Orientation & Setup | All | 2 hours |
| | - System overview | | |
| | - Test account setup | | |
| | - 2FA configuration | | |
| **Tue** | Authentication & Leave | Care Assistants, Senior Carers | 3 hours |
| | - Login/2FA tests | | |
| | - Leave request tests | | |
| | - Leave approval (OMs) | | |
| **Wed** | Shift Management | Operational Managers | 3 hours |
| | - Create/edit/delete shifts | | |
| | - Shift coverage reports | | |
| **Thu** | AI Chatbot | All | 2 hours |
| | - Basic queries | | |
| | - Chart generation | | |
| | - All 20+ query types | | |
| **Fri** | Dashboards | All | 3 hours |
| | - Role-specific dashboards | | |
| | - Widget accuracy | | |

### Week 2: Advanced Features & Integration

| Day | Focus Area | Testers | Duration |
|-----|------------|---------|----------|
| **Mon** | Executive Dashboards | Service Manager | 4 hours |
| | - All 7 dashboards | | |
| | - CI Performance | | |
| | - Excel exports | | |
| **Tue** | Compliance & Reporting | Operational Managers, Service Manager | 3 hours |
| | - Training compliance | | |
| | - Incident reports | | |
| | - Audit trails | | |
| **Wed** | ML Features | Service Manager, Operational Managers | 3 hours |
| | - Staffing forecasts | | |
| | - Leave predictions | | |
| **Thu** | Multi-Home Testing | Service Manager | 3 hours |
| | - Data isolation tests | | |
| | - Cross-home access attempts | | |
| **Fri** | Performance & Final Testing | All | 3 hours |
| | - Concurrent user test | | |
| | - Mobile responsiveness | | |
| | - Feedback survey | | |

**Total UAT Effort:** 29 hours over 2 weeks

---

## 8. Exit Criteria

### 8.1 Mandatory Requirements
- ✅ All CRITICAL test cases pass (100%)
- ✅ ≥ 95% of HIGH priority test cases pass
- ✅ No Critical or High severity open defects
- ✅ All security tests pass (authentication, authorization, data isolation)
- ✅ Performance tests meet targets (page loads < 2 seconds)
- ✅ User satisfaction score ≥ 4.0/5.0

### 8.2 Optional Requirements
- 🎯 ≥ 90% of MEDIUM priority test cases pass
- 🎯 ≥ 80% of LOW priority test cases pass
- 🎯 User satisfaction score ≥ 4.2/5.0
- 🎯 Zero Medium/Low defects (nice-to-have)

### 8.3 Go/No-Go Decision
- **GO:** Proceed to pilot deployment (Month 1)
- **NO-GO:** Address critical issues, repeat failed tests, reschedule UAT

**Decision Maker:** Service Manager + Technical Lead  
**Decision Date:** End of Week 2

---

## 9. Deliverables

### 9.1 UAT Report
- Executive summary (1 page)
- Test execution summary (pass/fail rates)
- Defect summary (by severity)
- User feedback analysis
- Screenshots (key features tested)
- Recommendations (go/no-go + improvements)

### 9.2 Defect Log
- All defects logged with severity, status, resolution
- Retest results for fixed defects
- Outstanding defects with workarounds

### 9.3 User Feedback Report
- Survey results (quantitative + qualitative)
- Key themes from open-ended responses
- Satisfaction scores by role
- Recommendations for improvements

---

## 10. Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Insufficient tester availability** | Medium | High | Schedule flexibility, remote testing option |
| **Test environment downtime** | Low | High | Backup server, daily backups |
| **Critical defects found late** | Medium | High | Prioritize security/data tests early |
| **User resistance to change** | Medium | Medium | Training videos, demo mode, hands-on sessions |
| **Performance issues under load** | Low | High | Load testing before UAT, scalability plan |
| **Data privacy concerns** | Low | Critical | Anonymize test data, NDAs for testers |

---

## 11. Next Steps After UAT

### Successful UAT (GO Decision)
1. **Production Prep (Week 3):**
   - Fix any Medium/Low priority defects
   - SSL configuration
   - Production email setup
   - Secrets management
   
2. **Load Testing (Week 3-4):**
   - 50+ concurrent users
   - Performance benchmarking
   - Scalability validation
   
3. **Pilot Deployment (Month 1):**
   - Deploy to 1-2 homes
   - Daily monitoring
   - User training

### Failed UAT (NO-GO Decision)
1. **Issue Resolution:**
   - Fix all Critical/High defects
   - Address user feedback concerns
   
2. **Retest:**
   - Repeat failed test cases
   - Regression testing
   
3. **Reschedule UAT:**
   - New UAT window (1 week)
   - Same test team

---

**Document Status:** Ready for Execution  
**Approval Required:** Service Manager  
**Estimated Start Date:** [To be scheduled]  
**Estimated Completion:** [Start date + 2 weeks]

---

## Appendix A: Quick Reference - Test Credentials

| Role | Username | Default Password | 2FA Required |
|------|----------|------------------|--------------|
| Operational Manager (Hawthorn) | `uat_om1` | `UAT2026!hawthorn` | No |
| Operational Manager (Meadowburn) | `uat_om2` | `UAT2026!meadowburn` | No |
| Service Manager | `uat_sm` | `UAT2026!service` | Yes |
| Senior Carer (Orchard) | `uat_senior1` | `UAT2026!orchard` | No |
| Senior Carer (Riverside) | `uat_senior2` | `UAT2026!riverside` | No |
| Care Assistant (Victoria) | `uat_ca1` | `UAT2026!victoria` | No |
| Care Assistant (Hawthorn) | `uat_ca2` | `UAT2026!hawthorn2` | No |
| Admin | `uat_admin` | `UAT2026!admin` | Yes |

**Note:** Change all passwords on first login

## Appendix B: AI Chatbot Test Queries

1. "How many staff do Hawthorn House have?"
2. "Show me a staffing trend chart"
3. "Who is on night shift tonight?"
4. "Agency usage this month"
5. "Care plan reviews due"
6. "Sickness comparison chart"
7. "Incident severity chart"
8. "Leave patterns chart"
9. "Staff distribution chart"
10. "ML forecast chart"
11. "List all senior carers"
12. "Show managers at Meadowburn"
13. "Orchard Grove performance"
14. "My leave balance"
15. "Pending leave approvals"
16. "Who is working day shift today?"
17. "Staff details for SAP12345"
18. "Compare homes by staffing"
19. "Training compliance report"
20. "Supervision due this month"

**Expected:** All queries return relevant, accurate responses with appropriate formatting (charts, lists, summaries)
