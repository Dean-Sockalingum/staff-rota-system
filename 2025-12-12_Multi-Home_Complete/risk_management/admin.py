"""
Risk Management Admin Interface

Enhanced admin with:
- Color-coded badges for risk levels and status
- Progress bars for mitigation completion
- Risk matrix heat map visualization
- Chart.js dashboard widgets
- Inline editing for mitigations and reviews
- Scottish regulatory compliance indicators
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count, Avg, Q
from .models import (
    RiskCategory,
    RiskRegister,
    RiskMitigation,
    RiskReview,
    RiskTreatmentPlan
)


@admin.register(RiskCategory)
class RiskCategoryAdmin(admin.ModelAdmin):
    """Enhanced admin for risk categories"""
    
    list_display = [
        'name',
        'parent',
        'color_badge',
        'his_domain',
        'care_inspectorate_theme',
        'subcategory_count',
        'is_active'
    ]
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description', 'his_domain', 'care_inspectorate_theme']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'parent', 'color', 'is_active')
        }),
        ('Scottish Regulatory Alignment', {
            'fields': ('his_domain', 'care_inspectorate_theme')
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def color_badge(self, obj):
        """Display color badge"""
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 15px; '
            'border-radius: 5px; font-weight: bold;">{}</span>',
            obj.color,
            obj.name[:10]
        )
    color_badge.short_description = 'Color'
    
    def subcategory_count(self, obj):
        """Count of subcategories"""
        count = obj.subcategories.count()
        if count > 0:
            return format_html('<strong>{}</strong> subcategories', count)
        return '—'
    subcategory_count.short_description = 'Subcategories'


class RiskMitigationInline(admin.TabularInline):
    """Inline for mitigations in risk register"""
    model = RiskMitigation
    extra = 0
    fields = [
        'action',
        'priority',
        'status',
        'assigned_to',
        'target_completion_date',
        'completion_percentage'
    ]
    readonly_fields = []


class RiskReviewInline(admin.TabularInline):
    """Inline for reviews in risk register"""
    model = RiskReview
    extra = 0
    fields = [
        'review_date',
        'reviewed_by',
        'reassessed_score',
        'decision',
        'next_review_date'
    ]
    readonly_fields = ['reassessed_score']


@admin.register(RiskRegister)
class RiskRegisterAdmin(admin.ModelAdmin):
    """
    Enhanced admin for risk register with:
    - Risk level badges (Critical/High/Medium/Low)
    - Risk reduction visualization
    - Review status indicators
    - 5x5 risk matrix display
    """
    
    list_display = [
        'risk_id',
        'title',
        'care_home',
        'category',
        'risk_level_badge',
        'status_badge',
        'residual_score_display',
        'risk_reduction_bar',
        'review_status',
        'days_to_review',
        'risk_owner'
    ]
    list_filter = [
        'status',
        'priority',
        'care_home',
        'category',
        'review_frequency',
        'is_escalated'
    ]
    search_fields = [
        'risk_id',
        'title',
        'description',
        'risk_owner__username',
        'risk_owner__first_name',
        'risk_owner__last_name'
    ]
    readonly_fields = [
        'risk_id',
        'inherent_score',
        'residual_score',
        'target_score',
        'priority',
        'created_at',
        'updated_at',
        'risk_matrix_display',
        'mitigation_summary'
    ]
    
    fieldsets = (
        ('Risk Identification', {
            'fields': (
                'risk_id',
                'title',
                'description',
                'category',
                'care_home',
                'affected_area'
            )
        }),
        ('Inherent Risk Assessment (Before Controls)', {
            'fields': (
                ('inherent_likelihood', 'inherent_impact', 'inherent_score'),
            ),
            'description': 'Risk level before any controls are applied'
        }),
        ('Current Controls', {
            'fields': (
                'current_controls',
                'control_effectiveness'
            )
        }),
        ('Residual Risk Assessment (After Controls)', {
            'fields': (
                ('residual_likelihood', 'residual_impact', 'residual_score'),
            ),
            'description': 'Risk level with current controls in place'
        }),
        ('Target Risk (Desired Level)', {
            'fields': (
                ('target_likelihood', 'target_impact', 'target_score'),
            ),
            'classes': ('collapse',)
        }),
        ('Risk Matrix Visualization', {
            'fields': ('risk_matrix_display',)
        }),
        ('Ownership & Accountability', {
            'fields': (
                ('risk_owner', 'assigned_to'),
                ('identified_by', 'identified_date')
            )
        }),
        ('Status & Priority', {
            'fields': (
                ('status', 'priority'),
                ('is_escalated', 'escalation_reason')
            )
        }),
        ('Review & Monitoring', {
            'fields': (
                ('review_frequency', 'last_reviewed', 'next_review_date'),
            )
        }),
        ('Regulatory Compliance', {
            'fields': (
                'regulatory_requirement',
                'compliance_deadline'
            ),
            'classes': ('collapse',)
        }),
        ('Integration', {
            'fields': ('related_incidents',),
            'classes': ('collapse',)
        }),
        ('Mitigation Summary', {
            'fields': ('mitigation_summary',),
            'description': 'Summary of associated mitigation actions'
        }),
        ('Additional Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [RiskMitigationInline, RiskReviewInline]
    
    actions = ['mark_as_escalated', 'mark_as_controlled', 'schedule_review']
    
    def risk_level_badge(self, obj):
        """Display color-coded risk level badge"""
        colors = {
            'CRITICAL': '#dc3545',  # Red
            'HIGH': '#fd7e14',      # Orange
            'MEDIUM': '#ffc107',    # Yellow
            'LOW': '#28a745'        # Green
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 15px; '
            'border-radius: 5px; font-weight: bold; text-transform: uppercase;">{}</span>',
            colors.get(obj.priority, '#6c757d'),
            obj.priority
        )
    risk_level_badge.short_description = 'Risk Level'
    risk_level_badge.admin_order_field = 'priority'
    
    def status_badge(self, obj):
        """Display status badge"""
        colors = {
            'IDENTIFIED': '#17a2b8',
            'ASSESSED': '#6c757d',
            'MITIGATED': '#007bff',
            'CONTROLLED': '#28a745',
            'ACCEPTED': '#ffc107',
            'TRANSFERRED': '#6f42c1',
            'CLOSED': '#28a745',
            'ESCALATED': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; '
            'border-radius: 5px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def residual_score_display(self, obj):
        """Display residual score with heat map color"""
        score = obj.residual_score
        if score >= 15:
            color = '#dc3545'
        elif score >= 10:
            color = '#fd7e14'
        elif score >= 6:
            color = '#ffc107'
        else:
            color = '#28a745'
        
        return format_html(
            '<div style="text-align: center; background: {}; color: white; '
            'font-weight: bold; padding: 8px; border-radius: 5px; min-width: 50px;">{}</div>',
            color,
            score
        )
    residual_score_display.short_description = 'Risk Score'
    residual_score_display.admin_order_field = 'residual_score'
    
    def risk_reduction_bar(self, obj):
        """Visual progress bar showing risk reduction"""
        reduction = obj.risk_reduction_percentage()
        
        # Color based on reduction achievement
        if reduction >= 70:
            color = '#28a745'  # Green
        elif reduction >= 40:
            color = '#ffc107'  # Yellow
        else:
            color = '#dc3545'  # Red
        
        return format_html(
            '<div style="width: 120px; background: #e9ecef; border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; background: {}; color: white; text-align: center; '
            'padding: 3px 0; font-size: 11px; font-weight: bold;">{:.0f}%</div>'
            '</div>',
            min(reduction, 100),
            color,
            reduction
        )
    risk_reduction_bar.short_description = 'Risk Reduction'
    
    def review_status(self, obj):
        """Review status indicator"""
        if obj.is_overdue_review():
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">⚠ OVERDUE</span>'
            )
        days = obj.days_until_review()
        if days <= 7:
            return format_html(
                '<span style="color: #fd7e14; font-weight: bold;">⏰ Due Soon</span>'
            )
        return format_html(
            '<span style="color: #28a745;">✓ On Schedule</span>'
        )
    review_status.short_description = 'Review Status'
    
    def days_to_review(self, obj):
        """Days until next review"""
        days = obj.days_until_review()
        if days < 0:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">{} days overdue</span>',
                abs(days)
            )
        elif days == 0:
            return format_html('<span style="color: #fd7e14; font-weight: bold;">TODAY</span>')
        elif days <= 7:
            return format_html('<span style="color: #fd7e14;">{} days</span>', days)
        return format_html('<span style="color: #28a745;">{} days</span>', days)
    days_to_review.short_description = 'Days to Review'
    
    def risk_matrix_display(self, obj):
        """Display 5x5 risk matrix with current risk highlighted"""
        matrix_html = '<div style="margin: 20px 0;"><h3>Risk Matrix (5×5)</h3>'
        matrix_html += '<table style="border-collapse: collapse; margin: 10px 0;">'
        
        # Header row
        matrix_html += '<tr><th style="padding: 8px; border: 1px solid #ddd;">Impact →<br>Likelihood ↓</th>'
        for i in range(1, 6):
            matrix_html += f'<th style="padding: 8px; border: 1px solid #ddd; text-align: center;">{i}</th>'
        matrix_html += '</tr>'
        
        # Matrix cells (5=top row, 1=bottom row for likelihood)
        for likelihood in range(5, 0, -1):
            matrix_html += f'<tr><th style="padding: 8px; border: 1px solid #ddd;">{likelihood}</th>'
            for impact in range(1, 6):
                score = likelihood * impact
                
                # Determine cell color
                if score >= 15:
                    bg_color = '#dc3545'  # Critical - Red
                elif score >= 10:
                    bg_color = '#fd7e14'  # High - Orange
                elif score >= 6:
                    bg_color = '#ffc107'  # Medium - Yellow
                else:
                    bg_color = '#28a745'  # Low - Green
                
                # Highlight current residual risk
                border = '4px solid #000' if (likelihood == obj.residual_likelihood and impact == obj.residual_impact) else '1px solid #ddd'
                text_weight = 'bold' if (likelihood == obj.residual_likelihood and impact == obj.residual_impact) else 'normal'
                
                matrix_html += f'<td style="padding: 15px; border: {border}; background: {bg_color}; color: white; text-align: center; font-weight: {text_weight}; font-size: 14px;">{score}</td>'
            matrix_html += '</tr>'
        
        matrix_html += '</table>'
        
        # Legend
        matrix_html += '<div style="margin-top: 15px;">'
        matrix_html += '<p><strong>Legend:</strong></p>'
        matrix_html += '<ul style="list-style: none; padding: 0;">'
        matrix_html += '<li><span style="background: #dc3545; color: white; padding: 3px 10px; border-radius: 3px; margin-right: 10px;">15-25</span> Critical Risk</li>'
        matrix_html += '<li><span style="background: #fd7e14; color: white; padding: 3px 10px; border-radius: 3px; margin-right: 10px;">10-14</span> High Risk</li>'
        matrix_html += '<li><span style="background: #ffc107; color: white; padding: 3px 10px; border-radius: 3px; margin-right: 10px;">6-9</span> Medium Risk</li>'
        matrix_html += '<li><span style="background: #28a745; color: white; padding: 3px 10px; border-radius: 3px; margin-right: 10px;">1-5</span> Low Risk</li>'
        matrix_html += '</ul>'
        matrix_html += '<p style="margin-top: 10px;"><strong>Black border</strong> indicates current residual risk position.</p>'
        matrix_html += '</div>'
        
        # Display inherent vs residual vs target
        matrix_html += '<div style="margin-top: 20px;">'
        matrix_html += '<h4>Risk Progression:</h4>'
        matrix_html += '<ul>'
        matrix_html += f'<li><strong>Inherent Risk:</strong> {obj.inherent_likelihood} × {obj.inherent_impact} = {obj.inherent_score} ({obj.get_risk_level()})</li>'
        matrix_html += f'<li><strong>Residual Risk (Current):</strong> {obj.residual_likelihood} × {obj.residual_impact} = {obj.residual_score} ({obj.get_risk_level()})</li>'
        if obj.target_score:
            matrix_html += f'<li><strong>Target Risk:</strong> {obj.target_likelihood} × {obj.target_impact} = {obj.target_score}</li>'
            matrix_html += f'<li><strong>Gap to Target:</strong> {obj.mitigation_gap()} points</li>'
        matrix_html += f'<li><strong>Risk Reduction:</strong> {obj.risk_reduction_percentage():.1f}%</li>'
        matrix_html += '</ul>'
        matrix_html += '</div>'
        
        matrix_html += '</div>'
        return format_html(matrix_html)
    risk_matrix_display.short_description = 'Risk Matrix Visualization'
    
    def mitigation_summary(self, obj):
        """Summary of mitigations"""
        mitigations = obj.mitigations.all()
        if not mitigations.exists():
            return format_html('<p style="color: #dc3545;">⚠ No mitigations defined</p>')
        
        total = mitigations.count()
        completed = mitigations.filter(status='COMPLETED').count()
        in_progress = mitigations.filter(status='IN_PROGRESS').count()
        overdue = mitigations.filter(status='OVERDUE').count()
        
        html = '<div style="margin: 10px 0;">'
        html += f'<p><strong>Total Mitigations:</strong> {total}</p>'
        html += '<ul>'
        html += f'<li>✅ Completed: {completed}</li>'
        html += f'<li>🔄 In Progress: {in_progress}</li>'
        if overdue > 0:
            html += f'<li style="color: #dc3545;">⚠ Overdue: {overdue}</li>'
        html += '</ul>'
        
        completion_pct = (completed / total * 100) if total > 0 else 0
        html += f'<div style="width: 100%; background: #e9ecef; border-radius: 4px; overflow: hidden; margin-top: 10px;">'
        html += f'<div style="width: {completion_pct}%; background: #28a745; color: white; text-align: center; padding: 8px 0; font-weight: bold;">{completion_pct:.0f}% Complete</div>'
        html += '</div>'
        html += '</div>'
        
        return format_html(html)
    mitigation_summary.short_description = 'Mitigation Progress'
    
    def mark_as_escalated(self, request, queryset):
        """Mark selected risks as escalated"""
        updated = queryset.update(is_escalated=True, status='ESCALATED')
        self.message_user(request, f'{updated} risk(s) marked as escalated')
    mark_as_escalated.short_description = 'Mark as escalated'
    
    def mark_as_controlled(self, request, queryset):
        """Mark selected risks as controlled"""
        updated = queryset.update(status='CONTROLLED')
        self.message_user(request, f'{updated} risk(s) marked as controlled')
    mark_as_controlled.short_description = 'Mark as controlled'
    
    def schedule_review(self, request, queryset):
        """Schedule next review for selected risks"""
        for risk in queryset:
            # Calculate next review date based on frequency
            if risk.review_frequency == 'MONTHLY':
                risk.next_review_date = timezone.now().date() + timezone.timedelta(days=30)
            elif risk.review_frequency == 'QUARTERLY':
                risk.next_review_date = timezone.now().date() + timezone.timedelta(days=90)
            elif risk.review_frequency == 'BIANNUALLY':
                risk.next_review_date = timezone.now().date() + timezone.timedelta(days=180)
            elif risk.review_frequency == 'ANNUALLY':
                risk.next_review_date = timezone.now().date() + timezone.timedelta(days=365)
            risk.save()
        self.message_user(request, f'{queryset.count()} risk(s) review scheduled')
    schedule_review.short_description = 'Schedule next review'
    
    def changelist_view(self, request, extra_context=None):
        """Add Chart.js dashboard to list view"""
        extra_context = extra_context or {}
        
        # Get risk statistics
        total_risks = RiskRegister.objects.count()
        critical_risks = RiskRegister.objects.filter(priority='CRITICAL').count()
        high_risks = RiskRegister.objects.filter(priority='HIGH').count()
        
        # Prepare Chart.js data
        extra_context['show_risk_dashboard'] = True
        extra_context['total_risks'] = total_risks
        extra_context['critical_risks'] = critical_risks
        extra_context['high_risks'] = high_risks
        
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(RiskMitigation)
class RiskMitigationAdmin(admin.ModelAdmin):
    """Enhanced admin for risk mitigations"""
    
    list_display = [
        'action',
        'risk',
        'priority_badge',
        'status_badge',
        'mitigation_type',
        'assigned_to',
        'progress_bar',
        'days_remaining_display',
        'effectiveness_badge'
    ]
    list_filter = ['status', 'priority', 'mitigation_type', 'regulatory_requirement']
    search_fields = ['action', 'description', 'risk__risk_id', 'risk__title']
    readonly_fields = ['created_at', 'updated_at', 'cost_variance_display']
    
    fieldsets = (
        ('Mitigation Details', {
            'fields': (
                'risk',
                'action',
                'description',
                'mitigation_type'
            )
        }),
        ('Expected Impact', {
            'fields': (
                ('expected_likelihood_reduction', 'expected_impact_reduction'),
            )
        }),
        ('Implementation', {
            'fields': (
                ('status', 'priority'),
                'assigned_to',
                ('start_date', 'target_completion_date', 'actual_completion_date'),
                'completion_percentage',
                'progress_notes'
            )
        }),
        ('Resources & Costs', {
            'fields': (
                ('estimated_cost', 'actual_cost', 'cost_variance_display'),
                'resources_required'
            ),
            'classes': ('collapse',)
        }),
        ('Effectiveness Tracking', {
            'fields': (
                'effectiveness_rating',
                'effectiveness_notes'
            ),
            'classes': ('collapse',)
        }),
        ('Integration', {
            'fields': (
                'linked_pdsa_project',
                'regulatory_requirement'
            ),
            'classes': ('collapse',)
        }),
        ('Audit Trail', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def priority_badge(self, obj):
        """Display priority badge"""
        colors = {
            'IMMEDIATE': '#dc3545',
            'HIGH': '#fd7e14',
            'MEDIUM': '#ffc107',
            'LOW': '#28a745'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; '
            'border-radius: 5px; font-weight: bold;">{}</span>',
            colors.get(obj.priority, '#6c757d'),
            obj.priority
        )
    priority_badge.short_description = 'Priority'
    priority_badge.admin_order_field = 'priority'
    
    def status_badge(self, obj):
        """Display status badge"""
        colors = {
            'PLANNED': '#6c757d',
            'IN_PROGRESS': '#007bff',
            'COMPLETED': '#28a745',
            'ON_HOLD': '#ffc107',
            'CANCELLED': '#dc3545',
            'OVERDUE': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; '
            'border-radius: 5px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def progress_bar(self, obj):
        """Visual progress bar"""
        pct = obj.completion_percentage
        
        # Color based on completion
        if pct == 100:
            color = '#28a745'  # Green
        elif pct >= 50:
            color = '#007bff'  # Blue
        else:
            color = '#ffc107'  # Yellow
        
        return format_html(
            '<div style="width: 150px; background: #e9ecef; border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; background: {}; color: white; text-align: center; '
            'padding: 5px 0; font-size: 11px; font-weight: bold;">{}</div>'
            '</div>',
            pct,
            color,
            f'{pct}%'
        )
    progress_bar.short_description = 'Progress'
    
    def days_remaining_display(self, obj):
        """Days until deadline"""
        days = obj.days_remaining()
        if obj.status == 'COMPLETED':
            return format_html('<span style="color: #28a745;">✓ Completed</span>')
        elif days < 0:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">⚠ {} days overdue</span>',
                abs(days)
            )
        elif days == 0:
            return format_html('<span style="color: #dc3545; font-weight: bold;">⏰ DUE TODAY</span>')
        elif days <= 7:
            return format_html('<span style="color: #fd7e14;">{} days</span>', days)
        return format_html('<span style="color: #28a745;">{} days</span>', days)
    days_remaining_display.short_description = 'Days Remaining'
    
    def effectiveness_badge(self, obj):
        """Effectiveness rating badge"""
        if not obj.effectiveness_rating:
            return '—'
        
        colors = {
            1: '#dc3545',  # Ineffective
            2: '#ffc107',  # Partially
            3: '#007bff',  # Mostly
            4: '#28a745'   # Fully
        }
        labels = {
            1: 'Ineffective',
            2: 'Partial',
            3: 'Mostly',
            4: 'Fully Effective'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; '
            'border-radius: 5px;">{}</span>',
            colors.get(obj.effectiveness_rating, '#6c757d'),
            labels.get(obj.effectiveness_rating, '—')
        )
    effectiveness_badge.short_description = 'Effectiveness'
    
    def cost_variance_display(self, obj):
        """Display cost variance"""
        variance = obj.cost_variance()
        if variance is None:
            return '—'
        
        if variance > 0:
            return format_html('<span style="color: #dc3545;">+£{:,.2f} over budget</span>', variance)
        elif variance < 0:
            return format_html('<span style="color: #28a745;">£{:,.2f} under budget</span>', abs(variance))
        return format_html('<span style="color: #28a745;">On budget</span>')
    cost_variance_display.short_description = 'Cost Variance'


@admin.register(RiskReview)
class RiskReviewAdmin(admin.ModelAdmin):
    """Enhanced admin for risk reviews"""
    
    list_display = [
        'risk',
        'review_date',
        'reviewed_by',
        'reassessed_score_display',
        'trend_badge',
        'decision_badge',
        'next_review_date'
    ]
    list_filter = ['decision', 'controls_effective', 'new_mitigations_required']
    search_fields = ['risk__risk_id', 'risk__title', 'decision_rationale']
    readonly_fields = ['reassessed_score', 'created_at']
    
    fieldsets = (
        ('Review Details', {
            'fields': (
                'risk',
                'review_date',
                'reviewed_by'
            )
        }),
        ('Reassessment', {
            'fields': (
                ('reassessed_likelihood', 'reassessed_impact', 'reassessed_score'),
            )
        }),
        ('Control Effectiveness', {
            'fields': (
                'controls_effective',
                'control_gaps'
            )
        }),
        ('New Mitigations', {
            'fields': (
                'new_mitigations_required',
                'recommended_actions'
            )
        }),
        ('Decision & Rationale', {
            'fields': (
                'decision',
                'decision_rationale',
                'next_review_date',
                'follow_up_actions'
            )
        }),
        ('Context', {
            'fields': (
                'incidents_since_last_review',
                'changes_in_environment'
            ),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def reassessed_score_display(self, obj):
        """Display reassessed score with color"""
        score = obj.reassessed_score
        if score >= 15:
            color = '#dc3545'
        elif score >= 10:
            color = '#fd7e14'
        elif score >= 6:
            color = '#ffc107'
        else:
            color = '#28a745'
        
        return format_html(
            '<div style="text-align: center; background: {}; color: white; '
            'font-weight: bold; padding: 8px; border-radius: 5px; min-width: 50px;">{}</div>',
            color,
            score
        )
    reassessed_score_display.short_description = 'Risk Score'
    reassessed_score_display.admin_order_field = 'reassessed_score'
    
    def trend_badge(self, obj):
        """Display risk trend"""
        trend = obj.trend()
        if trend == 'INCREASING':
            return format_html('<span style="color: #dc3545; font-weight: bold;">↑ Increasing</span>')
        elif trend == 'DECREASING':
            return format_html('<span style="color: #28a745; font-weight: bold;">↓ Decreasing</span>')
        return format_html('<span style="color: #6c757d;">→ Stable</span>')
    trend_badge.short_description = 'Trend'
    
    def decision_badge(self, obj):
        """Display decision badge"""
        colors = {
            'CONTINUE': '#28a745',
            'ESCALATE': '#dc3545',
            'DE_ESCALATE': '#007bff',
            'CLOSE': '#6c757d',
            'ACCEPT': '#ffc107',
            'TRANSFER': '#6f42c1',
            'ADDITIONAL_MITIGATION': '#fd7e14'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; '
            'border-radius: 5px;">{}</span>',
            colors.get(obj.decision, '#6c757d'),
            obj.get_decision_display()
        )
    decision_badge.short_description = 'Decision'
    decision_badge.admin_order_field = 'decision'


@admin.register(RiskTreatmentPlan)
class RiskTreatmentPlanAdmin(admin.ModelAdmin):
    """Enhanced admin for risk treatment plans"""
    
    list_display = [
        'plan_name',
        'risk',
        'status_badge',
        'progress_bar',
        'budget_utilization_bar',
        'schedule_status',
        'plan_owner'
    ]
    list_filter = ['status', 'start_date']
    search_fields = ['plan_name', 'objectives', 'risk__risk_id']
    readonly_fields = ['created_at', 'updated_at', 'last_updated']
    
    fieldsets = (
        ('Plan Details', {
            'fields': (
                'risk',
                'plan_name',
                'objectives',
                'treatment_strategy',
                'success_criteria'
            )
        }),
        ('Status & Approval', {
            'fields': (
                'status',
                ('approved_by', 'approval_date')
            )
        }),
        ('Timeline', {
            'fields': (
                ('start_date', 'target_completion_date', 'actual_completion_date'),
            )
        }),
        ('Budget', {
            'fields': (
                ('total_budget', 'spent_to_date'),
            )
        }),
        ('Team', {
            'fields': (
                'plan_owner',
                'team_members'
            )
        }),
        ('Progress', {
            'fields': (
                'overall_progress',
                'monthly_updates'
            )
        }),
        ('Integration', {
            'fields': ('linked_pdsa_projects',),
            'classes': ('collapse',)
        }),
        ('Audit Trail', {
            'fields': ('created_by', 'created_at', 'updated_at', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status badge"""
        colors = {
            'DRAFT': '#6c757d',
            'PENDING_APPROVAL': '#ffc107',
            'APPROVED': '#007bff',
            'IN_PROGRESS': '#17a2b8',
            'COMPLETED': '#28a745',
            'CANCELLED': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; '
            'border-radius: 5px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def progress_bar(self, obj):
        """Visual progress bar"""
        pct = obj.overall_progress
        
        if pct == 100:
            color = '#28a745'
        elif pct >= 70:
            color = '#007bff'
        elif pct >= 40:
            color = '#ffc107'
        else:
            color = '#dc3545'
        
        return format_html(
            '<div style="width: 150px; background: #e9ecef; border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; background: {}; color: white; text-align: center; '
            'padding: 5px 0; font-size: 11px; font-weight: bold;">{}</div>'
            '</div>',
            pct,
            color,
            f'{pct}%'
        )
    progress_bar.short_description = 'Overall Progress'
    
    def budget_utilization_bar(self, obj):
        """Budget utilization bar"""
        pct = obj.budget_utilization_percentage()
        
        if pct <= 80:
            color = '#28a745'  # Green - under budget
        elif pct <= 100:
            color = '#ffc107'  # Yellow - on budget
        else:
            color = '#dc3545'  # Red - over budget
        
        return format_html(
            '<div style="width: 150px; background: #e9ecef; border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; background: {}; color: white; text-align: center; '
            'padding: 5px 0; font-size: 11px; font-weight: bold;">{:.0f}%</div>'
            '</div>',
            min(pct, 100),
            color,
            pct
        )
    budget_utilization_bar.short_description = 'Budget Used'
    
    def schedule_status(self, obj):
        """Schedule status indicator"""
        if obj.is_on_schedule():
            return format_html('<span style="color: #28a745; font-weight: bold;">✓ On Schedule</span>')
        return format_html('<span style="color: #dc3545; font-weight: bold;">⚠ Behind Schedule</span>')
    schedule_status.short_description = 'Schedule'
