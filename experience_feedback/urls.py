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
    path('complaints/<int:pk>/', views.complaint_detail, name='complaint_detail'),
    
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
]
