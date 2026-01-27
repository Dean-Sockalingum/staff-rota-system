"""
TQM Module 3: Experience & Feedback URL Configuration
"""

from django.urls import path
from . import views

app_name = 'experience_feedback'

urlpatterns = [
    # Dashboard
    path('', views.experience_dashboard, name='dashboard'),
    
    # Satisfaction Surveys
    path('surveys/', views.survey_list, name='survey_list'),
    path('surveys/new/', views.survey_create, name='survey_create'),
    path('surveys/<int:pk>/', views.survey_detail, name='survey_detail'),
    path('surveys/<int:pk>/edit/', views.survey_edit, name='survey_edit'),
    path('surveys/<int:pk>/delete/', views.survey_delete, name='survey_delete'),
    path('surveys/<int:pk>/pdf/', views.survey_pdf, name='survey_pdf'),
    path('surveys/blank/<str:survey_type>/pdf/', views.blank_survey_pdf, name='blank_survey_pdf'),
    
    # Public Survey (no login required)
    path('public/<str:token>/', views.public_survey, name='public_survey'),
    
    # Complaints
    path('complaints/', views.complaint_list, name='complaint_list'),
    path('complaints/new/', views.complaint_create, name='complaint_create'),
    path('complaints/<int:pk>/', views.complaint_detail, name='complaint_detail'),
    path('complaints/<int:pk>/edit/', views.complaint_edit, name='complaint_edit'),
    path('complaints/<int:pk>/update/', views.complaint_update_status, name='complaint_update'),
    path('complaints/<int:pk>/delete/', views.complaint_delete, name='complaint_delete'),
    path('complaints/<int:pk>/add-stage/', views.complaint_add_stage, name='complaint_add_stage'),
    path('complaints/<int:pk>/add-stakeholder/', views.complaint_add_stakeholder, name='complaint_add_stakeholder'),
    
    # EBCD Touchpoints
    path('ebcd-touchpoints/', views.ebcd_touchpoint_list, name='ebcd_list'),
    
    # Quality of Life Assessments
    path('qol-assessments/', views.qol_assessment_list, name='qol_list'),
    
    # Feedback Themes
    path('feedback-themes/', views.feedback_theme_list, name='theme_list'),
    
    # JSON API Endpoints for Charts
    path('api/satisfaction-trend/', views.satisfaction_trend_data, name='satisfaction_trend_api'),
    path('api/complaint-stats/', views.complaint_stats_data, name='complaint_stats_api'),
    path('api/nps-trend/', views.nps_trend_data, name='nps_trend_api'),
    
    # You Said, We Did Actions
    path('yswda/', views.yswda_dashboard, name='yswda_dashboard'),
    path('yswda/list/', views.yswda_list, name='yswda_list'),
    path('yswda/new/', views.yswda_create, name='yswda_create'),
    path('yswda/<int:pk>/', views.yswda_detail, name='yswda_detail'),
    path('yswda/<int:pk>/edit/', views.yswda_update, name='yswda_update'),
    path('yswda/<int:pk>/delete/', views.yswda_delete, name='yswda_delete'),
    
    # Public You Said, We Did Board (no login required)
    path('public/yswda/<int:care_home_id>/', views.yswda_public_board, name='yswda_public_board'),
    
    # Survey Distribution
    path('distribution/', views.distribution_dashboard, name='distribution_dashboard'),
    path('distribution/schedules/', views.schedule_list, name='schedule_list'),
    path('distribution/schedules/new/', views.schedule_create, name='schedule_create'),
    path('distribution/schedules/<int:pk>/edit/', views.schedule_edit, name='schedule_edit'),
    path('distribution/schedules/<int:pk>/delete/', views.schedule_delete, name='schedule_delete'),
    path('distribution/<int:pk>/send/', views.distribution_send, name='distribution_send'),
    
    # Public Survey Links (no login required)
    path('survey/<str:token>/', views.survey_by_token, name='public_survey_token'),
    path('survey/<str:token>/qr/', views.survey_qr_code, name='survey_qr_code'),
    path('survey/<str:token>/thanks/', views.survey_thank_you, name='survey_thank_you'),
    
    # ========================================================================
    # FAMILY PORTAL
    # ========================================================================
    
    # Family Portal Authentication (no login required)
    path('family/login/', views.family_login, name='family_login'),
    path('family/logout/', views.family_logout, name='family_logout'),
    
    # Family Portal Pages (login required)
    path('family/dashboard/', views.family_dashboard, name='family_dashboard'),
    path('family/messages/', views.family_messages_list, name='family_messages_list'),
    path('family/messages/new/', views.family_message_create, name='family_message_create'),
    path('family/messages/<int:message_id>/', views.family_message_detail, name='family_message_detail'),
    path('family/surveys/', views.family_surveys_list, name='family_surveys_list'),
    
    # Staff Management of Family Messages (login required, staff only)
    path('staff/family-messages/', views.staff_family_messages, name='staff_family_messages'),
    path('staff/family-messages/<int:message_id>/respond/', views.staff_message_respond, name='staff_message_respond'),
    
    # ========================================================================
    # ADVANCED ANALYTICS & REPORTING
    # ========================================================================
    
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/export/', views.analytics_export, name='analytics_export'),
]
