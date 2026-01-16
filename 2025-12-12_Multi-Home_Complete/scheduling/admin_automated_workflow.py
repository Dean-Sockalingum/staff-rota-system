"""
Admin configuration for Automated Workflow and Multi-Home models

Registers all new models with Django admin interface for management and monitoring.

Created: 10 December 2025
"""

from django.contrib import admin
from .models_automated_workflow import (
    SicknessAbsence,
    StaffingCoverRequest,
    ReallocationRequest,
    OvertimeOfferBatch,
    OvertimeOffer,
    AgencyRequest,
    LongTermCoverPlan,
    PostShiftAdministration,
)
from .models_multi_home import CareHome


@admin.register(CareHome)
class CareHomeAdmin(admin.ModelAdmin):
    list_display = ['name', 'bed_capacity', 'current_occupancy', 'occupancy_rate', 'home_manager', 'is_active']
    list_filter = ['is_active', 'name']
    search_fields = ['name', 'care_inspectorate_id', 'location_address']
    readonly_fields = ['created_at', 'updated_at', 'occupancy_rate', 'available_beds']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'bed_capacity', 'current_occupancy', 'is_active')
        }),
        ('Location', {
            'fields': ('location_address', 'postcode', 'main_phone', 'main_email')
        }),
        ('Regulatory', {
            'fields': ('care_inspectorate_id', 'registration_number', 'opened_date')
        }),
        ('Management', {
            'fields': ('home_manager',)
        }),
        ('Financial Budgets', {
            'fields': ('budget_agency_monthly', 'budget_overtime_monthly')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SicknessAbsence)
class SicknessAbsenceAdmin(admin.ModelAdmin):
    list_display = ['staff_member', 'start_date', 'expected_duration_days', 'is_long_term', 'status', 'reported_datetime']
    list_filter = ['status', 'is_long_term', 'fit_note_required', 'start_date']
    search_fields = ['staff_member__first_name', 'staff_member__last_name', 'staff_member__sap', 'reason']
    readonly_fields = ['reported_datetime', 'created_at', 'updated_at', 'is_long_term']
    filter_horizontal = ['affected_shifts']
    
    fieldsets = (
        ('Staff & Timing', {
            'fields': ('staff_member', 'reported_by', 'reported_datetime', 'start_date', 'end_date', 'expected_duration_days')
        }),
        ('Classification', {
            'fields': ('is_long_term', 'status')
        }),
        ('Affected Shifts', {
            'fields': ('affected_shifts',)
        }),
        ('Details', {
            'fields': ('reason', 'notes')
        }),
        ('Medical Certificate', {
            'fields': ('fit_note_required', 'fit_note_received', 'fit_note_date'),
            'classes': ('collapse',)
        }),
        ('Return to Work', {
            'fields': ('actual_return_date', 'return_to_work_interview_completed'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StaffingCoverRequest)
class StaffingCoverRequestAdmin(admin.ModelAdmin):
    list_display = ['shift', 'priority', 'status', 'created_datetime', 'resolved_at', 'resolved_by']
    list_filter = ['status', 'priority', 'requested_by_system', 'created_datetime']
    search_fields = ['shift__unit__name', 'assigned_manager__first_name', 'assigned_manager__last_name']
    readonly_fields = ['created_datetime', 'created_at', 'updated_at', 'resolved_at', 'reallocation_deadline', 'ot_response_deadline']
    
    fieldsets = (
        ('Request Details', {
            'fields': ('shift', 'absence', 'priority', 'requested_by_system')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'assigned_manager')
        }),
        ('Deadlines', {
            'fields': ('reallocation_deadline', 'ot_response_deadline')
        }),
        ('Resolution', {
            'fields': ('resolved_at', 'resolved_by')
        }),
        ('System', {
            'fields': ('created_datetime', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReallocationRequest)
class ReallocationRequestAdmin(admin.ModelAdmin):
    list_display = ['cover_request', 'source_home', 'target_shift', 'status', 'response_deadline', 'responded_at']
    list_filter = ['status', 'response_deadline']
    search_fields = ['source_home__name', 'target_shift__unit__name']
    readonly_fields = ['created_at', 'responded_at']


@admin.register(OvertimeOfferBatch)
class OvertimeOfferBatchAdmin(admin.ModelAdmin):
    list_display = ['cover_request', 'response_deadline', 'status', 'created_at']
    list_filter = ['status', 'response_deadline']
    readonly_fields = ['created_at']


@admin.register(OvertimeOffer)
class OvertimeOfferAdmin(admin.ModelAdmin):
    list_display = ['staff_member', 'shift', 'priority_rank', 'status', 'sent_at', 'responded_at', 'estimated_payment']
    list_filter = ['status', 'sent_at']
    search_fields = ['staff_member__first_name', 'staff_member__last_name', 'staff_member__sap']
    readonly_fields = ['sent_at', 'responded_at']
    
    fieldsets = (
        ('Offer Details', {
            'fields': ('batch', 'staff_member', 'shift', 'priority_rank')
        }),
        ('Status & Timing', {
            'fields': ('status', 'sent_at', 'responded_at')
        }),
        ('Payment', {
            'fields': ('ot_rate_multiplier', 'estimated_payment')
        }),
    )


@admin.register(AgencyRequest)
class AgencyRequestAdmin(admin.ModelAdmin):
    list_display = ['shift', 'status', 'approval_deadline', 'approved_by', 'approved_at', 'estimated_cost']
    list_filter = ['status', 'approval_deadline', 'created_at']
    search_fields = ['shift__unit__name', 'approved_by']
    readonly_fields = ['created_at', 'approval_deadline', 'escalation_log']
    
    fieldsets = (
        ('Request Details', {
            'fields': ('cover_request', 'shift', 'estimated_cost')
        }),
        ('Approval Status', {
            'fields': ('status', 'approval_deadline', 'approved_by', 'approved_at')
        }),
        ('Agency', {
            'fields': ('preferred_agency',)
        }),
        ('Escalation Log', {
            'fields': ('escalation_log',),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(LongTermCoverPlan)
class LongTermCoverPlanAdmin(admin.ModelAdmin):
    list_display = ['absence', 'start_date', 'expected_end_date', 'total_shifts_affected', 'status', 'estimated_cost', 'actual_cost']
    list_filter = ['status', 'start_date']
    search_fields = ['absence__staff_member__first_name', 'absence__staff_member__last_name']
    readonly_fields = ['created_at', 'updated_at', 'strategy']
    
    fieldsets = (
        ('Absence Details', {
            'fields': ('absence', 'start_date', 'expected_end_date', 'total_shifts_affected')
        }),
        ('Status & Strategy', {
            'fields': ('status', 'strategy')
        }),
        ('Budget', {
            'fields': ('estimated_cost', 'actual_cost')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PostShiftAdministration)
class PostShiftAdministrationAdmin(admin.ModelAdmin):
    list_display = ['shift', 'completed_at', 'completed_by', 'overtime_worked', 'agency_used', 'amar_updated', 'rota_updated', 'payroll_updated']
    list_filter = ['overtime_worked', 'agency_used', 'amar_updated', 'rota_updated', 'payroll_updated', 'completed_at']
    search_fields = ['shift__unit__name', 'completed_by__first_name', 'completed_by__last_name']
    readonly_fields = ['completed_at']
    filter_horizontal = ['ot_staff']
    
    fieldsets = (
        ('Shift Details', {
            'fields': ('shift', 'completed_by', 'completed_at')
        }),
        ('Sickness', {
            'fields': ('sickness_confirmed', 'sickness_notes')
        }),
        ('Off Duty', {
            'fields': ('off_duty_changes',),
            'classes': ('collapse',)
        }),
        ('Overtime', {
            'fields': ('overtime_worked', 'ot_staff', 'ot_hours_confirmed')
        }),
        ('Agency', {
            'fields': ('agency_used', 'agency_staff_details', 'agency_hours_confirmed', 'agency_cost_actual')
        }),
        ('System Updates', {
            'fields': ('amar_updated', 'rota_updated', 'payroll_updated')
        }),
    )


# ==================== Admin Actions ====================

@admin.action(description="Trigger staffing workflow for selected absences")
def trigger_staffing_workflow(modeladmin, request, queryset):
    """Admin action to manually trigger workflow for sickness absences"""
    from scheduling.workflow_orchestrator import trigger_absence_workflow
    from django.contrib import messages
    
    triggered_count = 0
    errors = []
    
    for absence in queryset:
        try:
            result = trigger_absence_workflow(absence)
            if result.get('success'):
                triggered_count += 1
            else:
                errors.append(f"Absence #{absence.id}: {result.get('error', 'Unknown error')}")
        except Exception as e:
            errors.append(f"Absence #{absence.id}: {str(e)}")
    
    if triggered_count > 0:
        messages.success(request, f"Successfully triggered workflow for {triggered_count} absence(s)")
    
    if errors:
        for error in errors:
            messages.error(request, error)


@admin.action(description="View cover request status")
def view_cover_request_status(modeladmin, request, queryset):
    """Admin action to view workflow status for selected absences"""
    from scheduling.workflow_orchestrator import get_workflow_status
    from django.contrib import messages
    
    for absence in queryset:
        cover_requests = absence.cover_requests.all()
        
        if not cover_requests.exists():
            messages.warning(request, f"Absence #{absence.id}: No cover request found")
            continue
        
        for cover_request in cover_requests:
            status = get_workflow_status(cover_request)
            
            status_msg = (
                f"Absence #{absence.id} - {absence.staff_member.full_name} "
                f"({absence.start_date} to {absence.end_date or 'TBD'}) - "
                f"Status: {status['status']}, "
                f"Cost: £{status.get('total_cost', 0):.2f}"
            )
            
            messages.info(request, status_msg)


@admin.action(description="Cancel workflow for selected absences")
def cancel_staffing_workflow(modeladmin, request, queryset):
    """Admin action to cancel workflow for selected absences"""
    from scheduling.workflow_orchestrator import _cancel_pending_ot_offers, _cancel_pending_reallocations
    from django.contrib import messages
    
    cancelled_count = 0
    
    for absence in queryset:
        cover_requests = absence.cover_requests.filter(
            status__in=['PENDING', 'REALLOCATION_OFFERED', 'OT_OFFERED', 'AGENCY_REQUESTED']
        )
        
        for cover_request in cover_requests:
            _cancel_pending_ot_offers(cover_request)
            _cancel_pending_reallocations(cover_request)
            cover_request.status = 'CANCELLED'
            cover_request.save()
            cancelled_count += 1
    
    if cancelled_count > 0:
        messages.success(request, f"Successfully cancelled {cancelled_count} cover request(s)")
    else:
        messages.warning(request, "No active workflows found to cancel")


@admin.action(description="Escalate to agency immediately")
def escalate_to_agency_action(modeladmin, request, queryset):
    """Admin action to manually escalate to agency (Priority 3)"""
    from scheduling.workflow_orchestrator import escalate_to_agency
    from django.contrib import messages
    
    escalated_count = 0
    errors = []
    
    for absence in queryset:
        cover_requests = absence.cover_requests.filter(
            status__in=['PENDING', 'REALLOCATION_OFFERED', 'OT_OFFERED']
        )
        
        for cover_request in cover_requests:
            try:
                result = escalate_to_agency(cover_request)
                if result.get('success'):
                    escalated_count += 1
                else:
                    errors.append(f"CoverRequest #{cover_request.id}: {result.get('error', 'Unknown error')}")
            except Exception as e:
                errors.append(f"CoverRequest #{cover_request.id}: {str(e)}")
    
    if escalated_count > 0:
        messages.success(request, f"Successfully escalated {escalated_count} cover request(s) to agency")
    
    if errors:
        for error in errors:
            messages.error(request, error)


# Update SicknessAbsenceAdmin
class SicknessAbsenceAdminWithActions(admin.ModelAdmin):
    list_display = ('staff_member', 'start_date', 'end_date', 'expected_duration_days', 'is_long_term', 'status')
    list_filter = ('is_long_term', 'status', 'start_date')
    search_fields = ('staff_member__first_name', 'staff_member__last_name', 'reason')
    readonly_fields = ('reported_datetime', 'is_long_term')
    
    actions = [
        trigger_staffing_workflow,
        view_cover_request_status,
        cancel_staffing_workflow,
        escalate_to_agency_action
    ]
    
    fieldsets = (
        ('Staff Information', {
            'fields': ('staff_member', 'reported_by', 'reported_datetime')
        }),
        ('Absence Details', {
            'fields': ('start_date', 'end_date', 'expected_duration_days', 'reason', 'is_long_term', 'status')
        }),
        ('Shifts', {
            'fields': ('affected_shifts',),
            'classes': ('collapse',)
        }),
    )
    
    # Inline for cover requests
    class CoverRequestInline(admin.TabularInline):
        model = StaffingCoverRequest
        extra = 0
        readonly_fields = ('created_datetime', 'status', 'priority')
        can_delete = False
        fields = ('status', 'priority', 'created_datetime')
        
        def has_add_permission(self, request, obj=None):
            return False
    
    inlines = [CoverRequestInline]


# Re-register SicknessAbsence with actions
try:
    admin.site.unregister(SicknessAbsence)
except admin.sites.NotRegistered:
    pass

admin.site.register(SicknessAbsence, SicknessAbsenceAdminWithActions)
