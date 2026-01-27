from django.contrib import admin
from django.utils.html import format_html

from .models import (
    AnnualLeaveEntitlement,
    AnnualLeaveTransaction,
    ContactLogEntry,
    MedicalCertificate,
    SicknessAbsenceSummary,
    SicknessRecord,
    StaffProfile,
)


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "employment_status", "start_date", "end_date", "receives_cover_alerts")
    search_fields = ("user__sap", "user__first_name", "user__last_name")
    list_filter = ("employment_status", "receives_cover_alerts")


@admin.register(SicknessRecord)
class SicknessRecordAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "status",
        "first_working_day",
        "estimated_return_to_work",
        "actual_last_working_day",
        "total_working_days_sick",
        "trigger_reached",
    )
    list_filter = ("status", "reported_at", "trigger_reached")
    search_fields = ("profile__user__sap", "profile__user__first_name", "profile__user__last_name")


@admin.register(MedicalCertificate)
class MedicalCertificateAdmin(admin.ModelAdmin):
    list_display = ("sickness_record", "uploaded_by", "uploaded_at")
    search_fields = ("sickness_record__profile__user__sap",)
    list_filter = ("uploaded_at",)


@admin.register(ContactLogEntry)
class ContactLogEntryAdmin(admin.ModelAdmin):
    list_display = ("profile", "contact_method", "contact_datetime", "recorded_by", "follow_up_required")
    search_fields = ("profile__user__sap", "profile__user__first_name", "profile__user__last_name")
    list_filter = ("contact_method", "follow_up_required")


class AnnualLeaveTransactionInline(admin.TabularInline):
    """Inline display of leave transactions within entitlement admin."""
    model = AnnualLeaveTransaction
    extra = 0
    fields = ('transaction_type', 'hours', 'days_display', 'balance_after', 'description', 'approved_by', 'approved_at', 'created_at')
    readonly_fields = ('days_display', 'created_at', 'balance_after')
    can_delete = False
    
    def days_display(self, obj):
        """Show transaction in days"""
        if obj.id:
            return obj.days_display
        return "-"
    days_display.short_description = "Days"


@admin.register(AnnualLeaveEntitlement)
class AnnualLeaveEntitlementAdmin(admin.ModelAdmin):
    list_display = (
        'profile',
        'leave_year_display',
        'total_entitlement_display',
        'hours_used_display',
        'hours_remaining_display',
        'carryover_display',
        'updated_at',
    )
    list_filter = ('leave_year_start', 'created_at')
    search_fields = ('profile__user__sap', 'profile__user__first_name', 'profile__user__last_name')
    readonly_fields = ('hours_used', 'hours_pending', 'hours_remaining', 'updated_at', 'created_at')
    inlines = [AnnualLeaveTransactionInline]
    
    fieldsets = (
        ('Staff Member', {
            'fields': ('profile', 'created_by')
        }),
        ('Leave Year', {
            'fields': ('leave_year_start', 'leave_year_end')
        }),
        ('Entitlement (Hours)', {
            'fields': (
                'contracted_hours_per_week',
                'total_entitlement_hours',
                'carryover_hours',
                'carryover_expiry_date',
            )
        }),
        ('Balance (Auto-calculated)', {
            'fields': ('hours_used', 'hours_pending', 'hours_remaining'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def leave_year_display(self, obj):
        return f"{obj.leave_year_start.strftime('%d/%m/%Y')} - {obj.leave_year_end.strftime('%d/%m/%Y')}"
    leave_year_display.short_description = "Leave Year"
    
    def total_entitlement_display(self, obj):
        return format_html(
            '<strong>{} hrs</strong> ({} days)',
            f'{obj.total_available_hours:.1f}',
            f'{obj.days_entitlement:.1f}'
        )
    total_entitlement_display.short_description = "Total Entitlement"
    
    def hours_used_display(self, obj):
        return format_html(
            '{} hrs ({} days)',
            f'{obj.hours_used:.1f}',
            f'{obj.days_used:.1f}'
        )
    hours_used_display.short_description = "Used"
    
    def hours_remaining_display(self, obj):
        color = 'green' if obj.hours_remaining > 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} hrs ({} days)</span>',
            color,
            f'{obj.hours_remaining:.1f}',
            f'{obj.days_remaining:.1f}'
        )
    hours_remaining_display.short_description = "Remaining"
    
    def carryover_display(self, obj):
        if obj.carryover_hours > 0:
            return format_html(
                '{} hrs (exp: {})',
                f'{obj.carryover_hours:.1f}',
                obj.carryover_expiry_date.strftime('%d/%m/%Y') if obj.carryover_expiry_date else 'N/A'
            )
        return "-"
    carryover_display.short_description = "Carryover"


@admin.register(AnnualLeaveTransaction)
class AnnualLeaveTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'profile_name',
        'transaction_type',
        'hours_with_sign',
        'days_display',
        'balance_after_display',
        'approved_by',
        'description_short',
    )
    list_filter = ('transaction_type', 'created_at', 'approved_by')
    search_fields = (
        'entitlement__profile__user__sap',
        'entitlement__profile__user__first_name',
        'entitlement__profile__user__last_name',
        'description',
    )
    readonly_fields = ('balance_after', 'created_at')
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('entitlement', 'transaction_type', 'hours', 'balance_after', 'description')
        }),
        ('Related Request', {
            'fields': ('related_request',),
            'classes': ('collapse',)
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_at'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def profile_name(self, obj):
        return obj.entitlement.profile.user.full_name
    profile_name.short_description = "Staff Member"
    
    def hours_with_sign(self, obj):
        color = 'green' if obj.hours > 0 else 'red'
        sign = '+' if obj.hours > 0 else ''
        return format_html(
            '<span style="color: {};">{}{} hrs</span>',
            color,
            sign,
            f'{obj.hours:.1f}'
        )
    hours_with_sign.short_description = "Hours"
    
    def balance_after_display(self, obj):
        return f"{obj.balance_after:.1f} hrs"
    balance_after_display.short_description = "Balance After"
    
    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = "Description"


@admin.register(SicknessAbsenceSummary)
class SicknessAbsenceSummaryAdmin(admin.ModelAdmin):
    list_display = (
        'profile',
        'year',
        'total_absence_days',
        'total_absence_instances',
        'bradford_factor_display',
        'trigger_status',
        'review_status',
    )
    list_filter = ('year', 'trigger_level_reached', 'formal_review_conducted', 'support_plan_in_place')
    search_fields = ('profile__user__sap', 'profile__user__first_name', 'profile__user__last_name')
    readonly_fields = ('bradford_factor_score', 'rolling_12m_bradford', 'last_updated', 'created_at')
    
    fieldsets = (
        ('Staff Member & Year', {
            'fields': ('profile', 'year')
        }),
        ('Annual Absence Metrics', {
            'fields': (
                'total_absence_days',
                'total_absence_instances',
                'bradford_factor_score',
            )
        }),
        ('Rolling 12-Month Metrics', {
            'fields': (
                'rolling_12m_days',
                'rolling_12m_instances',
                'rolling_12m_bradford',
            ),
            'classes': ('collapse',)
        }),
        ('Trigger & Review', {
            'fields': (
                'trigger_threshold',
                'trigger_level_reached',
                'formal_review_conducted',
                'review_date',
                'review_outcome',
                'support_plan_in_place',
            )
        }),
        ('Audit', {
            'fields': ('created_at', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['recalculate_metrics']
    
    def bradford_factor_display(self, obj):
        color = 'red' if obj.bradford_factor_score >= obj.trigger_threshold else 'orange' if obj.bradford_factor_score >= 100 else 'green'
        return format_html(
            '<strong style="color: {};">{}</strong>',
            color,
            obj.bradford_factor_score
        )
    bradford_factor_display.short_description = "Bradford Factor"
    
    def trigger_status(self, obj):
        if obj.trigger_level_reached:
            return format_html('<span style="color: red;">⚠️ TRIGGERED</span>')
        return format_html('<span style="color: green;">✓ OK</span>')
    trigger_status.short_description = "Trigger Status"
    
    def review_status(self, obj):
        if obj.formal_review_conducted:
            icon = '✓' if obj.support_plan_in_place else '○'
            return format_html('<span>{} Reviewed</span>', icon)
        return '-'
    review_status.short_description = "Review"
    
    def recalculate_metrics(self, request, queryset):
        """Action to recalculate metrics from sickness records"""
        count = 0
        for summary in queryset:
            summary.recalculate_from_records()
            count += 1
        self.message_user(request, f"Recalculated {count} sickness summaries")
    recalculate_metrics.short_description = "Recalculate metrics from sickness records"

