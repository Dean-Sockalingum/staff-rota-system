"""
URLs for Task 56: Compliance Widgets
Minimal import file to avoid dependency issues in main urls.py
"""
from django.urls import path

# Import Task 56 views
from .views_compliance_widgets import (
    compliance_dashboard,
    widget_data_api,
    manage_widgets,
    create_widget,
    delete_widget,
    compliance_report,
    refresh_compliance_metrics
)

urlpatterns = [
    # Task 56: Compliance Widget URLs
    path('compliance/dashboard/', compliance_dashboard, name='compliance_dashboard'),
    path('api/compliance/widget/<int:widget_id>/', widget_data_api, name='widget_data_api'),
    path('compliance/widgets/', manage_widgets, name='manage_widgets'),
    path('compliance/widgets/create/', create_widget, name='create_widget'),
    path('compliance/widgets/<int:widget_id>/delete/', delete_widget, name='delete_widget'),
    path('compliance/report/', compliance_report, name='compliance_report'),
    path('api/compliance/refresh/', refresh_compliance_metrics, name='refresh_compliance_metrics'),
    path('api/compliance/refresh/<int:care_home_id>/', refresh_compliance_metrics, name='refresh_compliance_metrics_home'),
]
