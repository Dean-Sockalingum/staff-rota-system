"""
TQM Module 5: Document & Policy Management URL Configuration
"""

from django.urls import path
from . import views

app_name = 'document_management'

urlpatterns = [
    # Dashboard
    path('', views.document_dashboard, name='dashboard'),
    
    # Documents
    path('documents/', views.document_list, name='document_list'),
    path('documents/<int:pk>/', views.document_detail, name='document_detail'),
    path('documents/<int:document_pk>/versions/', views.version_history, name='version_history'),
    
    # Reviews
    path('reviews/', views.review_list, name='review_list'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    
    # Staff Acknowledgements
    path('my-acknowledgements/', views.my_acknowledgements, name='my_acknowledgements'),
    path('acknowledge/<int:pk>/', views.acknowledge_document, name='acknowledge_document'),
    
    # JSON API Endpoints for Charts
    path('api/document-stats/', views.document_stats_data, name='document_stats_api'),
    path('api/acknowledgement-stats/', views.acknowledgement_stats_data, name='acknowledgement_stats_api'),
    path('api/compliance-framework/', views.compliance_framework_data, name='compliance_framework_api'),
]
