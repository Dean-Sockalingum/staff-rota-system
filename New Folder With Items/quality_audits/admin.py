from django.contrib import admin
from django import forms
from django.contrib.postgres.fields import JSONField
from .models import (
    PDSAProject, PDSACycle, PDSATeamMember, PDSADataPoint, PDSAChatbotLog,
    QualityImprovementAction, QIAUpdate, QIAReview
)


class PDSAProjectAdminForm(forms.ModelForm):
    """Custom form to handle JSONField properly"""
    class Meta:
        model = PDSAProject
        fields = '__all__'
        widgets = {
            'ai_suggested_hypotheses': forms.Textarea(attrs={'rows': 4, 'cols': 60}),
            'chatbot_interactions': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }


class PDSADataPointInline(admin.TabularInline):
    model = PDSADataPoint
    extra = 1
    fields = ('measurement_date', 'value', 'notes', 'collected_by')


class PDSACycleInline(admin.StackedInline):
    model = PDSACycle
    extra = 0
    fields = (
        ('cycle_number', 'plan_start_date', 'plan_end_date'),
        'hypothesis',
        'prediction',
        'change_idea',
        'act_decision',
    )
    show_change_link = True


class PDSATeamMemberInline(admin.TabularInline):
    model = PDSATeamMember
    extra = 1


@admin.register(PDSAProject)
class PDSAProjectAdmin(admin.ModelAdmin):
    form = PDSAProjectAdminForm
    list_display = ('title', 'category', 'priority', 'status', 'lead_user', 'care_home', 'ai_success_score', 'created_at')
    list_filter = ('status', 'category', 'priority', 'care_home')
    search_fields = ('title', 'problem_description', 'aim_statement')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'aim_statement', 'problem_description', 'target_population')
        }),
        ('Team & Location', {
            'fields': ('lead_user', 'care_home', 'unit')
        }),
        ('Classification', {
            'fields': ('category', 'priority', 'status')
        }),
        ('Measurement', {
            'fields': ('baseline_value', 'target_value', 'measurement_unit')
        }),
        ('Timeline', {
            'fields': ('start_date', 'target_completion_date', 'actual_completion_date')
        }),
        ('AI & Automation', {
            'fields': ('ai_aim_generated', 'ai_success_score', 'chatbot_interactions'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PDSATeamMemberInline, PDSACycleInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PDSACycle)
class PDSACycleAdmin(admin.ModelAdmin):
    list_display = ('project', 'cycle_number', 'act_decision', 'plan_start_date', 'auto_analysis_completed')
    list_filter = ('act_decision', 'auto_analysis_completed', 'project__category')
    search_fields = ('project__title', 'hypothesis', 'change_idea')
    
    fieldsets = (
        ('Project Info', {
            'fields': ('project', 'cycle_number')
        }),
        ('PLAN Phase', {
            'fields': ('hypothesis', 'prediction', 'change_idea', 'data_collection_plan', 'plan_start_date', 'plan_end_date', 'ai_hypothesis_used')
        }),
        ('DO Phase', {
            'fields': ('execution_log', 'observations', 'deviations', 'staff_feedback', 'do_start_date', 'do_end_date'),
            'classes': ('collapse',)
        }),
        ('STUDY Phase', {
            'fields': ('data_analysis', 'ai_data_insights', 'findings', 'comparison_to_prediction', 'lessons_learned', 'unexpected_outcomes', 'study_completed_date', 'auto_analysis_completed'),
            'classes': ('collapse',)
        }),
        ('ACT Phase', {
            'fields': ('act_decision', 'next_steps', 'new_cycle_planned', 'spread_plan', 'act_completed_date'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PDSADataPointInline]


@admin.register(PDSATeamMember)
class PDSATeamMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role', 'joined_date')
    list_filter = ('role', 'joined_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'project__title')


@admin.register(PDSADataPoint)
class PDSADataPointAdmin(admin.ModelAdmin):
    list_display = ('cycle', 'measurement_date', 'value', 'collected_by', 'created_at')
    list_filter = ('measurement_date', 'collected_by')
    search_fields = ('cycle__project__title', 'notes')
    date_hierarchy = 'measurement_date'


@admin.register(PDSAChatbotLog)
class PDSAChatbotLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'context_phase', 'was_helpful', 'created_at')
    list_filter = ('context_phase', 'was_helpful', 'created_at')
    search_fields = ('user__username', 'project__title', 'user_question', 'chatbot_response')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'


# ============================================================================
# QIA (Quality Improvement Actions) ADMIN
# ============================================================================

class QIAUpdateInline(admin.TabularInline):
    model = QIAUpdate
    extra = 0
    fields = ('update_date', 'updated_by', 'percent_complete', 'update_notes')
    readonly_fields = ('update_date',)


class QIAReviewInline(admin.StackedInline):
    model = QIAReview
    extra = 0
    fields = (
        ('review_date', 'reviewer'),
        ('is_effective', 'effectiveness_rating'),
        'effectiveness_evidence',
        ('is_sustainable', 'sustainability_plan'),
        ('follow_up_required', 'follow_up_actions'),
        'lessons_learned',
        ('recommend_spread', 'spread_notes'),
        ('approved_for_closure', 'closure_notes'),
    )
    readonly_fields = ('review_date',)


@admin.register(QualityImprovementAction)
class QualityImprovementActionAdmin(admin.ModelAdmin):
    list_display = (
        'qia_reference',
        'title',
        'action_type',
        'source_type',
        'priority',
        'status',
        'responsible_person',
        'target_completion_date',
        'percent_complete',
        'is_overdue'
    )
    list_filter = (
        'status',
        'priority',
        'action_type',
        'source_type',
        'care_home',
        'requires_ci_notification',
    )
    search_fields = (
        'qia_reference',
        'title',
        'problem_description',
        'source_reference',
    )
    date_hierarchy = 'identified_date'
    readonly_fields = (
        'qia_reference',
        'created_at',
        'updated_at',
        'is_overdue',
        'days_until_due',
    )
    filter_horizontal = ('team_members',)
    
    fieldsets = (
        ('QIA Identification', {
            'fields': (
                'qia_reference',
                'title',
                'action_type',
                ('source_type', 'source_reference'),
            )
        }),
        ('Problem Analysis', {
            'fields': (
                'problem_description',
                'root_cause',
                'impact_analysis',
            )
        }),
        ('Action Planning', {
            'fields': (
                'action_plan',
                'success_criteria',
                'resources_needed',
            )
        }),
        ('Ownership', {
            'fields': (
                'care_home',
                'responsible_person',
                'team_members',
            )
        }),
        ('Timeline', {
            'fields': (
                'identified_date',
                ('planned_start_date', 'target_completion_date'),
                'actual_completion_date',
                ('days_until_due', 'is_overdue'),
            )
        }),
        ('Status & Progress', {
            'fields': (
                ('status', 'priority'),
                'percent_complete',
                'progress_notes',
            )
        }),
        ('Verification', {
            'fields': (
                'verification_method',
                ('verification_date', 'verified_by'),
                'effectiveness_rating',
                'effectiveness_notes',
            ),
            'classes': ('collapse',)
        }),
        ('Regulatory Compliance', {
            'fields': (
                'regulatory_requirement',
                ('requires_ci_notification', 'ci_notification_date'),
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': (
                'created_by',
                ('created_at', 'updated_at'),
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [QIAUpdateInline, QIAReviewInline]


@admin.register(QIAUpdate)
class QIAUpdateAdmin(admin.ModelAdmin):
    list_display = (
        'qia',
        'update_date',
        'updated_by',
        'percent_complete',
        'status_change',
    )
    list_filter = ('update_date', 'updated_by')
    search_fields = ('qia__qia_reference', 'qia__title', 'update_notes')
    date_hierarchy = 'update_date'
    readonly_fields = ('update_date',)


@admin.register(QIAReview)
class QIAReviewAdmin(admin.ModelAdmin):
    list_display = (
        'qia',
        'review_date',
        'reviewer',
        'is_effective',
        'effectiveness_rating',
        'approved_for_closure',
    )
    list_filter = (
        'review_date',
        'is_effective',
        'is_sustainable',
        'follow_up_required',
        'recommend_spread',
        'approved_for_closure',
    )
    search_fields = ('qia__qia_reference', 'qia__title', 'lessons_learned')
    date_hierarchy = 'review_date'
    readonly_fields = ('review_date',)
    
    fieldsets = (
        ('Review Details', {
            'fields': (
                'qia',
                ('review_date', 'reviewer'),
            )
        }),
        ('Effectiveness Assessment', {
            'fields': (
                ('is_effective', 'effectiveness_rating'),
                'effectiveness_evidence',
            )
        }),
        ('Sustainability', {
            'fields': (
                'is_sustainable',
                'sustainability_plan',
            )
        }),
        ('Follow-up', {
            'fields': (
                'follow_up_required',
                'follow_up_actions',
            )
        }),
        ('Learning & Spread', {
            'fields': (
                'lessons_learned',
                'recommend_spread',
                'spread_notes',
            )
        }),
        ('Closure', {
            'fields': (
                'approved_for_closure',
                'closure_notes',
            )
        }),
    )
