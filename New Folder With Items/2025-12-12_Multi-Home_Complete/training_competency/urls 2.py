"""
TQM Module 4: Training & Competency URL Configuration
"""

from django.urls import path
from . import views

app_name = 'training_competency'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Competency Framework - List & Detail
    path('competencies/', views.competency_list, name='competency_list'),
    path('competencies/<int:pk>/', views.competency_detail, name='competency_detail'),
    
    # Competency Framework - CRUD
    path('competencies/new/', views.CompetencyFrameworkCreateView.as_view(), name='competency_create'),
    path('competencies/<int:pk>/edit/', views.CompetencyFrameworkUpdateView.as_view(), name='competency_update'),
    path('competencies/<int:pk>/delete/', views.CompetencyFrameworkDeleteView.as_view(), name='competency_delete'),
    
    # Assessments - List
    path('my-assessments/', views.my_assessments, name='my_assessments'),
    
    # Assessments - CRUD
    path('assessments/new/', views.CompetencyAssessmentCreateView.as_view(), name='assessment_create'),
    path('assessments/<int:pk>/edit/', views.CompetencyAssessmentUpdateView.as_view(), name='assessment_update'),
    path('assessments/<int:pk>/delete/', views.CompetencyAssessmentDeleteView.as_view(), name='assessment_delete'),
    
    # Learning Pathways - List & Detail
    path('pathways/', views.learning_pathways, name='learning_pathways'),
    path('pathways/<int:pk>/', views.pathway_detail, name='pathway_detail'),
    path('pathways/<int:pk>/enroll/', views.enroll_pathway, name='enroll_pathway'),
    
    # Learning Pathways - CRUD
    path('pathways/new/', views.LearningPathwayCreateView.as_view(), name='pathway_create'),
    path('pathways/<int:pk>/edit/', views.LearningPathwayUpdateView.as_view(), name='pathway_update'),
    path('pathways/<int:pk>/delete/', views.LearningPathwayDeleteView.as_view(), name='pathway_delete'),
    
    # Learning Plans - List
    path('my-learning-plans/', views.my_learning_plans, name='my_learning_plans'),
    
    # Learning Plans - CRUD
    path('learning-plans/new/', views.StaffLearningPlanCreateView.as_view(), name='learning_plan_create'),
    path('learning-plans/<int:pk>/edit/', views.StaffLearningPlanUpdateView.as_view(), name='learning_plan_update'),
    path('learning-plans/<int:pk>/delete/', views.StaffLearningPlanDeleteView.as_view(), name='learning_plan_delete'),
    
    # Training Matrix - CRUD
    path('training-matrix/new/', views.TrainingMatrixCreateView.as_view(), name='training_matrix_create'),
    path('training-matrix/<int:pk>/edit/', views.TrainingMatrixUpdateView.as_view(), name='training_matrix_update'),
    path('training-matrix/<int:pk>/delete/', views.TrainingMatrixDeleteView.as_view(), name='training_matrix_delete'),
    
    # Skills Matrix
    path('skills-matrix/', views.skills_matrix, name='skills_matrix'),
    
    # Training Requirements
    path('training-requirements/', views.training_requirements, name='training_requirements'),
]
