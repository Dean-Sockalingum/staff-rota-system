"""
Risk Management URL Configuration

URL patterns for risk management module

"""

from django.urls import path
from . import views

app_name = 'risk_management'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('stats/', views.dashboard_stats, name='dashboard_stats'),
    
    # Risk CRUD
    path('risks/', views.risk_list, name='risk_list'),
    path('risks/create/', views.risk_create, name='risk_create'),
    path('risks/<int:pk>/', views.risk_detail, name='risk_detail'),
    path('risks/<int:pk>/edit/', views.risk_edit, name='risk_edit'),
    path('risks/<int:pk>/delete/', views.risk_delete, name='risk_delete'),
    
    # Mitigations
    path('risks/<int:risk_pk>/mitigations/create/', views.mitigation_create, name='mitigation_create'),
    
    # Reviews
    path('risks/<int:risk_pk>/reviews/create/', views.review_create, name='review_create'),
    
    # Risk Matrix
    path('matrix/', views.risk_matrix, name='risk_matrix'),
    
    # Reports & Export
    path('reports/', views.reports, name='reports'),
    path('export/csv/', views.export_risks_csv, name='export_csv'),
]
