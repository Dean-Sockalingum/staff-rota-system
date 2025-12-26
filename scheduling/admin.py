from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Role, Unit, ShiftType, Shift, LeaveRequest, 
    ShiftSwapRequest, BlackoutPeriod, StaffReallocation, ActivityLog,
    ComplianceRule, ComplianceCheck, ComplianceViolation, 
    AuditReport, DataChangeLog, SystemAccessLog,
    TrainingCourse, TrainingRecord, InductionProgress,
    SupervisionRecord, IncidentReport
)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_management', 'can_approve_leave', 'can_manage_rota']
    list_filter = ['is_management', 'can_approve_leave', 'can_manage_rota']
    search_fields = ['name']

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['sap', 'first_name', 'last_name', 'email', 'role', 'is_active', 'annual_leave_remaining']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['sap', 'first_name', 'last_name', 'email']
    ordering = ['sap']
    
    fieldsets = (
        (None, {'fields': ('sap', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Role & Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Annual Leave', {'fields': ('annual_leave_allowance', 'annual_leave_used', 'annual_leave_year_start')}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('sap', 'first_name', 'last_name', 'email', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'last_login']

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'min_day_staff', 'min_night_staff', 'min_weekend_staff', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(ShiftType)
class ShiftTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'duration_hours', 'color_code', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ['user', 'unit', 'shift_type', 'date', 'status', 'created_by']
    list_filter = ['unit', 'shift_type', 'status', 'date']
    search_fields = ['user__first_name', 'user__last_name', 'user__sap']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Info', {'fields': ('user', 'unit', 'shift_type', 'date', 'status')}),
        ('Custom Times', {'fields': ('custom_start_time', 'custom_end_time')}),
        ('Additional Info', {'fields': ('notes', 'created_by')}),
    )

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'leave_type', 'start_date', 'end_date', 'days_requested', 'status', 'automated_decision']
    list_filter = ['leave_type', 'status', 'automated_decision', 'is_blackout_period', 'causes_staffing_shortfall']
    search_fields = ['user__first_name', 'user__last_name', 'user__sap']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Request Details', {'fields': ('user', 'leave_type', 'start_date', 'end_date', 'days_requested', 'reason')}),
        ('Status', {'fields': ('status', 'approved_by', 'approval_date', 'approval_notes')}),
        ('Automated Checks', {'fields': ('is_blackout_period', 'causes_staffing_shortfall', 'automated_decision')}),
    )
    
    readonly_fields = ['days_requested']

@admin.register(ShiftSwapRequest)
class ShiftSwapRequestAdmin(admin.ModelAdmin):
    list_display = ['requesting_user', 'target_user', 'status', 'target_user_approved', 'management_approved', 'created_at']
    list_filter = ['status', 'target_user_approved', 'management_approved']
    search_fields = ['requesting_user__first_name', 'requesting_user__last_name', 'target_user__first_name', 'target_user__last_name']
    date_hierarchy = 'created_at'

@admin.register(BlackoutPeriod)
class BlackoutPeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_active', 'created_by']
    list_filter = ['is_active', 'units']
    search_fields = ['name']
    date_hierarchy = 'start_date'

@admin.register(StaffReallocation)
class StaffReallocationAdmin(admin.ModelAdmin):
    list_display = ['target_unit', 'target_date', 'target_shift_type', 'assigned_user', 'status', 'created_at']
    list_filter = ['target_unit', 'target_shift_type', 'status']
    search_fields = ['assigned_user__first_name', 'assigned_user__last_name']
    date_hierarchy = 'target_date'

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'automated', 'created_at', 'created_by']
    list_filter = ['action_type', 'automated']
    search_fields = ['user__first_name', 'user__last_name', 'description']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']


# Audit and Compliance Admin

@admin.register(ComplianceRule)
class ComplianceRuleAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'severity', 'is_active']
    list_filter = ['category', 'severity', 'is_active']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ComplianceCheck)
class ComplianceCheckAdmin(admin.ModelAdmin):
    list_display = ['rule', 'check_date', 'status', 'violations_found', 'items_checked', 'started_at']
    list_filter = ['status', 'rule__category', 'is_automated']
    search_fields = ['rule__name', 'rule__code']
    date_hierarchy = 'check_date'
    readonly_fields = ['started_at', 'completed_at']


@admin.register(ComplianceViolation)
class ComplianceViolationAdmin(admin.ModelAdmin):
    list_display = ['rule', 'status', 'severity', 'affected_user', 'detected_at', 'resolved_at']
    list_filter = ['status', 'severity', 'rule__category']
    search_fields = ['description', 'affected_user__first_name', 'affected_user__last_name']
    date_hierarchy = 'detected_at'
    readonly_fields = ['detected_at', 'acknowledged_at', 'resolved_at']


@admin.register(AuditReport)
class AuditReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'period_start', 'period_end', 'status', 'generated_by', 'generated_at']
    list_filter = ['report_type', 'status']
    search_fields = ['title', 'description']
    date_hierarchy = 'generated_at'
    readonly_fields = ['generated_at']


@admin.register(DataChangeLog)
class DataChangeLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'content_type', 'object_id', 'field_name', 'timestamp', 'is_automated']
    list_filter = ['action', 'content_type', 'is_automated']
    search_fields = ['user__first_name', 'user__last_name', 'object_id']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']


@admin.register(SystemAccessLog)
class SystemAccessLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'access_type', 'ip_address', 'success', 'timestamp']
    list_filter = ['access_type', 'success']
    search_fields = ['user__first_name', 'user__last_name', 'username_attempt', 'ip_address']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']


# ============================================================================
# CARE INSPECTORATE COMPLIANCE ADMIN
# ============================================================================

@admin.register(TrainingCourse)
class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'frequency', 'validity_months', 'is_mandatory', 'sssc_cpd_eligible']
    list_filter = ['category', 'is_mandatory', 'frequency', 'sssc_cpd_eligible']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']


@admin.register(TrainingRecord)
class TrainingRecordAdmin(admin.ModelAdmin):
    list_display = ['staff_member', 'course', 'completion_date', 'expiry_date', 'get_status', 'competency_assessed']
    list_filter = ['course__category', 'competency_assessed', 'competency_outcome']
    search_fields = ['staff_member__first_name', 'staff_member__last_name', 'course__name']
    date_hierarchy = 'completion_date'
    readonly_fields = ['created_at', 'updated_at', 'get_status', 'days_until_expiry']
    
    fieldsets = (
        ('Staff & Course', {'fields': ('staff_member', 'course')}),
        ('Dates', {'fields': ('completion_date', 'expiry_date', 'get_status', 'days_until_expiry')}),
        ('Training Details', {'fields': ('trainer_name', 'training_provider', 'certificate_number', 'certificate_file')}),
        ('Competency Assessment', {'fields': ('competency_assessed', 'competency_assessor', 'competency_date', 'competency_outcome')}),
        ('SSSC CPD', {'fields': ('sssc_cpd_hours_claimed',)}),
        ('Notes', {'fields': ('notes',)}),
        ('Audit', {'fields': ('created_at', 'updated_at', 'created_by')}),
    )


@admin.register(InductionProgress)
class InductionProgressAdmin(admin.ModelAdmin):
    list_display = ['staff_member', 'start_date', 'expected_completion_date', 'get_completion_percentage', 
                    'final_assessment_complete', 'final_assessment_outcome']
    list_filter = ['final_assessment_complete', 'final_assessment_outcome']
    search_fields = ['staff_member__first_name', 'staff_member__last_name']
    date_hierarchy = 'start_date'
    readonly_fields = ['get_completion_percentage', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Staff Member', {'fields': ('staff_member',)}),
        ('Dates', {'fields': ('start_date', 'expected_completion_date', 'actual_completion_date')}),
        ('Week 1 - Essential Induction', {'fields': (
            'week1_orientation_complete', 'week1_fire_safety_complete', 
            'week1_infection_control_complete', 'week1_moving_handling_complete',
            'week1_health_safety_complete'
        )}),
        ('Weeks 2-4 - Foundation Care', {'fields': (
            'week2_4_safeguarding_complete', 'week2_4_person_centred_care_complete'
        )}),
        ('Weeks 5-8 - Specialist Skills', {'fields': (
            'week5_8_medication_complete', 'week5_8_clinical_skills_complete'
        )}),
        ('Weeks 9-12 - Professional Development', {'fields': (
            'week9_12_sssc_registration_complete', 'week9_12_quality_improvement_complete',
            'week9_12_supervision_support_complete'
        )}),
        ('Competency Hours', {'fields': (
            'personal_care_hours', 'meal_prep_hours', 'documentation_hours', 'medication_hours'
        )}),
        ('Final Assessment', {'fields': (
            'final_assessment_complete', 'final_assessment_date', 'final_assessment_outcome', 'assessor'
        )}),
        ('Progress', {'fields': ('get_completion_percentage',)}),
        ('Notes', {'fields': ('notes',)}),
    )


@admin.register(SupervisionRecord)
class SupervisionRecordAdmin(admin.ModelAdmin):
    list_display = ['staff_member', 'session_date', 'session_type', 'supervisor', 'wellbeing_score', 
                    'mandatory_training_current', 'next_supervision_date']
    list_filter = ['session_type', 'mandatory_training_current', 'sssc_registration_current', 
                   'is_probationary_review', 'workload_manageable']
    search_fields = ['staff_member__first_name', 'staff_member__last_name', 'supervisor__first_name', 'supervisor__last_name']
    date_hierarchy = 'session_date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Session Details', {'fields': ('staff_member', 'supervisor', 'session_date', 'session_type', 'duration_minutes')}),
        ('Wellbeing', {'fields': ('wellbeing_score', 'sickness_days_since_last', 'wellbeing_concerns', 'support_offered')}),
        ('Performance', {'fields': ('performance_strengths', 'performance_development')}),
        ('Training', {'fields': ('mandatory_training_current', 'training_needs_identified')}),
        ('SSSC', {'fields': ('sssc_registration_current', 'sssc_cpd_hours_to_date')}),
        ('Safeguarding', {'fields': ('safeguarding_concerns_discussed', 'safeguarding_notes')}),
        ('Incidents', {'fields': ('incidents_since_last', 'incident_learning')}),
        ('Workload', {'fields': ('workload_manageable', 'workload_notes')}),
        ('Actions', {'fields': ('actions_from_previous', 'new_actions', 'next_supervision_date')}),
        ('Probationary Review', {'fields': (
            'is_probationary_review', 'probation_progress', 'probation_recommendation'
        )}),
        ('Sign-Off', {'fields': ('staff_signature_date', 'supervisor_signature_date', 'staff_comments')}),
    )


@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'incident_date', 'incident_type', 'severity', 'risk_rating',
                    'care_inspectorate_notified', 'incident_closed']
    list_filter = ['incident_type', 'severity', 'risk_rating', 'care_inspectorate_notified', 
                   'police_notified', 'safeguarding_alert_raised', 'incident_closed']
    search_fields = ['reference_number', 'service_user_name', 'description']
    date_hierarchy = 'incident_date'
    readonly_fields = ['created_at', 'updated_at', 'reported_date', 'requires_care_inspectorate_notification']
    
    fieldsets = (
        ('Basic Details', {'fields': ('reference_number', 'incident_date', 'incident_time', 
                                     'reported_date', 'reported_by', 'incident_type', 'location')}),
        ('Service User', {'fields': ('service_user_name', 'service_user_dob')}),
        ('Description', {'fields': ('description', 'witnesses', 'was_witnessed')}),
        ('Immediate Actions', {'fields': ('immediate_actions', 'injuries_sustained', 
                                         'body_map_completed', 'photos_taken')}),
        ('Medical Intervention', {'fields': ('gp_contacted', 'ambulance_called', 'hospital_attendance',
                                            'hospital_admission', 'medical_notes')}),
        ('Severity & Risk', {'fields': ('severity', 'risk_rating', 'requires_care_inspectorate_notification')}),
        ('External Notifications', {'fields': (
            'care_inspectorate_notified', 'care_inspectorate_ref',
            'police_notified', 'police_crime_ref',
            'local_authority_notified', 'safeguarding_alert_raised'
        )}),
        ('Investigation', {'fields': (
            'investigation_required', 'investigation_assigned_to', 'investigation_due_date',
            'investigation_complete', 'investigation_findings'
        )}),
        ('Learning & Actions', {'fields': ('lessons_learned', 'preventive_actions')}),
        ('Closure', {'fields': ('incident_closed', 'closed_date', 'closed_by')}),
        ('Manager Review', {'fields': ('manager_reviewed', 'manager_review_date', 'manager_comments', 'manager')}),
    )


# ============================================================================
# TASK 11: AI ASSISTANT FEEDBACK & LEARNING SYSTEM
# ============================================================================

from .feedback_learning import AIQueryFeedback, UserPreference

@admin.register(AIQueryFeedback)
class AIQueryFeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'short_query', 'intent_detected', 'rating', 'feedback_type', 'is_positive', 'created_at']
    list_filter = ['rating', 'feedback_type', 'intent_detected', 'created_at', 'learned_from']
    search_fields = ['user__first_name', 'user__last_name', 'query_text', 'feedback_comment']
    readonly_fields = ['created_at', 'learned_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Query Details', {'fields': ('user', 'query_text', 'intent_detected', 'confidence_score', 'session_id')}),
        ('Response', {'fields': ('response_text', 'response_data')}),
        ('Feedback', {'fields': ('rating', 'feedback_type', 'feedback_comment')}),
        ('Refinement', {'fields': ('refinement_query', 'refinement_successful')}),
        ('Learning', {'fields': ('learned_from', 'learned_at')}),
        ('Metadata', {'fields': ('created_at',)}),
    )
    
    def short_query(self, obj):
        return obj.query_text[:50] + '...' if len(obj.query_text) > 50 else obj.query_text
    short_query.short_description = 'Query'
    
    def is_positive(self, obj):
        return '✅' if obj.is_positive else '⚠️' if obj.rating == 3 else '❌'
    is_positive.short_description = 'Satisfaction'


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_detail_level', 'preferred_tone', 'avg_satisfaction_rating', 
                    'total_queries', 'total_feedback_count', 'last_updated']
    list_filter = ['preferred_detail_level', 'preferred_tone', 'prefers_examples', 
                   'prefers_step_by_step', 'prefers_visualizations']
    search_fields = ['user__first_name', 'user__last_name', 'most_common_intent']
    readonly_fields = ['last_updated', 'total_queries', 'total_feedback_count', 
                      'avg_satisfaction_rating', 'avg_queries_per_session', 'most_common_intent']
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Learned Preferences', {'fields': ('preferred_detail_level', 'preferred_tone')}),
        ('Interaction Patterns', {'fields': ('avg_queries_per_session', 'most_common_intent', 
                                            'avg_satisfaction_rating')}),
        ('Preference Flags', {'fields': ('prefers_examples', 'prefers_step_by_step', 'prefers_visualizations')}),
        ('Statistics', {'fields': ('total_queries', 'total_feedback_count', 'last_updated')}),
    )


# Import automated workflow admin configurations
from .admin_automated_workflow import *


