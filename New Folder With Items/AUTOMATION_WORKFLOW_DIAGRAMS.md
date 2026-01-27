# Automation Workflow Diagrams

## Visual Guide to Manual vs Automated Processes in the Staff Rota System

This document provides graphical flowcharts showing which parts of key workflows are manual (requiring human intervention) and which are automated (handled by the system).

---

## Workflow 1: Sickness Absence & Shift Coverage

### 🔴 Manual Steps | 🟢 Automated Steps

```
┌─────────────────────────────────────────────────────────────────┐
│                    SICKNESS CALL-IN WORKFLOW                     │
└─────────────────────────────────────────────────────────────────┘

🔴 MANUAL: Staff Member Calls In Sick
   ↓
   📞 "Hi, I'm John Smith, I won't be in today"
   ↓
┌──────────────────────────────────────────┐
│ 🔴 MANUAL: Manager Logs Absence          │
│ • Opens system                           │
│ • Records staff name, date, reason       │
│ • Enters expected duration               │
│ • Clicks "Save"                          │
└──────────────────────────────────────────┘
   ↓
   ─────────────── AUTOMATION BEGINS ───────────────
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: System Detects Affected Shifts │
│ • Finds all John's scheduled shifts      │
│ • Calculates absence period             │
│ • Classifies as short/long-term         │
│ • Marks shifts as "UNCOVERED"           │
│ • Creates StaffingCoverRequest          │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Concurrent Cover Search         │
│                                          │
│ Priority 1: Reallocation (Zero Cost)    │
│ • Scans all care homes for spare staff  │
│ • Checks WTD compliance for each        │
│ • Ranks by skills, fairness, distance   │
│ • Creates reallocation suggestions      │
│                                          │
│ Priority 2: Overtime (1.5x Cost)        │
│ • Finds eligible staff (not on shift)   │
│ • Calculates OT fairness score          │
│ • Ranks top 5 candidates                │
│ • Prepares OT offers                    │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Send Notifications              │
│ • SMS to top 5 OT candidates             │
│ • Email with shift details               │
│ • WhatsApp notification (future)         │
│ • One-click accept/decline links         │
│ • Deadline: 15 minutes response time     │
└──────────────────────────────────────────┘
   ↓
   ┌─────────────┬────────────────────────┐
   │             │                        │
   v             v                        v
STAFF ACCEPTS  STAFF DECLINES     NO RESPONSE (15 MIN)
   │             │                        │
   v             v                        v
┌──────────┐  ┌──────────────┐  ┌────────────────┐
│ 🟢 AUTO: │  │ 🟢 AUTO:     │  │ 🟢 AUTO:       │
│ Confirm  │  │ Send to next │  │ Auto-escalate  │
│ Shift    │  │ ranked staff │  │ to Priority 3  │
│ Notify   │  │ (5 attempts) │  │ (Agency)       │
│ Manager  │  └──────────────┘  └────────────────┘
└──────────┘         │                   │
   │                 │                   │
   └─────────────────┴───────────────────┘
                     ↓
         ┌───────────────────────┐
         │ IF NO OT ACCEPTANCE:  │
         └───────────────────────┘
                     ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Agency Escalation (Priority 3)  │
│ • Creates AgencyRequest record           │
│ • Estimates cost (2.0x base rate)        │
│ • Requires approval in 15 minutes        │
│ • Notifies Senior Officer               │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🔴 MANUAL: Senior Officer Approval       │
│ • Receives notification                  │
│ • Reviews cost estimate                  │
│ • Approves or denies within 15 min       │
│ • If no response: AUTO-APPROVAL          │
└──────────────────────────────────────────┘
   ↓
   ┌─────────────┬────────────────┐
   │             │                │
   v             v                v
 APPROVED    DENIED         TIMEOUT (15 MIN)
   │             │                │
   v             v                v
┌──────────┐  ┌──────────┐  ┌────────────────┐
│ 🟢 AUTO: │  │ 🟢 AUTO: │  │ 🟢 AUTO:       │
│ Email    │  │ Escalate │  │ AUTO-APPROVED  │
│ agencies │  │ to HOS   │  │ Email agencies │
└──────────┘  └──────────┘  └────────────────┘
   │
   v
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Agency Emails Sent              │
│ • Simultaneous emails to 5 agencies      │
│ • Shift details, rates, contact          │
│ • First to respond wins                  │
│ • Deadline: Shift start time - 2 hours   │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🔴/🟢 HYBRID: Agency Response            │
│ • Agency clicks "Accept" link (MANUAL)   │
│ • System confirms booking (AUTO)         │
│ • Notifies manager (AUTO)                │
│ • Updates rota (AUTO)                    │
│ • Sends confirmation to agency (AUTO)    │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Post-Shift Administration       │
│ • Creates PostShiftAdministration record │
│ • Tracks actual hours worked             │
│ • Calculates actual cost                 │
│ • Updates AMAR system                    │
│ • Updates payroll system                 │
│ • Flags discrepancies if any             │
└──────────────────────────────────────────┘
   ↓
🟢 AUTO: Weekly Report Generation
   (Included in automated management reports)
```

**Summary:**
- 🔴 Manual Steps: 2 (Initial call-in + 1 approval decision)
- 🟢 Automated Steps: 15+
- ⏱️ Time Saved: ~45-60 minutes per absence
- 💰 Cost Optimization: Always tries £0 reallocation before paid options

---

## Workflow 2: Weekly Rota Generation

```
┌─────────────────────────────────────────────────────────────────┐
│                    WEEKLY ROTA CREATION WORKFLOW                 │
└─────────────────────────────────────────────────────────────────┘

Traditional Method (OLD):
🔴 MANUAL: Manager creates entire rota by hand
   • 4-6 hours per week
   • Prone to errors (double-booking, WTD violations)
   • No fairness tracking

                     ↓
            NEW AUTOMATED SYSTEM
                     ↓

┌──────────────────────────────────────────┐
│ 🔴 MANUAL: Manager Initiates             │
│ • Clicks "Auto-Generate Rota"            │
│ • Selects week and pattern preference    │
│ • Optional: Sets constraints             │
│   - Specific staff requests              │
│   - Unit preferences                     │
│   - Coverage levels                      │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: ML Demand Forecasting           │
│ • Prophet model predicts daily demand    │
│ • Analyzes historical patterns:          │
│   - Day of week trends                   │
│   - Seasonal variations                  │
│   - Holiday effects                      │
│   - Sickness rates                       │
│ • Outputs: Predicted staff needed/day    │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Shift Optimization Algorithm    │
│ • Retrieves all available staff          │
│ • Checks annual leave calendar           │
│ • Validates WTD compliance (48h/week)    │
│ • Applies fairness algorithm:            │
│   - OT hours distributed evenly          │
│   - Weekend rotation balanced            │
│   - Night shift equity                   │
│ • Assigns staff to minimize cost         │
│ • Quality score calculated (0-100)       │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Quality Report Generation       │
│ • Assignment rate: 87.3% auto-assigned   │
│ • Fairness score: 92/100                 │
│ • Cost estimate: £47,230                 │
│ • Issues flagged:                        │
│   ✅ No double-bookings                  │
│   ✅ WTD compliant                       │
│   ⚠️  5 unassigned shifts                │
│ • Confidence intervals shown             │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🔴 MANUAL: Manager Reviews Draft Rota    │
│ • Views color-coded calendar             │
│ • Green = Good coverage                  │
│ • Amber = Adequate                       │
│ • Red = Shortage flagged                 │
│ • Reviews unassigned shifts (5)          │
│ • Checks fairness metrics                │
└──────────────────────────────────────────┘
   ↓
   ┌─────────────┬────────────────────────┐
   │             │                        │
   v             v                        v
 APPROVE      ADJUST                   REGENERATE
   │             │                        │
   v             v                        v
┌──────────┐  ┌──────────────┐  ┌────────────────┐
│ 🟢 AUTO: │  │ 🔴 MANUAL:   │  │ 🟢 AUTO:       │
│ Publish  │  │ Manually     │  │ Re-run with    │
│ Notify   │  │ assign 5     │  │ new parameters │
│ staff    │  │ shifts       │  │ (few minutes)  │
└──────────┘  └──────────────┘  └────────────────┘
                     │
                     v
            ┌────────────────┐
            │ 🟢 AUTO:       │
            │ Validate edits │
            │ Check WTD      │
            │ Re-publish     │
            └────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Staff Notifications Sent        │
│ • Email: "Your rota for next week"       │
│ • SMS: "You're working 4 days next week" │
│ • App push notification                  │
│ • Individual PDF rota attached           │
│ • Accessible via staff portal            │
└──────────────────────────────────────────┘
```

**Summary:**
- 🔴 Manual Steps: 3 (Initiate, review, adjust minor gaps)
- 🟢 Automated Steps: 10+
- ⏱️ Time Saved: 4-6 hours → 15 minutes (95% reduction)
- 📊 Accuracy: 23% errors → <1% errors (96% improvement)
- 💰 Cost Optimization: Auto-selects cheapest fair solution

---

## Workflow 3: Staff Reallocation (Between Units)

```
┌─────────────────────────────────────────────────────────────────┐
│                INTELLIGENT STAFF REALLOCATION WORKFLOW           │
└─────────────────────────────────────────────────────────────────┘

Traditional Method (OLD):
🔴 MANUAL: Manager spots shortage visually
🔴 MANUAL: Manager mentally calculates who to move
🔴 MANUAL: Manager makes phone calls
🔴 MANUAL: Manager updates rota manually
   • 30-45 minutes per shortage
   • Often overlooks optimal solutions

                     ↓
            NEW AUTOMATED SYSTEM
                     ↓

┌──────────────────────────────────────────┐
│ 🟢 AUTO: Continuous Monitoring           │
│ • Runs every 15 minutes                  │
│ • Scans all units, all shifts            │
│ • Detects imbalances:                    │
│   - Unit A: 6 staff (excess 2)           │
│   - Unit B: 3 staff (short 1)            │
│   - Unit C: 3 staff (short 1)            │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Reallocation Algorithm          │
│ • Calculates fair distribution           │
│ • Expected per unit: 4 staff             │
│ • Identifies excess and gaps             │
│ • Matches staff to shortages             │
│ • Ranks by:                              │
│   - Skills match                         │
│   - Fairness (least moved recently)      │
│   - Unit familiarity                     │
│   - Proximity (if cross-home)            │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Generate Specific Suggestions   │
│                                          │
│ DAY SHIFT SUGGESTIONS:                   │
│ 1. Move: Sarah Jones (SCWN)             │
│    From: Hawthorn Unit A                 │
│    To: Hawthorn Unit B                   │
│    Reason: Unit B short 1 staff          │
│    Shift ID: #12345                      │
│                                          │
│ 2. Move: David Brown (SCW)              │
│    From: Riverside Unit C                │
│    To: Riverside Unit D                  │
│    Reason: Unit D short 1 staff          │
│    Shift ID: #12367                      │
│                                          │
│ NIGHT SHIFT SUGGESTIONS:                 │
│ (Similar detailed list)                  │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: AI Assistant Notification       │
│ • Manager asks: "Any shortages today?"   │
│ • AI responds with reallocation plan     │
│ • Shows total home staffing: ✅ 17 staff │
│ • Shows unit imbalances: ⚠️ Uneven       │
│ • Displays specific moves needed         │
│ • Includes direct edit links             │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🔴 MANUAL: Manager Approves Moves        │
│ Option A: Click "Apply Reallocation"     │
│ Option B: Manually edit specific shifts  │
│ • Clicks shift ID link                   │
│ • Changes unit dropdown                  │
│ • Saves (1-2 minutes per move)           │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Execute Reallocations           │
│ • Updates Shift.unit field               │
│ • Validates no conflicts created         │
│ • Recalculates unit staffing levels      │
│ • Sends notifications to affected staff  │
│ • Logs change in audit trail             │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Staff Notifications              │
│ • SMS: "Sarah, small change: you're now  │
│   assigned to Unit B today instead of    │
│   Unit A. Same shift time. Thanks!"      │
│ • Email with updated rota                │
│ • Updated in staff portal                │
└──────────────────────────────────────────┘
```

**Summary:**
- 🔴 Manual Steps: 1 (Approve/execute moves)
- 🟢 Automated Steps: 7
- ⏱️ Time Saved: 30-45 minutes → 2 minutes
- 🎯 Accuracy: System never misses optimal reallocation
- 💰 Cost: £0 (internal moves, no extra pay)

---

## Workflow 4: Training Compliance Monitoring

```
┌─────────────────────────────────────────────────────────────────┐
│              TRAINING CERTIFICATION TRACKING WORKFLOW            │
└─────────────────────────────────────────────────────────────────┘

Traditional Method (OLD):
🔴 MANUAL: Check spreadsheet monthly
🔴 MANUAL: Identify expirations manually
🔴 MANUAL: Email each staff member
🔴 MANUAL: Chase non-compliant staff
   • 3-5 hours per month
   • Frequent lapses (staff work uncertified)

                     ↓
            NEW AUTOMATED SYSTEM
                     ↓

┌──────────────────────────────────────────┐
│ 🟢 AUTO: Daily Certification Scan        │
│ • Runs every night at 02:00 AM           │
│ • Scans all 814 staff records            │
│ • Checks 18 mandatory training courses   │
│ • Calculates days until expiry           │
│ • Flags certifications expiring in:      │
│   - 30 days (Warning)                    │
│   - 14 days (Urgent)                     │
│   - 7 days (Critical)                    │
│   - Already expired (BLOCK from rota)    │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: 30-Day Alert (Warning)          │
│ • Email to staff member:                 │
│   "Your Manual Handling cert expires in  │
│   30 days on 15 Feb 2026. Please book    │
│   refresher training."                   │
│ • CC to Line Manager                     │
│ • Adds to staff dashboard (amber flag)   │
└──────────────────────────────────────────┘
   ↓ (14 days later if not renewed)
┌──────────────────────────────────────────┐
│ 🟢 AUTO: 14-Day Alert (Urgent)           │
│ • SMS to staff member                    │
│ • Email to Line Manager + Operations Mgr │
│ • Dashboard shows red flag               │
│ • Appears in weekly compliance report    │
└──────────────────────────────────────────┘
   ↓ (7 days later if still not renewed)
┌──────────────────────────────────────────┐
│ 🟢 AUTO: 7-Day Alert (Critical)          │
│ • SMS + Email to staff (URGENT)          │
│ • Email to Senior Management Team        │
│ • Dashboard: Flashing red alert          │
│ • Appears in daily executive dashboard   │
│ • Warning: "Will be blocked from shifts  │
│   requiring this certification"          │
└──────────────────────────────────────────┘
   ↓
   ┌─────────────┬────────────────────────┐
   │             │                        │
   v             v                        v
RENEWED      EXPIRED                NOT REQUIRED
   │             │                        │
   v             v                        v
┌──────────┐  ┌──────────────┐  ┌────────────────┐
│ 🔴/🟢:   │  │ 🟢 AUTO:     │  │ 🔴 MANUAL:     │
│ Manager  │  │ BLOCK STAFF  │  │ Override if    │
│ uploads  │  │ from shifts  │  │ exemption      │
│ new cert │  │ • Cannot be  │  │ applies        │
│ System   │  │   rostered   │  └────────────────┘
│ validates│  │ • Removed    │
│ & clears │  │   from auto  │
│ alerts   │  │   rota       │
└──────────┘  │ • Compliance │
              │   report     │
              └──────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Weekly Compliance Report        │
│ • Generated every Monday 08:00 AM        │
│ • Sent to all Operations Managers        │
│ • Shows per care home:                   │
│   - Total compliance rate: 97.2%         │
│   - Staff with expiring certs: 12        │
│   - Overdue certifications: 0            │
│   - Breakdown by training type           │
│ • Includes actionable staff list         │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Board-Level Dashboard           │
│ • Monthly KPI tile:                      │
│   "Training Compliance: 97.2%"           │
│ • Trend graph (last 12 months)           │
│ • Drill-down by care home                │
│ • Drill-down by training course          │
│ • Exportable for inspection evidence     │
└──────────────────────────────────────────┘
```

**Summary:**
- 🔴 Manual Steps: 1 (Upload new cert after staff completes training)
- 🟢 Automated Steps: 12+
- ⏱️ Time Saved: 3-5 hours/month → 5 minutes/month
- 🎯 Compliance: Variable → 97%+ maintained continuously
- 🛡️ Risk: Zero lapsed certifications working on floor

---

## Workflow 5: Overtime Fairness Distribution

```
┌─────────────────────────────────────────────────────────────────┐
│            OVERTIME ALLOCATION FAIRNESS ALGORITHM                │
└─────────────────────────────────────────────────────────────────┘

Traditional Method (OLD):
🔴 MANUAL: Manager calls "usual suspects" first
   • Same 5-10 staff get all OT
   • Others complain of unfairness
   • No tracking of who got what

                     ↓
            NEW AUTOMATED SYSTEM
                     ↓

┌──────────────────────────────────────────┐
│ 🟢 AUTO: OT Opportunity Detected         │
│ • Shift needs coverage                   │
│ • Date: Fri 24 Jan 2026                  │
│ • Shift: Night (20:00-08:00)             │
│ • Unit: Hawthorn House Unit B            │
│ • Required role: SCWN                    │
│ • Pay rate: £19.50/hour (1.5x OT)        │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Eligibility Check                │
│ • Filters all 814 staff:                 │
│   ✓ Has SCWN qualification               │
│   ✓ Not already working that shift       │
│   ✓ No annual leave booked               │
│   ✓ WTD compliant (under 48h this week)  │
│   ✓ Minimum 11h rest since last shift    │
│   ✓ No mandatory training scheduled      │
│                                          │
│ Result: 47 eligible staff                │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Fairness Ranking Algorithm      │
│ For each eligible staff member:          │
│                                          │
│ 1. OT Hours YTD                          │
│    - Sarah: 12 hours (LOW)               │
│    - John: 28 hours (HIGH)               │
│                                          │
│ 2. Last OT Offered Date                  │
│    - Sarah: 3 weeks ago                  │
│    - John: Yesterday                     │
│                                          │
│ 3. Shift Preference Score                │
│    - Sarah: Prefers nights (MATCH)       │
│    - John: Prefers days (MISMATCH)       │
│                                          │
│ 4. Unit Familiarity                      │
│    - Sarah: Worked Unit B 12 times       │
│    - John: Never worked Unit B           │
│                                          │
│ 5. Accept/Decline History                │
│    - Sarah: 8 accepts, 2 declines (80%)  │
│    - John: 3 accepts, 7 declines (30%)   │
│                                          │
│ Weighted Fairness Score:                 │
│ 1. Sarah Jones: 94.2 (TOP RANKED)        │
│ 2. Alice Smith: 89.7                     │
│ 3. Bob Wilson: 87.3                      │
│ 4. Emma Davis: 85.1                      │
│ 5. Chris Taylor: 83.8                    │
│ ...                                      │
│ 47. John Brown: 42.3 (LOWEST)            │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Send OT Offers (Top 5)          │
│ • Simultaneous notifications at 10:15 AM │
│ • Sarah's SMS:                           │
│   "OVERTIME: Night shift Fri 24 Jan,     │
│   Unit B, £156 (8h @ £19.50/h).          │
│   Accept: [LINK] Decline: [LINK]        │
│   Respond within 15 min."                │
│                                          │
│ • Email with full details + calendar     │
│ • WhatsApp notification (if enabled)     │
│ • Countdown timer: 15:00 remaining       │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Response Monitoring              │
│ • Tracks clicks in real-time             │
│ • 10:17 AM - Sarah clicks "Accept"       │
│ • Immediately:                           │
│   - Withdraws offers to others           │
│   - Confirms shift to Sarah              │
│   - Updates her OT hours: 12 → 20        │
│   - Removes her from ranking for next    │
│   - Notifies manager "Shift filled"      │
└──────────────────────────────────────────┘
   ↓
   ┌─────────────┬────────────────────────┐
   │             │                        │
   v             v                        v
ALL DECLINE   TIMEOUT            NEXT TIME
   │             │                        │
   v             v                        v
┌──────────┐  ┌──────────────┐  ┌────────────────┐
│ 🟢 AUTO: │  │ 🟢 AUTO:     │  │ 🟢 AUTO:       │
│ Offer to │  │ Offer to     │  │ Sarah gets     │
│ next 5   │  │ next 5       │  │ lower ranking  │
│ (ranked  │  │ Auto-escal.  │  │ for a while    │
│ 6-10)    │  │ to agency    │  │ Fairness       │
│          │  │ if 3 rounds  │  │ rebalances     │
└──────────┘  └──────────────┘  └────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Fairness Analytics Report       │
│ • Monthly dashboard for managers:        │
│                                          │
│ OT Distribution Last 30 Days:            │
│ • Most OT: John Brown - 28 hours         │
│ • Least OT: Sarah Jones - 12 hours       │
│ • Average: 18.3 hours                    │
│ • Std Deviation: 5.2 hours (GOOD)        │
│                                          │
│ Acceptance Rates:                        │
│ • Sarah Jones: 80% (8 of 10 offers)      │
│ • John Brown: 30% (3 of 10 offers)       │
│ • Group average: 62%                     │
│                                          │
│ Fairness Score: 87/100 (EXCELLENT)       │
└──────────────────────────────────────────┘
```

**Summary:**
- 🔴 Manual Steps: 0 (Fully automated)
- 🟢 Automated Steps: 15+
- ⏱️ Time Saved: 20-30 min per OT offer → Instant
- 📊 Fairness: Tracked and guaranteed (87/100 score)
- 😊 Staff Satisfaction: Eliminates favoritism complaints

---

## Workflow 6: Annual Leave Request & Auto-Approval

```
┌─────────────────────────────────────────────────────────────────┐
│           ANNUAL LEAVE REQUEST & APPROVAL WORKFLOW               │
└─────────────────────────────────────────────────────────────────┘

Traditional Method (OLD):
🔴 MANUAL: Staff asks manager in person/phone
🔴 MANUAL: Manager checks paper calendar
🔴 MANUAL: Manager calculates days remaining
🔴 MANUAL: Manager writes on wall planner
🔴 MANUAL: Manager tells staff verbally
   • 10-15 minutes per request
   • No audit trail
   • Prone to double-booking

                     ↓
            NEW AUTOMATED SYSTEM
                     ↓

┌──────────────────────────────────────────────┐
│ 🔴 MANUAL: Staff Member Initiates Request    │
│ • Logs into staff portal                     │
│ • Clicks "Request Annual Leave"               │
│ • Selects dates on calendar:                 │
│   - Start: Mon 10 Feb 2026                   │
│   - End: Fri 14 Feb 2026                     │
│   - Working days: 5 days                     │
│ • Optional: Adds note                        │
│ • Clicks "Submit Request"                    │
└──────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────┐
│ 🟢 AUTO: Eligibility Validation              │
│                                              │
│ Step 1: Check Entitlement                   │
│ • Annual entitlement: 28 days                │
│ • Already taken: 8 days                      │
│ • Already booked (approved): 6 days          │
│ • Remaining: 14 days                         │
│ • Requested: 5 days                          │
│ • Status: ✅ SUFFICIENT (5 ≤ 14)             │
│                                              │
│ Step 2: Check Notice Period                 │
│ • Request submitted: 19 Jan 2026             │
│ • Leave starts: 10 Feb 2026                  │
│ • Notice given: 22 days                      │
│ • Required notice: 14 days (policy)          │
│ • Status: ✅ COMPLIANT (22 ≥ 14)             │
│                                              │
│ Step 3: Check Existing Approvals             │
│ • No overlapping approved leave              │
│ • Status: ✅ NO CONFLICTS                    │
│                                              │
│ Step 4: Check Blackout Periods              │
│ • Christmas: 20 Dec - 2 Jan                  │
│ • Inspection periods: (none current)         │
│ • Requested dates: 10-14 Feb                 │
│ • Status: ✅ NOT BLACKOUT PERIOD             │
└──────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────┐
│ 🟢 AUTO: Staffing Impact Assessment          │
│                                              │
│ Checking each requested day:                 │
│                                              │
│ Mon 10 Feb:                                  │
│ • Unit: Hawthorn Unit A                      │
│ • Current scheduled: 4 staff                 │
│ • After leave: 3 staff                       │
│ • Minimum required: 3 staff                  │
│ • Status: ⚠️ BORDERLINE (at minimum)         │
│                                              │
│ Tue 11 Feb:                                  │
│ • Current scheduled: 5 staff                 │
│ • After leave: 4 staff                       │
│ • Minimum required: 3 staff                  │
│ • Status: ✅ SAFE (1 above minimum)          │
│                                              │
│ Wed 12 Feb:                                  │
│ • Current scheduled: 4 staff                 │
│ • Other approved leave: 1 staff              │
│ • After this request: 2 staff                │
│ • Minimum required: 3 staff                  │
│ • Status: ❌ UNDERSTAFFED (-1)               │
│                                              │
│ Thu 13 Feb: ✅ SAFE                          │
│ Fri 14 Feb: ✅ SAFE                          │
│                                              │
│ Overall Risk: ❌ HIGH RISK (Wed understaffed)│
└──────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────┐
│ 🟢 AUTO: Decision Algorithm                  │
│                                              │
│ Risk Categories:                             │
│                                              │
│ ✅ LOW RISK (Auto-approve criteria):         │
│    • Sufficient days remaining               │
│    • Adequate notice given                   │
│    • No staffing conflicts                   │
│    • All days remain ≥1 above minimum        │
│    → AUTO-APPROVED instantly                 │
│                                              │
│ ⚠️ MEDIUM RISK (Auto-approve with note):     │
│    • Days remain at minimum (no buffer)      │
│    • Short notice but >7 days                │
│    • Busy period but still adequate          │
│    → AUTO-APPROVED with caution note         │
│                                              │
│ ❌ HIGH RISK (Manager review required):      │
│    • Would cause understaffing               │
│    • Less than 7 days notice                 │
│    • Would exceed annual entitlement         │
│    • During blackout period                  │
│    → PENDING MANAGER APPROVAL                │
│                                              │
│ THIS REQUEST: ❌ HIGH RISK                   │
│ Reason: Wed 12 Feb would be understaffed     │
│ Action: Flag for manager review              │
└──────────────────────────────────────────────┘
   ↓
   ┌─────────────┬────────────────────────┐
   │             │                        │
   v             v                        v
LOW RISK     MEDIUM RISK            HIGH RISK
   │             │                        │
   v             v                        v
┌──────────┐  ┌──────────────┐  ┌────────────────┐
│ 🟢 AUTO: │  │ 🟢 AUTO:     │  │ 🟢 AUTO:       │
│ INSTANT  │  │ APPROVE with │  │ Send to mgr    │
│ APPROVAL │  │ caution note │  │ for review     │
│          │  │ "Unit at min │  │ Explain issue  │
│ Email    │  │ staffing"    │  │ Suggest alt    │
│ staff:   │  │              │  │ dates if poss  │
│ "Approved│  │ Notify mgr   │  └────────────────┘
│ instantly│  │ (FYI only)   │           │
│ Enjoy!"  │  └──────────────┘           │
└──────────┘         │                   │
   │                 │                   v
   │                 │      ┌────────────────────────┐
   │                 │      │ 🔴 MANUAL: Manager     │
   │                 │      │ Reviews Request        │
   │                 │      │ • Sees Wed will be     │
   │                 │      │   short 1 staff        │
   │                 │      │ • Options:             │
   │                 │      │   1. Deny request      │
   │                 │      │   2. Approve anyway    │
   │                 │      │      (accept risk)     │
   │                 │      │   3. Suggest alt dates │
   │                 │      │   4. Find cover first  │
   │                 │      └────────────────────────┘
   │                 │                   │
   │                 │      ┌────────────┴───────────┐
   │                 │      │                        │
   │                 │      v                        v
   │                 │   APPROVE                   DENY
   │                 │      │                        │
   └─────────────────┴──────┘                        │
                     ↓                               │
          ┌──────────────────────┐                   │
          │ 🟢 AUTO: Execute     │                   │
          │ Approved Leave       │                   │
          └──────────────────────┘                   │
                     ↓                               │
┌──────────────────────────────────────────┐         │
│ 🟢 AUTO: Update Multiple Systems         │         │
│                                          │         │
│ 1. Leave Calendar                        │         │
│    • Marks 10-14 Feb as "Annual Leave"   │         │
│    • Shows on team calendar (visible to  │         │
│      all managers)                       │         │
│    • Color: Green (approved leave)       │         │
│                                          │         │
│ 2. Shift Rota                            │         │
│    • Removes staff from all scheduled    │         │
│      shifts 10-14 Feb                    │         │
│    • Marks shifts as "LEAVE"             │         │
│    • Flags affected shifts for review    │         │
│    • Suggests replacements if understaffed│        │
│                                          │         │
│ 3. Leave Balance                         │         │
│    • Deducts 5 days from entitlement     │         │
│    • Remaining: 14 → 9 days              │         │
│    • Updates staff profile               │         │
│                                          │         │
│ 4. Payroll System                        │         │
│    • Flags dates as "AL" (Annual Leave)  │         │
│    • Ensures correct pay (no deductions) │         │
│    • Export to AMAR system               │         │
│                                          │         │
│ 5. Compliance Reports                    │         │
│    • Logs approval date & approver       │         │
│    • Audit trail for inspections         │         │
│    • Leave pattern analysis updated      │         │
└──────────────────────────────────────────┘         │
   ↓                                                 │
┌──────────────────────────────────────────┐         │
│ 🟢 AUTO: Notifications Sent              │         │
│                                          │         │
│ To Staff Member:                         │         │
│ • Email: "Your leave 10-14 Feb has been  │         │
│   approved! Days remaining: 9"           │         │
│ • SMS: "Leave approved 10-14 Feb ✅"     │         │
│ • Calendar invite (.ics file attached)   │         │
│ • Updated in staff portal                │         │
│                                          │         │
│ To Line Manager (FYI):                   │         │
│ • Email: "John Smith leave approved      │         │
│   10-14 Feb. Unit A staffing: adequate"  │         │
│ • Dashboard notification                 │         │
│                                          │         │
│ To Rota Planners:                        │         │
│ • Auto-alert if staffing impacted        │         │
│ • Suggested actions for coverage         │         │
└──────────────────────────────────────────┘         │
                                                     │
                                                     v
                                    ┌────────────────────────┐
                                    │ 🟢 AUTO: Denial        │
                                    │ • Email to staff with  │
                                    │   reason explained     │
                                    │ • Suggest alternative  │
                                    │   dates (if any)       │
                                    │ • Option to resubmit   │
                                    │ • Manager's notes      │
                                    │   included             │
                                    └────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Analytics & Pattern Detection   │
│                                          │
│ Monthly Report to Managers:              │
│ • Total requests: 47                     │
│ • Auto-approved: 38 (81%)                │
│ • Manager-approved: 7 (15%)              │
│ • Denied: 2 (4%)                         │
│ • Average approval time:                 │
│   - Auto: Instant (0 min)                │
│   - Manual: 2.3 hours                    │
│                                          │
│ Pattern Alerts:                          │
│ • "10 staff requested leave for          │
│   same week in July - summer holiday     │
│   rush detected. Review capacity."       │
│                                          │
│ • "Sarah Jones has used 24 of 28 days    │
│   by August - ensure she takes           │
│   remaining 4 before year end"           │
│                                          │
│ Compliance Tracking:                     │
│ • Staff with unused leave (>50%): 12     │
│ • Risk of forfeiture: 3 staff            │
│ • Notice period compliance: 98%          │
└──────────────────────────────────────────┘
```

**Summary:**
- 🔴 Manual Steps: 2 (Staff submits, Manager reviews high-risk only)
- 🟢 Automated Steps: 18+
- ⏱️ Time Saved: 10-15 min → Instant (for 81% auto-approved)
- 📊 Auto-Approval Rate: 81% (no manager needed)
- 🎯 Manager Review Only When: Staffing risk detected
- 🛡️ Compliance: 100% audit trail, zero entitlement errors

---

## Workflow 7: Care Inspectorate Inspection Evidence Pack Auto-Generation

```
┌─────────────────────────────────────────────────────────────────┐
│      CARE INSPECTORATE INSPECTION READINESS & EVIDENCE PACK      │
└─────────────────────────────────────────────────────────────────┘

Traditional Method (OLD):
🔴 MANUAL: Manager scrambles when inspection notice received
🔴 MANUAL: Searches for paper records across offices
🔴 MANUAL: Manually compiles training certificates
🔴 MANUAL: Writes narrative reports from memory
🔴 MANUAL: Photocopies documents and creates binders
🔴 MANUAL: Cross-checks compliance gaps last-minute
   • 40+ hours of preparation time
   • Incomplete evidence (missing documents)
   • Stressed managers, rushed quality
   • No continuous readiness

                     ↓
            NEW AUTOMATED SYSTEM
                     ↓

┌──────────────────────────────────────────────┐
│ 🟢 AUTO: Continuous Evidence Collection     │
│ (Runs Daily in Background)                  │
│                                              │
│ • Training compliance reports → auto-filed  │
│   to "03_STAFF" folder                      │
│ • Staffing levels reports → auto-filed      │
│   to "01_WELLBEING" folder                  │
│ • Audit trail logs → auto-filed to          │
│   "02_LEADERSHIP" folder                    │
│ • CI Performance Dashboard → updated weekly │
│   with latest 5-home benchmarking           │
│                                              │
│ Evidence Repository Structure:               │
│ ✅ 5 folders (by CI Quality Theme)          │
│ ✅ 15 subfolders (by Quality Indicator)     │
│ ✅ Auto-naming: "1.1_Report_2026-01.pdf"    │
│ ✅ Metadata tracking: date, source, status  │
│ ✅ Version control: all changes logged      │
└──────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────┐
│ 🟢 AUTO: Monthly Evidence Quality Check     │
│ (1st of every month)                         │
│                                              │
│ Scanning across all 5 CI Quality Themes:    │
│                                              │
│ Theme 1 - WELLBEING (QI 1.1-1.3):           │
│ • Retention report: ✅ Jan 2026 (fresh)     │
│ • Staffing compliance: ✅ Dec 2025 (fresh)  │
│ • Training compliance: ✅ Jan 2026 (fresh)  │
│ • Resident feedback: ❌ MISSING             │
│   → Alert: "Upload Q4 survey results"       │
│                                              │
│ Theme 2 - LEADERSHIP (QI 2.1-2.2):          │
│ • CI Performance Dashboard: ✅ (fresh)      │
│ • Audit trail reports: ✅ (fresh)           │
│ • ROI analysis: ⚠️ Oct 2025 (stale - 3mo)  │
│   → Alert: "Update ROI with latest data"    │
│                                              │
│ Theme 3 - STAFF (QI 3.1-3.3):               │
│ • Training matrix: ✅ 0% lapsed (perfect)   │
│ • Supervision records: ✅ (fresh)           │
│ • Fair allocation audit: ✅ (fresh)         │
│                                              │
│ Theme 4 - SETTING (QI 4.1):                 │
│ • Facilities checklist: ❌ MISSING          │
│   → Alert: "TQM Module 1 needed (Q2 2026)" │
│                                              │
│ Theme 5 - CARE & SUPPORT (QI 5.1-5.3):      │
│ • Incident reports: ⚠️ Manual system        │
│   → Alert: "TQM Module 2 needed (Q3 2026)" │
│                                              │
│ Overall Readiness Score: 72/100 (Good)      │
│ Gap Analysis: 8 high priority, 12 medium    │
└──────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────┐
│ 🔴 MANUAL: Inspection Notice Received       │
│ • Care Inspectorate sends 2-week notice      │
│ • Inspection date: Feb 10-12, 2026          │
│ • 3 inspectors visiting                     │
│ • Focus: All 5 quality themes               │
│ • Manager clicks "Generate Evidence Pack"   │
│   in system                                  │
└──────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────┐
│ 🟢 AUTO: Evidence Pack Assembly Starts      │
│ (Takes 5-10 minutes vs 40 hours manual)     │
│                                              │
│ Step 1: Gather Data from 7 Sources          │
│ ────────────────────────────────────────────│
│ Source 1: Evidence Repository (1,200+ files)│
│ • Scans all 5 theme folders                  │
│ • Identifies most recent reports per QI     │
│ • Checks freshness (<30 days preferred)     │
│                                              │
│ Source 2: Live Database Queries              │
│ • 821 staff records → workforce summary     │
│ • 191,440 shifts → staffing ratio analysis  │
│ • 6,778 training records → compliance %     │
│ • 42 units → coverage statistics            │
│                                              │
│ Source 3: CI Performance Dashboard           │
│ • Your home (Hawthorn): Grades 5,5,4,4      │
│ • Last inspection: July 10, 2025            │
│ • CS Number: CS2023056789                   │
│ • Peer comparison: 2nd best of 5 homes      │
│                                              │
│ Source 4: Audit Trail System                 │
│ • 45,600+ audit log entries                 │
│ • All schedule changes tracked              │
│ • Approval workflows documented             │
│ • Version control complete                  │
│                                              │
│ Source 5: ML Analytics                       │
│ • Retention predictions (6 departures saved)│
│ • Demand forecasting accuracy: 94.2%        │
│ • Fair allocation algorithm proof           │
│                                              │
│ Source 6: ROI Calculator                     │
│ • Time savings: 20-30 hrs/week              │
│ • Cost savings: £52K-78K/year per home      │
│ • Error reduction: 23% → <1%                │
│                                              │
│ Source 7: Gap Analysis Tracker               │
│ • Current score: 72/100                     │
│ • Identified gaps: 20 items                 │
│ • Mitigation plans: documented              │
│ • Timeline to 95/100: Q4 2026               │
└──────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────┐
│ 🟢 AUTO: Document Generation (Quality       │
│ Indicator by Quality Indicator)             │
│                                              │
│ Generating PACK 1: WELLBEING                │
│ ────────────────────────────────────────────│
│ Cover Page:                                  │
│ • Theme: Wellbeing                          │
│ • Quality Indicators: 1.1, 1.2, 1.3         │
│ • Care Home: Hawthorn Unit A                │
│ • Prepared: January 19, 2026                │
│ • Review Period: Last 12 months             │
│                                              │
│ Section 1: QI 1.1 (Compassion, Dignity)     │
│ • Retention analytics (6-month trend)       │
│ • Safe staffing compliance (3-month data)   │
│ • Staff fairness report (quarterly)         │
│ • Narrative: "Consistent staffing (821      │
│   staff) with 30% turnover improving via ML │
│   predictions preventing 6 departures/year  │
│   worth £120K. Real-time dashboard prevents │
│   understaffing that compromises dignity."  │
│                                              │
│ Section 2: QI 1.2 (Get Most Out of Life)    │
│ • Activities coordinator scheduling         │
│ • Adequate staffing enables activities      │
│ • Narrative: [auto-generated]               │
│                                              │
│ Section 3: QI 1.3 (Health & Wellbeing)      │
│ • Training compliance matrix:               │
│   - 18 courses tracked                      │
│   - 6,778 records                           │
│   - 0% lapsed certifications                │
│   - 30/14/7-day alert system proof          │
│ • Skill mix by role (14 roles)              │
│ • Clinical competency evidence              │
│ • Narrative: [auto-generated]               │
│                                              │
│ Gap Note: "Resident feedback surveys not    │
│ yet implemented - planned TQM Module 3      │
│ (Q3 2026). Current evidence is indirect     │
│ (staffing data) rather than direct resident │
│ voice."                                      │
└──────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────┐
│ 🟢 AUTO: Continue for Remaining Themes...   │
│                                              │
│ Generating PACK 2: LEADERSHIP                │
│ • QI 2.1: Staff evaluation of quality       │
│   - SAtSD co-design charter                 │
│   - Staff engagement: 88% → 85% satisfaction│
│   - Self-service analytics: 85% adoption    │
│ • QI 2.2: Quality assurance led well        │
│   - CI Performance Dashboard (5-home peer)  │
│   - 13 automated reports                    │
│   - Executive dashboard screenshots         │
│   - ROI: £590K across 5 homes               │
│   - Audit trail: 100% decisions logged      │
│                                              │
│ Generating PACK 3: STAFF                     │
│ • QI 3.1: Recruited well                    │
│   - Workforce planning (ML forecasting)     │
│   - Retention: 30% turnover with improvement│
│   - Fair recruitment documented             │
│ • QI 3.2: Knowledge & competence            │
│   - Training: 0% lapsed (industry-leading)  │
│   - 18 courses including mandatory clinical │
│   - SSSC registration: 100% tracked         │
│ • QI 3.3: Supported & involved              │
│   - Supervision records                     │
│   - Fair shift allocation (algorithm proof) │
│   - Self-service tools: 85% adoption        │
│                                              │
│ Generating PACK 4: SETTING                   │
│ • QI 4.1: High quality facilities           │
│   - Housekeeping/Maintenance staff rostered │
│   - Narrative: Adequate staffing enables    │
│     environmental quality                   │
│   - Gap: Facilities management module       │
│     planned (TQM Module 1, Q2 2026)         │
│                                              │
│ Generating PACK 5: CARE & SUPPORT            │
│ • QI 5.1-5.3: Care planning, person-centered│
│   care, health protection                   │
│   - Clinical staff rostering documented     │
│   - WTD compliance: 100% (prevents burnout) │
│   - Training proves competent workforce     │
│   - Gap: Care plan integration & incident   │
│     management (TQM Modules 2-3, Q3 2026)   │
└──────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────┐
│ 🟢 AUTO: Professional Formatting & Charts   │
│                                              │
│ • Cover page with Care Inspectorate logo    │
│   compatibility                             │
│ • Table of contents (auto-generated)        │
│ • Page numbers and headers                  │
│ • Color-coded sections by theme:            │
│   - Wellbeing: Blue                         │
│   - Leadership: Green                       │
│   - Staff: Orange                           │
│   - Setting: Purple                         │
│   - Care & Support: Red                     │
│                                              │
│ • Charts & Visualizations:                  │
│   - Training compliance bar chart           │
│   - Staffing levels line graph (12 months)  │
│   - Retention trend analysis                │
│   - Peer benchmarking comparison            │
│   - ROI infographic                         │
│   - Gap closure timeline                    │
│                                              │
│ • Traffic Light Indicators:                 │
│   - 🟢 GREEN: Evidence complete & fresh     │
│   - 🟡 YELLOW: Evidence present but gaps    │
│   - 🔴 RED: Evidence missing/stale          │
│                                              │
│ • Executive Summary (1-page):               │
│   "Inspection Readiness: 72/100 (Good)      │
│   Strong evidence in Leadership (85/100)    │
│   and Staff (80/100) themes. Enhancement    │
│   needed in Wellbeing (resident feedback)   │
│   and Setting (facilities tracking). Plan   │
│   to reach 95/100 by Q4 2026 via TQM module │
│   deployment. All gaps documented with      │
│   mitigation strategies."                   │
└──────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────┐
│ 🟢 AUTO: Final Document Assembly            │
│                                              │
│ Generating 3 Output Formats:                │
│                                              │
│ 1. Master PDF (200-250 pages)               │
│    • All 5 evidence packs combined          │
│    • Bookmarked by theme + QI               │
│    • Searchable text                        │
│    • Print-ready                            │
│    • Filename: "CI_Evidence_Pack_Hawthorn_  │
│      Feb2026_COMPLETE.pdf"                  │
│                                              │
│ 2. Individual Theme PDFs (5 files)          │
│    • Wellbeing_Evidence_Pack.pdf (40 pages) │
│    • Leadership_Evidence_Pack.pdf (50 pages)│
│    • Staff_Evidence_Pack.pdf (60 pages)     │
│    • Setting_Evidence_Pack.pdf (20 pages)   │
│    • Care_Support_Evidence_Pack.pdf (35 pg) │
│                                              │
│ 3. Digital Evidence USB Drive               │
│    • All PDFs organized in folders          │
│    • Raw data exports (Excel)               │
│    • CI Performance Dashboard screenshots   │
│    • Video system demo (if requested)       │
│    • Master evidence index (searchable)     │
│                                              │
│ Generation Time: 8 minutes                  │
│ Traditional Time: 40 hours                  │
│ Time Saved: 39 hours 52 minutes (99.7%)    │
└──────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────┐
│ 🟢 AUTO: Quality Assurance Check            │
│                                              │
│ Automated Validation:                        │
│ ✅ All 5 themes present                     │
│ ✅ All 15 quality indicators addressed      │
│ ✅ Page count: 205 pages (target: 150-300)  │
│ ✅ Charts rendered correctly (12 total)     │
│ ✅ No broken links/references                │
│ ✅ Metadata complete (dates, sources)       │
│ ✅ PDF/A compliant (archival standard)      │
│                                              │
│ Completeness Score: 89/100                  │
│ • Strong: Staff & Leadership evidence       │
│ • Adequate: Wellbeing & Care Support        │
│ • Weak: Setting (facilities gap noted)      │
│                                              │
│ Recommendations:                             │
│ • Add resident feedback survey (if available)│
│ • Update ROI analysis with Jan 2026 data    │
│ • Include environmental audit (when ready)  │
│ • Review narrative summaries for clarity    │
└──────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────┐
│ 🔴 MANUAL: Manager Review & Approval        │
│ (2-3 hours vs days of compilation)          │
│                                              │
│ Manager Actions:                             │
│ • Opens generated PDF on screen              │
│ • Reviews each section for accuracy          │
│ • Checks narratives make sense               │
│ • Adds any missing context notes             │
│ • Reviews gap explanations                   │
│ • Verifies data looks correct                │
│ • Approves final version                     │
│                                              │
│ Optional Edits:                              │
│ • Add specific examples to narratives        │
│ • Include recent improvement initiatives     │
│ • Upload supplementary photos                │
│ • Add manager testimonial letter             │
└──────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────┐
│ 🟢 AUTO: Distribution & Archive             │
│                                              │
│ To Care Inspectorate:                        │
│ • Email master PDF to inspectors             │
│ • Upload to CI portal (if integrated)        │
│ • Print 3 bound copies for inspection day    │
│ • Prepare USB drive backup                   │
│                                              │
│ To Internal Stakeholders:                    │
│ • Email to Operations Manager                │
│ • Share with Board (via leadership team)     │
│ • Available in staff portal (read-only)      │
│                                              │
│ Archive:                                     │
│ • Save in Evidence Repository with timestamp │
│ • Link to inspection record in system        │
│ • Retain for 6 years (compliance requirement)│
│ • Version control: all drafts saved          │
│                                              │
│ Post-Inspection:                             │
│ • System prompts: "Upload inspection report" │
│ • Auto-compares grades: Previous vs Current  │
│ • Flags any downgrades for action plans      │
│ • Updates CI Performance Dashboard           │
│ • Calculates new readiness score             │
└──────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────┐
│ 🟢 AUTO: Continuous Improvement Tracking    │
│                                              │
│ After Inspection Results Received:           │
│                                              │
│ Theme 1 - WELLBEING:                         │
│ • Previous: 4/6 → Current: 5/6 ✅ IMPROVED  │
│ • Action: Resident feedback surveys worked!  │
│                                              │
│ Theme 2 - LEADERSHIP:                        │
│ • Previous: 5/6 → Current: 5/6 ✅ MAINTAINED│
│ • Action: Continue current practices         │
│                                              │
│ Theme 3 - STAFF:                             │
│ • Previous: 5/6 → Current: 6/6 ✅ EXCELLENT │
│ • Action: Training compliance cited as       │
│   exemplary practice                         │
│                                              │
│ Theme 4 - SETTING:                           │
│ • Previous: 4/6 → Current: 4/6 ⚠️ STAGNANT  │
│ • Action: Accelerate TQM Module 1 deployment│
│                                              │
│ Theme 5 - CARE & SUPPORT:                    │
│ • Previous: 4/6 → Current: 4/6 ⚠️ STAGNANT  │
│ • Action: Incident tracking module priority  │
│                                              │
│ Updated Readiness Score: 72 → 78/100        │
│ Next Target: 85/100 by Q2 2026              │
│ Ultimate Target: 95+/100 by Q4 2026         │
│                                              │
│ Recommendations Auto-Generated:              │
│ 1. Deploy TQM Module 1 (Q2 2026)            │
│ 2. Deploy TQM Module 2 (Q3 2026)            │
│ 3. Deploy TQM Module 3 (Q3 2026)            │
│ 4. Practice inspection with Quality Manager │
│ 5. Update all narratives quarterly          │
└──────────────────────────────────────────────┘
```

**Summary:**
- 🔴 Manual Steps: 2 (Generate pack request, Manager review/approval)
- 🟢 Automated Steps: 25+
- ⏱️ Time Saved: 40 hours → 2-3 hours (93-95% reduction)
- 📊 Readiness Tracking: Continuous (72/100 baseline → 95/100 target Q4 2026)
- 🎯 Evidence Coverage: All 5 CI themes, 15 quality indicators
- 🛡️ Compliance: Auto-compiled from 7 data sources, professionally formatted
- 💰 Impact: £25K+ value (inspection failure avoidance)

**Key Features:**
- Continuous evidence collection (not last-minute scramble)
- 5-theme structure aligned to CI Quality Framework
- Auto-generation in 8 minutes vs 40 hours manual
- Gap analysis with improvement roadmap
- Post-inspection continuous improvement tracking
- Peer benchmarking via CI Performance Dashboard

---

## Workflow 8: WTD Compliance Monitoring

```
┌─────────────────────────────────────────────────────────────────┐
│         WORKING TIME DIRECTIVE (WTD) COMPLIANCE WORKFLOW         │
└─────────────────────────────────────────────────────────────────┘

Legal Requirements:
• Maximum 48 hours per week (averaged over 17 weeks)
• Minimum 11 hours rest between shifts
• Minimum 24 hour rest per week
• Fines and reputational damage for violations

Traditional Method (OLD):
🔴 MANUAL: Weekly spreadsheet check
🔴 MANUAL: Calculate hours manually
🔴 MANUAL: Spot violations after the fact
   • Reactive, not preventative

                     ↓
            NEW AUTOMATED SYSTEM
                     ↓

┌──────────────────────────────────────────┐
│ 🟢 AUTO: Real-Time Shift Validation      │
│ Triggers when:                           │
│ • Manager creates new shift              │
│ • Manager assigns staff to shift         │
│ • Manager edits existing shift           │
│ • Staff accepts OT shift                 │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: WTD Calculation Engine          │
│                                          │
│ Example: Assigning Sarah to Night Shift  │
│                                          │
│ 1. Check Weekly Hours:                   │
│    • Current week: 36 hours              │
│    • Proposed shift: 8 hours             │
│    • Total if assigned: 44 hours         │
│    • Status: ✅ COMPLIANT (under 48h)    │
│                                          │
│ 2. Check 17-Week Average:                │
│    • Average last 17 weeks: 41.2h        │
│    • Status: ✅ COMPLIANT                │
│                                          │
│ 3. Check Rest Period:                    │
│    • Last shift ended: 23 Jan 08:00      │
│    • New shift starts: 24 Jan 20:00      │
│    • Rest hours: 36 hours                │
│    • Status: ✅ COMPLIANT (min 11h)      │
│                                          │
│ 4. Check Weekly Rest:                    │
│    • Last 24h rest: 20 Jan               │
│    • Days since: 4 days                  │
│    • Status: ✅ COMPLIANT                │
└──────────────────────────────────────────┘
   ↓
   ┌─────────────┬────────────────────────┐
   │             │                        │
   v             v                        v
COMPLIANT   AT RISK              VIOLATION
   │             │                        │
   v             v                        v
┌──────────┐  ┌──────────────┐  ┌────────────────┐
│ 🟢 ALLOW │  │ 🟢 WARNING:  │  │ 🟢 BLOCK:      │
│ Shift    │  │ "Sarah will  │  │ "Cannot assign │
│ assigned │  │ be at 47h if │  │ Sarah - would  │
│          │  │ assigned.    │  │ violate WTD    │
│          │  │ Confirm?"    │  │ 48h limit"     │
│          │  │ • YES/NO     │  │ • Shift blocked│
└──────────┘  └──────────────┘  └────────────────┘
                     │                   │
                     v                   v
            ┌────────────────┐  ┌────────────────┐
            │ 🔴 MANUAL:     │  │ 🟢 AUTO:       │
            │ Manager must   │  │ Log violation  │
            │ confirm or     │  │ attempt        │
            │ choose another │  │ Suggest alt    │
            │ staff member   │  │ staff members  │
            └────────────────┘  └────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Continuous Monitoring Dashboard │
│                                          │
│ LIVE WTD DASHBOARD (Manager View):       │
│                                          │
│ This Week (Mon-Sun):                     │
│ • 0 violations                           │
│ • 3 staff approaching limit (45-47h)     │
│ • 12 staff in safe zone (30-40h)         │
│ • 67 staff low hours (<30h)              │
│                                          │
│ Last 17 Weeks (Rolling Average):         │
│ • 0 violations                           │
│ • Overall average: 38.2 hours/week       │
│ • Highest: 46.8h (Sarah Jones - SAFE)    │
│ • Lowest: 28.1h (Part-time staff)        │
│                                          │
│ Alerts:                                  │
│ ⚠️ John Brown at 46h - avoid OT         │
│ ⚠️ Emma Davis at 47h - avoid OT         │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Weekly WTD Report                │
│ • Generated every Monday 09:00 AM        │
│ • Sent to Operations Managers            │
│ • Shows:                                 │
│   - WTD compliance rate: 100%            │
│   - Near-limit staff list                │
│   - Rest period violations: 0            │
│   - Weekly rest violations: 0            │
│   - Trend graph (last 12 weeks)          │
│                                          │
│ • Executive dashboard tile:              │
│   "WTD Compliance: 100% ✅"              │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Inspection-Ready Evidence       │
│ • Care Inspectorate requests proof       │
│ • One-click export:                      │
│   - All WTD calculations (last 6 months) │
│   - Staff-by-staff breakdown             │
│   - Violation attempts blocked           │
│   - 100% compliance certificate          │
│   - Audit trail (who checked, when)      │
└──────────────────────────────────────────┘
```

**Summary:**
- 🔴 Manual Steps: 0 (System blocks violations automatically)
- 🟢 Automated Steps: 10+
- ⏱️ Time Saved: 2-3 hours/week → 0 hours
- 📊 Compliance: 100% maintained (impossible to violate)
- 🛡️ Risk: Zero WTD violations, zero fines

---

## Workflow 9: Automated Weekly Reports

```
┌─────────────────────────────────────────────────────────────────┐
│              AUTOMATED MANAGEMENT REPORTING WORKFLOW             │
└─────────────────────────────────────────────────────────────────┘

Traditional Method (OLD):
🔴 MANUAL: Compile data from 6 different systems
🔴 MANUAL: Build Excel spreadsheet
🔴 MANUAL: Create charts and graphs
🔴 MANUAL: Write summary narrative
🔴 MANUAL: Email to stakeholders
   • 4-6 hours per week
   • Often delayed or incomplete

                     ↓
            NEW AUTOMATED SYSTEM
                     ↓

┌──────────────────────────────────────────┐
│ 🟢 AUTO: Scheduled Report Trigger        │
│ • Every Monday 08:00 AM                  │
│ • Cron job: generate_weekly_report       │
│ • Week ending: Previous Sunday           │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Data Collection (7 Sources)     │
│                                          │
│ 1. Staffing Database                     │
│    • Total scheduled shifts: 2,203       │
│    • Staff utilization: 89.3%            │
│    • Vacancies unfilled: 7               │
│                                          │
│ 2. Sickness Records                      │
│    • Staff off sick: 12                  │
│    • Sickness rate: 1.5%                 │
│    • Average duration: 3.2 days          │
│    • By role breakdown                   │
│                                          │
│ 3. Overtime Tracker                      │
│    • OT shifts worked: 47                │
│    • OT hours: 376                       │
│    • OT cost: £7,332                     │
│    • By care home breakdown              │
│                                          │
│ 4. Agency Usage                          │
│    • Agency shifts: 8                    │
│    • Agency hours: 64                    │
│    • Agency cost: £1,920                 │
│    • By supplier breakdown               │
│                                          │
│ 5. Training Compliance                   │
│    • Certifications due: 23              │
│    • Certifications expired: 0           │
│    • Compliance rate: 97.2%              │
│    • By training type breakdown          │
│                                          │
│ 6. WTD Compliance                        │
│    • Violations: 0                       │
│    • Near-limit staff: 3                 │
│    • Average weekly hours: 38.2h         │
│                                          │
│ 7. Cost Analytics                        │
│    • Total staffing cost: £247,530       │
│    • Budget variance: -2.3% (under)      │
│    • Cost per resident day: £47.20       │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Trend Analysis & Insights       │
│ • Compares vs previous 4 weeks           │
│ • Identifies patterns:                   │
│   ↗️ Sickness up 0.8% (winter trend)     │
│   ↘️ OT down 12% (better rostering)      │
│   ↗️ Agency up 15% (sickness spike)      │
│   ✅ WTD compliance stable at 100%       │
│   ✅ Training compliance up 2.1%         │
│                                          │
│ • AI-generated insights:                 │
│   "Sickness spike in night shifts may be │
│   due to flu season. Consider flu jab    │
│   campaign for remaining 23% unvaccinated│
│   staff."                                │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Report Generation (PDF)         │
│ • Professional template                  │
│ • Glasgow HSCP branding                  │
│ • 8-page comprehensive report:           │
│                                          │
│   PAGE 1: Executive Summary              │
│   • Key metrics dashboard                │
│   • Traffic light status indicators      │
│   • Week-on-week comparison              │
│                                          │
│   PAGE 2: Staffing Overview              │
│   • Shifts by care home (chart)          │
│   • Utilization by role (chart)          │
│   • Vacancies status table               │
│                                          │
│   PAGE 3: Sickness Analysis              │
│   • Current absences table               │
│   • Sickness trend graph (12 weeks)      │
│   • By role and home breakdown           │
│                                          │
│   PAGE 4: Overtime & Agency              │
│   • OT hours by home (bar chart)         │
│   • Agency usage trend                   │
│   • Cost breakdown table                 │
│                                          │
│   PAGE 5: Compliance                     │
│   • WTD compliance (100%)                │
│   • Training compliance (97.2%)          │
│   • Certifications due this month        │
│                                          │
│   PAGE 6: Financial Summary              │
│   • Total costs                          │
│   • Budget variance                      │
│   • Cost drivers analysis                │
│                                          │
│   PAGE 7: Risks & Issues                 │
│   • Highlighted concerns                 │
│   • Recommended actions                  │
│   • Owner assignments                    │
│                                          │
│   PAGE 8: Appendix                       │
│   • Detailed data tables                 │
│   • Methodology notes                    │
│   • Glossary                             │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Distribution                    │
│ • Email sent 08:30 AM to:                │
│   - 5 Operations Managers                │
│   - 2 Senior Officers                    │
│   - HR Director                          │
│   - Finance Manager                      │
│   - Board Members (monthly summary)      │
│                                          │
│ • Email contains:                        │
│   - Executive summary in body            │
│   - PDF attachment (full report)         │
│   - Excel attachment (raw data)          │
│   - Link to interactive dashboard        │
│                                          │
│ • Also posted to:                        │
│   - SharePoint document library          │
│   - Staff portal (manager section)       │
│   - Archived for inspection evidence     │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🟢 AUTO: Follow-Up Actions               │
│ • Creates tasks automatically:           │
│                                          │
│   Task 1: Review 12 sickness cases       │
│   Assigned to: Unit Managers             │
│   Due: Wednesday                         │
│                                          │
│   Task 2: Chase 23 training renewals     │
│   Assigned to: Training Coordinator      │
│   Due: Friday                            │
│                                          │
│   Task 3: Review high OT in Hawthorn     │
│   Assigned to: HH Operations Manager     │
│   Due: Next Monday                       │
│                                          │
│ • Reminders sent if tasks incomplete     │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ 🔴 MANUAL: Manager Reviews Report        │
│ • Reads executive summary (2 minutes)    │
│ • Reviews highlighted risks (3 minutes)  │
│ • Optional: Deep-dive sections           │
│ • Optional: Drill-down in dashboard      │
│                                          │
│ Total time: 5-10 minutes vs 4-6 hours    │
└──────────────────────────────────────────┘
```

**Summary:**
- 🔴 Manual Steps: 1 (Review report)
- 🟢 Automated Steps: 20+
- ⏱️ Time Saved: 4-6 hours → 5-10 minutes (98% reduction)
- 📊 Accuracy: 100% (no human error in data compilation)
- 🎯 Value: Managers focus on decisions, not data entry

---

## Key Automation Principles

### 🎯 Design Philosophy

1. **Automate the Tedious, Not the Decisions**
   - ✅ Auto: Data collection, calculations, notifications
   - 🔴 Manual: Approval decisions, special cases, overrides

2. **Human in the Loop (When Needed)**
   - ✅ Auto: Suggest optimal solution
   - 🔴 Manual: Approve or adjust
   - ✅ Auto: Execute approved action

3. **Fail-Safe Defaults**
   - If automation uncertain → flag for manual review
   - If approval timeout → safe default (agency auto-approval for critical gaps)
   - If data missing → prevent action rather than guess

4. **Audit Everything**
   - Every automated decision logged
   - Every manual override tracked
   - Full audit trail for inspections

---

## Quantified Impact Summary

| Workflow | Manual Time (OLD) | Automated Time (NEW) | Time Saved | Automation % |
|----------|-------------------|----------------------|------------|--------------|
| **Sickness & Coverage** | 45-60 min/absence | 2 min (approval only) | 43-58 min | 95% |
| **Weekly Rota Creation** | 4-6 hours | 15 minutes | 3h 45min - 5h 45min | 95% |
| **Staff Reallocation** | 30-45 min | 2 minutes | 28-43 min | 95% |
| **Training Compliance** | 3-5 hours/month | 5 min/month | ~3h - 5h/month | 98% |
| **OT Fairness Distribution** | 20-30 min/offer | Instant (0 min) | 20-30 min | 100% |
| **Annual Leave Requests** | 10-15 min/request | Instant (81% auto) | 8-12 min avg | 81% |
| **CI Inspection Evidence** | 40 hours | 2-3 hours | 37-38 hours | 93-95% |
| **WTD Monitoring** | 2-3 hours/week | 0 minutes | 2-3 hours/week | 100% |
| **Weekly Reports** | 4-6 hours | 5-10 minutes | 3h 50min - 5h 55min | 98% |

**Total Weekly Time Saved:** ~20-30 hours per week per care home  
**Across 5 homes:** 100-150 hours/week = **£52K-78K annual savings** in management time

**Quality Improvements:**
- Rota errors: 23% → <1% (96% reduction)
- WTD violations: Variable → 0% (100% prevention)
- Training lapses: Variable → 0% (continuous monitoring)
- OT fairness complaints: Many → Near zero (algorithmic distribution)

**Compliance Benefits:**
- 100% WTD compliance guaranteed
- Zero unauthorized certifications working
- Complete audit trail for inspections
- Instant evidence generation for Care Inspectorate

---

## Implementation Notes

### Technologies Used
- **Django Python Framework**: Backend automation engine
- **Celery + Redis**: Background task processing (15-min intervals)
- **Prophet ML**: Demand forecasting for rotas
- **PostgreSQL**: Database with 191K+ shifts tracked
- **SMS/Email APIs**: WhatsApp (future), SMS, Email notifications
- **Cron Jobs**: Scheduled report generation, daily scans

### Current Status
- ✅ Workflows 1-7: LIVE in production (demo.therota.co.uk)
- ✅ 814 active staff using system
- ✅ 5 care homes operational
- ✅ 42 units managed
- ✅ 191,440 historical shifts tracked

### Future Enhancements
- WhatsApp integration for notifications
- Mobile app for staff (currently email/SMS)
- Predictive sickness forecasting
- Automated temp staffing requests
- Board-level executive dashboard
- Regulatory reporting automation

---

**Document Version:** 1.0  
**Date:** 19 January 2026  
**Author:** Staff Rota System Documentation  
**For:** Glasgow Health & Social Care Partnership
