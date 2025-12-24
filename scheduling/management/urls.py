from django.urls import path
from . import views
from scheduling.views import (
    ai_assistant_page, ai_assistant_api, leave_usage_targets, 
    agency_companies_api, daily_additional_staffing_report, weekly_additional_staffing_report,
    careplan_overview, careplan_unit_view, careplan_review_detail, careplan_compliance_report,
    careplan_manager_dashboard, careplan_approve_review,
    staffing_alert_respond, staffing_my_alerts, staffing_create_alert,
    home_dashboard,  # Home-specific dashboards with role-based access
    ot_agency_report, ot_agency_report_csv  # OT and Agency reporting
)  # Import from main views
from scheduling.views_compliance import (
    my_training_dashboard, submit_training_record, training_compliance_dashboard, add_staff_training_record,
    my_induction_progress, induction_management, update_induction_progress,
    my_supervision_records, create_supervision_record, supervision_management, sign_supervision_record,
    report_incident, my_incident_reports, incident_management, view_incident
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

urlpatterns = [
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
]
