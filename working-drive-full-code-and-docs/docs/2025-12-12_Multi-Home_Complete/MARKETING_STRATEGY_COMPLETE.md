# Marketing & Sales Strategy - Complete Package
**Date:** January 8, 2026  
**Purpose:** Go-to-market roadmap for HSCP sales  
**Status:** Ready to execute  

---

## 🎯 STRATEGIC POSITIONING SUMMARY

### Core Recommendation:
**DO NOT** host HSCP data on your own domain (SaaS model)  
**DO** offer on-premise/self-hosted implementation services

### Why This Matters:
- **Data sovereignty** is critical for Scottish public sector
- **Procurement speed** is 3-6x faster for software purchase vs SaaS subscription
- **Open source** eliminates vendor lock-in (major public sector concern)
- **Cost model** favors one-time CapEx over monthly OpEx

---

## 📚 COMPLETE DELIVERABLES CREATED

### 1. **HSCP_DEPLOYMENT_STRATEGY.md** ✅
**Purpose:** Strategic business case for self-hosted vs SaaS

**Key Sections:**
- Deployment model comparison (SaaS vs self-hosted)
- Scottish public sector procurement realities
- Competitive positioning matrix
- Domain strategy (marketing site vs client deployments)
- Go-to-market phases (Pilot → HSCP → Framework)
- Realistic pricing for HSCP market (£30-40k implementation)
- Critical success factors

**Target Audience:** You (business strategy decisions)

---

### 2. **DEMO_DOMAIN_SETUP_GUIDE.md** ✅
**Purpose:** Technical implementation guide for demo infrastructure

**Key Sections:**
- Domain registration recommendations (`staffrotascotland.co.uk`)
- DigitalOcean/AWS Lightsail hosting setup
- Django deployment on Ubuntu 22.04 LTS
- PostgreSQL, Redis, Nginx, SSL configuration
- Demo data requirements (5 care homes, sample users)
- Auto-reset script (nightly demo refresh)
- Security considerations (rate limiting, captcha)
- Cost summary (£360/year total)
- Analytics setup (Google Analytics 4, Hotjar)
- Launch checklist (4-week timeline)

**Target Audience:** Technical implementation (you or hired developer)

**Investment Required:**
- Domain: £10-15/year
- Hosting: £30/month (DigitalOcean 4GB droplet)
- Total: £360-375/year
- Time: 30-35 hours over 3 weeks

---

### 3. **PILOT_PROGRAM_PROPOSAL_TEMPLATE.md** ✅
**Purpose:** Sales materials for free pilot approach

**Key Sections:**
- Initial outreach email template
- Formal proposal document (customizable)
- Pilot scope and deliverables (£10k value, free)
- Timeline (3 months, 13 weeks detailed)
- Success criteria (quantitative & qualitative)
- Simple 1-page pilot agreement
- Follow-up email templates
- Pilot evaluation scorecard

**Target Audience:** Care home operators (2-3 for free pilot)

**Value Proposition:**
- You invest: £10k in services (free to them)
- They invest: ~30 hours time over 3 months
- You gain: Case studies, testimonials, HSCP proof points
- They gain: Working system, option to continue at £2k/year

---

### 4. **CASE_STUDY_TEMPLATE.md** ✅
**Purpose:** Document pilot successes for HSCP marketing

**Key Sections:**
- Challenge/Solution/Results format
- Quantified outcomes (time savings, cost reductions)
- Testimonial collection
- Before/after metrics
- Technical details appendix
- Media assets (photos, videos, press release)
- Usage rights agreement

**Target Audience:** HSCP decision-makers (proof of concept)

**Usage:**
- Include in HSCP pitch deck
- Publish on marketing website
- LinkedIn/social media promotion
- Sales presentations

---

### 5. **HSCP_PITCH_DECK_OUTLINE.md** ✅
**Purpose:** Presentation for Glasgow City HSCP contract (£85k)

**Slide Breakdown (20 slides + 10 backup):**
1. Title slide
2. Executive summary (the ask: £85k for £539k return)
3. The problem (£241k annual waste on manual processes)
4. Current state challenges (5 pain points)
5. Why existing solutions fail (commercial SaaS comparison)
6. Our solution (production-ready, not development)
7. How it works (4-layer architecture)
8. ML forecasting in action (the killer feature)
9. Pilot customer results (3 case studies)
10. Financial analysis (£539k savings breakdown)
11. Implementation plan (6-month rollout)
12. Risk analysis (low-risk mitigations)
13. Why open source matters (strategic advantage)
14. Data sovereignty & security (critical for public sector)
15. Competitive analysis (vs PCS/Access/RotaMaster)
16. Support & maintenance (£15k/year optional)
17. Next steps & decision timeline
18. Investment summary (recap)
19. Call to action (approve pilot February 2026)
20. Q&A

**Target Audience:** Commissioning Manager, Head of Service, Digital Lead

**Expected Outcome:** Pilot approval (£20k for 2 homes), full rollout decision after 3 months

---

## 🚀 EXECUTION ROADMAP

### Phase 1: Demo Infrastructure (Weeks 1-3)

**Week 1: Domain & Hosting**
- [ ] Register `staffrotascotland.co.uk` (£10-15)
- [ ] Set up DigitalOcean account (£200 free credit)
- [ ] Deploy Ubuntu 22.04 droplet (4GB RAM)
- [ ] Configure DNS records

**Week 2: Demo Deployment**
- [ ] Install Django, PostgreSQL, Redis, Nginx
- [ ] Deploy your staff-rota-system codebase
- [ ] Create demo data fixture (5 homes, 250 users)
- [ ] Configure SSL with Let's Encrypt
- [ ] Set up auto-reset script (nightly refresh)

**Week 3: Marketing Site**
- [ ] Build simple HTML site (Hugo or Jekyll)
- [ ] Create features, pricing, case studies pages
- [ ] Set up Google Analytics 4
- [ ] Test mobile responsiveness
- [ ] Soft launch to test users

**Deliverable:** `demo.staffrotascotland.co.uk` live and functional

---

### Phase 2: Pilot Program (Months 1-3)

**Month 1: Pilot Recruitment**
- [ ] Identify 5-10 Glasgow care home prospects
- [ ] Send outreach emails (use template from PILOT_PROGRAM_PROPOSAL_TEMPLATE.md)
- [ ] Conduct discovery calls (15-30 minutes each)
- [ ] Demo system (30 minutes each)
- [ ] Select 2-3 pilot customers
- [ ] Sign pilot agreements

**Month 2: Pilot Implementation**
- [ ] Deploy at pilot customer sites (1 week each)
- [ ] Conduct on-site training (2 days each)
- [ ] Weekly check-in calls
- [ ] Monitor usage analytics
- [ ] Gather feedback

**Month 3: Pilot Results**
- [ ] Measure against success criteria
- [ ] Conduct end-of-pilot interviews
- [ ] Write case studies (use template)
- [ ] Collect testimonials
- [ ] Get written permission to publish

**Deliverable:** 2-3 case studies with quantified ROI

---

### Phase 3: HSCP Pitch (Month 4)

**Preparation:**
- [ ] Create pitch deck PowerPoint (from HSCP_PITCH_DECK_OUTLINE.md)
- [ ] Prepare demo walkthrough (15-minute video)
- [ ] Print case studies and 1-page executive summary
- [ ] Research Glasgow HSCP decision-makers (LinkedIn)

**Outreach:**
- [ ] Email Commissioning Manager with case studies
- [ ] Request 45-minute presentation meeting
- [ ] CC Head of Service, Digital Transformation Lead
- [ ] Offer to present to wider team if interested

**Presentation:**
- [ ] Deliver pitch (30-45 minutes)
- [ ] Demo system live
- [ ] Q&A (15-30 minutes)
- [ ] Leave behind: case studies, proposal, executive summary

**Follow-Up:**
- [ ] Send thank you email same day
- [ ] Answer questions within 24 hours
- [ ] Schedule decision timeline call (1 week later)

**Deliverable:** Pilot approval (£20k for 2 HSCP homes) or feedback for refinement

---

### Phase 4: HSCP Pilot & Rollout (Months 5-10)

**If Pilot Approved:**

**Month 5-7: HSCP Pilot (2 homes)**
- [ ] Deploy at Orchard Grove + Meadowburn
- [ ] 2 days on-site training each
- [ ] Weekly check-ins
- [ ] Document results

**Month 8: Pilot Review**
- [ ] Present results to HSCP decision-makers
- [ ] Recommend full rollout if successful
- [ ] Negotiate final pricing (£65k for remaining 3 homes)

**Month 9-10: Full Rollout (if approved)**
- [ ] Deploy at Hawthorn House, Riverside, Victoria Gardens
- [ ] Parallel implementation
- [ ] Handover to support contract

**Deliverable:** £85k contract complete, £539k annual savings delivering

---

### Phase 5: Scale & Framework (Months 11-18)

**Month 11-12: Refine & Document**
- [ ] Update case studies with long-term results
- [ ] Create video testimonials
- [ ] Publish Glasgow HSCP success story
- [ ] Develop reusable implementation playbook

**Month 13-15: Apply to Frameworks**
- [ ] Scottish Government Digital Marketplace application
- [ ] NHS National Services Scotland frameworks
- [ ] Care Inspectorate approved vendors list

**Month 16-18: Scale**
- [ ] Approach other Scottish HSCPs (Edinburgh, Aberdeen)
- [ ] Replicate Glasgow model
- [ ] Build partner network (IT suppliers who can install)
- [ ] Consider hiring implementation consultant

**Deliverable:** National presence, framework-approved vendor status

---

## 💰 FINANCIAL PROJECTIONS

### Investment Required (Your Costs):

**Phase 1: Demo Infrastructure**
- Domain & hosting: £375/year
- Development time: 35 hours @ £50/hour = £1,750
- **Subtotal: £2,125 Year 1**

**Phase 2: Pilot Program (Free to Customers)**
- Implementation services: 3 customers × £10k = £30,000
- Travel & expenses: £1,500
- **Subtotal: £31,500**

**Total Investment (Months 1-4): £33,625**

### Revenue Potential:

**HSCP Contract (Glasgow - Year 1):**
- Pilot: £20,000 (2 homes)
- Rollout: £65,000 (3 homes)
- **Subtotal: £85,000**

**Support Contracts (Year 2+):**
- Glasgow HSCP: £15,000/year
- 3 pilot customers: 3 × £2,000 = £6,000/year
- **Subtotal: £21,000/year recurring**

**ROI:**
- Investment: £33,625
- Year 1 Revenue: £85,000
- **Year 1 Profit: £51,375 (153% ROI)**
- **Year 2+ Recurring: £21,000/year (passive income)**

### Scale Potential (Year 2-3):

**If you replicate to 3 more HSCPs:**
- Edinburgh HSCP: £85k (6 homes)
- Aberdeen HSCP: £60k (4 homes)
- Dundee HSCP: £50k (3 homes)
- **Additional Revenue: £195,000**
- **Support: £30,000/year recurring**

**Year 3 Potential:**
- Total implementation revenue: £280k
- Total recurring support: £51k/year
- **Your annual income: £51k+ without new sales**

---

## 📊 SUCCESS METRICS (Track These)

### Demo Site (Month 1-3):
- [ ] Unique visitors: Target 200+
- [ ] Demo logins: Target 50+
- [ ] Average session duration: Target 10+ minutes
- [ ] Contact form submissions: Target 10+
- [ ] Demo → Pilot conversion: Target 20%

### Pilot Program (Month 2-4):
- [ ] Outreach emails sent: Target 20
- [ ] Discovery calls conducted: Target 10
- [ ] Demos delivered: Target 8
- [ ] Pilots signed: Target 3
- [ ] Pilots successful: Target 2+ (67%)

### HSCP Pitch (Month 4):
- [ ] Pitch meetings secured: Target 2 (Glasgow + backup)
- [ ] Decision-maker engagement: Target 3+ attendees per meeting
- [ ] Pilot approval: Target 1 (Glasgow)

### Long-Term (Month 12):
- [ ] Total implementation revenue: Target £100k+
- [ ] Recurring support revenue: Target £20k/year
- [ ] HSCP customers: Target 2
- [ ] Framework applications: Target 2 submitted

---

## 🎯 CRITICAL SUCCESS FACTORS

### What Will Make This Work:

1. **Pilot Quality**
   - Over-deliver on free pilots (£10k value)
   - Obsess over customer success
   - Document everything for case studies

2. **HSCP Relationships**
   - Research decision-makers thoroughly
   - Understand their procurement processes
   - Speak their language (data sovereignty, ROI, risk mitigation)

3. **Demo Excellence**
   - Fast, reliable, polished demo site
   - Realistic data (looks like their operation)
   - Mobile app works flawlessly

4. **Positioning Discipline**
   - ALWAYS emphasize open source advantage
   - NEVER compete on price alone (compete on value + control)
   - ALWAYS offer self-hosted deployment (avoid SaaS model)

5. **Patience**
   - Public sector moves slowly (6-12 month sales cycles)
   - Multiple stakeholders need buy-in
   - Procurement processes are rigid
   - Build relationships, not just transactions

---

## ⚠️ COMMON MISTAKES TO AVOID

### DON'T:
- ❌ Try to host HSCP data on your servers (SaaS)
- ❌ Promise monthly subscriptions (harder to approve than one-time)
- ❌ Ignore procurement frameworks (apply early)
- ❌ Over-promise timelines (under-promise, over-deliver)
- ❌ Compete on price alone (you'll lose to offshore)
- ❌ Skip the pilot (direct to HSCP is too risky)
- ❌ Neglect case study documentation
- ❌ Forget to get written testimonials

### DO:
- ✅ Position as implementation service (not SaaS)
- ✅ Emphasize data sovereignty and open source
- ✅ Offer free pilots to build proof points
- ✅ Get testimonials and case studies early
- ✅ Show NHS/Care Inspectorate integration
- ✅ Provide TCO comparison vs competitors
- ✅ Be patient with public sector timelines
- ✅ Build relationships with decision-makers

---

## 📞 IMMEDIATE NEXT ACTIONS (This Week)

### Day 1 (Today):
- [ ] **Decision:** Approve £375/year demo infrastructure budget
- [ ] **Action:** Register `staffrotascotland.co.uk` domain
- [ ] **Action:** Create DigitalOcean account (£200 free credit)

### Day 2-3:
- [ ] Deploy demo instance (follow DEMO_DOMAIN_SETUP_GUIDE.md)
- [ ] Create demo data fixture from your existing test data
- [ ] Test all user roles and features

### Day 4-5:
- [ ] Build simple marketing site (Hugo or HTML template)
- [ ] Write homepage copy (features, benefits, CTA)
- [ ] Set up Google Analytics

### Weekend:
- [ ] Identify 10 Glasgow care home prospects
- [ ] Research contact info (managers on LinkedIn)
- [ ] Customize pilot outreach email for each

### Week 2:
- [ ] Send 10 outreach emails (staggered, not all at once)
- [ ] Follow up with calls after 3-4 days
- [ ] Book discovery calls with interested prospects

**Goal:** 3 discovery calls booked by end of Week 2

---

## 📋 TEMPLATES & RESOURCES CREATED

### Marketing Materials:
- ✅ **Domain setup guide** (technical deployment)
- ✅ **Demo configuration** (auto-reset, sample data)
- ✅ **Marketing site structure** (pages, content)

### Sales Materials:
- ✅ **Outreach email** (cold contact template)
- ✅ **Pilot proposal** (formal document, customizable)
- ✅ **Pilot agreement** (simple 1-page contract)
- ✅ **Follow-up emails** (interested, not interested, 1 week before pilot ends)

### HSCP Materials:
- ✅ **Pitch deck outline** (20 slides + 10 backup)
- ✅ **1-page executive summary** (leave-behind)
- ✅ **Financial analysis** (ROI calculator integrated)
- ✅ **FAQ preparation** (anticipated questions + answers)

### Post-Sale Materials:
- ✅ **Case study template** (challenge/solution/results)
- ✅ **Testimonial collection** (quotes, video script)
- ✅ **Pilot evaluation scorecard** (success metrics)

---

## 🎬 YOUR DECISION POINTS

### Immediate (This Week):
**Q1: Approve demo infrastructure spend (£375/year)?**
- YES → Register domain, set up hosting
- NO → Revisit business case

**Q2: Can you commit 35 hours over 3 weeks for demo setup?**
- YES → Start Week 1 implementation
- NO → Consider hiring developer (£1,750)

### Short-Term (Month 1):
**Q3: Willing to invest £30k in free pilots (3 × £10k)?**
- YES → Recruit pilot customers
- NO → Consider paid pilot model (£5k discounted implementation)

### Medium-Term (Month 4):
**Q4: If HSCP pilot approved, can you deliver on £85k contract?**
- YES → You have capacity/skills
- NO → Hire implementation consultant or partner

**Q5: After Year 1, pursue scaling or stay boutique?**
- SCALE → Apply to frameworks, hire team
- BOUTIQUE → 3-5 HSCP contracts, solo operation

---

## 📖 RECOMMENDED READING ORDER

**If you're starting now:**

1. Read **HSCP_DEPLOYMENT_STRATEGY.md** (understand why self-hosted)
2. Read **DEMO_DOMAIN_SETUP_GUIDE.md** (technical next steps)
3. Skim **PILOT_PROGRAM_PROPOSAL_TEMPLATE.md** (sales approach)
4. Review **HSCP_PITCH_DECK_OUTLINE.md** (end goal)

**When recruiting pilots:**
5. Customize **PILOT_PROGRAM_PROPOSAL_TEMPLATE.md** for each prospect
6. Send outreach emails
7. Use demo site to close

**After pilot success:**
8. Fill in **CASE_STUDY_TEMPLATE.md** with real results
9. Build **HSCP_PITCH_DECK** PowerPoint from outline
10. Pitch to Glasgow HSCP

---

## 🏆 FINAL RECOMMENDATION

### Your Go-to-Market Strategy (TL;DR):

**Model:** On-premise implementation services (NOT SaaS)

**Positioning:** "Open-source staff rota with professional implementation - same control as building in-house, 90% cheaper, production-ready today."

**Pricing:**
- Small care homes (10-50 users): £5-10k one-time
- HSCP (5 homes, 250+ users): £85k one-time
- Support (optional): £2-15k/year

**Timeline:**
- Month 1-3: Demo site + 3 free pilots
- Month 4: HSCP pitch
- Month 5-10: HSCP pilot + rollout (if approved)
- Month 11+: Scale to other HSCPs, apply to frameworks

**Investment:** £34k (demo + free pilots)  
**Year 1 Return:** £85k (Glasgow HSCP)  
**Year 1 Profit:** £51k (153% ROI)  
**Year 2+ Passive:** £21k/year (support contracts)

**Success Probability:**
- Demo site working: 95% (technical, you control)
- 1+ pilot success: 80% (free value proposition)
- HSCP pilot approval: 60% (with strong case studies)
- HSCP full contract: 80% (if pilot succeeds)

**Overall probability of £85k contract: ~38%** (0.95 × 0.80 × 0.60 × 0.80)

**Expected value: £32k** (£85k × 38%)  
**Investment: £34k**  
**Risk-adjusted breakeven**

**BUT:** If you execute well (great pilots, strong pitch), probability jumps to 60-70% → £51-59k expected value → positive ROI

---

## ✅ YOU NOW HAVE EVERYTHING YOU NEED

**Marketing Strategy:** ✅ HSCP_DEPLOYMENT_STRATEGY.md  
**Technical Setup:** ✅ DEMO_DOMAIN_SETUP_GUIDE.md  
**Sales Approach:** ✅ PILOT_PROGRAM_PROPOSAL_TEMPLATE.md  
**Proof Points:** ✅ CASE_STUDY_TEMPLATE.md  
**Closing Tool:** ✅ HSCP_PITCH_DECK_OUTLINE.md  

**Next Action:** Register `staffrotascotland.co.uk` and deploy demo this week.

**Question for You:** Ready to execute, or do you need help with any specific part?
