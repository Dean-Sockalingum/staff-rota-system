# SOP: Care Plan Reviews

**Document ID:** SOP-005  
**Version:** 1.0  
**Effective Date:** December 2025  
**Review Date:** March 2026  
**Owner:** Clinical Lead

---

## Purpose

This SOP defines the process for completing, reviewing, and monitoring care plan reviews for all 120 residents across 8 care units to ensure compliance with Care Inspectorate standards.

## Scope

- Applies to all 120 residents in 8 units (DEMENTIA, BLUE, ORANGE, GREEN, VIOLET, ROSE, GRAPE, PEACH)
- Covers initial 4-week reviews and ongoing 6-monthly reviews
- Used by keyworkers, unit managers, and senior management

## Responsibilities

| Role | Responsibility |
|------|----------------|
| **Keyworker** | Complete care plan reviews on time, submit for approval |
| **Unit Manager** | Approve reviews, monitor compliance, escalate overdue reviews |
| **Senior Management** | Monitor overall compliance, review reports |
| **System Administrator** | Generate schedules, send alerts, maintain system |

---

## Process Overview

```
New Admission → 4-Week Initial Review → Manager Approval → 
6-Monthly Reviews (Ongoing) → Manager Approval → Auto-Schedule Next Review
```

**Compliance Target:** 95% of reviews completed on time  
**Current Status:** 64 completed (53%), 28 overdue, 2 due soon, 26 upcoming

---

## Review Schedule

### Initial Review (New Admissions)

- **When:** 4 weeks (28 days) after admission date
- **Type:** INITIAL
- **Assigned to:** Resident's keyworker
- **Approval:** Unit manager
- **Auto-generated:** Yes, on admission (or via management command)

### Ongoing Reviews

- **When:** Every 6 months (183 days) after previous review
- **Type:** SIX_MONTH
- **Assigned to:** Current keyworker
- **Approval:** Unit manager
- **Auto-generated:** Yes, when previous review approved

### Unscheduled Reviews

- **When:** As needed (change in condition, incident, family request)
- **Type:** UNSCHEDULED
- **Assigned to:** Keyworker or manager
- **Approval:** Required
- **Auto-generated:** No (created manually)

---

## Review Statuses

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| **UPCOMING** | Due in >7 days | Monitor |
| **DUE** | Due within 7 days | Complete urgently |
| **OVERDUE** | Past due date | Complete immediately |
| **IN_PROGRESS** | Draft saved | Finish and submit |
| **PENDING_APPROVAL** | Awaiting manager | Manager must approve |
| **COMPLETED** | Approved | None (next review auto-scheduled) |
| **CANCELLED** | Not required | None |

---

## Procedure for Keyworkers

### Step 1: View Your Assigned Reviews

**Method A: Dashboard View**

1. Log in to system
2. Click **"Care Plan Reviews"** in main navigation
3. See overview of all residents
4. Filter by your unit (e.g., "DEMENTIA")
5. Reviews assigned to you highlighted

**Method B: Unit View**

1. Navigate to **Care Plans → My Unit**
2. See 15 residents in your unit
3. Cards color-coded:
   - 🔴 **Red:** OVERDUE (complete immediately!)
   - 🟡 **Yellow:** DUE (within 7 days)
   - 🟢 **Green:** COMPLETED (next review date shown)
   - 🔵 **Blue:** UPCOMING

**Method C: AI Assistant**

1. Open chatbot (bottom right corner)
2. Ask: **"When is DEM01 review due?"**
3. Get instant answer with review status and link

---

### Step 2: Complete a Review

**For OVERDUE or DUE reviews:**

1. **Click "Complete Review" Button**
   - From overview or unit view
   - Opens review form

2. **Review Header Information**
   ```
   - Resident ID: DEM01
   - Full Name: [Resident Name]
   - Unit: DEMENTIA
   - Room Number: 1
   - Admission Date: [Date]
   - Days Since Admission: [Auto-calculated]
   - Review Type: INITIAL or SIX_MONTH
   - Due Date: [Date]
   - Days Overdue: [If overdue]
   ```

3. **Complete Four Required Sections**

   **Section 1: Care Needs Assessment**
   ```
   Document current care needs:
   - Physical health
   - Mobility
   - Personal care requirements
   - Medication management
   - Continence
   - Nutrition and hydration
   - Skin integrity
   - Pain management
   ```

   **Example:**
   > "Resident requires full assistance with all personal care. Mobilizes with zimmer frame and two-person assist. Continent during day, pads at night. Diet is soft, fortified. Skin intact, no pressure areas. Paracetamol PRN for arthritis pain."

   **Section 2: Goals Progress**
   ```
   Review goals from previous care plan:
   - Which goals achieved?
   - Progress towards ongoing goals
   - Barriers to achieving goals
   - New goals identified
   ```

   **Example:**
   > "Goal to increase independence in feeding achieved - now self-feeds with adapted cutlery. Mobility goal ongoing - walks 10m with zimmer (target 20m). New goal: participate in group activities twice weekly."

   **Section 3: Changes Required**
   ```
   Document any changes needed:
   - Care plan updates
   - Risk assessments needing review
   - Equipment needs
   - Referrals required (OT, physio, GP, etc.)
   - Staffing considerations
   ```

   **Example:**
   > "Update care plan to reflect improved feeding independence. Request OT assessment for chair raise. Refer to GP for arthritis review. Increase social activities to meet new goal."

   **Section 4: Family Involvement**
   ```
   Document family/representative engagement:
   - Family contacted? (Date and method)
   - Family input received?
   - Concerns raised?
   - Agreement with care plan?
   - Next contact planned?
   ```

   **Example:**
   > "Daughter visited 25/11/25. Very pleased with mum's progress in feeding. No concerns raised. Agrees with care plan changes. Will visit again next week for Christmas planning."

4. **Save Draft (Optional)**
   - Click **"Save Draft"** button
   - Status changes to IN_PROGRESS
   - Can return later to finish
   - Draft saved automatically every 2 minutes

5. **Submit for Approval**
   - Ensure all four sections completed
   - Click **"Submit for Approval"** button
   - Status changes to PENDING_APPROVAL
   - Unit manager notified automatically
   - Cannot edit once submitted (ask manager to reject if changes needed)

**Expected Result:**
- ✅ Review submitted within 30 minutes
- ✅ Unit manager receives notification
- ✅ Review appears in manager's approval queue

---

### Step 3: Monitor Your Reviews

**Weekly Checks:**

1. Log in every Monday
2. Check **Care Plans → My Unit**
3. Review status of all assigned residents:
   - Any OVERDUE? → Complete today
   - Any DUE this week? → Schedule time to complete
   - Any IN_PROGRESS drafts? → Finish and submit
   - Any PENDING_APPROVAL? → Follow up with manager

4. Plan your week:
   - Monday: Complete any overdue
   - Tuesday-Thursday: Complete due reviews
   - Friday: Check all submitted for approval

**Email Alerts:**

You will receive automatic emails:
- **7 days before due date:** "Review due soon" reminder
- **On due date:** "Review due today" alert
- **1 day after due date:** "Review overdue" escalation
- **7 days overdue:** "Urgent: Review seriously overdue" (manager copied)

---

## Procedure for Unit Managers

### Step 1: Monitor Unit Compliance

**Daily Dashboard Check:**

1. Navigate to **Care Plans → Unit Dashboard**
2. View compliance widgets:
   ```
   Total Residents: 15
   Completed This Month: 12 (80%)
   Overdue: 2 (urgent action needed)
   Due This Week: 1
   Compliance Rate: 80% (Target: 95%)
   ```

3. **Action Based on Compliance:**
   - <50% = RED (immediate intervention required)
   - 50-79% = YELLOW (improvement needed)
   - ≥80% = GREEN (on track, maintain)

---

### Step 2: Approve Reviews

**Review Approval Queue:**

1. Click **"Pending Approvals"** tab
2. See all reviews awaiting your approval
3. For each review:

   **Click "Review Details"**

4. **Read All Four Sections Carefully**
   - Is assessment comprehensive?
   - Are goals realistic and person-centered?
   - Are changes appropriate?
   - Is family involvement documented?

5. **Check for Red Flags:**
   - ⚠️ Vague or incomplete descriptions
   - ⚠️ No mention of family contact
   - ⚠️ Goals not reviewed
   - ⚠️ Safeguarding concerns not escalated
   - ⚠️ Unexplained deterioration

6. **Add Manager Comments**
   ```
   If approving:
   "Comprehensive review. Care plan changes agreed. Well done."

   If requesting changes:
   "Please provide more detail on nutrition - fluid intake not mentioned. 
   Also clarify when OT referral will be made."
   ```

7. **Make Decision:**

   **Option A: Approve**
   - Click **"Approve & Complete"** button
   - Review status changes to COMPLETED
   - Next 6-month review auto-generated (due date = today + 183 days)
   - Keyworker notified of approval
   - Review locked (cannot be edited)

   **Option B: Request Changes**
   - Add comments explaining what needs changing
   - Click **"Reject"** button (returns to keyworker)
   - Status returns to IN_PROGRESS
   - Keyworker receives notification with your comments
   - Keyworker makes changes and resubmits

**Expected Time:** 5-10 minutes per review

---

### Step 3: Escalate Overdue Reviews

**For Reviews >7 Days Overdue:**

1. **Speak to Keyworker**
   - Is there a reason for delay?
   - Do they need support?
   - Set deadline: Complete by end of day

2. **If Still Not Completed:**
   - **Escalate to Senior Manager**
   - Document in supervision notes
   - Consider capability concerns

3. **Emergency Option:**
   - Manager can complete review on behalf of keyworker
   - Document reason in manager comments
   - Discuss with keyworker in supervision

---

## Compliance Reporting

### Weekly Unit Report

**Every Monday:**

1. Navigate to **Care Plans → Reports**
2. Select date range: "Last 7 days"
3. Filter by your unit
4. Click **"Generate Report"**

5. **Review Statistics:**
   ```
   Total Reviews Due: 3
   Completed On Time: 2 (67%)
   Completed Late: 0
   Still Outstanding: 1
   Average Days Late: 0
   ```

6. **Export and Email:**
   - Click **"Print/Export"**
   - Save as PDF
   - Email to senior management

---

### Monthly Compliance Report

**First Monday of Each Month:**

1. **Care Plans → Reports**
2. Date range: "Last 30 days"
3. Generate full report showing:
   - Total reviews completed
   - On-time percentage
   - Late reviews (with reasons)
   - Outstanding reviews
   - Unit-by-unit breakdown

4. **Present at Management Meeting**

---

## Using the AI Assistant

**Quick Queries:**

Ask the chatbot:

- **"When is DEM01 review due?"**
  - Shows resident info, review status, due date, days overdue

- **"Show all overdue reviews in DEMENTIA unit"**
  - Lists all overdue with resident IDs

- **"How do I complete a care plan review?"**
  - Provides step-by-step guide

- **"What's my unit's compliance rate?"**
  - Shows current compliance percentage

- **"Generate care plan report for last month"**
  - Direct link to reporting page with dates pre-filled

---

## Common Scenarios

### Scenario 1: New Resident Admission

**Situation:** Mrs. Smith admitted today to DEMENTIA unit, room 5

**Action:**
1. Resident record created with admission date = today
2. System auto-generates initial review:
   - Type: INITIAL
   - Due date: Today + 28 days
   - Assigned to: Designated keyworker
   - Status: UPCOMING

3. Keyworker sees review in their list (due in 28 days)
4. Week before due date: Reminder email sent
5. On day 28: Keyworker completes review
6. Manager approves
7. System creates next review (6 months from today)

**Expected Timeline:** 4-week review completed on time, first 6-month review scheduled

---

### Scenario 2: Overdue Review

**Situation:** DEM03 review was due 10 days ago, still not completed

**Actions Taken by System:**
- Day 1 overdue: Email to keyworker
- Day 3 overdue: Second email to keyworker
- Day 7 overdue: Email to keyworker + unit manager
- Day 10: Marked as serious breach, senior management alerted

**Manager Action:**
1. Check dashboard - see DEM03 overdue by 10 days (RED flag)
2. Speak to keyworker immediately
3. If keyworker sick/absent: Complete review yourself or reassign
4. Document in compliance log
5. Ensure completed by end of day
6. Discuss in next supervision session

---

### Scenario 3: Change in Resident Condition

**Situation:** Resident has fall, condition deteriorates

**Action:**
1. **Immediate:** Update daily notes, incident report, notify family
2. **Within 24 hours:** Create UNSCHEDULED care plan review
   - Navigate to resident profile
   - Click "Create Unscheduled Review"
   - Complete review documenting changes
   - Submit for urgent approval
3. Manager approves same day
4. Regular 6-monthly schedule continues unchanged

---

### Scenario 4: Keyworker Change

**Situation:** Keyworker on long-term sick leave

**Action:**
1. Unit manager assigns new keyworker to resident
2. Navigate to resident profile → Edit
3. Change **Keyworker** field to new staff member
4. Save changes
5. All future reviews auto-assign to new keyworker
6. Pending reviews can be reassigned manually:
   - Open review
   - Change **Assigned To** field
   - Save

---

## Quality Standards

### What Makes a Good Review?

✅ **DO:**
- Be specific and descriptive
- Use person-centered language ("Mrs. Smith enjoys..." not "Patient requires...")
- Document actual conversations with family (dates, names, quotes)
- Identify both achievements and areas for improvement
- Set SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)
- Highlight any safeguarding or dignity concerns
- Reference other documents (risk assessments, GP letters, etc.)

❌ **DON'T:**
- Use vague terms ("doing well", "no change")
- Copy/paste from previous reviews without updating
- Miss family contact (must attempt even if unsuccessful)
- Ignore deterioration or concerns
- Set unrealistic goals
- Submit incomplete sections
- Leave to last minute

---

### Review Audit Checklist

Managers use this to assess quality:

- [ ] All four sections completed in full
- [ ] Person-centered language used
- [ ] Family contact documented with date
- [ ] Goals are SMART
- [ ] Changes linked to assessment
- [ ] Any concerns escalated appropriately
- [ ] Written clearly and professionally
- [ ] No spelling/grammar errors
- [ ] Completed on time
- [ ] Evidence-based (references observations, reports, etc.)

**Score:** 9-10/10 = Excellent | 7-8/10 = Good | 5-6/10 = Adequate | <5/10 = Requires improvement

---

## Troubleshooting

### Issue: "Cannot find resident in system"

**Cause:** Resident not added to database yet

**Solution:**
1. Contact administrator to add resident record
2. Provide: Full name, unit, room number, admission date
3. Once added, initial review auto-generates

---

### Issue: "Review shows as overdue but was completed on paper"

**Cause:** Paper review not entered into system

**Solution:**
1. Open the review in system
2. Transcribe paper review into four sections
3. Add note in manager comments: "Completed on paper DD/MM/YY, entered retrospectively"
4. Submit and approve
5. Moving forward: Only use electronic system

---

### Issue: "Cannot edit review - says locked"

**Cause:** Review already approved and completed

**Solution:**
- Completed reviews cannot be edited (audit requirement)
- If error found: Create note in resident record
- If major issue: Create unscheduled review with corrections

---

### Issue: "Manager hasn't approved my review for 2 weeks"

**Cause:** Review stuck in approval queue

**Solution:**
1. Speak to manager directly
2. If manager absent: Contact senior manager or deputy
3. Reviews MUST be approved within 5 working days
4. Escalate if still not approved

---

## Management Commands

### Generate Missing Reviews

Ensures all residents have proper review schedules:

```bash
cd /Users/deansockalingum/Staff\ Rota/rotasystems
python3 manage.py generate_careplan_reviews
```

**Output:**
```
Residents processed: 120
Initial reviews created: 5
6-month reviews created: 12
Already scheduled: 103
```

**Run:** Weekly (automated on Mondays at 8 AM)

---

### Send Review Alerts

Sends email reminders for due/overdue reviews:

```bash
python3 manage.py send_careplan_alerts
```

**Sends:**
- 7-day advance warnings
- Due today alerts
- Overdue escalations
- Manager notifications

**Run:** Daily at 8:30 AM (automated)

---

### Compliance Statistics

```bash
python3 manage.py careplan_stats
```

**Output:**
```
Total Residents: 120
Reviews Due This Month: 24
Completed On Time: 20 (83%)
Overdue: 4 (17%)

By Unit:
DEMENTIA: 12/15 complete (80%)
BLUE: 14/15 complete (93%)
...
```

---

## Key Performance Indicators (KPIs)

**We track:**

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **On-Time Completion** | ≥95% | 53% | 🔴 Needs urgent improvement |
| **Average Days Overdue** | <3 days | 12 days | 🔴 Too high |
| **Manager Approval Time** | <5 days | [TBC] | - |
| **Review Quality Score** | ≥8/10 | [TBC] | - |
| **Family Contact Rate** | 100% | [TBC] | - |

**Monthly Review Meeting:** Discuss KPIs and improvement actions

---

## Training Requirements

**Keyworkers must complete:**
- [ ] Care plan review writing training (2 hours)
- [ ] System navigation training (30 minutes)
- [ ] Person-centered care training (annual)
- [ ] Shadowing experienced keyworker (1-2 reviews)
- [ ] Supervised first review (with manager feedback)

**Managers must complete:**
- [ ] All keyworker training
- [ ] Review approval and quality assessment (1 hour)
- [ ] Compliance monitoring (30 minutes)

---

## Related Procedures

- Resident Admission Procedure
- Care Plan Writing Policy
- Safeguarding Policy
- Family Communication Policy
- [SOP: Compliance Reporting](SOP_COMPLIANCE_REPORTING.md)

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Dec 2025 | Initial SOP creation | Clinical Lead |

---

## Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **Clinical Lead** | | | |
| **Operations Director** | | | |
| **Care Inspectorate Liaison** | | | |

---

**For support with care plan reviews:**
- **AI Assistant:** Ask "How do I complete a care plan review?"
- **Clinical Lead:** [Insert contact]
- **System Administrator:** [Insert contact]

**Next SOP:** [Compliance Reporting](SOP_COMPLIANCE_REPORTING.md)
