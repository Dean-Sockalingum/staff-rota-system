from django.urls import path
from . import views
from .views_senior_dashboard import (
    senior_management_dashboard, 
    senior_dashboard_export,
    custom_report_builder,
    api_staffing_gaps,
    api_multi_home_staffing,
    api_budget_breakdown,
    api_overtime_detail,
    api_compliance_actions
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
from .views_analytics import (
    executive_dashboard,
    manager_dashboard as analytics_manager_dashboard,
    staff_performance_view,
    unit_analytics_view,
    budget_analysis_view,
    trends_analysis_view,
    api_dashboard_summary,
    api_unit_staffing,
    api_budget_analysis,
    api_weekly_trends
)
from .views_report_builder import (
    report_builder_home,
    create_report_template,
    edit_report_template,
    execute_report,
    view_report,
    export_report,
    delete_report_template,
    toggle_favorite,
    api_get_data_sources,
    api_preview_report
)
from .views_health_monitoring import (
    health_dashboard,
    health_metrics_api,
    performance_logs_view,
    error_logs_view,
    error_detail,
    uptime_history,
    health_checks_view,
    run_health_check,
    alert_rules_view,
    collect_metrics_now,
    system_info_api
)
from .views_audit import (
    audit_dashboard,
    data_changes_log,
    access_log_view,
    user_activity_view,
    object_history_view,
    compliance_dashboard,
    compliance_violations_view,
    acknowledge_violation,
    resolve_violation,
    generate_audit_report_view,
    audit_reports_list,
    view_audit_report,
    export_audit_data,
    suspicious_activity_api
)
from .views_integration_api import (
    api_get_token,
    api_list_staff,
    api_get_staff,
    api_list_shifts,
    api_list_leave_requests,
    api_export_payroll,
    api_create_webhook,
    api_get_info
)
from .views_cache import (
    cache_stats_view,
    clear_cache_view,
    warm_cache_view
)
from .views_datatable import (
    enhanced_shifts_table,
    enhanced_staff_table,
    enhanced_leave_table
)
from .views_executive_summary import (
    executive_summary_dashboard,
    executive_summary_export_pdf,
    executive_summary_api_kpis,
    executive_summary_api_trends,
    executive_summary_api_forecast,
    executive_summary_api_insights
)
# TEMPORARILY DISABLED FOR LOCAL DEVELOPMENT - 2FA REQUIRES django_otp
# from .views_2fa import (
#     two_factor_setup,
#     two_factor_disable,
#     two_factor_verify,
#     regenerate_backup_codes,
#     two_factor_status
# )
from .views_search import (
    global_search,
    autocomplete,
    advanced_search
)
from .views_preferences import (
    user_settings,
    update_theme,
    reset_preferences,
    export_preferences
)
from .views_errors import (
    trigger_error
)
from .views_week6 import (
    get_widget_preferences,
    save_widget_preferences,
    get_saved_filters,
    save_search_filter,
    delete_saved_filter,
    bulk_approve_leave,
    bulk_reject_leave,
    bulk_assign_training
)
from .views_workflow import (
    workflow_list,
    workflow_create,
    workflow_builder,
    workflow_detail,
    workflow_execute,
    workflow_toggle_status,
    workflow_delete,
    workflow_execution_detail,
    workflow_execution_list,
    workflow_template_list,
    workflow_template_create,
    workflow_add_step,
    workflow_update_step,
    workflow_delete_step
)
from .views_leave_calendar import (
    leave_calendar_view,
    team_leave_calendar_view,
    leave_calendar_data_api,
    leave_coverage_report_api
)
from .views_documents import (
    document_list,
    document_upload,
    document_detail,
    document_download,
    document_edit,
    document_delete,
    document_new_version,
    document_share,
    document_add_comment,
    my_documents,
    shared_with_me,
    category_manage,
    category_create
)
from .views_videos import (
    video_library,
    video_detail,
    video_upload,
    video_update_progress,
    video_rate,
    my_progress,
    playlist_create,
    playlist_detail,
    playlist_add_video,
    category_list as video_category_list,
    video_analytics
)

# Task 55: Recent Activity Feed views
from .views_activity import (
    recent_activity_feed,
    activity_feed_api,
    mark_activity_read,
    mark_all_read,
    archive_activity,
    activity_dashboard_widget,
    manage_activity_widgets,
    delete_activity_widget,
    toggle_activity_pin,
    activity_statistics
)

# Task 56: Compliance Dashboard Widgets views
from .views_compliance_widgets import (
    compliance_dashboard,
    widget_data_api,
    refresh_compliance_metrics,
    manage_widgets,
    create_widget,
    delete_widget,
    compliance_report
)

# Task 11: AI Assistant Feedback & Learning views
from .views_compliance import (
    ai_assistant_feedback_api,
    ai_assistant_analytics_api,
    ai_assistant_insights_api
)

# Intelligent OT Distribution views
from .views_ot_intelligence import (
    ot_intelligence_dashboard,
    ot_staff_rankings,
    ot_fairness_report,
    ot_request_coverage_api,
    ot_staff_detail,
    ot_analytics_api
)


urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Task 48: Two-Factor Authentication - DISABLED FOR LOCAL DEVELOPMENT
    # path('2fa/setup/', two_factor_setup, name='two_factor_setup'),
    # path('2fa/verify/', two_factor_verify, name='two_factor_verify'),
    # path('2fa/disable/', two_factor_disable, name='two_factor_disable'),
    # path('2fa/regenerate-backup-codes/', regenerate_backup_codes, name='regenerate_backup_codes'),
    # path('api/2fa/status/', two_factor_status, name='two_factor_status'),
    
    # Task 49: Advanced Search with Elasticsearch
    path('search/', global_search, name='global_search'),
    path('search/autocomplete/', autocomplete, name='search_autocomplete'),
    path('search/advanced/', advanced_search, name='advanced_search'),
    
    # Task 50: User Preferences Settings
    path('settings/', user_settings, name='user_settings'),
    path('settings/update-theme/', update_theme, name='update_theme'),
    path('settings/reset/', reset_preferences, name='reset_preferences'),
    path('settings/export/', export_preferences, name='export_preferences'),
    
    # Task 51: Error Tracking - Test Error View (DEBUG only)
    path('test-sentry-error/', trigger_error, name='trigger_error'),
    
    # Week 6: Power User Features
    # Task 21: Dashboard Widget Customization
    path('api/widget-preferences/', get_widget_preferences, name='get_widget_preferences'),
    path('api/widget-preferences/save/', save_widget_preferences, name='save_widget_preferences'),
    
    # Task 22: Saved Search Filters
    path('api/saved-filters/', get_saved_filters, name='get_saved_filters'),
    path('api/saved-filters/save/', save_search_filter, name='save_search_filter'),
    path('api/saved-filters/<int:filter_id>/delete/', delete_saved_filter, name='delete_saved_filter'),
    
    # Task 23-24: Bulk Operations
    path('api/bulk/leave/approve/', bulk_approve_leave, name='bulk_approve_leave'),
    path('api/bulk/leave/reject/', bulk_reject_leave, name='bulk_reject_leave'),
    path('api/bulk/training/assign/', bulk_assign_training, name='bulk_assign_training'),
    
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
    
    # Senior Dashboard
    path('senior-dashboard/export/', senior_dashboard_export, name='senior_dashboard_export'),
    path('senior-dashboard/reports/', custom_report_builder, name='custom_report_builder'),
    path('senior-dashboard/', senior_management_dashboard, name='senior_management_dashboard'),
    
    # Senior Dashboard API Endpoints
    path('api/staffing-gaps/', api_staffing_gaps, name='api_staffing_gaps'),
    path('api/multi-home/staffing/<str:date_str>/', api_multi_home_staffing, name='api_multi_home_staffing'),
    path('api/budget-breakdown/<int:home_id>/', api_budget_breakdown, name='api_budget_breakdown'),
    path('api/overtime/<str:date_str>/', api_overtime_detail, name='api_overtime_detail'),
    path('api/compliance/actions/<int:home_id>/<str:metric>/', api_compliance_actions, name='api_compliance_actions'),
    
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
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard_alias'),  # Alias for tests
    path('request-leave/', views.request_annual_leave, name='request_annual_leave'),
    path('request-leave/', views.request_annual_leave, name='request_leave'),  # Alias for compatibility
    path('request-swap/', views.request_shift_swap, name='request_shift_swap'),
    path('leave-approvals/', views.leave_approval_dashboard, name='leave_approval_dashboard'),
    
    # Leave Calendar Views (Task 59)
    path('leave/calendar/', leave_calendar_view, name='leave_calendar'),
    path('leave/calendar/team/', team_leave_calendar_view, name='team_leave_calendar'),
    path('leave/calendar/api/data/', leave_calendar_data_api, name='leave_calendar_data_api'),
    path('leave/calendar/api/coverage/', leave_coverage_report_api, name='leave_coverage_report_api'),
    
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
    
    # Cache Management (Task 44)
    path('cache/stats/', cache_stats_view, name='cache_stats'),
    path('cache/clear/', clear_cache_view, name='clear_cache'),
    path('cache/warm/', warm_cache_view, name='warm_cache'),
    
    # Enhanced Data Tables (Task 45)
    path('tables/shifts/', enhanced_shifts_table, name='enhanced_shifts_table'),
    path('tables/staff/', enhanced_staff_table, name='enhanced_staff_table'),
    path('tables/leave/', enhanced_leave_table, name='enhanced_leave_table'),
    
    # Executive Summary Dashboard (Task 46)
    path('executive-summary/', executive_summary_dashboard, name='executive_summary_dashboard'),
    path('executive-summary/export-pdf/', executive_summary_export_pdf, name='executive_summary_export_pdf'),
    path('executive-summary/api/kpis/', executive_summary_api_kpis, name='executive_summary_api_kpis'),
    path('executive-summary/api/trends/', executive_summary_api_trends, name='executive_summary_api_trends'),
    path('executive-summary/api/forecast/', executive_summary_api_forecast, name='executive_summary_api_forecast'),
    path('executive-summary/api/insights/', executive_summary_api_insights, name='executive_summary_api_insights'),
    
    # Advanced Analytics Dashboard (Task 39)
    path('analytics/executive/', executive_dashboard, name='analytics_executive_dashboard'),
    path('analytics/manager/', analytics_manager_dashboard, name='analytics_manager_dashboard'),
    path('analytics/staff/<str:sap>/', staff_performance_view, name='analytics_staff_performance'),
    path('analytics/unit/<int:unit_id>/', unit_analytics_view, name='analytics_unit'),
    path('analytics/budget/', budget_analysis_view, name='analytics_budget'),
    path('analytics/budget/<int:care_home_id>/', budget_analysis_view, name='analytics_budget_home'),
    path('analytics/trends/', trends_analysis_view, name='analytics_trends'),
    
    # Analytics API Endpoints
    path('api/analytics/dashboard/', api_dashboard_summary, name='api_dashboard_summary'),
    path('api/analytics/unit/<int:unit_id>/staffing/', api_unit_staffing, name='api_unit_staffing'),
    path('api/analytics/budget/<int:care_home_id>/', api_budget_analysis, name='api_budget_analysis'),
    path('api/analytics/trends/weekly/', api_weekly_trends, name='api_weekly_trends'),
    
    # Custom Report Builder (Task 40)
    path('reports/builder/', report_builder_home, name='report_builder_home'),
    path('reports/builder/create/', create_report_template, name='create_report_template'),
    path('reports/builder/edit/<int:template_id>/', edit_report_template, name='edit_report_template'),
    path('reports/builder/execute/<int:template_id>/', execute_report, name='execute_report'),
    path('reports/builder/view/<int:report_id>/', view_report, name='view_report'),
    path('reports/builder/export/<int:report_id>/<str:format>/', export_report, name='export_report'),
    path('reports/builder/delete/<int:template_id>/', delete_report_template, name='delete_report_template'),
    path('reports/builder/favorite/<int:template_id>/', toggle_favorite, name='toggle_favorite'),
    
    # Report Builder API
    path('api/reports/data-sources/', api_get_data_sources, name='api_get_data_sources'),
    path('api/reports/preview/', api_preview_report, name='api_preview_report'),
    
    # AI Assistant API
    path('ai-assistant/', views.ai_assistant_page, name='ai_assistant_page'),
    path('api/ai-assistant/', views.ai_assistant_api, name='ai_assistant_api'),
    path('api/ai-assistant/suggestions/', views.ai_assistant_suggestions_api, name='ai_assistant_suggestions_api'),
    
    # AI Assistant Feedback & Learning (Task 11 - Phase 3)
    path('api/ai-assistant/feedback/', ai_assistant_feedback_api, name='ai_assistant_feedback_api'),
    path('api/ai-assistant/analytics/', ai_assistant_analytics_api, name='ai_assistant_analytics_api'),
    path('api/ai-assistant/insights/', ai_assistant_insights_api, name='ai_assistant_insights_api'),
    
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
    path('performance/staff/<str:staff_id>/', views.staff_performance_detail, name='staff_performance_detail'),
    path('performance/generate-report/', views.generate_performance_report, name='generate_performance_report'),
    path('performance/api/search-staff/', views.search_staff_for_performance, name='search_staff_for_performance'),
    path('performance/review/create/', views.create_performance_review_view, name='create_performance_review'),
    path('performance/review/<int:review_id>/', views.performance_review_detail, name='performance_review_detail'),
    path('performance/team-comparison/', views.team_performance_comparison, name='team_performance_comparison'),
    
    # Care Plan Management URLs
    path('careplan/manager-dashboard/', views.careplan_manager_dashboard, name='careplan_manager_dashboard'),
    path('careplan/approve/<int:review_id>/', views.careplan_approve_review, name='careplan_approve_review'),
    
    # Task 35: Predictive Leave Forecasting URLs
    path('leave-forecast/', views.leave_forecast_dashboard, name='leave_forecast_dashboard'),
    path('leave-forecast/generate/', views.generate_staff_forecast, name='generate_staff_forecast'),
    path('leave-forecast/<int:forecast_id>/', views.leave_forecast_detail, name='leave_forecast_detail'),
    path('leave-forecast/team/', views.team_leave_forecast, name='team_leave_forecast'),
    path('leave-forecast/impact/run/', views.leave_impact_analysis_run, name='leave_impact_analysis_run'),
    path('leave-forecast/impact/<int:analysis_id>/', views.leave_impact_detail, name='leave_impact_detail'),
    path('leave-forecast/patterns/<int:staff_id>/', views.leave_pattern_analysis, name='leave_pattern_analysis'),
    path('leave-forecast/conflicts/', views.leave_conflict_detection, name='leave_conflict_detection'),
    
    # Task 36: Real-time Collaboration URLs
    path('collaboration/', views.collaboration_dashboard, name='collaboration_dashboard'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/count/', views.unread_notifications_count, name='unread_notifications_count'),
    path('messages/', views.messages_inbox, name='messages_inbox'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('messages/send/', views.send_message_view, name='send_message'),
    path('messages/reply/<int:message_id>/', views.reply_to_message, name='reply_to_message'),
    path('activity/', views.activity_feed_view, name='activity_feed'),
    path('presence/update/', views.update_presence, name='update_presence'),
    path('online-users/', views.online_users_list, name='online_users_list'),
    path('activity/stats/<int:user_id>/', views.user_activity_stats, name='user_activity_stats'),
    path('activity/stats/', views.user_activity_stats, name='my_activity_stats'),
    
    # Task 37: Multi-language Support URLs
    path('language/settings/', views.language_settings, name='language_settings'),
    path('language/set/<str:language_code>/', views.set_language_quick, name='set_language'),
    path('translations/', views.translation_management, name='translation_management'),
    path('translations/approve/<int:translation_id>/', views.approve_translation_view, name='approve_translation'),
    path('language/statistics/', views.language_statistics, name='language_statistics'),
    
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
    
    # Task 41: Integration API URLs
    # Authentication
    path("api/v1/integration/auth/token", api_get_token, name="api_get_token"),
    # Staff endpoints
    path("api/v1/integration/staff", api_list_staff, name="api_list_staff"),
    path("api/v1/integration/staff/<str:sap>", api_get_staff, name="api_get_staff"),
    # Shift endpoints
    path("api/v1/integration/shifts", api_list_shifts, name="api_list_shifts"),
    # Leave endpoints
    path("api/v1/integration/leave-requests", api_list_leave_requests, name="api_list_leave_requests"),
    # Payroll endpoints
    path("api/v1/integration/payroll/export", api_export_payroll, name="api_export_payroll"),
    # Webhook endpoints
    path("api/v1/integration/webhooks", api_create_webhook, name="api_create_webhook"),
    # System info
    path("api/v1/integration/info", api_get_info, name="api_get_info"),

    # Task 42: Health Monitoring URLs
    path("health/", health_dashboard, name="health_dashboard"),
    path("health/metrics/api/", health_metrics_api, name="health_metrics_api"),
    path("health/performance/", performance_logs_view, name="performance_logs"),
    path("health/errors/", error_logs_view, name="error_logs"),
    path("health/errors/<int:error_id>/", error_detail, name="error_detail"),
    path("health/uptime/", uptime_history, name="uptime_history"),
    path("health/checks/", health_checks_view, name="health_checks"),
    path("health/checks/<int:endpoint_id>/run/", run_health_check, name="run_health_check"),
    path("health/alerts/", alert_rules_view, name="alert_rules"),
    path("health/collect-now/", collect_metrics_now, name="collect_metrics_now"),
    path("health/system-info/", system_info_api, name="system_info_api"),

    # Task 43: Audit Trail URLs
    path("audit/", audit_dashboard, name="audit_dashboard"),
    path("audit/data-changes/", data_changes_log, name="data_changes_log"),
    path("audit/access-log/", access_log_view, name="access_log"),
    path("audit/user/<int:user_id>/", user_activity_view, name="user_activity"),
    path("audit/object-history/", object_history_view, name="object_history"),
    path("audit/compliance/", compliance_dashboard, name="compliance_dashboard"),
    path("audit/compliance/violations/", compliance_violations_view, name="compliance_violations"),
    path("audit/compliance/violations/<int:violation_id>/acknowledge/", acknowledge_violation, name="acknowledge_violation"),
    path("audit/compliance/violations/<int:violation_id>/resolve/", resolve_violation, name="resolve_violation"),
    path("audit/reports/generate/", generate_audit_report_view, name="generate_audit_report"),
    path("audit/reports/", audit_reports_list, name="audit_reports_list"),
    path("audit/reports/<int:report_id>/", view_audit_report, name="view_audit_report"),
    path("audit/export/", export_audit_data, name="export_audit_data"),
    path("audit/suspicious-activity/api/", suspicious_activity_api, name="suspicious_activity_api"),
    
    # Task 52: Workflow Automation Engine
    path('workflows/', workflow_list, name='workflow_list'),
    path('workflows/create/', workflow_create, name='workflow_create'),
    path('workflows/<int:workflow_id>/', workflow_detail, name='workflow_detail'),
    path('workflows/<int:workflow_id>/builder/', workflow_builder, name='workflow_builder'),
    path('workflows/<int:workflow_id>/execute/', workflow_execute, name='workflow_execute'),
    path('workflows/<int:workflow_id>/toggle/', workflow_toggle_status, name='workflow_toggle_status'),
    path('workflows/<int:workflow_id>/delete/', workflow_delete, name='workflow_delete'),
    path('workflows/executions/', workflow_execution_list, name='workflow_execution_list'),
    path('workflows/executions/<int:execution_id>/', workflow_execution_detail, name='workflow_execution_detail'),
    path('workflows/templates/', workflow_template_list, name='workflow_template_list'),
    path('workflows/templates/create/', workflow_template_create, name='workflow_template_create'),
    # Workflow API endpoints
    path('workflows/<int:workflow_id>/steps/add/', workflow_add_step, name='workflow_add_step'),
    path('workflows/steps/<int:step_id>/update/', workflow_update_step, name='workflow_update_step'),
    path('workflows/steps/<int:step_id>/', workflow_delete_step, name='workflow_delete_step'),
    
    # Task 53: Document Management System - DEPRECATED
    # These URLs are now handled by TQM Module 5 (document_management app)
    # Commenting out to prevent conflicts - use /documents/ which routes to document_management
    # path('documents/', document_list, name='document_list'),
    # path('documents/upload/', document_upload, name='document_upload'),
    # path('documents/<int:document_id>/', document_detail, name='document_detail'),
    # path('documents/<int:document_id>/download/', document_download, name='document_download'),
    # path('documents/<int:document_id>/edit/', document_edit, name='document_edit'),
    # path('documents/<int:document_id>/delete/', document_delete, name='document_delete'),
    # path('documents/<int:document_id>/new-version/', document_new_version, name='document_new_version'),
    # path('documents/<int:document_id>/share/', document_share, name='document_share'),
    # path('documents/<int:document_id>/comment/', document_add_comment, name='document_add_comment'),
    # path('documents/my/', my_documents, name='my_documents'),
    # path('documents/shared/', shared_with_me, name='shared_with_me'),
    # path('documents/categories/', category_manage, name='category_manage'),
    # path('documents/categories/create/', category_create, name='category_create'),
    
    # Task 54: Video Tutorial Library
    path('videos/', video_library, name='video_library'),
    path('videos/upload/', video_upload, name='video_upload'),
    path('videos/<int:video_id>/', video_detail, name='video_detail'),
    path('videos/<int:video_id>/progress/', video_update_progress, name='video_update_progress'),
    path('videos/<int:video_id>/rate/', video_rate, name='video_rate'),
    path('videos/progress/', my_progress, name='my_video_progress'),
    path('videos/categories/', video_category_list, name='video_category_list'),
    path('videos/analytics/', video_analytics, name='video_analytics'),
    path('playlists/create/', playlist_create, name='playlist_create'),
    path('playlists/<int:playlist_id>/', playlist_detail, name='playlist_detail'),
    path('playlists/<int:playlist_id>/add/', playlist_add_video, name='playlist_add_video'),
    
    # Activity Feed (Task 55)
    path('activity/', recent_activity_feed, name='recent_activity_feed'),
    path('activity/api/', activity_feed_api, name='activity_feed_api'),
    path('activity/<int:activity_id>/read/', mark_activity_read, name='mark_activity_read'),
    path('activity/mark-all-read/', mark_all_read, name='mark_all_read'),
    path('activity/<int:activity_id>/archive/', archive_activity, name='archive_activity'),
    path('activity/<int:activity_id>/pin/', toggle_activity_pin, name='toggle_activity_pin'),
    path('activity/widget/', activity_dashboard_widget, name='activity_dashboard_widget'),
    path('activity/widgets/manage/', manage_activity_widgets, name='manage_activity_widgets'),
    path('activity/widgets/<int:widget_id>/delete/', delete_activity_widget, name='delete_activity_widget'),
    path('activity/statistics/', activity_statistics, name='activity_statistics'),
    
    # Compliance Dashboard Widgets (Task 56)
    path('compliance/', compliance_dashboard, name='compliance_dashboard'),
    path('compliance/widgets/<int:widget_id>/api/', widget_data_api, name='widget_data_api'),
    path('compliance/metrics/refresh/', refresh_compliance_metrics, name='refresh_compliance_metrics'),
    path('compliance/metrics/refresh/<int:care_home_id>/', refresh_compliance_metrics, name='refresh_compliance_metrics_home'),
    path('compliance/widgets/manage/', manage_widgets, name='manage_compliance_widgets'),
    path('compliance/widgets/create/', create_widget, name='create_compliance_widget'),
    path('compliance/widgets/<int:widget_id>/delete/', delete_widget, name='delete_compliance_widget'),
    path('compliance/report/', compliance_report, name='compliance_report'),
    
    # Export Endpoints (PDF & Excel) - Week 5
    path('exports/ci-performance/pdf/', views.export_ci_performance_pdf, name='export_ci_pdf'),
    path('exports/ci-performance/excel/', views.export_ci_performance_excel, name='export_ci_excel'),
    path('exports/staffing-analysis/pdf/', views.export_staffing_analysis_pdf, name='export_staffing_pdf'),
    path('exports/staffing-analysis/excel/', views.export_staffing_analysis_excel, name='export_staffing_excel'),
    path('exports/overtime-summary/pdf/', views.export_overtime_summary_pdf, name='export_overtime_pdf'),
    path('exports/overtime-summary/excel/', views.export_overtime_summary_excel, name='export_overtime_excel'),
    
    # Intelligent OT Distribution System
    path('ot-intelligence/', ot_intelligence_dashboard, name='ot_intelligence_dashboard'),
    path('ot-intelligence/rankings/', ot_staff_rankings, name='ot_staff_rankings'),
    path('ot-intelligence/fairness/', ot_fairness_report, name='ot_fairness_report'),
    path('ot-intelligence/staff/<str:sap>/', ot_staff_detail, name='ot_staff_detail'),
    path('api/ot-intelligence/request-coverage/', ot_request_coverage_api, name='ot_request_coverage_api'),
    path('api/ot-intelligence/analytics/', ot_analytics_api, name='ot_analytics_api'),
]
