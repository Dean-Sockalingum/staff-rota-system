# User Testing Feedback & Enhancement Requests

**Document Purpose:** Track user feedback from SM/OM testing sessions and implementation status

**Testing Period:** December 2025 (Ongoing)  
**Test Environment:** Production system with 300 users across 5 care homes  
**Test Participants:** Service Managers (SM) and Operational Managers (OM)

---

## Enhancement Request Log

### Request #1: ML Forecasting in AI Chatbot
**Date Requested:** 22 December 2025  
**Requested By:** SM/OM User Testing Group  
**Priority:** HIGH  
**Status:** ✅ IMPLEMENTED (22 Dec 2025)

**Original Request:**
Users wanted access to Prophet ML forecasting predictions through the AI chatbot interface, rather than only through the dashboard.

**User Need:**
- Quick access to staffing forecasts without navigating to separate dashboard
- Natural language queries for demand predictions
- Instant shortage alerts via chat interface

**Implementation:**
Enhanced AI assistant (`scheduling/views/ai_assistant_api.py`) with:
1. `generate_staffing_forecast()` - Prophet predictions with confidence intervals
2. `check_staffing_shortage()` - ML-powered shortage detection
3. Query interpreter keywords: forecast, predict, shortage, understaffed

**New Queries Supported:**
- "What's the staffing forecast for next week?"
- "Will we be short-staffed tomorrow?"
- "Predict demand for next 30 days"
- "Are we understaffed on Monday?"

**User Impact:**
- SM/OM can access 7-30 day forecasts instantly via chat
- Proactive shortage alerts (compares predictions vs scheduled)
- Reduced time to identify staffing gaps (dashboard navigation eliminated)

**Technical Details:**
- Queries `StaffingForecast` model (Prophet predictions)
- Confidence interval analysis (flags >50% uncertainty)
- Unit-level shortage calculation (upper CI vs scheduled shifts)

**Validation:**
- Response format includes ML icon indicators (📊, ⚠️, ✅)
- Returns structured data + natural language summary
- Handles missing forecast data gracefully

---

## Testing Metrics

### User Acceptance Testing (UAT) Status

**Phase 1: Core Functionality** (Complete)
- ✅ Multi-home data isolation
- ✅ Leave auto-approval (70% automation rate)
- ✅ Role-based dashboards
- ✅ Shift scheduling

**Phase 2: ML Features** (In Progress)
- ✅ Prophet forecasting dashboard
- ✅ PuLP shift optimization
- ✅ ML chatbot integration (NEW - 22 Dec)
- ⏳ Performance monitoring
- ⏳ Model retraining workflow

**Phase 3: Production Readiness** (Scheduled)
- ⏳ Load testing (300+ concurrent users)
- ⏳ Security audit
- ⏳ Disaster recovery testing
- ⏳ Full system backup procedures

---

## Feedback Categories

### 1. Feature Requests (Pending)
*No additional requests at this time - testing ongoing*

### 2. Usability Issues (Pending)
*Awaiting feedback from ongoing testing*

### 3. Performance Issues (Pending)
*Monitoring dashboard response times (<1 second target)*

### 4. Bug Reports (Pending)
*No critical bugs reported during testing*

### 5. Training Needs (Pending)
*User training materials to be assessed after testing complete*

---

## Next Testing Phases

### Week 1 (22-29 Dec 2025)
- **Focus:** ML chatbot integration validation
- **Participants:** SM/OM users (5 homes)
- **Metrics:** Query success rate, response relevance, time savings

### Week 2 (30 Dec - 5 Jan 2026)
- **Focus:** Prophet forecast accuracy
- **Participants:** OM users
- **Metrics:** MAPE validation, confidence interval coverage

### Week 3 (6-12 Jan 2026)
- **Focus:** End-to-end workflow testing
- **Participants:** All user roles
- **Metrics:** Task completion time, user satisfaction scores

---

## User Satisfaction Scores

**Baseline (Pre-ML System):**
- Task completion time: 5.5 hours/day (manual scheduling)
- User satisfaction: Not measured
- Error rate: High (manual data entry)

**Current System (ML-Enhanced):**
- Task completion time: 40 minutes/day (87% reduction)
- User satisfaction: To be measured (SUS questionnaire planned)
- Error rate: Significantly reduced (automated validation)

**Target Metrics:**
- SUS Score: >70 (Above Average)
- Task time: <30 minutes/day
- Forecast accuracy: MAPE <20%

---

## Enhancement Request Template

**For New Requests:**

```
### Request #[NUMBER]: [TITLE]
**Date Requested:** [DATE]
**Requested By:** [USER ROLE/NAME]
**Priority:** [HIGH/MEDIUM/LOW]
**Status:** [PENDING/IN PROGRESS/IMPLEMENTED/DECLINED]

**Original Request:**
[Detailed description of user need]

**User Need:**
[Business justification]

**Proposed Implementation:**
[Technical approach]

**Implementation Status:**
[Progress updates]

**User Impact:**
[Expected benefits]
```

---

## Notes

- Testing is ongoing - this document will be updated as feedback is collected
- SM/OM users have direct access to submit requests via AI chatbot or email
- Critical issues escalated immediately to development team
- All enhancements tracked in git commits with reference to this document

**Last Updated:** 22 December 2025  
**Document Owner:** Dean Sockalingum  
**Review Frequency:** Weekly during testing phase
