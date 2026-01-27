"""
TQM Module 7: Performance Metrics & KPIs Admin Interface

Enhanced admin interface with visualizations, filters, and bulk operations for KPI management.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg, Max, Min
from django.urls import reverse
from django.utils import timezone
from .models import (
    KPIDefinition,
    KPIMeasurement,
    BalancedScorecardPerspective,
    ExecutiveDashboard,
    DashboardKPI,
    PerformanceTarget,
    BenchmarkData,
    KPIAlert,
    AlertThreshold
)


@admin.register(KPIDefinition)
class KPIDefinitionAdmin(admin.ModelAdmin):
    """Admin interface for KPI Definitions with enhanced filtering and display."""
    
    list_display = [
        'code',
        'name',
        'category_badge',
        'measurement_type',
        'trend_badge',
        'target_display',
        'reporting_frequency',
        'owner_display',
        'active_status',
        'dashboard_display'
    ]
    list_filter = [
        'category',
        'measurement_type',
        'trend_direction',
        'reporting_frequency',
        'is_active',
        'display_on_dashboard',
        'created_at'
    ]
    search_fields = ['code', 'name', 'description', 'responsible_owner__sap_number', 'responsible_owner__first_name', 'responsible_owner__last_name']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    filter_horizontal = []
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description', 'category')
        }),
        ('Measurement Configuration', {
            'fields': ('measurement_type', 'trend_direction', 'calculation_formula', 'data_source')
        }),
        ('Targets & Thresholds', {
            'fields': ('target_value', 'threshold_green', 'threshold_amber', 'threshold_red'),
            'description': 'Set performance thresholds for RAG (Red/Amber/Green) status'
        }),
        ('Reporting Settings', {
            'fields': ('reporting_frequency', 'responsible_owner')
        }),
        ('Dashboard Display', {
            'fields': ('is_active', 'display_on_dashboard', 'display_order')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        })
    )
    
    def category_badge(self, obj):
        """Display category with color-coded badge."""
        colors = {
            'FINANCIAL': '#28a745',
            'CUSTOMER': '#17a2b8',
            'INTERNAL': '#ffc107',
            'LEARNING': '#6f42c1',
            'QUALITY': '#dc3545',
            'COMPLIANCE': '#fd7e14',
            'WORKFORCE': '#20c997',
        }
        color = colors.get(obj.category, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_category_display()
        )
    category_badge.short_description = 'Category'
    
    def trend_badge(self, obj):
        """Display trend direction with icon."""
        icons = {
            'HIGHER_BETTER': '↑',
            'LOWER_BETTER': '↓',
            'TARGET_RANGE': '↔',
        }
        colors = {
            'HIGHER_BETTER': '#28a745',
            'LOWER_BETTER': '#dc3545',
            'TARGET_RANGE': '#ffc107',
        }
        icon = icons.get(obj.trend_direction, '?')
        color = colors.get(obj.trend_direction, '#6c757d')
        return format_html(
            '<span style="color: {}; font-size: 18px; font-weight: bold;" title="{}">{}</span>',
            color,
            obj.get_trend_direction_display(),
            icon
        )
    trend_badge.short_description = 'Trend'
    
    def target_display(self, obj):
        """Display target value with measurement type."""
        if obj.target_value:
            suffix = {
                'PERCENTAGE': '%',
                'CURRENCY': '',
                'HOURS': 'hrs',
                'DAYS': 'days',
                'COUNT': '',
                'RATIO': '',
                'SCORE': '',
            }.get(obj.measurement_type, '')
            
            if obj.measurement_type == 'CURRENCY':
                return format_html('<strong>£{:,.2f}</strong>', obj.target_value)
            else:
                return format_html('<strong>{}{}</strong>', obj.target_value, suffix)
        return format_html('<span style="color: #999;">No target</span>')
    target_display.short_description = 'Target'
    
    def owner_display(self, obj):
        """Display responsible owner."""
        if obj.responsible_owner:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:scheduling_user_change', args=[obj.responsible_owner.pk]),
                obj.responsible_owner.get_full_name()
            )
        return format_html('<span style="color: #999;">Unassigned</span>')
    owner_display.short_description = 'Owner'
    
    def active_status(self, obj):
        """Display active status with color indicator."""
        if obj.is_active:
            return format_html('<span style="color: #28a745;">● Active</span>')
        return format_html('<span style="color: #dc3545;">○ Inactive</span>')
    active_status.short_description = 'Status'
    
    def dashboard_display(self, obj):
        """Display dashboard visibility."""
        if obj.display_on_dashboard:
            return format_html('<span style="color: #28a745;">✓ Visible</span>')
        return format_html('<span style="color: #999;">✗ Hidden</span>')
    dashboard_display.short_description = 'On Dashboard'
    
    def save_model(self, request, obj, form, change):
        """Set created_by on new KPI definitions."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(KPIMeasurement)
class KPIMeasurementAdmin(admin.ModelAdmin):
    """Admin interface for KPI Measurements with RAG status visualization."""
    
    list_display = [
        'kpi_code',
        'measurement_date',
        'care_home_display',
        'actual_value_display',
        'target_value_display',
        'variance_display',
        'rag_badge',
        'verified_status',
        'recorded_by_display'
    ]
    list_filter = [
        'rag_status',
        'verified',
        'kpi__category',
        'care_home',
        'measurement_date',
        'recorded_at'
    ]
    search_fields = [
        'kpi__code',
        'kpi__name',
        'care_home__name',
        'notes'
    ]
    readonly_fields = ['variance', 'variance_percentage', 'rag_status', 'recorded_at', 'recorded_by']
    date_hierarchy = 'measurement_date'
    
    fieldsets = (
        ('KPI Information', {
            'fields': ('kpi', 'care_home')
        }),
        ('Measurement Period', {
            'fields': ('measurement_date', 'period_start', 'period_end')
        }),
        ('Values', {
            'fields': ('actual_value', 'target_value', 'numerator', 'denominator')
        }),
        ('Performance Analysis', {
            'fields': ('variance', 'variance_percentage', 'rag_status'),
            'description': 'Automatically calculated based on KPI thresholds'
        }),
        ('Notes & Commentary', {
            'fields': ('notes',)
        }),
        ('Verification', {
            'fields': ('verified', 'verified_by', 'verified_at')
        }),
        ('Metadata', {
            'fields': ('recorded_at', 'recorded_by'),
            'classes': ('collapse',)
        })
    )
    
    def kpi_code(self, obj):
        """Display KPI code as link."""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:performance_kpis_kpidefinition_change', args=[obj.kpi.pk]),
            obj.kpi.code
        )
    kpi_code.short_description = 'KPI'
    kpi_code.admin_order_field = 'kpi__code'
    
    def care_home_display(self, obj):
        """Display care home or Organization-wide."""
        if obj.care_home:
            return obj.care_home.name
        return format_html('<em>Organization-wide</em>')
    care_home_display.short_description = 'Care Home'
    care_home_display.admin_order_field = 'care_home__name'
    
    def actual_value_display(self, obj):
        """Display actual value with formatting."""
        suffix = self._get_value_suffix(obj.kpi.measurement_type)
        if obj.kpi.measurement_type == 'CURRENCY':
            return format_html('<strong>£{:,.2f}</strong>', obj.actual_value)
        return format_html('<strong>{}{}</strong>', obj.actual_value, suffix)
    actual_value_display.short_description = 'Actual'
    
    def target_value_display(self, obj):
        """Display target value."""
        target = obj.target_value or obj.kpi.target_value
        if target:
            suffix = self._get_value_suffix(obj.kpi.measurement_type)
            if obj.kpi.measurement_type == 'CURRENCY':
                return format_html('£{:,.2f}', target)
            return format_html('{}{}', target, suffix)
        return format_html('<span style="color: #999;">—</span>')
    target_value_display.short_description = 'Target'
    
    def variance_display(self, obj):
        """Display variance with color coding."""
        if obj.variance is not None:
            color = '#28a745' if obj.variance >= 0 else '#dc3545'
            prefix = '+' if obj.variance >= 0 else ''
            
            if obj.variance_percentage:
                return format_html(
                    '<span style="color: {};">{}{} ({:.1f}%)</span>',
                    color,
                    prefix,
                    obj.variance,
                    obj.variance_percentage
                )
            return format_html('<span style="color: {};">{}{}</span>', color, prefix, obj.variance)
        return format_html('<span style="color: #999;">—</span>')
    variance_display.short_description = 'Variance'
    
    def rag_badge(self, obj):
        """Display RAG status with color-coded badge."""
        colors = {
            'GREEN': '#28a745',
            'AMBER': '#ffc107',
            'RED': '#dc3545',
            'UNKNOWN': '#6c757d',
        }
        labels = {
            'GREEN': '● Green',
            'AMBER': '● Amber',
            'RED': '● Red',
            'UNKNOWN': '? Unknown',
        }
        color = colors.get(obj.rag_status, '#6c757d')
        label = labels.get(obj.rag_status, obj.rag_status)
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            label
        )
    rag_badge.short_description = 'RAG Status'
    rag_badge.admin_order_field = 'rag_status'
    
    def verified_status(self, obj):
        """Display verification status."""
        if obj.verified:
            return format_html(
                '<span style="color: #28a745;" title="Verified by {} on {}">✓ Verified</span>',
                obj.verified_by.get_full_name() if obj.verified_by else 'Unknown',
                obj.verified_at.strftime('%Y-%m-%d %H:%M') if obj.verified_at else 'Unknown'
            )
        return format_html('<span style="color: #6c757d;">○ Unverified</span>')
    verified_status.short_description = 'Verified'
    verified_status.admin_order_field = 'verified'
    
    def recorded_by_display(self, obj):
        """Display who recorded this measurement."""
        if obj.recorded_by:
            return obj.recorded_by.get_full_name()
        return format_html('<span style="color: #999;">Unknown</span>')
    recorded_by_display.short_description = 'Recorded By'
    
    def _get_value_suffix(self, measurement_type):
        """Get suffix for measurement type."""
        return {
            'PERCENTAGE': '%',
            'HOURS': ' hrs',
            'DAYS': ' days',
            'COUNT': '',
            'CURRENCY': '',
            'RATIO': '',
            'SCORE': '',
        }.get(measurement_type, '')
    
    def save_model(self, request, obj, form, change):
        """Set recorded_by and handle verification."""
        if not change:
            obj.recorded_by = request.user
        
        if obj.verified and not obj.verified_by:
            obj.verified_by = request.user
            obj.verified_at = timezone.now()
        
        super().save_model(request, obj, form, change)


@admin.register(BalancedScorecardPerspective)
class BalancedScorecardPerspectiveAdmin(admin.ModelAdmin):
    """Admin interface for Balanced Scorecard Perspectives."""
    
    list_display = ['name', 'color_preview', 'icon_display', 'display_order', 'active_status', 'kpi_count']
    list_editable = ['display_order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description', 'strategic_objective']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'strategic_objective')
        }),
        ('Display Settings', {
            'fields': ('display_order', 'icon_class', 'color_code')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def color_preview(self, obj):
        """Show color preview swatch."""
        return format_html(
            '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
            obj.color_code
        )
    color_preview.short_description = 'Color'
    
    def icon_display(self, obj):
        """Display icon if specified."""
        if obj.icon_class:
            return format_html('<i class="{}"></i> {}', obj.icon_class, obj.icon_class)
        return format_html('<span style="color: #999;">No icon</span>')
    icon_display.short_description = 'Icon'
    
    def active_status(self, obj):
        """Display active status."""
        if obj.is_active:
            return format_html('<span style="color: #28a745;">● Active</span>')
        return format_html('<span style="color: #dc3545;">○ Inactive</span>')
    active_status.short_description = 'Status'
    
    def kpi_count(self, obj):
        """Count of KPIs in this perspective."""
        # This would need to be implemented based on linking KPIs to perspectives
        return format_html('<span style="color: #999;">—</span>')
    kpi_count.short_description = '# KPIs'


@admin.register(ExecutiveDashboard)
class ExecutiveDashboardAdmin(admin.ModelAdmin):
    """Admin interface for Executive Dashboards."""
    
    list_display = ['name', 'owner_display', 'layout', 'kpi_count', 'visibility_badge', 'last_viewed_display', 'created_at']
    list_filter = ['layout', 'is_public', 'created_at', 'last_viewed']
    search_fields = ['name', 'description', 'owner__sap_number', 'owner__first_name', 'owner__last_name']
    readonly_fields = ['created_at', 'updated_at', 'last_viewed']
    filter_horizontal = ['care_homes', 'shared_with']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'owner')
        }),
        ('Display Configuration', {
            'fields': ('layout', 'refresh_interval')
        }),
        ('Filters', {
            'fields': ('care_homes',),
            'description': 'Select specific care homes to filter dashboard data (leave empty for organization-wide)'
        }),
        ('Sharing & Access', {
            'fields': ('is_public', 'shared_with')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'last_viewed'),
            'classes': ('collapse',)
        })
    )
    
    def owner_display(self, obj):
        """Display dashboard owner."""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:scheduling_user_change', args=[obj.owner.pk]),
            obj.owner.get_full_name()
        )
    owner_display.short_description = 'Owner'
    owner_display.admin_order_field = 'owner__last_name'
    
    def kpi_count(self, obj):
        """Count of KPIs on this dashboard."""
        count = obj.kpis.count()
        return format_html('<strong>{}</strong> KPIs', count)
    kpi_count.short_description = 'KPIs'
    
    def visibility_badge(self, obj):
        """Display visibility status."""
        if obj.is_public:
            return format_html('<span style="color: #17a2b8;">🌐 Public</span>')
        elif obj.shared_with.exists():
            count = obj.shared_with.count()
            return format_html('<span style="color: #ffc107;">👥 Shared ({})</span>', count)
        return format_html('<span style="color: #6c757d;">🔒 Private</span>')
    visibility_badge.short_description = 'Visibility'
    
    def last_viewed_display(self, obj):
        """Display last viewed timestamp."""
        if obj.last_viewed:
            return obj.last_viewed.strftime('%Y-%m-%d %H:%M')
        return format_html('<span style="color: #999;">Never</span>')
    last_viewed_display.short_description = 'Last Viewed'
    last_viewed_display.admin_order_field = 'last_viewed'


@admin.register(DashboardKPI)
class DashboardKPIAdmin(admin.ModelAdmin):
    """Admin interface for Dashboard KPI configuration."""
    
    list_display = ['dashboard_name', 'kpi_code', 'display_order', 'chart_type', 'time_range_display', 'show_trend', 'show_target']
    list_editable = ['display_order', 'chart_type']
    list_filter = ['chart_type', 'show_trend', 'show_target', 'dashboard__layout']
    search_fields = ['dashboard__name', 'kpi__code', 'kpi__name']
    
    fieldsets = (
        ('Dashboard & KPI', {
            'fields': ('dashboard', 'kpi', 'display_order')
        }),
        ('Chart Configuration', {
            'fields': ('chart_type', 'time_range_days', 'show_trend', 'show_target')
        })
    )
    
    def dashboard_name(self, obj):
        """Display dashboard name."""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:performance_kpis_executivedashboard_change', args=[obj.dashboard.pk]),
            obj.dashboard.name
        )
    dashboard_name.short_description = 'Dashboard'
    dashboard_name.admin_order_field = 'dashboard__name'
    
    def kpi_code(self, obj):
        """Display KPI code."""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:performance_kpis_kpidefinition_change', args=[obj.kpi.pk]),
            obj.kpi.code
        )
    kpi_code.short_description = 'KPI'
    kpi_code.admin_order_field = 'kpi__code'
    
    def time_range_display(self, obj):
        """Display time range in days."""
        return format_html('{} days', obj.time_range_days)
    time_range_display.short_description = 'Time Range'


@admin.register(PerformanceTarget)
class PerformanceTargetAdmin(admin.ModelAdmin):
    """Admin interface for Performance Targets."""
    
    list_display = [
        'kpi_code',
        'care_home_display',
        'period_display',
        'target_value_display',
        'status_badge',
        'approved_status',
        'is_current_period'
    ]
    list_filter = ['status', 'target_period', 'period_start', 'approved_at', 'care_home']
    search_fields = ['kpi__code', 'kpi__name', 'strategic_objective', 'action_plan']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    date_hierarchy = 'period_start'
    
    fieldsets = (
        ('KPI & Location', {
            'fields': ('kpi', 'care_home')
        }),
        ('Target Period', {
            'fields': ('target_period', 'period_start', 'period_end')
        }),
        ('Target Values', {
            'fields': ('target_value', 'stretch_target', 'minimum_acceptable')
        }),
        ('Strategic Alignment', {
            'fields': ('strategic_objective', 'action_plan')
        }),
        ('Status & Approval', {
            'fields': ('status', 'approved_by', 'approved_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        })
    )
    
    def kpi_code(self, obj):
        """Display KPI code."""
        return obj.kpi.code
    kpi_code.short_description = 'KPI'
    kpi_code.admin_order_field = 'kpi__code'
    
    def care_home_display(self, obj):
        """Display care home or organization-wide."""
        if obj.care_home:
            return obj.care_home.name
        return format_html('<em>Organization-wide</em>')
    care_home_display.short_description = 'Care Home'
    
    def period_display(self, obj):
        """Display target period."""
        return format_html(
            '{} to {}',
            obj.period_start.strftime('%Y-%m-%d'),
            obj.period_end.strftime('%Y-%m-%d')
        )
    period_display.short_description = 'Period'
    
    def target_value_display(self, obj):
        """Display target value with min/max range."""
        if obj.minimum_acceptable and obj.stretch_target:
            return format_html(
                '{} <span style="color: #999;">(Min: {} / Stretch: {})</span>',
                obj.target_value,
                obj.minimum_acceptable,
                obj.stretch_target
            )
        return format_html('<strong>{}</strong>', obj.target_value)
    target_value_display.short_description = 'Target'
    
    def status_badge(self, obj):
        """Display status with color coding."""
        colors = {
            'DRAFT': '#6c757d',
            'APPROVED': '#17a2b8',
            'ACTIVE': '#28a745',
            'ACHIEVED': '#20c997',
            'NOT_ACHIEVED': '#dc3545',
            'CANCELLED': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def approved_status(self, obj):
        """Display approval status."""
        if obj.approved_by and obj.approved_at:
            return format_html(
                '<span style="color: #28a745;" title="Approved by {} on {}">✓ Approved</span>',
                obj.approved_by.get_full_name(),
                obj.approved_at.strftime('%Y-%m-%d')
            )
        return format_html('<span style="color: #999;">Pending</span>')
    approved_status.short_description = 'Approval'
    
    def is_current_period(self, obj):
        """Indicate if this is currently active."""
        if obj.is_current():
            return format_html('<span style="color: #28a745;">● Current</span>')
        return format_html('<span style="color: #999;">○ Past/Future</span>')
    is_current_period.short_description = 'Current'
    
    def save_model(self, request, obj, form, change):
        """Set created_by and handle approval."""
        if not change:
            obj.created_by = request.user
        
        if obj.status == 'APPROVED' and not obj.approved_by:
            obj.approved_by = request.user
            obj.approved_at = timezone.now()
        
        super().save_model(request, obj, form, change)


@admin.register(BenchmarkData)
class BenchmarkDataAdmin(admin.ModelAdmin):
    """Admin interface for Benchmark Data."""
    
    list_display = [
        'kpi_code',
        'source_name',
        'benchmark_type_badge',
        'benchmark_value_display',
        'period_display',
        'sample_size_display',
        'created_at'
    ]
    list_filter = ['benchmark_type', 'period_start', 'created_at', 'kpi__category']
    search_fields = ['kpi__code', 'kpi__name', 'source_name', 'source_description']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    date_hierarchy = 'period_start'
    
    fieldsets = (
        ('KPI & Source', {
            'fields': ('kpi', 'source_name', 'source_description', 'benchmark_type')
        }),
        ('Benchmark Period', {
            'fields': ('period_start', 'period_end')
        }),
        ('Benchmark Value', {
            'fields': ('benchmark_value', 'sample_size')
        }),
        ('Methodology & Notes', {
            'fields': ('methodology', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        })
    )
    
    def kpi_code(self, obj):
        """Display KPI code."""
        return obj.kpi.code
    kpi_code.short_description = 'KPI'
    kpi_code.admin_order_field = 'kpi__code'
    
    def benchmark_type_badge(self, obj):
        """Display benchmark type with badge."""
        colors = {
            'NATIONAL': '#007bff',
            'REGIONAL': '#6f42c1',
            'SECTOR': '#fd7e14',
            'TOP_QUARTILE': '#20c997',
            'BEST_IN_CLASS': '#28a745',
            'REGULATORY': '#dc3545',
        }
        color = colors.get(obj.benchmark_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_benchmark_type_display()
        )
    benchmark_type_badge.short_description = 'Type'
    
    def benchmark_value_display(self, obj):
        """Display benchmark value."""
        return format_html('<strong>{}</strong>', obj.benchmark_value)
    benchmark_value_display.short_description = 'Benchmark Value'
    
    def period_display(self, obj):
        """Display period."""
        return format_html(
            '{} to {}',
            obj.period_start.strftime('%Y-%m-%d'),
            obj.period_end.strftime('%Y-%m-%d')
        )
    period_display.short_description = 'Period'
    
    def sample_size_display(self, obj):
        """Display sample size."""
        if obj.sample_size:
            return format_html('n={}', obj.sample_size)
        return format_html('<span style="color: #999;">—</span>')
    sample_size_display.short_description = 'Sample'
    
    def save_model(self, request, obj, form, change):
        """Set created_by."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ============================================================================
# KPI ALERT SYSTEM ADMIN
# ============================================================================

@admin.register(KPIAlert)
class KPIAlertAdmin(admin.ModelAdmin):
    """Admin interface for KPI Alerts."""
    
    list_display = [
        'severity_badge',
        'title',
        'module_display',
        'metric_name',
        'value_display',
        'status_badge',
        'assigned_to',
        'age_display',
        'created_at'
    ]
    list_filter = [
        'severity',
        'status',
        'module',
        'created_at'
    ]
    search_fields = ['title', 'description', 'metric_name']
    readonly_fields = ['created_at', 'acknowledged_at', 'acknowledged_by', 'resolved_at', 'resolved_by']
    
    fieldsets = (
        ('Alert Details', {
            'fields': ('title', 'description', 'module', 'metric_name')
        }),
        ('Threshold Breach', {
            'fields': ('current_value', 'threshold_value', 'severity')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'assigned_to')
        }),
        ('Resolution', {
            'fields': ('resolution_notes', 'resolved_at', 'resolved_by'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'acknowledged_at', 'acknowledged_by'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['acknowledge_alerts', 'resolve_alerts', 'dismiss_alerts']
    
    def severity_badge(self, obj):
        """Display severity as colored badge."""
        colors = {
            'INFO': '#17a2b8',
            'WARNING': '#ffc107',
            'CRITICAL': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 10px; font-weight: bold;">{}</span>',
            colors.get(obj.severity, '#6c757d'),
            obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'ACTIVE': '#dc3545',
            'ACKNOWLEDGED': '#ffc107',
            'RESOLVED': '#28a745',
            'DISMISSED': '#6c757d'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 10px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def module_display(self, obj):
        """Display module."""
        return obj.get_module_display().replace('Module ', 'M')
    module_display.short_description = 'Module'
    
    def value_display(self, obj):
        """Display current vs threshold."""
        return format_html(
            '{} <span style="color: #999;">(threshold: {})</span>',
            obj.current_value,
            obj.threshold_value
        )
    value_display.short_description = 'Value'
    
    def age_display(self, obj):
        """Display alert age."""
        hours = obj.get_age_in_hours()
        if hours < 1:
            return format_html('<span style="color: #28a745;">{}m</span>', int(hours * 60))
        elif hours < 24:
            return format_html('<span style="color: #ffc107;">{}h</span>', int(hours))
        else:
            days = int(hours / 24)
            color = '#dc3545' if days > 3 else '#ffc107'
            return format_html('<span style="color: {};">{}d</span>', color, days)
    age_display.short_description = 'Age'
    
    def acknowledge_alerts(self, request, queryset):
        """Bulk acknowledge alerts."""
        count = 0
        for alert in queryset.filter(status='ACTIVE'):
            alert.acknowledge(request.user)
            count += 1
        self.message_user(request, f'{count} alert(s) acknowledged.')
    acknowledge_alerts.short_description = 'Acknowledge selected alerts'
    
    def resolve_alerts(self, request, queryset):
        """Bulk resolve alerts."""
        count = 0
        for alert in queryset.filter(status__in=['ACTIVE', 'ACKNOWLEDGED']):
            alert.resolve(request.user, 'Bulk resolved from admin')
            count += 1
        self.message_user(request, f'{count} alert(s) resolved.')
    resolve_alerts.short_description = 'Resolve selected alerts'
    
    def dismiss_alerts(self, request, queryset):
        """Bulk dismiss alerts."""
        count = queryset.update(status='DISMISSED')
        self.message_user(request, f'{count} alert(s) dismissed.')
    dismiss_alerts.short_description = 'Dismiss selected alerts'


@admin.register(AlertThreshold)
class AlertThresholdAdmin(admin.ModelAdmin):
    """Admin interface for Alert Thresholds."""
    
    list_display = [
        'display_name',
        'module_display',
        'threshold_display',
        'operator_display',
        'active_status',
        'email_notifications'
    ]
    list_filter = [
        'module',
        'is_active',
        'send_email_notifications',
        'comparison_operator'
    ]
    search_fields = ['metric_name', 'display_name', 'description']
    filter_horizontal = ['notification_recipients']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Threshold Configuration', {
            'fields': ('metric_name', 'display_name', 'module', 'description')
        }),
        ('Threshold Values', {
            'fields': ('warning_threshold', 'critical_threshold', 'comparison_operator')
        }),
        ('Notifications', {
            'fields': ('send_email_notifications', 'notification_recipients')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def module_display(self, obj):
        """Display module."""
        return obj.get_module_display()
    module_display.short_description = 'Module'
    
    def threshold_display(self, obj):
        """Display thresholds."""
        return format_html(
            'Warning: {} | Critical: {}',
            obj.warning_threshold,
            obj.critical_threshold
        )
    threshold_display.short_description = 'Thresholds'
    
    def operator_display(self, obj):
        """Display comparison operator."""
        return obj.get_comparison_operator_display()
    operator_display.short_description = 'Operator'
    
    def active_status(self, obj):
        """Display active status."""
        if obj.is_active:
            return format_html('<span style="color: #28a745;">●</span> Active')
        return format_html('<span style="color: #6c757d;">○</span> Inactive')
    active_status.short_description = 'Status'
    
    def email_notifications(self, obj):
        """Display email notification status."""
        if obj.send_email_notifications:
            count = obj.notification_recipients.count()
            return format_html('<span style="color: #28a745;">✓</span> {} recipient(s)', count)
        return format_html('<span style="color: #999;">—</span>')
    email_notifications.short_description = 'Email'
