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
    
    # PWA Offline Page
    path('offline/', views.offline_view, name='offline'),
    
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
    
    # PDF Export (Phase 2 - Task 19)
    path('export/my-shifts/pdf/', views.export_my_shifts_pdf, name='export_my_shifts_pdf'),
    path('export/rota/weekly/<int:home_id>/', views.export_weekly_rota_pdf, name='export_weekly_rota_pdf'),
    path('export/rota/monthly/<int:home_id>/', views.export_monthly_rota_pdf, name='export_monthly_rota_pdf'),
    path('export/schedule/<int:staff_id>/', views.export_staff_schedule_pdf, name='export_staff_schedule_pdf'),
    path('export/leave/summary/', views.export_leave_summary_pdf, name='export_leave_summary_pdf'),
    path('export/allocation/<int:home_id>/', views.export_allocation_summary_pdf, name='export_allocation_summary_pdf'),
    
    # Excel Export (Phase 2 - Task 20)
    path('export/my-shifts/excel/', views.export_my_shifts_excel, name='export_my_shifts_excel'),
    path('export/rota/weekly/<int:home_id>/excel/', views.export_weekly_rota_excel, name='export_weekly_rota_excel'),
    
    # Email Notifications (Phase 2 - Task 21)
    path('email/test/', views.send_test_email, name='send_test_email'),
    path('email/weekly-rotas/', views.trigger_weekly_rotas, name='trigger_weekly_rotas'),
    
    # SMS Notifications (Phase 2 - Task 22)
    path('sms/preferences/', views.sms_preferences, name='sms_preferences'),
    path('sms/test/', views.send_test_sms, name='send_test_sms'),
    path('sms/bulk-emergency/', views.send_bulk_emergency_sms, name='send_bulk_emergency_sms'),
    path('sms/opt-in-report/', views.sms_opt_in_report, name='sms_opt_in_report'),
    
    # Calendar Sync (Phase 2 - Task 23)
    path('calendar/export/shifts/', views.export_my_shifts_ical, name='export_my_shifts_ical'),
    path('calendar/export/leave/', views.export_leave_ical, name='export_leave_ical'),
    path('calendar/feed/<str:sap>/<str:token>/', views.calendar_feed, name='calendar_feed'),
    path('calendar/feed/info/', views.my_calendar_feed_info, name='my_calendar_feed_info'),
    path('calendar/add-shift/<int:shift_id>/', views.add_shift_to_calendar, name='add_shift_to_calendar'),
    path('calendar/google/<int:shift_id>/', views.google_calendar_redirect, name='google_calendar_redirect'),
    path('calendar/outlook/<int:shift_id>/', views.outlook_calendar_redirect, name='outlook_calendar_redirect'),
    
    # Bulk Operations (Phase 2 - Task 24)
    path('bulk/', views.bulk_operations_menu, name='bulk_operations_menu'),
    path('bulk/assign/', views.bulk_assign_shifts, name='bulk_assign_shifts'),
    path('bulk/delete/', views.bulk_delete_shifts, name='bulk_delete_shifts'),
    path('bulk/copy-week/', views.bulk_copy_week, name='bulk_copy_week'),
    path('bulk/swap/', views.bulk_swap_staff, name='bulk_swap_staff'),
    path('bulk/undo/', views.undo_last_bulk_operation, name='undo_last_bulk_operation'),
    path('bulk/ajax/units/', views.get_units_for_home_ajax, name='get_units_for_home_ajax'),
    path('bulk/ajax/staff/', views.get_staff_for_home_ajax, name='get_staff_for_home_ajax'),
    
    # Analytics & Reporting (Phase 3 - Task 25)
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/report/', views.analytics_detailed_report, name='analytics_detailed_report'),
    path('analytics/export/', views.analytics_export_data, name='analytics_export_data'),
    path('analytics/kpi/<str:kpi_type>/', views.analytics_kpi_widget, name='analytics_kpi_widget'),
    
    # Predictive Staffing (Phase 3 - Task 26)
    path('predictive/', views.predictive_staffing_dashboard, name='predictive_staffing_dashboard'),
    path('predictive/week/', views.predictive_week_forecast, name='predictive_week_forecast'),
    path('predictive/day/', views.predictive_single_day, name='predictive_single_day'),
    
    # Custom Report Builder (Phase 3 - Task 27)
    path('reports/', views.report_builder_dashboard, name='report_builder_dashboard'),
    path('reports/create/', views.report_builder_create, name='report_builder_create'),
    path('reports/execute/', views.report_execute, name='report_execute'),
    path('reports/preview/', views.report_preview, name='report_preview'),
    path('reports/template/save/', views.report_template_save, name='report_template_save'),
    path('reports/template/<int:template_id>/delete/', views.report_template_delete, name='report_template_delete'),
    path('reports/schedule/create/', views.report_schedule_create, name='report_schedule_create'),
    path('reports/schedule/<int:schedule_id>/delete/', views.report_schedule_delete, name='report_schedule_delete'),
    
    # KPI Tracking System (Phase 3 - Task 28)
    path('kpi/', views.kpi_dashboard, name='kpi_dashboard'),
    path('kpi/<int:kpi_id>/', views.kpi_detail, name='kpi_detail'),
    path('kpi/calculate/', views.kpi_calculate, name='kpi_calculate'),
    path('kpi/<int:kpi_id>/targets/', views.kpi_target_manage, name='kpi_target_manage'),
    path('kpi/executive/', views.kpi_executive_summary, name='kpi_executive_summary'),
    
    # Data Visualization Suite (Phase 3 - Task 29)
    path('dashboards/', views.dashboard_builder, name='dashboard_builder'),
    path('dashboards/create/', views.dashboard_create, name='dashboard_create'),
    path('dashboards/<int:dashboard_id>/', views.dashboard_view, name='dashboard_view'),
    path('dashboards/<int:dashboard_id>/edit/', views.dashboard_edit, name='dashboard_edit'),
    path('dashboards/<int:dashboard_id>/delete/', views.dashboard_delete, name='dashboard_delete'),
    path('dashboards/<int:dashboard_id>/widget/add/', views.widget_add, name='widget_add'),
    path('dashboards/widget/<int:widget_id>/delete/', views.widget_delete, name='widget_delete'),
    path('dashboards/widget/preview/', views.widget_preview, name='widget_preview'),
    
    # Trend Analysis Engine (Phase 3 - Task 30)
    path('trends/', views.trend_analysis_dashboard, name='trend_analysis_dashboard'),
    path('trends/run/', views.trend_analysis_run, name='trend_analysis_run'),
    path('trends/<int:analysis_id>/', views.trend_analysis_detail, name='trend_analysis_detail'),
    path('trends/anomaly/<int:anomaly_id>/acknowledge/', views.anomaly_acknowledge, name='anomaly_acknowledge'),
    path('trends/correlation/', views.correlation_analysis, name='correlation_analysis'),
    
    # Shift Pattern Analysis (Phase 3 - Task 31)
    path('patterns/', views.shift_pattern_dashboard, name='shift_pattern_dashboard'),
    path('patterns/analyze/', views.shift_pattern_analyze, name='shift_pattern_analyze'),
    path('patterns/gaps/detect/', views.coverage_gaps_detect, name='coverage_gaps_detect'),
    path('patterns/gaps/<int:gap_id>/fill/', views.coverage_gap_fill, name='coverage_gap_fill'),
    path('patterns/workload/analyze/', views.workload_distribution_analyze, name='workload_distribution_analyze'),
    path('patterns/workload/<int:distribution_id>/', views.workload_distribution_detail, name='workload_distribution_detail'),
    path('patterns/heatmap/', views.shift_pattern_heat_map, name='shift_pattern_heat_map'),
    
    # Cost Analytics (Phase 3 - Task 32)
    path('costs/', views.cost_analytics_dashboard, name='cost_analytics_dashboard'),
    path('costs/analyze/', views.cost_analysis_run, name='cost_analysis_run'),
    path('costs/<int:analysis_id>/', views.cost_analysis_detail, name='cost_analysis_detail'),
    path('costs/agency/', views.agency_comparison_run, name='agency_comparison_run'),
    path('costs/agency/<int:comparison_id>/', views.agency_comparison_detail, name='agency_comparison_detail'),
    path('costs/forecast/create/', views.budget_forecast_create, name='budget_forecast_create'),
    path('costs/forecast/<int:forecast_id>/', views.budget_forecast_detail, name='budget_forecast_detail'),
    
    # Compliance Monitoring (Phase 3 - Task 33)
    path('compliance/', views.compliance_dashboard, name='compliance_dashboard'),
    path('compliance/check/run/', views.run_compliance_check, name='run_compliance_check'),
    path('compliance/check/<int:check_id>/', views.compliance_check_detail, name='compliance_check_detail'),
    path('compliance/certifications/', views.certification_expiry_list, name='certification_expiry_list'),
    path('compliance/training/', views.training_compliance_view, name='training_compliance_view'),
    path('compliance/audit-trail/', views.audit_trail_view, name='audit_trail_view'),
    path('compliance/report/', views.compliance_report_view, name='compliance_report_view'),
    
    # Task 34: Staff Performance Tracking URLs
    path('performance/', views.performance_dashboard, name='performance_dashboard'),
    path('performance/attendance/<int:shift_id>/', views.record_attendance_view, name='record_attendance'),
    path('performance/staff/<int:staff_id>/', views.staff_performance_detail, name='staff_performance_detail'),
    path('performance/generate-report/', views.generate_performance_report, name='generate_performance_report'),
    path('performance/review/create/', views.create_performance_review_view, name='create_performance_review'),
    path('performance/review/<int:review_id>/', views.performance_review_detail, name='performance_review_detail'),
    path('performance/team-comparison/', views.team_performance_comparison, name='team_performance_comparison'),
    
    # Task 35: Predictive Leave Forecasting URLs
    path('leave-forecast/', views.leave_forecast_dashboard, name='leave_forecast_dashboard'),
    path('leave-forecast/generate/', views.generate_staff_forecast, name='generate_staff_forecast'),
    path('leave-forecast/<int:forecast_id>/', views.leave_forecast_detail, name='leave_forecast_detail'),
    path('leave-forecast/team/', views.team_leave_forecast, name='team_leave_forecast'),
    path('leave-forecast/impact/run/', views.leave_impact_analysis_run, name='leave_impact_analysis_run'),
    path('leave-forecast/impact/<int:analysis_id>/', views.leave_impact_detail, name='leave_impact_detail'),
    path('leave-forecast/patterns/<int:staff_id>/', views.leave_pattern_analysis, name='leave_pattern_analysis'),
    path('leave-forecast/conflicts/', views.leave_conflict_detection, name='leave_conflict_detection'),
    
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