"""
Admin interface for overtime preference management
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models_overtime import (
    StaffOvertimePreference,
    OvertimeCoverageRequest,
    OvertimeCoverageResponse
)


@admin.register(StaffOvertimePreference)
class StaffOvertimePreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'staff_name',
        'staff_role',
        'home_unit',
        'overtime_status',
        'preferred_homes',
        'shift_preferences',
        'reliability_badge',
        'acceptance_rate_display',
        'total_shifts_worked',
        'last_contacted_display'
    ]
    
    list_filter = [
        'available_for_overtime',
        'staff__role',
        'staff__unit',
        'available_early_shifts',
        'available_late_shifts',
        'available_night_shifts',
        'available_weekdays',
        'available_weekends',
        'preferred_contact_method'
    ]
    
    search_fields = [
        'staff__name',
        'staff__employee_id',
        'phone_number'
    ]
    
    filter_horizontal = ['willing_to_work_at']
    
    fieldsets = (
        ('Staff Information', {
            'fields': ('staff',)
        }),
        ('Overtime Availability', {
            'fields': (
                'available_for_overtime',
                'willing_to_work_at',
            )
        }),
        ('Shift Type Preferences', {
            'fields': (
                'available_early_shifts',
                'available_late_shifts',
                'available_night_shifts',
            )
        }),
        ('Day Preferences', {
            'fields': (
                'available_weekdays',
                'available_weekends',
            )
        }),
        ('Contact Information', {
            'fields': (
                'preferred_contact_method',
                'phone_number',
            )
        }),
        ('Constraints', {
            'fields': (
                'max_hours_per_week',
                'min_notice_hours',
            )
        }),
        ('Performance Tracking', {
            'fields': (
                'total_requests_sent',
                'total_requests_accepted',
                'total_shifts_worked',
                'acceptance_rate',
                'last_contacted',
                'last_worked_overtime',
            ),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = [
        'acceptance_rate',
        'total_requests_sent',
        'total_requests_accepted',
        'total_shifts_worked',
        'last_contacted',
        'last_worked_overtime'
    ]
    
    def staff_name(self, obj):
        return obj.staff.name
    staff_name.short_description = 'Staff Name'
    staff_name.admin_order_field = 'staff__name'
    
    def staff_role(self, obj):
        return obj.staff.role
    staff_role.short_description = 'Role'
    staff_role.admin_order_field = 'staff__role'
    
    def home_unit(self, obj):
        return obj.staff.unit.name
    home_unit.short_description = 'Home Unit'
    home_unit.admin_order_field = 'staff__unit__name'
    
    def overtime_status(self, obj):
        if obj.available_for_overtime:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Available</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Unavailable</span>'
        )
    overtime_status.short_description = 'OT Status'
    
    def preferred_homes(self, obj):
        homes = obj.willing_to_work_at.all()
        if not homes:
            return format_html('<span style="color: red;">None selected</span>')
        
        home_names = [home.name for home in homes]
        if len(home_names) > 3:
            display = ', '.join(home_names[:3]) + f' +{len(home_names)-3} more'
        else:
            display = ', '.join(home_names)
        
        return format_html('<span style="font-size: 11px;">{}</span>', display)
    preferred_homes.short_description = 'Willing to Work At'
    
    def shift_preferences(self, obj):
        shifts = []
        if obj.available_early_shifts:
            shifts.append('E')
        if obj.available_late_shifts:
            shifts.append('L')
        if obj.available_night_shifts:
            shifts.append('N')
        
        if not shifts:
            return format_html('<span style="color: red;">None</span>')
        
        return format_html('<span style="font-weight: bold;">{}</span>', '/'.join(shifts))
    shift_preferences.short_description = 'Shifts (E/L/N)'
    
    def reliability_badge(self, obj):
        score = obj.get_reliability_score()
        
        if score >= 80:
            color = '#28a745'  # Green
            label = 'Excellent'
        elif score >= 60:
            color = '#17a2b8'  # Blue
            label = 'Good'
        elif score >= 40:
            color = '#ffc107'  # Yellow
            label = 'Fair'
        else:
            color = '#dc3545'  # Red
            label = 'Poor'
        
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">'
            '{} ({})</span>',
            color, label, f'{score:.0f}'
        )
    reliability_badge.short_description = 'Reliability'
    
    def acceptance_rate_display(self, obj):
        rate = float(obj.acceptance_rate)
        
        if rate >= 80:
            color = '#28a745'
        elif rate >= 60:
            color = '#17a2b8'
        elif rate >= 40:
            color = '#ffc107'
        else:
            color = '#dc3545'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, rate
        )
    acceptance_rate_display.short_description = 'Accept %'
    acceptance_rate_display.admin_order_field = 'acceptance_rate'
    
    def last_contacted_display(self, obj):
        if not obj.last_contacted:
            return format_html('<span style="color: #999;">Never</span>')
        
        from django.utils import timezone
        days_ago = (timezone.now() - obj.last_contacted).days
        
        if days_ago == 0:
            return format_html('<span style="color: #ffc107;">Today</span>')
        elif days_ago == 1:
            return 'Yesterday'
        elif days_ago <= 7:
            return format_html('<span style="color: green;">{} days ago</span>', days_ago)
        else:
            return f'{days_ago} days ago'
    last_contacted_display.short_description = 'Last Contact'
    last_contacted_display.admin_order_field = 'last_contacted'
    
    actions = ['mark_available_for_overtime', 'mark_unavailable_for_overtime']
    
    def mark_available_for_overtime(self, request, queryset):
        updated = queryset.update(available_for_overtime=True)
        self.message_user(request, f'{updated} staff marked as available for overtime')
    mark_available_for_overtime.short_description = "Mark selected as available for OT"
    
    def mark_unavailable_for_overtime(self, request, queryset):
        updated = queryset.update(available_for_overtime=False)
        self.message_user(request, f'{updated} staff marked as unavailable for overtime')
    mark_unavailable_for_overtime.short_description = "Mark selected as unavailable for OT"


@admin.register(OvertimeCoverageRequest)
class OvertimeCoverageRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'unit',
        'shift_date_display',
        'shift_type',
        'required_role',
        'status_badge',
        'contacted_count',
        'response_stats',
        'filled_by_display',
        'time_to_fill_display',
        'created_at_display'
    ]
    
    list_filter = [
        'status',
        'unit',
        'shift_type',
        'required_role',
        'shift_date',
        'created_at'
    ]
    
    search_fields = [
        'unit__name',
        'filled_by__name',
        'notes'
    ]
    
    readonly_fields = [
        'created_at',
        'filled_at',
        'total_contacted',
        'total_responses',
        'total_acceptances',
        'time_to_fill_minutes'
    ]
    
    fieldsets = (
        ('Shift Details', {
            'fields': (
                'unit',
                'shift_date',
                'shift_type',
                'required_role',
            )
        }),
        ('Status', {
            'fields': (
                'status',
                'filled_by',
                'filled_at',
            )
        }),
        ('Statistics', {
            'fields': (
                'total_contacted',
                'total_responses',
                'total_acceptances',
                'time_to_fill_minutes',
            )
        }),
        ('Notes', {
            'fields': ('notes',)
        })
    )
    
    def shift_date_display(self, obj):
        return obj.shift_date.strftime('%a, %b %d, %Y')
    shift_date_display.short_description = 'Date'
    shift_date_display.admin_order_field = 'shift_date'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#ffc107',
            'FILLED': '#28a745',
            'UNFILLED': '#dc3545',
            'CANCELLED': '#6c757d'
        }
        
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#999'), obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def contacted_count(self, obj):
        return f'{obj.total_contacted} staff'
    contacted_count.short_description = 'Contacted'
    contacted_count.admin_order_field = 'total_contacted'
    
    def response_stats(self, obj):
        if obj.total_contacted == 0:
            return '-'
        
        response_rate = (obj.total_responses / obj.total_contacted) * 100
        acceptance_rate = (obj.total_acceptances / obj.total_contacted) * 100 if obj.total_contacted > 0 else 0
        
        return format_html(
            '<span style="font-size: 11px;">'
            '{} responses ({}%)<br>{} accepted ({}%)'
            '</span>',
            obj.total_responses, f'{response_rate:.0f}',
            obj.total_acceptances, f'{acceptance_rate:.0f}'
        )
    response_stats.short_description = 'Responses'
    
    def filled_by_display(self, obj):
        if obj.filled_by:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>',
                obj.filled_by.name
            )
        return format_html('<span style="color: #999;">-</span>')
    filled_by_display.short_description = 'Filled By'
    
    def time_to_fill_display(self, obj):
        if not obj.time_to_fill_minutes:
            return '-'
        
        hours = obj.time_to_fill_minutes // 60
        minutes = obj.time_to_fill_minutes % 60
        
        if hours > 0:
            return f'{hours}h {minutes}m'
        return f'{minutes}m'
    time_to_fill_display.short_description = 'Time to Fill'
    time_to_fill_display.admin_order_field = 'time_to_fill_minutes'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%b %d, %I:%M %p')
    created_at_display.short_description = 'Created'
    created_at_display.admin_order_field = 'created_at'


@admin.register(OvertimeCoverageResponse)
class OvertimeCoverageResponseAdmin(admin.ModelAdmin):
    list_display = [
        'staff',
        'request_summary',
        'contacted_at_display',
        'contact_method',
        'response_badge',
        'responded_at_display',
        'decline_reason_display',
        'reliability_score_when_sent'
    ]
    
    list_filter = [
        'response',
        'contact_method',
        'decline_reason',
        'contacted_at',
        'request__unit',
        'request__shift_type'
    ]
    
    search_fields = [
        'staff__name',
        'request__unit__name'
    ]
    
    readonly_fields = [
        'contacted_at',
        'responded_at',
        'reliability_score_when_sent'
    ]
    
    def request_summary(self, obj):
        return format_html(
            '<span style="font-size: 11px;">{}<br>{} - {}</span>',
            obj.request.unit.name,
            obj.request.shift_date.strftime('%b %d'),
            obj.request.shift_type
        )
    request_summary.short_description = 'Request'
    
    def contacted_at_display(self, obj):
        return obj.contacted_at.strftime('%b %d, %I:%M %p')
    contacted_at_display.short_description = 'Contacted'
    contacted_at_display.admin_order_field = 'contacted_at'
    
    def response_badge(self, obj):
        colors = {
            'ACCEPTED': '#28a745',
            'DECLINED': '#dc3545',
            'NO_RESPONSE': '#6c757d'
        }
        
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.response, '#999'), obj.get_response_display()
        )
    response_badge.short_description = 'Response'
    response_badge.admin_order_field = 'response'
    
    def responded_at_display(self, obj):
        if not obj.responded_at:
            return format_html('<span style="color: #999;">-</span>')
        return obj.responded_at.strftime('%b %d, %I:%M %p')
    responded_at_display.short_description = 'Responded'
    responded_at_display.admin_order_field = 'responded_at'
    
    def decline_reason_display(self, obj):
        if obj.response != 'DECLINED' or not obj.decline_reason:
            return '-'
        return obj.get_decline_reason_display()
    decline_reason_display.short_description = 'Decline Reason'
