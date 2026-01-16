"""
TQM Module 3: Experience & Feedback Admin Interface

Enhanced admin interfaces for:
- Satisfaction Surveys with average scoring
- Complaints with resolution tracking
- EBCD Touchpoint mapping
- Quality of Life Assessments
- Feedback Theme analysis
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg, Count
from .models import (
    SatisfactionSurvey,
    Complaint,
    EBCDTouchpoint,
    QualityOfLifeAssessment,
    FeedbackTheme,
)


@admin.register(SatisfactionSurvey)
class SatisfactionSurveyAdmin(admin.ModelAdmin):
    """Admin interface for Satisfaction Surveys."""
    
    list_display = [
        'survey_reference',
        'survey_type',
        'care_home',
        'resident',
        'survey_date',
        'satisfaction_badge',
        'nps_badge',
        'requires_followup',
    ]
    
    list_filter = [
        'survey_type',
        'care_home',
        'survey_date',
        'requires_followup',
        'followup_completed',
    ]
    
    search_fields = [
        'respondent_name',
        'resident__first_name',
        'resident__last_name',
        'what_works_well',
        'areas_for_improvement',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'average_score_display',
        'nps_category_display',
    ]
    
    fieldsets = (
        ('Survey Information', {
            'fields': (
                'survey_type',
                'survey_date',
                'care_home',
                'resident',
            )
        }),
        ('Respondent', {
            'fields': (
                'respondent_name',
                'relationship_to_resident',
                'is_anonymous',
            )
        }),
        ('Satisfaction Ratings', {
            'fields': (
                'overall_satisfaction',
                'quality_of_care',
                'staff_attitude',
                'communication',
                'environment_cleanliness',
                'meals_nutrition',
                'activities_engagement',
                'dignity_respect',
                'safety_security',
                'average_score_display',
            )
        }),
        ('Net Promoter Score', {
            'fields': (
                'likelihood_recommend',
                'nps_category_display',
            )
        }),
        ('Qualitative Feedback', {
            'fields': (
                'what_works_well',
                'areas_for_improvement',
                'additional_comments',
            )
        }),
        ('Follow-up', {
            'fields': (
                'requires_followup',
                'followup_assigned_to',
                'followup_completed',
                'followup_notes',
            )
        }),
        ('Metadata', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at', 'created_by'),
        }),
    )
    
    def survey_reference(self, obj):
        """Display a shortened reference."""
        return f"SS-{obj.id:04d}"
    survey_reference.short_description = 'Reference'
    
    def satisfaction_badge(self, obj):
        """Display satisfaction as a colored badge."""
        avg = obj.get_average_score()
        if avg >= 4.0:
            color = '#28a745'  # Green
            label = 'Excellent'
        elif avg >= 3.0:
            color = '#ffc107'  # Amber
            label = 'Good'
        else:
            color = '#dc3545'  # Red
            label = 'Needs Attention'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{:.1f} - {}</span>',
            color, avg, label
        )
    satisfaction_badge.short_description = 'Avg Score'
    
    def nps_badge(self, obj):
        """Display NPS category as a badge."""
        if obj.likelihood_recommend is None:
            return '-'
        
        category = obj.get_nps_category()
        if category == 'PROMOTER':
            color = '#28a745'
            label = f'Promoter ({obj.likelihood_recommend})'
        elif category == 'PASSIVE':
            color = '#ffc107'
            label = f'Passive ({obj.likelihood_recommend})'
        else:
            color = '#dc3545'
            label = f'Detractor ({obj.likelihood_recommend})'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color, label
        )
    nps_badge.short_description = 'NPS'
    
    def average_score_display(self, obj):
        """Display average score across all dimensions."""
        return f"{obj.get_average_score():.2f} / 5.00"
    average_score_display.short_description = 'Average Score'
    
    def nps_category_display(self, obj):
        """Display NPS category."""
        if obj.likelihood_recommend is None:
            return 'Not Provided'
        return f"{obj.get_nps_category()} (Score: {obj.likelihood_recommend}/10)"
    nps_category_display.short_description = 'NPS Category'
    
    def save_model(self, request, obj, form, change):
        """Auto-populate created_by on new surveys."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    """Admin interface for Complaints."""
    
    list_display = [
        'complaint_reference',
        'care_home',
        'date_received',
        'severity_badge',
        'status_badge',
        'overdue_indicator',
        'escalated',
    ]
    
    list_filter = [
        'status',
        'severity',
        'care_home',
        'complaint_category',
        'escalated_to_care_inspectorate',
        'date_received',
    ]
    
    search_fields = [
        'complaint_reference',
        'complainant_name',
        'complaint_description',
        'resolution_details',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'days_since_received_display',
        'acknowledgement_status_display',
        'overdue_status_display',
    ]
    
    fieldsets = (
        ('Complaint Identification', {
            'fields': (
                'complaint_reference',
                'care_home',
                'date_received',
                'complaint_category',
                'severity',
            )
        }),
        ('Complainant Information', {
            'fields': (
                'complainant_name',
                'complainant_relationship',
                'complainant_contact',
                'resident',
            )
        }),
        ('Complaint Details', {
            'fields': (
                'complaint_description',
                'desired_outcome',
            )
        }),
        ('Status & Timeline', {
            'fields': (
                'status',
                'date_acknowledged',
                'target_resolution_date',
                'actual_resolution_date',
                'days_since_received_display',
                'acknowledgement_status_display',
                'overdue_status_display',
            )
        }),
        ('Investigation', {
            'fields': (
                'investigating_officer',
                'investigation_notes',
                'root_cause',
                'lessons_learned',
            )
        }),
        ('Resolution', {
            'fields': (
                'resolution_details',
                'complainant_satisfied',
            )
        }),
        ('Escalation', {
            'fields': (
                'escalated_to_care_inspectorate',
                'escalation_date',
                'escalation_reference',
            )
        }),
        ('Related Records', {
            'fields': (
                'related_incident',
            )
        }),
        ('Metadata', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at', 'created_by'),
        }),
    )
    
    def severity_badge(self, obj):
        """Display severity as a colored badge."""
        colors = {
            'LOW': '#17a2b8',  # Info
            'MEDIUM': '#ffc107',  # Warning
            'HIGH': '#fd7e14',  # Orange
            'CRITICAL': '#dc3545',  # Danger
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.severity, '#6c757d'),
            obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'
    
    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'RECEIVED': '#6c757d',
            'ACKNOWLEDGED': '#17a2b8',
            'INVESTIGATING': '#007bff',
            'AWAITING_RESPONSE': '#ffc107',
            'RESOLVED': '#28a745',
            'ESCALATED': '#dc3545',
            'CLOSED': '#6c757d',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def overdue_indicator(self, obj):
        """Show if complaint is overdue."""
        if obj.is_overdue():
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">⚠ OVERDUE</span>'
            )
        return format_html(
            '<span style="color: #28a745;">✓ On Track</span>'
        )
    overdue_indicator.short_description = 'Timeline'
    
    def escalated(self, obj):
        """Show if escalated to Care Inspectorate."""
        if obj.escalated_to_care_inspectorate:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">⚠ Escalated</span>'
            )
        return '-'
    escalated.short_description = 'Escalation'
    
    def days_since_received_display(self, obj):
        """Display days since complaint received."""
        return f"{obj.days_since_received()} days"
    days_since_received_display.short_description = 'Days Open'
    
    def acknowledgement_status_display(self, obj):
        """Display acknowledgement status."""
        if obj.acknowledgement_within_target():
            return format_html(
                '<span style="color: #28a745;">✓ Within 3 days</span>'
            )
        elif obj.date_acknowledged:
            return format_html(
                '<span style="color: #dc3545;">⚠ Late acknowledgement</span>'
            )
        else:
            return format_html(
                '<span style="color: #ffc107;">⚠ Not yet acknowledged</span>'
            )
    acknowledgement_status_display.short_description = 'Acknowledgement'
    
    def overdue_status_display(self, obj):
        """Display overdue status with details."""
        if obj.is_overdue():
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">⚠ OVERDUE - Requires urgent attention</span>'
            )
        return format_html(
            '<span style="color: #28a745;">✓ On track</span>'
        )
    overdue_status_display.short_description = 'Overdue Status'
    
    def save_model(self, request, obj, form, change):
        """Auto-populate created_by on new complaints."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EBCDTouchpoint)
class EBCDTouchpointAdmin(admin.ModelAdmin):
    """Admin interface for EBCD Touchpoints."""
    
    list_display = [
        'touchpoint_name',
        'category',
        'care_home',
        'importance_badge',
        'emotional_badge',
        'experience_gap_badge',
        'is_active',
    ]
    
    list_filter = [
        'category',
        'care_home',
        'is_active',
        'importance_rating',
        'emotional_impact',
    ]
    
    search_fields = [
        'touchpoint_name',
        'description',
        'pain_points',
        'improvement_ideas',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'improvement_gap_display',
    ]
    
    fieldsets = (
        ('Touchpoint Definition', {
            'fields': (
                'care_home',
                'touchpoint_name',
                'category',
                'description',
                'sequence_order',
            )
        }),
        ('Importance & Impact', {
            'fields': (
                'importance_rating',
                'emotional_impact',
            )
        }),
        ('Current State', {
            'fields': (
                'current_experience_rating',
                'pain_points',
            )
        }),
        ('Desired State', {
            'fields': (
                'target_experience_rating',
                'improvement_gap_display',
                'improvement_ideas',
            )
        }),
        ('Co-Design Participation', {
            'fields': (
                'residents_consulted',
                'families_consulted',
                'staff_consulted',
            )
        }),
        ('Implementation', {
            'fields': (
                'improvements_implemented',
                'implementation_date',
                'is_active',
            )
        }),
        ('Metadata', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at', 'created_by'),
        }),
    )
    
    def importance_badge(self, obj):
        """Display importance as stars."""
        stars = '★' * obj.importance_rating + '☆' * (5 - obj.importance_rating)
        return format_html(
            '<span style="color: #ffc107; font-size: 14px;">{}</span>',
            stars
        )
    importance_badge.short_description = 'Importance'
    
    def emotional_badge(self, obj):
        """Display emotional impact as colored badge."""
        colors = {
            'VERY_POSITIVE': '#28a745',
            'POSITIVE': '#20c997',
            'NEUTRAL': '#6c757d',
            'NEGATIVE': '#fd7e14',
            'VERY_NEGATIVE': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.emotional_impact, '#6c757d'),
            obj.get_emotional_impact_display()
        )
    emotional_badge.short_description = 'Emotional Impact'
    
    def experience_gap_badge(self, obj):
        """Display gap between current and target experience."""
        gap = obj.get_improvement_gap()
        if gap is None:
            return '-'
        
        if gap > 0:
            color = '#ffc107'
            label = f'Gap: {gap} points'
        elif gap == 0:
            color = '#28a745'
            label = 'Target Met'
        else:
            color = '#17a2b8'
            label = f'Exceeds by {abs(gap)}'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color, label
        )
    experience_gap_badge.short_description = 'Experience Gap'
    
    def improvement_gap_display(self, obj):
        """Display improvement gap calculation."""
        gap = obj.get_improvement_gap()
        if gap is None:
            return 'Current or target rating not set'
        return f"{gap} point gap (Current: {obj.current_experience_rating}, Target: {obj.target_experience_rating})"
    improvement_gap_display.short_description = 'Improvement Gap'
    
    def save_model(self, request, obj, form, change):
        """Auto-populate created_by on new touchpoints."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(QualityOfLifeAssessment)
class QualityOfLifeAssessmentAdmin(admin.ModelAdmin):
    """Admin interface for Quality of Life Assessments."""
    
    list_display = [
        'resident',
        'assessment_date',
        'assessment_tool',
        'qol_score_badge',
        'assessment_method',
        'requires_review',
    ]
    
    list_filter = [
        'assessment_tool',
        'assessment_method',
        'requires_review',
        'review_completed',
        'assessment_date',
    ]
    
    search_fields = [
        'resident__first_name',
        'resident__last_name',
        'strengths_noted',
        'concerns_noted',
        'interventions_recommended',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'overall_qol_score',
        'composite_score_breakdown',
    ]
    
    fieldsets = (
        ('Assessment Information', {
            'fields': (
                'resident',
                'assessment_date',
                'assessment_tool',
                'assessed_by',
                'assessment_method',
            )
        }),
        ('Core QoL Dimensions', {
            'fields': (
                'physical_health',
                'psychological_wellbeing',
                'social_relationships',
                'independence_autonomy',
                'environment_comfort',
            )
        }),
        ('Additional Dimensions', {
            'fields': (
                'pain_discomfort',
                'cognitive_function',
                'meaningful_activity',
                'spiritual_needs',
            )
        }),
        ('Overall Score', {
            'fields': (
                'overall_qol_score',
                'composite_score_breakdown',
            )
        }),
        ('Qualitative Notes', {
            'fields': (
                'strengths_noted',
                'concerns_noted',
                'interventions_recommended',
            )
        }),
        ('Follow-up', {
            'fields': (
                'requires_review',
                'review_completed',
                'next_assessment_due',
            )
        }),
        ('Metadata', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )
    
    def qol_score_badge(self, obj):
        """Display QoL score as colored badge."""
        score = float(obj.overall_qol_score)
        if score >= 4.0:
            color = '#28a745'
            label = 'Excellent'
        elif score >= 3.0:
            color = '#ffc107'
            label = 'Good'
        elif score >= 2.0:
            color = '#fd7e14'
            label = 'Needs Attention'
        else:
            color = '#dc3545'
            label = 'Critical'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{:.2f} - {}</span>',
            color, score, label
        )
    qol_score_badge.short_description = 'QoL Score'
    
    def composite_score_breakdown(self, obj):
        """Display breakdown of composite score calculation."""
        scores = []
        scores.append(f"Physical Health: {obj.physical_health}/5")
        scores.append(f"Psychological Wellbeing: {obj.psychological_wellbeing}/5")
        scores.append(f"Social Relationships: {obj.social_relationships}/5")
        scores.append(f"Independence & Autonomy: {obj.independence_autonomy}/5")
        scores.append(f"Environment & Comfort: {obj.environment_comfort}/5")
        
        if obj.pain_discomfort:
            scores.append(f"Pain/Discomfort: {obj.pain_discomfort}/5")
        if obj.cognitive_function:
            scores.append(f"Cognitive Function: {obj.cognitive_function}/5")
        if obj.meaningful_activity:
            scores.append(f"Meaningful Activity: {obj.meaningful_activity}/5")
        if obj.spiritual_needs:
            scores.append(f"Spiritual Needs: {obj.spiritual_needs}/5")
        
        return format_html('<br>'.join(scores))
    composite_score_breakdown.short_description = 'Score Breakdown'


@admin.register(FeedbackTheme)
class FeedbackThemeAdmin(admin.ModelAdmin):
    """Admin interface for Feedback Themes."""
    
    list_display = [
        'theme_name',
        'care_home',
        'theme_category_badge',
        'occurrences_badge',
        'trend_badge',
        'impact_badge',
        'is_active',
    ]
    
    list_filter = [
        'theme_category',
        'care_home',
        'is_active',
        'trend_direction',
    ]
    
    search_fields = [
        'theme_name',
        'description',
        'action_plan',
        'actions_taken',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Theme Definition', {
            'fields': (
                'care_home',
                'theme_name',
                'theme_category',
                'description',
            )
        }),
        ('Frequency & Trend', {
            'fields': (
                'occurrences_count',
                'first_identified',
                'last_occurrence',
                'trend_direction',
            )
        }),
        ('Response & Action', {
            'fields': (
                'action_plan',
                'actions_taken',
                'assigned_to',
            )
        }),
        ('Impact Assessment', {
            'fields': (
                'impact_on_satisfaction',
            )
        }),
        ('Status', {
            'fields': (
                'is_active',
                'resolved_date',
            )
        }),
        ('Metadata', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at', 'created_by'),
        }),
    )
    
    def theme_category_badge(self, obj):
        """Display category as colored badge."""
        colors = {
            'POSITIVE': '#28a745',
            'CONCERN': '#ffc107',
            'SUGGESTION': '#17a2b8',
            'COMPLAINT': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.theme_category, '#6c757d'),
            obj.get_theme_category_display()
        )
    theme_category_badge.short_description = 'Category'
    
    def occurrences_badge(self, obj):
        """Display occurrence count with emphasis."""
        if obj.occurrences_count > 20:
            color = '#dc3545'  # High frequency
        elif obj.occurrences_count > 10:
            color = '#ffc107'  # Medium frequency
        else:
            color = '#17a2b8'  # Low frequency
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{} times</span>',
            color, obj.occurrences_count
        )
    occurrences_badge.short_description = 'Occurrences'
    
    def trend_badge(self, obj):
        """Display trend direction with icon."""
        if not obj.trend_direction:
            return '-'
        
        icons = {
            'INCREASING': '↗️',
            'STABLE': '→',
            'DECREASING': '↘️',
        }
        colors = {
            'INCREASING': '#dc3545' if obj.theme_category in ['CONCERN', 'COMPLAINT'] else '#28a745',
            'STABLE': '#6c757d',
            'DECREASING': '#28a745' if obj.theme_category in ['CONCERN', 'COMPLAINT'] else '#dc3545',
        }
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            colors.get(obj.trend_direction, '#6c757d'),
            icons.get(obj.trend_direction, ''),
            obj.get_trend_direction_display()
        )
    trend_badge.short_description = 'Trend'
    
    def impact_badge(self, obj):
        """Display impact rating as stars."""
        if obj.impact_on_satisfaction is None:
            return '-'
        
        stars = '★' * obj.impact_on_satisfaction + '☆' * (5 - obj.impact_on_satisfaction)
        return format_html(
            '<span style="color: #ffc107; font-size: 14px;">{}</span>',
            stars
        )
    impact_badge.short_description = 'Impact'
    
    def save_model(self, request, obj, form, change):
        """Auto-populate created_by on new themes."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

