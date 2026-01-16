"""
URLs for Task 59: Leave Calendar
Minimal import file to avoid dependency issues in main urls.py
"""
from django.urls import path

# Import Task 59 views
from .views_leave_calendar import (
    leave_calendar_view,
    team_leave_calendar_view,
    leave_calendar_data_api,
    leave_coverage_report_api
)

urlpatterns = [
    # Task 59: Leave Calendar URLs
    path('leave/calendar/', leave_calendar_view, name='leave_calendar'),
    path('leave/calendar/team/', team_leave_calendar_view, name='team_leave_calendar'),
    path('api/leave/calendar/data/', leave_calendar_data_api, name='leave_calendar_data_api'),
    path('api/leave/coverage-report/', leave_coverage_report_api, name='leave_coverage_report_api'),
]
