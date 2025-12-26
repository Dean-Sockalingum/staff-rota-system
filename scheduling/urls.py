from django.urls import path
from . import views
from .views_senior_dashboard import (
    senior_management_dashboard, 
    senior_dashboard_export,
    custom_report_builder
)
from .views_forecasting import (
    forecasting_dashboard,
    forecast_accuracy_view,
    unit_performance_view
)
from .ai_recommendations import (
    approve_ai_recommendation,
    reject_ai_recommendation
)
from .views_onboarding import (
    onboarding_welcome,
    onboarding_complete,
    onboarding_skip,
    onboarding_resume,
    update_onboarding_progress,
    get_onboarding_progress,
    mark_onboarding_step_complete,
    get_user_tips
)

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Onboarding Wizard (Pitch Demo - Step 5)
    path('onboarding/', onboarding_welcome, name='onboarding_welcome'),
    path('onboarding/complete/', onboarding_complete, name='onboarding_complete'),
    path('onboarding/skip/', onboarding_skip, name='onboarding_skip'),
    path('onboarding/resume/', onboarding_resume, name='onboarding_resume'),
    path('api/onboarding/progress/', update_onboarding_progress, name='update_onboarding_progress'),
    path('api/onboarding/progress/get/', get_onboarding_progress, name='get_onboarding_progress'),
    path('api/onboarding/step/complete/', mark_onboarding_step_complete, name='mark_onboarding_step_complete'),
    path('api/onboarding/tips/', get_user_tips, name='get_user_tips'),
    
    # Manager/Admin Views
    path('dashboard/', views.manager_dashboard, name='manager_dashboard'),
    
    # Home-Specific Dashboards (5 homes with role-based access)
    path('home/', views.home_dashboard, name='home_dashboard'),  # Auto-detects user's home
    path('home/<slug:home_slug>/', views.home_dashboard, name='home_dashboard_specific'),  # Specific home view
    
    path('senior-dashboard/export/', senior_dashboard_export, name='senior_dashboard_export'),
    path('senior-dashboard/reports/', custom_report_builder, name='custom_report_builder'),
    path('senior-dashboard/', senior_management_dashboard, name='senior_management_dashboard'),
    
    # ML Forecasting Dashboard (Task 11)
    path('forecasting/', forecasting_dashboard, name='forecasting_dashboard'),
    path('forecasting/accuracy/', forecast_accuracy_view, name='forecast_accuracy'),
    path('forecasting/performance/', unit_performance_view, name='unit_performance'),
    
    path('rota/', views.rota_view, name='rota_view'),
    path('staff-search-rota/', views.staff_search_rota, name='staff_search_rota'),
    path('edit-shift/', views.edit_shift, name='edit_shift'),
    path('add-shift/', views.add_shift, name='add_shift'),
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/annual-leave/', views.get_annual_leave_report, name='get_annual_leave_report'),
    path('reports/leave-targets/', views.leave_usage_targets, name='leave_usage_targets'),
    path('guidance/', views.staff_guidance, name='staff_guidance'),
    
    # Staff Views
    path('my-rota/', views.staff_dashboard, name='staff_dashboard'),
    path('request-leave/', views.request_annual_leave, name='request_annual_leave'),
    path('request-swap/', views.request_shift_swap, name='request_shift_swap'),
    path('leave-approvals/', views.leave_approval_dashboard, name='leave_approval_dashboard'),
    
    # Staff Management URLs
    path('staff-management/', views.staff_management, name='staff_management'),
    path('team-management/', views.team_management, name='team_management'),
    path('team-management/summary/', views.team_shift_summary, name='team_shift_summary'),
    path('team-management/update/', views.update_team_assignment, name='update_team_assignment'),
    path('staff-detail/<str:sap>/', views.staff_detail, name='staff_detail'),
    path('add-staff/', views.add_staff, name='add_staff'),
    path('auto-assign-teams/', views.auto_assign_teams, name='auto_assign_teams'),
    
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
    path('ai-assistant/', views.ai_assistant_page, name='ai_assistant_page'),
    path('api/ai-assistant/', views.ai_assistant_api, name='ai_assistant_api'),
    path('api/ai-assistant/suggestions/', views.ai_assistant_suggestions_api, name='ai_assistant_suggestions_api'),
    
    # AI Assistant Feedback & Learning (Task 11 - Phase 3)
    path('api/ai-assistant/feedback/', views.ai_assistant_feedback_api, name='ai_assistant_feedback_api'),
    path('api/ai-assistant/analytics/', views.ai_assistant_analytics_api, name='ai_assistant_analytics_api'),
    path('api/ai-assistant/insights/', views.ai_assistant_insights_api, name='ai_assistant_insights_api'),
    
    path('api/ai-recommendations/approve/', approve_ai_recommendation, name='approve_ai_recommendation'),
    path('api/ai-recommendations/reject/', reject_ai_recommendation, name='reject_ai_recommendation'),
    
    # Smart Staff Matching (Task 1 - Phase 1)
    path('smart-matching/test/', views.smart_matching_test_page, name='smart_matching_test'),
    path('api/smart-matching/<int:shift_id>/', views.smart_staff_matching_api, name='smart_staff_matching'),
    path('api/smart-matching/<int:shift_id>/send-offers/', views.auto_send_smart_offers_api, name='auto_send_smart_offers'),
    
    # Enhanced Agency Coordination (Task 2 - Phase 1)
    path('agency-coordination/test/', views.agency_coordination_test_page, name='agency_coordination_test'),
    path('api/agency-coordination/<int:shift_id>/', views.agency_recommendations_api, name='agency_recommendations'),
    path('api/agency-coordination/<int:cover_request_id>/auto-coordinate/', views.auto_coordinate_agencies_api, name='auto_coordinate_agencies'),
    
    # Intelligent Shift Swap Auto-Approval (Task 3 - Phase 1)
    path('shift-swaps/test/', views.shift_swap_test_page, name='shift_swap_test'),
    path('api/shift-swaps/request/', views.request_shift_swap_api, name='request_shift_swap'),
    path('api/shift-swaps/<int:shift_id>/recommendations/', views.get_swap_recommendations_api, name='get_swap_recommendations'),
    path('api/shift-swaps/<int:swap_id>/status/', views.get_swap_status_api, name='get_swap_status'),
    
    # Predictive Shortage Alert System (ML) - Task 5, Phase 2
    path('shortage-predictor/test/', views.shortage_predictor_test_page, name='shortage_predictor_test'),
    path('api/shortage-predictor/train/', views.train_shortage_model_api, name='train_shortage_model'),
    path('api/shortage-predictor/alerts/', views.get_shortage_alerts_api, name='get_shortage_alerts'),
    path('api/shortage-predictor/features/', views.get_feature_importance_api, name='get_feature_importance'),
    
    # Agency & Additional Staffing APIs
    path('api/agency-companies/', views.agency_companies_api, name='agency_companies_api'),
    path('api/reports/daily-additional-staffing/', views.daily_additional_staffing_report, name='daily_additional_staffing_report'),
    path('api/reports/weekly-additional-staffing/', views.weekly_additional_staffing_report, name='weekly_additional_staffing_report'),
    
    # OT and Agency Comprehensive Report
    path('reports/ot-agency/', views.ot_agency_report, name='ot_agency_report'),
    path('reports/ot-agency/export/', views.ot_agency_report_csv, name='ot_agency_report_csv'),
    
    # Staff Vacancies Report
    path('reports/vacancies/', views.staff_vacancies_report, name='staff_vacancies_report'),
    path('reports/vacancies/export/', views.staff_vacancies_report_csv, name='staff_vacancies_report_csv'),
    
    # Staffing Alert URLs
    path('staffing/alerts/', views.staffing_my_alerts, name='staffing_my_alerts'),
    path('staffing/respond/<uuid:token>/<str:action>/', views.staffing_alert_respond, name='staffing_alert_respond'),
    path('staffing/create-alert/', views.staffing_create_alert, name='staffing_create_alert'),
    path('staffing/dashboard/', views.staffing_dashboard, name='staffing_dashboard'),
    
    # Demo Feedback System
    path('feedback/', views.demo_feedback, name='demo_feedback'),
    path('feedback/thanks/', views.demo_feedback_thanks, name='demo_feedback_thanks'),
    path('feedback/results/', views.view_feedback_results, name='view_feedback_results'),
    path('feature-request/', views.submit_feature_request, name='submit_feature_request'),
]