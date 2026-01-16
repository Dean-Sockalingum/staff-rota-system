from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Policy, PolicyVersion, PolicyAcknowledgement, PolicyReview,
    Procedure, ProcedureStep, PolicyComplianceCheck, AuditTrail
)


class PolicyVersionInline(admin.TabularInline):
    """Inline for policy versions"""
    model = PolicyVersion
    extra = 0
    fields = ('version_number', 'change_summary', 'is_current', 'approval_date', 'approved_by')
    readonly_fields = ('created_date', 'created_by')


class PolicyReviewInline(admin.TabularInline):
    """Inline for policy reviews"""
    model = PolicyReview
    extra = 0
    fields = ('review_date', 'reviewer', 'review_outcome', 'completion_date')


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    """Admin interface for Policy model"""
    list_display = (
        'policy_number', 'title', 'category', 'status_badge', 
        'version', 'effective_date', 'next_review_date', 
        'review_status_badge', 'is_mandatory'
    )
    list_filter = ('category', 'status', 'is_mandatory', 'effective_date', 'next_review_date')
    search_fields = ('policy_number', 'title', 'keywords', 'summary')
    readonly_fields = ('created_date', 'updated_date')
    inlines = [PolicyVersionInline, PolicyReviewInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('policy_number', 'title', 'category', 'summary', 'keywords')
        }),
        ('Dates & Review', {
            'fields': ('effective_date', 'next_review_date', 'review_frequency_months')
        }),
        ('Status & Version', {
            'fields': ('status', 'version', 'is_mandatory')
        }),
        ('Ownership', {
            'fields': ('owner', 'department')
        }),
        ('Regulatory', {
            'fields': ('regulatory_framework',)
        }),
        ('Document', {
            'fields': ('file_path',)
        }),
        ('Metadata', {
            'fields': ('created_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'draft': 'gray',
            'under_review': 'orange',
            'active': 'green',
            'archived': 'red',
            'superseded': 'purple'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def review_status_badge(self, obj):
        """Display review status with warning if overdue"""
        if obj.is_overdue_review:
            return format_html(
                '<span style="background-color: red; color: white; padding: 3px 10px; border-radius: 3px;">⚠ OVERDUE</span>'
            )
        elif obj.days_until_review and obj.days_until_review <= 30:
            return format_html(
                '<span style="background-color: orange; color: white; padding: 3px 10px; border-radius: 3px;">Due Soon ({} days)</span>',
                obj.days_until_review
            )
        return format_html('<span style="color: green;">✓ Current</span>')
    review_status_badge.short_description = 'Review Status'


@admin.register(PolicyVersion)
class PolicyVersionAdmin(admin.ModelAdmin):
    """Admin interface for PolicyVersion model"""
    list_display = (
        'policy', 'version_number', 'current_badge', 
        'created_date', 'created_by', 'approval_status_badge'
    )
    list_filter = ('is_current', 'approval_date', 'created_date')
    search_fields = ('policy__policy_number', 'policy__title', 'change_summary')
    readonly_fields = ('created_date',)
    
    def current_badge(self, obj):
        """Display if version is current"""
        if obj.is_current:
            return format_html('<span style="background-color: green; color: white; padding: 3px 10px; border-radius: 3px;">CURRENT</span>')
        return '-'
    current_badge.short_description = 'Current'
    
    def approval_status_badge(self, obj):
        """Display approval status"""
        if obj.approval_date:
            return format_html(
                '<span style="color: green;">✓ Approved {}</span>',
                obj.approval_date.strftime('%d %b %Y')
            )
        return format_html('<span style="color: orange;">⏳ Pending</span>')
    approval_status_badge.short_description = 'Approval'


@admin.register(PolicyAcknowledgement)
class PolicyAcknowledgementAdmin(admin.ModelAdmin):
    """Admin interface for PolicyAcknowledgement model"""
    list_display = (
        'policy', 'staff_member', 'acknowledged_date', 
        'acknowledgement_method', 'signature', 'overdue_badge'
    )
    list_filter = ('acknowledgement_method', 'is_overdue', 'acknowledged_date')
    search_fields = ('policy__policy_number', 'policy__title', 'staff_member__username', 'signature')
    readonly_fields = ('acknowledged_date', 'ip_address')
    
    def overdue_badge(self, obj):
        """Display overdue status"""
        if obj.is_overdue:
            return format_html('<span style="background-color: red; color: white; padding: 3px 10px; border-radius: 3px;">OVERDUE</span>')
        return format_html('<span style="color: green;">✓ Current</span>')
    overdue_badge.short_description = 'Status'


@admin.register(PolicyReview)
class PolicyReviewAdmin(admin.ModelAdmin):
    """Admin interface for PolicyReview model"""
    list_display = (
        'policy', 'review_date', 'reviewer', 'review_outcome',
        'completion_status_badge', 'next_review_date'
    )
    list_filter = ('review_outcome', 'review_date', 'completion_date')
    search_fields = ('policy__policy_number', 'policy__title', 'reviewer__username')
    readonly_fields = ('completion_date',)
    
    def completion_status_badge(self, obj):
        """Display completion status"""
        if obj.is_completed:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 10px; border-radius: 3px;">✓ Completed</span>'
            )
        return format_html('<span style="background-color: orange; color: white; padding: 3px 10px; border-radius: 3px;">⏳ Pending</span>')
    completion_status_badge.short_description = 'Status'


class ProcedureStepInline(admin.TabularInline):
    """Inline for procedure steps"""
    model = ProcedureStep
    extra = 1
    fields = ('step_number', 'description', 'critical_point', 'evidence_required')


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    """Admin interface for Procedure model"""
    list_display = ('procedure_number', 'title', 'policy', 'last_updated', 'updated_by')
    list_filter = ('last_updated',)
    search_fields = ('procedure_number', 'title', 'policy__policy_number')
    inlines = [ProcedureStepInline]


@admin.register(PolicyComplianceCheck)
class PolicyComplianceCheckAdmin(admin.ModelAdmin):
    """Admin interface for PolicyComplianceCheck model"""
    list_display = (
        'policy', 'check_date', 'checker', 'compliance_badge',
        'completed', 'overdue_badge'
    )
    list_filter = ('compliance_status', 'completed', 'check_date')
    search_fields = ('policy__policy_number', 'policy__title', 'checker__username')
    
    def compliance_badge(self, obj):
        """Display compliance status with colored badge"""
        colors = {
            'fully_compliant': 'green',
            'partially_compliant': 'orange',
            'non_compliant': 'red',
            'not_applicable': 'gray'
        }
        color = colors.get(obj.compliance_status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_compliance_status_display()
        )
    compliance_badge.short_description = 'Compliance'
    
    def overdue_badge(self, obj):
        """Display overdue warning"""
        if obj.is_overdue:
            return format_html('<span style="background-color: red; color: white; padding: 3px 10px; border-radius: 3px;">⚠ OVERDUE</span>')
        return '-'
    overdue_badge.short_description = 'Overdue'


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    """Admin interface for AuditTrail model"""
    list_display = ('policy', 'action_type', 'performed_by', 'timestamp', 'details_preview')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('policy__policy_number', 'policy__title', 'performed_by__username', 'details')
    readonly_fields = ('policy', 'action_type', 'performed_by', 'timestamp', 'details', 'previous_values')
    
    def details_preview(self, obj):
        """Show truncated details"""
        if len(obj.details) > 50:
            return obj.details[:50] + '...'
        return obj.details
    details_preview.short_description = 'Details'
    
    def has_add_permission(self, request):
        """Prevent manual creation of audit trail entries"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of audit trail entries"""
        return False
