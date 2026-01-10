# Phase 3: Health Improvement Scotland (HIS) Quality Management Systems Integration
**Date:** January 10, 2026  
**Project:** Digital Staff Rota & Quality Management System  
**Purpose:** Integrate HIS Quality Management Systems (QMS) framework principles into system design and TQM module planning

---

## HIS Quality Management Systems Framework Overview

**Source:** [Health Improvement Scotland - Quality Management Systems](https://www.healthcareimprovementscotland.scot/improving-care/improvement-resources/)

### **What is a Quality Management System?**

A Quality Management System (QMS) is defined by HIS as:
> *"A formalized system that documents processes, procedures, and responsibilities for achieving quality policies and objectives. A QMS helps coordinate and direct an organization's activities to meet customer and regulatory requirements and improve its effectiveness and efficiency on a continuous basis."*

### **Core QMS Principles from HIS:**

1. **Leadership Commitment** - Senior management drives quality culture
2. **Person-Centered Approach** - People receiving care are at the heart of all decisions
3. **Process-Based Thinking** - Understanding and managing interrelated processes
4. **Evidence-Based Decision Making** - Data and information drive improvements
5. **Continuous Improvement** - Systematic approach to enhancing quality (PDSA cycles)
6. **Risk-Based Thinking** - Proactive identification and mitigation of quality risks
7. **Relationship Management** - Effective stakeholder engagement and partnership working

---

## HIS QMS Cycle: Plan-Do-Study-Act (PDSA)

The HIS framework emphasizes the PDSA improvement cycle:

### **PLAN** - Identify improvement opportunity and develop plan
- What are we trying to accomplish?
- How will we know a change is an improvement?
- What changes can we make that will result in improvement?

### **DO** - Implement the plan on a small scale
- Carry out the test
- Document problems and unexpected observations
- Begin analysis of data

### **STUDY** - Analyze results and compare to predictions
- Complete data analysis
- Compare results to predictions
- Summarize learning

### **ACT** - Refine the change or expand implementation
- Determine what modifications should be made
- Prepare plan for next cycle (or implementation)
- Decide whether to abandon, adapt, or adopt

---

## Current Staff Rota System → HIS QMS Principles Mapping

### **1. Leadership Commitment**

**HIS Principle:** *"Quality is a strategic priority requiring active senior management engagement, not delegated to quality departments alone."*

**Current System Alignment:**

✅ **Executive Dashboard Suite (13 Reports):**
- CI Performance Dashboard with actual inspection data (CS numbers, ratings, benchmarking)
- Traffic light indicators for at-a-glance quality oversight
- 0-100 scoring enables board-level quality discussions
- **Evidence:** Automated email digests (daily/weekly/monthly) keep leadership informed

✅ **Data-Driven Strategic Decisions:**
- ML forecasting (Prophet 25.1% MAPE) supports workforce planning at executive level
- £590K ROI quantified across 6 categories provides business case for quality investment
- Retention analytics (preventing 6 departures/year = £120K) demonstrates leadership impact
- **Evidence:** Head of Service role included in design team (DLP Charter)

✅ **Digital Lead/Executive Sponsor:**
- DLP Project Charter identifies executive sponsorship role
- Leadership support section documented with responsibilities
- **Evidence:** Strategic alignment section links to organizational 3-5 year plan

**HIS QMS Enhancement Opportunities:**
- 📋 **Quality Governance Dashboard:** Board-level quality metrics aligned with HIS QMS KPIs
- 📋 **Leadership Quality Walkrounds:** Schedule and track executive rounding (visibility + engagement)
- 📋 **Quality Strategy Tracker:** Link system metrics to organizational quality improvement plan
- 📋 **Senior Management QMS Training:** Track leadership participation in quality improvement learning

---

### **2. Person-Centered Approach**

**HIS Principle:** *"People receiving care and their families are active partners in planning, delivering, and improving services."*

**Current System Alignment:**

✅ **Staff as Service Users (Person-Centered Employment):**
- Fair shift allocation algorithms reduce perceived bias → dignity and respect for staff
- Self-service portal empowers staff autonomy (85% mobile adoption)
- Transparent leave approval reduces power imbalances
- AI assistant provides 24/7 support without judgment
- **Evidence:** 88% baseline dissatisfaction → 85% satisfaction target demonstrates person-centered design

✅ **Scottish Approach to Service Design (SAtSD) Integration:**
- 7 principles embedded: problem exploration, design around people, user participation from day one
- Double Diamond methodology (Discover ✅, Define ✅, Develop ✅, Deliver ⏳)
- Co-design with 9 OMs, 5 SMs, Families Council representatives
- **Evidence:** DLP Charter documents SAtSD as primary framework

✅ **Indirect Support for Resident-Centered Care:**
- 88% administrative burden reduction frees manager time for resident relationships
- Consistent staffing (reduced turnover) enables familiar care relationships
- Safe staffing ratios prevent rushed, task-focused care
- **Evidence:** 23% error rate → <1% ensures adequate staffing for person-centered time

**HIS QMS Enhancement Opportunities:**
- 📋 **Resident/Family Feedback Module (TQM):** Direct voice of people receiving care
  - Person-centered care surveys aligned with HIS person-led care principles
  - Complaint and compliment tracking
  - Integration with "Can I Help You?" Scottish Government initiative
  - Family involvement in care planning (system-supported)
- 📋 **Resident Preference Matching:** Algorithm considers resident-staff relationship preferences
- 📋 **Care Plan Integration:** API links to existing care planning systems for holistic view
- 📋 **Meaningful Activities Tracking:** Outcomes measurement for "what matters to you"

---

### **3. Process-Based Thinking**

**HIS Principle:** *"Understanding that desired outcomes are achieved through interconnected processes, not isolated activities."*

**Current System Alignment:**

✅ **Integrated Workflow Processes:**
- Rota creation → Leave approval → Absence management → Training compliance → Reporting (end-to-end)
- Each process feeds the next (e.g., leave approvals automatically update rota, training gaps trigger alerts)
- **Evidence:** 18 integrated features demonstrating process connectivity

✅ **Cross-Functional Process Mapping:**
- Multi-role integration: OM, SM, HOS, HR, Finance, Training Coordinator, Staff
- 14 distinct roles with defined responsibilities and permissions
- **Evidence:** Role-based access control reflects process ownership

✅ **Process Documentation:**
- 36 guidance documents organized by category (Staff Procedures, Manager Guidance, SOPs)
- Searchable knowledge base with role-based access
- **Evidence:** 7 staff procedures, 10 manager guides, 7 SOPs, 4 CI resources, 5 system guides

✅ **Process Performance Metrics:**
- 777ms average response time (production validated)
- 115 req/s throughput under 300 concurrent users
- 0% error rate demonstrates process reliability
- **Evidence:** 69-test ML validation suite ensures process quality

**HIS QMS Enhancement Opportunities:**
- 📋 **Process Mapping Visualization:** Flowcharts showing interconnected workflows
- 📋 **Process Ownership Matrix:** RACI chart (Responsible, Accountable, Consulted, Informed) for each process
- 📋 **Process Audit Schedule:** Regular review cycles for process effectiveness
- 📋 **Process Improvement Log:** Track PDSA cycles for each core process

---

### **4. Evidence-Based Decision Making**

**HIS Principle:** *"Decisions based on analysis of data and information lead to better outcomes than intuition alone."*

**Current System Alignment:**

✅ **Comprehensive Data Analytics:**
- ML forecasting (Prophet) with 25.1% MAPE for demand prediction
- Linear programming optimization achieving 12.6% cost reduction
- 6 Chart.js visualizations (staffing trends, sickness comparison, incident severity, leave patterns, staff distribution, ML forecasts)
- **Evidence:** Data science rigor with 80% confidence intervals and validated models

✅ **Real-Time Operational Intelligence:**
- Dashboard speedup (6.7× faster: 180ms vs 1200ms) enables immediate data access
- Live staffing levels vs. required ratios
- Training compliance status with 30-day expiry alerts
- **Evidence:** Real-time decision support vs. retrospective manual analysis

✅ **Quantified Baseline and Outcomes:**
- Baseline: 15,756 hrs/year burden, £587,340 cost, 23% error rate
- Outcomes: 88% reduction, £590K savings, 24,500% ROI
- **Evidence:** Academic paper with 6,940 lines of research validation

✅ **Automated Compliance Reporting:**
- 13 executive reports with objective metrics (traffic lights, 0-100 scoring)
- CI Performance Dashboard with actual inspection data
- Training matrices eliminating manual compilation
- **Evidence:** 40 hours inspection prep → 8 hours (80% reduction)

**HIS QMS Enhancement Opportunities:**
- 📋 **Quality Metrics Library:** Pre-configured KPIs aligned with HIS quality indicators
- 📋 **Benchmarking Module:** Compare performance across homes and against sector averages
- 📋 **Statistical Process Control (SPC) Charts:** Run charts, control charts for trend analysis
- 📋 **Evidence Repository:** Centralized location for all quality improvement evidence

---

### **5. Continuous Improvement (PDSA Cycles)**

**HIS Principle:** *"Organizations committed to systematic quality improvement using structured methodologies (PDSA) achieve sustained gains."*

**Current System Alignment:**

✅ **Development Methodology:**
- 5 agile phases over 270 hours demonstrating iterative improvement
- User feedback loops with 1,352 users providing real-world testing
- Production deployment with continuous enhancement (Phase 2 ongoing)
- **Evidence:** Weekly rota grid alignment deferred but tracked for future iteration

✅ **User-Driven Iteration:**
- AI assistant query analytics (200+ patterns) reveal improvement opportunities
- Mobile adoption tracking (85% within 3 months) measures change effectiveness
- Shift swap rate (18% weekly) indicates engagement with new processes
- **Evidence:** SAtSD principle 5: continuous feedback informs design

✅ **Performance Monitoring for Improvement:**
- System analytics tracking login frequency, feature usage, error logs
- Performance profiling enabling targeted optimization (3.1× Prophet training acceleration)
- **Evidence:** 6.7× dashboard speedup shows commitment to user experience improvement

**HIS QMS Enhancement Opportunities:**
- 📋 **PDSA Tracker Module:** Structured improvement project management
  - Templates for PLAN (aim, measures, changes)
  - DO (test documentation, data collection)
  - STUDY (analysis, comparison to predictions)
  - ACT (refinement decisions, next steps)
- 📋 **Quality Improvement Register:** Log all active improvement initiatives
- 📋 **Lessons Learned Repository:** Share successful change ideas across homes
- 📋 **Improvement Capability Building:** Track staff participation in quality improvement training

---

### **6. Risk-Based Thinking**

**HIS Principle:** *"Proactive identification and mitigation of risks to quality prevents harm and improves outcomes."*

**Current System Alignment:**

✅ **Comprehensive Risk Register (DLP Charter):**
- 12 identified risks with impact/likelihood/mitigation strategies:
  - User resistance to change (High/Medium) → Mitigation: Early involvement, champions, training
  - Technical issues/downtime (High/Low-Medium) → Mitigation: 99.5% SLA, 24/7 monitoring, backups
  - Data security breach (Very High/Low) → Mitigation: Security audits, encryption, GDPR compliance
  - Regulatory framework changes (Medium/Medium) → Mitigation: Flexible architecture, monitoring
  - Budget constraints (Medium/Medium) → Mitigation: Phased rollout, ROI demonstration
  - Integration challenges (Medium/High) → Mitigation: API-first, interim processes
  - Digital skills gap (Medium/Medium) → Mitigation: Multi-format training, super-users
  - Scope creep (Medium/High) → Mitigation: Change control, parking lot
  - Competitor solutions (Low-Medium/Medium) → Mitigation: Scottish focus, integrated platform
  - Key person dependency (High/Medium) → Mitigation: Documentation, knowledge transfer
  - Inspection failure (High/Low) → Mitigation: Pre-inspection evidence gathering, expert review
  - Network connectivity (Medium/Medium) → Mitigation: Offline features, contingency procedures
- **Evidence:** Structured risk management approach documented in charter

✅ **Proactive Compliance Alerts:**
- Training expiry 30-day warnings prevent lapsed certifications
- Real-time staffing ratio alerts prevent unsafe coverage
- Automated leave balance tracking prevents approval errors
- **Evidence:** 15% lapsed training (baseline) → 0% (automated alerts)

✅ **Audit Trail for Accountability:**
- All schedule changes logged with user/timestamp
- Approval workflows documented
- System access and data modifications tracked
- **Evidence:** Regulatory-grade audit trail demonstrates risk control

**HIS QMS Enhancement Opportunities:**
- 📋 **Risk Management Module (TQM):**
  - Risk register with likelihood × impact matrices
  - Control measures tracking and effectiveness monitoring
  - Risk review scheduling aligned with HIS QMS cycles
  - Integration with incident management for trend identification
  - Board-level risk reporting dashboard
- 📋 **Early Warning System:** Predictive alerts for quality deterioration (e.g., rising incident rates, falling satisfaction)
- 📋 **Business Continuity Planning:** Disaster recovery procedures, backup systems
- 📋 **Horizon Scanning:** Monitor regulatory and sector changes proactively

---

### **7. Relationship Management**

**HIS Principle:** *"Effective engagement with stakeholders (staff, people receiving care, regulators, partners) drives quality improvement."*

**Current System Alignment:**

✅ **Multi-Stakeholder Engagement:**
- Design team includes: 9 OMs, 5 SMs, frontline SCWs, Families Council, IT, Quality Manager, Finance, Digital Lead
- NES DLP advisors providing methodology guidance
- Care Inspectorate liaison for regulatory framework alignment
- **Evidence:** DLP Charter participation section documents diverse engagement

✅ **Staff Engagement Mechanisms:**
- Monthly user feedback sessions (planned ongoing activities)
- Annual satisfaction surveys (SAtSD Principle 3 & 7)
- AI assistant query analytics revealing staff needs
- **Evidence:** 85% mobile adoption demonstrates successful staff engagement

✅ **Regulatory Relationship:**
- CI Performance Dashboard facilitates constructive inspector conversations
- Automated evidence generation demonstrates transparency and cooperation
- Early engagement on evidence requirements (inspection readiness planning)
- **Evidence:** Gap analysis and pre-inspection preparation approach

✅ **Partnership Working:**
- NES Digital Learning Programme submission demonstrates collaborative approach
- Scottish Approach to Service Design alignment shows commitment to national frameworks
- HIS/NES/Care Inspectorate framework integration evidences sector partnership
- **Evidence:** DLP Charter strategic alignment section

**HIS QMS Enhancement Opportunities:**
- 📋 **Stakeholder Engagement Log:** Track meetings, feedback, actions with external partners
- 📋 **Partnership Dashboard:** Visualize collaborative projects and shared outcomes
- 📋 **Sector Benchmarking Consortium:** Multi-organization data sharing for mutual learning
- 📋 **Regulatory Communication Portal:** Centralized location for all CI/SSSC/HIS correspondence
- 📋 **Families Council Integration:** Direct portal access for resident advocates

---

## HIS QMS Implementation Roadmap for Staff Rota System

### **Phase 3B: HIS QMS Quick Wins (Q1 2026)**

**1. QMS Principles Alignment Documentation**
- ✅ Create mapping document (this document) showing current alignment
- 📋 Develop "HIS QMS User Guide" for managers explaining how system supports quality management
- 📋 Add HIS QMS principles to staff training materials

**2. Leadership Visibility Enhancement**
- 📋 Expand executive dashboard with HIS-aligned quality metrics
- 📋 Create board reporting template linking system data to quality strategy
- 📋 Schedule quarterly leadership quality reviews using system data

**3. Evidence-Based Decision Making Toolkit**
- 📋 Pre-built report templates for each HIS quality domain
- 📋 Statistical analysis tools (trends, variations, correlations)
- 📋 Data visualization library for quality presentations

---

### **Phase 3C: TQM Modules with HIS QMS Integration (Q2-Q4 2026)**

**Module 1: Quality Audits & Inspections** (Q2 2026)
- **HIS QMS Alignment:**
  - **Leadership Commitment:** Senior management audit scheduling oversight
  - **Process-Based Thinking:** Audit protocols for interconnected processes
  - **Evidence-Based Decisions:** Data-driven audit findings
  - **Continuous Improvement:** Corrective action PDSA cycles
  - **Risk-Based Thinking:** Audit frequency based on risk assessment

- **Features:**
  - Scheduled audit calendar aligned with Care Inspectorate cycles
  - Compliance checklists using HIS quality indicators
  - Findings categorization (strengths, areas for improvement, requirements)
  - Corrective action planning with PDSA templates
  - Trend analysis across audits
  - Evidence repository for inspection readiness

**Module 2: Incident Management** (Q3 2026)
- **HIS QMS Alignment:**
  - **Person-Centered:** Duty of Candour - transparent communication with families
  - **Evidence-Based:** Root cause analysis using data and investigation
  - **Continuous Improvement:** Learning from incidents via PDSA
  - **Risk-Based Thinking:** Proactive risk identification from incident trends
  - **Relationship Management:** Staff involvement in improvement solutions

- **Features:**
  - Scottish Patient Safety Programme (SPSP) aligned reporting
  - Root cause analysis tools from NES QI Zone
  - Significant adverse event management protocols
  - Duty of Candour compliance tracking and documentation
  - Trend analysis linking incidents to staffing patterns
  - Corrective action tracking with effectiveness monitoring
  - Lessons learned library

**Module 3: Training & Competency** (Q4 2026)
- **HIS QMS Alignment:**
  - **Evidence-Based:** Competency assessments drive training priorities
  - **Continuous Improvement:** CPD tracking for ongoing skill development
  - **Risk-Based:** Training gaps identified proactively
  - **Relationship Management:** SSSC partnership for registration compliance

- **Features:**
  - Enhanced competency assessment tools beyond basic tracking
  - Skills matrices by role and unit
  - CPD logs for SSSC registration requirements
  - Skills gap analysis with training prioritization
  - Integration with NES Quality Improvement Zone learning resources
  - Training impact measurement (pre/post competency scores)
  - Supervision and induction tracking with QMS alignment

**Module 4: Document Control** (Q4 2026)
- **HIS QMS Alignment:**
  - **Process-Based:** Version control ensures process consistency
  - **Evidence-Based:** Audit trail of policy changes and staff acknowledgment
  - **Risk-Based:** Outdated guidance identified and updated
  - **Relationship Management:** Links to national guidance (HIS, SSSC, Scottish Gov)

- **Features:**
  - Policy and procedure lifecycle management
  - Version control with approval workflows
  - Expiry tracking and renewal alerts
  - Staff acknowledgment and understanding testing
  - Links to HIS, SSSC, Scottish Government national guidance
  - Document library organized by Care Inspectorate themes

**Module 5: Risk Management** (2027)
- **HIS QMS Alignment:**
  - **Risk-Based Thinking:** Systematic risk identification and mitigation
  - **Leadership Commitment:** Board-level risk oversight
  - **Evidence-Based:** Risk controls monitored for effectiveness
  - **Continuous Improvement:** Risk reviews inform quality improvements

- **Features:**
  - Organizational risk register (clinical, operational, reputational, financial)
  - Likelihood × impact matrices
  - Control measures tracking with effectiveness ratings
  - Risk review scheduling aligned with HIS QMS cycles
  - Integration with incident management for trend identification
  - Board-level risk reporting dashboard

**Module 6: Performance Metrics & KPIs** (2027)
- **HIS QMS Alignment:**
  - **Evidence-Based Decisions:** Real-time quality metrics inform actions
  - **Leadership Commitment:** Board KPI dashboards
  - **Continuous Improvement:** Track PDSA cycle effectiveness
  - **Relationship Management:** Benchmarking with peer organizations

- **Features:**
  - Pre-configured HIS quality indicators
  - National Health & Wellbeing Outcomes alignment
  - Custom metric builder for service-specific KPIs
  - Benchmarking against Care Inspectorate quality themes
  - Statistical Process Control (SPC) charts
  - Automated board and regulatory reporting
  - Real-time quality improvement tracking

**Module 7: Feedback & Complaints** (2027)
- **HIS QMS Alignment:**
  - **Person-Centered:** Voice of people receiving care drives improvement
  - **Continuous Improvement:** Feedback informs PDSA cycles
  - **Relationship Management:** Transparent communication with families
  - **Evidence-Based:** Complaint trends identify systemic issues

- **Features:**
  - Resident/family satisfaction surveys (person-led care principles)
  - Complaint logging, investigation, and resolution tracking
  - Compliment tracking for positive reinforcement
  - Trend analysis and learning
  - Integration with "Can I Help You?" Scottish Government initiative
  - Annual feedback reporting for Care Inspectorate
  - Duty of Candour linkage

---

## HIS QMS Compliance Checklist for Current System

### **Leadership and Accountability**
- ✅ Executive dashboards provide senior management oversight
- ✅ Quality metrics quantified (£590K ROI, 88% burden reduction)
- ✅ Strategic alignment documented (DLP Charter)
- ⏳ Board-level quality governance meetings scheduled (planned)
- ⏳ Leadership quality walkrounds tracked (future enhancement)

### **Person-Centered Care**
- ✅ SAtSD framework integration (7 principles, Double Diamond)
- ✅ Co-design with service users (staff) and families
- ✅ Staff empowerment through self-service and transparency
- 📋 Resident/family feedback integration (TQM module planned)
- 📋 Care plan integration for holistic view (future API)

### **Systems and Processes**
- ✅ End-to-end integrated workflows (rota → leave → absence → training → reporting)
- ✅ Process documentation (36 guidance documents)
- ✅ Role-based access control reflecting process ownership
- ⏳ Process mapping visualization (planned)
- ⏳ Process audit schedule (TQM Quality Audits module)

### **Data and Information**
- ✅ ML forecasting and optimization (25.1% MAPE, 12.6% cost reduction)
- ✅ Real-time operational intelligence (777ms response, 0% error rate)
- ✅ Quantified baseline and outcomes (academic research validation)
- ✅ Automated compliance reporting (13 reports, 80% time reduction)
- 📋 Statistical Process Control charts (TQM Performance Metrics module)

### **Quality Improvement Capability**
- ✅ Agile development methodology (iterative PDSA approach)
- ✅ User feedback loops (1,352 users, analytics tracking)
- ✅ Performance monitoring and optimization (continuous enhancement)
- 📋 PDSA tracker for structured improvement projects (TQM module planned)
- 📋 Lessons learned repository (TQM module planned)

### **Risk Management**
- ✅ Comprehensive risk register (12 risks with mitigation)
- ✅ Proactive compliance alerts (training expiry, staffing ratios)
- ✅ Audit trail for accountability (all changes logged)
- 📋 Risk management module with controls tracking (TQM planned)
- 📋 Early warning system for quality deterioration (future enhancement)

### **Partnership and Engagement**
- ✅ Multi-stakeholder design team (diverse representation)
- ✅ Staff engagement mechanisms (feedback sessions, surveys)
- ✅ Regulatory relationship (CI evidence generation, pre-inspection planning)
- ✅ Sector partnership (NES DLP, HIS/NES framework alignment)
- 📋 Benchmarking consortium for mutual learning (future)

---

## Success Metrics for HIS QMS Integration

### **Leadership Commitment Metrics:**
- **Baseline:** Ad-hoc quality discussions without structured data
- **Target:** Quarterly board quality reviews using system dashboards with HIS-aligned KPIs
- **Measurement:** Board meeting minutes, quality metrics reviewed

### **Evidence-Based Decision Making Metrics:**
- **Baseline:** 40 hours manual evidence gathering for inspections
- **Target:** 8 hours using automated HIS QMS-aligned reports (80% reduction)
- **Measurement:** Manager time logs, inspector feedback

### **Continuous Improvement Metrics:**
- **Baseline:** Informal improvement efforts without tracking
- **Target:** 10+ active PDSA projects tracked in system annually (TQM module)
- **Measurement:** PDSA tracker completion rates, improvement outcomes

### **Person-Centered Care Metrics:**
- **Baseline:** No systematic resident/family feedback integration
- **Target:** Quarterly satisfaction surveys with >70% response rate (TQM Feedback module)
- **Measurement:** Survey completion rates, action plan tracking

### **Risk Management Metrics:**
- **Baseline:** Risk register in separate spreadsheet, quarterly manual review
- **Target:** Real-time risk dashboard with automated control effectiveness monitoring
- **Measurement:** Risk review frequency, control measure updates

---

## Next Steps

### **Completed:**
✅ Task 1: Map system features to Care Inspectorate quality themes  
✅ Task 2: Integrate HIS Quality Management Systems framework

### **In Progress:**
📋 Task 3: Align with NES Quality Improvement Zone methodologies

### **Upcoming:**
📋 Task 4: Review and update compliance reporting templates  
📋 Task 5: Conduct Care Inspectorate inspection readiness gap analysis  
📋 Task 6: Develop evidence repository structure for regulatory submissions  
📋 Task 7: User research with quality managers for TQM co-design

---

## Key Takeaways

**Current Strengths:**
- Strong alignment with 5/7 HIS QMS principles (Leadership, Evidence-Based, Continuous Improvement, Risk-Based, Relationship Management)
- Moderate alignment with Person-Centered (staff-focused, needs resident feedback integration)
- Moderate alignment with Process-Based (good workflows, needs visualization and audit)

**Strategic Opportunities:**
- TQM modules represent systematic HIS QMS implementation across all 7 principles
- Each module addresses specific QMS gaps while strengthening existing capabilities
- Integrated platform approach (rota + quality) differentiates from competitors

**Competitive Advantage:**
- Scottish-specific HIS/NES alignment (not available in commercial UK-wide solutions)
- Evidence-based ROI (£590K, 24,500%) supports business case for quality investment
- Person-centered design (SAtSD) demonstrates commitment to HIS principles

---

**Document Version:** 1.0  
**Author:** Dean Sockalingum  
**Review Date:** February 2026 (post-presentation)  
**Status:** Phase 3 Task 2 Complete ✅

**References:**
- [Health Improvement Scotland - Quality Management Systems](https://www.healthcareimprovementscotland.scot/improving-care/improvement-resources/)
- [HIS - Person-Led Care](https://www.healthcareimprovementscotland.scot/our-work/person-centred-care-and-health-and-wellbeing/person-led-care/)
- [Scottish Patient Safety Programme (SPSP)](https://www.healthcareimprovementscotland.scot/our-work/patient-safety/spsp/)
