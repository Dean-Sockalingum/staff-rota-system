"""
URL Configuration for Quality Audits (PDSA Tracker)

This module defines URL patterns for the PDSA Tracker interface.
All URLs are prefixed with /quality-audits/ in the main project URLconf.
"""

from django.urls import path
from . import views

app_name = 'quality_audits'

urlpatterns = [
    # Dashboard / Home
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # PDSA Project URLs
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    
    # PDSA Cycle URLs
    path('projects/<int:project_pk>/cycles/create/', views.CycleCreateView.as_view(), name='cycle_create'),
    path('cycles/<int:pk>/', views.CycleDetailView.as_view(), name='cycle_detail'),
    path('cycles/<int:pk>/update/', views.CycleUpdateView.as_view(), name='cycle_update'),
    path('cycles/<int:pk>/delete/', views.CycleDeleteView.as_view(), name='cycle_delete'),
    
    # Data Point Entry URLs
    path('cycles/<int:cycle_pk>/data/add/', views.DataPointCreateView.as_view(), name='datapoint_create'),
    path('data/<int:pk>/update/', views.DataPointUpdateView.as_view(), name='datapoint_update'),
    path('data/<int:pk>/delete/', views.DataPointDeleteView.as_view(), name='datapoint_delete'),
    
    # ML/AI Feature URLs
    path('projects/<int:pk>/generate-aim/', views.GenerateSMARTAimView.as_view(), name='generate_aim'),
    path('projects/<int:pk>/suggest-hypotheses/', views.SuggestHypothesesView.as_view(), name='suggest_hypotheses'),
    path('cycles/<int:pk>/analyze/', views.AnalyzeCycleDataView.as_view(), name='analyze_cycle'),
    path('projects/<int:pk>/predict-success/', views.PredictSuccessView.as_view(), name='predict_success'),
    path('projects/<int:pk>/chatbot/', views.PDSAChatbotView.as_view(), name='chatbot'),
    
    # Team Member URLs
    path('projects/<int:project_pk>/team/add/', views.TeamMemberCreateView.as_view(), name='team_member_create'),
    path('team/<int:pk>/remove/', views.TeamMemberDeleteView.as_view(), name='team_member_delete'),
    
    # Reports & Analytics
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('reports/project/<int:pk>/pdf/', views.ProjectReportPDFView.as_view(), name='project_report_pdf'),
    path('reports/cycle/<int:pk>/pdf/', views.CycleReportPDFView.as_view(), name='cycle_report_pdf'),
    
    # Export & Reports
    path('export/projects/csv/', views.ExportProjectCSVView.as_view(), name='export_projects_csv'),
    path('export/cycles/<int:pk>/csv/', views.ExportCycleDataCSVView.as_view(), name='export_cycle_csv'),
    
    # API Endpoints (for AJAX calls)
    path('api/dashboard/stats/', views.DashboardStatsAPIView.as_view(), name='dashboard_stats'),
    path('api/projects/<int:pk>/status/', views.ProjectStatusAPIView.as_view(), name='api_project_status'),
    path('api/cycles/<int:pk>/chart-data/', views.CycleChartDataAPIView.as_view(), name='api_cycle_chart_data'),
]
