"""
URLs for Task 55-59: Activity Feed, Compliance Widgets, Form Autosave, Leave Calendar
Minimal import file to avoid dependency issues in main urls.py
"""
from django.urls import path
from . import views

# Import Task 55 views
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

urlpatterns = [
    # Task 55: Activity Feed URLs
    path('activity/', recent_activity_feed, name='activity_feed'),  # Main activity feed
    path('api/activity/feed/', activity_feed_api, name='activity_feed_api'),
    path('api/activity/mark-read/<int:activity_id>/', mark_activity_read, name='mark_activity_read'),
    path('api/activity/mark-all-read/', mark_all_read, name='mark_all_read'),
    path('api/activity/archive/<int:activity_id>/', archive_activity, name='archive_activity'),
    path('api/activity/pin/<int:activity_id>/', toggle_activity_pin, name='toggle_activity_pin'),
    path('api/activity/widgets/', activity_dashboard_widget, name='activity_dashboard_widget'),
    path('api/activity/widgets/manage/', manage_activity_widgets, name='manage_activity_widgets'),
    path('api/activity/widgets/<int:widget_id>/delete/', delete_activity_widget, name='delete_activity_widget'),
    path('api/activity/statistics/', activity_statistics, name='activity_statistics'),
    
    # Existing notification URLs (from management.urls, duplicated here for compatibility)
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/count/', views.unread_notifications_count, name='unread_notifications_count'),
]
