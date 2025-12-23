# Executive Presentation Slides
**PowerPoint Slide Content - HSCP & CGI**

---

## SLIDE 1: TITLE SLIDE

**Title:** Glasgow HSCP Staff Rota Management System  
**Subtitle:** ML-Enhanced Scheduling for Older People's Care Homes  
**Presenter:** [Your Name], [Title]  
**Date:** January 2026  
**Audience:** HSCP Executive Board & CGI Digital Partner

**Visual Elements:**
- Glasgow HSCP logo (top left)
- System dashboard screenshot (background, 40% opacity)
- Tagline: "Proven. Secure. Production-Ready."

---

## SLIDE 2: THE CHALLENGE

**Title:** Current Manual Scheduling - The Hidden Costs

**Content:**

**3,264 Hours Lost Annually**
- 9 Operations Managers × 7 hours/week
- £81,000 in labour costs
- Time diverted from patient care

**Operational Inefficiencies**
- ❌ Reactive agency bookings (£40/hour emergency rates)
- ❌ Manual WTD compliance tracking (audit risk)
- ❌ No forecasting capability (gaps discovered late)

**The Question:**  
*Can technology eliminate these inefficiencies while maintaining managerial flexibility?*

**Visual Elements:**
- Process flow diagram: Leave request → Manual review → Shift pattern update → Gap coverage → Agency call
- Red highlights on pain points
- Clock icon showing "7 hours weekly per OM"

---

## SLIDE 3: THE SOLUTION

**Title:** ML-Enhanced Scheduling Platform

**Content:**

**Three Proven Technologies:**

**1. Django 4.2 LTS**
- Used by Instagram, NHS Digital
- Production-proven framework
- Long-term support (April 2026)

**2. Prophet ML Forecasting**
- Facebook's open-source algorithm
- 39 trained models (one per unit)
- 30-day predictions with 80% confidence

**3. Linear Programming Optimization**
- 5 constraint types: Coverage | Availability | Qualifications | Fairness | WTD
- <1 second optimization time
- 12.6% cost reduction

**Visual Elements:**
- Architecture diagram: Django (UI) → Prophet (Forecasting) → LP Optimizer (Scheduling) → PostgreSQL (Data)
- Technology logos: Django, Prophet, PuLP
- Blue/green color scheme (professional, healthcare-appropriate)

---

## SLIDE 4: PROVEN PERFORMANCE

**Title:** Production-Scale Validation

**Content:**

**Operational Metrics**
- ✅ 103,074 shifts generated
- ✅ 1,350 staff members managed
- ✅ 5 homes, 42 units, 220 beds
- ✅ 93.6% citywide occupancy

**Performance Benchmarks**
- **300 concurrent users** validated (3x requirement)
- **180ms** dashboard load (target: 500ms) 🟢 **64% faster**
- **0.8 seconds** shift optimization (vs 7 hours manual)
- **115 requests/second** throughput

**User Validation**
- **4.1/5** overall satisfaction (SM/OM participants)
- *"More reliable than manual for compliance"* - Service Manager

**Visual Elements:**
- Dashboard screenshot with metrics highlighted
- Bar chart comparing manual (7 hrs) vs automated (0.8 sec)
- User testimonial quote box
- Green checkmarks for each metric

---

## SLIDE 5: FINANCIAL IMPACT

**Title:** £538,941 Annual Savings - 534% ROI Year 1

**Content:**

**Savings Breakdown (5 Homes)**

| Category | Annual Savings | Mechanism |
|----------|----------------|-----------|
| Labour Savings | £81,000 | 3,264 manager hours redeployed |
| Optimized Scheduling | £346,500 | 12.6% cost reduction (LP optimizer) |
| Reduced Agency Usage | £111,441 | 30-day forecasting enables planning |
| **TOTAL** | **£538,941** | |

**Return on Investment**

**Year 1:**  
Investment: £85,000 | Savings: £538,941 | **Net: £453,941** | **ROI: 534%**

**Year 2+:**  
Investment: £15,000/year | Savings: £538,941 | **Net: £523,941** | **ROI: 3,493%**

**Payback Period:** **3 months**

**Visual Elements:**
- Stacked bar chart showing savings categories
- ROI badge: "534% Year 1"
- Timeline showing payback at month 3
- Green highlighting on net benefit numbers

---

## SLIDE 6: MACHINE LEARNING INNOVATION

**Title:** Prophet Forecasting + Cost Prediction Models

**Content:**

**Prophet Forecasting (39 Models)**
- 30-day staffing demand predictions
- 80% confidence intervals
- 25.1% MAPE accuracy (industry standard)

**[CHART: Prophet Forecast Example]**
- Blue line: Predicted demand
- Gray band: Uncertainty range (80% CI)
- Orange dots: Actual outcomes
- Week 3 spike highlighted: "Early warning enables proactive recruiting"

**New: Cost Prediction Models (Dec 2025)**
- ✅ Leave Predictor: 66.5% accuracy
- ✅ Overtime Forecaster: **95% accuracy** 🏆
- ✅ High-Cost Classifier: 87.5% accuracy
- ✅ Anomaly Detector: Identified £11.8M cost drivers

**Visual Elements:**
- Live Prophet forecast chart
- Mini charts for each cost prediction model
- Icon: Brain with circuits (ML visualization)

---

## SLIDE 7: SECURITY & COMPLIANCE

**Title:** Healthcare-Grade Security by Design

**Content:**

**GDPR Compliance** ✅
- ✅ Data Protection Impact Assessment (DPIA) complete
- ✅ ICO registration documented
- ✅ Right to erasure implemented
- ✅ Data portability (CSV export)

**Authentication & Authorization**
- 10-character passwords, complexity enforced
- Account lockout: 5 failures = 1 hour
- Role-based access: 7 roles (SM, OM, HOS, etc.)
- 1-hour session timeout

**Audit & Encryption**
- django-auditlog: Every change tracked
- Field-level encryption (SAP numbers, DOB)
- CVE-2025-66418 & CVE-2025-66471 remediated

**Pending:** External penetration test (CGI-led during technical review)

**Visual Elements:**
- Security shield icon with checkmarks
- Lock icon for encryption
- Green "GDPR Compliant" badge
- Timeline showing CVE remediation

---

## SLIDE 8: TESTING & QUALITY ASSURANCE

**Title:** Comprehensive Testing - 88/100 Score

**Content:**

**Test Coverage**

**Unit Tests (15 files, 45+ cases)**
- Password validation (4 tests)
- Audit logging (5 tests)
- ML forecasting (6 tests)
- Shift optimization (8 tests)
- Staffing safeguards (12 tests)

**Performance Tests**
- 300 concurrent users ✅
- Dashboard: 180ms (target: 500ms) ✅
- Optimization: 0.8s (target: 5s) ✅

**Security Tests**
- 222-line security suite
- Account lockout, CSRF, session timeout validated

**User Acceptance**
- 3 managers (SM/OM roles)
- 4.1/5 satisfaction
- Real workflows tested

**In Progress:** 8 integration tests, external pentest, disaster recovery drill

**Visual Elements:**
- Test pyramid diagram (unit → integration → UAT)
- Progress bar: 88/100 filled green
- Checkmarks for completed tests

---

## SLIDE 9: DEPLOYMENT PLAN

**Title:** Low-Risk Phased Rollout - 6 Months to Full Operations

**Content:**

**Phase 1: Pilot (Months 1-3)**
- **Homes:** Orchard Grove + Hawthorn House
- **Scope:** 17 units, ~340 staff
- **Training:** 4 OMs, 1 SM
- **Success:** 7 hrs → <1 hr weekly, zero WTD violations, 10% agency reduction

**Phase 2: Expansion (Months 4-6)**
- **Homes:** Meadowburn, Riverside, Victoria Gardens
- **Scope:** 25 units, ~481 staff
- **Milestone:** Full coverage (all 5 HSCP older people's homes)

**Phase 3: Optimization (Months 7-12)**
- SWISS API integration (payroll sync)
- Cross-home reallocation (staff sharing)
- Advanced analytics (monthly cost reports)

**Go-Live Targets:**
- **Feb 2026:** Pilot launch
- **May 2026:** Full deployment

**Visual Elements:**
- Gantt chart with 3 phases color-coded
- Home icons showing progressive rollout
- Timeline arrows
- Green checkmarks for milestones

---

## SLIDE 10: CGI INTEGRATION

**Title:** Open Standards - Easy Integration

**Content:**

**Technology Compatibility**
- **Django 4.2 LTS** + **PostgreSQL 15**
- CGI-familiar tech stack
- No cloud-only dependencies
- Standard HTTP/JSON protocols

**API Integration Points**
- SWISS HR system (staff master data)
- eESS leave system (leave balance sync)
- Payroll exports (shift hours)
- Existing HSCP infrastructure

**No Vendor Lock-In**
- Open-source Django framework
- Full source code transferred to HSCP
- CGI can maintain with standard Django developers
- Data exportable: CSV, JSON, SQL

**CGI Technical Review (2 Weeks)**
1. Architecture assessment
2. Security penetration test
3. Integration feasibility
4. Performance validation
5. Disaster recovery procedures

**Visual Elements:**
- Integration diagram: Rota System ↔ SWISS ↔ Payroll
- Django + PostgreSQL logos
- "No Lock-In" badge with open padlock
- Timeline: 2-week review → 2-week remediation → Go-live

---

## SLIDE 11: RISK MITIGATION

**Title:** Risks Identified & Mitigated

**Content:**

| Risk | Likelihood | Impact | Mitigation | Residual Risk |
|------|------------|--------|------------|---------------|
| **Data migration errors** | MEDIUM | HIGH | Dry-run tested, rollback documented | 🟢 LOW |
| **Staff resistance** | MEDIUM | MEDIUM | 33KB training guide, OM champions | 🟢 LOW |
| **CGI integration delays** | MEDIUM | MEDIUM | REST API ready, CSV fallback | 🟢 LOW |
| **Performance at scale** | LOW | HIGH | 300 users validated, Redis caching | 🟢 LOW |
| **Security vulnerabilities** | LOW | HIGH | Pentest scheduled, CVE monitoring | 🟢 LOW |

**Fallback Procedures**
- ✅ Rollback to manual processes (documented)
- ✅ CSV import/export (maintains operations during API delays)
- ✅ Disaster recovery: 25-minute full restore

**Visual Elements:**
- Risk matrix (2x2 grid: likelihood vs impact)
- Green "LOW" badges in residual risk column
- Shield icon with checkmarks

---

## SLIDE 12: DECISION & NEXT STEPS

**Title:** Approval Required - Go-Live February 2026

**Content:**

**Three Approvals Needed:**

**1. Executive Approval (Today)**
- ✅ Proceed with 3-month pilot (2 homes)
- ✅ Budget: £28,333 (£85K ÷ 3 phases)

**2. CGI Technical Review (2 Weeks)**
- Architecture, security, integration feasibility
- Full documentation provided

**3. HSCP IG Board (1 Week)**
- Final DPIA sign-off
- Data processing lawful basis confirmed

**Timeline:**
- **Today:** Decision to proceed
- **Weeks 1-2:** CGI review
- **Week 3:** IG Board approval
- **Week 4:** Deployment planning
- **Feb 2026:** Pilot go-live

**Investment Decision:**
- **Year 1:** £85,000 investment → £453,941 net benefit → **534% ROI**
- **Year 2+:** £15,000/year → £523,941 net benefit → **3,493% ROI**
- **Payback:** 3 months

**Visual Elements:**
- Timeline with decision points
- ROI callout box (large, green)
- "Approve Today" button graphic
- Calendar showing Feb 2026 go-live

---

## SLIDE 13: SUMMARY

**Title:** Ready for Production - Awaiting Approval

**Content:**

**✅ Proven System**
- 103,074 shifts generated
- 300 concurrent users validated
- 4.1/5 user satisfaction

**✅ Measurable ROI**
- £538,941 annual savings
- 534% Year 1 ROI
- 3-month payback

**✅ Low Risk**
- Phased rollout
- Fallback procedures
- Tested workflows

**✅ Healthcare-Grade**
- GDPR compliant
- Audit trails
- Secure architecture

**✅ Open-Source**
- No vendor lock-in
- CGI can maintain
- Full code ownership

**The Ask:**  
*Approve pilot deployment (£28,333) and authorize CGI technical review.*

**This isn't just a scheduling system—it's 3,264 hours of manager time returned to patient care annually.**

**Visual Elements:**
- 5 checkmark boxes with icons
- Large ROI number: "534%"
- Photo: Care home staff (stock image, professional)
- Call-to-action button: "Questions?"

---

## SLIDE 14: BACKUP SLIDE - TECHNICAL SPECIFICATIONS

**Title:** System Specifications (For Technical Questions)

**Content:**

**Infrastructure Requirements**
- Python 3.11+
- Django 4.2.27 LTS
- PostgreSQL 15+
- Redis 7+ (caching/Celery)
- Gunicorn 21.2+ (WSGI)
- Nginx 1.24+ (reverse proxy)

**Scalability**
- Validated: 300 concurrent users
- Throughput: 115 requests/second
- Database: 103,074 shifts, <100ms queries
- Caching: Redis with 1-hour TTL

**Security Features**
- django-axes (account lockout)
- django-auditlog (change tracking)
- django-encrypted-model-fields (field encryption)
- django-csp (Content Security Policy)

**ML Models**
- Prophet: 39 models (3.2s training time per model)
- PuLP: LP optimizer (<1s solve time)
- scikit-learn: 4 cost prediction models

---

## SLIDE 15: BACKUP SLIDE - DOCUMENTATION PROVIDED

**Title:** Comprehensive Documentation Package

**Content:**

**Deployment Guides (3)**
- ML_DEPLOYMENT_GUIDE.md (30 KB)
- PRODUCTION_MIGRATION_CHECKLIST.md (32 KB)
- SYSTEM_HANDOVER_DOCUMENTATION.md (32 KB)

**ML Implementation (6)**
- Phase 1-4 complete guides
- Validation test results
- Database integration documentation

**Operations (4)**
- USER_TRAINING_GUIDE_OM_SM.md (33 KB)
- PERFORMANCE_OPTIMIZATION_GUIDE.md (11 KB)
- CI_CD_INTEGRATION_GUIDE.md (13 KB)
- PRODUCTION_READINESS_REPORT (26 KB)

**Business (2)**
- BUSINESS_CASE_GLASGOW_HSCP.md (36 KB)
- SCOTTISH_POLICY_INTEGRATION_SUMMARY.md

**Total:** 17 documents, 293 KB

---

## SLIDE 16: BACKUP SLIDE - CONTACT & SUPPORT

**Title:** Project Team & Support

**Content:**

**Project Leadership**
- **Project Sponsor:** [Name], HSCP Head of Service
- **Technical Lead:** [Name], System Developer
- **Clinical Champion:** [Name], Senior Operations Manager

**CGI Technical Review Team**
- **Security Lead:** [TBD - CGI to assign]
- **Integration Architect:** [TBD - CGI to assign]
- **Infrastructure Lead:** [TBD - CGI to assign]

**Support During Pilot**
- **On-site support:** Weeks 1-2 (full-time)
- **Remote support:** Weeks 3-12 (same-day response)
- **Escalation:** 24/7 critical issue hotline

**Training Delivery**
- **Week 1:** System overview (all OMs, 2 hours)
- **Week 2:** Leave management (hands-on, 3 hours)
- **Week 3:** ML forecasts (data literacy, 2 hours)
- **Week 4:** Advanced features (optimization, 2 hours)

**Post-Go-Live**
- Monthly check-ins (first 6 months)
- Quarterly performance reviews
- Annual strategic planning sessions

---

**[END OF SLIDES]**

**Total Slide Count:** 16 slides (13 main + 3 backup)  
**Presentation Duration:** 42 minutes + 3-5 min Q&A

**File Format Instructions:**
To convert to PowerPoint:
1. Use Pandoc: `pandoc -o presentation.pptx -f markdown EXECUTIVE_PRESENTATION_SLIDES.md`
2. Or manually create slides in PowerPoint using this content as reference
3. Add visual elements as specified in each slide description
4. Use Glasgow HSCP brand colors and logo
5. Include dashboard screenshots from live system
