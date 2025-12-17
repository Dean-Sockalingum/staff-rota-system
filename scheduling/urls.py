from django.urls import path
from . import views
from .views_senior_dashboard import senior_management_dashboard, senior_dashboard_export

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Manager/Admin Views
    path('dashboard/', views.manager_dashboard, name='manager_dashboard'),
    
    # Home-Specific Dashboards (5 homes with role-based access)
    path('home/', views.home_dashboard, name='home_dashboard'),  # Auto-detects user's home
    path('home/<slug:home_slug>/', views.home_dashboard, name='home_dashboard_specific'),  # Specific home view
    
    path('senior-dashboard/export/', senior_dashboard_export, name='senior_dashboard_export'),
    path('senior-dashboard/', senior_management_dashboard, name='senior_management_dashboard'),
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
    
    # Agency & Additional Staffing APIs
    path('api/agency-companies/', views.agency_companies_api, name='agency_companies_api'),
    path('api/reports/daily-additional-staffing/', views.daily_additional_staffing_report, name='daily_additional_staffing_report'),
    path('api/reports/weekly-additional-staffing/', views.weekly_additional_staffing_report, name='weekly_additional_staffing_report'),
    
    # Staffing Alert URLs
    path('staffing/alerts/', views.staffing_my_alerts, name='staffing_my_alerts'),
    path('staffing/respond/<uuid:token>/<str:action>/', views.staffing_alert_respond, name='staffing_alert_respond'),
    path('staffing/create-alert/', views.staffing_create_alert, name='staffing_create_alert'),
    path('staffing/dashboard/', views.staffing_dashboard, name='staffing_dashboard'),
]