"""
URL Configuration for TQM Module 5: Policies & Procedures
"""
from django.urls import path
from . import views

app_name = 'policies_procedures'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Policy CRUD
    path('policies/', views.policy_list, name='policy_list'),
    path('policies/<int:pk>/', views.policy_detail, name='policy_detail'),
    path('policies/new/', views.PolicyCreateView.as_view(), name='policy_create'),
    path('policies/<int:pk>/edit/', views.PolicyUpdateView.as_view(), name='policy_update'),
    path('policies/<int:pk>/delete/', views.PolicyDeleteView.as_view(), name='policy_delete'),
    
    # Version Control
    path('policies/<int:pk>/versions/', views.version_history, name='version_history'),
    path('policies/<int:policy_pk>/versions/new/', views.PolicyVersionCreateView.as_view(), name='version_create'),
    
    # Staff Acknowledgements
    path('policies/<int:pk>/acknowledge/', views.acknowledge_policy, name='acknowledge_policy'),
    path('my-acknowledgements/', views.my_acknowledgements, name='my_acknowledgements'),
    path('pending-acknowledgements/', views.pending_acknowledgements, name='pending_acknowledgements'),
    
    # Policy Reviews
    path('policies/<int:policy_pk>/review/', views.PolicyReviewCreateView.as_view(), name='review_create'),
    path('reviews/<int:pk>/edit/', views.PolicyReviewUpdateView.as_view(), name='review_update'),
    
    # Compliance
    path('compliance/', views.compliance_dashboard, name='compliance_dashboard'),
    path('compliance/new/', views.PolicyComplianceCheckCreateView.as_view(), name='compliance_create'),
]
