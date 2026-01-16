# Penetration Testing Request for Proposal (RFP)
**Staff Rota System - NHS/HSCP Deployment**  
**Prepared:** 6 January 2026  
**RFP Issue Date:** January 2026  
**Proposal Deadline:** TBD  
**Testing Window:** February-March 2026

---

## 1. Executive Summary

Glasgow Health & Social Care Partnership (HSCP) is deploying a custom-built Staff Rota Management System for care home operations. As part of NHS Cyber Essentials compliance and preparation for pilot deployment with CGI as corporate IT partner, we require independent penetration testing services.

**System Overview:**
- **Application Type:** Django 5.2+ web application (Python 3.14)
- **Database:** PostgreSQL
- **Deployment:** Linux server, HTTPS/TLS
- **Users:** 821 staff across 5 care homes (pilot phase)
- **Data Sensitivity:** Personal data (GDPR), staffing records, operational data
- **Regulatory Context:** NHS Scotland, Care Inspectorate, Local Government

---

## 2. Project Objectives

### 2.1 Primary Goals
1. **NHS Cyber Essentials Compliance** - Validate security controls meet NHS Digital standards
2. **Vulnerability Identification** - Discover security weaknesses before production deployment
3. **Risk Assessment** - Quantify risks for HSCP leadership and CGI partnership
4. **Remediation Roadmap** - Provide actionable recommendations with severity ratings

### 2.2 Success Criteria
- ✅ Comprehensive security assessment covering OWASP Top 10
- ✅ NHS Digital Technology Assessment Criteria (DTAC) alignment validation
- ✅ GDPR data protection controls verification
- ✅ Clear, actionable report suitable for non-technical stakeholders
- ✅ Re-test option for critical findings

---

## 3. Scope of Testing

### 3.1 In-Scope Systems

**Web Application:**
- **URL:** https://[deployment-domain] (TBD - staging environment)
- **Technology Stack:**
  - Frontend: Bootstrap 5, JavaScript, Progressive Web App (PWA)
  - Backend: Django 5.2+, Python 3.14
  - Database: PostgreSQL
  - Caching: Redis (if deployed)
  - Search: Elasticsearch (if deployed)
  
**Testing Accounts:**
- Staff user (limited permissions)
- Senior Care Worker (shift lead permissions)
- Manager (care home management)
- Operational Manager (multi-home oversight)
- Head of Service (executive access)
- Admin (system administration)

**API Endpoints:**
- REST API v1 (`/api/v1/integration/`, `/api/v1/mobile/`)
- Webhooks (`/api/webhooks/`)
- OAuth 2.0 authentication endpoints

### 3.2 Testing Focus Areas

**Priority 1 (Critical):**
1. **Authentication & Authorization**
   - Multi-factor authentication (django-otp) bypass attempts
   - Account lockout mechanism (django-axes) validation
   - Session management and token security
   - Password policy enforcement
   - Role-Based Access Control (RBAC) privilege escalation
   - API authentication (OAuth 2.0, API keys)

2. **Data Protection**
   - SQL injection vulnerabilities (despite ORM usage)
   - Cross-Site Scripting (XSS) attacks
   - Data encryption in transit (TLS configuration)
   - Sensitive data exposure (PII, staffing data)
   - GDPR right to deletion/export functionality security

3. **Access Control**
   - Care home data isolation (multi-tenancy boundaries)
   - Object-level permission bypass
   - Horizontal privilege escalation (access other homes' data)
   - Vertical privilege escalation (staff → manager → admin)

**Priority 2 (High):**
4. **Input Validation**
   - Cross-Site Request Forgery (CSRF)
   - Server-Side Request Forgery (SSRF)
   - File upload vulnerabilities (document management)
   - Command injection
   - Template injection

5. **Business Logic**
   - Shift manipulation vulnerabilities
   - Leave request approval bypass
   - Overtime offer gaming
   - Budget forecast tampering
   - Audit log manipulation/deletion

6. **API Security**
   - Rate limiting bypass (60/min, 1000/hour)
   - API authentication bypass
   - Mass assignment vulnerabilities
   - Webhook injection/replay attacks
   - CORS misconfiguration

**Priority 3 (Medium):**
7. **Configuration & Deployment**
   - Security header validation (HSTS, CSP, X-Frame-Options)
   - TLS/SSL configuration strength
   - Default credentials
   - Debug mode exposure
   - Error message information disclosure
   - Directory traversal

8. **Denial of Service (DoS)**
   - Application-layer DoS resistance
   - Resource exhaustion attacks
   - Query performance abuse (e.g., Prophet forecasting endpoints)

### 3.3 Out of Scope
❌ Social engineering attacks on staff  
❌ Physical security of hosting infrastructure  
❌ Third-party services (Twilio SMS, email providers)  
❌ Distributed Denial of Service (DDoS) testing  
❌ Testing against production systems (staging only)  

---

## 4. Testing Methodology

### 4.1 Required Standards
- **OWASP Testing Guide** (latest version)
- **OWASP Top 10** (2021 or later)
- **NHS Digital Cyber Security Standards**
- **NCSC Penetration Testing Guidance**

### 4.2 Testing Approach
1. **Reconnaissance** (1-2 days)
   - Technology fingerprinting
   - Public information gathering
   - Architecture review (documentation provided)

2. **Vulnerability Assessment** (3-5 days)
   - Automated scanning (Burp Suite, OWASP ZAP, Nessus)
   - Manual testing of critical functions
   - Code review (if white-box testing agreed)

3. **Exploitation** (2-3 days)
   - Proof-of-concept development for high/critical findings
   - Privilege escalation attempts
   - Data exfiltration scenarios

4. **Reporting** (2-3 days)
   - Executive summary for leadership
   - Technical findings with CVSS scores
   - Remediation recommendations
   - Re-test plan

### 4.3 Testing Types
**Preferred:** Grey-box testing (credentials + documentation provided)  
**Alternative:** Black-box testing (no credentials, external attacker perspective)  
**Optional:** White-box testing (source code access for deeper analysis)

---

## 5. Supplier Requirements

### 5.1 Mandatory Qualifications
✅ **CREST Certification** (Council of Registered Ethical Security Testers)  
  - OR **CHECK Scheme** approval (NCSC)  
  - OR **NCSC Certified Professional**  

✅ **NHS Experience** - Previous penetration testing for NHS organizations  

✅ **Public Sector Clearance** - Team members with SC clearance preferred  

✅ **Professional Indemnity Insurance** - Minimum £5M coverage  

### 5.2 Desired Experience
- Django/Python web application testing
- Healthcare sector compliance (GDPR, NHS DSP Toolkit)
- Multi-tenant application security assessment
- API security testing (REST, OAuth 2.0, webhooks)
- PostgreSQL database security

### 5.3 Team Composition
- **Lead Penetration Tester** (minimum 5 years experience, CREST certified)
- **Application Security Specialist** (web application focus)
- **Minimum 2 testers** for quality assurance and peer review

---

## 6. Deliverables

### 6.1 Required Reports

**1. Executive Summary Report** (5-10 pages)
- Overall security posture (RAG rating)
- High-level findings summary
- Business risk assessment
- Compliance status (NHS Cyber Essentials readiness)
- Recommended actions with priorities

**2. Technical Report** (20-50 pages)
- Detailed vulnerability descriptions
- CVSS v3.1 scores for each finding
- Proof-of-concept screenshots/evidence
- Step-by-step reproduction instructions
- Remediation guidance (specific to Django/Python)
- Testing methodology and tools used

**3. Re-Test Report** (if required)
- Verification of remediation for critical/high findings
- Residual risk assessment

### 6.2 Presentation
- **Findings Presentation** (1-2 hours)
  - To technical team (developers, CGI infrastructure team)
  - To leadership (HSCP, CGI management) - non-technical summary

### 6.3 Ongoing Support
- **30-day consultation period** for remediation questions
- **Re-test of critical findings** (included in base price)

---

## 7. Logistics & Constraints

### 7.1 Timeline
| Phase | Duration | Target Dates |
|-------|----------|--------------|
| RFP Response Period | 2 weeks | Jan 6-20, 2026 |
| Supplier Selection | 1 week | Jan 20-27, 2026 |
| Kickoff & Planning | 1 week | Jan 27-Feb 3, 2026 |
| **Penetration Testing** | **2-3 weeks** | **Feb 3-24, 2026** |
| Report Delivery | 1 week | Feb 24-Mar 3, 2026 |
| Remediation Period | 2-4 weeks | Mar 3-31, 2026 |
| Re-Test (Critical Findings) | 3-5 days | Early April 2026 |

### 7.2 Testing Environment
- **Environment:** Dedicated staging server (isolated from production)
- **Access:** VPN access to staging environment (CGI-provided)
- **Availability:** 24/7 access during testing window
- **Test Data:** Anonymized production data, no real PII
- **Backup:** Daily backups during testing (rollback capability)

### 7.3 Communication
- **Primary Contact:** Dean Sockalingum (System Developer)
- **Technical Lead:** [CGI Technical Lead - TBD]
- **Project Manager:** [HSCP Project Manager - TBD]
- **Daily Standups:** 15-minute calls during active testing
- **Severity 1 Escalation:** Immediate notification for critical findings

### 7.4 Restrictions
- **Testing Hours:** No restrictions (24/7 testing permitted on staging)
- **DoS Testing:** Limited application-layer DoS only (pre-approved scenarios)
- **Data Handling:** No exfiltration of test data from environment
- **Confidentiality:** NDA required (HSCP/CGI sensitive information)

---

## 8. Commercial Requirements

### 8.1 Budget Range
**Indicative Budget:** £5,000 - £15,000 (excluding VAT)

### 8.2 Pricing Structure (Requested)
Please provide breakdown:
- **Daily Rate:** Per tester-day
- **Fixed Price:** Total cost for full engagement
- **Inclusions:**
  - Reconnaissance
  - Vulnerability assessment
  - Exploitation attempts
  - Executive + Technical reports
  - Findings presentation
  - Re-test (critical/high findings only)
  - 30-day consultation
  
- **Exclusions/Optional Add-ons:**
  - White-box source code review
  - Full re-test (all findings)
  - Infrastructure penetration testing
  - Additional support beyond 30 days

### 8.3 Payment Terms
- **Milestone 1 (25%):** Kickoff meeting completion
- **Milestone 2 (50%):** Testing completion and draft report delivery
- **Milestone 3 (25%):** Final report delivery and presentation

---

## 9. Proposal Evaluation Criteria

Proposals will be evaluated on the following weighted criteria:

| Criterion | Weight | Details |
|-----------|--------|---------|
| **Qualifications & Experience** | 30% | CREST/CHECK certification, NHS experience, team credentials |
| **Methodology & Approach** | 25% | Testing methodology, tools, comprehensiveness |
| **Price** | 20% | Value for money, clarity of pricing |
| **Deliverables Quality** | 15% | Sample reports, previous client references |
| **Timeline & Availability** | 10% | Ability to meet Feb-Mar 2026 window |

**Minimum Requirements to Pass:**
- ✅ CREST or CHECK certification
- ✅ Minimum 2 NHS/public sector references
- ✅ £5M professional indemnity insurance
- ✅ Availability within testing window

---

## 10. System Context (Background)

### 10.1 Current Security Posture
**Implemented Controls:**
- Multi-factor authentication (django-otp)
- Account lockout after 5 failed attempts (django-axes)
- Role-Based Access Control (6 role types)
- HTTPS/TLS ready
- Security headers (HSTS, CSP, X-Frame-Options)
- CSRF protection (Django built-in)
- SQL injection prevention (ORM-based)
- XSS protection (template escaping)
- Audit logging (django-auditlog)
- Rate limiting (60/min, 1000/hour)
- Session security (secure cookies)

**Known Gaps (To Be Validated):**
- ⚠️ No previous independent penetration test
- ⚠️ Penetration testing findings may reveal additional vulnerabilities
- ⚠️ TLS configuration not independently verified
- ⚠️ Third-party dependency vulnerabilities (automated scanning only)

### 10.2 Compliance Targets
- **NHS Cyber Essentials** - Required for NHS deployment
- **GDPR Article 32** - Security of processing (encryption, pseudonymization)
- **NHS Digital DTAC** - Digital Technology Assessment Criteria
- **ISO 27001 Alignment** - Information security best practices

### 10.3 Post-Test Roadmap
1. **Remediation Phase** (2-4 weeks) - Fix critical/high findings
2. **Re-Test** (3-5 days) - Verify remediation
3. **Cyber Essentials Plus Application** (6-8 weeks) - Full certification
4. **Pilot Deployment** (April-May 2026) - Glasgow HSCP care homes
5. **Production Rollout** (Summer 2026) - Full HSCP deployment

---

## 11. Proposal Submission

### 11.1 Required Documents
1. **Company Profile** - Certifications, experience, team CVs
2. **Methodology Document** - Detailed testing approach
3. **Sample Report** - Redacted example from previous engagement
4. **Commercial Proposal** - Pricing breakdown, payment terms
5. **References** - Minimum 2 NHS/public sector clients
6. **Insurance Certificate** - Professional indemnity (£5M minimum)
7. **NDA Acceptance** - Signed confidentiality agreement

### 11.2 Submission Details
**Contact:** Dean Sockalingum  
**Email:** [Insert contact email]  
**Deadline:** [Insert date - typically 2 weeks from RFP issue]  
**Format:** PDF, maximum 50 pages  
**Questions:** Submit questions by [Insert date - 1 week before deadline]

### 11.3 Evaluation Process
1. **Initial Review** (1 week) - Compliance with mandatory requirements
2. **Shortlisting** (3 days) - Top 3 suppliers selected
3. **Interviews** (Optional) - Technical presentation/Q&A
4. **Award Decision** (3 days) - Notification to successful bidder
5. **Contract Execution** (1 week) - Terms negotiation and signing

---

## 12. Academic & Business Case Context

### 12.1 Why This Matters for Academic Paper
This penetration test will provide:
- **Evidence-based security validation** for academic publication
- **Quantifiable risk metrics** (CVSS scores, vulnerability counts)
- **NHS compliance validation** demonstrating production-readiness
- **Comparison data** vs commercial alternatives (security posture)
- **Lessons learned** for public sector custom development

**Target Publication:** Academic paper on Staff Rota System development and ROI

### 12.2 Business Case Impact
Penetration testing strengthens the business case by:
- **De-risking CGI partnership** - Professional security validation
- **Demonstrating due diligence** - NHS governance compliance
- **Enabling insurance/indemnity** - Professional risk assessment completed
- **Supporting procurement** - Security evidence for other HSCPs
- **Justifying investment** - £5-15K vs potential breach costs (£millions)

**ROI Context:**
- System saves £590K/year (quantified)
- Penetration test: £5-15K (0.8-2.5% of annual savings)
- Commercial alternatives: £36-120K/year + unknown security posture

### 12.3 CGI Partnership Value
- **Trust building** - Independent validation of security claims
- **Shared responsibility model** - Clear delineation of security controls
- **Integration planning** - Security findings inform LDAP/SSO/SIEM work
- **Risk transfer** - Professional report reduces CGI liability concerns

---

## 13. Next Steps

### For HSCP/CGI:
1. ☐ Review and approve RFP document
2. ☐ Finalize contact details and submission email
3. ☐ Set RFP issue date and proposal deadline
4. ☐ Identify 3-5 CREST/CHECK certified firms to invite
5. ☐ Prepare staging environment (by late January)
6. ☐ Arrange VPN access for successful bidder
7. ☐ Brief CGI infrastructure team on testing window

### For Bidders:
1. ☐ Submit questions by [Insert Q&A deadline]
2. ☐ Prepare proposal (company profile, methodology, pricing, references)
3. ☐ Submit proposal by [Insert deadline]
4. ☐ Prepare for potential interview/presentation

---

## Appendix A: System Architecture Overview

**High-Level Architecture:**
```
┌─────────────────────────────────────────────────────────┐
│                  Internet (HTTPS/TLS)                    │
└─────────────────────────────────────────────────────────┘
                           │
                  ┌────────▼────────┐
                  │  Load Balancer  │
                  │     (Nginx)     │
                  └────────┬────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
┌───────▼────────┐                  ┌────────▼────────┐
│  Django App    │                  │  Django App     │
│   Server 1     │◄────────────────►│   Server 2      │
│  (Primary)     │   Session Sync   │  (Replica)      │
└───────┬────────┘                  └────────┬────────┘
        │                                     │
        └──────────────────┬──────────────────┘
                           │
                  ┌────────▼────────┐
                  │   PostgreSQL    │
                  │   (Primary +    │
                  │    Standby)     │
                  └─────────────────┘
```

**Technology Stack Summary:**
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript (Vanilla + jQuery)
- **Backend:** Django 5.2+, Python 3.14, Gunicorn WSGI
- **Database:** PostgreSQL 14+
- **Caching:** Redis (optional)
- **Search:** Elasticsearch (optional)
- **Security:** django-otp (2FA), django-axes (lockout), django-auditlog
- **API:** Django REST Framework, OAuth 2.0

---

## Appendix B: Sample Vulnerability Severity Guide

Please use CVSS v3.1 for scoring. Expected severity distribution:

| Severity | CVSS Score | Example Findings | Remediation SLA |
|----------|------------|------------------|-----------------|
| **Critical** | 9.0-10.0 | Authentication bypass, SQL injection with data access | 48 hours |
| **High** | 7.0-8.9 | Privilege escalation, XSS with session hijacking | 1 week |
| **Medium** | 4.0-6.9 | CSRF on non-critical functions, information disclosure | 2 weeks |
| **Low** | 0.1-3.9 | Security header missing (non-exploitable), version disclosure | 4 weeks |
| **Informational** | 0.0 | Best practice recommendations | Backlog |

---

## Appendix C: References & Resources

**NHS Security Standards:**
- NHS Digital Cyber Essentials: https://digital.nhs.uk/cyber-security
- DTAC Framework: https://digital.nhs.uk/services/digital-technology-assessment-criteria-dtac

**OWASP Resources:**
- OWASP Top 10 (2021): https://owasp.org/www-project-top-ten/
- OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/

**CREST Certification:**
- CREST Certified Testers: https://www.crest-approved.org/

**NCSC Guidance:**
- CHECK Scheme: https://www.ncsc.gov.uk/information/check-penetration-testing

---

**Document Version:** 1.0  
**Author:** Dean Sockalingum (System Developer)  
**Reviewed By:** [Insert reviewer names]  
**Approval:** [Insert approval signatures/dates]  

**Confidentiality:** This document contains sensitive system information. Distribution limited to RFP recipients under NDA.
