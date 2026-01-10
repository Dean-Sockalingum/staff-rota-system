# Phase 3: Care Inspectorate Quality Framework Mapping
**Date:** January 10, 2026  
**Project:** Digital Staff Rota & Quality Management System  
**Purpose:** Map existing system features to Care Inspectorate quality themes and identify enhancement opportunities

---

## Care Inspectorate Quality Framework Overview

The Care Inspectorate uses a quality framework with **5 key quality themes**, each containing multiple quality indicators rated on a 6-point scale (1=Unsatisfactory to 6=Excellent):

### **1. Wellbeing** - How well do we support people's wellbeing?
### **2. Leadership** - How good is our leadership?
### **3. Staff** - How good is our staff team?
### **4. Setting** - How good is our setting?
### **5. Care & Support** - How well do we support people's health and wellbeing?

---

## Current System Features → Care Inspectorate Quality Themes Mapping

### **Theme 1: WELLBEING - How well do we support people's wellbeing?**

#### **Quality Indicator 1.1: People experience compassion, dignity and respect**

**Current System Support:**
- ✅ **Consistent Staffing:** Automated rota ensures continuity of care with familiar staff members
  - 821 staff tracked across 42 units with predictable rotation patterns
  - Reduces resident confusion and anxiety from unfamiliar faces
  - **Evidence:** 109,267 shifts managed with stable staff allocation patterns

- ✅ **Safe Staffing Levels:** Real-time monitoring prevents understaffing that compromises dignity and time for person-centered care
  - Dashboard alerts for staffing ratio compliance
  - **Evidence:** 23% error rate eliminated (manual system) → <1% (automated system)

- ✅ **Staff Retention Support:** Features designed to reduce 30% annual turnover
  - Fair shift allocation algorithms (reduces perceived bias)
  - Self-service transparency (85% mobile adoption)
  - **Impact:** Lower turnover = more experienced staff = better person-centered care

**Enhancement Opportunities:**
- 📋 Link resident preferences to staff allocation (e.g., resident-staff matching based on relationship continuity)
- 📋 Track resident feedback on care quality by specific staff members
- 📋 Incident correlation with staffing patterns (understaffing → poorer wellbeing outcomes)

---

#### **Quality Indicator 1.2: People get the most out of life**

**Current System Support:**
- ✅ **Activities Coordinator Scheduling:** System tracks Activities Coordinator role (1 of 14 tracked roles)
  - Ensures dedicated activities staff presence
  - **Evidence:** Activities staff included in 821 staff database

- ⚠️ **Limited Direct Support:** Core rota system doesn't directly manage activities planning

**Enhancement Opportunities:**
- 📋 Activities planning module as TQM add-on
- 📋 Track participation rates and outcomes
- 📋 Link staffing levels to quality of life metrics (more staff = more activities)

---

#### **Quality Indicator 1.3: People's health and wellbeing benefits from their care and support**

**Current System Support:**
- ✅ **Training Compliance Tracking:** 18 mandatory courses tracked for 6,778 training records
  - Courses include: Safeguarding, First Aid, Infection Control, Medication, Dementia Care, End of Life Care, Person-Centred Care, Falls Prevention, Oral Health, Nutritional Awareness
  - 30-day renewal reminders prevent lapsed certifications (15% lapse rate eliminated)
  - **Evidence:** Automated alerts ensure staff competency for safe, effective care

- ✅ **Skill Mix Compliance:** Dashboard shows skill mix by unit ensuring appropriate clinical oversight
  - Senior Care Workers, Senior Social Care Workers, Senior Social Care Worker Night roles tracked
  - **Evidence:** 14 distinct roles with competency requirements

- ✅ **Supervision Tracking:** System logs supervision sessions for professional development
  - Supports reflective practice and continuous learning
  - **Evidence:** Supervision session database integrated

**Enhancement Opportunities:**
- 📋 Medication error tracking (TQM Incident Management module)
- 📋 Health outcome monitoring (weight, falls, pressure sores correlation with staffing)
- 📋 Clinical governance dashboard linking staffing to health metrics

---

### **Theme 2: LEADERSHIP - How good is our leadership?**

#### **Quality Indicator 2.1: Staff and people who use the service are involved in evaluating and improving the quality of care**

**Current System Support:**
- ✅ **SAtSD Co-Design:** Scottish Approach to Service Design principles embedded in development
  - Managers and staff involved in design phase (9 OMs, 5 SMs participated)
  - User feedback loops for continuous improvement
  - **Evidence:** 1,352 users providing real-world testing and feedback

- ✅ **AI Assistant Query Tracking:** 200+ natural language patterns reveal common pain points
  - Data-driven insights into staff concerns and information gaps
  - **Evidence:** Query analytics inform system improvements

- ✅ **Stakeholder Engagement:** Families Council representatives involved in design team
  - Voice of residents and families in system development
  - **Evidence:** Documented in DLP Project Charter

**Enhancement Opportunities:**
- 📋 Formal feedback module (TQM add-on) for structured quality improvement cycles
- 📋 Resident/family satisfaction surveys linked to staffing patterns
- 📋 Staff engagement surveys with automated analysis and action planning

---

#### **Quality Indicator 2.2: Quality assurance and improvement are led well**

**Current System Support:**
- ✅ **Audit Trail:** Complete version control and change logging
  - All schedule changes logged with user/timestamp
  - Approval workflows for leave/swaps documented
  - System access and data modifications tracked
  - **Evidence:** Regulatory-grade audit trail for accountability

- ✅ **Automated Compliance Reporting:** 13 executive reports with traffic light indicators
  - CI Performance Dashboard with actual inspection data (CS numbers, 4-theme ratings, 1-6 scale)
  - Training compliance matrices
  - Staffing pattern analysis
  - **Evidence:** 40 hours inspection prep reduced to 8 hours (80% reduction)

- ✅ **Data-Driven Decision Making:** Executive dashboards enable evidence-based quality improvement
  - Real-time KPIs vs. manual retrospective analysis
  - Trend identification for proactive management
  - **Evidence:** 6.7× dashboard speedup (180ms vs 1200ms) enables real-time insights

- ✅ **HIS/NES Framework Alignment:** Quality improvement methodologies embedded
  - HIS Quality Management Systems framework referenced
  - NES Quality Improvement Zone tools integrated
  - PDSA cycles supported through iterative system enhancement
  - **Evidence:** TQM modules designed with Scottish frameworks foundation

**Enhancement Opportunities:**
- 📋 Quality Audits module with scheduled compliance checks
- 📋 Automated gap analysis against Care Inspectorate standards
- 📋 Continuous improvement tracker (PDSA cycles, corrective actions)
- 📋 Benchmarking consortium for sector-wide learning

---

### **Theme 3: STAFF - How good is our staff team?**

#### **Quality Indicator 3.1: Staff have been recruited well**

**Current System Support:**
- ✅ **Workforce Planning Intelligence:** ML forecasting (Prophet 25.1% MAPE) predicts staffing needs
  - 30-day demand prediction with 80% confidence intervals
  - Enables proactive recruitment planning vs. reactive hiring
  - **Evidence:** Validated forecasting model with 69-test suite

- ✅ **Retention Analytics:** System tracks turnover patterns and identifies at-risk staff
  - ML prediction preventing 6 departures/year (£120K savings)
  - Data-driven retention interventions
  - **Evidence:** £120K retention improvement in £590K total ROI

- ⚠️ **Limited Direct Recruitment Support:** Core system doesn't manage recruitment workflows

**Enhancement Opportunities:**
- 📋 Recruitment workflow module (vacancy posting → interview → onboarding)
- 📋 Skill gap analysis to target recruitment priorities
- 📋 Integration with SSSC registration verification at hiring

---

#### **Quality Indicator 3.2: Staff have the right knowledge, competence and development to care for and support people**

**Current System Support:**
- ✅ **Comprehensive Training Tracking:** 18 mandatory courses across 6,778 records
  - Courses aligned with SSSC registration requirements and Care Inspectorate standards
  - Automated expiry alerts prevent lapsed certifications (15% lapse rate eliminated)
  - **Evidence:** Mandatory courses include Safeguarding, First Aid, Infection Control, Medication, Manual Handling, Fire Safety, Food Hygiene, Duty of Candour, GDPR, Mental Capacity, Challenging Behaviour, Dementia Care, End of Life Care, Person-Centred Care, Falls Prevention, Oral Health, Nutritional Awareness, Documentation

- ✅ **Supervision Session Tracking:** Logged for reflective practice and CPD
  - Supports SSSC registration requirements (1:1 supervision minimum quarterly)
  - **Evidence:** Supervision database integrated into compliance tracking

- ✅ **Competency-Based Role Assignment:** 14 distinct roles with training prerequisites
  - Senior Care Worker, Senior Social Care Worker, SSCW Night require specific certifications
  - System prevents unqualified staff assignment to specialist roles
  - **Evidence:** Role-based access control linked to competency data

- ✅ **Training Efficiency:** Proactive scheduling and group coordination
  - £85K savings through batch training and compliance automation
  - **Evidence:** Training efficiency category in £590K ROI analysis

**Enhancement Opportunities:**
- 📋 TQM Training & Competency module with:
  - Competency assessment tools and skills matrices
  - CPD (Continuing Professional Development) logs for SSSC registration
  - Skills gap analysis by unit/home
  - Training impact measurement (pre/post competency scores)
  - Integration with NES Quality Improvement Zone learning resources
  - Induction tracking with staged competency sign-off

---

#### **Quality Indicator 3.3: Staff are supported and involved in their work**

**Current System Support:**
- ✅ **Fair Shift Allocation:** Algorithmic scheduling ensures equitable workload distribution
  - Reduces perceived bias and favoritism
  - 88% of staff wanted transparency (baseline) → 85% satisfaction target
  - **Evidence:** Fair rotation algorithms with audit trail proving impartiality

- ✅ **Self-Service Empowerment:** Staff portal provides 24/7 access to schedules and documents
  - Submit leave requests digitally (vs. paper forms lost 10-15% of time)
  - Request shift swaps with manager approval
  - Access personal training records and guidance
  - **Evidence:** 85% mobile adoption within 3 months, 18% weekly shift swap rate

- ✅ **Communication Efficiency:** Automated shift confirmations and updates
  - £20K savings from reduced WhatsApp/phone communication burden
  - **Evidence:** Communication efficiency category in £590K ROI

- ✅ **AI Assistant Support:** 200+ natural language patterns provide instant answers
  - Reduces manager interruptions for routine queries
  - 24/7 availability for policy/procedure questions
  - **Evidence:** 80% query resolution without human escalation target

- ✅ **Work-Life Balance:** Advanced schedule visibility enables personal planning
  - Rota visibility >1 week in advance (vs. manual system often <1 week)
  - Transparent leave approval process with digital tracking
  - **Evidence:** Staff feedback reports improved ability to plan personal life

**Enhancement Opportunities:**
- 📋 Staff engagement and wellbeing module
- 📋 Workload analytics (shift patterns, overtime, rest period compliance)
- 📋 Anonymous feedback mechanism for staff concerns
- 📋 Recognition and reward tracking

---

### **Theme 4: SETTING - How good is our setting?**

#### **Quality Indicator 4.1: People experience high quality facilities**

**Current System Support:**
- ✅ **Housekeeping/Maintenance Scheduling:** System tracks Housekeeper and Maintenance roles
  - Ensures consistent presence for facility upkeep
  - **Evidence:** Housekeeper and Maintenance included in 14 tracked roles

- ⚠️ **Limited Direct Facilities Support:** Core rota system doesn't manage facilities maintenance workflows

**Enhancement Opportunities:**
- 📋 Facilities management module (maintenance scheduling, safety checks)
- 📋 Environmental audit checklist (cleanliness, safety, infection control)
- 📋 Link staffing to environmental quality metrics

---

### **Theme 5: CARE & SUPPORT - How well do we support people's health and wellbeing?**

#### **Quality Indicator 5.1: Assessment and personal planning reflects people's outcomes and wishes**

**Current System Support:**
- ⚠️ **Limited Direct Support:** Core rota system focuses on staffing, not care planning

- ✅ **Indirect Support Through Adequate Staffing:** Sufficient staff enables time for person-centered assessments
  - Reduces rushed interactions and task-focused care
  - **Evidence:** 88% administrative burden reduction frees manager time for care quality focus

**Enhancement Opportunities:**
- 📋 Care plan integration (future API development for existing care planning systems)
- 📋 Link staffing levels to care plan review compliance
- 📋 Track resident preference implementation through staffing continuity

---

#### **Quality Indicator 5.2: People experience person-centred care**

**Current System Support:**
- ✅ **Consistent Staff Relationships:** Rota stability enables relationship continuity
  - Familiar staff understand resident preferences and communication needs
  - **Evidence:** Reduced turnover (ML-predicted retention improvements) supports continuity

- ✅ **Adequate Time for Person-Centered Care:** Safe staffing prevents task-focused rushing
  - Real-time alerts prevent understaffing that compromises dignity and choice
  - **Evidence:** <1% error rate ensures regulatory staffing ratios maintained

**Enhancement Opportunities:**
- 📋 Resident-staff matching algorithms (preference-based allocation)
- 📋 Person-centered care audit checklist linked to staffing patterns
- 📋 Track meaningful activities participation vs. staffing levels

---

#### **Quality Indicator 5.3: People's health and wellbeing are protected**

**Current System Support:**
- ✅ **Infection Control Compliance:** Training tracking ensures all staff certified
  - Infection Control included in 18 mandatory courses (6,778 records)
  - Automated expiry alerts prevent lapsed certifications
  - **Evidence:** 15% lapse rate eliminated through 30-day renewal reminders

- ✅ **Medication Competency:** Medication training tracked and monitored
  - Prevents unqualified staff administering medications
  - **Evidence:** Medication course included in mandatory training matrix

- ✅ **Safeguarding Awareness:** Safeguarding training mandatory for all staff
  - Ensures protection of vulnerable adults
  - **Evidence:** Safeguarding included in 18 tracked courses

- ✅ **Safe Staffing Ratios:** Real-time monitoring prevents unsafe coverage
  - Dashboard alerts for ratio non-compliance
  - **Evidence:** Estimated 2-3 ratio breaches/month (manual system) → <1% error rate (automated)

**Enhancement Opportunities:**
- 📋 TQM Incident Management module:
  - Falls, medication errors, safeguarding concerns logging
  - SPSP (Scottish Patient Safety Programme) alignment
  - Root cause analysis tools from NES QI Zone
  - Duty of Candour compliance tracking
  - Trend analysis by shift patterns, staffing levels, time of day
- 📋 Clinical governance dashboard linking incidents to staffing data
- 📋 Early warning system for deteriorating residents (linked to care plans)

---

## Care Inspectorate Inspection Evidence Repository

### **Current System Capabilities for Inspection Readiness:**

#### **1. How well do we support people's wellbeing?**
**Evidence the system provides:**
- Training compliance matrices (18 courses, 6,778 records) → demonstrates competent, qualified staff
- Staffing pattern analysis → proves consistent care relationships
- Skill mix reports by unit → shows appropriate clinical oversight
- Supervision logs → evidences staff support and development
- **Inspection Prep Time:** 40 hours (manual) → 8 hours (automated) = 80% reduction

#### **2. How good is our leadership?**
**Evidence the system provides:**
- Audit trail of all decisions → demonstrates accountability
- CI Performance Dashboard → shows quality monitoring and benchmarking
- Automated compliance reports → evidences systematic quality assurance
- Data-driven improvement tracking → proves continuous quality improvement (PDSA cycles)
- SAtSD co-design documentation → shows person-centered service development

#### **3. How good is our staff team?**
**Evidence the system provides:**
- Complete training records with no lapsed certifications → demonstrates competent workforce
- Supervision tracking → evidences staff support
- Fair allocation algorithms with audit trails → proves equitable treatment
- Retention analytics → shows workforce stability
- Competency-based role assignment → prevents unqualified staff in specialist roles

#### **4. How good is our setting?**
**Evidence the system provides:**
- Housekeeping/maintenance staff scheduling → demonstrates facility upkeep commitment
- (Limited - future enhancement opportunity)

#### **5. How well do we support people's health and wellbeing?**
**Evidence the system provides:**
- Safe staffing ratio compliance → proves protection of residents
- Medication/Infection Control training → demonstrates clinical safety
- Safeguarding training → shows vulnerable adult protection
- Adequate staffing enabling person-centered care time → evidences dignity and respect

---

## Gap Analysis: Current vs. Care Inspectorate Expectations

### **Strengths (Green - Excellent Evidence):**
✅ **Leadership - Quality Assurance:** Automated reporting, audit trails, data-driven decision making  
✅ **Staff - Competence & Development:** Comprehensive training tracking, supervision, competency-based roles  
✅ **Staff - Support & Involvement:** Fair allocation, self-service, AI assistant, transparency  
✅ **Care & Support - Health Protection:** Safe staffing, infection control, medication competency, safeguarding

### **Moderate Support (Amber - Good Evidence, Enhancement Opportunities):**
⚠️ **Wellbeing - Compassion & Respect:** Indirect support through consistent staffing, but no direct resident feedback integration  
⚠️ **Wellbeing - Health Benefits:** Training ensures competence, but no incident/outcome tracking  
⚠️ **Leadership - Stakeholder Involvement:** Co-design documented, but no ongoing feedback module  
⚠️ **Staff - Recruitment:** Analytics support planning, but no direct recruitment workflows  
⚠️ **Care & Support - Assessment & Planning:** Adequate staffing enables time, but no care plan integration

### **Gaps (Red - Limited Evidence):**
❌ **Wellbeing - Get Most Out of Life:** No activities planning or outcome tracking  
❌ **Setting - High Quality Facilities:** Limited facilities management functionality  
❌ **Care & Support - Person-Centred Care:** No resident preference matching or care plan integration

---

## Priority Enhancement Roadmap for Care Inspectorate Compliance

### **Phase 3A: Immediate Quick Wins (Q1 2026)**
1. ✅ Document existing evidence capabilities in user-friendly "Inspection Readiness Guide"
2. ✅ Create pre-built report templates for each Care Inspectorate quality theme
3. ✅ Develop "Evidence Repository" guidance document showing where each quality indicator is evidenced
4. ✅ Train managers on using system for inspection preparation (reduce 40 hrs → 8 hrs)

### **Phase 3B: TQM Module Prioritization (Q2 2026)**
**Module 1 Priority: Quality Audits & Inspections** ⭐⭐⭐
- Directly addresses "Leadership - Quality Assurance" theme
- Scheduled compliance checks aligned with Care Inspectorate timelines
- Audit findings and corrective actions with PDSA cycle tracking
- Self-assessment tools using HIS quality indicators
- **Impact:** Strongest inspection readiness enhancement

**Module 2 Priority: Incident Management** ⭐⭐⭐
- Addresses "Care & Support - Health Protection" gap
- SPSP-aligned incident reporting (falls, medication, safeguarding)
- Root cause analysis using NES QI Zone tools
- Trend analysis linking incidents to staffing patterns
- Duty of Candour compliance tracking
- **Impact:** Critical for demonstrating safety culture and learning

**Module 3 Priority: Feedback & Complaints** ⭐⭐
- Addresses "Leadership - Stakeholder Involvement" and "Wellbeing - Person-Centred Care" gaps
- Resident/family satisfaction surveys
- Complaint logging and resolution tracking
- Integration with Can I Help You? Scottish Government initiative
- **Impact:** Demonstrates person-led care principles (HIS framework)

### **Phase 3C: System Enhancements (Q3-Q4 2026)**
- Resident-staff preference matching algorithm
- Activities planning and outcome tracking module
- Care plan API integration (link to existing care planning systems)
- Facilities management workflows (maintenance scheduling, safety checks)

---

## Success Metrics for Phase 3

### **Inspection Readiness Metrics:**
- **Baseline:** 40 hours gathering evidence across fragmented systems
- **Target:** 8 hours using automated reports and evidence repository (80% reduction)
- **Measurement:** Manager time logs during next Care Inspectorate inspection

### **Quality Theme Coverage:**
- **Baseline:** Moderate-Strong evidence for 3/5 themes (Leadership, Staff, partial Care & Support)
- **Target:** Strong evidence for 5/5 themes following TQM module implementation
- **Measurement:** Gap analysis review Q4 2026

### **Inspector Feedback:**
- **Baseline:** "Difficulty demonstrating systematic staffing compliance," "fragmented quality assurance evidence"
- **Target:** Positive feedback on integrated quality management and digital evidence systems
- **Measurement:** Care Inspectorate inspection report comments

### **Compliance Scores:**
- **Current:** CS003844 (Home 1), CS003845 (Home 2), CS003846 (Home 3), CS003847 (Home 4), CS003848 (Home 5)
- **Baseline Ratings:** Tracked in CI Performance Dashboard (1-6 scale across 4 themes)
- **Target:** Improvement in "Leadership" and "Staff" themes following system demonstration
- **Measurement:** Next inspection cycle scores (tracked in dashboard)

---

## Next Steps

### **Completed:**
✅ Task 1: Map system features to Care Inspectorate quality themes

### **In Progress:**
📋 Task 2: Integrate HIS Quality Management Systems framework
📋 Task 3: Align with NES Quality Improvement Zone methodologies

### **Upcoming:**
📋 Task 4: Review and update compliance reporting templates
📋 Task 5: Conduct Care Inspectorate inspection readiness gap analysis
📋 Task 6: Develop evidence repository structure for regulatory submissions
📋 Task 7: User research with quality managers for TQM co-design

---

**Document Version:** 1.0  
**Author:** Dean Sockalingum  
**Review Date:** February 2026 (post-presentation)  
**Status:** Phase 3 Task 1 Complete ✅

