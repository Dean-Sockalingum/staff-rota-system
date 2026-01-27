# SOP: Additional Staffing Management

**Document ID:** SOP-004  
**Version:** 1.0  
**Effective Date:** December 2025  
**Review Date:** March 2026  
**Owner:** Finance Manager

---

## Purpose

This SOP defines procedures for managing additional staffing including overtime shifts and agency staff bookings, with emphasis on cost control and compliance tracking.

## Scope

- Overtime shift creation and management
- Agency staff booking across 8 approved agencies
- Cost tracking and reporting
- Weekly staffing reports
- Budget monitoring

## Responsibilities

| Role | Responsibility |
|------|----------------|
| **Unit Manager** | Book overtime/agency, monitor unit costs, approve shifts |
| **Finance Manager** | Review costs, analyze trends, set budgets |
| **Senior Management** | Approve agency usage, review weekly reports |
| **System Administrator** | Configure agencies, maintain rates, generate reports |

---

## Agency Companies Overview

**8 Approved Agencies:**

| Agency | Day Rate | Night Rate | Contact |
|--------|----------|------------|---------|
| ABC Healthcare | £38.00/hr | £43.00/hr | [Account details in system] |
| Care Response | £42.50/hr | £48.00/hr | [Account details in system] |
| CarePro | £37.50/hr | £42.50/hr | [Account details in system] |
| Elite Care | £36.00/hr | £41.00/hr | [Account details in system] |
| Newcross Healthcare | £39.50/hr | £44.50/hr | [Account details in system] |
| Rapid Response | £40.00/hr | £45.00/hr | [Account details in system] |
| REED Healthcare | £41.00/hr | £46.00/hr | [Account details in system] |
| Staffscanner | £40.00/hr | £45.00/hr | [Account details in system] |

**Rate Range:** £36-£42.50/hr (day) | £41-£48/hr (night)

---

## Procedure: Creating Overtime Shifts

### When to Use Overtime

**Appropriate Situations:**
- Existing staff member working extra hours
- Staff covering colleague's sick leave
- Short-notice cover (within 4 hours)
- Staff prefer overtime to agency booking
- Cost-effective alternative to agency

**When NOT to Use:**
- Staff already at maximum hours
- Staff on rest days (check working time regulations)
- Regular/predictable shortfall (use recruitment instead)
- Staff refuses (never pressure staff)

---

### Step 1: Create Overtime Shift

1. **Navigate to Additional Staffing**
   - URL: `http://127.0.0.1:8000/management/additional-staffing/`
   - Click **"Additional Staffing"** in main menu

2. **Select "Create Overtime Shift" Tab**

3. **Fill in Shift Details**
   ```
   Required Fields:
   - Staff Member: [Select from dropdown]
   - Date: [DD/MM/YYYY]
   - Unit: [Select unit]
   - Shift Type: Early (7am-3pm), Late (3pm-11pm), Night (11pm-7am)
   - Hours: [Auto-calculated based on shift type or enter custom]
   - Hourly Rate: [Staff member's rate + overtime premium]
   - Reason: [Brief explanation, e.g., "Cover for J. Smith sick leave"]
   ```

4. **Review Calculated Cost**
   - System shows: Base rate + Premium = Total cost
   - Example: £15/hr base + £5/hr premium = £20/hr × 8 hours = £160

5. **Check Staff Availability**
   - System warns if staff member:
     - Already scheduled that day
     - Exceeds 48-hour working week
     - Has annual leave booked
     - On rest day

6. **Click "Create Overtime Shift"**
   - Shift appears in rota (marked as "Overtime" in orange)
   - Staff member notified via email/SMS
   - Added to weekly staffing report
   - Cost tracked in additional staffing budget

**Expected Time:** 2-3 minutes per shift

---

## Procedure: Booking Agency Staff

### When to Use Agency

**Appropriate Situations:**
- No permanent staff available for overtime
- Specialist skills needed (e.g., mental health nurse)
- Emergency cover (within 2 hours)
- Planned absences (annual leave periods)
- Short-term vacancy cover

**Budget Consideration:**
- Agency costs 2-3x permanent staff costs
- Average shift: £320-£384 (8-hour shift)
- Monthly budget: [Set by finance manager]

---

### Step 1: Check Budget

**Before Booking:**

1. Navigate to **Additional Staffing → Budget Overview**
2. Check current month spend vs. budget
3. See remaining budget available

**Budget Status Indicators:**
- 🟢 **Green:** <70% budget used (safe to book)
- 🟡 **Yellow:** 70-90% budget used (proceed with caution)
- 🔴 **Red:** >90% budget used (requires senior approval)

---

### Step 2: Select Agency

**Cost Comparison:**

1. Click **"Agency Rates"** tab
2. View all 8 agencies with current rates
3. Sort by cost (lowest to highest)
4. Consider:
   - **Cheapest option:** Elite Care (£36/hr day, £41/hr night)
   - **Most expensive:** Care Response (£42.50/hr day, £48/hr night)
   - **Reliability:** Check agency performance ratings in system
   - **Availability:** Call agency to confirm before booking

**Recommended Approach:**
- Start with cheapest agencies
- Build relationships with 2-3 reliable agencies
- Track performance (punctuality, quality, cancellations)

---

### Step 3: Create Agency Booking

1. **Click "Book Agency Staff"**

2. **Fill in Booking Details**
   ```
   Required Fields:
   - Agency: [Select from 8 approved agencies]
   - Date: [DD/MM/YYYY]
   - Unit: [Select unit needing cover]
   - Shift Type: Early/Late/Night
   - Role Required: Care Staff / Senior Carer / Nurse
   - Number of Staff: [Usually 1, can be multiple]
   - Special Requirements: [Any specific skills/experience needed]
   - Contact Person: [Your name/number for agency to confirm]
   ```

3. **System Calculates Cost**
   ```
   Example:
   Agency: REED Healthcare
   Shift: Night (8 hours)
   Rate: £46/hr
   Total Cost: £368
   
   Budget Impact: £368 / £5,000 monthly budget = 7.4%
   ```

4. **Review and Confirm**
   - Double-check date and shift times
   - Verify budget available
   - Click **"Create Agency Booking"**

5. **System Actions**
   - Sends booking confirmation email to agency
   - Adds to rota (marked as "Agency" in blue)
   - Tracks cost against budget
   - Creates record for timesheet/invoice matching

**Expected Time:** 3-5 minutes per booking

---

### Step 4: Confirm with Agency

**Important: System creates booking record, but you must confirm with agency**

1. **Call Agency Immediately**
   - Confirm they received booking
   - Confirm they can provide staff
   - Get staff member name (if available)
   - Confirm arrival time and location

2. **Update Booking in System**
   - Click **"Edit Booking"**
   - Add agency staff member name
   - Add confirmation reference number
   - Change status to "Confirmed"

3. **If Agency Cannot Provide**
   - Cancel booking in system
   - Select next cheapest agency
   - Repeat booking process
   - Document in notes why first agency unavailable

---

## Daily Operations

### Morning Routine (Every Day)

**For Unit Managers:**

1. **Check Today's Additional Staffing** (9 AM)
   - Navigate to Additional Staffing → Today's Cover
   - See all overtime and agency shifts for today
   - Verify agency staff confirmed to arrive

2. **If Agency Staff Doesn't Show**
   - Call agency immediately
   - Mark as "No Show" in system
   - Book alternative cover urgently
   - Document for invoice dispute

3. **Track Actual Hours**
   - When agency staff arrives: Record arrival time
   - When agency staff leaves: Record departure time
   - System calculates actual cost vs. booked cost

---

### Weekly Routine

**For Unit Managers (Every Friday):**

1. **Review Week's Additional Staffing**
   - Total overtime hours used
   - Total agency shifts booked
   - Total cost for the week
   - Reasons for each booking

2. **Identify Patterns**
   - Which shifts regularly need cover?
   - Which staff frequently on overtime?
   - Which agencies most reliable?
   - Any cost-saving opportunities?

3. **Weekly Staffing Report (Auto-generated)**
   - Runs every Monday at 8 AM
   - Emailed to unit managers and finance
   - Shows previous week's data

---

## Weekly Staffing Report

### Report Contents

**Automatically Generated Every Monday:**

```
WEEKLY STAFFING REPORT
Week: 25 Nov - 1 Dec 2025

OVERTIME SUMMARY:
- Total Overtime Hours: 48 hours
- Total Overtime Cost: £960
- Busiest Unit: DEMENTIA (16 hours)
- Most Used Staff: J. Smith (12 hours)

AGENCY SUMMARY:
- Total Agency Shifts: 12 shifts
- Total Agency Cost: £4,320
- Most Used Agency: Elite Care (5 shifts)
- Busiest Unit: BLUE (4 shifts)

TOTAL ADDITIONAL STAFFING COST: £5,280
Monthly Budget Used: 35.2% (£5,280 of £15,000)

COST COMPARISON:
- Cheapest Agency: Elite Care (£36/hr)
- Most Expensive: Care Response (£42.50/hr)
- Average Agency Rate: £39.20/hr
- Potential Savings: £156 if all shifts booked with cheapest agency

RECOMMENDATIONS:
- DEMENTIA unit: Consider permanent recruitment (high overtime use)
- J. Smith approaching maximum hours (check working time compliance)
- Elite Care: Excellent reliability (5/5 shifts on time) - consider preferred supplier
```

---

### Accessing the Report

**Method 1: Email**
- Automatically sent every Monday 8 AM
- To: All unit managers, finance manager, operations director
- Subject: "Weekly Staffing Report - Week Ending [Date]"

**Method 2: System**
- Navigate to Additional Staffing → Reports
- Click "Weekly Reports"
- Select week to view
- Export to PDF or Excel

**Method 3: AI Assistant**
- Ask: "Show me last week's staffing report"
- Or: "What was our agency spend last week?"
- Or: "Which agency did we use most?"

---

## Cost Control Strategies

### Best Practices

**1. Prioritize Overtime Over Agency**
- Overtime typically 50% cheaper than agency
- Ask existing staff first before booking agency
- Offer incentives for short-notice overtime

**2. Build Relationships with Cheaper Agencies**
- Elite Care (£36/hr) vs. Care Response (£42.50/hr) = 18% saving
- On 100 shifts/month: Saves £5,200/month
- Preferred supplier agreements for guaranteed availability

**3. Plan Ahead**
- Book agency for known leave periods in advance
- Better rates for advance bookings (negotiate)
- Reduces emergency booking premium rates

**4. Track and Analyze**
- Review weekly reports religiously
- Identify patterns requiring permanent recruitment
- Challenge unnecessary bookings

**5. Set Unit Budgets**
- Each unit has monthly additional staffing budget
- Unit managers accountable for staying within budget
- Escalation required for over-budget bookings

---

### Red Flags to Watch

**High Cost Indicators:**

- Same unit repeatedly needing agency (recruitment issue?)
- Same staff member repeatedly overtime (burnout risk?)
- Regular late-notice bookings (planning issue?)
- Agency no-shows increasing (switch agencies?)
- Budget consistently exceeded (unrealistic budget or management issue?)

**Action Required:**
- Investigate root cause
- Implement corrective action
- Review with senior management
- Consider permanent recruitment

---

## Invoice Management

### Matching Timesheets to Invoices

**Monthly Process:**

1. **Agency Sends Invoice** (usually by 5th of following month)

2. **Pull System Records**
   - Additional Staffing → Agency Invoices
   - Select agency and month
   - System shows all bookings with actual hours worked

3. **Match Invoice to Records**
   - Check each shift on invoice appears in system
   - Verify hours match what was actually worked
   - Check rate matches agreed rate
   - Flag discrepancies

4. **Common Invoice Errors**
   - Charging for no-shows
   - Incorrect hourly rate
   - Rounding hours up
   - Including unauthorized shifts
   - Wrong shift dates

5. **Dispute Process**
   - Email agency with system printout showing actual hours
   - Request corrected invoice
   - Don't pay until resolved
   - Escalate to agency account manager if needed

6. **Approve for Payment**
   - Once verified, click "Approve Invoice"
   - Forwards to finance for payment
   - System records payment against budget

---

## Reporting & Analytics

### Available Reports

**1. Daily Additional Staffing Report**
- Who's covering what today
- Expected costs for today
- Real-time budget tracking

**2. Weekly Staffing Report** (Auto-generated)
- Full week breakdown
- Cost analysis
- Recommendations

**3. Monthly Cost Analysis**
- Total spend by unit
- Budget vs. actual
- Agency comparison
- Trend analysis (vs. previous months)

**4. Agency Performance Report**
- Reliability (% on-time arrivals)
- No-show rate
- Average cost
- Quality ratings (if implemented)

**5. Custom Reports**
- Date range selector
- Filter by unit, agency, shift type
- Export to Excel for further analysis

---

### Generating Reports

**Standard Reports:**

1. Navigate to **Additional Staffing → Reports**
2. Select report type
3. Choose date range
4. Apply filters (optional)
5. Click "Generate Report"
6. View on screen or export (PDF/Excel)

**Custom Reports:**

1. Use "Custom Report Builder"
2. Select data fields needed
3. Apply filters
4. Set date range
5. Generate and export

**Scheduling Reports:**

1. Click "Schedule Report"
2. Select frequency (Daily/Weekly/Monthly)
3. Choose recipients (email addresses)
4. Set delivery time
5. Reports sent automatically

---

## Common Scenarios

### Scenario 1: Emergency Short-Notice Cover

**Situation:** Staff member calls in sick at 6:30 AM, shift starts 7 AM

**Action:**

1. **Check for overtime availability** (1 minute)
   - Call/text staff who might be available
   - Offer premium rate for emergency cover

2. **If no staff available, book agency** (3 minutes)
   - Call preferred agency (Elite Care or agency with best emergency response)
   - Confirm they can provide staff within 30 minutes
   - Create booking in system (mark as "Emergency")
   - Get agency staff name and ETA

3. **Notify Unit**
   - Inform staff agency worker arriving
   - Brief agency worker on arrival
   - Log in system as emergency booking

**Time to Cover:** 5-10 minutes  
**Cost Impact:** Usually 20-30% premium for emergency bookings

---

### Scenario 2: Planned Leave Period (Christmas/Summer)

**Situation:** 5 staff on annual leave week of 23-30 December

**Action (4 Weeks in Advance):**

1. **Identify Coverage Needs**
   - Review rota for affected week
   - Calculate total shortfall (e.g., 10 shifts)
   - Determine skill mix needed

2. **Offer Overtime First**
   - Email all staff: "Overtime available Christmas week"
   - Incentive: Time-and-a-half or double time
   - Book staff who volunteer

3. **Book Agency for Remaining Shifts**
   - Contact 2-3 agencies for quotes
   - Negotiate advance booking discount
   - Book cheapest reliable option
   - Get written confirmation

4. **Create Bookings in System**
   - Enter all overtime shifts
   - Enter all agency bookings
   - Review total cost vs. budget
   - Get senior approval if over budget

**Time to Organize:** 2-3 hours  
**Cost Saving:** 10-15% by booking in advance

---

### Scenario 3: Monthly Budget Exceeded

**Situation:** It's 20th of month, already spent 95% of additional staffing budget

**Action:**

1. **Review Spending**
   - Pull monthly report
   - Identify why budget exceeded
   - Check for errors or unauthorized bookings

2. **Implement Emergency Measures**
   - Pause non-essential agency bookings
   - Prioritize overtime (cheaper)
   - Ask for volunteers for extra shifts
   - Escalate to senior management

3. **Request Budget Increase** (if justified)
   - Document reasons (e.g., unexpected sickness outbreak)
   - Show cost comparison (agency vs. unsafe staffing)
   - Get approval for temporary increase
   - Put plan in place to prevent recurrence

4. **Root Cause Analysis**
   - Why did we exceed budget?
   - Recruitment needed?
   - Budget too low?
   - Poor planning?
   - Implement corrective action

---

### Scenario 4: Agency Staff No-Show

**Situation:** Agency staff booked for night shift, doesn't arrive by 11:15 PM

**Action:**

1. **Call Agency Immediately** (11:15 PM)
   - Confirm booking reference
   - Where is the staff member?
   - Can they send replacement?
   - Get ETA or confirmation

2. **If No Replacement Available:**
   - Call alternative agencies
   - Offer emergency premium rate
   - Book fastest available
   - Call in permanent staff as last resort

3. **Document in System:**
   - Mark original booking as "No Show"
   - Add notes with timeline
   - Create dispute flag for invoice
   - Rate agency performance as "Poor"

4. **Follow Up Next Day:**
   - Email agency requesting explanation
   - Formal complaint if repeated issue
   - Request credit/refund for no-show
   - Consider removing from approved supplier list

5. **Debrief:**
   - How did we manage without them?
   - Impact on service/staff?
   - Lessons learned
   - Update contingency plan

---

## Budget Management

### Setting Budgets

**Annual Budget Calculation:**

1. **Historical Analysis**
   - Review last 12 months actual spend
   - Identify trends and patterns
   - Factor in known changes (e.g., new residents, staffing levels)

2. **Unit-Level Budgets**
   - Allocate budget per unit based on:
     - Resident numbers
     - Dependency levels
     - Historical usage
     - Expected recruitment gaps

3. **Monthly Phasing**
   - Higher budget for:
     - Summer (annual leave peak)
     - Christmas/New Year
     - Winter (sickness peak)
   - Lower budget for:
     - Spring/Autumn (typically lower sickness)

**Example Monthly Budget:**
```
Total Annual Budget: £180,000
Average Monthly: £15,000
January (high sickness): £18,000
July (high leave): £20,000
October (low): £12,000
```

---

### Monitoring Budget

**Weekly Checks:**
- Run weekly report
- Check % of monthly budget used
- Forecast month-end position
- Adjust booking patterns if needed

**Monthly Reviews:**
- Actual vs. budget
- Variance analysis (why over/under?)
- Unit-by-unit breakdown
- Identify cost-saving opportunities

**Quarterly Reviews:**
- Trend analysis
- Budget reforecast
- Agency rate negotiations
- Contract renewals

---

## Compliance & Regulations

### Working Time Regulations

**Maximum Hours:**
- 48-hour average working week (over 17-week period)
- Unless staff opts out in writing
- System warns if booking would exceed limit

**Rest Periods:**
- 11 hours daily rest
- 24 hours weekly rest (or 48 hours fortnightly)
- System blocks bookings that violate rest periods

**Record Keeping:**
- All overtime hours logged
- Available for inspection
- Retained for 2 years

---

### Care Inspectorate Requirements

**Staffing Records:**
- All agency bookings documented
- Proof of agency staff qualifications
- Induction records for agency staff
- Competency assessments

**Budget Transparency:**
- Additional staffing costs reported
- Reasons for agency usage documented
- Cost control measures in place
- Regular reviews conducted

---

## Troubleshooting

### Issue: Agency dropdown not showing options

**Solution:**
- Agency API endpoint may be down
- Check: http://127.0.0.1:8000/api/agency-companies/
- Should return JSON with 8 agencies
- If not, restart server or contact administrator

---

### Issue: Cost calculation incorrect

**Possible Causes:**
- Wrong hourly rate selected
- Shift hours miscalculated
- Rate not updated in system

**Solution:**
- Verify agency rate in system matches contract
- Check shift time calculation (auto vs. manual)
- Update agency rates if needed (admin function)

---

### Issue: Weekly report not received

**Solution:**
- Check spam/junk folder
- Verify email address in system settings
- Check cron job running: `crontab -l | grep staffing`
- Manually generate: Additional Staffing → Reports → Generate Weekly

---

### Issue: Budget shows exceeded but shouldn't

**Solution:**
- Check for duplicate bookings
- Verify all cancellations marked as cancelled
- Check date filters on report
- Contact administrator to audit budget calculations

---

## Key Performance Indicators (KPIs)

**We track:**

| Metric | Target | Frequency |
|--------|--------|-----------|
| **Agency Cost as % of Total Staffing** | <8% | Monthly |
| **Overtime Hours per FTE** | <10 hours/month | Monthly |
| **Budget Variance** | ±5% | Monthly |
| **Agency No-Show Rate** | <2% | Monthly |
| **Average Agency Cost per Shift** | <£350 | Weekly |
| **Emergency Bookings (< 4hr notice)** | <15% | Weekly |

**Red Flags:**
- Agency cost >10% of total staffing
- Same unit >20% over budget
- Emergency bookings >20%
- Agency no-shows >5%

---

## Management Commands

### Generate Weekly Report Manually

```bash
cd /Users/deansockalingum/Staff\ Rota/rotasystems
python3 manage.py generate_staffing_report --week-start 2025-12-02
```

### Send Weekly Report Email

```bash
python3 manage.py send_weekly_staffing_report
```

### Update Agency Rates

```bash
python3 manage.py update_agency_rates --agency "Elite Care" --day-rate 37.00 --night-rate 42.00
```

### Budget Analysis

```bash
python3 manage.py staffing_budget_analysis --month 12 --year 2025
```

---

## Training Requirements

**Unit Managers must complete:**
- [ ] Understanding agency contracts and rates (1 hour)
- [ ] System booking procedures (1 hour)
- [ ] Budget management (1 hour)
- [ ] Invoice verification (30 minutes)
- [ ] Compliance requirements (30 minutes)

**Competency sign-off required before booking authority granted**

---

## Related Procedures

- [SOP: Shift Management](SOP_SHIFT_MANAGEMENT.md) - Creating regular rotas
- [SOP: Staff Onboarding](SOP_STAFF_ONBOARDING.md) - Adding agency staff to system
- Financial Procedures - Invoice processing and payment

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Dec 2025 | Initial SOP creation | Finance Manager |

---

## Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **Finance Manager** | | | |
| **Operations Director** | | | |
| **HR Manager** | | | |

---

**For support with additional staffing:**
- **System Help:** AI Assistant - Ask "How do I book agency staff?"
- **Finance Queries:** finance@[organization].com
- **Agency Issues:** Contact agency directly, CC finance manager

**Back to:** [SOP Index](SYSTEM_SOP_INDEX.md)
