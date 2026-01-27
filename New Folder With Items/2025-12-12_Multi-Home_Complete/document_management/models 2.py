"""
TQM Module 5: Document & Policy Management Models

Models for managing organizational documents, policies, procedures with full
version control, compliance mapping, and staff acknowledgement tracking.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
import os

User = get_user_model()


class DocumentCategory(models.Model):
    """Categories for organizing documents and policies."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    order = models.IntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_doc_categories')
    
    class Meta:
        verbose_name_plural = "Document Categories"
        ordering = ['order', 'name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def get_full_path(self):
        """Get full category path for breadcrumbs."""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class Document(models.Model):
    """
    Core document model with version control and compliance tracking.
    Supports policies, procedures, forms, guidance documents, etc.
    """
    
    DOCUMENT_TYPE_CHOICES = [
        ('POLICY', 'Policy'),
        ('PROCEDURE', 'Procedure'),
        ('GUIDANCE', 'Guidance Document'),
        ('FORM', 'Form/Template'),
        ('PROTOCOL', 'Clinical Protocol'),
        ('STANDARD', 'Standard Operating Procedure'),
        ('CHARTER', 'Charter/Strategy'),
        ('MANUAL', 'Manual/Handbook'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('IN_REVIEW', 'In Review'),
        ('APPROVED', 'Approved'),
        ('PUBLISHED', 'Published'),
        ('ARCHIVED', 'Archived'),
        ('SUPERSEDED', 'Superseded'),
    ]
    
    COMPLIANCE_FRAMEWORK_CHOICES = [
        ('HIS', 'Healthcare Improvement Scotland'),
        ('SSSC', 'Scottish Social Services Council'),
        ('CARE_INSP', 'Care Inspectorate'),
        ('GDPR', 'GDPR/Data Protection'),
        ('HEALTH_SAFETY', 'Health & Safety'),
        ('EMPLOYMENT', 'Employment Law'),
        ('CLINICAL', 'Clinical Governance'),
        ('INTERNAL', 'Internal Standards'),
    ]
    
    # Core fields
    title = models.CharField(max_length=255)
    document_code = models.CharField(max_length=50, unique=True, help_text="Unique document identifier (e.g., POL-001)")
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    category = models.ForeignKey(DocumentCategory, on_delete=models.PROTECT, related_name='documents')
    
    # Version control
    version_number = models.CharField(max_length=20, default='1.0', help_text="Version number (e.g., 1.0, 2.1)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Content
    summary = models.TextField(help_text="Brief summary/purpose of document")
    content = models.TextField(blank=True, help_text="Main document content (supports Markdown)")
    file_upload = models.FileField(upload_to='documents/%Y/%m/', blank=True, null=True, help_text="PDF/DOCX file upload")
    
    # Compliance mapping
    compliance_frameworks = models.JSONField(
        default=list,
        help_text="List of compliance frameworks this document addresses",
        blank=True
    )
    regulatory_references = models.TextField(
        blank=True,
        help_text="Specific regulatory requirements/standards addressed"
    )
    
    # Ownership & responsibility
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='owned_documents',
        help_text="Document owner responsible for maintenance"
    )
    approver = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='approved_documents',
        null=True,
        blank=True,
        help_text="Person who approved this version"
    )
    
    # Care home scope
    care_home = models.ForeignKey(
        'scheduling.CareHome',
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True,
        help_text="Leave blank for organization-wide documents"
    )
    
    # Review cycle
    review_frequency_months = models.IntegerField(
        default=12,
        validators=[MinValueValidator(1), MaxValueValidator(60)],
        help_text="How often document should be reviewed (months)"
    )
    next_review_date = models.DateField(null=True, blank=True)
    last_reviewed_date = models.DateField(null=True, blank=True)
    
    # Publishing
    published_date = models.DateField(null=True, blank=True)
    effective_from = models.DateField(null=True, blank=True, help_text="When this version becomes effective")
    supersedes = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='superseded_by_documents',
        help_text="Previous version this document replaces"
    )
    
    # Acknowledgement tracking
    requires_acknowledgement = models.BooleanField(
        default=False,
        help_text="Staff must acknowledge reading this document"
    )
    acknowledgement_due_days = models.IntegerField(
        default=14,
        validators=[MinValueValidator(1), MaxValueValidator(90)],
        help_text="Days staff have to acknowledge after publication"
    )
    
    # Metadata
    keywords = models.CharField(max_length=500, blank=True, help_text="Comma-separated keywords for search")
    attachments_count = models.IntegerField(default=0, editable=False)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_documents')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_documents')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document_code']),
            models.Index(fields=['status']),
            models.Index(fields=['next_review_date']),
        ]
    
    def __str__(self):
        return f"{self.document_code} - {self.title} (v{self.version_number})"
    
    def save(self, *args, **kwargs):
        # Set next review date if not set
        if not self.next_review_date and self.published_date:
            self.next_review_date = self.published_date + timedelta(days=self.review_frequency_months * 30)
        
        super().save(*args, **kwargs)
    
    def is_overdue_for_review(self):
        """Check if document review is overdue."""
        if self.next_review_date:
            return timezone.now().date() > self.next_review_date
        return False
    
    def days_until_review(self):
        """Calculate days until next review (negative if overdue)."""
        if self.next_review_date:
            delta = self.next_review_date - timezone.now().date()
            return delta.days
        return None
    
    def get_review_status(self):
        """Get color-coded review status."""
        days = self.days_until_review()
        if days is None:
            return 'unknown'
        elif days < 0:
            return 'overdue'
        elif days <= 30:
            return 'due_soon'
        else:
            return 'current'
    
    def acknowledgement_rate(self):
        """Calculate percentage of staff who have acknowledged."""
        if not self.requires_acknowledgement or self.status != 'PUBLISHED':
            return None
        
        total_required = self.acknowledgement_requirements.count()
        if total_required == 0:
            return 0
        
        acknowledged = self.acknowledgement_requirements.filter(acknowledged_at__isnull=False).count()
        return round((acknowledged / total_required) * 100, 1)
    
    def get_file_extension(self):
        """Get file extension from uploaded file."""
        if self.file_upload:
            return os.path.splitext(self.file_upload.name)[1].lower()
        return None


class DocumentVersion(models.Model):
    """
    Version history for documents. Each edit creates a new version entry.
    """
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version_number = models.CharField(max_length=20)
    
    # Snapshot of document at this version
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    file_upload = models.FileField(upload_to='document_versions/%Y/%m/', blank=True, null=True)
    summary = models.TextField(blank=True)
    
    # Change tracking
    change_summary = models.TextField(help_text="Summary of changes in this version")
    change_type = models.CharField(
        max_length=20,
        choices=[
            ('MAJOR', 'Major Revision'),
            ('MINOR', 'Minor Update'),
            ('CORRECTION', 'Correction/Fix'),
            ('REVIEW', 'Scheduled Review'),
        ],
        default='MINOR'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file_size = models.IntegerField(null=True, blank=True, help_text="File size in bytes")
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['document', 'version_number']
    
    def __str__(self):
        return f"{self.document.document_code} v{self.version_number}"


class DocumentReview(models.Model):
    """
    Scheduled and ad-hoc document reviews with reviewer feedback.
    """
    
    REVIEW_TYPE_CHOICES = [
        ('SCHEDULED', 'Scheduled Review'),
        ('AD_HOC', 'Ad-Hoc Review'),
        ('POST_INCIDENT', 'Post-Incident Review'),
        ('REGULATORY', 'Regulatory Requirement'),
    ]
    
    REVIEW_OUTCOME_CHOICES = [
        ('NO_CHANGE', 'No Changes Required'),
        ('MINOR_UPDATE', 'Minor Updates Required'),
        ('MAJOR_REVISION', 'Major Revision Required'),
        ('RETIRE', 'Recommend Retirement'),
    ]
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='reviews')
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPE_CHOICES)
    
    # Scheduling
    due_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    
    # Reviewer assignment
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='document_reviews')
    additional_reviewers = models.ManyToManyField(
        User,
        blank=True,
        related_name='additional_document_reviews',
        help_text="Additional stakeholders for review"
    )
    
    # Review findings
    outcome = models.CharField(max_length=20, choices=REVIEW_OUTCOME_CHOICES, blank=True)
    findings = models.TextField(blank=True, help_text="Review findings and recommendations")
    action_items = models.TextField(blank=True, help_text="Required actions from review")
    
    # Compliance check
    compliance_verified = models.BooleanField(default=False, help_text="Regulatory compliance verified")
    compliance_notes = models.TextField(blank=True)
    
    # Status
    is_complete = models.BooleanField(default=False)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_reviews')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.document.document_code} Review - {self.due_date}"
    
    def is_overdue(self):
        """Check if review is overdue."""
        if not self.is_complete and self.due_date:
            return timezone.now().date() > self.due_date
        return False
    
    def days_overdue(self):
        """Calculate days overdue (negative if not yet due)."""
        if self.due_date:
            delta = timezone.now().date() - self.due_date
            return delta.days
        return None


class StaffAcknowledgement(models.Model):
    """
    Track staff acknowledgement of reading and understanding documents/policies.
    """
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='acknowledgement_requirements')
    staff_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_acknowledgements')
    
    # Assignment
    required_by = models.DateField(help_text="Date by which acknowledgement is required")
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_acknowledgements'
    )
    
    # Acknowledgement
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledgement_method = models.CharField(
        max_length=20,
        choices=[
            ('ONLINE', 'Online Portal'),
            ('PAPER', 'Paper Signature'),
            ('EMAIL', 'Email Confirmation'),
            ('MEETING', 'Team Meeting'),
        ],
        blank=True
    )
    
    # Comprehension check (optional)
    quiz_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Quiz score percentage if comprehension test required"
    )
    
    # Notes
    notes = models.TextField(blank=True, help_text="Any comments or questions from staff member")
    
    # Reminders
    reminder_sent_count = models.IntegerField(default=0, editable=False)
    last_reminder_sent = models.DateTimeField(null=True, blank=True, editable=False)
    
    class Meta:
        unique_together = ['document', 'staff_member']
        ordering = ['-required_by']
        indexes = [
            models.Index(fields=['required_by']),
            models.Index(fields=['acknowledged_at']),
        ]
    
    def __str__(self):
        return f"{self.staff_member.get_full_name()} - {self.document.document_code}"
    
    def is_overdue(self):
        """Check if acknowledgement is overdue."""
        if not self.acknowledged_at and self.required_by:
            return timezone.now().date() > self.required_by
        return False
    
    def days_overdue(self):
        """Calculate days overdue (negative if not yet due)."""
        if not self.acknowledged_at and self.required_by:
            delta = timezone.now().date() - self.required_by
            return delta.days
        return None
    
    def acknowledge(self, method='ONLINE', quiz_score=None, notes=''):
        """Mark as acknowledged."""
        self.acknowledged_at = timezone.now()
        self.acknowledgement_method = method
        if quiz_score is not None:
            self.quiz_score = quiz_score
        if notes:
            self.notes = notes
        self.save()


class DocumentAttachment(models.Model):
    """
    Supporting files/attachments for documents (forms, appendices, etc.).
    """
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='attachments')
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='document_attachments/%Y/%m/')
    file_type = models.CharField(max_length=50, blank=True, help_text="e.g., PDF, DOCX, XLSX")
    file_size = models.IntegerField(help_text="File size in bytes")
    
    order = models.IntegerField(default=0, help_text="Display order")
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['order', 'title']
    
    def __str__(self):
        return f"{self.document.document_code} - {self.title}"
    
    def save(self, *args, **kwargs):
        # Extract file type from extension
        if self.file:
            ext = os.path.splitext(self.file.name)[1].upper().replace('.', '')
            self.file_type = ext
        
        super().save(*args, **kwargs)
        
        # Update document attachment count
        self.document.attachments_count = self.document.attachments.count()
        self.document.save(update_fields=['attachments_count'])


class PolicyImpactAssessment(models.Model):
    """
    Equality and Quality Impact Assessment for policies/procedures.
    Required for major policy changes in Scottish care homes.
    """
    
    IMPACT_LEVEL_CHOICES = [
        ('POSITIVE', 'Positive Impact'),
        ('NEUTRAL', 'Neutral/No Impact'),
        ('NEGATIVE', 'Negative Impact (requires mitigation)'),
        ('UNKNOWN', 'Unknown/Requires Further Analysis'),
    ]
    
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name='impact_assessment',
        limit_choices_to={'document_type__in': ['POLICY', 'PROCEDURE']}
    )
    
    # Equality Impact Assessment
    equality_impact_level = models.CharField(max_length=20, choices=IMPACT_LEVEL_CHOICES)
    equality_analysis = models.TextField(
        help_text="Analysis of impact on protected characteristics (age, disability, race, etc.)"
    )
    mitigation_actions = models.TextField(
        blank=True,
        help_text="Actions to mitigate negative equality impacts"
    )
    
    # Quality Impact Assessment
    quality_impact_level = models.CharField(max_length=20, choices=IMPACT_LEVEL_CHOICES)
    quality_analysis = models.TextField(
        help_text="Analysis of impact on care quality and resident outcomes"
    )
    quality_measures = models.TextField(
        blank=True,
        help_text="How quality impact will be measured/monitored"
    )
    
    # Risk Assessment
    implementation_risks = models.TextField(
        blank=True,
        help_text="Risks identified during implementation"
    )
    resource_requirements = models.TextField(
        blank=True,
        help_text="Resources needed for successful implementation"
    )
    
    # Stakeholder Consultation
    consultation_completed = models.BooleanField(default=False)
    consultation_summary = models.TextField(
        blank=True,
        help_text="Summary of stakeholder feedback"
    )
    
    # Sign-off
    assessed_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='impact_assessments')
    assessed_date = models.DateField()
    approved_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='approved_impact_assessments'
    )
    approved_date = models.DateField(null=True, blank=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Policy Impact Assessment"
    
    def __str__(self):
        return f"Impact Assessment - {self.document.document_code}"
    
    def overall_impact_rating(self):
        """Calculate overall impact rating based on equality and quality impacts."""
        impact_scores = {
            'POSITIVE': 2,
            'NEUTRAL': 1,
            'NEGATIVE': -1,
            'UNKNOWN': 0,
        }
        
        equality_score = impact_scores.get(self.equality_impact_level, 0)
        quality_score = impact_scores.get(self.quality_impact_level, 0)
        
        avg_score = (equality_score + quality_score) / 2
        
        if avg_score > 1:
            return 'POSITIVE'
        elif avg_score > 0:
            return 'NEUTRAL'
        elif avg_score < 0:
            return 'NEGATIVE'
        else:
            return 'UNKNOWN'
