"""
TQM Module 5: Document & Policy Management Admin

Enhanced admin interface with badges, version control, and compliance tracking.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    DocumentCategory, Document, DocumentVersion, DocumentReview,
    StaffAcknowledgement, DocumentAttachment, PolicyImpactAssessment
)


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order', 'document_count', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'parent', 'order', 'is_active')
        }),
    )
    
    def document_count(self, obj):
        count = obj.documents.count()
        return format_html('<span class="badge badge-info">{}</span>', count)
    document_count.short_description = 'Documents'


class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    fields = ['version_number', 'change_type', 'change_summary', 'created_at', 'created_by']
    readonly_fields = ['created_at', 'created_by']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


class DocumentAttachmentInline(admin.TabularInline):
    model = DocumentAttachment
    extra = 1
    fields = ['title', 'file', 'file_type', 'file_size', 'order']
    readonly_fields = ['file_type', 'file_size']


class DocumentReviewInline(admin.TabularInline):
    model = DocumentReview
    extra = 0
    fields = ['review_type', 'due_date', 'reviewer', 'outcome', 'is_complete']
    readonly_fields = []
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('reviewer')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        'document_code', 'title', 'document_type_badge', 'status_badge',
        'version_number', 'owner', 'review_status_badge', 'acknowledgement_progress',
        'care_home'
    ]
    list_filter = [
        'status', 'document_type', 'category', 'requires_acknowledgement',
        'care_home', 'compliance_frameworks'
    ]
    search_fields = ['title', 'document_code', 'summary', 'keywords']
    readonly_fields = [
        'created_at', 'created_by', 'updated_at', 'updated_by',
        'attachments_count', 'review_status_display'
    ]
    
    fieldsets = (
        ('Document Information', {
            'fields': (
                ('document_code', 'document_type'),
                'title',
                'category',
                'summary',
                'keywords',
            )
        }),
        ('Version & Status', {
            'fields': (
                ('version_number', 'status'),
                'supersedes',
            )
        }),
        ('Content', {
            'fields': (
                'content',
                'file_upload',
                'attachments_count',
            )
        }),
        ('Ownership & Responsibility', {
            'fields': (
                ('owner', 'approver'),
                'care_home',
            )
        }),
        ('Compliance Mapping', {
            'fields': (
                'compliance_frameworks',
                'regulatory_references',
            ),
            'classes': ['collapse']
        }),
        ('Review Cycle', {
            'fields': (
                'review_frequency_months',
                ('last_reviewed_date', 'next_review_date'),
                'review_status_display',
            )
        }),
        ('Publishing', {
            'fields': (
                ('published_date', 'effective_from'),
            )
        }),
        ('Acknowledgement Tracking', {
            'fields': (
                'requires_acknowledgement',
                'acknowledgement_due_days',
            )
        }),
        ('Metadata', {
            'fields': (
                ('created_at', 'created_by'),
                ('updated_at', 'updated_by'),
            ),
            'classes': ['collapse']
        }),
    )
    
    inlines = [DocumentVersionInline, DocumentAttachmentInline, DocumentReviewInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def document_type_badge(self, obj):
        colors = {
            'POLICY': 'primary',
            'PROCEDURE': 'info',
            'GUIDANCE': 'secondary',
            'FORM': 'warning',
            'PROTOCOL': 'danger',
            'STANDARD': 'success',
        }
        color = colors.get(obj.document_type, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_document_type_display()
        )
    document_type_badge.short_description = 'Type'
    
    def status_badge(self, obj):
        colors = {
            'DRAFT': 'secondary',
            'IN_REVIEW': 'info',
            'APPROVED': 'success',
            'PUBLISHED': 'primary',
            'ARCHIVED': 'warning',
            'SUPERSEDED': 'danger',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def review_status_badge(self, obj):
        status = obj.get_review_status()
        days = obj.days_until_review()
        
        if status == 'overdue':
            return format_html(
                '<span class="badge badge-danger" title="{} days overdue">⚠️ OVERDUE</span>',
                abs(days)
            )
        elif status == 'due_soon':
            return format_html(
                '<span class="badge badge-warning" title="Due in {} days">⏰ DUE SOON</span>',
                days
            )
        elif status == 'current':
            return format_html(
                '<span class="badge badge-success" title="Due in {} days">✓ CURRENT</span>',
                days
            )
        else:
            return format_html('<span class="badge badge-secondary">—</span>')
    review_status_badge.short_description = 'Review Status'
    
    def review_status_display(self, obj):
        """Detailed review status for detail view."""
        days = obj.days_until_review()
        if days is None:
            return "Not scheduled"
        
        if days < 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ OVERDUE by {} days</span>',
                abs(days)
            )
        elif days <= 30:
            return format_html(
                '<span style="color: orange; font-weight: bold;">⏰ DUE in {} days</span>',
                days
            )
        else:
            return format_html(
                '<span style="color: green;">✓ CURRENT (due in {} days)</span>',
                days
            )
    review_status_display.short_description = 'Review Status'
    
    def acknowledgement_progress(self, obj):
        if not obj.requires_acknowledgement or obj.status != 'PUBLISHED':
            return format_html('<span class="text-muted">N/A</span>')
        
        rate = obj.acknowledgement_rate()
        if rate is None:
            return format_html('<span class="text-muted">—</span>')
        
        # Color based on completion rate
        if rate >= 90:
            color = 'success'
        elif rate >= 70:
            color = 'warning'
        else:
            color = 'danger'
        
        return format_html(
            '<div class="progress" style="width: 100px; height: 20px;">'
            '<div class="progress-bar bg-{}" role="progressbar" style="width: {}%;" '
            'aria-valuenow="{}" aria-valuemin="0" aria-valuemax="100">{:.0f}%</div>'
            '</div>',
            color, rate, rate, rate
        )
    acknowledgement_progress.short_description = 'Acknowledgements'


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ['document', 'version_number', 'change_type_badge', 'created_at', 'created_by', 'file_size_display']
    list_filter = ['change_type', 'created_at']
    search_fields = ['document__title', 'document__document_code', 'version_number', 'change_summary']
    readonly_fields = ['created_at', 'file_size']
    
    fieldsets = (
        ('Version Information', {
            'fields': (
                'document',
                'version_number',
                'change_type',
                'change_summary',
            )
        }),
        ('Content Snapshot', {
            'fields': (
                'title',
                'summary',
                'content',
                'file_upload',
                'file_size',
            ),
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': (
                ('created_at', 'created_by'),
            )
        }),
    )
    
    def change_type_badge(self, obj):
        colors = {
            'MAJOR': 'danger',
            'MINOR': 'warning',
            'CORRECTION': 'info',
            'REVIEW': 'success',
        }
        color = colors.get(obj.change_type, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_change_type_display()
        )
    change_type_badge.short_description = 'Change Type'
    
    def file_size_display(self, obj):
        if obj.file_size:
            # Convert bytes to KB/MB
            if obj.file_size < 1024:
                return f"{obj.file_size} bytes"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return "—"
    file_size_display.short_description = 'File Size'


@admin.register(DocumentReview)
class DocumentReviewAdmin(admin.ModelAdmin):
    list_display = [
        'document', 'review_type_badge', 'due_date', 'reviewer',
        'outcome_badge', 'completion_status', 'overdue_indicator'
    ]
    list_filter = ['review_type', 'outcome', 'is_complete', 'compliance_verified']
    search_fields = ['document__title', 'document__document_code', 'findings']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['additional_reviewers']
    
    fieldsets = (
        ('Review Information', {
            'fields': (
                'document',
                'review_type',
                ('due_date', 'completed_date'),
            )
        }),
        ('Reviewers', {
            'fields': (
                'reviewer',
                'additional_reviewers',
            )
        }),
        ('Findings & Outcome', {
            'fields': (
                'outcome',
                'findings',
                'action_items',
            )
        }),
        ('Compliance Verification', {
            'fields': (
                'compliance_verified',
                'compliance_notes',
            )
        }),
        ('Status', {
            'fields': ('is_complete',)
        }),
    )
    
    def review_type_badge(self, obj):
        colors = {
            'SCHEDULED': 'primary',
            'AD_HOC': 'info',
            'POST_INCIDENT': 'warning',
            'REGULATORY': 'danger',
        }
        color = colors.get(obj.review_type, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_review_type_display()
        )
    review_type_badge.short_description = 'Type'
    
    def outcome_badge(self, obj):
        if not obj.outcome:
            return format_html('<span class="badge badge-secondary">Pending</span>')
        
        colors = {
            'NO_CHANGE': 'success',
            'MINOR_UPDATE': 'info',
            'MAJOR_REVISION': 'warning',
            'RETIRE': 'danger',
        }
        color = colors.get(obj.outcome, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_outcome_display()
        )
    outcome_badge.short_description = 'Outcome'
    
    def completion_status(self, obj):
        if obj.is_complete:
            return format_html('<span class="badge badge-success">✓ Complete</span>')
        else:
            return format_html('<span class="badge badge-warning">⏳ In Progress</span>')
    completion_status.short_description = 'Status'
    
    def overdue_indicator(self, obj):
        if obj.is_overdue():
            days = obj.days_overdue()
            return format_html(
                '<span class="badge badge-danger" title="{} days overdue">⚠️ OVERDUE</span>',
                days
            )
        return format_html('<span class="badge badge-success">✓ On Time</span>')
    overdue_indicator.short_description = 'Due Status'


@admin.register(StaffAcknowledgement)
class StaffAcknowledgementAdmin(admin.ModelAdmin):
    list_display = [
        'staff_member', 'document_code', 'required_by',
        'acknowledgement_status', 'quiz_score_display', 'overdue_indicator'
    ]
    list_filter = ['acknowledgement_method', 'required_by', 'acknowledged_at']
    search_fields = [
        'staff_member__first_name', 'staff_member__last_name',
        'document__title', 'document__document_code'
    ]
    readonly_fields = ['assigned_at', 'reminder_sent_count', 'last_reminder_sent']
    
    fieldsets = (
        ('Assignment', {
            'fields': (
                'document',
                'staff_member',
                'required_by',
                ('assigned_at', 'assigned_by'),
            )
        }),
        ('Acknowledgement', {
            'fields': (
                'acknowledged_at',
                'acknowledgement_method',
                'quiz_score',
                'notes',
            )
        }),
        ('Reminders', {
            'fields': (
                'reminder_sent_count',
                'last_reminder_sent',
            ),
            'classes': ['collapse']
        }),
    )
    
    def document_code(self, obj):
        return obj.document.document_code
    document_code.short_description = 'Document Code'
    document_code.admin_order_field = 'document__document_code'
    
    def acknowledgement_status(self, obj):
        if obj.acknowledged_at:
            return format_html(
                '<span class="badge badge-success" title="Acknowledged on {}">✓ ACKNOWLEDGED</span>',
                obj.acknowledged_at.strftime('%Y-%m-%d %H:%M')
            )
        else:
            return format_html('<span class="badge badge-warning">⏳ PENDING</span>')
    acknowledgement_status.short_description = 'Status'
    
    def quiz_score_display(self, obj):
        if obj.quiz_score is not None:
            if obj.quiz_score >= 80:
                color = 'success'
            elif obj.quiz_score >= 60:
                color = 'warning'
            else:
                color = 'danger'
            
            return format_html(
                '<span class="badge badge-{}">{:.0f}%</span>',
                color,
                obj.quiz_score
            )
        return format_html('<span class="text-muted">—</span>')
    quiz_score_display.short_description = 'Quiz Score'
    
    def overdue_indicator(self, obj):
        if obj.is_overdue():
            days = obj.days_overdue()
            return format_html(
                '<span class="badge badge-danger" title="{} days overdue">⚠️ {} days</span>',
                days, days
            )
        elif obj.acknowledged_at:
            return format_html('<span class="badge badge-success">✓ Complete</span>')
        else:
            days_until = abs(obj.days_overdue()) if obj.days_overdue() else 0
            return format_html(
                '<span class="badge badge-info">{} days left</span>',
                days_until
            )
    overdue_indicator.short_description = 'Due Status'


@admin.register(DocumentAttachment)
class DocumentAttachmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'document', 'file_type_badge', 'file_size_display', 'uploaded_at', 'uploaded_by']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['title', 'document__title', 'document__document_code']
    readonly_fields = ['file_type', 'file_size', 'uploaded_at']
    
    fieldsets = (
        ('Attachment Information', {
            'fields': (
                'document',
                'title',
                'description',
                'order',
            )
        }),
        ('File', {
            'fields': (
                'file',
                ('file_type', 'file_size'),
            )
        }),
        ('Metadata', {
            'fields': (
                ('uploaded_at', 'uploaded_by'),
            )
        }),
    )
    
    def file_type_badge(self, obj):
        colors = {
            'PDF': 'danger',
            'DOCX': 'primary',
            'XLSX': 'success',
            'PPTX': 'warning',
        }
        color = colors.get(obj.file_type, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.file_type
        )
    file_type_badge.short_description = 'File Type'
    
    def file_size_display(self, obj):
        if obj.file_size < 1024:
            return f"{obj.file_size} bytes"
        elif obj.file_size < 1024 * 1024:
            return f"{obj.file_size / 1024:.1f} KB"
        else:
            return f"{obj.file_size / (1024 * 1024):.1f} MB"
    file_size_display.short_description = 'Size'


@admin.register(PolicyImpactAssessment)
class PolicyImpactAssessmentAdmin(admin.ModelAdmin):
    list_display = [
        'document', 'equality_impact_badge', 'quality_impact_badge',
        'overall_rating', 'assessed_by', 'assessed_date', 'approval_status'
    ]
    list_filter = ['equality_impact_level', 'quality_impact_level', 'consultation_completed']
    search_fields = ['document__title', 'document__document_code']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Document', {
            'fields': ('document',)
        }),
        ('Equality Impact Assessment', {
            'fields': (
                'equality_impact_level',
                'equality_analysis',
                'mitigation_actions',
            )
        }),
        ('Quality Impact Assessment', {
            'fields': (
                'quality_impact_level',
                'quality_analysis',
                'quality_measures',
            )
        }),
        ('Risk & Resources', {
            'fields': (
                'implementation_risks',
                'resource_requirements',
            ),
            'classes': ['collapse']
        }),
        ('Stakeholder Consultation', {
            'fields': (
                'consultation_completed',
                'consultation_summary',
            )
        }),
        ('Sign-Off', {
            'fields': (
                ('assessed_by', 'assessed_date'),
                ('approved_by', 'approved_date'),
            )
        }),
    )
    
    def equality_impact_badge(self, obj):
        colors = {
            'POSITIVE': 'success',
            'NEUTRAL': 'info',
            'NEGATIVE': 'danger',
            'UNKNOWN': 'secondary',
        }
        color = colors.get(obj.equality_impact_level, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_equality_impact_level_display()
        )
    equality_impact_badge.short_description = 'Equality Impact'
    
    def quality_impact_badge(self, obj):
        colors = {
            'POSITIVE': 'success',
            'NEUTRAL': 'info',
            'NEGATIVE': 'danger',
            'UNKNOWN': 'secondary',
        }
        color = colors.get(obj.quality_impact_level, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_quality_impact_level_display()
        )
    quality_impact_badge.short_description = 'Quality Impact'
    
    def overall_rating(self, obj):
        rating = obj.overall_impact_rating()
        colors = {
            'POSITIVE': 'success',
            'NEUTRAL': 'info',
            'NEGATIVE': 'danger',
            'UNKNOWN': 'secondary',
        }
        color = colors.get(rating, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            rating
        )
    overall_rating.short_description = 'Overall Rating'
    
    def approval_status(self, obj):
        if obj.approved_by and obj.approved_date:
            return format_html(
                '<span class="badge badge-success" title="Approved by {} on {}">✓ APPROVED</span>',
                obj.approved_by.get_full_name(),
                obj.approved_date
            )
        else:
            return format_html('<span class="badge badge-warning">⏳ PENDING</span>')
    approval_status.short_description = 'Approval'
