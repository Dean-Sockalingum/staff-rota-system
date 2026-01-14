from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import (
    RootCauseAnalysis,
    CorrectivePreventiveAction,
    DutyOfCandourRecord,
    IncidentTrendAnalysis
)


@admin.register(RootCauseAnalysis)
class RootCauseAnalysisAdmin(admin.ModelAdmin):
    list_display = ('incident', 'lead_investigator', 'status_badge', 'completion_badge', 'created_at')
    list_filter = ('status', 'created_at', 'investigation_start_date')
    search_fields = ('incident__description', 'lead_investigator__first_name', 'lead_investigator__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Incident Information', {
            'fields': ('incident', 'status', 'lead_investigator', 'investigation_team')
        }),
        ('Timeline', {
            'fields': ('investigation_start_date', 'investigation_end_date', 'review_due_date')
        }),
        ('5 Whys Analysis', {
            'fields': ('why_1', 'why_2', 'why_3', 'why_4', 'why_5', 'root_cause_identified'),
            'classes': ('collapse',)
        }),
        ('Fishbone Analysis', {
            'fields': ('fishbone_people', 'fishbone_environment', 'fishbone_processes', 
                      'fishbone_organizational', 'fishbone_external'),
            'classes': ('collapse',)
        }),
        ('Evidence & Approval', {
            'fields': ('evidence_collected', 'approved_by', 'approval_date'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ('investigation_team',)
    
    def status_badge(self, obj):
        colors = {
            'NOT_STARTED': '#6c757d',
            'IN_PROGRESS': '#0dcaf0',
            'UNDER_REVIEW': '#ffc107',
            'APPROVED': '#198754',
            'CLOSED': '#0d6efd'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def completion_badge(self, obj):
        is_complete = obj.is_complete()
        color = '#198754' if is_complete else '#dc3545'
        text = '✓ Complete' if is_complete else '✗ Incomplete'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, text
        )
    completion_badge.short_description = 'Completion'


@admin.register(CorrectivePreventiveAction)
class CorrectivePreventiveActionAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'title', 'priority_badge', 'status_badge', 'due_date_status', 'progress_bar')
    list_filter = ('action_type', 'priority', 'status', 'due_date')
    search_fields = ('reference_number', 'title', 'description', 'action_owner__first_name')
    readonly_fields = ('reference_number', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('reference_number', 'incident', 'root_cause_analysis', 'title', 'description')
        }),
        ('Action Details', {
            'fields': ('action_type', 'priority', 'status', 'action_owner', 'supporting_staff')
        }),
        ('Timeline', {
            'fields': ('due_date', 'completion_date', 'progress_percentage')
        }),
        ('Verification', {
            'fields': ('verification_method', 'verification_date', 'verified_by', 
                      'effectiveness_review', 'effectiveness_rating'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ('supporting_staff',)
    
    def priority_badge(self, obj):
        colors = {
            'IMMEDIATE': '#dc3545',
            'HIGH': '#fd7e14',
            'MEDIUM': '#ffc107',
            'LOW': '#0dcaf0'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.priority, '#6c757d'),
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def status_badge(self, obj):
        colors = {
            'IDENTIFIED': '#6c757d',
            'PLANNED': '#0dcaf0',
            'IN_PROGRESS': '#0d6efd',
            'IMPLEMENTED': '#198754',
            'UNDER_VERIFICATION': '#ffc107',
            'VERIFIED': '#20c997',
            'CLOSED': '#495057'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def due_date_status(self, obj):
        if obj.is_overdue():
            days = obj.days_until_due()
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">⚠ {} days overdue</span>',
                abs(days)
            )
        elif obj.days_until_due() <= 7:
            return format_html(
                '<span style="color: #fd7e14; font-weight: bold;">⚡ {} days remaining</span>',
                obj.days_until_due()
            )
        else:
            return format_html(
                '<span style="color: #198754;">{} days remaining</span>',
                obj.days_until_due()
            )
    due_date_status.short_description = 'Due Date'
    
    def progress_bar(self, obj):
        percent = obj.progress_percentage
        color = '#dc3545' if percent < 30 else '#ffc107' if percent < 70 else '#198754'
        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 3px; overflow: hidden;">'
            '<div style="width: {}%; background-color: {}; color: white; text-align: center; padding: 2px; font-size: 11px; font-weight: bold;">{:.0f}%</div>'
            '</div>',
            percent, color, percent
        )
    progress_bar.short_description = 'Progress'


@admin.register(DutyOfCandourRecord)
class DutyOfCandourRecordAdmin(admin.ModelAdmin):
    list_display = ('incident', 'harm_level_badge', 'status_badge', 'compliance_status', 'notification_window')
    list_filter = ('harm_level', 'status', 'incident_date', 'notification_date')
    search_fields = ('incident__description', 'family_contact_name', 'family_contact_phone')
    readonly_fields = ('created_at', 'updated_at', 'compliance_percentage')
    
    fieldsets = (
        ('Incident & Harm Assessment', {
            'fields': ('incident', 'incident_date', 'harm_level', 'harm_description')
        }),
        ('Family Contact', {
            'fields': ('family_contact_name', 'family_contact_relationship', 
                      'family_contact_phone', 'family_contact_email', 'communication_log')
        }),
        ('Duty of Candour Workflow', {
            'fields': ('status', 'assessment_completed', 'notification_date', 
                      'verbal_apology_date', 'written_apology_date', 'apology_letter')
        }),
        ('Investigation & Sharing', {
            'fields': ('investigation_findings_shared', 'findings_shared_date', 
                      'actions_discussed', 'family_feedback'),
            'classes': ('collapse',)
        }),
        ('Compliance', {
            'fields': ('compliance_percentage',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def harm_level_badge(self, obj):
        colors = {
            'DEATH': '#000000',
            'SEVERE': '#dc3545',
            'MODERATE': '#fd7e14',
            'LOW': '#ffc107',
            'NONE': '#198754'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.harm_level, '#6c757d'),
            obj.get_harm_level_display()
        )
    harm_level_badge.short_description = 'Harm Level'
    
    def status_badge(self, obj):
        colors = {
            'ASSESSMENT': '#6c757d',
            'NOTIFICATION_REQUIRED': '#dc3545',
            'NOTIFIED': '#0dcaf0',
            'VERBAL_APOLOGY': '#0d6efd',
            'WRITTEN_APOLOGY': '#198754',
            'FINDINGS_SHARED': '#20c997',
            'COMPLETE': '#495057'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def compliance_status(self, obj):
        percent = obj.get_compliance_status()
        color = '#dc3545' if percent < 50 else '#ffc107' if percent < 80 else '#198754'
        return format_html(
            '<div style="width: 120px;">'
            '<div style="background-color: #e9ecef; border-radius: 3px; overflow: hidden; margin-bottom: 2px;">'
            '<div style="width: {}%; background-color: {}; padding: 2px; text-align: center; color: white; font-size: 11px; font-weight: bold;">{:.0f}%</div>'
            '</div>'
            '<span style="font-size: 10px; color: #6c757d;">Compliance</span>'
            '</div>',
            percent, color, percent
        )
    compliance_status.short_description = 'Compliance'
    
    def notification_window(self, obj):
        if obj.is_within_notification_window():
            return format_html(
                '<span style="color: #198754; font-weight: bold;">✓ Within 24 hours</span>'
            )
        else:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">✗ Outside 24 hours</span>'
            )
    notification_window.short_description = '24hr Window'


@admin.register(IncidentTrendAnalysis)
class IncidentTrendAnalysisAdmin(admin.ModelAdmin):
    list_display = ('analysis_period_display', 'scope', 'trend_badge', 'total_incidents', 'analysis_date')
    list_filter = ('analysis_period', 'trend_direction', 'analysis_date')
    search_fields = ('care_home__name', 'recommendations')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Analysis Setup', {
            'fields': ('analysis_period', 'period_start', 'period_end', 'care_home')
        }),
        ('Incident Data', {
            'fields': ('total_incidents', 'incidents_by_type', 'incidents_by_severity')
        }),
        ('Trend Analysis', {
            'fields': ('trend_direction', 'trend_percentage', 'staffing_correlation', 'peak_times')
        }),
        ('Recommendations', {
            'fields': ('recommendations', 'actions_taken', 'analysis_date'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def analysis_period_display(self, obj):
        return f"{obj.get_analysis_period_display()} ({obj.period_start.strftime('%b %d')} - {obj.period_end.strftime('%b %d')})"
    analysis_period_display.short_description = 'Period'
    
    def trend_badge(self, obj):
        colors = {
            'INCREASING': '#dc3545',
            'STABLE': '#0dcaf0',
            'DECREASING': '#198754'
        }
        icons = {
            'INCREASING': '↗',
            'STABLE': '→',
            'DECREASING': '↘'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{} {}</span>',
            colors.get(obj.trend_direction, '#6c757d'),
            icons.get(obj.trend_direction, ''),
            obj.get_trend_direction_display()
        )
    trend_badge.short_description = 'Trend'
    
    def scope(self, obj):
        return obj.care_home.name if obj.care_home else 'Organization-wide'
    scope.short_description = 'Scope'
