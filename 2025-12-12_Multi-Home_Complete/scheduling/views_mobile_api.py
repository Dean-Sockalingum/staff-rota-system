"""
Mobile API Views
================

ViewSets for mobile app REST API.

Created: 30 December 2025
Task 38: Mobile App API - Fixed version
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import Shift, ShiftType, Unit, LeaveRequest, ShiftSwapRequest, Role
from .models_multi_home import CareHome
from .serializers import (
    UserSerializer, RoleSerializer, CareHomeSerializer, UnitSerializer,
    ShiftTypeSerializer, ShiftSerializer, LeaveRequestSerializer,
    ShiftSwapRequestSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for user information.
    
    list: Get all users
    retrieve: Get specific user
    me: Get current user's information
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['role', 'unit', 'team', 'is_active']
    search_fields = ['first_name', 'last_name', 'sap', 'email']
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for roles.
    
    list: Get all roles
    retrieve: Get specific role
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]


class CareHomeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for care homes.
    
    list: Get all care homes
    retrieve: Get specific care home
    """
    queryset = CareHome.objects.filter(is_active=True)
    serializer_class = CareHomeSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['name', 'is_active']
    search_fields = ['name', 'location_address']


class UnitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for units.
    
    list: Get all units
    retrieve: Get specific unit
    """
    queryset = Unit.objects.filter(is_active=True)
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['care_home', 'is_active']
    search_fields = ['name', 'description']


class ShiftTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for shift types.
    
    list: Get all shift types
    retrieve: Get specific shift type
    """
    queryset = ShiftType.objects.filter(is_active=True)
    serializer_class = ShiftTypeSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['care_home', 'role', 'is_active']
    search_fields = ['name']


class ShiftViewSet(viewsets.ModelViewSet):
    """
    API endpoint for shifts.
    
    list: Get all shifts (filterable)
    retrieve: Get specific shift
    my_shifts: Get current user's shifts
    upcoming: Get upcoming shifts
    """
    queryset = Shift.objects.all().select_related('user', 'shift_type', 'unit', 'unit__care_home')
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['user', 'unit', 'shift_type', 'date', 'status']
    search_fields = ['user__first_name', 'user__last_name']
    ordering_fields = ['date', 'status']
    ordering = ['-date']
    
    @action(detail=False, methods=['get'])
    def my_shifts(self, request):
        """Get shifts for the current user"""
        shifts = self.queryset.filter(user=request.user)
        
        # Optional date filtering
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            shifts = shifts.filter(date__gte=start_date)
        if end_date:
            shifts = shifts.filter(date__lte=end_date)
        
        page = self.paginate_queryset(shifts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(shifts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming shifts for the current user"""
        today = timezone.now().date()
        shifts = self.queryset.filter(
            user=request.user,
            date__gte=today
        ).order_by('date')[:10]
        
        serializer = self.get_serializer(shifts, many=True)
        return Response(serializer.data)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for leave requests.
    
    list: Get all leave requests
    retrieve: Get specific leave request
    my_requests: Get current user's leave requests
    create: Create new leave request
    """
    queryset = LeaveRequest.objects.all().select_related('user', 'approved_by')
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['user', 'leave_type', 'status']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Automatically set the requesting user"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get leave requests for the current user"""
        requests = self.queryset.filter(user=request.user)
        
        page = self.paginate_queryset(requests)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a leave request (managers only)"""
        leave_request = self.get_object()
        
        # Check if user has permission to approve
        if not request.user.role or not request.user.role.can_approve_leave:
            return Response(
                {'error': 'You do not have permission to approve leave requests'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        leave_request.status = 'APPROVED'
        leave_request.approved_by = request.user
        leave_request.approval_date = timezone.now()
        leave_request.approval_notes = request.data.get('notes', '')
        leave_request.save()
        
        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deny(self, request, pk=None):
        """Deny a leave request (managers only)"""
        leave_request = self.get_object()
        
        # Check if user has permission to deny
        if not request.user.role or not request.user.role.can_approve_leave:
            return Response(
                {'error': 'You do not have permission to deny leave requests'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        leave_request.status = 'DENIED'
        leave_request.approved_by = request.user
        leave_request.approval_date = timezone.now()
        leave_request.approval_notes = request.data.get('notes', '')
        leave_request.save()
        
        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)


class ShiftSwapRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for shift swap requests.
    
    list: Get all shift swap requests
    retrieve: Get specific shift swap request
    my_requests: Get current user's swap requests
    create: Create new shift swap request
    """
    queryset = ShiftSwapRequest.objects.all().select_related(
        'requesting_user', 'target_user', 'requesting_shift', 'target_shift'
    )
    serializer_class = ShiftSwapRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['requesting_user', 'target_user', 'status']
    ordering_fields = ['requested_at']
    ordering = ['-requested_at']
    
    def perform_create(self, serializer):
        """Automatically set the requesting user"""
        serializer.save(requesting_user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get shift swap requests involving the current user"""
        from django.db.models import Q
        
        requests = self.queryset.filter(
            Q(requesting_user=request.user) | Q(target_user=request.user)
        )
        
        page = self.paginate_queryset(requests)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a shift swap request"""
        swap_request = self.get_object()
        
        # Check if user is target user or has management permissions
        if request.user != swap_request.target_user:
            if not request.user.role or not request.user.role.can_approve_swaps:
                return Response(
                    {'error': 'You do not have permission to approve this swap'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        swap_request.status = 'APPROVED'
        swap_request.processed_at = timezone.now()
        swap_request.processed_by = request.user
        swap_request.save()
        
        # Actually perform the swap
        requesting_shift = swap_request.requesting_shift
        target_shift = swap_request.target_shift
        
        # Swap the users
        requesting_shift.user, target_shift.user = target_shift.user, requesting_shift.user
        requesting_shift.save()
        target_shift.save()
        
        serializer = self.get_serializer(swap_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deny(self, request, pk=None):
        """Deny a shift swap request"""
        swap_request = self.get_object()
        
        # Check if user is target user or has management permissions
        if request.user != swap_request.target_user:
            if not request.user.role or not request.user.role.can_approve_swaps:
                return Response(
                    {'error': 'You do not have permission to deny this swap'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        swap_request.status = 'DENIED'
        swap_request.processed_at = timezone.now()
        swap_request.processed_by = request.user
        swap_request.save()
        
        serializer = self.get_serializer(swap_request)
        return Response(serializer.data)
