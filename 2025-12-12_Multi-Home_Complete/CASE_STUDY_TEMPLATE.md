# Case Study Template
**Purpose:** Document pilot customer success for HSCP marketing  

---

## CASE STUDY STRUCTURE

---

# [Care Home Name] Reduces Scheduling Time by 89% with ML-Enhanced Staff Rota System

**Industry:** Residential Care  
**Location:** Glasgow, Scotland  
**Size:** [X] beds, [Y] staff  
**Implementation:** [Month Year]  
**Results:** £[X] annual savings, [Y]% time reduction  

---

## 📋 THE CHALLENGE

### Organization Background
[Care Home Name] is a [X]-bed residential care facility in Glasgow serving [elderly/dementia/learning disability] residents. With [Y] permanent staff and [Z] regular bank/agency workers, the operations management team faced significant scheduling challenges.

### Pain Points

**Before implementing the system:**

**1. Manual Scheduling Burden**
- Operations Manager spent **25-30 hours per week** creating 4-week rotas in Excel
- Constant interruptions from staff requesting shift changes
- Last-minute scrambling to cover unexpected absences
- **Quote:** *"I was spending more time on the rota than on resident care. Something had to change."* - [Name, Title]

**2. Unpredictable Costs**
- Agency usage averaging **12-15% of shifts** at premium rates (£35-50/hour vs £14-18/hour permanent)
- Excessive overtime creating budget overruns
- No forecasting capability - reactive hiring only
- **Impact:** £[X] annual overspend on agency costs

**3. Compliance Risks**
- Training expiry dates tracked in paper files
- Supervision sessions scheduled manually (often missed)
- Right-to-work documents scattered across filing cabinets
- **Risk:** CQC inspection gaps, potential regulatory action

**4. Staff Dissatisfaction**
- Rotas published only 2 weeks in advance (staff wanted 4-6 weeks)
- Frequent last-minute changes
- Difficulty requesting leave (paper forms, slow approval)
- **Result:** Higher turnover, recruitment costs averaging £3,000-5,000 per hire

### Business Impact
**Total annual cost of scheduling inefficiencies:** Estimated £[X]
- Manager time: £[X]
- Excess agency: £[X]
- Overtime premium: £[X]
- Turnover costs: £[X]

---

## 💡 THE SOLUTION

### Why They Chose Our System

[Care Home Name] evaluated three options:

| Option | Cost | Decision |
|--------|------|----------|
| **Commercial SaaS** (RotaMaster, PlanDay) | £3,000-5,000/year | ❌ Expensive, vendor lock-in |
| **Build In-House** | £50,000+ development | ❌ Too expensive, risky |
| **Our Open-Source System** | £0 pilot, £2,000/year support | ✅ **Selected** |

**Key selection criteria:**
1. **No vendor lock-in** - Open source ownership
2. **ML forecasting** - Unique feature vs competitors
3. **Proven results** - 109,000+ shifts processed in testing
4. **Risk-free pilot** - 3 months free to validate
5. **Scottish focus** - Built for UK care regulations

### Implementation Timeline

**Week 1: Setup**
- Deployed on care home's existing server (Ubuntu VM)
- PostgreSQL database configured
- SSL certificate installed
- Initial data import (250 staff records, 3 months historical shifts)

**Week 2: Customization**
- Configured 6 care units (residential wings)
- Set up shift patterns (Early: 7am-3pm, Late: 3pm-11pm, Night: 11pm-7am)
- Imported training requirements (Manual Handling, Safeguarding, First Aid)
- Applied care home branding (logo, colors)

**Week 3: Training**
- **Day 1:** Operations Manager + Deputy Manager (6 hours hands-on training)
- **Day 2:** 10 senior care workers (mobile app training)
- Written user guides provided
- Video tutorials recorded for future staff

**Week 4: Go-Live**
- First auto-generated rota created (4-week schedule in 45 minutes vs 25 hours manual)
- Staff onboarded to mobile app (85% adoption in first week)
- Daily check-ins with implementation team

**Months 2-3: Optimization**
- ML forecasting trained on historical data
- Automated compliance alerts configured
- Report templates customized for management team
- Weekly check-ins reduced to bi-weekly

**Total implementation time:** 3 weeks to go-live, 3 months to full optimization

---

## 📊 THE RESULTS

### Quantified Outcomes (After 3 Months)

**1. Time Savings**

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Weekly scheduling time | 25-30 hours | 2-3 hours | **89% reduction** |
| Leave request processing | 5 hours/week | 15 min/week | **95% reduction** |
| Compliance tracking | 8 hours/week | 1 hour/week | **87% reduction** |
| Report generation | 4 hours/week | 10 min/week | **96% reduction** |

**Total manager time saved:** 35-40 hours/week = **£37,440/year** @ £36/hour

**Quote:** *"I now spend 3 hours on the rota instead of 25. That's 22 hours I can focus on resident care and staff development."* - [Operations Manager Name]

**2. Cost Savings**

| Category | Before | After | Annual Savings |
|----------|--------|-------|----------------|
| Agency usage | 12% of shifts | 7% of shifts | **£24,000** |
| Overtime costs | £18,000/year | £11,000/year | **£7,000** |
| Manager overtime | £8,000/year | £2,000/year | **£6,000** |
| Recruitment (turnover) | 5 hires/year | 3 hires/year | **£8,000** |

**Total annual savings:** £45,000 (first year, expected to increase as ML improves)

**ROI:** Pilot was free, ongoing cost £2,000/year = **2,150% ROI**

**3. Staff Satisfaction**

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Schedule notice period | 2 weeks | 4-6 weeks | **+100%** |
| Mobile app adoption | N/A | 92% | - |
| Staff rating "Schedule predictability" | 2.3/5 | 4.1/5 | **+78%** |
| Voluntary turnover rate | 28%/year | 18%/year | **-36%** |

**Quote:** *"The app is brilliant. I can check my shifts, swap with colleagues, and request leave without chasing the manager."* - [Care Worker Name]

**4. Compliance Improvements**

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Training compliance rate | 76% | 94% | **+18 points** |
| Supervision sessions on time | 62% | 88% | **+26 points** |
| Time to generate CQC report | 4 hours | 10 minutes | **96% faster** |

**Quote:** *"The automated alerts mean I never miss a training renewal. Our last CQC inspection was the smoothest we've ever had."* - [Operations Manager]

**5. Operational Efficiency**

**ML Forecasting Impact:**
- System predicted staffing surge for Christmas period **4 weeks in advance**
- Enabled proactive hiring of 3 temporary staff vs last-minute agency
- Saved £3,200 in agency premiums for December alone

**Shift Coverage:**
- Unfilled shifts reduced from 8-12/month to 2-3/month
- Shift swap requests processed automatically (95% approved within 2 hours vs 24-48 hours manual)

---

## 🎯 KEY SUCCESS FACTORS

### What Made This Work

**1. Leadership Buy-In**
Operations Manager championed the system, led training, encouraged staff adoption.

**2. Comprehensive Training**
2 full days on-site, hands-on practice, ongoing support for 3 months.

**3. Data Quality**
Clean import of historical shift data enabled ML to learn patterns quickly.

**4. Staff Engagement**
Mobile app made it easy for staff to adopt (92% using app within 2 weeks).

**5. Ongoing Support**
Weekly check-ins during first month, bi-weekly in months 2-3, ensured smooth operation.

### Challenges & How We Overcame Them

**Challenge 1: Initial Staff Resistance**
*"Some senior staff were skeptical of 'another new system.'"*

**Solution:** 
- Demonstrated time savings in first week
- Mobile app's ease of use won them over
- Early adopters became champions

**Challenge 2: Historical Data Gaps**
*"We only had 2 months of shift history in Excel."*

**Solution:**
- Imported what was available
- ML learned patterns within 4 weeks
- Forecasting accuracy improved month-over-month

**Challenge 3: Server Performance**
*"Initial server was under-spec (2GB RAM)."*

**Solution:**
- Upgraded to 4GB RAM (£10/month additional cost)
- Performance improved significantly
- Recommendation: 4GB minimum from day 1

---

## 💬 TESTIMONIALS

### Operations Manager
> *"This system has transformed how we manage our team. I've gone from spending 25 hours a week on the rota to just 2-3 hours. The ML forecasting is incredible - it predicted our Christmas staffing surge 4 weeks ahead, saving us thousands in agency costs. I can't imagine going back to Excel."*
> 
> **[Name, Operations Manager]**  
> **[Care Home Name]**

### Deputy Manager
> *"The compliance dashboard is a game-changer. I get alerts 30 days before training expires, so we can plan renewals properly. Our CQC inspection last month was the smoothest we've ever had - I generated all required reports in 10 minutes."*
> 
> **[Name, Deputy Manager]**

### Senior Care Worker
> *"The mobile app is so easy to use. I can see my shifts 4 weeks ahead, swap with colleagues if I need to, and request leave without filling out paper forms. It's made my life much easier."*
> 
> **[Name, Senior Care Worker]**

### Care Home Manager (Strategic)
> *"The ROI is undeniable. We're saving £45,000 a year and my operations team is spending time on care quality instead of spreadsheets. I'd recommend this to any care provider."*
> 
> **[Name, Care Home Manager]**

---

## 📈 LONG-TERM IMPACT (6-12 Months)

### After 6 Months:
- **ML accuracy improved:** Forecasting MAPE reduced from 28% to 19%
- **Agency usage down to 5%** (vs 12% pre-system)
- **Staff turnover reduced to 15%/year** (vs 28% pre-system)
- **Total savings increased to £52,000/year** as system optimized

### After 12 Months:
- **Expanded to second care home** in the group
- **Group-wide visibility** into staffing across both homes
- **Cross-home shift coverage** (staff can pick up shifts at either location)
- **£95,000 total group savings** (2 homes)

---

## 🚀 WHAT'S NEXT FOR [CARE HOME NAME]

**Future Plans:**
1. **Integration with HR system** (automatic new starter onboarding)
2. **Payroll export** (auto-calculate hours worked for payroll)
3. **Advanced analytics** (predict optimal staffing levels by season)
4. **Third care home** onboarding planned for Q2 2026

**Quote:** *"We're exploring how to integrate with our payroll system to fully automate the end-to-end process from scheduling to payment."* - [Operations Manager]

---

## 📋 SYSTEM FEATURES USED

### Most Valuable Features (Ranked by User Feedback):

1. **Auto-Scheduling** ⭐⭐⭐⭐⭐
   - Generates 4-week rotas in minutes
   - Respects staff availability, preferences, working time regs
   - Manager just reviews and adjusts vs building from scratch

2. **ML Forecasting** ⭐⭐⭐⭐⭐
   - Predicts staffing needs 4 weeks ahead
   - Alerts to high-risk days (holidays, seasonal patterns)
   - Enables proactive hiring vs reactive agency bookings

3. **Mobile App** ⭐⭐⭐⭐⭐
   - 92% staff adoption
   - View shifts, request leave, swap shifts
   - Push notifications for changes

4. **Compliance Dashboard** ⭐⭐⭐⭐⭐
   - Automated training expiry alerts (30-day advance)
   - Supervision session tracking
   - One-click CQC reports

5. **Leave Management** ⭐⭐⭐⭐
   - Staff request via app
   - Manager approves in 2 clicks
   - Auto-checks coverage before approving

6. **Reporting** ⭐⭐⭐⭐
   - Real-time agency usage dashboard
   - Overtime tracking
   - Staff hours reports for payroll

---

## 🏆 AWARDS & RECOGNITION

**[If applicable, add any awards or recognition the care home received after implementation]**

- Finalist: Care Home Awards 2026 - "Innovation in Operations"
- CQC Rating: Improved from "Good" to "Outstanding" (staffing cited as strength)

---

## 📞 WANT SIMILAR RESULTS?

If you're a care provider in Scotland facing similar challenges, we'd love to help.

**Contact:**
- **Email:** [your.email@domain.com]
- **Phone:** [Your number]
- **Demo:** demo.staffrotascotland.co.uk
- **Website:** staffrotascotland.co.uk

**Special Offer:** Limited pilot program available (£10,000 value, no cost)

---

## APPENDIX: TECHNICAL DETAILS

### System Specifications
- **Platform:** Django 4.2 (Python web framework)
- **Database:** PostgreSQL 14
- **Hosting:** Ubuntu 22.04 LTS server (4GB RAM, 2 CPU cores)
- **Mobile:** Progressive Web App (works on iOS/Android, no app store required)
- **Security:** SSL encryption, 2FA, role-based access control
- **Uptime:** 99.7% over 3-month pilot

### Integration Points
- **HR System:** CSV export/import (manual during pilot, API planned)
- **Payroll:** Excel export of hours worked
- **Email:** Automated shift notifications, alert emails

### Data Migration
- **Staff records:** 250 imported from Excel
- **Historical shifts:** 3 months imported for ML training
- **Training records:** 180 qualifications imported
- **Time to migrate:** 4 hours (with data cleaning)

---

## MEDIA ASSETS

### Photos (With Permission):
- [ ] Operations Manager using scheduling screen
- [ ] Care worker using mobile app
- [ ] Compliance dashboard screenshot
- [ ] Before/After: Excel rota vs generated rota

### Video (Optional):
- [ ] 2-minute testimonial from Operations Manager
- [ ] 30-second mobile app demo by care worker

### Press Release (If Significant):
```
FOR IMMEDIATE RELEASE

Glasgow Care Home Reduces Admin Time by 89% with AI-Powered Scheduling

[Care Home Name] saves £45,000 annually using open-source ML forecasting system

GLASGOW, [Date] - [Care Home Name], a [X]-bed residential care facility, 
has achieved a 89% reduction in scheduling time and £45,000 in annual 
savings after implementing an AI-enhanced staff rota system.

[Quote from Care Home Manager]

The system uses machine learning to forecast staffing needs 4 weeks in 
advance, enabling proactive hiring and reducing expensive agency usage 
from 12% to 7% of shifts.

[Additional details]

For more information: [contact]
```

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | [Date] | Initial draft for review |
| 2.0 | [Date] | Added 6-month results |
| 3.0 | [Date] | Added testimonials, photos |
| 4.0 | [Date] | Final version for publication |

---

**USAGE RIGHTS:**

This case study may be used for:
- ✅ Marketing materials (website, brochures)
- ✅ Sales presentations to prospective clients
- ✅ Press releases and media outreach
- ✅ Conference presentations
- ✅ Academic publications

With the following conditions:
- [ ] Care home name anonymized (if requested): Use "[Glasgow Care Home A]"
- [ ] Photos require written consent from individuals
- [ ] Financial figures can be presented as ranges (e.g., "£40-50k savings")
- [ ] Care home has right to review before publication

---

**TEMPLATE INSTRUCTIONS:**

1. **Conduct end-of-pilot interview** (1 hour) to gather:
   - Quantitative metrics (time saved, costs reduced)
   - Qualitative feedback (quotes, experiences)
   - Challenges and solutions
   - Future plans

2. **Compile data** from:
   - System usage logs (hours saved calculated from timestamps)
   - Financial reports (agency usage before/after)
   - Staff surveys (satisfaction scores)
   - Manager reports

3. **Draft case study** using this template

4. **Review with care home** (allow 1-2 weeks for feedback)

5. **Revise and finalize**

6. **Obtain written permission** to publish (see usage rights above)

7. **Publish** on:
   - Your website (case studies page)
   - LinkedIn (company page + personal profiles)
   - Sales materials
   - Pitch decks for HSCP

8. **Promote**:
   - Email to prospects: "See how [Care Home] saved £45k"
   - Social media posts
   - Include in HSCP pitch

---

**TARGET: 2-3 case studies from pilot program by Month 6**

Use these to demonstrate proven results when pitching Glasgow HSCP.
