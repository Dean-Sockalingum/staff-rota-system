# Staff Rota System - User Training Guide
## For Operational Managers & Senior Managers

**Training Duration:** 3 hours  
**Format:** Hands-on workshop with live system  
**Target Audience:** OMs, SMs, Care Home Managers  
**Prerequisites:** Basic computer skills, understanding of shift patterns

---

## Table of Contents

**Session 1: System Overview & Login (30 minutes)**
- [1.1 What is the Staff Rota System?](#11-what-is-the-staff-rota-system)
- [1.2 First Login & Password Setup](#12-first-login--password-setup)
- [1.3 Dashboard Tour](#13-dashboard-tour)

**Session 2: Viewing & Managing Schedules (45 minutes)**
- [2.1 Viewing the Rota](#21-viewing-the-rota)
- [2.2 Understanding Shift Types](#22-understanding-shift-types)
- [2.3 Filtering and Searching](#23-filtering-and-searching)
- [2.4 Printing and Exporting](#24-printing-and-exporting)

**Session 3: Vacancy Management (30 minutes)**
- [3.1 Viewing Vacant Shifts](#31-viewing-vacant-shifts)
- [3.2 Filling Vacancies Manually](#32-filling-vacancies-manually)
- [3.3 Requesting Agency Staff](#33-requesting-agency-staff)
- [3.4 Vacancy Reports](#34-vacancy-reports)

**Session 4: Leave Management (30 minutes)**
- [4.1 Viewing Leave Requests](#41-viewing-leave-requests)
- [4.2 Approving/Rejecting Leave](#42-approvingreject leave)
- [4.3 Leave Targets & Compliance](#43-leave-targets--compliance)
- [4.4 Email Notifications](#44-email-notifications)

**Session 5: ML-Powered Features (30 minutes)**
- [5.1 Demand Forecasting](#51-demand-forecasting)
- [5.2 Automated Shift Optimization](#52-automated-shift-optimization)
- [5.3 Interpreting Recommendations](#53-interpreting-recommendations)
- [5.4 Cost Optimization](#54-cost-optimization)

**Session 6: Reporting & Analytics (15 minutes)**
- [6.1 Weekly Staffing Reports](#61-weekly-staffing-reports)
- [6.2 Compliance Reports](#62-compliance-reports)
- [6.3 Cost Analysis](#63-cost-analysis)

---

## Session 1: System Overview & Login (30 minutes)

### 1.1 What is the Staff Rota System?

**Purpose:** Automated staff scheduling system that:
- ✅ Creates optimal shift rotas based on demand
- ✅ Predicts staffing needs using machine learning
- ✅ Manages leave requests and approvals
- ✅ Ensures Care Inspectorate compliance
- ✅ Reduces costs while maintaining quality care

**Key Benefits for You:**
- ⏰ Save 10-15 hours/week on manual scheduling
- 📊 Real-time visibility of staffing levels
- 💰 12.6% reduction in agency costs
- ✅ Automatic compliance checking
- 📧 Email notifications for important events

### 1.2 First Login & Password Setup

**Step 1:** Navigate to https://rota.yourcompany.com

**Step 2:** Enter your credentials
- **Username:** Your SAP number (e.g., SAP12345)
- **Temporary Password:** Provided by IT team

**Step 3:** Create new password
- Minimum 8 characters
- Must include: uppercase, lowercase, number
- Example: `Rota2026!`

**Step 4:** Set up 2-factor authentication (if enabled)
- Download Google Authenticator app
- Scan QR code
- Enter 6-digit code

**Troubleshooting:**
- **Forgot password?** Click "Forgot Password" → Enter email → Check inbox
- **Account locked?** Contact IT: support@yourcompany.com

### 1.3 Dashboard Tour

After login, you'll see your **Dashboard** - your command center:

```
┌─────────────────────────────────────────────────────┐
│  Staff Rota System - Dashboard                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  📅 Today's Shifts          👥 Vacant Shifts (7)    │
│  Day: 15 staff              🏥 Orchard Grove        │
│  Night: 8 staff             Unit: OG Mulberry       │
│  Total: 23 staff            Date: 22 Dec 2025      │
│                                                      │
│  📊 This Week's Forecast    ✉️ Pending Leave (3)   │
│  Mon: 24 staff predicted    Alice Smith - 2 weeks   │
│  Tue: 22 staff predicted    Bob Jones - 1 day       │
│  Wed: 25 staff predicted    Carol White - 3 days    │
│                                                      │
│  💰 Cost Summary            ⚠️ Alerts (1)           │
│  This Week: £8,420          WTD compliance warning  │
│  Last Week: £8,950 (-6%)    Unit: OG Willow        │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Dashboard Sections:**

1. **Today's Shifts** - Current staffing levels
2. **Vacant Shifts** - Unfilled shifts needing attention
3. **Forecast** - Predicted demand for next 7 days
4. **Pending Leave** - Requests awaiting approval
5. **Cost Summary** - Weekly spending vs. budget
6. **Alerts** - Compliance warnings or issues

**Quick Actions (Top Menu):**
- 📅 **View Rota** - See full schedule
- 👤 **Manage Staff** - Add/edit staff profiles
- 🏖️ **Leave Requests** - Approve/reject leave
- 📊 **Reports** - Generate analytics
- ⚙️ **Settings** - Customize preferences

---

## Session 2: Viewing & Managing Schedules (45 minutes)

### 2.1 Viewing the Rota

**Navigate:** Dashboard → "View Rota"

**Calendar View:**
```
    Week of 21 Dec 2025 - Orchard Grove - OG Mulberry
┌──────┬─────────┬─────────┬─────────┬─────────┬─────────┐
│ Date │ Mon 21  │ Tue 22  │ Wed 23  │ Thu 24  │ Fri 25  │
├──────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│ 08:00│ Alice   │ Alice   │ Bob     │ Alice   │ Carol   │
│ -    │ Bob     │ Carol   │ Carol   │ Bob     │ David   │
│ 20:00│ Carol   │ David   │ David   │ Carol   │ [VACANT]│
│      │ David   │         │         │ David   │         │
├──────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│ 20:00│ Eve     │ Eve     │ Frank   │ Eve     │ Frank   │
│ -    │ Frank   │ Frank   │ George  │ Frank   │ George  │
│ 08:00│ George  │ George  │         │ George  │         │
└──────┴─────────┴─────────┴─────────┴─────────┴─────────┘
```

**Color Coding:**
- 🟢 **Green** = Fully staffed (meets demand)
- 🟡 **Yellow** = Slightly understaffed (90-99% demand)
- 🔴 **Red** = Critically understaffed (<90% demand)
- ⚪ **White with "VACANT"** = Unfilled shift

**Clicking on a Shift:**
- See staff details (name, role, SAP number)
- View shift notes or warnings
- Edit shift (reassign, cancel, add notes)

### 2.2 Understanding Shift Types

**Day Shift (08:00-20:00):**
- Care Workers, Senior Carers
- Activities Coordinators
- Kitchen staff

**Night Shift (20:00-08:00):**
- Care Workers (night rate applies)
- Waking night staff
- Sleeping night staff (if applicable)

**Shift Icons:**
- 👤 = Permanent staff
- 🏢 = Agency staff (higher cost)
- 🌙 = Night shift
- ☀️ = Day shift
- ⏰ = Overtime

### 2.3 Filtering and Searching

**Filters Available:**

1. **By Care Home:**
   - Select from dropdown: Orchard Grove, Victoria Gardens, etc.

2. **By Unit:**
   - After selecting home, choose unit: OG Mulberry, OG Willow, etc.

3. **By Date Range:**
   - This Week, Next Week, This Month, Custom Range

4. **By Shift Type:**
   - Day shifts only, Night shifts only, All shifts

5. **By Staff Member:**
   - Search by name or SAP number

**Example: Find all Alice's shifts next week**
1. Click "Filter" button
2. Date Range → "Next Week"
3. Staff Member → Search "Alice" → Select
4. Click "Apply"

### 2.4 Printing and Exporting

**Print Rota:**
1. View desired time period (e.g., "Next Week")
2. Click "Print" button (printer icon)
3. Preview opens → Print or Save as PDF

**Export to Excel:**
1. Click "Export" button (download icon)
2. Choose format: Excel (.xlsx) or CSV
3. File downloads automatically
4. Open in Excel for further editing

**Use Cases:**
- Print weekly rota for staff noticeboard
- Export for payroll processing
- Archive historical rotas

---

## Session 3: Vacancy Management (30 minutes)

### 3.1 Viewing Vacant Shifts

**Navigate:** Dashboard → "Vacant Shifts" widget or Menu → "Vacancies"

**Vacancy List:**
```
📋 Vacant Shifts (7 found)

┌────────────┬──────────┬────────┬──────────┬─────────┐
│ Date       │ Unit     │ Shift  │ Role     │ Status  │
├────────────┼──────────┼────────┼──────────┼─────────┤
│ 22 Dec Mon │ Mulberry │ Day    │ Carer    │ URGENT  │
│ 23 Dec Tue │ Willow   │ Night  │ Carer    │ Urgent  │
│ 25 Dec Thu │ Mulberry │ Day    │ Carer    │ Open    │
│ 27 Dec Sat │ Oak      │ Day    │ Senior   │ Open    │
│ 29 Dec Mon │ Mulberry │ Night  │ Carer    │ Open    │
│ 30 Dec Tue │ Willow   │ Day    │ Carer    │ Open    │
│ 31 Dec Wed │ Oak      │ Night  │ Carer    │ Open    │
└────────────┴──────────┴────────┴──────────┴─────────┘
```

**Vacancy Priorities:**
- 🔴 **URGENT** = Within 48 hours, <80% staffed
- 🟡 **Urgent** = Within 1 week, <90% staffed
- 🟢 **Open** = >1 week out, normal priority

### 3.2 Filling Vacancies Manually

**Option 1: Assign Existing Staff**

1. Click on vacant shift row
2. "Assign Staff" button appears
3. See list of **available staff**:
   ```
   Available Staff for 22 Dec 2025, Day Shift:
   
   ✓ Alice Smith (Carer, 0 hours this week)
   ✓ Bob Jones (Carer, 12 hours this week)
   ⚠️ Carol White (Carer, 36 hours this week) - Near WTD limit
   ✗ David Brown (Carer, on leave)
   ✗ Eve Taylor (Senior Carer, already assigned to Willow)
   ```
4. Select staff member → Click "Assign"
5. System checks:
   - ✅ Working Time Directive compliance
   - ✅ Role qualification match
   - ✅ No double-booking
6. Confirmation: "Shift assigned to Alice Smith"

**Option 2: Request Overtime**

1. Click "Request Overtime" button
2. Select staff member
3. Enter justification (e.g., "Short notice sickness cover")
4. System calculates overtime rate (1.5x)
5. Submit for approval (if required)

### 3.3 Requesting Agency Staff

**When to Use Agency:**
- No permanent staff available
- Last-minute sickness cover
- Temporary surge in demand

**Steps:**

1. Click vacant shift → "Request Agency"
2. Fill form:
   ```
   Agency Request Form
   
   Date: 22 Dec 2025
   Shift: Day (08:00-20:00)
   Unit: OG Mulberry
   Role: Care Worker
   
   Agency: [Select from dropdown]
   - Premier Care
   - Scottish Staffing Solutions
   - Emergency Carers Ltd
   
   Reason: [Required]
   - Last-minute sickness
   - Planned leave coverage
   - Surge demand
   - Other (specify)
   
   Max Rate: £18.50/hour [Default from contract]
   
   Notes: [Optional]
   "Prefer Maria if available - familiar with residents"
   ```
3. Click "Submit Request"
4. Email sent to agency contact
5. Agency confirms → Shift marked "Agency Pending"
6. Agency assigns staff → Update shift with agency staff name

**Cost Warning:**
```
⚠️ Agency Cost Alert
Permanent staff: £14.20/hour = £170.40 total
Agency staff: £18.50/hour = £222.00 total
Additional cost: £51.60 (+30.3%)

Proceed with agency request? [Yes] [No]
```

### 3.4 Vacancy Reports

**Generate Weekly Vacancy Report:**

1. Menu → "Reports" → "Vacancy Report"
2. Select date range (default: Next 7 days)
3. Report shows:
   ```
   Vacancy Report: 21 Dec - 27 Dec 2025
   
   Summary:
   - Total Shifts: 420
   - Vacant Shifts: 7 (1.7%)
   - Agency Requested: 2
   - Urgent (< 48hrs): 1
   
   By Unit:
   OG Mulberry: 3 vacant (4.2%)
   OG Willow: 2 vacant (2.8%)
   OG Oak: 2 vacant (2.8%)
   
   Forecast vs. Actual:
   Predicted vacancies: 5 (±2)
   Actual vacancies: 7 ✗ (Outside forecast range)
   
   Recommendation:
   Consider increasing staff pool by 2-3 carers for Mulberry unit
   ```
4. Export as PDF or Excel
5. Share with Senior Management

---

## Session 4: Leave Management (30 minutes)

### 4.1 Viewing Leave Requests

**Navigate:** Dashboard → "Pending Leave" or Menu → "Leave Management"

**Leave Request Queue:**
```
📋 Leave Requests Awaiting Approval (3)

┌──────────────┬─────────────┬──────────┬────────┬─────────┐
│ Staff        │ Request Date│ Period   │ Days   │ Type    │
├──────────────┼─────────────┼──────────┼────────┼─────────┤
│ Alice Smith  │ 15 Dec 2025 │ 5-19 Jan │ 14 days│ Annual  │
│ Bob Jones    │ 18 Dec 2025 │ 22 Dec   │ 1 day  │ Sick    │
│ Carol White  │ 20 Dec 2025 │ 2-4 Jan  │ 3 days │ Annual  │
└──────────────┴─────────────┴──────────┴────────┴─────────┘
```

**Click on Request to See Details:**
```
Leave Request Details - Alice Smith

Staff: Alice Smith (SAP12345)
Unit: OG Mulberry
Role: Care Worker

Leave Type: Annual Leave
Start Date: 5 Jan 2026
End Date: 19 Jan 2026
Total Days: 14 days (10 working days)

Leave Balance:
- Entitlement: 28 days/year
- Taken: 10 days
- Approved Pending: 0 days
- If Approved: 20 days used, 8 days remaining

Impact Analysis:
⚠️ Staffing Impact: MEDIUM
- 5 shifts affected in Mulberry unit
- Forecast demand: 4-5 carers needed per shift
- Current coverage: 4 carers (including Alice)
- Coverage if approved: 3 carers (-25%)

✅ Replacement Options:
- Bob Jones available for 3/5 shifts
- Overtime available from Carol White
- Agency backup: Premier Care (£18.50/hr)

📊 Team Leave:
- 2 other Mulberry staff on leave same period
- Total Mulberry staff out: 3/12 (25%)
- Recommended max: 20%

Manager Notes: [Optional]
"Alice has worked all Christmas period - approve"
```

### 4.2 Approving/Rejecting Leave

**Approve Leave:**

1. Review impact analysis
2. Check replacement coverage
3. Click "Approve" button
4. Confirmation:
   ```
   ✅ Leave Approved
   
   Email sent to Alice Smith confirming approval
   Leave calendar updated
   Shifts marked as "On Leave" in rota
   
   Action Required:
   - Assign replacement staff for 5 shifts
   - Consider agency backup for peak days
   ```

**Reject Leave:**

1. Click "Reject" button
2. **Must provide reason** (required):
   ```
   Reason for Rejection:
   
   ☐ Insufficient coverage available
   ☐ Too many staff already on leave
   ☐ Business critical period
   ☐ Outside notice period (< 2 weeks)
   ☐ Other: [Specify]
   
   Manager Comments: [Required]
   "Already have 2 staff on leave that week. Can you take week of 26 Jan instead?"
   ```
3. Click "Confirm Rejection"
4. Email sent to staff with reason
5. Staff can resubmit with different dates

**Partial Approval:**

Some systems allow partial approval (e.g., 7 of 14 days):

1. Click "Partial Approval"
2. Adjust dates:
   ```
   Original Request: 5-19 Jan (14 days)
   
   Approve: 5-12 Jan (7 days)
   Suggest Alternative for: 12-19 Jan
   
   Reason:
   "Can approve first week. Second week conflicts with training event. Please resubmit for different dates."
   ```

### 4.3 Leave Targets & Compliance

**Annual Leave Targets:**

UK care sector best practice: Encourage staff to use 50% leave by June 30, 80% by September 30.

**System Tracks:**
```
Leave Target Dashboard - As of 21 Dec 2025

┌────────────────┬──────────┬─────────┬─────────┬──────────┐
│ Staff          │ Entitled │ Taken   │ Target  │ Status   │
├────────────────┼──────────┼─────────┼─────────┼──────────┤
│ Alice Smith    │ 28 days  │ 10 days │ 22 days │ 🔴 Behind│
│ Bob Jones      │ 28 days  │ 24 days │ 22 days │ 🟢 On Track│
│ Carol White    │ 28 days  │ 18 days │ 22 days │ 🟡 Slight │
│ David Brown    │ 21 days  │ 15 days │ 17 days │ 🟡 Slight │
└────────────────┴──────────┴─────────┴─────────┴──────────┘

Target for 31 Dec: 80% of annual entitlement (22-23 days)
```

**Automated Email Reminders:**
- Sent to staff in November: "You have 18 days unused leave. Please book before year end."
- Sent to managers weekly: "3 staff below leave target - encourage booking"

### 4.4 Email Notifications

**You Receive Emails For:**

1. **New Leave Request:**
   ```
   Subject: Leave Request - Alice Smith (5-19 Jan 2026)
   
   Alice Smith has requested 14 days annual leave.
   Dates: 5 Jan 2026 - 19 Jan 2026
   
   [View Request] [Approve] [Reject]
   ```

2. **Shift Vacancy Alert:**
   ```
   Subject: URGENT: Vacant Shift Tomorrow (22 Dec 2025)
   
   1 shift remains unfilled for tomorrow:
   - Date: 22 Dec 2025
   - Unit: OG Mulberry
   - Shift: Day (08:00-20:00)
   
   [Fill Vacancy] [Request Agency]
   ```

3. **Working Time Directive Warning:**
   ```
   Subject: WTD Compliance Alert - Carol White
   
   Carol White is approaching 48-hour weekly limit:
   - Current Week: 42 hours
   - Next Scheduled: 8 hours (50 hours total)
   
   Action required: Review schedule or request WTD opt-out
   
   [View Schedule] [Request Opt-Out]
   ```

4. **Weekly Summary (Every Monday 7am):**
   ```
   Subject: Weekly Rota Summary - Week of 21 Dec 2025
   
   Staffing Overview:
   - Total Shifts: 140
   - Vacant: 7 (5%)
   - Agency: 2 (1.4%)
   
   Leave Pending: 3 requests
   Compliance Alerts: 1 (WTD warning)
   
   Cost: £8,420 (6% below budget)
   
   [View Full Report]
   ```

**Configure Email Preferences:**
- Menu → Settings → Email Notifications
- Choose frequency: Real-time, Daily digest, Weekly summary
- Select which alerts to receive

---

## Session 5: ML-Powered Features (30 minutes)

### 5.1 Demand Forecasting

**What is Forecasting?**

The system uses **Prophet machine learning** to predict how many staff you'll need in future weeks, based on:
- Historical shift patterns
- Seasonal trends (winter = higher demand)
- Day of week patterns (weekends = different needs)
- Public holidays
- Occupancy levels

**View Forecast:**

1. Menu → "Reports" → "Demand Forecast"
2. Select unit: OG Mulberry
3. See 30-day forecast:

```
Demand Forecast - OG Mulberry Unit

┌────────────┬─────────────┬──────────────┬──────────┐
│ Date       │ Predicted   │ Confidence   │ Planned  │
├────────────┼─────────────┼──────────────┼──────────┤
│ 22 Dec Mon │ 4.2 staff   │ ±0.5 (Good)  │ 4 staff  │
│ 23 Dec Tue │ 4.1 staff   │ ±0.5 (Good)  │ 4 staff  │
│ 24 Dec Wed │ 4.5 staff   │ ±0.7 (Fair)  │ 4 staff ⚠️│
│ 25 Dec Thu │ 5.2 staff   │ ±0.9 (Fair)  │ 4 staff 🔴│
│ 26 Dec Fri │ 5.0 staff   │ ±0.8 (Fair)  │ 5 staff  │
└────────────┴─────────────┴──────────────┴──────────┘

⚠️ Understaffing Alert:
- Christmas Day (25 Dec): Predicted 5.2 staff, Planned 4 staff
- Recommendation: Add 1-2 staff to Christmas Day rota
```

**Interpreting Confidence:**
- **±0.5 (Good):** Forecast accurate 90% of time
- **±0.7 (Fair):** Forecast accurate 80% of time
- **±1.0 (Caution):** Forecast less certain (unusual patterns)

**How to Use Forecasts:**

✅ **DO:**
- Plan rotas 2-3 weeks in advance using forecasts
- Add extra staff when forecast predicts high demand
- Book agency in advance for predicted peaks

❌ **DON'T:**
- Rely solely on forecast - use your judgment
- Ignore local knowledge (e.g., expected admissions)
- Over-react to small variations (±0.5 staff)

### 5.2 Automated Shift Optimization

**What is Optimization?**

The system can **automatically create rotas** that:
- ✅ Meet predicted demand
- ✅ Minimize costs (prefer permanent over agency)
- ✅ Respect Working Time Directive (48-hour week)
- ✅ Match staff skills to unit needs
- ✅ Distribute shifts fairly

**Run Optimization:**

1. Menu → "Schedule" → "Optimize Rota"
2. Configure:
   ```
   Optimization Settings
   
   Date Range: [21 Dec 2025] to [27 Dec 2025] (1 week)
   
   Units to Optimize: [Select All ✓]
   ☑ OG Mulberry
   ☑ OG Willow
   ☑ OG Oak
   
   Optimization Goals: (Drag to prioritize)
   1. Meet demand forecast 🎯
   2. Minimize agency usage 💰
   3. Balance workload 👥
   4. Respect WTD limits ⏰
   5. Prefer permanent staff 👤
   
   Advanced Options:
   ☐ Allow overtime (max 10% of shifts)
   ☑ Respect staff preferences (if available)
   ☐ Lock existing shifts (don't reassign)
   ```
3. Click "Run Optimization" → Processing ~30 seconds
4. See results:
   ```
   ✅ Optimization Complete
   
   Summary:
   - 140 shifts optimized
   - 7 vacancies filled
   - 2 agency shifts converted to permanent
   - 0 WTD violations
   - Estimated savings: £520/week (6.2%)
   
   Changes Preview:
   ┌──────────┬─────────────────────────────────┐
   │ 22 Dec   │ Added: Alice to Day shift       │
   │ 23 Dec   │ Removed: Agency (Jane) →        │
   │          │ Replaced: Bob (permanent)       │
   │ 24 Dec   │ Added: Carol to Night shift     │
   └──────────┴─────────────────────────────────┘
   
   [Apply Changes] [Review Details] [Cancel]
   ```
5. Review changes → Click "Apply Changes"

**When Optimization Fails:**

```
⚠️ Optimization Warning

Could not fully optimize schedule:
- 2 shifts remain vacant (insufficient staff pool)
- 1 WTD violation (Carol White: 52 hours if optimized)

Suggestions:
- Hire 2 additional care workers for Mulberry unit
- Request WTD opt-out from Carol White
- Use agency for remaining vacancies
```

### 5.3 Interpreting Recommendations

**Cost Optimization Recommendations:**

After optimization, system shows **potential savings**:

```
💰 Cost Optimization Recommendations

Current Weekly Cost: £8,950
Optimized Weekly Cost: £8,430
Potential Savings: £520/week (5.8%)

Breakdown:
✓ Reduced agency usage: -£380/week
  - 3 agency shifts → permanent staff
  
✓ Optimized shift distribution: -£140/week
  - Reduced overtime by 8 hours
  - Better demand matching
  
⚠️ Trade-offs:
- Some staff may receive fewer hours (Bob: -4hrs)
- Requires 2-3 week advance planning
- Less flexibility for last-minute changes

Recommendation: APPLY
Expected annual savings: £27,040
```

**Staffing Gap Analysis:**

```
📊 Staffing Gap Analysis - OG Mulberry

Current Staff Pool: 12 carers, 3 senior carers

Demand Analysis (Next 30 Days):
- Average daily demand: 4.3 carers
- Peak demand: 5.5 carers (Christmas/New Year)
- Minimum demand: 3.8 carers (mid-week)

Gap Identification:
🔴 CRITICAL GAP: Christmas Day (25 Dec)
   - Demand: 5.5 carers
   - Available: 3 carers (2 on leave, 1 sick)
   - Shortfall: -2.5 carers

🟡 MINOR GAP: Weekends in January
   - Demand: 4.5 carers average
   - Available: 4 carers (assuming 1 on leave)
   - Shortfall: -0.5 carers

Recommendations:
1. Recruit 1 full-time carer for Mulberry (Priority: HIGH)
2. Establish bank staff pool for weekend coverage
3. Pre-book agency for Christmas Day (deadline: 18 Dec)
```

### 5.4 Cost Optimization

**View Cost Dashboard:**

1. Menu → "Reports" → "Cost Analysis"
2. See breakdown:

```
Cost Analysis - Week of 21 Dec 2025

Total Staffing Cost: £8,420

By Type:
┌──────────────────┬─────────┬───────┬─────────┐
│ Staff Type       │ Hours   │ Rate  │ Total   │
├──────────────────┼─────────┼───────┼─────────┤
│ Permanent Day    │ 480hrs  │ £14.20│ £6,816  │
│ Permanent Night  │ 72hrs   │ £16.50│ £1,188  │
│ Agency Day       │ 12hrs   │ £18.50│ £222    │
│ Overtime         │ 8hrs    │ £21.30│ £170    │
│ Bank Staff       │ 4hrs    │ £15.50│ £62     │
└──────────────────┴─────────┴───────┴─────────┘

Comparison to Last Week:
- Last Week: £8,950
- This Week: £8,420
- Savings: £530 (5.9%) ✅

Comparison to Budget:
- Budgeted: £9,000/week
- Actual: £8,420/week
- Under Budget: £580 (6.4%) ✅

Cost Drivers:
✓ Reduced agency: -£380 (2 fewer agency shifts)
✓ Less overtime: -£170 (4 fewer OT hours)
✗ Increased bank staff: +£20 (but cheaper than agency)
```

**Monthly Cost Trends:**

```
📈 Monthly Cost Trends

December 2025:
Week 1: £9,200 (peak - holiday season)
Week 2: £8,950 (normal)
Week 3: £8,420 (optimized ✓)
Week 4: £9,500 (forecast - Christmas/NY)

Average: £9,017/week
Monthly Total: £36,070

Target: £9,000/week (£36,000/month)
Variance: +£70 (+0.2%) ✅ On Target

Year-to-Date Savings: £4,320 (12.6% vs. previous year)
```

---

## Session 6: Reporting & Analytics (15 minutes)

### 6.1 Weekly Staffing Reports

**Auto-Generated Every Monday (7am Email):**

```
Weekly Staffing Report - Week of 21 Dec 2025
Care Home: Orchard Grove

SUMMARY:
- Total Shifts: 140
- Shifts Filled: 133 (95%)
- Vacant: 7 (5%)
- Agency Used: 2 (1.4%)
- Average Cost/Shift: £60.14

BY UNIT:
OG Mulberry:
  - Demand: 28 shifts
  - Filled: 26 (93%)
  - Agency: 1
  - Cost: £1,685

OG Willow:
  - Demand: 28 shifts
  - Filled: 27 (96%)
  - Agency: 0
  - Cost: £1,595

OG Oak:
  - Demand: 28 shifts
  - Filled: 25 (89%)
  - Agency: 1
  - Cost: £1,710

FORECAST ACCURACY:
  - Predicted Demand: 140 ±5 shifts
  - Actual Demand: 140 shifts
  - Accuracy: 100% (within confidence interval ✓)

COMPLIANCE:
  ✓ All WTD limits respected
  ✓ No skill mismatches
  ⚠️ 1 staff member near leave target shortfall

RECOMMENDATIONS:
  - Mulberry unit: Recruit 1 additional carer
  - Consider 2-week advance scheduling to reduce agency use
```

### 6.2 Compliance Reports

**Working Time Directive (WTD) Report:**

```
WTD Compliance Report - December 2025

┌────────────────┬────────────┬──────────┬───────────┐
│ Staff          │ Week Hours │ WTD Limit│ Status    │
├────────────────┼────────────┼──────────┼───────────┤
│ Alice Smith    │ 36 hours   │ 48 hours │ ✅ OK     │
│ Bob Jones      │ 44 hours   │ 48 hours │ ✅ OK     │
│ Carol White    │ 46 hours   │ 48 hours │ ⚠️ Near   │
│ David Brown    │ 40 hours   │ 48 hours │ ✅ OK     │
│ Eve Taylor     │ 38 hours   │ 48 hours │ ✅ OK     │
└────────────────┴────────────┴──────────┴───────────┘

⚠️ Warnings:
- Carol White at 96% of limit (46/48 hours)
- Cannot assign additional shifts this week

Compliance Score: 100% (All staff within limits)
```

**Leave Compliance Report:**

```
Leave Target Compliance - As of 31 Dec 2025

Target: 80% of annual leave taken by year end

┌────────────────┬───────────┬────────┬─────────┬──────────┐
│ Staff          │ Entitle   │ Taken  │ Target  │ Status   │
├────────────────┼───────────┼────────┼─────────┼──────────┤
│ Alice Smith    │ 28 days   │ 24 days│ 22 days │ ✅ Above │
│ Bob Jones      │ 28 days   │ 26 days│ 22 days │ ✅ Above │
│ Carol White    │ 28 days   │ 18 days│ 22 days │ 🔴 Below │
│ David Brown    │ 21 days   │ 17 days│ 17 days │ ✅ On    │
└────────────────┴───────────┴────────┴─────────┴──────────┘

Action Required:
- Carol White: 4 days below target
- Email reminder sent: 15 Dec 2025
- Follow-up required: Schedule meeting to book leave
```

### 6.3 Cost Analysis

**Monthly Cost Report:**

```
Cost Analysis - December 2025
Care Home: Orchard Grove

┌──────────────────┬─────────┬─────────┬──────────┐
│ Cost Category    │ Actual  │ Budget  │ Variance │
├──────────────────┼─────────┼─────────┼──────────┤
│ Permanent Staff  │ £32,400 │ £32,000 │ +£400    │
│ Agency Staff     │ £1,800  │ £3,000  │ -£1,200 ✓│
│ Overtime         │ £680    │ £1,000  │ -£320 ✓  │
│ Bank Staff       │ £250    │ £200    │ +£50     │
├──────────────────┼─────────┼─────────┼──────────┤
│ TOTAL            │ £35,130 │ £36,200 │ -£1,070 ✓│
└──────────────────┴─────────┴─────────┴──────────┘

✅ Under Budget: £1,070 (3.0%)

Key Savings:
- 60% reduction in agency usage vs. budget
- 32% reduction in overtime vs. budget

Savings Attribution:
- ML forecasting: £640 (better planning)
- Shift optimization: £430 (efficient assignment)

Year-to-Date Savings: £12,840 (12.6% vs. previous year)
Annualized Savings Projection: £14,500
```

---

## Hands-On Exercises

### Exercise 1: Fill a Vacant Shift (10 minutes)

**Scenario:** Bob Jones called in sick for tomorrow's day shift.

**Your Task:**
1. Navigate to "Vacancies"
2. Find tomorrow's shift for Bob
3. Review available staff
4. Assign a replacement
5. Verify WTD compliance

**Success Criteria:** Shift filled, no WTD violations, confirmation email sent

---

### Exercise 2: Approve a Leave Request (10 minutes)

**Scenario:** Alice Smith requested 2 weeks leave in January.

**Your Task:**
1. Navigate to "Leave Management"
2. Find Alice's request
3. Review impact analysis
4. Check team leave calendar
5. Approve or reject with justification

**Success Criteria:** Decision made, email sent, leave calendar updated

---

### Exercise 3: Run Weekly Optimization (15 minutes)

**Scenario:** Optimize next week's rota to reduce costs.

**Your Task:**
1. Navigate to "Optimize Rota"
2. Select next week (7 days)
3. Configure optimization goals
4. Run optimization
5. Review recommendations
6. Apply changes if savings ≥5%

**Success Criteria:** Optimization completed, savings calculated, changes applied

---

## Quick Reference Card

**Common Tasks:**

| Task | Navigation |
|------|------------|
| View Today's Rota | Dashboard → "Today's Shifts" |
| Fill Vacant Shift | Menu → Vacancies → Click shift → Assign Staff |
| Approve Leave | Menu → Leave Management → Click request → Approve |
| Check WTD Compliance | Menu → Reports → WTD Report |
| Run Optimization | Menu → Schedule → Optimize Rota |
| View Cost Analysis | Menu → Reports → Cost Analysis |
| Export Rota | View Rota → Export button → Excel |

**Keyboard Shortcuts:**

- `Alt+D` = Dashboard
- `Alt+R` = View Rota
- `Alt+L` = Leave Management
- `Alt+V` = Vacancies
- `Alt+P` = Print Current View
- `Ctrl+F` = Search/Filter

**Support:**

- **Technical Issues:** support@yourcompany.com
- **Training Questions:** hr@yourcompany.com
- **Emergency (System Down):** +44 XXXX XXXXXX

---

## Assessment & Certification

**Post-Training Quiz (15 minutes):**

1. What are the 3 main optimization goals?
2. When should you use agency staff vs. overtime?
3. How do you check WTD compliance before assigning a shift?
4. What is the leave target for December 31?
5. How far in advance can demand forecasts predict staffing needs?

**Pass Criteria:** 4/5 correct answers

**Certification:** Certificate of Completion issued upon passing

---

**Training Document Version:** 1.0  
**Last Updated:** 21 December 2025  
**Next Review:** March 2026  
**Trainer Contact:** training@yourcompany.com
