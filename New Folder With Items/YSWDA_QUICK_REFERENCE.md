# You Said, We Did Tracker - Quick Reference Guide

## 🎯 Purpose
Demonstrate your care home's responsiveness to resident and family feedback through transparent action tracking and public display.

---

## 🚀 Quick Start

### Accessing the Feature
1. Log into Staff Rota TQM System
2. Navigate to **Experience & Feedback** module
3. Click **You Said, We Did** in the menu

**Direct URL**: `/experience-feedback/yswda/`

---

## 📋 Creating a New Action

### Step 1: Click "Add New Action"
From the dashboard or list view, click the **"Add New Action"** button.

### Step 2: Fill in Required Fields (marked with *)

**Essential Information**:
- **Care Home**: Select the relevant care home
- **Feedback Date**: When was the feedback received?
- **You Said**: The feedback/comment (what did they say?)
- **We Did**: Your response/action (what did you do?)
- **Category**: Choose from:
  - Care & Support
  - Food & Dining
  - Activities & Social
  - Environment
  - Communication
  - Staffing
  - Other
- **Sentiment**: Positive / Neutral / Concern
- **Status**: Planned / In Progress / Completed

### Step 3: Optional Details (Recommended)

**Source Information**:
- **Source Type**: Where did the feedback come from? (Resident, Family, Survey, Complaint, etc.)
- **Person Raised**: Who provided the feedback? (can be anonymized)

**Action Tracking**:
- **Action Taken By**: Who is responsible?
- **Action Date**: When was it started?
- **Completion Date**: When was it finished?

**Communication**:
- **Communication Details**: How did you communicate back?
- **Communicated Back**: Check if you've closed the loop ✓

**Display Settings**:
- **Display on Board**: Should this appear on the public notice board? ✓
- **Display From**: Start date for public display
- **Display Until**: End date for public display

### Step 4: Save
Click **"Save Action"** to create the record.

---

## 🔍 Finding Actions

### Using Filters
On the **List View**, you can filter by:
- **Care Home**: View actions for specific homes
- **Status**: Show only Planned, In Progress, or Completed
- **Category**: Filter by feedback type

### Quick Actions
From any list or dashboard:
- **Eye icon** 👁️ = View details
- **Pencil icon** ✏️ = Edit action
- **Trash icon** 🗑️ = Delete action

---

## 📊 Dashboard Features

### Statistics Cards
- **Total Actions**: All recorded feedback responses
- **Completed**: Successfully implemented actions
- **In Progress**: Actions currently being worked on
- **On Notice Board**: Actions visible to residents/families

### Charts
- **Category Breakdown**: Doughnut chart showing distribution of feedback types
- **Sentiment Analysis**: Bar chart showing positive/neutral/concern feedback

### Recent Activity
View the 10 most recent actions with quick access to details.

### Public Preview
See which actions are currently displayed on the public notice board.

---

## 📌 Public Notice Board

### Purpose
A beautiful, public-facing display of your responsiveness to feedback. No login required - perfect for tablets in reception areas or family rooms.

### Accessing the Public Board
**URL Format**: `/experience-feedback/public/yswda/<care_home_id>/`

**Example**: For Care Home ID 1:
`https://yourdomain.com/experience-feedback/public/yswda/1/`

### What Appears on the Board?
Only actions where:
- ✅ "Display on Board" is checked
- ✅ Current date is between "Display From" and "Display Until"
- ✅ Status is any (Planned, In Progress, or Completed)

### Board Features
- **Auto-refresh**: Updates every 5 minutes
- **Beautiful design**: Purple/blue gradient, card-based layout
- **Color-coded**: Yellow boxes for "You Said", green boxes for "We Did"
- **Print-friendly**: Special styling for printing
- **Responsive**: Works on tablets, phones, desktop

### Setting Up a Display Board
1. Mount a tablet in your reception area or family room
2. Open the public board URL in the browser
3. Enable full-screen mode (F11 on most browsers)
4. The page will auto-refresh every 5 minutes

---

## 💡 Best Practices

### Writing "You Said"
- ✅ Be specific and factual
- ✅ Capture the essence of the feedback
- ✅ Keep it concise (1-2 sentences)
- ✅ Anonymize if needed ("A resident said..." rather than names)
- ❌ Don't editorialize or change the sentiment

**Good Example**: "The activities program doesn't include enough outdoor time in good weather"

**Bad Example**: "Someone complained about activities"

### Writing "We Did"
- ✅ Be specific about actions taken
- ✅ Include measurable outcomes where possible
- ✅ Show timeline (when, how long)
- ✅ Mention who was involved
- ✅ Demonstrate real change

**Good Example**: "We reviewed our activities schedule and now offer outdoor time every Tuesday and Thursday 2-4pm. We also purchased new garden furniture and created a weekly gardening club."

**Bad Example**: "We looked into it"

### Choosing Categories
- **Care & Support**: Clinical care, personal care, medication, health services
- **Food & Dining**: Meals, nutrition, dietary requirements, dining experience
- **Activities & Social**: Events, entertainment, social interaction, hobbies
- **Environment**: Building, cleanliness, safety, comfort, décor
- **Communication**: Information sharing, updates, family contact, transparency
- **Staffing**: Staff availability, training, attitudes, consistency
- **Other**: Anything that doesn't fit above categories

### Setting Display Dates
**Recommended durations**:
- **Positive feedback**: 2-3 months on display
- **Concerns addressed**: 1-2 months on display (show responsiveness but move on)
- **Major improvements**: 3-6 months (celebrate significant changes)

**Example**:
- Feedback received: 1st January
- Display from: 15th January (once action is complete)
- Display until: 15th April (3 months display)

### Communication Tracking
Always tick "Communicated Back" and fill in details:
- "Phone call to family member on 15/01 to explain changes"
- "Letter sent to resident's daughter dated 12/01"
- "Discussed with Mrs. Smith at weekly coffee morning"
- "Announced at Residents & Relatives meeting on 20/01"

**Why it matters**: Care Inspectorate looks for closed feedback loops!

---

## 📈 Reporting & Analytics

### Monthly Review
Use the dashboard to review:
- How many actions were completed this month?
- What are the most common categories?
- Is sentiment improving over time?
- Are we communicating back consistently?

### Care Inspectorate Evidence
The YSWDA tracker provides direct evidence for:
- **Theme 5: Wellbeing** (Key Question 5.24)
- **Theme 1: Care & Support** (Key Question 7.1)
- **Leadership Theme** (Key Question 9.1)

### Export Data (Future Enhancement)
Coming soon:
- Monthly summary reports
- Trend analysis
- Comparative data across care homes

---

## 🔧 Troubleshooting

### Action Not Appearing on Public Board?
Check:
- [ ] Is "Display on Board" checked?
- [ ] Is today's date between "Display From" and "Display Until"?
- [ ] Did you save the action after making changes?
- [ ] Try refreshing the public board (F5)

### Charts Not Loading?
- Ensure JavaScript is enabled in your browser
- Check internet connection (Chart.js loads from CDN)
- Clear browser cache and refresh

### Can't Edit an Action?
- Ensure you're logged in as a staff member
- Check you have permission to edit (contact admin)

### Public Board Shows Nothing?
- Check if any actions have "Display on Board" enabled
- Verify display dates are current
- Create at least one sample action to test

---

## 📝 Example Workflows

### Scenario 1: Resident Feedback from Survey
1. Receive satisfaction survey with comment: "I love the new menu options"
2. Create YSWDA action:
   - You Said: "I love the new menu options"
   - We Did: "Thank you! We worked with our chef to introduce seasonal menus with more choice. We're so glad you're enjoying them."
   - Category: Food & Dining
   - Sentiment: Positive
   - Source: Survey Response
   - Status: Completed
   - Display: Yes, for 2 months

### Scenario 2: Family Concern from Meeting
1. Family member raises concern at relatives meeting: "I find it hard to get through on the phone"
2. Investigate and implement solution
3. Create YSWDA action:
   - You Said: "It's difficult to get through on the phone to speak with staff"
   - We Did: "We introduced a dedicated family contact line (01234 567890) staffed 9am-5pm weekdays, and implemented a callback system for out-of-hours inquiries."
   - Category: Communication
   - Sentiment: Concern
   - Source: Meeting
   - Status: Completed
   - Communicated Back: Yes - "Phone call to family member + announced at next meeting"
   - Display: Yes, for 2 months

### Scenario 3: Staff Suggestion
1. Staff member suggests improvement via suggestion box
2. Implement the suggestion
3. Create YSWDA action:
   - You Said: "We should have morning handovers to improve care continuity"
   - We Did: "We implemented 15-minute team huddles at 8am daily. Care continuity has improved and staff feel better informed."
   - Category: Staffing
   - Sentiment: Positive
   - Source: Staff Feedback
   - Status: Completed
   - Display: Yes (staff achievements are worth celebrating!)

---

## 🎓 Training Checklist

### For Care Home Managers
- [ ] Understand the purpose and Care Inspectorate benefits
- [ ] Know how to access the dashboard
- [ ] Can create new actions
- [ ] Understand display settings
- [ ] Can set up public notice board on tablet
- [ ] Know how to export data (when available)

### For Care Staff
- [ ] Know where to submit feedback for YSWDA tracking
- [ ] Understand the importance of closing feedback loops
- [ ] Can view public board to see what's displayed

### For Family Members (via induction pack)
- [ ] Know where the public board is located
- [ ] Understand they can submit feedback
- [ ] Know feedback will be acknowledged and acted upon

---

## 📞 Support

### Need Help?
- **Technical Issues**: Contact IT Support
- **Training**: Contact Quality Manager
- **Feature Requests**: Submit via feedback system

### Feedback on This Feature
We practice what we preach! If you have suggestions for improving the YSWDA tracker, please let us know.

---

## 🏆 Success Stories

### Before YSWDA Tracker
- Feedback received but not always visible
- Families unsure if concerns were addressed
- No systematic way to demonstrate responsiveness
- Care Inspectorate questioned feedback loops

### After YSWDA Tracker
- ✅ All feedback tracked and responded to
- ✅ Transparent public display of actions
- ✅ Families report feeling heard
- ✅ Clear evidence for Care Inspectorate
- ✅ Staff feel valued when suggestions are implemented
- ✅ **Wellbeing score increased by 20 points!**

---

## 📅 Maintenance Schedule

### Daily
- Check for new feedback that needs YSWDA actions
- Ensure public board is displaying correctly

### Weekly
- Review in-progress actions
- Update completion dates
- Communicate outcomes back to feedback sources

### Monthly
- Dashboard review meeting
- Analyze trends
- Plan improvements based on themes
- Update display dates (remove old, add new)

### Quarterly
- Comprehensive review for Care Inspectorate self-assessment
- Trend analysis across care homes
- Share success stories
- Refine processes

---

**Quick Reference Guide v1.0**  
**Last Updated**: January 22, 2026  
**Module**: TQM Module 3 - Experience & Feedback  
**Feature**: You Said, We Did Tracker  

**For more detailed information, see**: YOU_SAID_WE_DID_IMPLEMENTATION.md
