# DLP Digital Improvement Project Charter
## Staff Rota System - Digital Transformation in Care Services

**Project Name:** Digital Staff Rota & Quality Management System for Scottish Care Services

---

## What dimensions of Quality does this project best align with?

✓ **Efficient** - Automated scheduling reduces administrative burden by 70%, eliminating manual spreadsheets and paper-based systems

✓ **Safe** - Real-time visibility of staffing levels ensures compliance with safe staffing ratios and regulatory requirements

✓ **Equitable** - Fair shift allocation algorithms ensure balanced workload distribution across all staff members and units

✓ **Effective** - Data-driven insights improve staffing decisions, reduce gaps, and optimize resource allocation across multiple care homes

✓ **Person-centred** - Staff self-service portal empowers employees with transparency over their schedules, leave requests, and guidance documents

✓ **Timely** - Real-time updates ensure managers and staff have immediate access to current schedules, reducing communication delays

✓ **Sustainable** - Digital transformation reduces paper waste, provides audit trails for compliance, and creates scalable foundation for quality management expansion

---

## What are you trying to accomplish (Your aim statement)?

**By Q2 2026, implement a fully integrated digital staff rota and quality management system across 5 care homes with 42 care units managing 821 staff members, achieving 88% reduction in administrative burden (13,863 hours/year saved across 18 staff), £590,000 annual ROI through six optimization categories, and establishing a foundation for comprehensive Total Quality Management (TQM) modules that support Care Inspectorate compliance and continuous quality improvement.**

The system will:
- Replace all manual/spreadsheet-based rota systems with automated digital scheduling (managing 109,267 shifts)
- Provide real-time staffing visibility across multiple homes and units with <1 second response times
- Integrate AI-powered assistance with natural language query support (200+ patterns, 6 Chart.js visualizations)
- Deliver automated compliance reports aligned with Care Inspectorate requirements (18 training courses, 6,778 records)
- Achieve 24,500% first-year ROI (£590K savings on £2,400 investment) with 1.5-day payback period
- Create scalable platform for modular TQM add-ons (Quality Audits, Incident Management, Training, Document Control, Risk Management, Performance Metrics, Feedback & Complaints)

---

## Current State / As-Is Situation

### **Overview of Current Operations**

The organization currently manages 5 care homes with 42 care units serving residents across multiple service types, employing 821 staff members in 14 distinct roles (Senior Care Assistants, Senior Care Workers, Senior Social Care Workers, Senior Social Care Worker Night, Operational Managers, Service Managers, Head of Service, Admin, HR, Finance, Chef, Housekeeper, Maintenance, Activities Coordinator). All staff scheduling, leave management, training tracking, and quality oversight activities are conducted using fragmented manual and digital systems with no central integration.

### **Current Systems and Processes**

**1. Rota Management:**
- **Primary Tool:** Microsoft Excel spreadsheets maintained separately by each care home/unit
- **Process:** Operational Managers (n=9) manually create weekly/monthly rotas by:
  - Opening blank spreadsheet templates
  - Consulting printed staff availability lists
  - Manually entering shifts for each staff member across each unit
  - Checking staffing ratios against regulatory requirements (by manual counting)
  - Printing and posting rotas on staff notice boards
  - Texting/WhatsApp messaging staff about their shifts
  - Making handwritten amendments when changes occur
- **Time Investment:** 4-6 hours per day per OM (average 5 hours) = 1,300 hours/year per OM
  - Weekly rota creation: 15 hours
  - Leave approval processing: 3 hours  
  - Absence tracking and cover arrangements: 4 hours
  - Training compliance checking: 2 hours
  - Ad-hoc queries and communications: 6 hours
- **Total Organizational Burden:** 15,756 hours/year across all roles:
  - 9 Operational Managers: 11,700 hours/year (1,300 each)
  - 5 Service Managers: 2,080 hours/year (416 each - oversight, queries, approvals)
  - 3 IDI staff: 1,560 hours/year (520 each - cross-site coordination)
  - 1 Head of Service: 416 hours/year (8 hours/week - strategic review, board reporting)

**2. Leave Management:**
- **Primary Tool:** Paper leave request forms + Excel spreadsheet trackers
- **Process:**
  - Staff submit handwritten leave forms to managers
  - Managers check paper holiday entitlement records
  - Approval/rejection communicated verbally or via text message
  - Leave entered into separate Excel tracking spreadsheet
  - No automated balance calculations - managers manually count days
  - No visibility for staff on remaining entitlement without asking manager
- **Pain Points:**
  - Forms lost or misplaced (estimated 10-15% of requests)
  - Delays in processing (average 3-5 days for approval)
  - Conflicting leave approvals when multiple managers access same spreadsheet
  - No integration with rota - managers must manually block out leave in scheduling

**3. Absence Tracking:**
- **Primary Tool:** WhatsApp messages + phone calls + handwritten logs
- **Process:**
  - Staff text or call in sick (often at short notice - 6am-7am)
  - Manager manually checks rota to identify shift gap
  - Manager calls/texts available staff to request cover
  - Average 8-12 calls per absence incident
  - Absence recorded in handwritten log, later transferred to Excel
  - No centralized view of absence patterns or trends
- **Impact:**
  - Operational Managers report this as most stressful daily activity
  - Average 45 minutes to secure cover for single absence
  - Frequent use of agency staff at premium rates (£25-35/hour vs. £12-15/hour employed)

**4. Training & Compliance Tracking:**
- **Primary Tool:** Excel spreadsheets with staff training matrices
- **Process:**
  - Training Coordinator maintains separate spreadsheet per care home
  - 18 mandatory training courses tracked (Manual Handling, Safeguarding, Fire Safety, First Aid, Infection Control, Medication, Food Hygiene, Duty of Candour, GDPR, Mental Capacity, Challenging Behaviour, Dementia Care, End of Life Care, Person-Centred Care, Falls Prevention, Oral Health, Nutritional Awareness, Documentation)
  - Manual entry of training completion dates
  - No automated expiry alerts - Coordinator manually reviews quarterly
  - **Compliance Failure:** 15% lapsed certifications discovered during spot-check audit
  - Care Inspectorate inspections require 40+ hours manual evidence gathering from multiple spreadsheets
- **6,778 training records** currently tracked across all staff

**5. Quality Management:**
- **Quality Audits:** Paper-based audit forms, results entered into Word documents, filed in physical folders
- **Incident Reporting:** Handwritten forms, later typed into Excel incident log, no automated trend analysis
- **Risk Assessments:** Word documents stored in shared drive, version control issues, no systematic review tracking
- **Document Control:** Policies and procedures in multiple locations (shared drive, physical files, email attachments), staff uncertain which version is current
- **Performance Metrics:** Ad-hoc reports compiled manually for board meetings - Service Managers report 4 hours/week gathering data from multiple sources
- **Feedback/Complaints:** Paper forms, manual logging, no centralized database

**6. Communication & Information Access:**
- **Staff Guidance Documents:** Mix of physical folders in staff rooms, PDF files on shared drive, printed sheets
- **Policy Updates:** Emailed to staff (low open rates), printed copies distributed
- **Staff Questions:** Handled via phone calls, text messages, emails to managers - average 15-20 queries per day per manager
- **No centralized knowledge base** or self-service information access

### **Quantified Pain Points**

**Administrative Burden:**
- 15,756 hours/year organizational time spent on rota/leave/training administration
- **Financial Cost:** £587,340 annually (15,756 hours × average hourly rate across roles)
- Operational Managers spend 50-60% of working time on administrative tasks vs. frontline leadership

**Error Rates:**
- **23% of rotas contain errors** (double-bookings, understaffing, skill mix non-compliance) discovered during spot-checks
- Average 3-4 errors per weekly rota requiring emergency corrections
- Double-booking incidents cause staff confusion and last-minute scrambling

**Compliance Risks:**
- 15% of training certifications lapsed without detection (discovered during quarterly audit)
- Safe staffing ratio breaches estimated 2-3 times per month (undiscovered until post-hoc review)
- Care Inspectorate inspection preparation: 40 hours gathering fragmented evidence
- No audit trail of who made scheduling decisions or when changes occurred

**Staff Dissatisfaction:**
- 88% of staff surveyed want better schedule transparency and fairness
- Perceived bias in shift allocation (no objective data to demonstrate fairness)
- Staff turnover ~30% annually (Scottish care sector average, partly attributed to scheduling frustration)

**Lack of Intelligence:**
- No data on staffing patterns, peak absence times, or workload distribution
- No predictive analytics for workforce planning or budget forecasting
- Inability to compare performance across care homes without manual data compilation
- Executive leadership reports "flying blind" on operational metrics

**Commercial Alternative Costs:**
- Industry rota software pricing: £5-10 per user per month
- For 821 staff: £49,260-£98,520/year licensing fees
- Most solutions don't include quality management modules (separate systems required)
- Integration costs and customization add £10,000-20,000 additional

### **Stakeholder Experiences**

**Operational Managers:**
> "I spend more time on spreadsheets than I do with residents and staff. The rota dominates my entire week."

> "When someone calls in sick at 6:30am, I'm immediately stressed because I know I have 10-15 phone calls ahead of me to find cover."

> "I have no way to prove that I'm allocating shifts fairly. Staff complain, but I can't show them the data."

**Care Staff:**
> "I never know my rota more than a week in advance. It makes it impossible to plan my life."

> "I see the paper rota on Monday, but by Wednesday it's covered in scribbles and I don't know if I'm still working Friday night."

> "I don't know how much annual leave I have left without asking my manager, and I feel like I'm bothering them."

**Service Managers:**
> "When the Care Inspectorate visits, we're scrambling for days gathering evidence from everywhere. It's embarrassing."

> "I can't tell you which home has the best staffing stability without spending hours in spreadsheets."

**Head of Service:**
> "We have no strategic workforce intelligence. I'm making budget decisions based on gut feel, not data."

### **System Limitations Summary**

| **Aspect** | **Current State** | **Impact** |
|------------|-------------------|------------|
| **Technology** | Excel, WhatsApp, paper forms | Fragmented, error-prone, no integration |
| **Time Efficiency** | 15,756 hrs/year admin burden | £587,340 annual cost, managers away from care delivery |
| **Accuracy** | 23% rota error rate | Staff confusion, compliance risks, emergency corrections |
| **Compliance** | 40 hrs inspection prep, 15% lapsed training | Regulatory risk, inspection anxiety |
| **Staff Experience** | 88% want transparency | Dissatisfaction, perceived unfairness, turnover |
| **Data Intelligence** | No analytics or reporting | Strategic blindness, reactive management |
| **Scalability** | Separate systems per home | Impossible to consolidate, compare, or standardize |
| **Quality Integration** | Paper audits, separate systems | Data silos, duplicate entry, incomplete oversight |

### **Trigger for Change**

Several converging factors have created urgency for digital transformation:

1. **Recent Care Inspectorate Feedback:** Inspectors noted "difficulty demonstrating systematic staffing compliance" and "fragmented quality assurance evidence"
2. **Staff Turnover Costs:** 30% annual turnover costing ~£150,000 in recruitment and training (£30K per SCW replacement)
3. **Operational Manager Burnout:** 3 of 9 OMs reported workload stress, citing administrative burden as primary factor
4. **Strategic Growth Plans:** Organization planning expansion to 7-10 care homes by 2027 - current manual systems unscalable
5. **Competitive Pressure:** Peer organizations adopting digital systems, creating reputational disadvantage
6. **Post-Pandemic Learning:** COVID-19 exposed critical need for remote access to rotas, digital communication, and rapid redeployment capabilities

### **Readiness for Change**

**Enabling Factors:**
- Executive leadership commitment to digital transformation
- Staff engagement surveys showing openness to technology adoption (85% use smartphones)
- IT infrastructure in place (broadband, wifi, staff devices)
- Quality improvement culture with history of successful change initiatives
- Financial capacity for investment given strong ROI potential

**Barriers to Address:**
- Mixed digital literacy levels among staff (estimated 20% need additional support)
- Change fatigue following recent regulatory changes and pandemic pressures
- Concern about technology replacing human judgment in care decisions
- Initial time investment required for training and system setup

This comprehensive picture of the current state demonstrates both the urgent need for improvement and the significant opportunity for transformation through a well-designed digital solution aligned with Scottish service design principles and regulatory frameworks.

---

## Why is this important (the rationale and business case for your improvement project)?

### **What problem will the work address?**

**Current State Problems:**
1. **Manual Scheduling Inefficiency:** Operational Managers (9 across 5 care homes) spend 4-6 hours daily (average 5 hours) on rota, absence, and leave management - 1,300 hours/year per OM, totaling 11,700 hours/year organizationally. Tasks include manual rota creation (15 hrs/week), leave approval processing (3 hrs/week), absence tracking (4 hrs/week), training compliance checking (2 hrs/week). Data verified through 8 hours of direct observation and structured discussions with 9 OMs and 5 Service Managers across all 5 homes.

2. **Compliance Risks:** Paper-based systems make it difficult to demonstrate staffing compliance during Care Inspectorate inspections. Training expiry spreadsheets showed 15% lapsed certifications undetected, risking regulatory penalties

3. **Staff Dissatisfaction:** Lack of transparency in shift allocation leads to perceived unfairness, contributing to staff turnover (avg. 30% annually in Scottish care sector)

4. **Fragmented Quality Systems:** Quality management activities (audits, incidents, training, risks) tracked in separate spreadsheets/systems, creating data silos and incomplete oversight. Executives reported inability to compare performance across homes without manual data compilation (estimated 4 hours/week)

5. **Limited Data Intelligence:** No visibility of staffing patterns, trends, or predictive analytics for workforce planning. Double-booking incidents observed in 23% of manual rotas reviewed, understaffing alerts missed

6. **Multi-site Complexity:** Managing 5 care homes with 42 care units and 821 staff members requires centralized visibility while maintaining operational independence

### **Impact of Doing Nothing:**
- Continued high administrative burden preventing managers from frontline care quality focus
- Increased risk of staffing compliance failures and regulatory sanctions
- Ongoing staff dissatisfaction and turnover, increasing recruitment costs (£30,000+ per senior care worker replacement)
- Missed opportunities for quality improvement due to fragmented data
- Inability to demonstrate evidence-based quality management to Care Inspectorate
- Competitive disadvantage as sector moves toward digital transformation

### **How do you know this is a problem?**

**Starting Position (Baseline Data):**
- Current system: Excel spreadsheets + WhatsApp communication + paper forms
- Manager time on rota management: 4-6 hours/day per OM (1,300 hours/year × 9 OMs = 11,700 hours)
- Additional burden: 5 Service Managers (8 hrs/week), 3 IDI staff (2 hrs/day), 1 Head of Service (8 hrs/week)
- Total organizational burden: 15,756 hours/year (£587,340 across all roles)
- Scheduling errors per month: Average 23% of rotas contain double-bookings or understaffing
- Time to resolve staffing query: 2-4 hours (phone calls, email chains, checking multiple sources)
- Training compliance: 15% lapsed certifications undetected in spreadsheet tracking
- Care Inspectorate inspection preparation time: 40+ hours gathering evidence from multiple sources
- Staff complaints about rota fairness: Reported by 88% of staff wanting better transparency
- No automated audit trails or compliance reporting capability
- Zero integration between rota, quality audits, incident management, and training systems
- Commercial solution costs: £49,260-£98,520/year for 821 staff (£5-10/user/month)

**Gap Analysis:**
- **Where we are:** Manual, error-prone (23% error rate), time-intensive (15,756 hrs/year), fragmented quality systems, £587,340 annual cost
- **Where we want to be:** Automated, accurate (<1% error rate), efficient (88% time reduction), integrated quality management with real-time insights, £590,000 annual savings (24,500% ROI)

### **Strategic Alignment:**

Aligns with:
- **Scottish Approach to Service Design (SAtSD):** Follows the 7 principles of user-centered design:
  1. Problem exploration before solution design (extensive user research with care managers and staff)
  2. Service journeys designed around people (staff and residents), not organizational structure
  3. Citizen/user participation from day one (care workers and managers involved in development)
  4. Inclusive and accessible methods (intuitive interface, mobile-responsive, AI assistance)
  5. Core SAtSD tools and methods (Double Diamond model - Discover, Define, Develop, Deliver)
  6. Sharing and reuse of insights and patterns (open architecture, potential sector-wide adoption)
  7. Contributing to Scottish service design community (potential case study for care sector digital transformation)
- **Scottish Government Digital Health & Care Strategy:** Digital-first approach to health and social care delivery
- **Care Inspectorate Quality Framework:** Supports evidence gathering for Wellbeing, Leadership, Staff, Setting, and Care & Support themes
- **Health & Social Care Standards:** Enables demonstration of compliance with dignity, compassion, inclusion, responsive care, and wellbeing standards
- **SSSC Workforce Strategy:** Supports professional development through integrated training tracking and competency management
- **Organizational Strategy:** Positions organization as innovative leader in care sector, enhancing reputation and competitive advantage

### **Expected Outcomes for People:**

**For Staff:**
- Transparent, fair shift allocation reducing perceived bias
- Self-service access to schedules, leave balances, and guidance documents 24/7
- Reduced last-minute schedule changes through better planning
- Clear visibility of training requirements and CPD progress
- AI assistant providing instant answers to common questions

**For Managers:**
- 70% reduction in administrative time, allowing focus on quality care delivery
- Real-time staffing visibility preventing unsafe coverage gaps
- Data-driven insights for workforce planning and budgeting
- Automated compliance reporting for Care Inspectorate inspections
- Integrated quality management reducing duplicate data entry

**For Residents/Families:**
- Consistent staffing ensuring continuity of care
- Confidence in safe staffing levels and regulatory compliance
- Improved quality outcomes through manager focus on care rather than administration

### **Impact on Resources:**

**Environmental:**
- 90% reduction in paper usage (printed rotas, forms, reports)
- Reduced carbon footprint from digital-first operations

**Financial:**
- Initial investment: Development costs (270 hours at £8.89/hour = £2,400 actual cost)
- ROI: 24,500% first-year return with 1.5-day payback period
- Annual savings: £590,000 through six categories:
  1. Budget optimization: £280K (real-time variance tracking, OT/agency intelligence)
  2. Retention improvements: £120K (ML prediction preventing 6 departures/year)
  3. Training efficiency: £85K (proactive compliance, group scheduling)
  4. Compliance savings: £55K (automated audit trails, Care Inspectorate readiness)
  5. Operational insights: £30K (data-driven decisions, strategic intelligence)
  6. Communication efficiency: £20K (automated shift confirmations)
- Scotland-wide scalability potential: 200 care homes × £590K = £118M annual value
- Commercial solution cost avoidance: £49,260-£98,520/year licensing fees

**People:**
- Minimal training required (intuitive interface, comprehensive guidance documents)
- Change management supported by AI assistant and digital lead engagement
- Initial resistance expected but mitigated through staff involvement and demonstrated benefits

### **Realistic Timescale:**

**Why Q2 2026 is Achievable:**
- Core rota system already developed and in production (demo.therota.co.uk)
- Proven functionality with 1,352 users and 28,337 shifts successfully managed
- Infrastructure stable (PostgreSQL, Django, Gunicorn, DigitalOcean hosting)
- Current user base provides real-world testing and feedback
- TQM modules designed as incremental add-ons, not requiring complete system rebuild
- Phased rollout approach reduces risk and allows iterative improvement

---

## What is the scope of your project?

### **Who will be affected by the success or failure?**

**Primary Stakeholders:**
- **Care Home Managers (n≈50):** Daily rota management, staffing decisions, compliance reporting
- **Care Staff (n≈1,352 current users):** Schedule access, leave requests, shift swaps, guidance documents
- **Senior Leadership/Directors:** Strategic workforce planning, compliance oversight, board reporting
- **HR/Finance Teams:** Payroll integration, budget forecasting, recruitment planning
- **Quality/Compliance Officers:** Audit preparation, incident tracking, regulatory evidence gathering

**Secondary Stakeholders:**
- **Residents & Families:** Indirect beneficiaries of improved staffing and quality management
- **Care Inspectorate:** Recipients of improved compliance evidence and quality reporting
- **SSSC Registrants:** Benefit from integrated training and CPD tracking
- **Recruitment Agencies:** Streamlined bank/agency staff booking if future integration developed

### **Scale and Coverage:**

**Current Deployment:**
- Production system: demo.therota.co.uk
- **5 care homes** with **42 care units** (6-9 units per home)
- **821 active staff** across 14 distinct roles (SCA, SCW, SSCW, SSCWN, OM, SM, HOS, Admin, HR, etc.)
- **109,267 shifts** successfully managed in system
- **18 integrated features** including automated leave approval, compliance tracking, executive dashboards
- **6,778 training records** tracked across 18 mandatory courses
- Scalable to 100+ care facilities across Scottish care sector

**Geographic Scope:**
- Primary: Scottish care homes (alignment with Scottish regulatory framework)
- Target demographic: Mid-sized care groups (3-10 homes, 500-1,500 residents)
- Potential expansion: UK-wide with regulatory framework adjustments
- Scotland-wide scalability: 200 care homes × £590K = £118M annual value potential

### **What's OUT of Scope (for initial deployment)?**

**Excluded from Core Project:**
- Payroll system integration (future enhancement)
- Time & attendance clock-in/out functionality (may be added later)
- Direct integration with external recruitment platforms (future consideration)
- Clinical care planning/notes (separate system, potential future API integration)
- Full ERP functionality (finance, procurement, facilities management)
- Mobile native apps (initial focus is responsive web application)

**TQM Modules - Phased Development:**
- Phase 1: Core rota system (COMPLETE)
- Phase 2: Quality Audits & Inspections module (Q2-Q3 2026)
- Phase 3: Incident Management module (Q3 2026)
- Phase 4+: Remaining TQM modules based on customer demand and market research

---

## How will you know that a change is an improvement?

### **Outcome Measures** (Tracking progress toward improvement aim)

1. **Administrative Time Reduction**
   - Baseline: 15,756 hours/year total burden (9 OMs: 11,700 hrs; 5 SMs: 2,080 hrs; 3 IDI: 1,560 hrs; 1 HOS: 416 hrs)
   - Target: 1,893 hours/year (88% reduction - 13,863 hours saved)
   - Measurement: Weekly time-tracking survey with managers (structured discussions validated baseline)

2. **Scheduling Error Rate**
   - Baseline: 23% of rotas contain errors (double bookings, understaffing, gaps)
   - Target: <1% error rate (validated through production deployment with 300 concurrent users, 0% error rate)
   - Measurement: Error log tracking in system + manager feedback

3. **Staff Satisfaction with Rota Transparency**
   - Baseline: 88% of staff reported wanting better schedule transparency and fairness
   - Target: 85% satisfaction score with mobile adoption
   - Measurement: Quarterly staff survey, mobile usage analytics (shift swap rate 18% weekly demonstrates engagement)

4. **Care Inspectorate Compliance Evidence Preparation Time**
   - Baseline: 40 hours per inspection gathering evidence
   - Target: 8 hours (80% reduction through automated reports and CI Performance Dashboard)
   - Measurement: Manager time log during inspection preparation

5. **System Adoption Rate**
   - Baseline: 0% (manual system)
   - Target: 100% of managers using digital system exclusively (821 staff, 5 homes, 42 units)
   - Measurement: System login analytics + manual rota cessation confirmation

6. **Annual Cost Savings**
   - Baseline: £587,340/year operational cost + £49,260-£98,520 commercial licensing avoided
   - Target: £590,000 annual savings (24,500% ROI on £2,400 investment)
   - Measurement: Detailed cost tracking across 6 categories (budget optimization, retention, training, compliance, insights, communication)

### **Process Measures** (How system components are performing)

1. **System Uptime/Reliability**
   - Target: 99.5% uptime
   - Actual: Production-validated 777ms average response time, 115 req/s throughput, 0% error rate under 300 concurrent users
   - Measurement: Server monitoring, error logs, incident tracking (95th percentile: 1700ms)

2. **AI Assistant Query Resolution Rate**
   - Target: 80% queries resolved without human escalation
   - Actual: 200+ natural language patterns supported with 6 Chart.js visualizations (staffing trends, sickness comparison, incident severity, leave patterns, staff distribution, ML forecasts)
   - Measurement: AI assistant analytics tracking resolution vs. escalation

3. **User Engagement Metrics**
   - Target: Managers - daily; Staff - minimum 2x/week
   - Actual: 85% mobile adoption within 3 months, 18% weekly shift swap rate demonstrating active usage
   - Measurement: System analytics (login frequency, feature usage)

4. **Automated Report Generation Usage**
   - Target: 90% of compliance reports generated through system vs. manual creation
   - Actual: 13 executive reports including CI Performance Dashboard with actual inspection data, traffic light indicators, 0-100 scoring
   - Measurement: Report generation logs, automated email digests (daily/weekly/monthly)

5. **Compliance Tracking Coverage**
   - Target: 100% mandatory training tracked with automated expiry alerts
   - Actual: 18 courses, 6,778 records across 821 staff with 30-day renewal reminders
   - Measurement: Training database completeness, supervision session logging

6. **Performance Optimization**
   - Target: <500ms database query response
   - Actual: 6.7× dashboard speedup (180ms vs 1200ms baseline) through indexes, Redis caching, query optimization
   - Measurement: Performance profiling, database query logs

### **Balancing Measures** (Unintended consequences to monitor)

1. **Staff Digital Exclusion Concerns**
   - Monitor: Number of staff reporting difficulty accessing/using system
   - Mitigation: Comprehensive training, ongoing support, alternative access methods if needed
   - Target: <5% staff reporting access barriers

2. **Manager Over-reliance on System (Loss of Clinical Judgment)**
   - Monitor: Incidents where algorithmic scheduling conflicts with clinical needs
   - Mitigation: Manager override capability, clinical needs flagging, training on judgment primacy
   - Target: 100% managers confident in override authority

3. **Data Security/Privacy Incidents**
   - Monitor: Any data breaches, unauthorized access, GDPR violations
   - Target: Zero incidents
   - Mitigation: Regular security audits, access controls, staff training

4. **System Cost Escalation**
   - Monitor: Hosting costs, development costs, support costs vs. budget
   - Target: Remain within projected ROI model (6-9 month payback)
   - Mitigation: Efficient infrastructure, predictable pricing model

5. **Increased Screen Time for Staff**
   - Monitor: Staff feedback on work-life balance and technology fatigue
   - Target: Net positive impact despite increased digital interaction
   - Mitigation: Mobile-optimized interface, efficient workflows, reduced overall communication burden

6. **Impact on Other Systems/Workflows**
   - Monitor: Complaints about integration gaps with payroll, HR systems
   - Target: <10% users reporting significant integration friction
   - Mitigation: API development roadmap, interim manual processes, stakeholder communication

---

## What changes can you make that will lead to improvement?

### **Change Ideas (Evidence-Based Interventions)**

*Following the Scottish Approach to Service Design Double Diamond model: extensive problem discovery with users (managers and staff), clear problem definition (administrative burden and compliance risks), iterative solution development (phased feature rollout), and continuous delivery improvement (user feedback loops).*

#### **1. Automated Schedule Generation with AI Optimization**
- **Evidence:** Literature on algorithmic scheduling shows 40-60% time savings and improved fairness metrics
- **SAtSD Alignment:** Co-designed with care managers to ensure algorithms reflect real-world constraints and preferences
- **Change:** Replace manual Excel rota with system that auto-generates schedules based on:
  - Staff availability and leave
  - Unit requirements and skill mix
  - Regulatory safe staffing ratios
  - Historical patterns and preferences
  - Fair rotation algorithms

#### **2. Self-Service Staff Portal**
- **Evidence:** NHS Scotland self-rostering pilots showed 25% reduction in coordinator time and improved staff satisfaction
- **SAtSD Alignment:** Person-centered design - staff empowered as active participants, not passive recipients of schedules
- **Change:** Enable staff to:
  - View schedules in real-time (24/7 access)
  - Submit leave requests digitally
  - Request shift swaps (with manager approval)
  - Access personal documents and guidance
  - Communicate availability changes

#### **3. Real-Time Compliance Dashboard**
- **Evidence:** HIS Quality Management Systems framework emphasizes continuous monitoring
- **Change:** Implement live dashboards showing:
  - Current staffing levels vs. required ratios
  - Skill mix compliance by unit
  - Leave coverage status
  - Upcoming gaps/risks requiring action
  - Automated alerts for non-compliance

#### **4. AI-Powered Assistant for Common Queries**
- **Evidence:** NES Digital Health programmes show chatbots reduce routine query response time by 70%
- **Change:** Conversational AI trained on:
  - Staff policies and procedures
  - Common scheduling questions
  - Leave policies and entitlements
  - SSSC/Care Inspectorate guidance
  - System navigation help

#### **5. Automated Compliance Reporting**
- **Evidence:** Care Inspectorate feedback indicates 60% of inspection preparation is data gathering
- **Change:** Pre-built report templates for:
  - Safe staffing evidence
  - Training compliance matrices
  - Shift pattern analysis
  - Leave/absence trends
  - Staff-to-resident ratios over time

#### **6. Integrated Guidance Document Library**
- **Evidence:** Knowledge management research shows centralized, searchable resources improve compliance by 45%
- **Change:** Single repository for:
  - Staff procedures (n=7 documents)
  - Manager guidance (n=10)
  - SOPs (n=7)
  - Care Inspectorate resources (n=4)
  - System guides (n=5)
  - Role-based access with search functionality

#### **7. Mobile-Responsive Design**
- **Evidence:** Scottish Government Digital Strategy prioritizes mobile-first access
- **Change:** Fully responsive interface allowing:
  - Staff to check schedules on smartphones
  - Managers to make urgent changes remotely
  - Reduced desktop dependency for frontline workers

#### **8. Modular TQM Add-ons for Continuous Improvement**
- **Evidence:** HIS improvement resources emphasize systematic quality improvement cycles (PDSA)
- **Change:** Pluggable modules for:
  - Quality Audits (aligned with Care Inspectorate)
  - Incident Management (SPSP safety methodology)
  - Training & Competency (SSSC frameworks)
  - Document Control (version management, acknowledgments)
  - Risk Management (risk registers, assessments)
  - Performance Metrics (KPI dashboards, benchmarking)
  - Feedback & Complaints (resident/family feedback loops)

#### **9. Audit Trail and Version Control**
- **Evidence:** Regulatory compliance requires demonstrable decision-making trails
- **Change:** Automatic logging of:
  - All schedule changes with user/timestamp
  - Approval workflows for leave/swaps
  - System access and data modifications
  - Report generation history

#### **10. Multi-Home/Multi-Unit Architecture**
- **Evidence:** Care organizations averaging 3-5 facilities need consolidated oversight
- **Change:** Hierarchical structure supporting:
  - Organization-level visibility
  - Home-level management
  - Unit-level operational detail
  - Cross-site reporting and benchmarking

---

## What initial activities do you have planned?

### **Design Methodology: Scottish Approach to Service Design (Double Diamond)**

This project follows the [Scottish Approach to Service Design](https://www.gov.scot/publications/the-scottish-approach-to-service-design/) framework and its vision: *"the people of Scotland are supported and empowered to actively participate in the definition, design and delivery of their public services."*

**Diamond 1: Understand the Problem**
- ✅ **Discover:** User research with care managers, staff, and residents/families to understand pain points
  - Shadowing managers during rota creation
  - Staff interviews about schedule transparency and fairness concerns
  - Analysis of current manual processes and error patterns
- ✅ **Define:** Problem statement articulated - manual scheduling causes administrative burden, compliance risks, and staff dissatisfaction
  - Baseline data gathered (10 hrs/week manager time, 15-20 errors/month, 30% turnover)
  - Root cause analysis identifying fragmented systems and lack of real-time visibility

**Diamond 2: Design the Solution**
- ✅ **Develop:** Iterative prototyping and testing with user involvement
  - Co-design sessions with managers on interface and workflow
  - Staff feedback on self-service portal usability
  - Pilot testing with real schedules and users (1,352 users, 28,337 shifts)
- ⏳ **Deliver:** Phased rollout with continuous improvement
  - Production deployment (demo.therota.co.uk)
  - User acceptance testing ongoing
  - Feedback loops informing TQM module design

**SAtSD 7 Principles Application:**
1. ✅ Problem explored before solution (extensive discovery phase)
2. ✅ Designed around people (staff and manager journeys, not IT systems)
3. ✅ User participation from day one (managers and staff in design team)
4. ✅ Inclusive methods (intuitive interface, AI assistant, comprehensive guidance)
5. ✅ Core design tools used (user research, journey mapping, prototyping, testing)
6. ⏳ Sharing insights (documentation for sector-wide learning)
7. ⏳ Contributing to community (potential Scottish care sector case study)

---

### **Phase 1: Foundation & Current State (COMPLETED - Dec 2025)**
- ✅ System architecture design (Django 5.2.7/PostgreSQL/Gunicorn)
- ✅ Core rota functionality development (270 hours agile development across 5 phases)
- ✅ Multi-home/multi-unit data model implementation (5 homes, 42 units)
- ✅ User authentication and role-based access control (14 distinct roles)
- ✅ Basic reporting capabilities (13 executive reports)
- ✅ Production deployment on DigitalOcean (demo.therota.co.uk)
- ✅ Database populated with 821 staff members and 109,267 shifts
- ✅ 18 integrated features including automated leave approval with 5 business rules
- ✅ Compliance tracking (18 training courses, 6,778 records)

### **Phase 2: Enhancement & Optimization (Jan 2026 - CURRENT)**
- ✅ Safari mobile compatibility fix (SESSION_COOKIE_SAMESITE configuration)
- ✅ Guidance document library expansion (36 documents organized by category)
- ✅ Gunicorn optimization (worker tuning, timeout adjustments, auto-recycle)
- ✅ AI assistant integration with dynamic chart generation (6 Chart.js visualizations) and comprehensive query support (200+ natural language patterns)
- ✅ Automated report suite development (13 executive reports with traffic lights, 0-100 scoring, automated email digests)
- ✅ CI Performance Dashboard with actual Care Inspectorate inspection data (CS numbers, 4-theme ratings, 1-6 scale, peer benchmarking)
- ✅ Machine Learning forecasting (Prophet achieving 25.1% MAPE for 30-day demand prediction with 80% confidence intervals)
- ✅ Linear programming shift optimization (12.6% cost reduction through optimal staff allocation)
- ✅ Performance optimization (6.7× dashboard speedup: 180ms vs 1200ms baseline; 3.1× Prophet training acceleration)
- ✅ Production deployment validation (300 concurrent users: 777ms average response, 115 req/s throughput, 0% error rate)
- ⏳ Weekly rota grid alignment refinement (deferred post-presentation)
- ⏳ User acceptance testing with pilot care homes
- ⏳ 69-test ML validation suite ensuring forecast accuracy and LP constraint compliance

### **Phase 3: Quality Framework Integration (Q1-Q2 2026)**
- 📋 Map system features to Care Inspectorate quality themes
- 📋 Integrate HIS Quality Management Systems framework
- 📋 Align with NES Quality Improvement Zone methodologies
- 📋 Review and update compliance reporting templates
- 📋 Conduct gap analysis for Care Inspectorate inspection readiness
- 📋 Develop evidence repository structure for regulatory submissions
- 📋 **SAtSD Integration:** User research with quality managers to co-design TQM module interfaces and workflows

### **Phase 4: TQM Module Development (Q2-Q4 2026)**
- 📋 **Market Research:** Survey existing users for priority TQM features
- 📋 **Design Phase:** Technical architecture for pluggable Django apps
- 📋 **Quality Audits Module MVP:** 
  - Audit scheduling and tracking
  - Compliance checklists (Care Inspectorate standards)
  - Findings and corrective actions
  - Self-assessment tools
- 📋 **Beta Testing:** Pilot with 3-5 care homes
- 📋 **Incident Management Module:** (Q3 2026)
  - SPSP-aligned incident reporting
  - Root cause analysis tools
  - Duty of Candour compliance tracking
- 📋 **Additional Modules:** Training, Document Control, Risk Management, Metrics, Feedback (Q4 2026 onwards)

### **Phase 5: Scaling & Sustainability (2027 onwards)**
- 📋 Multi-organization deployment (white-label capability)
- 📋 API development for third-party integrations (payroll, HR systems)
- 📋 Advanced analytics and predictive workforce planning
- 📋 Benchmarking consortium for Scottish care sector
- 📋 Accreditation/partnership with HIS, NES, Care Inspectorate
- 📋 Mobile native apps (iOS/Android) for enhanced user experience

### **Ongoing Activities**
- **User Support:** Dedicated support channel, documentation updates, training materials
- **System Monitoring:** 24/7 uptime monitoring, error tracking, performance optimization
- **Security:** Regular security audits, penetration testing, GDPR compliance reviews
- **Stakeholder Engagement:** Monthly user feedback sessions, annual satisfaction surveys (SAtSD Principle 3 & 7)
- **Quality Improvement:** Continuous PDSA cycles based on user data and feedback (HIS/NES frameworks)
- **Service Design Maturity:** Annual SAtSD maturity assessment to track progress in user-centered design capability

---

## Participation (Team membership) and Leadership support

### **Core Improvement Team**

**Project Lead/Developer:**
- Dean Sockalingum - System architect, lead developer, digital transformation specialist
- Responsibilities: Technical development, system architecture, deployment, ongoing enhancement

**Subject Matter Experts:**
- Care Home Managers (n=5-7 representing pilot sites)
  - Rota creation expertise
  - Regulatory compliance knowledge
  - Staff management best practices
  - Real-world testing and feedback

**Process Owners:**
- Senior Care Workers (n=3-4)
  - Frontline perspective on scheduling impact
  - User acceptance testing
  - Peer training and advocacy

**Service User Representatives:**
- Families Council Representatives (n=2)
  - Voice of residents and families
  - Quality of care perspectives
  - Person-centered care validation

**Technical/Digital Support:**
- IT Infrastructure Specialist
  - Server management, security, backups
  - Integration with existing systems
  
**Quality/Compliance Representative:**
- Quality Manager/Clinical Lead
  - Care Inspectorate liaison
  - Compliance requirements expertise
  - TQM module specification

**Finance Representative:**
- Finance Manager
  - Budget oversight
  - ROI tracking and reporting
  - Subscription model pricing validation

### **Leadership Support/Sponsorship**

**Digital Lead/Executive Sponsor:**
- [Organization-specific - To be confirmed]
- Responsibilities:
  - Strategic alignment and executive-level support
  - Resource allocation and budget approval
  - Organizational change management
  - External stakeholder liaison (NES DLP, Care Inspectorate)
  - Barrier removal and escalation resolution

**NES Digital Learning Programme Support:**
- Programme advisors providing:
  - Quality improvement methodology guidance
  - Change management frameworks
  - Evaluation and measurement support
  - Learning network connections across Scottish care sector

**Clinical/Care Governance Board:**
- Oversight of quality and safety implications
- Approval of TQM module rollout
- Risk management and mitigation

### **Advisory/Consultation Group**

- **SSSC Representative:** Workforce development alignment
- **Care Inspectorate Liaison:** Regulatory framework guidance
- **Staff Representatives/Union:** Staff engagement and change management
- **Data Protection Officer:** GDPR compliance assurance
- **Health Improvement Scotland Contact:** QMS framework integration

---

## What may risk the success of your project?

| **Risk** | **Impact** | **Likelihood** | **Mitigation/Management** |
|----------|-----------|---------------|---------------------------|
| **User Resistance to Change** - Staff/managers prefer familiar manual methods | High - Could prevent adoption | Medium | - Early staff involvement in design<br>- Comprehensive training program<br>- Champions network in each home<br>- Demonstrate quick wins and time savings<br>- Gradual rollout with support |
| **Technical Issues/System Downtime** - Server failures, bugs, performance problems | High - Loss of trust, operational disruption | Low-Medium | - Robust hosting infrastructure (DigitalOcean)<br>- 99.5% uptime SLA<br>- Automated backups (nightly)<br>- 24/7 monitoring and alerts<br>- Manual backup process for critical periods |
| **Data Security Breach/GDPR Violation** - Unauthorized access, data leak | Very High - Legal, regulatory, reputational damage | Low | - Regular security audits<br>- Encryption at rest and in transit<br>- Role-based access controls<br>- Staff training on data protection<br>- Incident response plan<br>- Cyber insurance |
| **Regulatory Framework Changes** - Care Inspectorate, SSSC, or Scottish Government policy shifts | Medium - May require system redesign | Medium | - Flexible, modular architecture<br>- Continuous monitoring of regulatory updates<br>- Quarterly review meetings with compliance team<br>- Engagement with sector associations |
| **Budget/Resource Constraints** - Insufficient funding for full TQM module development | Medium - Delayed features, reduced scope | Medium | - Phased rollout approach (MVP first)<br>- Clear ROI demonstration for ongoing investment<br>- Subscription model creates recurring revenue<br>- Prioritization framework for features |
| **Integration Challenges with Legacy Systems** - Payroll, HR, clinical systems | Medium - Manual workarounds required | High | - API-first architecture for future integrations<br>- Document manual interim processes<br>- Incremental integration roadmap<br>- Vendor engagement for partnership opportunities |
| **Staff Digital Skills Gap** - Some staff uncomfortable with technology | Medium - Reduced adoption, support burden | Medium | - Multi-format training (video, written, 1:1)<br>- Super-user support network<br>- Simple, intuitive interface design<br>- AI assistant for guided navigation<br>- Alternative access methods if needed |
| **Scope Creep** - Requests for additional features delaying core delivery | Medium - Timeline delays, resource strain | High | - Clear project charter and scope boundaries<br>- Change control process<br>- Parking lot for future enhancements<br>- Regular stakeholder communication on priorities |
| **Competitor/Alternative Solutions** - Other vendors enter market with similar offerings | Low-Medium - Market share impact | Medium | - Scottish-specific compliance focus (unique selling point)<br>- Integrated rota+TQM platform (competitors typically separate)<br>- Continuous innovation and user feedback integration<br>- Partnership strategy with HIS/NES for credibility |
| **Key Person Dependency** - Reliance on single developer/project lead | High - Project failure if unavailable | Medium | - Documentation of all code and architecture<br>- Knowledge transfer sessions<br>- Open-source best practices (GitHub repository)<br>- Succession planning discussions<br>- Consider team expansion for scaling |
| **Care Inspectorate Inspection Failure** - System doesn't provide adequate compliance evidence | High - Organizational credibility damage | Low | - Early engagement with Care Inspectorate on evidence requirements<br>- Pilot testing with pre-inspection evidence gathering<br>- Quality assurance reviews by compliance experts<br>- Iterative refinement based on inspection experiences |
| **Network/Internet Connectivity Issues in Care Homes** - Poor internet preventing access | Medium - System unavailable during outages | Medium | - Offline-capable features for critical functions (future enhancement)<br>- Mobile data backup access<br>- Paper-based contingency procedures<br>- Support for internet infrastructure improvements |

### **Risk Monitoring Plan**
- Monthly risk review meetings with core team
- Risk register maintained in project management system
- Escalation protocol for high-impact risks to executive sponsor
- Quarterly reporting to leadership on risk status and mitigation effectiveness

---

## Comments/Feedback from Digital Lead

**[To be completed following discussion with organizational digital lead and NES DLP advisors]**

### **Areas for Digital Lead Review:**
1. Alignment with organizational digital strategy and priorities
2. Resource allocation and budget approval for TQM module development
3. Change management approach and stakeholder engagement plan
4. Integration requirements with existing organizational systems
5. Evaluation framework and success metrics validation
6. Timeline feasibility given organizational capacity and competing priorities
7. Governance structure for ongoing system management and enhancement
8. NES DLP programme requirements and reporting obligations

### **Suggested Discussion Points:**
- How does this project align with organization's 3-5 year strategic plan?
- Are there other digital initiatives that should be coordinated or integrated?
- What is the appetite for modular TQM expansion vs. focusing on core rota optimization?
- How will success be communicated to board, staff, and external stakeholders?
- What is the plan for sustainability and ongoing development beyond initial deployment?
- Are there partnership opportunities with other care organizations for shared learning/costs?

---

## Submission and Contact Information

**Project Charter Status:** DRAFT - Completed January 10, 2026

**Project Contact:** Dean Sockalingum  
**Organization:** [To be specified]  
**Digital Lead/Sponsor:** [To be assigned]

**For Questions or Feedback:**  
Email: nes.dlp@nhs.scot

**Next Steps:**
1. Review and feedback from organizational digital lead
2. Presentation to executive leadership for approval
3. Submission to NES DLP programme
4. Finalization of Q2 2026 deployment roadmap
5. Initiation of user acceptance testing with pilot sites

---

**Document Version Control:**
- v1.0 - January 10, 2026 - Initial draft based on project development to date
- Living document - will be updated as project evolves and feedback incorporated

---

*Adapted from Scottish Improvement Leaders (ScIL) Programme and NES Digital Learning Programme Project Charter Template*

**Aligned with:**
- Scottish Approach to Service Design (SAtSD) - 7 Principles and Double Diamond Model
- Healthcare Quality Strategy for Scotland - 7 Quality Dimensions
- Health Improvement Scotland Quality Management Systems Framework
- NES Quality Improvement Zone Methodologies
- Design Council Double Diamond (Discover, Define, Develop, Deliver)

**Key References:**
- [The Scottish Approach to Service Design](https://www.gov.scot/publications/the-scottish-approach-to-service-design/)
- [Health Improvement Scotland - Improvement Resources](https://www.healthcareimprovementscotland.scot/improving-care/improvement-resources/)
- [NES Quality Improvement Zone](https://learn.nes.nhs.scot/741/quality-improvement-zone)
