# Survey Distribution System - Complete Guide

## Overview
The Experience Feedback module now has a complete survey distribution system with **4 different methods** to collect satisfaction feedback from residents, families, staff, and external professionals.

---

## 📋 Survey Types Available

### Resident Surveys
1. **Resident - Admission** (`RESIDENT_ADMISSION`)
2. **Resident - Ongoing Care** (`RESIDENT_ONGOING`)
3. **Resident - Discharge** (`RESIDENT_DISCHARGE`)

### Family Surveys
4. **Family - Admission** (`FAMILY_ADMISSION`)
5. **Family - Ongoing Care** (`FAMILY_ONGOING`)
6. **Family - Bereavement** (`FAMILY_BEREAVEMENT`)

### Staff Surveys
7. **Staff - Experience Survey** (`STAFF_EXPERIENCE`)

### Professional Surveys
8. **Professional - Partnership Survey** (`PROFESSIONAL_PARTNERSHIP`)

---

## 🎯 Distribution Methods

### Method 1: Online Survey Creation (Staff-Initiated)
**Use Case:** Staff member creates survey on behalf of respondent

**URL:** `/experience-feedback/surveys/new/`

**Features:**
- Full Django form with all survey fields
- Pre-select survey type from dropdown
- Link to specific resident
- Support for anonymous submissions
- Rating scales (1-5 Likert) for 9 dimensions
- Net Promoter Score (0-10)
- Qualitative feedback fields
- Save and edit capability

**How to Use:**
1. Navigate to Experience Feedback > Surveys
2. Click "Create Survey" dropdown
3. Select survey type
4. Fill in respondent information
5. Complete all rating questions
6. Add qualitative feedback
7. Click "Save Survey"

---

### Method 2: Public Survey Links (External Access)
**Use Case:** Send survey link to families/external professionals via email/SMS

**URL:** `/experience-feedback/public/<token>/`

**Features:**
- No login required
- Beautiful, user-friendly interface
- Purple gradient design
- Responsive mobile layout
- Optional name/anonymous submission
- Same rating questions as staff form
- Thank you page after submission
- Confidentiality message

**How to Use:**
1. Generate unique token for each respondent (future enhancement)
2. Send link via email/SMS: `https://yourdomain.com/experience-feedback/public/ABC123/`
3. Respondent completes survey on any device
4. Automatic submission to database

**Future Enhancement Needed:**
- Token generation system (UUID-based)
- Email/SMS distribution system
- Token expiry management

---

### Method 3: Printable Blank Templates (Paper Distribution)
**Use Case:** Paper surveys for residents/families who prefer physical forms

**URL:** `/experience-feedback/surveys/blank/<survey_type>/pdf/`

**Features:**
- Professional A4 print layout
- Checkbox rating scales (1-5)
- Checkbox NPS scale (0-10)
- Text areas for qualitative feedback
- Clear instructions
- Privacy notice
- Return instructions

**How to Use:**
1. Navigate to Experience Feedback > Surveys
2. Click "Blank Templates" dropdown
3. Select survey type
4. Template opens in new tab
5. Print (Ctrl+P / Cmd+P)
6. Distribute to respondents
7. Collect completed forms
8. **Manually enter data** using Method 1 (staff-initiated form)

**Survey Types Available:**
- Resident - Admission: `/experience-feedback/surveys/blank/RESIDENT_ADMISSION/pdf/`
- Resident - Ongoing: `/experience-feedback/surveys/blank/RESIDENT_ONGOING/pdf/`
- Resident - Discharge: `/experience-feedback/surveys/blank/RESIDENT_DISCHARGE/pdf/`
- Family - Admission: `/experience-feedback/surveys/blank/FAMILY_ADMISSION/pdf/`
- Family - Ongoing: `/experience-feedback/surveys/blank/FAMILY_ONGOING/pdf/`
- Family - Bereavement: `/experience-feedback/surveys/blank/FAMILY_BEREAVEMENT/pdf/`
- Staff Experience: `/experience-feedback/surveys/blank/STAFF_EXPERIENCE/pdf/`
- Professional Partnership: `/experience-feedback/surveys/blank/PROFESSIONAL_PARTNERSHIP/pdf/`

---

### Method 4: PDF Export of Completed Surveys
**Use Case:** Download/print completed survey results for records

**URL:** `/experience-feedback/surveys/<survey_id>/pdf/`

**Features:**
- Professional PDF layout
- Survey metadata (date, care home, respondent)
- All rating scores with visual presentation
- NPS score with category (Promoter/Passive/Detractor)
- Qualitative feedback displayed
- Color-coded for printing
- Confidentiality footer

**How to Use:**
1. View survey detail page
2. Click "Download PDF" button
3. PDF opens in new tab
4. Print or save for records

**Future Enhancement (Actual PDF Generation):**
Currently returns HTML. To convert to actual PDF:
```bash
pip install weasyprint
```
Then uncomment lines in `views.py` → `survey_pdf()` function

---

## 📊 Survey Questions (All Types)

### Rating Questions (1-5 Likert Scale)
1. Overall satisfaction
2. Quality of care
3. Staff attitude & professionalism
4. Communication
5. Environment cleanliness
6. Meals & nutrition
7. Activities & engagement
8. Dignity & respect
9. Safety & security

### Net Promoter Score
- "How likely are you to recommend us?" (0-10 scale)
- Categorized as: Promoter (9-10), Passive (7-8), Detractor (0-6)

### Qualitative Feedback
- What works well?
- What could we improve?
- Additional comments

---

## 🔧 Technical Implementation

### Files Created/Modified

**Forms:**
- `experience_feedback/forms.py` ✅ NEW
  - `SatisfactionSurveyForm` (staff-initiated)
  - `PublicSurveyForm` (public access)

**Views:**
- `experience_feedback/views.py` ✅ UPDATED
  - `survey_create()` - Create new survey
  - `survey_edit()` - Edit existing survey
  - `survey_delete()` - Delete survey
  - `public_survey()` - Public survey form (no login)
  - `survey_pdf()` - Generate PDF of completed survey
  - `blank_survey_pdf()` - Generate blank printable template

**URLs:**
- `experience_feedback/urls.py` ✅ UPDATED
  - `/surveys/new/` - Create survey
  - `/surveys/<pk>/edit/` - Edit survey
  - `/surveys/<pk>/delete/` - Delete survey
  - `/surveys/<pk>/pdf/` - Download PDF
  - `/surveys/blank/<survey_type>/pdf/` - Blank template
  - `/public/<token>/` - Public survey (no login)

**Templates:**
- `survey_form.html` ✅ NEW - Staff survey creation form
- `public_survey.html` ✅ NEW - Beautiful public survey
- `public_survey_thanks.html` ✅ NEW - Thank you page
- `blank_survey_pdf.html` ✅ NEW - Printable blank template
- `survey_pdf.html` ✅ NEW - Completed survey PDF
- `survey_confirm_delete.html` ✅ NEW - Delete confirmation
- `survey_list.html` ✅ UPDATED - Added create/template buttons
- `survey_detail.html` ✅ UPDATED - Added PDF/edit/delete buttons

---

## 🚀 Quick Start Guide

### For Care Home Managers

**Option A: Enter Survey on Behalf of Resident/Family**
1. Go to Experience Feedback → Surveys
2. Click "Create Survey" → Select type
3. Fill in all fields
4. Save

**Option B: Send Public Link (Email/SMS)**
1. Generate token (future feature)
2. Send link: `https://yourdomain.com/experience-feedback/public/TOKEN/`
3. Survey auto-saves when submitted

**Option C: Paper Distribution**
1. Go to Experience Feedback → Surveys
2. Click "Blank Templates" → Select type
3. Print template
4. Distribute to residents/families
5. Manually enter completed surveys using Option A

**Option D: Download Completed Survey**
1. View survey detail
2. Click "Download PDF"
3. Print or save to records

---

## 📈 Workflow Examples

### Scenario 1: New Resident Admission
1. Family arrives for admission
2. Staff prints "Resident - Admission" blank template
3. Family completes paper survey
4. Staff enters data via "Create Survey" form
5. Data available in dashboard analytics

### Scenario 2: Monthly Family Feedback
1. Staff generates public survey links
2. Emails sent to all families with token
3. Families complete online (phone/tablet/computer)
4. Responses auto-save to database
5. Monthly report generated from dashboard

### Scenario 3: Staff Experience Survey
1. HR prints "Staff Experience" blank templates
2. Distributes to all staff members
3. Staff complete anonymously
4. HR enters anonymous responses
5. Trends analyzed for staff satisfaction

### Scenario 4: Professional Partnership Survey
1. Partnership meeting with NHS team
2. Send public link to professionals
3. Complete survey during/after meeting
4. Feedback used for service improvement

---

## ⚠️ Current Limitations & Future Enhancements

### Current Limitations
1. **Token System:** Public survey uses placeholder token, needs UUID generation
2. **Email Distribution:** No automated email sending yet
3. **PDF Generation:** Returns HTML, needs WeasyPrint for true PDF
4. **QR Codes:** No QR code generation for paper→digital link
5. **Reminders:** No automated follow-up reminders

### Recommended Enhancements
1. **Token Management:**
   - Create `SurveyToken` model
   - Generate unique UUID per survey invitation
   - Track token usage and expiry
   
2. **Email Integration:**
   - Django email backend configuration
   - Survey invitation email templates
   - Automated reminder emails
   
3. **True PDF Generation:**
   ```bash
   pip install weasyprint
   ```
   Uncomment PDF code in `views.py`
   
4. **QR Code Generation:**
   ```bash
   pip install qrcode[pil]
   ```
   Add QR codes to blank templates linking to public survey
   
5. **SMS Distribution:**
   - Integrate Twilio/similar
   - Send survey links via SMS

---

## 🔒 Security & Privacy

### Anonymous Submissions
- Respondent name field optional
- "Submit as anonymous" checkbox
- No IP tracking on public surveys

### Access Control
- Staff survey creation: Login required (`@login_required`)
- Public surveys: No login (unique token controls access)
- Survey edit/delete: Login required

### Data Protection
- Confidentiality notice on all forms
- GDPR-compliant data collection
- Secure database storage
- PDF exports marked "Confidential - Internal Use Only"

---

## 📱 Mobile Responsiveness

All survey forms are fully responsive:
- ✅ Desktop (large screens)
- ✅ Tablet (iPad, etc.)
- ✅ Mobile (iPhone, Android)

Public survey uses Bootstrap 5.3.2 with touch-friendly radio buttons.

---

## 💡 Best Practices

1. **Survey Type Selection:** Choose appropriate survey type for context
2. **Anonymous Feedback:** Encourage honest feedback via anonymous option
3. **Regular Distribution:** Schedule monthly/quarterly surveys
4. **Mixed Methods:** Combine online and paper for maximum response
5. **Action on Feedback:** Review and act on survey results promptly
6. **Thank Respondents:** Use thank you page to acknowledge input

---

## 🎨 Visual Design

### Staff Form
- Clean Bootstrap 5 layout
- Color-coded sections
- Inline validation
- Progress indication

### Public Survey
- Purple gradient background
- White card design
- Large touch-friendly controls
- Animated success checkmark

### Blank Template
- Professional A4 layout
- Clear checkbox designs
- Print-optimized spacing
- Return instructions

### PDF Export
- Color-coded categories
- Visual score displays
- Professional formatting
- Page break optimization

---

## Support & Contact

For questions about survey distribution:
- Review this documentation
- Check Django admin for survey data
- Test each distribution method
- Contact system administrator for token generation setup

---

**Last Updated:** January 2025  
**Version:** 1.0  
**Module:** TQM Module 3 - Experience & Feedback
