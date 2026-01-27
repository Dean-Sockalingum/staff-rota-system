from django.contrib import admin
from django.utils.html import format_html
from .models import (
    CompetencyFramework,
    RoleCompetencyRequirement,
    CompetencyAssessment,
    TrainingMatrix,
    LearningPathway,
    PathwayCompetency,
    PathwayTraining,
    StaffLearningPlan
)


@admin.register(CompetencyFramework)
class CompetencyFrameworkAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'competency_type', 'is_active', 'review_frequency_months', 'related_roles_count']
    list_filter = ['competency_type', 'is_active']
    search_fields = ['code', 'title', 'description']
    filter_horizontal = ['linked_training_courses']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'title', 'competency_type', 'description', 'is_active')
        }),
        ('Assessment Requirements', {
            'fields': (
                'assessment_criteria',
                'evidence_required',
                'review_frequency_months'
            )
        }),
        ('Related Items', {
            'fields': ('linked_training_courses',)
        }),
    )
    
    def related_roles_count(self, obj):
        return obj.required_for_roles.count()
    related_roles_count.short_description = 'Roles'


@admin.register(RoleCompetencyRequirement)
class RoleCompetencyRequirementAdmin(admin.ModelAdmin):
    list_display = ['role', 'competency', 'required_level', 'is_mandatory', 'grace_period_days']
    list_filter = ['role', 'required_level', 'is_mandatory']
    search_fields = ['role__name', 'competency__name']


@admin.register(CompetencyAssessment)
class CompetencyAssessmentAdmin(admin.ModelAdmin):
    list_display = ['staff_member', 'competency', 'assessment_date', 'achieved_level', 'outcome_badge', 'assessor']
    list_filter = ['assessment_method', 'achieved_level', 'outcome', 'assessment_date']
    search_fields = ['staff_member__sap', 'staff_member__first_name', 'staff_member__last_name', 'competency__name']
    date_hierarchy = 'assessment_date'
    
    fieldsets = (
        ('Assessment Details', {
            'fields': ('staff_member', 'competency', 'assessment_date', 'assessor', 'assessment_method')
        }),
        ('Results', {
            'fields': ('achieved_level', 'outcome', 'assessor_comments', 'evidence_submitted')
        }),
        ('Staff Reflection & Development', {
            'fields': ('staff_reflection', 'identified_development_needs', 'action_plan')
        }),
        ('Follow-up', {
            'fields': ('next_review_date', 'expiry_date')
        }),
    )
    
    def outcome_badge(self, obj):
        colors = {
            'NOT_YET_STARTED': '#6c757d',
            'IN_PROGRESS': '#0dcaf0',
            'COMPETENT': '#198754',
            'HIGHLY_COMPETENT': '#0d6efd',
            'NOT_YET_COMPETENT': '#ffc107',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.outcome, '#6c757d'),
            obj.get_outcome_display()
        )
    outcome_badge.short_description = 'Outcome'


@admin.register(TrainingMatrix)
class TrainingMatrixAdmin(admin.ModelAdmin):
    list_display = ['role', 'training_course', 'requirement_type', 'priority_order', 'care_home']
    list_filter = ['role', 'requirement_type', 'care_home', 'must_complete_before_solo_work']
    search_fields = ['role__name', 'training_course__name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('role', 'training_course', 'requirement_type', 'care_home')
        }),
        ('Timing Requirements', {
            'fields': ('must_complete_within_days', 'must_complete_before_solo_work')
        }),
        ('Ordering & Prerequisites', {
            'fields': ('priority_order', 'prerequisite_courses')
        }),
    )


@admin.register(LearningPathway)
class LearningPathwayAdmin(admin.ModelAdmin):
    list_display = ['title', 'from_role', 'to_role', 'estimated_duration_months', 'status', 'owner']
    list_filter = ['status', 'from_role', 'to_role']
    search_fields = ['title', 'description']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'from_role', 'to_role', 'status')
        }),
        ('Timeline', {
            'fields': ('estimated_duration_months', 'total_learning_hours')
        }),
        ('Management', {
            'fields': ('owner', 'approved_by', 'approved_date')
        }),
    )


@admin.register(PathwayCompetency)
class PathwayCompetencyAdmin(admin.ModelAdmin):
    list_display = ['pathway', 'competency', 'required_level', 'sequence_order']
    list_filter = ['pathway', 'required_level']
    search_fields = ['pathway__name', 'competency__name']


@admin.register(PathwayTraining)
class PathwayTrainingAdmin(admin.ModelAdmin):
    list_display = ['pathway', 'training_course', 'is_mandatory', 'sequence_order']
    list_filter = ['pathway', 'is_mandatory']
    search_fields = ['pathway__name', 'training_course__name']


@admin.register(StaffLearningPlan)
class StaffLearningPlanAdmin(admin.ModelAdmin):
    list_display = ['staff_member', 'pathway', 'status_badge', 'progress_bar', 'target_completion_date', 'mentor']
    list_filter = ['status', 'pathway', 'enrollment_date']
    search_fields = ['staff_member__sap', 'staff_member__first_name', 'staff_member__last_name']
    date_hierarchy = 'enrollment_date'
    
    fieldsets = (
        ('Plan Details', {
            'fields': ('staff_member', 'pathway', 'enrollment_date', 'status')
        }),
        ('Progress', {
            'fields': ('percent_complete', 'target_completion_date', 'actual_completion_date')
        }),
        ('Support', {
            'fields': ('mentor', 'line_manager', 'review_notes')
        }),
        ('Review Schedule', {
            'fields': ('last_review_date', 'next_review_date')
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'PLANNED': '#6c757d',
            'IN_PROGRESS': '#0dcaf0',
            'ON_HOLD': '#ffc107',
            'COMPLETED': '#198754',
            'WITHDRAWN': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def progress_bar(self, obj):
        percent = obj.percent_complete or 0
        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 3px;">'
            '<div style="width: {}%; background-color: #198754; color: white; text-align: center; border-radius: 3px; padding: 2px 0;">{}%</div>'
            '</div>',
            percent,
            percent
        )
    progress_bar.short_description = 'Progress'

