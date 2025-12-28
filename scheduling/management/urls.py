from django.urls import path
from . import views
from scheduling.views.ai_assistant_api import (
    ai_assistant_api, proactive_suggestions_api, leave_usage_targets, 
    agency_companies_api, daily_additional_staffing_report, weekly_additional_staffing_report,
    careplan_overview, careplan_unit_view, careplan_review_detail, careplan_compliance_report,
    careplan_manager_dashboard, careplan_approve_review,
    staffing_alert_respond, staffing_my_alerts, staffing_create_alert,
    home_dashboard,  # Home-specific dashboards with role-based access
    ot_agency_report, ot_agency_report_csv,  # OT and Agency reporting
    staff_vacancies_report, staff_vacancies_report_csv  # Staff Vacancies reporting
)
from scheduling.views_cost_analysis import (
    rota_cost_analysis,
    export_cost_analysis_pdf,
    export_cost_analysis_excel,
    export_cost_analysis_csv
)
from scheduling.views_onboarding import (
    onboarding_welcome,
    onboarding_dashboard_tour,
    onboarding_rota_tour,
    onboarding_staff_tour,
    onboarding_ai_intro,
    onboarding_mobile_tips,
    onboarding_complete,
    onboarding_skip,
    onboarding_reset,
    onboarding_mark_step_complete,
    get_contextual_tips
)
from scheduling.views_compliance import (
    my_training_dashboard, submit_training_record, training_compliance_dashboard, add_staff_training_record,
    training_breakdown_report,
    my_induction_progress, induction_management, update_induction_progress,
    my_supervision_records, create_supervision_record, supervision_management, sign_supervision_record,
    report_incident, my_incident_reports, incident_management, view_incident,
    # Task 6: Real-Time Compliance Monitor API endpoints
    compliance_dashboard_api, staff_compliance_status_api, validate_assignment_api, staff_at_risk_api,
    # Task 7: AI-Powered Payroll Validator API endpoints
    payroll_validation_api, payroll_entry_check_api, fraud_risk_api,
    # Task 8: Budget-Aware Smart Recommendations API endpoints
    budget_optimization_api, budget_status_api, budget_forecast_api,
    # Task 10: Natural Language Query Interface API endpoints
    ai_assistant_query_api, ai_assistant_suggestions_api
)
from scheduling.views_senior_dashboard import senior_management_dashboard, senior_dashboard_export, custom_report_builder
from scheduling.views_forecasting import (
    forecasting_dashboard,
    forecast_accuracy_view,
    unit_performance_view
)
from scheduling.views_optimization import (
    shift_optimization_dashboard,
    run_optimization,
    apply_optimization,
    optimization_comparison
)
from scheduling.views_overtime_management import (
    overtime_preferences_list,
    overtime_preference_form,
    overtime_preference_delete,
    overtime_coverage_request,
    overtime_coverage_detail,
    api_overtime_rankings,
    api_overtime_response_record,
    api_overtime_coverage_remind,
)
from scheduling.views_ai_dashboards import (
    proactive_suggestions_dashboard,
    rota_health_dashboard,
    rota_health_api,
)

urlpatterns = [
    # Onboarding Wizard (Option B - Step 5: Pitch-Ready First-Time Experience)
    path('onboarding/', onboarding_welcome, name='onboarding_welcome'),
    path('onboarding/dashboard-tour/', onboarding_dashboard_tour, name='onboarding_dashboard_tour'),
    path('onboarding/rota-tour/', onboarding_rota_tour, name='onboarding_rota_tour'),
    path('onboarding/staff-tour/', onboarding_staff_tour, name='onboarding_staff_tour'),
    path('onboarding/ai-intro/', onboarding_ai_intro, name='onboarding_ai_intro'),
    path('onboarding/mobile-tips/', onboarding_mobile_tips, name='onboarding_mobile_tips'),
    path('onboarding/complete/', onboarding_complete, name='onboarding_complete'),
    path('onboarding/skip/', onboarding_skip, name='onboarding_skip'),
    path('onboarding/reset/', onboarding_reset, name='onboarding_reset'),
    path('api/onboarding/mark-step/', onboarding_mark_step_complete, name='onboarding_mark_step_complete'),
    path('api/onboarding/tips/', get_contextual_tips, name='get_contextual_tips'),
    
    path('', views.home, name='home'),
    path('team-management/', views.team_management, name='team_management'),
    path('staff-management/', views.staff_management, name='staff_management'),
    path('add-staff/', views.add_staff, name='add_staff'),
    path('staff/<str:sap>/', views.staff_detail, name='staff_detail'),
    path('staff-guidance/', views.staff_guidance, name='staff_guidance'),
    path('manager-dashboard/', views.manager_dashboard, name='manager_dashboard'),
    
    # Home-Specific Dashboards (5 homes with role-based access)
    path('home/', home_dashboard, name='home_dashboard'),  # Auto-detects user's home
    path('home/<slug:home_slug>/', home_dashboard, name='home_dashboard_specific'),  # Specific home view
    
    path('senior-dashboard/export/', senior_dashboard_export, name='senior_dashboard_export'),
    path('senior-dashboard/reports/', custom_report_builder, name='custom_report_builder'),
    path('senior-dashboard/', senior_management_dashboard, name='senior_management_dashboard'),
    
    # ML Forecasting Dashboard (Task 11 - AI-powered demand forecasting)
    path('forecasting/', forecasting_dashboard, name='forecasting_dashboard'),
    path('forecasting/accuracy/', forecast_accuracy_view, name='forecast_accuracy'),
    path('forecasting/performance/', unit_performance_view, name='unit_performance'),
    
    # ML Shift Optimization (Task 12 - AI-powered shift scheduling)
    path('optimization/', shift_optimization_dashboard, name='shift_optimization_dashboard'),
    path('optimization/run/', run_optimization, name='run_optimization'),
    path('optimization/apply/', apply_optimization, name='apply_optimization'),
    path('optimization/comparison/', optimization_comparison, name='optimization_comparison'),
    
    path('reports-dashboard/', views.reports_dashboard, name='reports_dashboard'),
    
    # OT and Agency Comprehensive Report
    path('reports/ot-agency/', ot_agency_report, name='ot_agency_report'),
    path('reports/ot-agency/export/', ot_agency_report_csv, name='ot_agency_report_csv'),
    
    # Staff Vacancies Report
    path('reports/vacancies/', staff_vacancies_report, name='staff_vacancies_report'),
    path('reports/vacancies/export/', staff_vacancies_report_csv, name='staff_vacancies_report_csv'),
    
    # Rota Cost Analysis
    path('reports/cost-analysis/', rota_cost_analysis, name='rota_cost_analysis'),
    path('reports/cost-analysis/export/pdf/', export_cost_analysis_pdf, name='export_cost_analysis_pdf'),
    path('reports/cost-analysis/export/excel/', export_cost_analysis_excel, name='export_cost_analysis_excel'),
    path('reports/cost-analysis/export/csv/', export_cost_analysis_csv, name='export_cost_analysis_csv'),
    
    path('reports/annual-leave/', views.get_annual_leave_report, name='get_annual_leave_report'),
    path('reports/leave-targets/', leave_usage_targets, name='leave_usage_targets'),
    path('rota-view/', views.rota_view, name='rota_view'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('request-leave/', views.request_leave, name='request_annual_leave'),
    path('request-shift-swap/', views.request_shift_swap, name='request_shift_swap'),
    path('login/', views.login_view, name='login'),
    path('leave-approvals/', views.leave_approval_dashboard, name='leave_approval_dashboard'),
    path('staff-search-rota/', views.staff_search_rota, name='staff_search_rota'),
    path('edit-shift/', views.edit_shift, name='edit_shift'),
    path('add-shift/', views.add_shift, name='add_shift'),
    path('staff-home-units/', views.staff_home_units, name='staff_home_units'),
    path('team-shift-summary/', views.team_shift_summary, name='team_shift_summary'),
    path('update-team-assignment/', views.update_team_assignment, name='update_team_assignment'),
    
    # Audit & Compliance URLs
    path('audit/', views.audit_dashboard, name='audit_dashboard'),
    path('audit/compliance/', views.compliance_dashboard, name='compliance_dashboard'),
    path('audit/data-changes/', views.data_change_log_list, name='data_change_log_list'),
    path('audit/access-logs/', views.system_access_log_list, name='system_access_log_list'),
    path('audit/violations/', views.compliance_violation_list, name='compliance_violation_list'),
    path('audit/violations/<int:violation_id>/', views.compliance_violation_detail, name='compliance_violation_detail'),
    path('audit/reports/', views.audit_report_list, name='audit_report_list'),
    path('audit/reports/<int:report_id>/', views.audit_report_detail, name='audit_report_detail'),
    path('audit/reports/generate/', views.generate_audit_report, name='generate_audit_report'),
    
    # AI Assistant API
    path('ai-assistant/', ai_assistant_page, name='ai_assistant_page'),
    path('api/ai-assistant/', ai_assistant_api, name='ai_assistant_api'),
    path('api/proactive-suggestions/', proactive_suggestions_api, name='proactive_suggestions_api'),
    
    # Agency & Additional Staffing APIs
    path('api/agency-companies/', agency_companies_api, name='agency_companies_api'),
    path('api/reports/daily-additional-staffing/', daily_additional_staffing_report, name='daily_additional_staffing_report'),
    path('api/reports/weekly-additional-staffing/', weekly_additional_staffing_report, name='weekly_additional_staffing_report'),
    
    # Care Inspectorate Compliance URLs
    # Training
    path('compliance/training/', my_training_dashboard, name='my_training_dashboard'),
    path('compliance/training/submit/', submit_training_record, name='submit_training_record'),
    path('compliance/training/management/', training_compliance_dashboard, name='training_compliance_dashboard'),
    path('compliance/training/add-record/', add_staff_training_record, name='add_staff_training_record'),
    path('compliance/training/breakdown-report/', training_breakdown_report, name='training_breakdown_report'),
    
    # Induction
    path('compliance/induction/', my_induction_progress, name='my_induction_progress'),
    path('compliance/induction/management/', induction_management, name='induction_management'),
    path('compliance/induction/<int:induction_id>/update/', update_induction_progress, name='update_induction_progress'),
    
    # Supervision
    path('compliance/supervision/', my_supervision_records, name='my_supervision_records'),
    path('compliance/supervision/create/', create_supervision_record, name='create_supervision_record'),
    path('compliance/supervision/management/', supervision_management, name='supervision_management'),
    path('compliance/supervision/<int:record_id>/sign/', sign_supervision_record, name='sign_supervision_record'),
    
    # Incidents
    path('compliance/incident/report/', report_incident, name='report_incident'),
    path('compliance/incident/my-reports/', my_incident_reports, name='my_incident_reports'),
    path('compliance/incident/management/', incident_management, name='incident_management'),
    path('compliance/incident/<int:incident_id>/', view_incident, name='view_incident'),
    
    # Care Plan Reviews
    path('careplan/', careplan_overview, name='careplan_overview'),
    path('careplan/unit/<str:unit_name>/', careplan_unit_view, name='careplan_unit_view'),
    path('careplan/review/<int:review_id>/', careplan_review_detail, name='careplan_review_detail'),
    path('careplan/reports/', careplan_compliance_report, name='careplan_compliance_report'),
    path('careplan/manager-dashboard/', careplan_manager_dashboard, name='careplan_manager_dashboard'),
    path('careplan/approve/<int:review_id>/', careplan_approve_review, name='careplan_approve_review'),
    
    # Staffing Alerts
    path('staffing-alerts/dashboard/', staffing_my_alerts, name='staffing_alerts_dashboard'),
    path('staffing-alerts/create/', staffing_create_alert, name='staffing_create_alert'),
    path('staffing-alerts/respond/<str:token>/<str:action>/', staffing_alert_respond, name='staffing_alert_respond'),
    
    # Overtime Preferences Management
    path('overtime/preferences/', overtime_preferences_list, name='overtime_preferences_list'),
    path('overtime/preferences/add/', overtime_preference_form, name='overtime_preference_add'),
    path('overtime/preferences/edit/<int:preference_id>/', overtime_preference_form, name='overtime_preference_edit'),
    path('overtime/preferences/delete/<int:preference_id>/', overtime_preference_delete, name='overtime_preference_delete'),
    
    # Intelligent OT Coverage
    path('overtime/coverage/request/<int:shift_id>/', overtime_coverage_request, name='overtime_coverage_request'),
    path('overtime/coverage/<int:request_id>/', overtime_coverage_detail, name='overtime_coverage_detail'),
    path('api/overtime/rankings/', api_overtime_rankings, name='api_overtime_rankings'),
    path('api/overtime/response/<int:response_id>/', api_overtime_response_record, name='api_overtime_response_record'),
    path('api/overtime/coverage/<int:request_id>/remind/', api_overtime_coverage_remind, name='api_overtime_coverage_remind'),
    
    # AI Dashboards - Quick Win Features
    path('ai/suggestions/', proactive_suggestions_dashboard, name='proactive_suggestions_dashboard'),
    path('ai/rota-health/', rota_health_dashboard, name='rota_health_dashboard'),
    path('api/rota-health/', rota_health_api, name='rota_health_api'),
    
    # Task 6: Real-Time Compliance Monitor - Phase 2 API Endpoints
    path('api/compliance/dashboard/', compliance_dashboard_api, name='compliance_dashboard_api'),
    path('api/compliance/staff/<int:user_id>/status/', staff_compliance_status_api, name='staff_compliance_status_api'),
    path('api/compliance/validate-assignment/', validate_assignment_api, name='validate_assignment_api'),
    path('api/compliance/at-risk/', staff_at_risk_api, name='staff_at_risk_api'),
    
    # Task 7: AI-Powered Payroll Validator - Phase 2 API Endpoints
    path('api/payroll/validate/', payroll_validation_api, name='payroll_validation_api'),
    path('api/payroll/check-entry/', payroll_entry_check_api, name='payroll_entry_check_api'),
    path('api/payroll/fraud-risk/<int:user_id>/', fraud_risk_api, name='fraud_risk_api'),
    
    # Task 8: Budget-Aware Smart Recommendations - Phase 2 API Endpoints
    path('api/budget/optimize/', budget_optimization_api, name='budget_optimization_api'),
    path('api/budget/status/', budget_status_api, name='budget_status_api'),
    path('api/budget/forecast/', budget_forecast_api, name='budget_forecast_api'),
    
    # Task 10: Natural Language Query Interface - Phase 3 API Endpoints
    path('api/ai-assistant/query/', ai_assistant_query_api, name='ai_assistant_query_api'),
    path('api/ai-assistant/suggestions/', ai_assistant_suggestions_api, name='ai_assistant_suggestions_api'),
]
