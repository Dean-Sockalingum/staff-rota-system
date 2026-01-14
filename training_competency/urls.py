"""
TQM Module 4: Training & Competency URL Configuration
"""

from django.urls import path
from . import views

app_name = 'training_competency'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Competency Framework
    path('competencies/', views.competency_list, name='competency_list'),
    path('competencies/<int:pk>/', views.competency_detail, name='competency_detail'),
    
    # Assessments
    path('my-assessments/', views.my_assessments, name='my_assessments'),
    
    # Learning Pathways
    path('pathways/', views.learning_pathways, name='learning_pathways'),
    path('pathways/<int:pk>/', views.pathway_detail, name='pathway_detail'),
    path('pathways/<int:pk>/enroll/', views.enroll_pathway, name='enroll_pathway'),
    
    # Learning Plans
    path('my-learning-plans/', views.my_learning_plans, name='my_learning_plans'),
    
    # Skills Matrix
    path('skills-matrix/', views.skills_matrix, name='skills_matrix'),
    
    # Training Requirements
    path('training-requirements/', views.training_requirements, name='training_requirements'),
]
