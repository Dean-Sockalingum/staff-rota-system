# TQM Modules 2-7: Implementation Assessment & Roadmap

**Date:** 14 January 2026  
**Objective:** Assess current state and plan implementation for TQM Modules 2-7  
**Strategy:** PostgreSQL for production, local SQLite testing, demo environment only  

---

## EXECUTIVE SUMMARY

### Module Status Overview

| Module | Name | Models Exist | Views Exist | Templates Exist | Implementation % | Priority |
|--------|------|--------------|-------------|-----------------|------------------|----------|
| **Module 1** | Quality Audits & Inspections | ✅ Complete | ✅ Complete | ✅ Complete | **100%** | P1 ✅ |
| **Module 2** | Incident & Safety Management | ⚠️ **Partial** | ⚠️ **Partial** | ⚠️ **Partial** | **45%** | **P1** |
| **Module 3** | Experience & Feedback | ⚠️ **Partial** | ⚠️ **Partial** | ⚠️ **Partial** | **30%** | **P2** |
| **Module 4** | Training & Competency | ⚠️ **Partial** | ⚠️ **Partial** | ⚠️ **Partial** | **50%** | **P1** |
| **Module 5** | Document & Policy Management | ❌ None | ❌ None | ❌ None | **0%** | P3 |
| **Module 6** | Risk Management | ❌ None | ❌ None | ❌ None | **0%** | P2 |
| **Module 7** | Performance Analytics & Dashboards | ⚠️ **Partial** | ⚠️ **Partial** | ⚠️ **Partial** | **40%** | P1 |

**Overall Assessment:**
- **1 module complete** (Module 1 - PDSA Tracker)
- **4 modules partially implemented** (Modules 2, 3, 4, 7)
- **2 modules not started** (Modules 5, 6)
- **Average completion: 38%** across all 7 modules

---

## MODULE 2: INCIDENT & SAFETY MANAGEMENT (45% Complete)

### Current State Analysis

#### ✅ What EXISTS

**Database Models** (`scheduling/models.py` lines 1120-1210):
```python
class IncidentReport(models.Model):
    # Core Fields
    reference_number         # Auto-generated (e.g., INC-2026-001)
    care_home               # FK to CareHome
    incident_date           # Date of incident
    incident_time           # Time of incident
    
    # Incident Details
    incident_type           # 25 choices (FALL, MEDICATION_ERROR, ABUSE, etc.)
    location               # Free text
    description            # Full description
    immediate_action_taken # Response taken
    
    # People Involved
    resident_involved      # FK to Resident (nullable)
    staff_involved         # ManyToMany to User
    reported_by           # FK to User
    witnesses             # FK to User (nullable)
    
    # Severity & Risk
    severity              # MINOR, MODERATE, MAJOR, DEATH
    risk_rating           # LOW, MEDIUM, HIGH, CRITICAL
    
    # External Notifications
    care_inspectorate_notified    # Boolean
    care_inspectorate_ref         # Text
    police_notified              # Boolean
    police_crime_ref             # Text
    local_authority_notified     # Boolean
    safeguarding_alert_raised    # Boolean
    
    # Investigation
    investigation_required        # Boolean
    investigation_assigned_to     # FK to User
    investigation_due_date       # Date
    investigation_complete       # Boolean
    investigation_findings       # Text
    
    # Learning & Actions
    lessons_learned              # Text
    preventive_actions          # Text
    
    # Closure
    incident_closed             # Boolean
    closed_date                 # Date
    closed_by                   # FK to User
    
    # Manager Review
    manager_reviewed            # Boolean
    manager_review_date         # Date
    manager_comments            # Text
    manager                     # FK to User
    
    # Timestamps
    created_at, updated_at
    
    # Methods
    requires_care_inspectorate_notification()  # Logic for CI notification
```

**Views** (Partial implementation in `scheduling/views.py`):
- Dashboard integration (recent incidents display)
- Basic incident display in manager dashboard
- Incident counting in analytics

**Templates** (4 templates exist):
- `compliance/report_incident.html` - Create new incident
- `compliance/view_incident.html` - View incident details
- `compliance/incident_management.html` - List incidents
- `compliance/my_incident_reports.html` - Staff's own reports

**URLs** (Partial routing exists):
- Some incident-related routes in `scheduling/urls.py`

#### ❌ What is MISSING

**Database Models:**
1. **Root Cause Analysis (RCA)** model
   - Fishbone diagram support
   - Contributing factors tracking
   - 5 Whys analysis
   
2. **Corrective Action** model
   - CAPA (Corrective & Preventive Actions)
   - Action ownership
   - Due dates and completion tracking
   - Effectiveness verification
   
3. **Duty of Candour** model
   - Family notification tracking
   - Communication logs
   - Apology letters
   - Statutory compliance
   
4. **Incident Category Trends** model
   - Statistical analysis
   - Month-over-month comparisons
   - Staffing correlation analysis

**Views:**
1. Full CRUD for incident lifecycle
2. Investigation workflow
3. Root cause analysis interface
4. CAPA tracking dashboard
5. Duty of Candour compliance tracker
6. Incident analytics and reporting
7. SPSP (Scottish Patient Safety Programme) alignment
8. Trend analysis with staffing correlation

**Templates:**
1. Investigation assignment interface
2. RCA documentation form
3. CAPA management dashboard
4. Duty of Candour tracker
5. Incident trend charts
6. CI notification generator
7. Lessons learned library

**Integration:**
1. Link to PDSA projects (incidents → improvement projects)
2. Link to training needs (incident patterns → training requirements)
3. Link to staffing (incident rates vs staffing levels)
4. Risk register integration

**ML/AI Features:**
1. Incident prediction based on staffing patterns
2. Similar incident suggestions
3. Automatic root cause suggestions
4. Risk scoring algorithms

### Implementation Priority: **P1 (High)**

**Estimated Effort:** 3 weeks  
**Dependencies:** Module 1 (PDSA) for improvement project linkage  
**Regulatory Impact:** High (Care Inspectorate compliance)  

---

## MODULE 3: EXPERIENCE & FEEDBACK (30% Complete)

### Current State Analysis

#### ✅ What EXISTS

**Basic Feedback System:**
- `scheduling/templates/scheduling/demo_feedback.html` - Demo feedback form
- `scheduling/templates/scheduling/feedback_widget.html` - Widget for feedback
- `scheduling/templates/scheduling/demo_feedback_thanks.html` - Thank you page
- `scheduling/templates/scheduling/feedback_results.html` - View results

**Views:**
- `demo_feedback()` - Capture feedback
- `demo_feedback_thanks()` - Confirmation
- `view_feedback_results()` - Display results

**URLs:**
- `/feedback/` - Submit feedback
- `/feedback/thanks/` - Confirmation
- `/feedback/results/` - View results

**AI Assistant Feedback:**
- `ai_assistant_feedback_api` - API endpoint for AI assistant feedback
- AI learning and improvement tracking

#### ❌ What is MISSING

**Database Models:**
1. **Resident Experience Feedback**
   - Resident satisfaction surveys
   - Family feedback
   - Compliments and complaints
   - Care plan involvement tracking
   
2. **Staff Feedback**
   - Staff satisfaction surveys
   - Anonymous suggestion box
   - Exit interviews
   - Team feedback
   
3. **Complaint Management**
   - Formal complaint logging
   - Investigation tracking
   - Resolution and learning
   - SPSO (Scottish Public Services Ombudsman) compliance
   
4. **Feedback Themes & Trends**
   - Sentiment analysis
   - Theme categorization
   - Action tracking from feedback

**Views:**
1. Resident/family feedback portal
2. Staff feedback portal
3. Complaint management workflow
4. Feedback analytics dashboard
5. Action tracking from feedback
6. Sentiment trend analysis

**Templates:**
1. Resident satisfaction survey (mobile-friendly)
2. Family feedback form
3. Staff satisfaction survey
4. Complaint submission form
5. Complaint investigation tracker
6. Feedback analytics dashboard
7. Action plan from feedback

**Integration:**
1. Link to PDSA projects (feedback → improvement projects)
2. Link to incident management (complaints → incidents)
3. Link to training (feedback themes → training needs)
4. Care Inspectorate quality indicators

**ML/AI Features:**
1. Sentiment analysis on free-text feedback
2. Automatic theme extraction
3. Feedback priority scoring
4. Improvement suggestion generator

### Implementation Priority: **P2 (Medium)**

**Estimated Effort:** 2.5 weeks  
**Dependencies:** Module 1 (PDSA) for improvement linkage  
**Regulatory Impact:** Medium (Care Inspectorate quality indicators)  

---

## MODULE 4: TRAINING & COMPETENCY (50% Complete)

### Current State Analysis

#### ✅ What EXISTS

**Database Models** (`scheduling/models.py` lines 765-870):
```python
class TrainingCourse(models.Model):
    # Course Details
    name                    # Course name
    category               # ESSENTIAL, PERSON_CENTRED, CLINICAL, SPECIALIST
    description            # Text
    frequency              # ANNUAL, 2_YEAR, 3_YEAR, ONCE
    validity_months        # Expiry period
    is_mandatory           # Boolean
    requires_competency_assessment  # Boolean
    requires_certificate   # Boolean
    minimum_hours          # Decimal
    
    # SSSC CPD
    sssc_cpd_eligible      # Boolean
    sssc_cpd_hours         # Decimal
    
class TrainingRecord(models.Model):
    # Core Fields
    staff_member           # FK to User
    course                 # FK to TrainingCourse
    completion_date        # Date
    expiry_date           # Date
    
    # Training Details
    trainer_name          # Text
    training_provider     # Text
    certificate_number    # Text
    certificate_file      # File upload
    
    # Competency Assessment
    competency_assessed   # Boolean
    competency_assessor   # FK to User
    competency_date       # Date
    competency_outcome    # COMPETENT, NOT_YET_COMPETENT
    
    # SSSC CPD
    sssc_cpd_hours_claimed  # Decimal
    
    # Methods
    get_status()           # CURRENT, EXPIRING_SOON, EXPIRED
    days_until_expiry()    # Calculate days remaining
```

**Views** (Partial):
- `training_compliance_view()` - Dashboard view
- Training summary in manager dashboard
- Training breakdown reports

**Templates** (7 templates):
- `compliance/training_compliance_dashboard.html` - Dashboard
- `compliance/my_training_dashboard.html` - Staff view
- `compliance/submit_training_record.html` - Add record
- `compliance/add_staff_training_record.html` - Manager adds for staff
- `compliance/training_breakdown_report.html` - Reports

**URLs:**
- `/compliance/training/` - Main training dashboard
- Training record APIs

**Scripts:**
- `add_mandatory_training_courses.py` - Populate courses
- `populate_sample_training_records.py` - Generate sample data

#### ❌ What is MISSING

**Database Models:**
1. **Competency Framework**
   - Role-specific competency matrices
   - Skill levels (Novice, Competent, Proficient, Expert)
   - Competency verification workflows
   
2. **Training Needs Analysis**
   - Individual training plans
   - Team training gaps
   - Automatic training scheduling
   
3. **Induction Tracking** (Partial exists - `InductionProgress` model)
   - Enhanced induction workflow
   - Induction checklist completion
   - Probation review linkage
   
4. **Training Matrix**
   - Who needs what training
   - Compliance forecasting
   - Training budget planning

**Views:**
1. Training matrix view (grid of staff × courses)
2. Competency assessment workflow
3. Training needs analysis dashboard
4. Automatic training renewal reminders
5. Training budget and planning
6. SSSC registration tracking
7. Induction progress tracker (enhanced)
8. Training certificate verification

**Templates:**
1. Training matrix (visual grid)
2. Competency assessment form
3. Training plan creation
4. Training calendar
5. Training budget dashboard
6. SSSC CPD tracker
7. Induction checklist (enhanced)
8. Training reminder emails

**Integration:**
1. Link to incidents (incident → training need identified)
2. Link to supervision (supervision → training needs)
3. Link to PDSA (training effectiveness projects)
4. Link to staffing (training gaps affect shift allocation)

**ML/AI Features:**
1. Training need prediction
2. Competency gap analysis
3. Training effectiveness scoring
4. Optimal training scheduling

### Implementation Priority: **P1 (High)**

**Estimated Effort:** 3.5 weeks  
**Dependencies:** None (standalone but integrates with Module 2)  
**Regulatory Impact:** High (SSSC, Care Inspectorate mandatory)  

---

## MODULE 5: DOCUMENT & POLICY MANAGEMENT (0% Complete)

### Current State Analysis

#### ✅ What EXISTS
**Nothing** - This module is not started.

#### ❌ What is MISSING

**Database Models:**
1. **Policy Document**
   - Title, version, category
   - Review cycle
   - Approval workflow
   - Distribution tracking
   
2. **Policy Review**
   - Review due dates
   - Review assignments
   - Version control
   - Change tracking
   
3. **Document Access Log**
   - Who accessed what document
   - Acknowledgment tracking
   - Training linkage (read policy → training complete)
   
4. **Document Category**
   - Care Inspectorate themes
   - Statutory vs internal policies
   - Document hierarchy

**Views:**
1. Policy library
2. Policy review workflow
3. Staff acknowledgment tracking
4. Document search and filter
5. Version comparison
6. Policy approval workflow

**Templates:**
1. Policy library homepage
2. Policy detail view
3. Policy review form
4. Acknowledgment tracker
5. Document search results
6. Policy approval interface

**Integration:**
1. Link to training (policy updates → training requirement)
2. Link to incidents (incident → policy review trigger)
3. Link to Care Inspectorate evidence repository
4. Link to induction (new staff must read key policies)

**ML/AI Features:**
1. Policy chatbot (answer questions from policies)
2. Policy gap analysis
3. Review prioritization

### Implementation Priority: **P3 (Low)**

**Estimated Effort:** 2 weeks  
**Dependencies:** None  
**Regulatory Impact:** Medium (Care Inspectorate evidence)  

---

## MODULE 6: RISK MANAGEMENT (0% Complete)

### Current State Analysis

#### ✅ What EXISTS
**Nothing** - This module is not started.

#### ❌ What is MISSING

**Database Models:**
1. **Risk Register**
   - Risk description
   - Category (clinical, operational, financial, reputational)
   - Likelihood and impact scores
   - Risk rating matrix
   - Control measures
   
2. **Risk Assessment**
   - Individual resident risk assessments
   - Environmental risk assessments
   - Moving & handling assessments
   
3. **Risk Mitigation Action**
   - Action to reduce risk
   - Ownership
   - Due dates
   - Effectiveness review
   
4. **Risk Review History**
   - Risk score changes over time
   - Control effectiveness tracking

**Views:**
1. Risk register dashboard
2. Risk assessment workflow
3. Risk matrix visualization (heat map)
4. Risk mitigation tracker
5. Risk reporting
6. Environmental risk assessments

**Templates:**
1. Risk register
2. Risk assessment form
3. Risk matrix (visual)
4. Mitigation action tracker
5. Risk reports
6. Risk trend analysis

**Integration:**
1. Link to incidents (incidents → risk register)
2. Link to PDSA (risk mitigation projects)
3. Link to staffing (staffing levels = risk factor)
4. Care Inspectorate reporting

**ML/AI Features:**
1. Risk prediction models
2. Automated risk scoring
3. Control effectiveness analysis

### Implementation Priority: **P2 (Medium)**

**Estimated Effort:** 2.5 weeks  
**Dependencies:** Module 2 (incidents inform risks)  
**Regulatory Impact:** Medium (Care Inspectorate expects risk management)  

---

## MODULE 7: PERFORMANCE ANALYTICS & EXECUTIVE DASHBOARDS (40% Complete)

### Current State Analysis

#### ✅ What EXISTS

**Executive Dashboard:**
- `/scheduling/executive-dashboard/` - Main executive view
- Key metrics display
- Home performance summaries

**Analytics Views:**
- Staffing analytics in manager dashboard
- Leave usage tracking
- Overtime tracking
- Budget analytics

**Charts:**
- Chart.js integration
- Various dashboard visualizations

**ML Components:**
- Demand forecasting
- Leave prediction
- Cost forecasting
- Shift optimization

#### ❌ What is MISSING

**Database Models:**
1. **Performance KPI**
   - KPI definition
   - Target values
   - Actual values
   - Variance tracking
   
2. **Dashboard Widget Configuration**
   - User-customizable dashboards
   - Widget library
   - Layout preferences
   
3. **Automated Report Schedule**
   - Report templates
   - Distribution lists
   - Generation schedule

**Views:**
1. Quality KPI dashboard (CI quality indicators)
2. Custom report builder
3. Benchmark comparisons (home vs home)
4. Executive summary generator
5. Board report automation
6. Drill-down analytics
7. Predictive analytics dashboard

**Templates:**
1. Enhanced executive dashboard
2. Quality indicators dashboard
3. Benchmark comparison view
4. Custom report builder
5. Automated report templates
6. Predictive analytics view

**Integration:**
1. All modules feed into analytics
2. PDSA project outcomes → performance metrics
3. Incident rates → quality indicators
4. Training compliance → CI ratings
5. Feedback themes → improvement areas

**ML/AI Features:**
1. Predictive quality ratings
2. Benchmark intelligence
3. Anomaly detection
4. What-if scenario modeling

### Implementation Priority: **P1 (High)**

**Estimated Effort:** 4 weeks  
**Dependencies:** All other modules (analytics aggregates everything)  
**Regulatory Impact:** High (Board reporting, CI inspections)  

---

## IMPLEMENTATION ROADMAP

### Phase 1: High-Priority Modules (Weeks 1-8)

**Week 1-3: Module 2 - Incident & Safety Management**
- Week 1: Database models (RCA, CAPA, Duty of Candour)
- Week 2: Views and workflows
- Week 3: Templates and testing

**Week 4-7: Module 4 - Training & Competency**
- Week 4-5: Database models (competency framework, training matrix)
- Week 6: Views and workflows
- Week 7: Templates and integration

**Week 8: Module 7 Enhancement - Analytics Foundation**
- Create KPI models
- Build quality indicators dashboard
- Test integration with Modules 1, 2, 4

### Phase 2: Medium-Priority Modules (Weeks 9-14)

**Week 9-11: Module 3 - Experience & Feedback**
- Week 9: Database models (complaints, surveys)
- Week 10: Views and workflows
- Week 11: Templates and sentiment analysis

**Week 12-14: Module 6 - Risk Management**
- Week 12: Database models (risk register)
- Week 13: Views and workflows
- Week 14: Templates and risk matrix

### Phase 3: Low-Priority & Finalization (Weeks 15-18)

**Week 15-16: Module 5 - Document & Policy Management**
- Week 15: Database models
- Week 16: Views, templates, integration

**Week 17-18: Module 7 Completion - Advanced Analytics**
- Custom report builder
- Predictive analytics
- Benchmark comparisons
- Final integration testing

---

## DATABASE MIGRATION STRATEGY

### PostgreSQL Migration Plan

**Current State:**
- Local: SQLite (empty db.sqlite3, db_backup_DEMO.sqlite3 has data)
- Production: PostgreSQL (DigitalOcean 159.65.18.80)

**Strategy:**
1. **Develop locally** with SQLite
2. **Test migrations** on local SQLite
3. **Export/import** sample data to PostgreSQL test instance
4. **Deploy to production** PostgreSQL after thorough testing

**PostgreSQL Advantages for TQM:**
- JSON field support (better for incident data, feedback themes)
- Full-text search (policy documents, lessons learned)
- Complex queries (analytics across multiple modules)
- Concurrent access (multiple users reporting incidents)
- Compliance audit trails

---

## IMPLEMENTATION EFFORT ESTIMATE

| Module | Priority | Weeks | Dependencies | Completion % | Remaining Work |
|--------|----------|-------|--------------|--------------|----------------|
| Module 1 | P1 | - | None | 100% | ✅ Complete |
| Module 2 | P1 | 3 | Module 1 | 45% | 55% (RCA, CAPA, Duty of Candour) |
| Module 3 | P2 | 2.5 | Module 1 | 30% | 70% (Surveys, Complaints, Sentiment) |
| Module 4 | P1 | 3.5 | None | 50% | 50% (Competency, Matrix, Planning) |
| Module 5 | P3 | 2 | None | 0% | 100% (Full implementation) |
| Module 6 | P2 | 2.5 | Module 2 | 0% | 100% (Full implementation) |
| Module 7 | P1 | 4 | All | 40% | 60% (KPIs, Reports, Predictive) |
| **TOTAL** | - | **17.5 weeks** | - | **38%** | **62%** |

**Timeline:** Q1-Q2 2026 (January - May 2026)  
**Team:** 1-2 developers  
**Testing:** Continuous local testing, demo environment only  
**Production Deployment:** After full local validation  

---

## SUCCESS CRITERIA

### Module 2 Success Criteria
- [ ] All incident types captured with proper workflows
- [ ] Root cause analysis for high-severity incidents
- [ ] CAPA tracking with 100% closure rate
- [ ] Duty of Candour compliance for all applicable incidents
- [ ] Integration with PDSA for improvement projects
- [ ] Care Inspectorate notifications automated

### Module 4 Success Criteria
- [ ] 100% training compliance visibility
- [ ] Automated training renewal reminders
- [ ] Competency assessment workflows
- [ ] SSSC CPD hour tracking
- [ ] Training matrix shows all gaps
- [ ] Integration with incidents for training needs

### Module 7 Success Criteria
- [ ] Real-time KPI dashboards
- [ ] Automated board reports
- [ ] Predictive analytics operational
- [ ] Benchmark comparisons across homes
- [ ] Drill-down capabilities to source data
- [ ] Mobile-responsive dashboards

---

## NEXT STEPS

### Immediate Actions (Today - Week 1)

1. **✅ Complete this assessment document**
2. **Set up Module 2 Django app**
   - Create `incident_safety/` app directory
   - Add to INSTALLED_APPS
   - Create initial models (RCA, CAPA, DutyOfCandour)
3. **Set up Module 4 enhancements**
   - Extend TrainingCourse model
   - Create CompetencyFramework model
   - Create TrainingMatrix model
4. **Create migration files**
   - Test migrations on local SQLite
   - Document schema changes
5. **Begin Module 2 views**
   - Incident workflow views
   - Investigation assignment
   - RCA documentation

### This Week Priorities

- [ ] Complete Module 2 database models
- [ ] Create Module 2 admin interface
- [ ] Build incident investigation workflow
- [ ] Create RCA template
- [ ] Test with sample incident data

---

## APPENDIX A: EXISTING CODE INVENTORY

### Module 2 (Incident & Safety) - Existing Code
- **Model:** `scheduling/models.py` class `IncidentReport` (lines 1120-1210)
- **Templates:** 4 files in `scheduling/templates/compliance/`
  - `report_incident.html`
  - `view_incident.html`
  - `incident_management.html`
  - `my_incident_reports.html`
- **Views:** Partial in `scheduling/views.py`
- **URLs:** Partial in `scheduling/urls.py`

### Module 4 (Training) - Existing Code
- **Models:** `scheduling/models.py` (lines 765-870)
  - `class TrainingCourse`
  - `class TrainingRecord`
  - `class InductionProgress`
- **Templates:** 7 files in `scheduling/templates/compliance/`
  - `training_compliance_dashboard.html`
  - `my_training_dashboard.html`
  - `submit_training_record.html`
  - `add_staff_training_record.html`
  - `training_breakdown_report.html`
- **Views:** `training_compliance_view()` in `scheduling/views.py`
- **Scripts:**
  - `add_mandatory_training_courses.py`
  - `populate_sample_training_records.py`

### Module 3 (Feedback) - Existing Code
- **Templates:** 4 files in `scheduling/templates/scheduling/`
  - `demo_feedback.html`
  - `feedback_widget.html`
  - `demo_feedback_thanks.html`
  - `feedback_results.html`
- **Views:** 3 functions in `scheduling/views.py`
  - `demo_feedback()`
  - `demo_feedback_thanks()`
  - `view_feedback_results()`
- **URLs:** `/feedback/` routes

### Module 7 (Analytics) - Existing Code
- **Executive Dashboard:** `/scheduling/executive-dashboard/`
- **ML Components:** `scheduling/ml/` directory
  - Demand forecasting
  - Leave prediction
  - Cost forecasting
- **Charts:** Chart.js integration in templates

---

## APPENDIX B: REGULATORY ALIGNMENT

### Care Inspectorate Quality Framework

**Module Mapping:**

| CI Quality Indicator | Primary Module | Secondary Modules |
|---------------------|----------------|-------------------|
| **1.1 People experience compassion, dignity and respect** | Module 3 (Feedback) | Module 1 (PDSA) |
| **1.2 People's rights are protected** | Module 2 (Incidents), Module 5 (Policies) | Module 6 (Risk) |
| **2.1 People are safe and protected from harm** | Module 2 (Incidents), Module 6 (Risk) | Module 4 (Training) |
| **3.1 People's health and wellbeing benefit from the care** | Module 1 (PDSA), Module 7 (Analytics) | All modules |
| **4.1 Staff skills and knowledge meet people's needs** | Module 4 (Training) | Module 2, Module 3 |
| **5.1 Leadership and management support effective care** | Module 7 (Analytics) | All modules |

---

## VERSION HISTORY

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 14 Jan 2026 | Initial assessment document created | GitHub Copilot |

---

**END OF ASSESSMENT DOCUMENT**
