"""
Mobile App API - URL Configuration
==================================

RESTful API endpoints for mobile app access.

Created: 30 December 2025
Task 38: Mobile App API - Fixed version
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_mobile_api import (
    UserViewSet, RoleViewSet, CareHomeViewSet, UnitViewSet,
    ShiftTypeViewSet, ShiftViewSet, LeaveRequestViewSet,
    ShiftSwapRequestViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='api-user')
router.register(r'roles', RoleViewSet, basename='api-role')
router.register(r'care-homes', CareHomeViewSet, basename='api-care-home')
router.register(r'units', UnitViewSet, basename='api-unit')
router.register(r'shift-types', ShiftTypeViewSet, basename='api-shift-type')
router.register(r'shifts', ShiftViewSet, basename='api-shift')
router.register(r'leave-requests', LeaveRequestViewSet, basename='api-leave-request')
router.register(r'shift-swaps', ShiftSwapRequestViewSet, basename='api-shift-swap')

# Wire up API URLs
urlpatterns = [
    path('', include(router.urls)),
]
