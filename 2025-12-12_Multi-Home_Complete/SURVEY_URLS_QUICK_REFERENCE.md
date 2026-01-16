# 📋 Quick Reference: Survey Distribution URLs

## Staff Access (Login Required)

### Main Survey Pages
- **Survey List:** http://127.0.0.1:8001/experience-feedback/surveys/
- **Create Survey:** http://127.0.0.1:8001/experience-feedback/surveys/new/
- **View Survey:** http://127.0.0.1:8001/experience-feedback/surveys/1/
- **Edit Survey:** http://127.0.0.1:8001/experience-feedback/surveys/1/edit/
- **Delete Survey:** http://127.0.0.1:8001/experience-feedback/surveys/1/delete/
- **Download PDF:** http://127.0.0.1:8001/experience-feedback/surveys/1/pdf/

### Create Survey with Pre-Selected Type
- Resident Admission: `/surveys/new/?type=RESIDENT_ADMISSION`
- Resident Ongoing: `/surveys/new/?type=RESIDENT_ONGOING`
- Resident Discharge: `/surveys/new/?type=RESIDENT_DISCHARGE`
- Family Admission: `/surveys/new/?type=FAMILY_ADMISSION`
- Family Ongoing: `/surveys/new/?type=FAMILY_ONGOING`
- Family Bereavement: `/surveys/new/?type=FAMILY_BEREAVEMENT`
- Staff Experience: `/surveys/new/?type=STAFF_EXPERIENCE`
- Professional Partnership: `/surveys/new/?type=PROFESSIONAL_PARTNERSHIP`

### Blank Printable Templates
- Resident Admission: `/surveys/blank/RESIDENT_ADMISSION/pdf/`
- Resident Ongoing: `/surveys/blank/RESIDENT_ONGOING/pdf/`
- Resident Discharge: `/surveys/blank/RESIDENT_DISCHARGE/pdf/`
- Family Admission: `/surveys/blank/FAMILY_ADMISSION/pdf/`
- Family Ongoing: `/surveys/blank/FAMILY_ONGOING/pdf/`
- Family Bereavement: `/surveys/blank/FAMILY_BEREAVEMENT/pdf/`
- Staff Experience: `/surveys/blank/STAFF_EXPERIENCE/pdf/`
- Professional Partnership: `/surveys/blank/PROFESSIONAL_PARTNERSHIP/pdf/`

---

## Public Access (No Login)

### Public Survey Form
- **URL Pattern:** http://127.0.0.1:8001/experience-feedback/public/TOKEN/
- **Example:** http://127.0.0.1:8001/experience-feedback/public/ABC123/

### Thank You Page (Auto-Redirect)
- Shown after successful public survey submission

---

## Navigation Flow

```
Dashboard
    ↓
Experience Feedback
    ↓
Surveys List
    ├─→ Create Survey (dropdown: 8 types)
    ├─→ Blank Templates (dropdown: 8 types)
    ├─→ Filter by type/home/date
    └─→ View Survey Details
            ├─→ Download PDF
            ├─→ Edit Survey
            └─→ Delete Survey
```

---

## Buttons on Survey List Page

```
┌────────────────────────────────────────────────────┐
│  [Create Survey ▼]  [Blank Templates ▼]  [Back]   │
└────────────────────────────────────────────────────┘
```

**Create Survey Dropdown:**
- 8 survey types → Opens pre-filled form

**Blank Templates Dropdown:**
- 8 survey types → Opens printable PDF in new tab

---

## Buttons on Survey Detail Page

```
┌────────────────────────────────────────────────────┐
│  [Download PDF]  [Edit]  [Delete]  [Back]          │
└────────────────────────────────────────────────────┘
```

---

## Distribution Workflows

### Workflow 1: Staff Enters Survey
1. Click "Create Survey" → Select type
2. Fill form → Save
3. Survey appears in list

### Workflow 2: Email Public Link
1. Generate token (future: UUID system)
2. Send email: `http://domain.com/experience-feedback/public/TOKEN/`
3. Respondent completes online
4. Auto-saves to database

### Workflow 3: Paper Distribution
1. Click "Blank Templates" → Select type
2. Print template
3. Distribute to respondents
4. Collect completed forms
5. Enter data using "Create Survey"

### Workflow 4: Download Results
1. View survey detail
2. Click "Download PDF"
3. Print or save

---

## File Locations

### Forms
- `experience_feedback/forms.py`

### Views
- `experience_feedback/views.py`
  - Lines 445-600: New survey views

### URLs
- `experience_feedback/urls.py`

### Templates
- `experience_feedback/templates/experience_feedback/`
  - `survey_form.html`
  - `public_survey.html`
  - `public_survey_thanks.html`
  - `blank_survey_pdf.html`
  - `survey_pdf.html`
  - `survey_confirm_delete.html`

---

## Testing URLs (Development)

**Base URL:** http://127.0.0.1:8001/experience-feedback/

Try these:
```bash
# Survey list
open http://127.0.0.1:8001/experience-feedback/surveys/

# Create new survey
open http://127.0.0.1:8001/experience-feedback/surveys/new/

# Blank template (Staff)
open http://127.0.0.1:8001/experience-feedback/surveys/blank/STAFF_EXPERIENCE/pdf/

# Public survey (no login)
open http://127.0.0.1:8001/experience-feedback/public/test123/
```

---

## Security Notes

✅ **Staff URLs:** Login required (`@login_required`)  
✅ **Public URLs:** No login (token controls access)  
✅ **CSRF Protection:** All forms protected  
✅ **Anonymous Option:** Privacy-focused  

---

**Last Updated:** January 2025  
**Server:** http://127.0.0.1:8001  
**Django:** 4.2.27
