# SCOTTISH TERMINOLOGY: QIA NOT CAPA
**Date:** January 25, 2026  
**Critical Compliance Update**

---

## ⚠️ TERMINOLOGY CORRECTION

### THE ISSUE
**CAPA** in Scottish residential care homes means:
- **"Care about Physical Activity"** 
- A Scottish Government initiative to promote physical activity in care settings
- Completely unrelated to quality improvement actions

Using "CAPA" for corrective/preventive actions would cause **immediate confusion** with:
- Care Inspectorate inspectors
- Scottish care home staff
- Regulatory frameworks
- Industry terminology

---

## ✅ SOLUTION: QIA System

### Quality Improvement Actions (QIA)
- **Acronym:** QIA
- **Full Name:** Quality Improvement Action Register
- **Reference Format:** `QIA-2026-001`
- **Purpose:** Track corrective and preventive actions from:
  - Incident investigations (Module 2)
  - Audit findings (Module 1)
  - Risk assessments (Module 6)
  - Complaint resolutions (Module 3)
  - Trend analysis

### Why QIA Works for Scotland
1. **No Confusion:** Clear distinction from "Care about Physical Activity"
2. **Care Inspectorate Alignment:** Fits with Quality Indicator framework
3. **PDSA Integration:** Natural fit with Plan-Do-Study-Act methodology
4. **Industry Standard:** Commonly used in Scottish healthcare/social care

---

## 📋 IMPLEMENTATION PLAN

### Module 1: QIA System Structure

**Models:**
```python
class QualityImprovementAction(models.Model):
    """
    QIA - Scottish terminology for corrective/preventive actions
    NOT CAPA (Care about Physical Activity in Scotland)
    """
    qia_reference = CharField(unique=True)  # QIA-2026-001
    action_type = ['CORRECTIVE', 'PREVENTIVE']
    source_type = ['INCIDENT', 'AUDIT', 'RISK', 'COMPLAINT', 'TREND']
    # ... full implementation

class PreventiveAction(models.Model):
    """Subset of QIA for proactive measures"""
    
class QIAReview(models.Model):
    """QIA effectiveness verification"""
```

**Views:**
- `qia_dashboard()` - Overview and status tracking
- `qia_create()` - Generate from incidents/audits/risks
- `qia_detail()` - Full lifecycle and history
- `qia_update()` - Progress tracking
- `qia_verify()` - Effectiveness review
- `qia_close()` - Final sign-off

**URLs:**
- `/quality-audits/qia/` - QIA register
- `/quality-audits/qia/<id>/` - QIA detail
- `/quality-audits/qia/create/` - New QIA

**Templates:**
- `qia_dashboard.html`
- `qia_detail.html`
- `qia_form.html`

---

## 📝 DOCUMENTATION UPDATES

**Files Updated:**
1. ✅ `MODULE_7_DASHBOARD_COMPLETE_JAN25_2026.md`
   - All CAPA references → QIA
   - Updated model names, view functions, timelines
   
2. ✅ `WEEKEND_SPRINT_REPORT_JAN25_2026.md`
   - Updated Module 1 requirements
   - Corrected terminology throughout

3. ✅ Todo list
   - Task renamed: "Build QIA system (NOT CAPA)"

**Still Using CAPA (Correctly):**
- Module 2 incident_safety historically called actions "Safety Action Plans" (SAPs)
- This is fine - different module, different context
- See: `incident_safety/RENAME_CAPA_TO_ACTION_PLAN.md` (historical reference)

---

## 🎯 KEY POINTS FOR DEVELOPMENT

1. **Always Use QIA** for quality improvement actions in Module 1
2. **Never Use CAPA** in user-facing text for Scottish care homes
3. **Code Comments:** Add clarification where needed:
   ```python
   # QIA = Quality Improvement Action (NOT CAPA)
   # CAPA in Scotland = Care about Physical Activity
   ```
4. **User Documentation:** Explain QIA terminology clearly
5. **Training Materials:** Emphasize Scottish regulatory context

---

## 🏴󠁧󠁢󠁳󠁣󠁴󠁿 SCOTTISH REGULATORY ALIGNMENT

**QIA System Maps To:**
- **Care Inspectorate:** Quality Indicator 7.3 (Quality Assurance and Improvement)
- **Health & Social Care Standards:** Theme 4.19 (My care and support is right for me)
- **SPSP:** Improvement actions from safety incidents
- **HIS Quality Management System:** Corrective action requirements

**Evidence for Inspections:**
- QIA register demonstrates continuous improvement
- Links incidents → risks → actions → outcomes
- Shows organizational learning and response
- Tracks effectiveness of improvement measures

---

## ✅ IMPLEMENTATION STATUS

**Terminology Updated:**
- ✅ MODULE_7_DASHBOARD_COMPLETE_JAN25_2026.md
- ✅ WEEKEND_SPRINT_REPORT_JAN25_2026.md
- ✅ Todo list
- ✅ This clarification document created

**Next Steps:**
1. Implement QIA models in Module 1 (3-4 hours)
2. Create QIA views and workflows (2-3 hours)
3. Integrate with Modules 2, 6 (1-2 hours)
4. User documentation with Scottish context (1 hour)

**Timeline:** Sunday night → Monday morning (8-10 hours total)

---

## 📚 REFERENCES

**Scottish Government:**
- Care about Physical Activity (CAPA): https://www.gov.scot/policies/physical-activity/

**Care Inspectorate:**
- Quality Indicators: https://www.careinspectorate.com/

**TQM Terminology:**
- QIA = Quality Improvement Action ✅
- PDSA = Plan-Do-Study-Act ✅
- RCA = Root Cause Analysis ✅
- HSAP = Health & Safety Action Plan ✅

---

**Document Owner:** TQM Development Team  
**Last Updated:** January 25, 2026  
**Status:** ACTIVE - Use QIA terminology from this point forward
