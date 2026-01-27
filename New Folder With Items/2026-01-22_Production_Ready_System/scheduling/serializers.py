"""
API Serializers for Mobile App
===============================

Serializers for the mobile API endpoints.

Created: 30 December 2025
Task 38: Mobile App API - Fixed version
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Shift, ShiftType, Unit, LeaveRequest, ShiftSwapRequest, Role
from .models_multi_home import CareHome

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.CharField(read_only=True)
    annual_leave_remaining = serializers.IntegerField(read_only=True)
    shifts_per_week = serializers.IntegerField(read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'sap', 'first_name', 'last_name', 'full_name',
            'email', 'phone_number', 'role', 'role_name', 'unit', 'unit_name',
            'team', 'shift_preference', 'is_active', 'annual_leave_allowance',
            'annual_leave_used', 'annual_leave_remaining', 'shifts_per_week'
        ]
        read_only_fields = ['sap', 'full_name', 'annual_leave_remaining', 'shifts_per_week']


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model"""
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'is_management', 'permission_level']


class CareHomeSerializer(serializers.ModelSerializer):
    """Serializer for CareHome model"""
    occupancy_rate = serializers.SerializerMethodField()
    manager_name = serializers.CharField(source='home_manager.full_name', read_only=True)
    
    class Meta:
        model = CareHome
        fields = [
            'id', 'name', 'bed_capacity', 'current_occupancy',
            'occupancy_rate', 'location_address', 'postcode',
            'main_phone', 'main_email', 'is_active', 'home_manager',
            'manager_name'
        ]
    
    def get_occupancy_rate(self, obj):
        """Calculate occupancy rate percentage"""
        if obj.bed_capacity > 0:
            return round((obj.current_occupancy / obj.bed_capacity) * 100, 1)
        return 0


class UnitSerializer(serializers.ModelSerializer):
    """Serializer for Unit model"""
    care_home_name = serializers.CharField(source='care_home.name', read_only=True)
    
    class Meta:
        model = Unit
        fields = [
            'id', 'name', 'description', 'care_home', 'care_home_name',
            'is_active', 'min_day_staff', 'ideal_day_staff',
            'min_night_staff', 'ideal_night_staff'
        ]


class ShiftTypeSerializer(serializers.ModelSerializer):
    """Serializer for ShiftType model"""
    duration_hours = serializers.SerializerMethodField()
    care_home_name = serializers.CharField(source='care_home.name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = ShiftType
        fields = [
            'id', 'name', 'start_time', 'end_time', 'care_home',
            'care_home_name', 'role', 'role_name', 'is_active', 'duration_hours'
        ]
    
    def get_duration_hours(self, obj):
        """Calculate shift duration in hours"""
        from datetime import datetime, timedelta
        
        start = datetime.combine(datetime.today(), obj.start_time)
        end = datetime.combine(datetime.today(), obj.end_time)
        
        # Handle overnight shifts
        if end < start:
            end += timedelta(days=1)
        
        duration = end - start
        return duration.total_seconds() / 3600


class ShiftSerializer(serializers.ModelSerializer):
    """Serializer for Shift model"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    shift_type_name = serializers.CharField(source='shift_type.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    care_home_name = serializers.CharField(source='unit.care_home.name', read_only=True)
    
    class Meta:
        model = Shift
        fields = [
            'id', 'user', 'user_name', 'shift_type', 'shift_type_name',
            'date', 'unit', 'unit_name', 'care_home_name', 'status',
            'shift_classification', 'shift_pattern', 'is_overtime',
            'created_at', 'updated_at'
        ]


class LeaveRequestSerializer(serializers.ModelSerializer):
    """Serializer for LeaveRequest model"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'user', 'user_name', 'leave_type', 'start_date',
            'end_date', 'days_requested', 'status', 'reason',
            'approved_by', 'approved_by_name', 'approval_date',
            'approval_notes', 'created_at'
        ]


class ShiftSwapRequestSerializer(serializers.ModelSerializer):
    """Serializer for ShiftSwapRequest model"""
    requesting_user_name = serializers.CharField(source='requesting_user.full_name', read_only=True)
    target_user_name = serializers.CharField(source='target_user.full_name', read_only=True)
    requesting_shift_date = serializers.DateField(source='requesting_shift.date', read_only=True)
    target_shift_date = serializers.DateField(source='target_shift.date', read_only=True)
    
    class Meta:
        model = ShiftSwapRequest
        fields = [
            'id', 'requesting_user', 'requesting_user_name', 'target_user', 'target_user_name',
            'requesting_shift', 'requesting_shift_date', 'target_shift', 'target_shift_date',
            'status', 'requested_at', 'processed_at', 'processed_by',
            'automated_decision', 'qualification_match_score',
            'wdt_compliance_check'
        ]
