"""
TQM Module 7: Performance Metrics & KPIs URL Configuration
"""

from django.urls import path
from . import views

app_name = 'performance_kpis'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # KPI Management
    path('kpis/', views.kpi_list_view, name='kpi_list'),
    path('kpis/<int:kpi_id>/', views.kpi_detail_view, name='kpi_detail'),
    
    # Measurements
    path('kpis/<int:kpi_id>/measure/', views.measurement_create_view, name='measurement_create'),
    
    # Balanced Scorecard
    path('balanced-scorecard/', views.balanced_scorecard_view, name='balanced_scorecard'),
    
    # API Endpoints
    path('api/dashboard/<int:dashboard_id>/', views.dashboard_api, name='dashboard_api'),
    path('api/kpi/<int:kpi_id>/trend/', views.kpi_trend_api, name='kpi_trend_api'),
]
