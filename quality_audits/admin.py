from django.contrib import admin
from .models import PDSAProject, PDSACycle, PDSATeamMember, PDSADataPoint, PDSAChatbotLog


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
    list_display = ('title', 'category', 'priority', 'status', 'lead_user', 'care_home', 'ai_success_score', 'created_at')
    list_filter = ('status', 'category', 'priority', 'care_home')
    search_fields = ('title', 'problem_description', 'aim_statement')
    date_hierarchy = 'created_at'
    
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
            'fields': ('ai_aim_generated', 'ai_success_score', 'ai_suggested_hypotheses', 'chatbot_interactions'),
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
