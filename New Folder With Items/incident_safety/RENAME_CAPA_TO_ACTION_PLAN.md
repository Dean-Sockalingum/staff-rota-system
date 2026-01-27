# Terminology Change: CAPA → Safety Action Plan

## Date: 24 January 2026

## Reason for Change
**CRITICAL:** The term "CAPA" causes confusion in residential care settings where it means **"Care About Physical Activity"** rather than "Corrective and Preventive Action".

## Changes Made

### Model Renamed
- `CorrectivePreventiveAction` → `SafetyActionPlan`
- Reference numbers: `CAPA-2026-001` → `SAP-2026-001` (Safety Action Plan)
- All related_names updated: `capa_actions` → `safety_action_plans`

### Views Renamed
- `CAPAListView` → `SafetyActionPlanListView`
- `CAPADetailView` → `SafetyActionPlanDetailView`
- `CAPACreateView` → `SafetyActionPlanCreateView`
- `CAPAUpdateView` → `SafetyActionPlanUpdateView`
- `CAPADeleteView` → `SafetyActionPlanDeleteView`
- `CAPAVerifyView` → `SafetyActionPlanVerifyView`
- `ExportCAPAView` → `ExportSafetyActionPlanView`

### URL Patterns Updated
- `/capa/` → `/action-plan/`
- `capa_list` → `action_plan_list`
- `capa_detail` → `action_plan_detail`
- `capa_create` → `action_plan_create`
- `capa_update` → `action_plan_update`
- `capa_delete` → `action_plan_delete`
- `capa_verify` → `action_plan_verify`
- `export-capa` → `export-action-plan`

### Template Names (to be created/updated)
- `capa_list.html` → `action_plan_list.html`
- `capa_detail.html` → `action_plan_detail.html`
- `capa_form.html` → `action_plan_form.html`
- `capa_verify.html` → `action_plan_verify.html`
- `capa_confirm_delete.html` → `action_plan_confirm_delete.html`

### Context Variables Updated
- `capas` → `action_plans`
- `overdue_capas` → `overdue_action_plans`
- `total_capas` → `total_action_plans`
- `open_capas` → `open_action_plans`

## Database Migration Required

**NEXT STEPS:**
```bash
python manage.py makemigrations incident_safety -n rename_capa_to_safety_action_plan
python manage.py migrate
```

This will rename the database table from:
- `incident_safety_correctivepreventiveaction` → `incident_safety_safetyactionplan`

## Staff Communication
- Update all training materials to use "Safety Action Plan" or "Action Plan"
- Avoid "CAPA" terminology in user-facing documentation
- Reference numbers now use SAP prefix for clarity

## NHS Alignment
"Action Plan" is standard NHS Scotland terminology for documenting corrective and preventive actions following incidents and investigations.
