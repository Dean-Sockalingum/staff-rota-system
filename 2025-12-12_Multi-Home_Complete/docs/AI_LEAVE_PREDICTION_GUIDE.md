# AI-Powered Leave Approval Prediction - User Guide

## Overview

The AI Assistant now includes **intelligent leave approval prediction** to help staff choose the best dates for annual leave requests. Instead of submitting leave requests blindly and risking denial, staff can now check approval likelihood first.

## Features

### 1. **Leave Likelihood Prediction** 📊
Ask the AI chatbot about specific dates, and it will analyze:
- Current staffing levels for those dates
- Existing approved leave
- Your leave balance
- Coverage requirements
- Historical approval patterns
- Blackout periods (December, summer holidays)

### 2. **Conversational Interface** 💬
Natural language queries supported:
```
"Can I take leave from Dec 25 to Dec 27?"
"What are my chances for next week?"
"Are dates Jan 10-15 good for holiday?"
"Is next Monday available for leave?"
```

### 3. **Optimal Date Finder** 🎯
Find the best time for leave:
```
"When is the best time for leave in March?"
"Find me 5 days with best approval chance in April"
"When should I take my week off in June?"
```

### 4. **Direct Submission** 📝
After checking likelihood, submit your request directly:
- If likelihood is high (>85%): "Submit Leave Request" button appears
- One click to pre-fill the leave request form with predicted dates
- Seamless workflow: Query → Predict → Submit

## How to Use

### Step 1: Open AI Assistant
1. Click **AI Assistant** in the navigation menu
2. Or visit: http://localhost:8080/ai-assistant/

### Step 2: Ask About Leave
Use the "AI Leave Predictions" example queries or type your own:

**Example Query:**
```
Can I take leave from March 10 to March 15?
```

### Step 3: Review Prediction
The AI will respond with:

**Leave Approval Prediction**
- **Requested:** Monday, March 10 - Friday, March 15, 2025
- **Duration:** 5 days
- **Approval Likelihood:** 85% (GOOD)

**Analysis:**
✅ Sufficient leave balance: 120 hours available
✅ Good staffing coverage maintained
⚠️ 1 other staff member on leave during this period
✅ Good advance notice (45 days)

**Recommendations:**
✅ Strong chance of approval - safe to proceed

**[📝 Submit Leave Request]** (button appears)

### Step 4: Submit or Adjust
- **High likelihood (85%+)**: Click button to submit immediately
- **Medium likelihood (60-84%)**: Submit with expectation of manager review
- **Low likelihood (<60%)**: View alternative dates or choose different period

## Prediction Factors

The AI analyzes multiple factors:

### ✅ Positive Factors
- Sufficient leave balance
- Good staffing coverage (>70% maintained)
- Advance notice (>14 days)
- No recent leave taken
- Low competition for same dates

### ⚠️ Neutral Factors
- Medium notice (7-14 days)
- Adequate coverage (50-70%)
- Some existing leave during period
- Recent leave taken (1-2 requests in 90 days)

### ❌ Negative Factors
- Insufficient leave balance
- Low coverage (<50%)
- Short notice (<7 days)
- Peak periods (December, summer)
- Multiple staff on leave same dates
- Excessive recent leave (3+ requests in 90 days)

## Likelihood Scores

| Score | Status | Meaning | Action |
|-------|--------|---------|--------|
| 85-100% | HIGH | Excellent chance of auto-approval | Submit with confidence |
| 60-84% | MEDIUM | Likely approved after review | Submit, expect manager review |
| 40-59% | LOW | Uncertain, may be declined | Consider alternatives |
| 0-39% | VERY LOW | High risk of denial | Choose different dates |

## Alternative Date Suggestions

If your requested dates have low likelihood, the AI will suggest better alternatives:

**Better Alternative Dates:**
• March 17 - March 22 (92% approval chance)
• March 24 - March 29 (88% approval chance)
• April 7 - April 12 (90% approval chance)

Click on suggested dates to check details.

## Sample Queries

### Check Specific Dates
```
Can I take leave from Dec 25 to Dec 27?
What are my chances for Jan 10-15?
Is next week available for holiday?
Check leave for March 1 to March 5
```

### Find Optimal Dates
```
When is the best time for leave in April?
Find me 5 days with good approval in May
When should I take my week off in summer?
Best dates for 3 days leave next month
```

### Check Current Status
```
Show my leave balance
Who else is on leave next week?
What's the coverage like in June?
```

## Benefits

### For Staff
- **Save Time**: No more submitting requests only to have them denied
- **Better Planning**: Choose dates with best approval odds
- **Transparency**: Understand why certain dates may not work
- **Flexibility**: See alternative dates immediately

### For Managers
- **Fewer Denials**: Staff pick better dates upfront
- **Reduced Admin**: Less back-and-forth with staff
- **Better Coverage**: Proactive staffing planning
- **Happier Staff**: Less frustration, better vacation experiences

### For Operations
- **Maintain Coverage**: Predict and prevent staffing gaps
- **Proactive Planning**: Anticipate leave patterns
- **Compliance**: Ensure minimum staffing levels
- **Cost Savings**: Reduced agency/overtime from poor coverage

## ROI Estimate

Based on 8 care homes with 200 staff:

**Time Savings**:
- Average denied request: 15 minutes manager time + 10 minutes staff time
- Estimated 30% reduction in denials: ~50 requests/year avoided
- **Annual savings: 20-25 hours** (£500-600 admin time)

**Staff Satisfaction**:
- Reduced frustration from denied requests
- Better vacation planning experience
- Improved work-life balance perception

**Operational Efficiency**:
- Better advance planning reduces agency bookings
- Improved coverage reduces compliance risks
- Proactive staffing reduces last-minute scrambling

**Total Estimated ROI: £8,000-12,000/year**

## Technical Details

### Prediction Algorithm
The system uses a multi-factor scoring model:

1. **Leave Balance Check** (0-20 points)
   - Insufficient balance: -50 points (blocking)
   - Adequate balance: +10 points
   - Excellent balance (>2x needed): +20 points

2. **Staffing Coverage** (0-30 points)
   - Per date in range:
     - Coverage >70%: +2 points
     - Coverage 50-70%: 0 points
     - Coverage <50%: -5 points

3. **Peak Period** (0-15 points)
   - December or Summer: -15 points
   - Other months: 0 points

4. **Notice Period** (0-20 points)
   - >60 days: +10 points
   - 14-60 days: +5 points
   - 7-14 days: -20 points
   - <7 days: -40 points

5. **Recent Usage** (0-10 points)
   - 0 requests in 90 days: +10 points
   - 1-2 requests: 0 points
   - 3+ requests: -10 points

**Final Score = 100 + sum(all factors)**

### Data Sources
- `LeaveRequest` model: Approved/pending leave
- `Shift` model: Scheduled shifts and coverage
- `AnnualLeaveEntitlement`: Leave balances
- `StaffProfile`: Unit assignments
- `User` model: Staff details and roles

## Troubleshooting

### "Unable to determine your unit assignment"
- Contact manager to ensure your profile is set up with unit assignment
- Check: Staff Records → Your Profile → Unit field

### "No leave entitlement found"
- Entitlement may not be created for current leave year
- Contact manager to set up annual leave entitlement
- Check: /staff-records/annual-leave-entitlements/

### Dates not parsed correctly
Try more explicit formats:
- ✅ "Dec 25 to Dec 27"
- ✅ "2025-01-10 to 2025-01-15"
- ✅ "from March 10 to March 15"
- ❌ "around Christmas" (too vague)
- ❌ "sometime next month" (no specific dates)

### Prediction seems inaccurate
The AI analyzes current data. Factors that may affect accuracy:
- Last-minute shift changes not yet in system
- Pending leave requests not yet approved
- Special events/blackout dates not configured
- Staffing requirements not set up for all units

## Support

For issues or questions:
- **Demo Practice**: Use AI Assistant to test queries
- **Manager Support**: Contact your line manager
- **System Issues**: Contact IT support
- **Feature Requests**: Email rostering.support@example.com

## Version History

- **v1.0** (Dec 29, 2025): Initial release
  - Leave likelihood prediction
  - Natural language query support
  - Alternative date suggestions
  - Direct submission integration

## Future Enhancements

Planned for future releases:
- 📧 Email notifications for better dates if initially low
- 📊 Personal leave analytics dashboard
- 🎯 Team leave coordination (sync with colleagues)
- 📅 Calendar integration (Google Calendar, Outlook)
- 🤖 Auto-suggest best leave periods for entire year
