# Phase 3: Evidence Repository Structure for Regulatory Submissions
**Date:** January 10, 2026  
**Project:** Digital Staff Rota & Quality Management System  
**Purpose:** Structured framework for organizing, indexing, and presenting inspection evidence to Care Inspectorate and other regulatory bodies

---

## Executive Summary

**Repository Purpose:**
Centralized, systematically organized collection of evidence demonstrating compliance with Care Inspectorate quality themes, Health Improvement Scotland standards, and SSSC registration requirements. Designed to reduce inspection preparation time from 40 hours to 4-5 hours while ensuring comprehensive, accessible evidence.

**Key Features:**
- **5-Theme Structure:** Evidence organized by Care Inspectorate quality themes
- **Quality Indicator Index:** Direct mapping to CI 1.1-5.3 indicators
- **Automated Population:** System-generated reports auto-filed with version control
- **Inspection Readiness Pack:** Pre-assembled evidence bundles by theme
- **Evidence Traceability:** Metadata tracking (date, source, reviewer, status)
- **Role-Based Access:** Managers access relevant evidence, leadership sees all

**Success Metrics:**
- ✅ Inspection prep time: 40 hrs → 4-5 hrs (88-90% reduction)
- ✅ Evidence completeness: 100% quality indicators covered
- ✅ Evidence freshness: <30 days for all quantitative data
- ✅ Manager confidence: 90%+ comfort level presenting evidence
- ✅ Retrieval speed: <5 minutes to locate specific evidence item

---

## Repository Structure Overview

### **Primary Organization: 5-Folder Structure by Care Inspectorate Theme**

```
Evidence_Repository/
│
├── 01_WELLBEING/
│   ├── 1.1_Compassion_Dignity_Respect/
│   ├── 1.2_Get_Most_Out_Of_Life/
│   └── 1.3_Health_Wellbeing_Benefits/
│
├── 02_LEADERSHIP/
│   ├── 2.1_Staff_People_Evaluate_Quality/
│   └── 2.2_Quality_Assurance_Led_Well/
│
├── 03_STAFF/
│   ├── 3.1_Recruited_Well/
│   ├── 3.2_Right_Knowledge_Competence/
│   └── 3.3_Supported_Involved/
│
├── 04_SETTING/
│   └── 4.1_High_Quality_Facilities/
│
├── 05_CARE_SUPPORT/
│   ├── 5.1_Assessment_Personal_Planning/
│   ├── 5.2_Person_Centred_Care/
│   └── 5.3_Health_Wellbeing_Protected/
│
├── INSPECTION_READINESS_PACKS/
│   ├── Wellbeing_Evidence_Pack.pdf
│   ├── Leadership_Evidence_Pack.pdf
│   ├── Staff_Evidence_Pack.pdf
│   ├── Setting_Evidence_Pack.pdf
│   └── Care_Support_Evidence_Pack.pdf
│
├── AUTOMATED_REPORTS/
│   ├── Weekly_Management_Reports/
│   ├── Monthly_Executive_Summaries/
│   ├── Quarterly_CI_Performance_Reviews/
│   └── Annual_Quality_Improvement_Reviews/
│
├── AUDIT_TRAIL/
│   ├── System_Access_Logs/
│   ├── Schedule_Change_History/
│   ├── Approval_Workflow_Records/
│   └── Data_Integrity_Audits/
│
└── MASTER_INDEX/
    ├── Evidence_Index_Master.xlsx
    ├── Quality_Indicator_Mapping.pdf
    ├── Evidence_Freshness_Dashboard.pdf
    └── Gap_Analysis_Tracker.xlsx
```

---

## Detailed Folder Specifications

### **FOLDER 1: WELLBEING - How well do we support people's wellbeing?**

#### **Subfolder 1.1: Compassion, Dignity & Respect**

**Evidence Types:**
- **Staffing Continuity Reports:**
  - Monthly retention analytics (turnover rates, ML predictions)
  - Staff consistency by unit (same staff ratios per resident)
  - Continuity of care evidence (familiar faces supporting relationships)
  - File naming: `1.1_Retention_Analytics_YYYY-MM.pdf`

- **Safe Staffing Compliance Reports:**
  - Real-time staffing level dashboards
  - Ratio compliance trends (actual vs. required)
  - Understaffing alert response records
  - File naming: `1.1_Safe_Staffing_Compliance_YYYY-MM.pdf`

- **Staff Fairness & Support Evidence:**
  - Fair shift allocation audit trails
  - Staff engagement survey results (satisfaction with fairness)
  - Self-service portal usage analytics (transparency metrics)
  - File naming: `1.1_Staff_Fairness_YYYY-QQ.pdf`

- **Resident/Family Feedback:** *(Future - TQM Feedback module Q3 2026)*
  - Satisfaction surveys (compassion, dignity, respect questions)
  - Complaint/compliment analysis
  - Resident voice in quality improvement
  - File naming: `1.1_Resident_Feedback_YYYY-QQ.pdf`

**Evidence Index Entry Example:**
| Evidence Item | Quality Indicator | File Path | Date Range | Source System | Reviewer | Status |
|---|---|---|---|---|---|---|
| Retention Analytics | 1.1 Compassion/Dignity | 01_WELLBEING/1.1/1.1_Retention_Analytics_2026-01.pdf | Jan 2026 | ML Forecasting Module | OM - Sarah | ✅ Current |
| Safe Staffing Compliance | 1.1 Compassion/Dignity | 01_WELLBEING/1.1/1.1_Safe_Staffing_Compliance_2026-01.pdf | Jan 2026 | Real-Time Dashboard | OM - Sarah | ✅ Current |

---

#### **Subfolder 1.2: Get Most Out of Life**

**Evidence Types:**
- **Activities Coordinator Scheduling:**
  - Role coverage reports (Activities Coordinator presence)
  - Staffing adequacy enabling activities (narrative report)
  - File naming: `1.2_Activities_Staffing_YYYY-MM.pdf`

- **Activities Outcomes:** *(Future - Activities module 2027)*
  - Participation tracking
  - Resident preference fulfillment
  - File naming: `1.2_Activities_Outcomes_YYYY-QQ.pdf`

**Evidence Index Entry Example:**
| Evidence Item | Quality Indicator | File Path | Date Range | Source System | Reviewer | Status |
|---|---|---|---|---|---|---|
| Activities Staffing | 1.2 Get Most Out of Life | 01_WELLBEING/1.2/1.2_Activities_Staffing_2026-01.pdf | Jan 2026 | Role Coverage Report | OM - Sarah | ✅ Current |

---

#### **Subfolder 1.3: Health & Wellbeing Benefits**

**Evidence Types:**
- **Training Compliance - Clinical Skills:**
  - Training matrices (18 courses including Dementia, EOL, Falls Prevention)
  - 0% lapsed certification reports
  - Course completion timelines
  - File naming: `1.3_Training_Compliance_YYYY-MM.pdf`

- **Skill Mix Compliance:**
  - Senior Care Worker coverage by unit
  - Clinical oversight presence (SSCW, SSCWN ratios)
  - Competency-based role assignment evidence
  - File naming: `1.3_Skill_Mix_YYYY-MM.pdf`

- **Supervision for Clinical Development:**
  - Supervision session logs (quarterly minimum per SSSC)
  - Reflective practice records
  - CPD hours tracking *(Enhanced Q2 2026)*
  - File naming: `1.3_Supervision_Records_YYYY-QQ.pdf`

- **Health Outcome Correlation:** *(Future - TQM Incident module Q3 2026)*
  - Incident analysis linked to staffing
  - Clinical governance dashboard
  - Health Protection & Safety Report
  - File naming: `1.3_Health_Protection_YYYY-QQ.pdf`

**Evidence Index Entry Example:**
| Evidence Item | Quality Indicator | File Path | Date Range | Source System | Reviewer | Status |
|---|---|---|---|---|---|---|
| Training Compliance | 1.3 Health/Wellbeing | 01_WELLBEING/1.3/1.3_Training_Compliance_2026-01.pdf | Jan 2026 | Training Module | HOS - Mark | ✅ Current |
| Skill Mix Report | 1.3 Health/Wellbeing | 01_WELLBEING/1.3/1.3_Skill_Mix_2026-01.pdf | Jan 2026 | Role Coverage Report | OM - Sarah | ✅ Current |

---

### **FOLDER 2: LEADERSHIP - How good is our leadership?**

#### **Subfolder 2.1: Staff & People Evaluate Quality**

**Evidence Types:**
- **SAtSD Co-Design Documentation:**
  - DLP Project Charter (user participation evidence)
  - Double Diamond methodology documentation
  - Stakeholder engagement records (9 OMs, 5 SMs, SCWs, Families Council)
  - File naming: `2.1_SAtSD_CoDesign_YYYY.pdf`

- **Staff Engagement Mechanisms:**
  - Staff engagement survey results (quarterly)
  - Monthly feedback session minutes
  - AI assistant query analytics (user pain points)
  - File naming: `2.1_Staff_Engagement_YYYY-QQ.pdf`

- **Resident/Family QI Involvement:** *(Future - TQM Feedback module Q3 2026)*
  - Families Council ongoing participation
  - Resident QI priority surveys
  - "You Said, We Did" action tracker
  - File naming: `2.1_Resident_QI_Involvement_YYYY-QQ.pdf`

**Evidence Index Entry Example:**
| Evidence Item | Quality Indicator | File Path | Date Range | Source System | Reviewer | Status |
|---|---|---|---|---|---|---|
| SAtSD Co-Design Charter | 2.1 Evaluate Quality | 02_LEADERSHIP/2.1/2.1_SAtSD_CoDesign_2025.pdf | 2025 Development | DLP Program | HOS - Mark | ✅ Current |
| Staff Engagement Survey | 2.1 Evaluate Quality | 02_LEADERSHIP/2.1/2.1_Staff_Engagement_2026-Q1.pdf | Q1 2026 | Survey Module | HOS - Mark | ⏳ Pending |

---

#### **Subfolder 2.2: Quality Assurance Led Well**

**Evidence Types:**
- **Audit Trail Documentation:**
  - System access logs (who, when, what actions)
  - Schedule change history (all edits logged)
  - Approval workflow records
  - File naming: `2.2_Audit_Trail_YYYY-MM.pdf`

- **Automated Compliance Reporting:**
  - Weekly Management Reports
  - Monthly Executive Summaries
  - CI Performance Dashboard (actual inspection data)
  - File naming: `2.2_CI_Performance_Dashboard_YYYY-QQ.pdf`

- **Data-Driven Decision Making:**
  - Executive dashboard screenshots (real-time KPIs)
  - ML forecasting accuracy reports (25.1% MAPE)
  - ROI analysis (£590K savings documentation)
  - File naming: `2.2_Executive_Dashboard_YYYY-MM.pdf`

- **HIS/NES Framework Alignment:**
  - HIS QMS Performance Dashboard *(Q2 2026)*
  - PDSA Project Tracker *(Q2 2026)*
  - Quality Improvement Project Tracker
  - File naming: `2.2_PDSA_Tracker_YYYY-QQ.pdf`

- **Board Quality Governance:**
  - Board meeting minutes (quality discussions)
  - Quarterly quality review schedules
  - Board-level quality metrics
  - File naming: `2.2_Board_Quality_Review_YYYY-QQ.pdf`

**Evidence Index Entry Example:**
| Evidence Item | Quality Indicator | File Path | Date Range | Source System | Reviewer | Status |
|---|---|---|---|---|---|---|
| CI Performance Dashboard | 2.2 QA Led Well | 02_LEADERSHIP/2.2/2.2_CI_Performance_Dashboard_2026-Q1.pdf | Q1 2026 | Dashboard Module | HOS - Mark | ✅ Current |
| Audit Trail Report | 2.2 QA Led Well | 02_LEADERSHIP/2.2/2.2_Audit_Trail_2026-01.pdf | Jan 2026 | System Logs | IT Admin | ✅ Current |

---

### **FOLDER 3: STAFF - How good is our staff team?**

#### **Subfolder 3.1: Recruited Well**

**Evidence Types:**
- **Workforce Planning Intelligence:**
  - ML forecasting reports (30-day staffing predictions)
  - 80% confidence intervals documentation
  - Proactive recruitment planning evidence
  - File naming: `3.1_Workforce_Planning_YYYY-QQ.pdf`

- **Retention Analytics:**
  - Turnover tracking (30% baseline)
  - ML-predicted departures (6/year preventable = £120K)
  - At-risk staff intervention records
  - File naming: `3.1_Retention_Analytics_YYYY-QQ.pdf`

- **Recruitment Workflow:** *(Future - Phase 5 2027)*
  - Vacancy posting to hire timeline
  - Skills gap analysis documentation
  - SSSC registration verification
  - File naming: `3.1_Recruitment_Workflow_YYYY-QQ.pdf`

**Evidence Index Entry Example:**
| Evidence Item | Quality Indicator | File Path | Date Range | Source System | Reviewer | Status |
|---|---|---|---|---|---|---|
| Workforce Planning Report | 3.1 Recruited Well | 03_STAFF/3.1/3.1_Workforce_Planning_2026-Q1.pdf | Q1 2026 | ML Forecasting | HOS - Mark | ✅ Current |
| Retention Analytics | 3.1 Recruited Well | 03_STAFF/3.1/3.1_Retention_Analytics_2026-Q1.pdf | Q1 2026 | Analytics Module | HOS - Mark | ✅ Current |

---

#### **Subfolder 3.2: Right Knowledge & Competence**

**Evidence Types:**
- **Comprehensive Training Tracking:**
  - Training compliance matrices (18 courses, 6,778 records)
  - 0% lapsed certification reports (vs. 15% manual baseline)
  - Course completion timelines (30-day alerts)
  - Training by role reports (competency requirements)
  - File naming: `3.2_Training_Compliance_YYYY-MM.pdf`

- **Supervision Session Tracking:**
  - Quarterly 1:1 supervision logs (SSSC requirement)
  - Reflective practice documentation
  - CPD hours tracking *(Enhanced Q2 2026)*
  - File naming: `3.2_Supervision_Records_YYYY-QQ.pdf`

- **Competency-Based Role Assignment:**
  - Role-based access control evidence
  - Specialist role prerequisites (SSCW, SSCWN)
  - Safe skill mix assurance
  - File naming: `3.2_Competency_Based_Roles_YYYY-MM.pdf`

- **Competency Assessment Scores:** *(Future - TQM Training module Q4 2026)*
  - Pre/post training assessments
  - Proficiency levels by staff
  - Skills matrix by unit
  - File naming: `3.2_Competency_Assessments_YYYY-QQ.pdf`

**Evidence Index Entry Example:**
| Evidence Item | Quality Indicator | File Path | Date Range | Source System | Reviewer | Status |
|---|---|---|---|---|---|---|
| Training Compliance Matrix | 3.2 Knowledge/Competence | 03_STAFF/3.2/3.2_Training_Compliance_2026-01.pdf | Jan 2026 | Training Module | HOS - Mark | ✅ Current |
| Supervision Records | 3.2 Knowledge/Competence | 03_STAFF/3.2/3.2_Supervision_Records_2026-Q1.pdf | Q1 2026 | Supervision Module | OM - Sarah | ✅ Current |

---

#### **Subfolder 3.3: Supported & Involved**

**Evidence Types:**
- **Fair Shift Allocation:**
  - Algorithmic scheduling audit trails
  - Workload equity analytics (overtime distribution)
  - Fairness transparency evidence
  - File naming: `3.3_Fair_Allocation_YYYY-MM.pdf`

- **Self-Service Empowerment:**
  - Portal usage analytics (85% mobile adoption)
  - Digital leave request metrics (vs. 10-15% paper loss)
  - Shift swap statistics (18% weekly usage)
  - File naming: `3.3_Self_Service_Analytics_YYYY-MM.pdf`

- **Communication Efficiency:**
  - AI assistant query analytics (200+ patterns, 80% resolution)
  - £20K WhatsApp/phone savings documentation
  - 24/7 support availability evidence
  - File naming: `3.3_Communication_Efficiency_YYYY-QQ.pdf`

- **Work-Life Balance:**
  - Advanced schedule visibility metrics (>1 week vs. <1 week)
  - Leave approval transparency reports
  - Staff engagement survey (work-life balance questions)
  - File naming: `3.3_Work_Life_Balance_YYYY-QQ.pdf`

- **Staff Engagement Survey Results:**
  - Quarterly satisfaction surveys (85% target)
  - Fairness perception data
  - Anonymous feedback summaries
  - File naming: `3.3_Staff_Engagement_YYYY-QQ.pdf`

**Evidence Index Entry Example:**
| Evidence Item | Quality Indicator | File Path | Date Range | Source System | Reviewer | Status |
|---|---|---|---|---|---|---|
| Fair Allocation Report | 3.3 Supported/Involved | 03_STAFF/3.3/3.3_Fair_Allocation_2026-01.pdf | Jan 2026 | Scheduling Module | OM - Sarah | ✅ Current |
| Self-Service Analytics | 3.3 Supported/Involved | 03_STAFF/3.3/3.3_Self_Service_Analytics_2026-01.pdf | Jan 2026 | Portal Analytics | IT Admin | ✅ Current |

---

### **FOLDER 4: SETTING - How good is our setting?**

#### **Subfolder 4.1: High Quality Facilities**

**Evidence Types:**
- **Housekeeping/Maintenance Scheduling:**
  - Role coverage reports (Housekeeper, Maintenance presence)
  - Consistent environmental care staffing
  - File naming: `4.1_Facilities_Staffing_YYYY-MM.pdf`

- **Environmental Quality Tracking:** *(Future - TQM Quality Audits Q2 2026)*
  - Cleanliness audit checklists
  - Safety check schedules
  - Infection control compliance
  - File naming: `4.1_Environmental_Audits_YYYY-QQ.pdf`

- **Facilities Maintenance Management:** *(Future - Phase 5 2027)*
  - Maintenance request logs
  - Repair completion tracking
  - Preventive maintenance schedules
  - File naming: `4.1_Maintenance_Management_YYYY-QQ.pdf`

**Evidence Index Entry Example:**
| Evidence Item | Quality Indicator | File Path | Date Range | Source System | Reviewer | Status |
|---|---|---|---|---|---|---|
| Facilities Staffing Report | 4.1 High Quality Facilities | 04_SETTING/4.1/4.1_Facilities_Staffing_2026-01.pdf | Jan 2026 | Role Coverage | OM - Sarah | ✅ Current |

---

### **FOLDER 5: CARE & SUPPORT - How well do we support health & wellbeing?**

#### **Subfolder 5.1: Assessment & Personal Planning**

**Evidence Types:**
- **Adequate Staffing for Care Planning:**
  - Time savings documentation (88% burden reduction)
  - Manager time freed for care planning evidence
  - Narrative reports on staffing impact
  - File naming: `5.1_Staffing_Enables_Planning_YYYY-QQ.pdf`

- **Care Plan Integration:** *(Future - Phase 5 2027)*
  - Care plan review compliance
  - Resident preference data
  - Goal achievement tracking
  - File naming: `5.1_Care_Plan_Compliance_YYYY-QQ.pdf`

**Evidence Index Entry Example:**
| Evidence Item | Quality Indicator | File Path | Date Range | Source System | Reviewer | Status |
|---|---|---|---|---|---|---|
| Staffing Enables Planning | 5.1 Assessment/Planning | 05_CARE_SUPPORT/5.1/5.1_Staffing_Enables_Planning_2026-Q1.pdf | Q1 2026 | Efficiency Report | OM - Sarah | ✅ Current |

---

#### **Subfolder 5.2: Person-Centred Care**

**Evidence Types:**
- **Consistent Staff Relationships:**
  - Retention analytics (staff continuity)
  - Turnover reduction impact on familiarity
  - File naming: `5.2_Staff_Continuity_YYYY-QQ.pdf`

- **Adequate Time for Person-Centered Care:**
  - Real-time understaffing alert records (<1% error rate)
  - Safe ratio compliance (dignity and choice time)
  - File naming: `5.2_Safe_Ratios_YYYY-MM.pdf`

- **Resident-Staff Matching:** *(Future - Q2-Q3 2026)*
  - Preference-based allocation
  - Resident satisfaction with assigned staff
  - File naming: `5.2_Resident_Staff_Matching_YYYY-QQ.pdf`

**Evidence Index Entry Example:**
| Evidence Item | Quality Indicator | File Path | Date Range | Source System | Reviewer | Status |
|---|---|---|---|---|---|---|
| Staff Continuity Report | 5.2 Person-Centred Care | 05_CARE_SUPPORT/5.2/5.2_Staff_Continuity_2026-Q1.pdf | Q1 2026 | Retention Analytics | HOS - Mark | ✅ Current |
| Safe Ratios Report | 5.2 Person-Centred Care | 05_CARE_SUPPORT/5.2/5.2_Safe_Ratios_2026-01.pdf | Jan 2026 | Real-Time Dashboard | OM - Sarah | ✅ Current |

---

#### **Subfolder 5.3: Health & Wellbeing Protected**

**Evidence Types:**
- **Infection Control & Clinical Training:**
  - Training compliance (Infection Control, Medication, Safeguarding)
  - 0% lapsed certifications
  - File naming: `5.3_Clinical_Training_YYYY-MM.pdf`

- **Safe Staffing Ratios:**
  - Real-time monitoring evidence
  - Ratio breach reduction (2-3/month → <1%)
  - File naming: `5.3_Safe_Staffing_YYYY-MM.pdf`

- **Incident Management:** *(Future - TQM Incident module Q3 2026)*
  - Root cause analysis (5 Whys, Fishbone, Pareto)
  - SPSP alignment documentation
  - Duty of Candour compliance
  - Medication error tracking
  - SPC run charts (incident trends)
  - File naming: `5.3_Incident_Management_YYYY-QQ.pdf`

- **Clinical Governance Dashboard:** *(Future - Q3 2026)*
  - Incidents linked to staffing patterns
  - Early warning system for deteriorating residents
  - File naming: `5.3_Clinical_Governance_YYYY-QQ.pdf`

**Evidence Index Entry Example:**
| Evidence Item | Quality Indicator | File Path | Date Range | Source System | Reviewer | Status |
|---|---|---|---|---|---|---|
| Clinical Training Compliance | 5.3 Health Protected | 05_CARE_SUPPORT/5.3/5.3_Clinical_Training_2026-01.pdf | Jan 2026 | Training Module | HOS - Mark | ✅ Current |
| Safe Staffing Report | 5.3 Health Protected | 05_CARE_SUPPORT/5.3/5.3_Safe_Staffing_2026-01.pdf | Jan 2026 | Dashboard | OM - Sarah | ✅ Current |

---

## Automated Report Filing System

### **Report Generation & Auto-Filing Workflow**

**Trigger Events:**
1. **Weekly Reports:** Monday 7:00 AM
   - Weekly Management Report → `AUTOMATED_REPORTS/Weekly_Management_Reports/`
   - Additional Staffing Report → `AUTOMATED_REPORTS/Weekly_Management_Reports/`

2. **Monthly Reports:** First Monday 8:00 AM
   - Training Compliance Report → `03_STAFF/3.2/` AND `AUTOMATED_REPORTS/Monthly_Executive_Summaries/`
   - Retention Analytics → `03_STAFF/3.1/` AND `AUTOMATED_REPORTS/Monthly_Executive_Summaries/`
   - Skill Mix Report → `01_WELLBEING/1.3/` AND `AUTOMATED_REPORTS/Monthly_Executive_Summaries/`

3. **Quarterly Reports:** 10 days post-quarter
   - CI Performance Dashboard → `02_LEADERSHIP/2.2/` AND `AUTOMATED_REPORTS/Quarterly_CI_Performance_Reviews/`
   - Staff Engagement Survey → `02_LEADERSHIP/2.1/` AND `03_STAFF/3.3/`
   - Supervision Records Summary → `03_STAFF/3.2/`

4. **On-Demand Reports:** Inspection trigger
   - All Inspection Readiness Packs → `INSPECTION_READINESS_PACKS/`
   - Gap Analysis Tracker update → `MASTER_INDEX/`

**File Naming Convention:**
```
[QI_Number]_[Report_Name]_[YYYY]-[MM or QQ].[Extension]

Examples:
- 3.2_Training_Compliance_2026-01.pdf
- 2.2_CI_Performance_Dashboard_2026-Q1.pdf
- 5.3_Incident_Management_2026-Q2.pdf
```

**Version Control:**
- Most recent version stored in primary location
- Previous versions archived in `AUTOMATED_REPORTS/Archive/[YYYY]/`
- Retention: 5 years (regulatory requirement)

**Metadata Tagging:**
Each auto-filed report includes:
- Report generation date/time
- Data date range covered
- Source system/module
- Auto-generated or manual flag
- Reviewer name (assigned OM/HOS)
- Evidence status (✅ Current, ⏳ Pending Review, ❌ Outdated)

---

## Inspection Readiness Pack Assembly

### **Pack Components (One per Quality Theme)**

**PACK 1: Wellbeing Evidence Pack**

**Cover Page:**
- Care Inspectorate Theme 1: Wellbeing
- Quality Indicators: 1.1, 1.2, 1.3
- Care Home: [Name]
- Preparation Date: [Date]
- Prepared By: [OM Name]
- Review Period: [Last 12 months]

**Section 1: Quality Indicator 1.1 Evidence (Compassion, Dignity, Respect)**
- Retention Analytics (last 6 months)
- Safe Staffing Compliance Report (last 3 months)
- Staff Fairness Report (last quarter)
- Resident Feedback Summary (if available)
- **Narrative Summary:** 1-page explanation of evidence

**Section 2: Quality Indicator 1.2 Evidence (Get Most Out of Life)**
- Activities Coordinator Staffing Report
- Narrative on how adequate staffing enables activities
- **Narrative Summary:** 1-page explanation

**Section 3: Quality Indicator 1.3 Evidence (Health & Wellbeing Benefits)**
- Training Compliance Matrix (current month)
- Skill Mix Report (current month)
- Supervision Records Summary (last quarter)
- Health Protection Report (if available)
- **Narrative Summary:** 1-page explanation

**Section 4: Trend Analysis & Improvement**
- 12-month trend charts (retention, training, staffing levels)
- PDSA cycles related to wellbeing improvements
- Actions taken based on evidence

**Section 5: Appendices**
- System screenshots (dashboard, reports)
- Stakeholder quotes (staff, residents, families)
- External validation (audits, awards, benchmarking)

**Total Pages:** 25-30 pages per theme pack

---

**PACK 2: Leadership Evidence Pack**

**Quality Indicators:** 2.1 (Staff/People Evaluate Quality), 2.2 (QA Led Well)

**Key Evidence:**
- SAtSD Co-Design Charter
- Staff Engagement Survey Results
- Audit Trail Reports
- CI Performance Dashboard
- Executive Dashboard Screenshots
- PDSA Project Tracker
- Board Quality Review Minutes
- ROI Analysis (£590K savings)

---

**PACK 3: Staff Evidence Pack**

**Quality Indicators:** 3.1 (Recruited Well), 3.2 (Knowledge/Competence), 3.3 (Supported/Involved)

**Key Evidence:**
- Workforce Planning Reports (ML forecasting)
- Training Compliance Matrices (0% lapsed)
- Supervision Records Summaries
- Fair Allocation Audit Trails
- Self-Service Analytics
- Staff Engagement Surveys
- Communication Efficiency Reports

---

**PACK 4: Setting Evidence Pack**

**Quality Indicator:** 4.1 (High Quality Facilities)

**Key Evidence:**
- Facilities Staffing Reports
- Environmental Audit Checklists (when available)
- Narrative on Staffing Support for Facilities

---

**PACK 5: Care & Support Evidence Pack**

**Quality Indicators:** 5.1 (Assessment/Planning), 5.2 (Person-Centred Care), 5.3 (Health Protected)

**Key Evidence:**
- Staffing Enables Care Planning Reports
- Staff Continuity Reports
- Safe Ratios Compliance
- Clinical Training Compliance
- Incident Management Reports (when available)
- Clinical Governance Dashboard (when available)

---

## Master Evidence Index

### **Evidence_Index_Master.xlsx Structure**

**Columns:**
1. **Evidence ID:** Unique identifier (e.g., WB-1.1-001)
2. **Quality Theme:** Wellbeing, Leadership, Staff, Setting, Care & Support
3. **Quality Indicator:** 1.1, 1.2, 1.3, 2.1, 2.2, 3.1, 3.2, 3.3, 4.1, 5.1, 5.2, 5.3
4. **Evidence Item Name:** Descriptive title
5. **File Path:** Full path within repository
6. **Date Range:** Data period covered
7. **Generation Date:** When evidence created
8. **Source System:** Module/report that generated it
9. **Reviewer:** Assigned OM/HOS
10. **Review Date:** When last reviewed
11. **Status:** ✅ Current (<30 days), ⏳ Pending Review, ❌ Outdated (>30 days), 🆕 New
12. **Inspection Pack Inclusion:** Yes/No
13. **Notes:** Additional context

**Example Rows:**

| Evidence ID | Theme | QI | Evidence Item | File Path | Date Range | Gen Date | Source | Reviewer | Status |
|---|---|---|---|---|---|---|---|---|---|
| WB-1.1-001 | Wellbeing | 1.1 | Retention Analytics | 01_WELLBEING/1.1/1.1_Retention_Analytics_2026-01.pdf | Jan 2026 | 2026-02-01 | ML Module | HOS-Mark | ✅ Current |
| LD-2.2-005 | Leadership | 2.2 | CI Dashboard | 02_LEADERSHIP/2.2/2.2_CI_Performance_Dashboard_2026-Q1.pdf | Q1 2026 | 2026-01-10 | Dashboard | HOS-Mark | ✅ Current |
| ST-3.2-012 | Staff | 3.2 | Training Matrix | 03_STAFF/3.2/3.2_Training_Compliance_2026-01.pdf | Jan 2026 | 2026-02-01 | Training | HOS-Mark | ✅ Current |

**Filtering & Sorting:**
- Filter by Quality Indicator to see all evidence for 1.1, 1.2, etc.
- Filter by Status to identify outdated evidence needing refresh
- Sort by Review Date to prioritize evidence requiring manager review
- Filter by Inspection Pack Inclusion to assemble readiness packs

---

### **Quality_Indicator_Mapping.pdf**

**Purpose:** Visual guide linking system features → reports → quality indicators

**Structure:**
- **Page 1:** Overview of 5 themes with QI breakdown
- **Pages 2-6:** One page per theme showing:
  - Quality Indicator list
  - System features supporting each QI
  - Reports demonstrating compliance
  - Evidence file locations
  - Gap areas (acknowledged limitations)

**Example - Theme 3: Staff (Page 4):**

| Quality Indicator | System Features | Reports Available | Evidence Location | Gap Areas |
|---|---|---|---|---|
| 3.1 Recruited Well | ML forecasting, retention analytics | Workforce Planning Report, Retention Analytics | 03_STAFF/3.1/ | Recruitment workflow not tracked |
| 3.2 Knowledge/Competence | 18-course training, supervision logs, role-based access | Training Compliance Matrix, Supervision Records | 03_STAFF/3.2/ | Competency scores not tracked (Q4 2026) |
| 3.3 Supported/Involved | Fair allocation, self-service portal, AI assistant | Fair Allocation Report, Self-Service Analytics, Engagement Survey | 03_STAFF/3.3/ | Need quarterly survey data |

---

### **Evidence_Freshness_Dashboard.pdf**

**Purpose:** Monthly snapshot of evidence currency

**Visual Elements:**
- **Traffic Light Summary:**
  - 🟢 Green: >80% evidence current (<30 days)
  - 🟡 Amber: 60-80% evidence current
  - 🔴 Red: <60% evidence current

- **Evidence Aging Chart:**
  - X-axis: Quality Indicators (1.1-5.3)
  - Y-axis: Days since last evidence update
  - Bar color: Green (<30), Amber (30-60), Red (>60)

- **Action Items:**
  - List of evidence items >30 days old requiring refresh
  - Assigned reviewer and target completion date

**Example:**
```
Evidence Freshness Status - February 2026

Overall: 🟢 85% Current (34/40 evidence items <30 days)

By Theme:
- Wellbeing: 🟢 90% (9/10 items current)
- Leadership: 🟢 100% (8/8 items current)
- Staff: 🟢 87% (13/15 items current)
- Setting: 🟡 67% (2/3 items current) ⚠️
- Care & Support: 🟢 80% (4/5 items current)

Action Required:
- 4.1_Facilities_Staffing_2025-12.pdf (62 days old) - Assign: OM-Sarah - Due: Feb 15
- 5.1_Staffing_Enables_Planning_2025-Q4.pdf (45 days old) - Assign: OM-Sarah - Due: Feb 20
```

---

### **Gap_Analysis_Tracker.xlsx**

**Purpose:** Monitor progress on closing inspection readiness gaps

**Columns:**
1. **Gap ID:** Unique identifier
2. **Quality Indicator:** Affected QI
3. **Gap Description:** What evidence is missing
4. **Impact:** High/Medium/Low
5. **Mitigation Plan:** How gap will be addressed
6. **Target Date:** When evidence will be available
7. **Status:** 🔴 Not Started, 🟡 In Progress, 🟢 Complete
8. **Owner:** Responsible person
9. **Dependencies:** What needs to happen first

**Example Rows:**

| Gap ID | QI | Gap Description | Impact | Mitigation Plan | Target | Status | Owner |
|---|---|---|---|---|---|---|---|
| GAP-001 | 1.1 | Resident feedback integration | HIGH | Deploy TQM Feedback module | Q3 2026 | 🟡 In Progress | HOS-Mark |
| GAP-002 | 5.3 | Incident RCA tools | HIGH | Deploy TQM Incident module | Q3 2026 | 🟡 In Progress | HOS-Mark |
| GAP-003 | 2.2 | PDSA project tracker | HIGH | Build tracker in TQM QA module | Q2 2026 | 🟡 In Progress | HOS-Mark |
| GAP-004 | 3.3 | Staff engagement survey data | HIGH | Conduct quarterly survey | Q1 2026 | 🔴 Not Started | OM-Sarah |
| GAP-005 | 4.1 | Environmental quality audits | MEDIUM | Add to TQM QA module checklists | Q2 2026 | 🟡 In Progress | HOS-Mark |

---

## Evidence Collection Procedures for Managers

### **Operational Manager (OM) Responsibilities**

**Daily Tasks:**
- ✅ Review automated report generation confirmations (Monday 7am)
- ✅ Verify shift data accuracy (supports downstream evidence integrity)

**Weekly Tasks:**
- ✅ Review Weekly Management Report (Monday morning)
- ✅ Review Additional Staffing Report (Monday morning)
- ✅ Flag any data anomalies to IT/HOS for correction

**Monthly Tasks:**
- ✅ Review monthly automated reports (first Monday)
- ✅ Conduct narrative analysis (1-2 paragraphs per report explaining trends)
- ✅ File reports in appropriate Evidence Repository folders
- ✅ Update Evidence Index with new entries
- ✅ Check Evidence Freshness Dashboard for outdated items

**Quarterly Tasks:**
- ✅ Review quarterly reports (CI Performance Dashboard, Supervision Summary)
- ✅ Prepare narrative summaries for inspection readiness packs
- ✅ Participate in staff engagement survey administration
- ✅ Review Gap Analysis Tracker progress
- ✅ Update inspection readiness packs with new evidence

**Inspection Trigger Tasks (48-72 hours notice):**
- ✅ Assemble relevant inspection readiness pack (theme announced by CI)
- ✅ Review evidence for completeness (use Master Index checklist)
- ✅ Prepare 1-page narrative summary per quality indicator
- ✅ Print evidence pack and create digital backup
- ✅ Rehearse walkthrough with HOS (anticipated questions)

**Time Commitment:**
- Daily: 5 minutes
- Weekly: 30 minutes (review reports)
- Monthly: 2 hours (review, narrative, filing)
- Quarterly: 4 hours (comprehensive review, pack assembly)
- **Total:** ~4-5 hours/month (vs. 40 hours manual inspection prep)

---

### **Head of Service (HOS) Responsibilities**

**Monthly Tasks:**
- ✅ Review all executive dashboards and monthly summaries
- ✅ Approve evidence narratives prepared by OMs
- ✅ Conduct data quality audits (spot-check 5-10 records)
- ✅ Update board on quality metrics

**Quarterly Tasks:**
- ✅ Lead staff engagement survey analysis
- ✅ Review Gap Analysis Tracker with senior leadership
- ✅ Update PDSA Project Tracker (ongoing QI initiatives)
- ✅ Prepare board quality review presentation
- ✅ Conduct mock inspection walkthrough with OMs

**Annually:**
- ✅ Comprehensive inspection readiness review (Q4)
- ✅ Update evidence repository structure (add new modules/reports)
- ✅ Archive outdated evidence (5-year retention)
- ✅ Refresh manager training on evidence collection

**Inspection Trigger Tasks:**
- ✅ Final review of inspection readiness pack
- ✅ Brief OMs on anticipated inspector questions
- ✅ Coordinate with external stakeholders (CI liaison)
- ✅ Arrange live system demonstration if requested

---

## Role-Based Access Control for Evidence Repository

### **Access Levels**

**Level 1: Operational Managers (OMs)**
- **Read Access:** All evidence for their assigned care homes
- **Write Access:** Can add evidence, update narratives, file reports for their homes
- **Restrictions:** Cannot delete evidence, cannot access audit trail logs

**Level 2: Head of Service (HOS)**
- **Read Access:** All evidence across all 5 care homes
- **Write Access:** Can add, update, approve evidence; can manage Gap Analysis Tracker
- **Admin Access:** Can delete outdated evidence, access audit trail logs, manage access permissions

**Level 3: IT Administrator**
- **Technical Access:** System logs, automated report configurations, version control
- **Restrictions:** Cannot edit evidence narratives (operational content managed by OM/HOS)

**Level 4: External Reviewers (Care Inspectorate)**
- **Read-Only Access:** On-demand access to inspection readiness packs during inspection
- **Duration:** Temporary (inspection period only)
- **Scope:** Theme-specific (only evidence pack for announced theme)

**Level 5: Board/Leadership**
- **Read Access:** Executive summaries, quarterly reports, Gap Analysis Tracker
- **Restrictions:** No access to detailed operational evidence (governance oversight only)

---

## Evidence Quality Assurance

### **Data Integrity Checks**

**Automated Validations:**
- ✅ Report generation timestamp verification
- ✅ Data range coverage confirmation (no missing months)
- ✅ File naming convention compliance
- ✅ Cross-reference checks (e.g., training data matches staff roster)

**Manual Reviews (Monthly by OM):**
- ✅ Spot-check 10 random data points for accuracy
- ✅ Verify narrative summaries align with quantitative data
- ✅ Check trend charts for anomalies (e.g., sudden spikes)
- ✅ Confirm evidence freshness (<30 days for critical items)

**Quarterly Audits (by HOS):**
- ✅ Comprehensive data quality audit (50-100 records)
- ✅ Evidence completeness assessment (all QIs covered?)
- ✅ Gap analysis progress review
- ✅ External benchmarking (vs. sector standards)

**Annual Certification (by HOS + External Auditor):**
- ✅ Full evidence repository review
- ✅ Compliance with retention policies (5 years)
- ✅ Access control verification
- ✅ Disaster recovery testing (backup restoration)

---

## Evidence Retention & Archival Policy

### **Retention Periods**

**Regulatory Minimum:** 5 years (Care Inspectorate requirement)

**Active Evidence:** Current + 2 years
- Stored in primary Evidence Repository folders
- Readily accessible for inspections

**Archived Evidence:** 3-5 years old
- Moved to `AUTOMATED_REPORTS/Archive/[YYYY]/`
- Accessible on request (not in inspection readiness packs)

**Destruction:** >5 years old
- Secure deletion with certificate of destruction
- Exception: Legal holds, ongoing investigations

### **Backup & Disaster Recovery**

**Daily Backups:**
- Full system backup at 2:00 AM (off-peak)
- Encrypted backup to DigitalOcean Spaces (S3-compatible)
- Retention: 30 days rolling

**Monthly Archival Backups:**
- Full evidence repository snapshot
- Stored on external NVME drive (offline for ransomware protection)
- Retention: 5 years

**Recovery Testing:**
- Quarterly restoration drills
- Recovery Time Objective (RTO): 4 hours
- Recovery Point Objective (RPO): 24 hours

---

## Implementation Roadmap

### **Phase 1: Foundation (January 2026 - Weeks 1-2)**

**Week 1:**
- ✅ Create Evidence Repository folder structure (5 themes, 12 QI subfolders)
- ✅ Develop Evidence Index Master template (Excel)
- ✅ Configure automated report filing rules
- ✅ Assign OM/HOS repository access permissions

**Week 2:**
- ✅ Populate repository with existing reports (backfill December 2025 - January 2026)
- ✅ Create first version of Quality Indicator Mapping guide
- ✅ Develop Evidence Freshness Dashboard template
- ✅ Initialize Gap Analysis Tracker with Phase 3 gaps

**Deliverables:**
- Evidence Repository operational
- 40-50 evidence items filed and indexed
- Manager access configured

---

### **Phase 2: Operationalization (January 2026 - Weeks 3-4)**

**Week 3:**
- ✅ Develop 7 priority NEW reports (Wellbeing QI, Staff Competence, Health Protection, QA & Improvement, Stakeholder Engagement, Staff Support, Workforce Planning)
- ✅ Configure auto-filing for NEW reports
- ✅ Create Inspection Readiness Pack templates (5 themes)

**Week 4:**
- ✅ Manager training session: "Using the Evidence Repository"
- ✅ Practice inspection readiness pack assembly (1 theme pilot)
- ✅ Refine Evidence Index based on OM feedback
- ✅ Conduct first Evidence Freshness Dashboard review

**Deliverables:**
- 13 existing + 7 NEW reports = 20 total reports auto-filing
- 5 Inspection Readiness Pack templates
- Managers trained and confident

---

### **Phase 3: Enhancement (February-March 2026)**

**February:**
- ✅ Assemble first complete set of 5 inspection readiness packs
- ✅ Conduct mock inspection with quality manager (1 theme)
- ✅ Refine narrative summaries based on mock findings
- ✅ Document board quality review schedule

**March:**
- ✅ Monthly evidence collection cycle fully operational (OMs self-sufficient)
- ✅ First quarterly Gap Analysis Tracker review
- ✅ Update repository with Q1 2026 quarterly reports
- ✅ Conduct second mock inspection (different theme)

**Deliverables:**
- 100% evidence repository coverage for current capabilities
- Mock inspection validation (2 themes tested)
- Gap closure progress documented

---

### **Phase 4: Continuous Improvement (Q2-Q4 2026)**

**Q2 (April-June):**
- ✅ Integrate TQM Quality Audits module evidence (PDSA tracker, audit checklists)
- ✅ Add HIS QMS Performance Dashboard to Leadership theme
- ✅ Conduct staff engagement survey (Q2 data)
- ✅ Quarterly evidence repository audit

**Q3 (July-September):**
- ✅ Integrate TQM Incident Management evidence (RCA reports, SPSP compliance)
- ✅ Add TQM Feedback module evidence (resident surveys, complaints)
- ✅ Update inspection readiness packs with 6 months of trend data
- ✅ Conduct comprehensive mock inspection (all 5 themes)

**Q4 (October-December):**
- ✅ Integrate TQM Training module enhancements (competency scores, skills matrix)
- ✅ Annual inspection readiness review
- ✅ Update repository structure for 2027 (new modules/reports)
- ✅ Archive 2021 evidence (5 years old)

**Deliverables:**
- Evidence repository fully integrated with TQM modules
- Annual inspection readiness certification
- Repository maturity: 95+ readiness score

---

## Success Metrics & KPIs

### **Efficiency Metrics**

**Inspection Preparation Time:**
- **Baseline (Manual):** 40 hours per inspection
- **Q1 2026 Target:** 8 hours (80% reduction)
- **Q2-Q4 2026 Target:** 4-5 hours (88-90% reduction)

**Evidence Retrieval Speed:**
- **Target:** <5 minutes to locate any evidence item
- **Measurement:** Monthly spot-check (10 random requests)

**Evidence Freshness:**
- **Target:** >80% evidence <30 days old
- **Measurement:** Monthly Evidence Freshness Dashboard

---

### **Quality Metrics**

**Evidence Completeness:**
- **Target:** 100% quality indicators covered (12/12 QIs)
- **Measurement:** Master Index coverage analysis

**Data Accuracy:**
- **Target:** <1% error rate in spot-checks
- **Measurement:** Monthly data integrity audits

**Manager Confidence:**
- **Target:** 90%+ managers comfortable presenting evidence
- **Measurement:** Quarterly survey ("How confident are you in using evidence repository?")

---

### **Compliance Metrics**

**Inspection Readiness Score:**
- **Baseline (Dec 2025):** 72/100
- **Q1 2026 Target:** 78/100
- **Q2 2026 Target:** 85/100
- **Q3 2026 Target:** 92/100
- **Q4 2026 Target:** 95+/100

**Gap Closure Rate:**
- **Target:** 60% gaps closed by Q2, 80% by Q3, 95% by Q4
- **Measurement:** Gap Analysis Tracker progress

---

## Appendices

### **Appendix A: Evidence Repository Quick Reference Guide**

**For Operational Managers:**

**Where do I file...?**
- Training reports → `03_STAFF/3.2/`
- Retention analytics → `03_STAFF/3.1/` AND `01_WELLBEING/1.1/` (cross-reference)
- CI Performance Dashboard → `02_LEADERSHIP/2.2/`
- Staff engagement survey → `02_LEADERSHIP/2.1/` AND `03_STAFF/3.3/`

**How often do I update...?**
- Evidence Index → Monthly (after new reports filed)
- Inspection Readiness Packs → Quarterly (or inspection trigger)
- Evidence Freshness Dashboard → Monthly (auto-generated)
- Gap Analysis Tracker → Quarterly progress review

**Who do I contact if...?**
- Evidence file won't upload → IT Administrator
- Not sure which QI folder → Head of Service
- Need evidence narrative help → Peer OM or HOS
- Inspector requests evidence → HOS (coordinate response)

---

### **Appendix B: Sample Narrative Summary Template**

**Quality Indicator [X.X]: [Title]**

**Evidence Summary:**
[2-3 sentences describing what evidence demonstrates]

**Key Findings:**
- Strength 1: [Quantified data point]
- Strength 2: [Quantified data point]
- Area for improvement: [If applicable]

**Trend Analysis:**
[1-2 sentences on 3-6 month trends - improving/stable/declining]

**Actions Taken:**
[Bullet points on improvement initiatives based on evidence]

**Supporting Evidence Files:**
- [File 1 name and path]
- [File 2 name and path]

**Prepared By:** [OM Name]  
**Review Date:** [Date]

---

### **Appendix C: Mock Inspection Checklist**

**Pre-Inspection (3 days before):**
- [ ] Identify announced quality theme
- [ ] Assemble relevant inspection readiness pack
- [ ] Review Evidence Index for completeness
- [ ] Prepare 1-page narrative summaries per QI
- [ ] Print evidence pack + create digital backup
- [ ] Schedule 1-hour prep session with HOS

**During Mock Inspection:**
- [ ] Welcome inspector, offer evidence pack
- [ ] Demonstrate live system capabilities (dashboard, reports)
- [ ] Respond to questions using prepared narratives
- [ ] Show audit trail and accountability features
- [ ] Highlight quantified improvements (baseline → current)
- [ ] Acknowledge gaps with credible mitigation plans

**Post-Inspection Debrief:**
- [ ] Document inspector questions asked
- [ ] Identify evidence gaps revealed during questioning
- [ ] Update Gap Analysis Tracker with findings
- [ ] Refine narrative summaries based on feedback
- [ ] Schedule follow-up mock inspection (different theme)

---

**Document Version:** 1.0  
**Author:** Dean Sockalingum  
**Review Date:** February 2026 (post-manager training)  
**Status:** Phase 3 Task 6 Complete ✅

**Next Review:** Quarterly (April, July, October 2026) to integrate TQM module evidence

**Overall Assessment:** Evidence Repository Structure provides systematic, efficient framework for organizing and presenting regulatory evidence. Designed to reduce inspection preparation from 40 hours to 4-5 hours (88-90% reduction) while ensuring comprehensive quality indicator coverage. Automated filing, role-based access, and freshness monitoring ensure evidence remains current and accessible for inspection readiness.
