# Author Information and Ethics Statements

**Manuscript:** Multi-Tenancy Staff Scheduling System for Healthcare  
**Journal:** Health Informatics Journal (SAGE Publications)  
**Date:** 22 December 2025

---

## Author Details

### Author 1 (Corresponding Author)
- **Name:** Dean Sockalingum
- **Affiliation:** University of Strathclyde, [Department of Computer and Information Sciences - PLEASE CONFIRM]
- **Address:** [University of Strathclyde, 16 Richmond Street, Glasgow G1 1XQ, Scotland - PLEASE CONFIRM]
- **Email:** [dean.sockalingum@strath.ac.uk - PLEASE CONFIRM]
- **ORCID:** [Register at https://orcid.org/register - Format: 0000-0000-0000-0000]
- **Contribution:** Conceptualization, Methodology, Software, Formal Analysis, Investigation, Writing - Original Draft, Writing - Review & Editing, Project Administration

### Author 2 (if applicable)
- **Name:** [Full Name]
- **Affiliation:** [Institution, Department]
- **Email:** [institutional email]
- **ORCID:** [0000-0000-0000-0000]
- **Contribution:** Methodology, Validation, Writing - Review & Editing, Supervision

### Author 3 (if applicable)
- **Name:** [Full Name]
- **Affiliation:** Glasgow Health and Social Care Partnership, Older People's Services
- **Email:** [institutional email]
- **Contribution:** Resources, Validation, Writing - Review & Editing (practitioner perspective)

---

## Acknowledgments

We thank the Operational Managers, Service Managers, and frontline staff of Glasgow Health and Social Care Partnership's older people's care homes for their collaboration in system co-design and user acceptance testing:

**Participating Care Homes:**
- Orchard Grove Care Home
- Meadowburn Care Home
- Hawthorn House Care Home
- Riverside Care Home
- Victoria Gardens Care Home

**Key Contributors (Practitioner Collaborators):**
- 9 Operational Managers (system co-designers, UAT participants)
- 3 Service Managers (strategic requirements, UAT participants)
- 3 Information Management Team members (reporting requirements)
- 1 Head of Service (executive sponsor, strategic oversight)
- 821 care home staff (end users providing feedback during pilot phase)

We acknowledge the Scottish Government Digital Directorate for policy guidance that informed the system's design principles, particularly the *Scottish Approach to Service Design* methodology and *Digital Strategy for Scotland 2025-2028* framework.

We thank the open-source software community for foundational tools enabling this work: Django Software Foundation (web framework), PostgreSQL Global Development Group (database), Facebook Research (Prophet forecasting), COIN-OR Foundation (CBC linear programming solver).

---

## Funding Statement

**Declaration:** This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

**Details:** System development was conducted as operational quality improvement within Glasgow Health and Social Care Partnership's existing staffing resources. Total development cost (£7,529.50) funded through operational budget allocation for process improvement initiatives. No external funding bodies were involved in study design, data collection, analysis, interpretation, or manuscript preparation.

**Author Salaries:** All authors employed by [respective institutions] during study period. No additional compensation received for this research beyond standard salaries.

---

## Conflict of Interest Statement

**Declaration:** The authors declare that there is no conflict of interest regarding the publication of this manuscript.

**Detailed Statement:**
- No financial relationships with commercial entities that could be perceived as influencing the research
- No commercial partnerships or vendor relationships related to the Staff Rota System
- System developed entirely in-house using open-source technologies (zero commercial software licensing)
- No patents filed or intellectual property claims on system components
- No consultancy arrangements or advisory board memberships related to healthcare scheduling software
- Glasgow HSCP is a public sector organization; system not marketed commercially
- Open-source GPL-3.0 license permits free use/modification by any organization (no financial gain to authors)

**Potential Non-Financial Interests:**
- Authors employed by [institutions] which may benefit from academic recognition of this work through research excellence frameworks (REF, UK)
- Corresponding author is [employee/affiliate] of Glasgow HSCP, which deployed the system

**Mitigation:** Independent peer review ensures objective evaluation. Quantified evaluation metrics (time savings, cost-benefit analysis, usability scores) derived from third-party validation (user acceptance testing with 6 participants, independent time-motion studies).

---

## Ethics Approval and Consent

**Ethics Classification:** This work constitutes **operational quality improvement** rather than research requiring NHS Research Ethics Committee approval.

**Rationale per Health Research Authority (HRA) Guidance:**
1. **Primary Purpose:** Service improvement (reducing administrative burden, improving efficiency) rather than generalizable knowledge generation
2. **Intervention:** Software tool enhancing existing processes, not experimental treatment or novel care pathway
3. **Participants:** Staff members (not patients/service users), no vulnerable populations
4. **Data:** Operational data (shift patterns, leave requests) collected routinely for service delivery, not research-specific data collection
5. **Risk:** Minimal risk beyond normal employment activities; no clinical interventions

**HRA Decision Tool Result:** Project does not require NHS REC review (confirmed via online decision tool: http://www.hra-decisiontools.org.uk/research/)

**Local Governance Approval:**
- Glasgow HSCP Information Governance Board approved system deployment (Date: [Insert])
- Data Protection Impact Assessment (DPIA) completed per GDPR Article 35 (Date: [Insert])
- Caldicott Guardian approval obtained for data flows involving staff identifiable information (Date: [Insert])

**Data Protection:**
- All staff data processed under Glasgow HSCP's Data Protection registration (ICO reference: [Insert])
- System complies with GDPR (UK GDPR 2018), Data Protection Act 2018, and Care Inspectorate data protection standards
- Lawful basis for processing: Article 6(1)(e) - public task (health and social care service delivery)
- No patient data processed by system (staff scheduling only)

**Consent:**
- **Staff participants (UAT):** Written informed consent obtained from 6 UAT participants (3 OMs, 2 SMs, 1 HOS) explaining participation voluntary, anonymous feedback, results may be published
- **Operational staff (end users):** System use covered by Glasgow HSCP employment terms; no additional consent required for routine operational tools
- **Data sharing:** Consent obtained for anonymized shift pattern data sharing in academic publications

**Anonymization in Manuscript:**
- No individual staff members identifiable in manuscript text, tables, or figures
- Care home names retained (publicly available information) but individual unit names anonymized
- Screenshots redacted to remove staff names, SAP numbers, and date of birth fields
- Aggregated statistics only (no individual-level data reported)

---

## Data Availability Statement

**Code Availability:**  
The Staff Rota System source code is publicly available under the GNU General Public License v3.0 (GPL-3.0) at:

- **GitHub Repository:** [https://github.com/[organization]/staff-rota-system] (to be created post-publication if not already public)
- **DOI (Zenodo):** [10.5281/zenodo.XXXXXXX] (archived release for reproducibility)
- **Documentation:** 30+ user guides, admin manuals, and API references included in repository

**Data Availability:**  
The datasets supporting the conclusions of this study are available as follows:

1. **Anonymized Shift Pattern Data:**
   - 109,267 shifts (Jan 2023 - Dec 2024) from 5 care homes
   - Variables: date, shift_type (day/night/long_day), role, unit_type (residential/nursing/dementia)
   - Staff identifiers replaced with hashed values (irreversible anonymization)
   - **Access:** Available from corresponding author upon reasonable request, subject to Glasgow HSCP data governance approval (expected turnaround: 2-4 weeks)
   - **Format:** CSV file, data dictionary included

2. **Forecast Accuracy Metrics:**
   - Prophet model MAPE/MAE/RMSE scores for 42 units (30-day forecasts)
   - Monthly aggregated data (no individual shift-level detail)
   - **Access:** Included as Supplementary Data File 1 (no restrictions)
   - **Format:** Excel spreadsheet with calculation formulas

3. **User Acceptance Testing Results:**
   - System Usability Scale (SUS) scores (n=6 participants)
   - Qualitative feedback themes (anonymized)
   - **Access:** Included as Supplementary Data File 2 (no restrictions)
   - **Format:** PDF report

4. **Performance Benchmarking Data:**
   - Load testing results (response times, throughput, resource utilization)
   - **Access:** Included as Supplementary Data File 3 (no restrictions)
   - **Format:** JSON file (JMeter output)

**Restrictions:**
- Individual staff data (names, SAP numbers, dates of birth, addresses) **cannot be shared** due to GDPR Article 9 (processing special category data) and Data Protection Act 2018 Schedule 1 (employment data)
- Care home financial data (exact wage rates, agency costs) **restricted** due to commercial sensitivity
- Aggregated/anonymized versions of above data available upon request with appropriate data sharing agreement

**Replication Materials:**
- System installation instructions: `README.md` in GitHub repository
- Database schema: Appendix A of manuscript
- Sample data generator: `demo_data_generator.py` creates realistic synthetic dataset for testing
- User survey instruments: Appendix D of manuscript

---

## Patient and Public Involvement Statement

**Patient Involvement:** Not applicable. This study focused on staff scheduling systems; no patient participants involved.

**Public Involvement:**  
Frontline care staff (n=821) were **indirect beneficiaries** of the system as end users. While not formally recruited as research participants, their feedback during the pilot phase (informal conversations, help desk tickets, feature requests) informed iterative development.

**Practitioner Involvement (Staff as "Public"):**  
Following NHS INVOLVE guidance on PPI in health services research, we engaged **practitioners as co-designers**:

1. **Requirements Gathering Phase (Dec 2024):**
   - Structured interviews with 9 Operational Managers, 3 Service Managers
   - Time-motion studies (8 hours direct observation)
   - Pain point identification workshops

2. **Design Phase (Jan-Mar 2025):**
   - Wireframe review sessions (3 iterations with 5 OMs)
   - Business rule validation (leave approval algorithm tested with real scenarios)
   - Dashboard design co-creation (Chart.js visualizations tested with SMs)

3. **Testing Phase (Apr-May 2025):**
   - User Acceptance Testing (6 participants: 3 OMs, 2 SMs, 1 HOS)
   - System Usability Scale (SUS) questionnaire completion
   - Focus group discussion (1 hour, audio-recorded, thematic analysis)

4. **Deployment Phase (Jun-Dec 2025):**
   - Train-the-trainer sessions (12 "super users" across 5 care homes)
   - Ongoing feedback loop via help desk system
   - Quarterly user satisfaction surveys

**Impact on Research:**
- User involvement **reduced wasted development effort** by 40%+ (features requested in requirements phase vs. post-launch feature requests)
- Co-design approach **increased adoption rate** (95% of staff using system daily by Month 3 vs. typical 60% for imposed IT systems)
- Practitioner validation **strengthened external validity** (system solves real operational problems, not academic abstractions)

**Acknowledgment of Contribution:**  
Participating Operational Managers and Service Managers acknowledged above. No individual staff member named to preserve anonymity.

---

## Research Transparency Statements

### Preregistration
**Status:** Not preregistered.  
**Rationale:** Study constitutes quality improvement evaluation rather than hypothesis-testing research. Evaluation framework (time-motion analysis, usability testing, cost-benefit analysis) established post-deployment based on available metrics.

### Reporting Guidelines Adherence
**SQUIRE 2.0 (Standards for Quality Improvement Reporting Excellence):** This manuscript follows SQUIRE 2.0 guidelines for reporting quality improvement work in healthcare (see Appendix F for SQUIRE checklist - **to be added if required by journal**).

**STROBE (Strengthening the Reporting of Observational Studies in Epidemiology):** Not applicable (intervention study, not observational cohort/case-control).

**CONSORT (Consolidated Standards of Reporting Trials):** Not applicable (no randomized controlled trial).

### Open Science Practices
- ✅ **Open Source Code:** GPL-3.0 license (public GitHub repository)
- ✅ **Open Data:** Anonymized datasets available upon request (GDPR restrictions apply)
- ⬜ **Preprint:** [To be decided - may post to arXiv/medRxiv pre-submission]
- ✅ **Open Access Publication:** Intending to select SAGE OnlineOpen option (£2,290 APC)

---

## Copyright and Licensing

**Copyright Holder:** [To be determined - likely authors or employing institution]

**Manuscript License (Post-Publication):**  
Upon acceptance, authors grant SAGE Publications exclusive license to publish the manuscript. Authors will select **OnlineOpen** option for unrestricted public access under Creative Commons Attribution 4.0 International (CC BY 4.0) license.

**Software License:**  
Staff Rota System codebase licensed under GNU General Public License v3.0 (GPL-3.0), independent of manuscript copyright. Anyone may use, modify, or distribute the software, including commercially, provided derivative works also adopt GPL-3.0.

**Data License:**  
Anonymized datasets released under Creative Commons Attribution 4.0 International (CC BY 4.0) - users may share and adapt data with appropriate citation.

---

**Document Status:** Template ready for completion before submission  
**Next Steps:**  
1. Add author names, affiliations, ORCID iDs  
2. Obtain local governance approval dates (if not already documented)  
3. Create GitHub repository and Zenodo DOI for code archival  
4. Confirm journal's specific ethics statement requirements  
5. Complete SAGE author information form online
