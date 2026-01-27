# Outstanding Issues - Staff Rota System
**Last Updated:** January 9, 2026

## 🔴 HIGH PRIORITY - Post-Presentation

### 1. Weekly Rota Grid Alignment Issue
**Status:** DEFERRED  
**Priority:** High  
**Description:** Management sections and staff names appear at different vertical positions across day columns in the weekly schedule grid.

**Problem Details:**
- Some days have leave banners, others don't, causing content to shift
- CSS Grid and Flexbox attempts were overridden by JavaScript
- Inline styles were applied but still get overridden after page load
- JavaScript appears to be manipulating the DOM after initial render

**Attempted Solutions (All Failed):**
1. CSS Grid with fixed row positions - overridden by JS
2. Flexbox with order property - overridden by JS
3. Simple block layout with min-heights - overridden by JS
4. Inline styles with !important - still overridden
5. JavaScript lock with MutationObserver - still shifts
6. Complete template rebuild - caused 500 error

**Next Steps:**
- Identify the specific JavaScript causing DOM manipulation
- Consider server-side rendering to ensure identical HTML structure
- May need to disable conflicting JavaScript entirely
- Consider using a completely different layout approach (e.g., separate tables per section)

**Files Involved:**
- `/home/staff-rota-system/scheduling/templates/scheduling/rota_view.html`
- Multiple backups available with .backup_* extensions

**Server:** demo.therota.co.uk (159.65.18.80)

---

## ✅ COMPLETED

### Safari Mobile Login Issue
**Status:** RESOLVED  
**Date:** January 9, 2026  
**Solution:** Changed `SESSION_COOKIE_SAMESITE` from 'Strict' to 'Lax' in settings.py
- File: `/home/staff-rota-system/rotasystems/settings.py` (Line 207)
- Backup: settings.py.backup_safari

### Guidance Documents Visibility
**Status:** RESOLVED  
**Date:** January 9, 2026  
**Solution:** Added 19 missing guidance documents to hardcoded list in views.py
- All 36 guidance documents now visible
- File: `/home/staff-rota-system/scheduling/views.py` (628KB, 16,177 lines)
- Gunicorn auto-recycle implemented (--max-requests 1000) to prevent module caching

### Server Optimization
**Status:** COMPLETED  
**Date:** January 9, 2026  
**Changes:**
- Reduced workers from 3 to 2
- Increased timeout to 120s
- Added --max-requests 1000 --max-requests-jitter 100 for worker recycling
- Prevents dashboard timeouts and module caching issues

---

## 📋 NOTES

### Production Environment
- **Server:** demo.therota.co.uk (159.65.18.80)
- **Admin:** SAP 000541 / Greenball99##
- **Database:** PostgreSQL staffrota_demo (1,352 users, 28,337 shifts)
- **Gunicorn Command:**
  ```bash
  /home/staff-rota-system/venv/bin/gunicorn \
    --workers 2 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --bind unix:/home/staff-rota-system/staffrota.sock \
    rotasystems.wsgi:application \
    --daemon \
    --access-logfile /home/staff-rota-system/logs/gunicorn-access.log \
    --error-logfile /home/staff-rota-system/logs/gunicorn-error.log
  ```

### Presentation
- **Date:** Next week (moved from January 10, 2026)
- **Status:** Site ready with core functionality working
- **Known Cosmetic Issue:** Rota grid alignment (non-blocking)

---

## 🎯 FUTURE ENHANCEMENTS

### 1. Modular TQM Add-ons for Product Upselling
**Status:** PLANNING  
**Priority:** Medium (Post-Production Launch)  
**Type:** Revenue Enhancement / Product Expansion

**Objective:** Build modular Total Quality Management (TQM) sections as paid add-ons to increase product value and create upsell opportunities.

**Quality Framework Foundation:**
Our TQM approach is underpinned by Scottish health and social care quality frameworks:

- **Health Improvement Scotland (HIS)** - [Improvement Resources](https://www.healthcareimprovementscotland.scot/improving-care/improvement-resources/)
  - Quality Management Systems (QMS) for consistent and coordinated quality approach
  - Scottish Patient Safety Programme (SPSP) for safety and reliability
  - Person-led care principles
  - Community care quality standards (frailty, dementia, future care planning)
  
- **NHS Education Scotland (NES)** - [Quality Improvement Zone](https://learn.nes.nhs.scot/741/quality-improvement-zone)
  - Systematic quality improvement methodologies
  - Quality improvement tools and frameworks
  - eLearning modules and educational resources
  - Evidence-based improvement programs
  
- **Care Inspectorate Scotland**
  - Quality standards compliance
  - Inspection frameworks integration
  - National Care Standards alignment

**Strategic Alignment:**
All TQM modules will be designed to:
- Support Care Inspectorate compliance requirements
- Align with HIS Quality Management Systems framework
- Utilize NES Quality Improvement Zone methodologies
- Enable evidence-based quality improvement cycles (Plan-Do-Study-Act)
- Provide audit trails for regulatory compliance
- Support continuous professional development (CPD) requirements

**Potential TQM Modules:**

- **Quality Audits & Inspections**
  - Scheduled audit tracking aligned with Care Inspectorate timelines
  - Compliance checklists based on National Care Standards
  - Audit findings and corrective actions (linked to HIS QMS framework)
  - Integration with Care Inspectorate requirements
  - Evidence repository for inspection readiness
  - Self-assessment tools using HIS quality indicators

- **Incident Management**
  - Incident reporting and logging (aligned with SPSP safety methodology)
  - Investigation tracking using root cause analysis tools from NES QI Zone
  - Significant adverse event management
  - Corrective and preventive action planning
  - Trend analysis and reporting against safety metrics
  - Duty of Candour compliance tracking

- **Training & Competency Management**
  - Training matrix and scheduling (SSSC registration requirements)
  - Competency assessments aligned with Scottish Social Services Council (SSSC) frameworks
  - Mandatory training tracking (Care Inspectorate requirements)
  - CPD (Continuing Professional Development) logs for SSSC registration
  - Skills gap analysis
  - Learning resources from NES Quality Improvement Zone integration
  - Induction and supervision tracking

- **Document Control**
  - Policy and procedure version control
  - Document approval workflows
  - Expiry tracking and renewal alerts
  - Staff acknowledgment and understanding tracking
  - Links to national guidance (HIS, SSSC, Scottish Government)
  - Document library aligned with Care Inspectorate themes

- **Risk Management**
  - Risk register (clinical, operational, reputational)
  - Risk assessments (health & safety, clinical, environmental, financial)
  - Control measures tracking and effectiveness monitoring
  - Risk review scheduling aligned with HIS QMS cycles
  - Integration with incident management for trend identification
  - Board-level risk reporting

- **Performance Metrics & KPIs**
  - Quality indicators dashboard (aligned with National Health & Wellbeing Outcomes)
  - Benchmarking against Care Inspectorate quality themes
  - Custom metric builder for service-specific KPIs
  - Automated reporting for board and regulatory submissions
  - Real-time quality improvement tracking (PDSA cycles)
  - Scottish Patient Safety Programme metrics integration

- **Feedback & Complaints**
  - Resident/family feedback collection (person-led care principles from HIS)
  - Complaint logging and investigation
  - Resolution tracking with timescales
  - Trend analysis and learning
  - Integration with Can I Help You? Scottish Government initiative
  - Annual feedback reporting for Care Inspectorate

**Technical Considerations:**
- Design as pluggable Django apps with modular architecture
- Separate database migrations per module
- License key/subscription model for module activation
- API integration points for cross-module data sharing
- Consistent UI/UX with core rota system
- Integration with NES Quality Improvement Zone learning resources
- Data export capabilities for Care Inspectorate submissions
- Quality improvement (QI) tools library (PDSA cycles, fishbone diagrams, run charts, etc.)
- Mobile-responsive for frontline staff access
- Automated alert systems for compliance deadlines
- Audit trails for all quality-related activities

**Regulatory Compliance Features:**
- Care Inspectorate quality framework themes (Wellbeing, Leadership, Staff, Setting, Care & Support)
- Health & Social Care Standards alignment (Dignity & Respect, Compassion, Inclusion, Responsive Care, Wellbeing)
- SSSC Codes of Practice integration
- Duty of Candour statutory requirements
- GDPR and data protection compliance
- Public Services Reform (Social Care) requirements

**Business Model:**
- Base subscription: Core rota system
- Add-on modules: £X/month per module
- Module bundles: Discounted package deals (e.g., "Quality Assurance Bundle", "Compliance Bundle")
- Enterprise tier: All modules included
- Scottish care sector pricing competitive analysis required
- Potential partnership opportunities with HIS/NES for accredited quality improvement solutions

**Competitive Advantages:**
- Built specifically for Scottish care sector regulatory environment
- Integrated with Health Improvement Scotland frameworks
- Aligned with NES Quality Improvement methodologies
- Single system for rota AND quality management (reduces duplicate data entry)
- Real-time quality insights linked to staffing patterns
- Evidence-ready for Care Inspectorate inspections

**Next Steps:**
1. **Market Research Phase** (Q1 2026)
   - Survey existing customers for most wanted quality management features
   - Interview care home managers about Care Inspectorate pain points
   - Analyze Care Inspectorate inspection reports for common improvement areas
   - Engage with HIS and NES for potential collaboration/accreditation

2. **Framework Mapping Phase** (Q1-Q2 2026)
   - Map all modules to Care Inspectorate quality themes
   - Align features with Health & Social Care Standards
   - Integrate NES Quality Improvement Zone tools and methodologies
   - Review SSSC requirements for training and competency tracking

3. **Competitive Analysis** (Q2 2026)
   - Review existing quality management systems in care sector
   - Identify gaps in current market offerings
   - Determine pricing strategy based on competitor analysis
   - Identify unique selling propositions (Scottish-specific compliance, integrated rota+quality)

4. **Technical Architecture** (Q2 2026)
   - Design modular Django app framework
   - Create API specification for inter-module communication
   - Plan database schema for quality data
   - Design user permission models for quality roles

5. **Prioritization & Roadmap** (Q2-Q3 2026)
   - Rank modules by customer demand and development effort
   - Create phased rollout plan
   - Identify quick wins vs. strategic long-term builds

6. **MVP Development** (Q3 2026)
   - Build first module (likely Quality Audits or Incident Management)
   - Integrate with HIS quality frameworks
   - Implement PDSA cycle tracking from NES methodologies

7. **Beta Testing** (Q4 2026)
   - Pilot with select care homes
   - Gather feedback on usability and compliance value
   - Refine based on real-world Care Inspectorate preparation use

8. **Launch & Scaling** (Q1 2027)
   - Marketing campaign emphasizing Scottish compliance
   - Pricing and packaging finalization
   - Customer success and training programs
   - Continuous module development based on roadmap

**Dependencies:**
- Core system must be stable in production
- Payment/subscription infrastructure needed
- Module activation/licensing system
- Customer account management portal

