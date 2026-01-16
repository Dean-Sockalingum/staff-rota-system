"""
TQM Module 5: Policies & Procedures Management
==============================================

Complete policy lifecycle management for Scottish care homes,
ensuring regulatory compliance with Care Inspectorate and CQC requirements.

Models:
- Policy: Core policy documents with metadata
- PolicyVersion: Complete version control and change tracking
- PolicyAcknowledgement: Digital staff sign-off with audit trail
- PolicyReview: Scheduled review process management
- Procedure: Detailed step-by-step procedures linked to policies
- ProcedureStep: Granular procedure steps with critical points
- PolicyComplianceCheck: Policy compliance auditing
- AuditTrail: Complete audit log of all policy changes
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


class Policy(models.Model):
    """
    Core policy document with regulatory framework mapping.
    Supports full lifecycle from draft through active to archived.
    """
    
    CATEGORY_CHOICES = [
        ('clinical', 'Clinical Care'),
        ('operational', 'Operational'),
        ('hr', 'Human Resources'),
        ('health_safety', 'Health & Safety'),
        ('safeguarding', 'Safeguarding'),
        ('infection_control', 'Infection Prevention & Control'),
        ('quality', 'Quality Assurance'),
        ('regulatory', 'Regulatory Compliance'),
        ('finance', 'Finance & Business'),
        ('it_data', 'IT & Data Protection'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('superseded', 'Superseded'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    policy_number = models.CharField(max_length=50, unique=True, help_text="Unique policy identifier (e.g., POL-001)")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    
    # Dates and Review Cycle
    effective_date = models.DateField(help_text="Date policy becomes effective")
    next_review_date = models.DateField(help_text="Date policy must be reviewed")
    review_frequency_months = models.PositiveIntegerField(default=12, validators=[MinValueValidator(1), MaxValueValidator(60)], help_text="Review frequency in months")
    
    # Status and Version
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    version = models.DecimalField(max_digits=4, decimal_places=1, default=1.0, help_text="Current version number (e.g., 1.0, 2.5)")
    
    # Content
    summary = models.TextField(help_text="Brief summary of policy scope and purpose")
    keywords = models.CharField(max_length=500, blank=True, help_text="Comma-separated keywords for search")
    regulatory_framework = models.TextField(blank=True, help_text="CQC/Care Inspectorate references and regulatory requirements")
    
    # Ownership and Department
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_policies', help_text="Policy author/owner")
    department = models.CharField(max_length=100, blank=True, help_text="Responsible department")
    
    # File Storage
    file_path = models.FileField(upload_to='policies/', blank=True, help_text="Policy document file (PDF/Word)")
    
    # Mandatory Training
    is_mandatory = models.BooleanField(default=True, help_text="Requires staff acknowledgement")
    
    # Metadata
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Policy'
        verbose_name_plural = 'Policies'
        ordering = ['-effective_date', 'policy_number']
        indexes = [
            models.Index(fields=['policy_number']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['next_review_date']),
        ]
    
    def __str__(self):
        return f"{self.policy_number}: {self.title} (v{self.version})"
    
    def get_absolute_url(self):
        return reverse('policies_procedures:policy_detail', kwargs={'pk': self.pk})
    
    @property
    def is_overdue_review(self):
        """Check if policy review is overdue"""
        return self.next_review_date < timezone.now().date() if self.next_review_date else False
    
    @property
    def days_until_review(self):
        """Days until next review (negative if overdue)"""
        if self.next_review_date:
            return (self.next_review_date - timezone.now().date()).days
        return None
    
    @property
    def acknowledgement_rate(self):
        """Percentage of staff who have acknowledged this policy"""
        total_acknowledgements = self.acknowledgements.filter(is_overdue=False).count()
        # In production, calculate against total staff count
        return total_acknowledgements


class PolicyVersion(models.Model):
    """
    Complete version control for policy documents.
    Maintains history of all changes with approval workflow.
    """
    
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='versions')
    version_number = models.DecimalField(max_digits=4, decimal_places=1, help_text="Version number (e.g., 1.0, 2.5)")
    
    # Change Information
    change_summary = models.TextField(help_text="Summary of changes in this version")
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_policy_versions')
    
    # File Storage
    file_path = models.FileField(upload_to='policies/versions/', help_text="Archived version of policy document")
    
    # Version Status
    is_current = models.BooleanField(default=False, help_text="Is this the current active version?")
    
    # Approval Workflow
    approval_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_policy_versions')
    
    class Meta:
        verbose_name = 'Policy Version'
        verbose_name_plural = 'Policy Versions'
        ordering = ['-version_number']
        unique_together = [['policy', 'version_number']]
    
    def __str__(self):
        return f"{self.policy.policy_number} v{self.version_number}"


class PolicyAcknowledgement(models.Model):
    """
    Digital acknowledgement tracking for policy compliance.
    Creates audit trail for Care Inspectorate/CQC evidence.
    """
    
    ACKNOWLEDGEMENT_METHOD_CHOICES = [
        ('digital', 'Digital Signature'),
        ('paper', 'Paper Form'),
        ('verbal', 'Verbal Confirmation'),
        ('training', 'Training Session'),
    ]
    
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='acknowledgements')
    staff_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='policy_acknowledgements')
    
    # Acknowledgement Details
    acknowledged_date = models.DateTimeField(auto_now_add=True)
    signature = models.CharField(max_length=200, help_text="Digital signature or name")
    ip_address = models.GenericIPAddressField(help_text="IP address for audit trail")
    acknowledgement_method = models.CharField(max_length=20, choices=ACKNOWLEDGEMENT_METHOD_CHOICES, default='digital')
    
    # Additional Information
    comments = models.TextField(blank=True, help_text="Staff comments or questions")
    is_overdue = models.BooleanField(default=False, help_text="Acknowledgement was required but not completed on time")
    
    class Meta:
        verbose_name = 'Policy Acknowledgement'
        verbose_name_plural = 'Policy Acknowledgements'
        ordering = ['-acknowledged_date']
        unique_together = [['policy', 'staff_member']]
        indexes = [
            models.Index(fields=['policy', 'acknowledged_date']),
            models.Index(fields=['staff_member', 'acknowledged_date']),
        ]
    
    def __str__(self):
        return f"{self.staff_member.get_full_name()} acknowledged {self.policy.policy_number} on {self.acknowledged_date.strftime('%Y-%m-%d')}"


class PolicyReview(models.Model):
    """
    Scheduled policy review tracking.
    Ensures policies remain current and compliant.
    """
    
    REVIEW_OUTCOME_CHOICES = [
        ('no_changes', 'No Changes Required'),
        ('minor_updates', 'Minor Updates'),
        ('major_revision', 'Major Revision Required'),
        ('retire', 'Retire Policy'),
    ]
    
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='policy_reviews')
    
    # Review Information
    review_date = models.DateField()
    review_outcome = models.CharField(max_length=20, choices=REVIEW_OUTCOME_CHOICES)
    recommendations = models.TextField(help_text="Reviewer recommendations and findings")
    next_review_date = models.DateField(help_text="Recommended next review date")
    
    # Completion Status
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_policy_reviews')
    completion_date = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Policy Review'
        verbose_name_plural = 'Policy Reviews'
        ordering = ['-review_date']
    
    def __str__(self):
        return f"Review of {self.policy.policy_number} on {self.review_date}"
    
    @property
    def is_completed(self):
        return self.completion_date is not None


class Procedure(models.Model):
    """
    Detailed step-by-step procedures linked to policies.
    Provides operational guidance for policy implementation.
    """
    
    title = models.CharField(max_length=200)
    procedure_number = models.CharField(max_length=50, unique=True, help_text="Unique procedure identifier (e.g., PROC-001)")
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='procedures', help_text="Parent policy")
    
    # Procedure Content
    steps = models.TextField(help_text="Detailed step-by-step instructions")
    equipment_required = models.TextField(blank=True, help_text="Equipment or materials needed")
    safety_notes = models.TextField(blank=True, help_text="Safety precautions and warnings")
    
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Procedure'
        verbose_name_plural = 'Procedures'
        ordering = ['procedure_number']
    
    def __str__(self):
        return f"{self.procedure_number}: {self.title}"


class ProcedureStep(models.Model):
    """
    Granular procedure steps with critical control points.
    Enables detailed workflow tracking and compliance evidence.
    """
    
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name='detailed_steps')
    step_number = models.PositiveIntegerField(help_text="Step sequence number")
    description = models.TextField(help_text="Detailed step description")
    
    # Critical Control Points
    critical_point = models.BooleanField(default=False, help_text="Critical control point requiring verification")
    evidence_required = models.CharField(max_length=200, blank=True, help_text="Evidence or documentation required")
    
    class Meta:
        verbose_name = 'Procedure Step'
        verbose_name_plural = 'Procedure Steps'
        ordering = ['procedure', 'step_number']
        unique_together = [['procedure', 'step_number']]
    
    def __str__(self):
        return f"{self.procedure.procedure_number} - Step {self.step_number}"


class PolicyComplianceCheck(models.Model):
    """
    Policy compliance auditing and monitoring.
    Supports Care Inspectorate/CQC inspection readiness.
    """
    
    COMPLIANCE_STATUS_CHOICES = [
        ('fully_compliant', 'Fully Compliant'),
        ('partially_compliant', 'Partially Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('not_applicable', 'Not Applicable'),
    ]
    
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='compliance_checks')
    check_date = models.DateField()
    checker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='policy_compliance_checks')
    
    # Compliance Results
    compliance_status = models.CharField(max_length=25, choices=COMPLIANCE_STATUS_CHOICES)
    findings = models.TextField(help_text="Detailed compliance findings")
    actions_required = models.TextField(blank=True, help_text="Actions needed to achieve compliance")
    
    # Action Tracking
    due_date = models.DateField(null=True, blank=True, help_text="Date actions must be completed")
    completed = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Policy Compliance Check'
        verbose_name_plural = 'Policy Compliance Checks'
        ordering = ['-check_date']
    
    def __str__(self):
        return f"Compliance check for {self.policy.policy_number} on {self.check_date}"
    
    @property
    def is_overdue(self):
        if self.due_date and not self.completed:
            return self.due_date < timezone.now().date()
        return False


class AuditTrail(models.Model):
    """
    Complete audit trail of all policy changes.
    Maintains regulatory compliance evidence.
    """
    
    ACTION_TYPE_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('reviewed', 'Reviewed'),
        ('acknowledged', 'Acknowledged'),
        ('archived', 'Archived'),
        ('superseded', 'Superseded'),
        ('compliance_check', 'Compliance Check'),
    ]
    
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='audit_trail')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Change Details
    details = models.TextField(help_text="Description of action performed")
    previous_values = models.JSONField(null=True, blank=True, help_text="Previous field values (for updates)")
    
    class Meta:
        verbose_name = 'Audit Trail Entry'
        verbose_name_plural = 'Audit Trail'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['policy', '-timestamp']),
            models.Index(fields=['action_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action_type} by {self.performed_by} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
