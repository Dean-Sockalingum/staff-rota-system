"""
Risk Management Models

Comprehensive risk management system for Scottish care homes.
Supports risk identification, assessment, mitigation planning, and monitoring
in compliance with Healthcare Improvement Scotland (HIS), Care Inspectorate,
and Scottish Social Services Council (SSSC) requirements.

Key Features:
- Risk register with hierarchical categories
- 5x5 risk matrix (likelihood × impact)
- Residual vs inherent risk calculation
- Mitigation planning and tracking
- Risk review cycles and escalation
- Integration with incident management
- Regulatory compliance tracking
- Chart.js dashboards
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta


class RiskCategory(models.Model):
    """
    Hierarchical risk categories for Scottish care homes.
    
    Categories align with Care Inspectorate Quality Framework:
    - Clinical & Care Quality
    - Health & Safety
    - Safeguarding
    - Infection Prevention & Control
    - Staffing & Workforce
    - Environmental & Facilities
    - Financial & Business
    - Regulatory & Compliance
    - Reputational
    """
    
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    color = models.CharField(
        max_length=7,
        default='#6c757d',
        help_text='Hex color for dashboards (e.g., #dc3545)'
    )
    is_active = models.BooleanField(default=True)
    
    # Scottish regulatory alignment
    his_domain = models.CharField(
        max_length=100,
        blank=True,
        help_text='Healthcare Improvement Scotland domain'
    )
    care_inspectorate_theme = models.CharField(
        max_length=100,
        blank=True,
        help_text='Care Inspectorate quality theme'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Risk Categories'
        ordering = ['name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def get_full_path(self):
        """Get full hierarchical path (e.g., 'Clinical > Medication Management')"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class RiskRegister(models.Model):
    """
    Main risk register entry for identified risks.
    
    Follows Scottish Care risk management framework.
    Each risk has:
    - Inherent risk (before controls)
    - Residual risk (after controls)
    - Target risk (desired level)
    """
    
    STATUS_CHOICES = [
        ('IDENTIFIED', 'Identified'),
        ('ASSESSED', 'Assessed'),
        ('MITIGATED', 'Mitigation in Progress'),
        ('CONTROLLED', 'Controlled'),
        ('ACCEPTED', 'Accepted'),
        ('TRANSFERRED', 'Transferred'),
        ('CLOSED', 'Closed'),
        ('ESCALATED', 'Escalated'),
    ]
    
    LIKELIHOOD_CHOICES = [
        (1, 'Rare (1) - <5% chance'),
        (2, 'Unlikely (2) - 5-25% chance'),
        (3, 'Possible (3) - 25-50% chance'),
        (4, 'Likely (4) - 50-75% chance'),
        (5, 'Almost Certain (5) - >75% chance'),
    ]
    
    IMPACT_CHOICES = [
        (1, 'Negligible (1) - Minor injury/disruption'),
        (2, 'Minor (2) - First aid/short-term effects'),
        (3, 'Moderate (3) - Medical treatment/moderate harm'),
        (4, 'Major (4) - Severe harm/long-term effects'),
        (5, 'Catastrophic (5) - Death/permanent disability'),
    ]
    
    # Basic Information
    risk_id = models.CharField(max_length=20, unique=True, editable=False)
    title = models.CharField(max_length=300)
    description = models.TextField(help_text='Detailed description of the risk')
    category = models.ForeignKey(RiskCategory, on_delete=models.PROTECT)
    
    # Care Home Context
    care_home = models.ForeignKey(
        'scheduling.CareHome',
        on_delete=models.CASCADE,
        related_name='risks'
    )
    affected_area = models.CharField(
        max_length=200,
        blank=True,
        help_text='Specific unit, department, or area affected'
    )
    
    # Risk Assessment - Inherent (before controls)
    inherent_likelihood = models.IntegerField(
        choices=LIKELIHOOD_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    inherent_impact = models.IntegerField(
        choices=IMPACT_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    inherent_score = models.IntegerField(editable=False)  # likelihood × impact
    
    # Current Controls
    current_controls = models.TextField(
        help_text='Existing controls and measures in place'
    )
    control_effectiveness = models.IntegerField(
        choices=[
            (1, 'Ineffective'),
            (2, 'Partially Effective'),
            (3, 'Mostly Effective'),
            (4, 'Fully Effective'),
        ],
        default=2
    )
    
    # Risk Assessment - Residual (after current controls)
    residual_likelihood = models.IntegerField(
        choices=LIKELIHOOD_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    residual_impact = models.IntegerField(
        choices=IMPACT_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    residual_score = models.IntegerField(editable=False)  # likelihood × impact
    
    # Target Risk (desired level after mitigation)
    target_likelihood = models.IntegerField(
        choices=LIKELIHOOD_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    target_impact = models.IntegerField(
        choices=IMPACT_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    target_score = models.IntegerField(editable=False, null=True, blank=True)
    
    # Ownership & Accountability
    risk_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_risks',
        help_text='Person responsible for managing this risk'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_risks',
        help_text='Person assigned to implement mitigations'
    )
    
    # Status & Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IDENTIFIED')
    priority = models.CharField(
        max_length=20,
        editable=False,
        help_text='Auto-calculated from residual score'
    )
    
    # Review & Monitoring
    last_reviewed = models.DateField(null=True, blank=True)
    next_review_date = models.DateField()
    review_frequency = models.CharField(
        max_length=20,
        choices=[
            ('DAILY', 'Daily'),
            ('WEEKLY', 'Weekly'),
            ('MONTHLY', 'Monthly'),
            ('QUARTERLY', 'Quarterly'),
            ('BIANNUALLY', 'Bi-Annually'),
            ('ANNUALLY', 'Annually'),
        ],
        default='MONTHLY'
    )
    
    # Integration with Incidents
    related_incidents = models.ManyToManyField(
        'scheduling.IncidentReport',
        blank=True,
        related_name='risks',
        help_text='Incidents that led to risk identification'
    )
    
    # Regulatory Compliance
    regulatory_requirement = models.TextField(
        blank=True,
        help_text='Scottish regulatory requirements (HIS, Care Inspectorate, SSSC)'
    )
    compliance_deadline = models.DateField(null=True, blank=True)
    
    # Audit Trail
    identified_date = models.DateField(default=timezone.now)
    identified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='identified_risks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional Context
    notes = models.TextField(blank=True)
    is_escalated = models.BooleanField(default=False)
    escalation_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-residual_score', 'next_review_date']
        indexes = [
            models.Index(fields=['care_home', 'status']),
            models.Index(fields=['residual_score']),
            models.Index(fields=['next_review_date']),
        ]
    
    def __str__(self):
        return f"{self.risk_id}: {self.title}"
    
    def save(self, *args, **kwargs):
        """Calculate scores and priority on save"""
        # Generate risk ID if new
        if not self.risk_id:
            year = timezone.now().year
            count = RiskRegister.objects.filter(
                care_home=self.care_home,
                created_at__year=year
            ).count() + 1
            self.risk_id = f"{self.care_home.code}-R{year}-{count:03d}"
        
        # Calculate scores
        self.inherent_score = self.inherent_likelihood * self.inherent_impact
        self.residual_score = self.residual_likelihood * self.residual_impact
        
        if self.target_likelihood and self.target_impact:
            self.target_score = self.target_likelihood * self.target_impact
        
        # Calculate priority based on residual score (5x5 matrix)
        if self.residual_score >= 15:
            self.priority = 'CRITICAL'  # Red zone
        elif self.residual_score >= 10:
            self.priority = 'HIGH'  # Orange zone
        elif self.residual_score >= 6:
            self.priority = 'MEDIUM'  # Yellow zone
        else:
            self.priority = 'LOW'  # Green zone
        
        super().save(*args, **kwargs)
    
    def get_risk_level(self):
        """Get human-readable risk level"""
        score = self.residual_score
        if score >= 15:
            return 'Critical (15-25)'
        elif score >= 10:
            return 'High (10-14)'
        elif score >= 6:
            return 'Medium (6-9)'
        else:
            return 'Low (1-5)'
    
    def is_overdue_review(self):
        """Check if risk review is overdue"""
        return timezone.now().date() > self.next_review_date
    
    def days_until_review(self):
        """Days until next review (negative if overdue)"""
        delta = self.next_review_date - timezone.now().date()
        return delta.days
    
    def risk_reduction_percentage(self):
        """Calculate percentage reduction from inherent to residual"""
        if self.inherent_score == 0:
            return 0
        reduction = ((self.inherent_score - self.residual_score) / self.inherent_score) * 100
        return max(0, reduction)  # Don't show negative reduction
    
    def mitigation_gap(self):
        """Gap between residual and target risk"""
        if self.target_score:
            return self.residual_score - self.target_score
        return 0


class RiskMitigation(models.Model):
    """
    Mitigation actions to reduce risk likelihood or impact.
    
    Follows Plan-Do-Study-Act (PDSA) improvement methodology.
    Links to PDSA projects for quality improvement integration.
    """
    
    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('ON_HOLD', 'On Hold'),
        ('CANCELLED', 'Cancelled'),
        ('OVERDUE', 'Overdue'),
    ]
    
    PRIORITY_CHOICES = [
        ('IMMEDIATE', 'Immediate'),
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]
    
    TYPE_CHOICES = [
        ('ELIMINATE', 'Eliminate - Remove the hazard'),
        ('SUBSTITUTE', 'Substitute - Replace with safer alternative'),
        ('ENGINEERING', 'Engineering Controls - Physical changes'),
        ('ADMINISTRATIVE', 'Administrative - Policies and procedures'),
        ('PPE', 'PPE - Personal protective equipment'),
    ]
    
    # Link to Risk
    risk = models.ForeignKey(RiskRegister, on_delete=models.CASCADE, related_name='mitigations')
    
    # Mitigation Details
    action = models.CharField(max_length=300, help_text='Specific mitigation action')
    description = models.TextField(help_text='Detailed description of how to implement')
    mitigation_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Expected Impact
    expected_likelihood_reduction = models.IntegerField(
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        help_text='Expected reduction in likelihood (1-5)'
    )
    expected_impact_reduction = models.IntegerField(
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        help_text='Expected reduction in impact (1-5)'
    )
    
    # Implementation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='mitigation_tasks'
    )
    
    # Timeline
    start_date = models.DateField(null=True, blank=True)
    target_completion_date = models.DateField()
    actual_completion_date = models.DateField(null=True, blank=True)
    
    # Resources
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Estimated cost in GBP'
    )
    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Actual cost in GBP'
    )
    resources_required = models.TextField(blank=True)
    
    # Effectiveness Tracking
    effectiveness_rating = models.IntegerField(
        choices=[
            (1, 'Ineffective'),
            (2, 'Partially Effective'),
            (3, 'Mostly Effective'),
            (4, 'Fully Effective'),
        ],
        null=True,
        blank=True,
        help_text='Post-implementation effectiveness'
    )
    effectiveness_notes = models.TextField(blank=True)
    
    # Integration with Quality Improvement
    linked_pdsa_project = models.ForeignKey(
        'quality_audits.PDSAProject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='risk_mitigations',
        help_text='PDSA improvement project'
    )
    
    # Compliance
    regulatory_requirement = models.BooleanField(
        default=False,
        help_text='Required by Scottish regulations'
    )
    
    # Audit Trail
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_mitigations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Progress Tracking
    completion_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Completion percentage (0-100%)'
    )
    progress_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['priority', 'target_completion_date']
        indexes = [
            models.Index(fields=['risk', 'status']),
            models.Index(fields=['target_completion_date']),
        ]
    
    def __str__(self):
        return f"{self.risk.risk_id} - {self.action}"
    
    def is_overdue(self):
        """Check if mitigation is overdue"""
        if self.status in ['COMPLETED', 'CANCELLED']:
            return False
        return timezone.now().date() > self.target_completion_date
    
    def days_remaining(self):
        """Days until target completion (negative if overdue)"""
        delta = self.target_completion_date - timezone.now().date()
        return delta.days
    
    def duration_days(self):
        """Duration from start to completion"""
        if self.start_date and self.actual_completion_date:
            return (self.actual_completion_date - self.start_date).days
        return None
    
    def cost_variance(self):
        """Difference between estimated and actual cost"""
        if self.estimated_cost and self.actual_cost:
            return self.actual_cost - self.estimated_cost
        return None


class RiskReview(models.Model):
    """
    Periodic risk reviews and reassessments.
    
    Ensures risks are monitored and updated regularly.
    Tracks changes in risk level over time.
    """
    
    DECISION_CHOICES = [
        ('CONTINUE', 'Continue Monitoring'),
        ('ESCALATE', 'Escalate'),
        ('DE_ESCALATE', 'De-Escalate'),
        ('CLOSE', 'Close Risk'),
        ('ACCEPT', 'Accept Risk'),
        ('TRANSFER', 'Transfer Risk'),
        ('ADDITIONAL_MITIGATION', 'Additional Mitigation Required'),
    ]
    
    # Review Details
    risk = models.ForeignKey(RiskRegister, on_delete=models.CASCADE, related_name='reviews')
    review_date = models.DateField(default=timezone.now)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    
    # Reassessment
    reassessed_likelihood = models.IntegerField(
        choices=RiskRegister.LIKELIHOOD_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    reassessed_impact = models.IntegerField(
        choices=RiskRegister.IMPACT_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    reassessed_score = models.IntegerField(editable=False)
    
    # Control Effectiveness
    controls_effective = models.BooleanField(
        default=True,
        help_text='Are current controls effective?'
    )
    control_gaps = models.TextField(
        blank=True,
        help_text='Identified gaps in current controls'
    )
    
    # New Mitigations
    new_mitigations_required = models.BooleanField(default=False)
    recommended_actions = models.TextField(blank=True)
    
    # Decision
    decision = models.CharField(max_length=30, choices=DECISION_CHOICES)
    decision_rationale = models.TextField()
    
    # Next Steps
    next_review_date = models.DateField()
    follow_up_actions = models.TextField(blank=True)
    
    # Context
    incidents_since_last_review = models.ManyToManyField(
        'scheduling.IncidentReport',
        blank=True,
        help_text='Related incidents since last review'
    )
    changes_in_environment = models.TextField(
        blank=True,
        help_text='Changes in care home environment, regulations, or operations'
    )
    
    # Audit Trail
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-review_date']
        indexes = [
            models.Index(fields=['risk', '-review_date']),
        ]
    
    def __str__(self):
        return f"{self.risk.risk_id} Review - {self.review_date}"
    
    def save(self, *args, **kwargs):
        """Calculate reassessed score"""
        self.reassessed_score = self.reassessed_likelihood * self.reassessed_impact
        super().save(*args, **kwargs)
    
    def score_change_from_previous(self):
        """Change in score compared to previous review"""
        previous_reviews = RiskReview.objects.filter(
            risk=self.risk,
            review_date__lt=self.review_date
        ).order_by('-review_date')
        
        if previous_reviews.exists():
            previous = previous_reviews.first()
            return self.reassessed_score - previous.reassessed_score
        return 0
    
    def trend(self):
        """Risk trend (increasing/stable/decreasing)"""
        change = self.score_change_from_previous()
        if change > 0:
            return 'INCREASING'
        elif change < 0:
            return 'DECREASING'
        return 'STABLE'


class RiskTreatmentPlan(models.Model):
    """
    Comprehensive treatment plan for high-priority risks.
    
    Combines multiple mitigations into a coordinated strategy.
    Used for CRITICAL and HIGH priority risks requiring formal plans.
    """
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Plan Details
    risk = models.OneToOneField(
        RiskRegister,
        on_delete=models.CASCADE,
        related_name='treatment_plan'
    )
    plan_name = models.CharField(max_length=300)
    objectives = models.TextField(help_text='Goals of this treatment plan')
    
    # Strategy
    treatment_strategy = models.TextField(
        help_text='Overall strategy to manage this risk'
    )
    success_criteria = models.TextField(
        help_text='How to measure success of this plan'
    )
    
    # Status & Approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='approved_treatment_plans'
    )
    approval_date = models.DateField(null=True, blank=True)
    
    # Timeline
    start_date = models.DateField()
    target_completion_date = models.DateField()
    actual_completion_date = models.DateField(null=True, blank=True)
    
    # Budget
    total_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Total budget in GBP'
    )
    spent_to_date = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Amount spent so far in GBP'
    )
    
    # Team
    plan_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_treatment_plans'
    )
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='treatment_plan_teams'
    )
    
    # Progress
    overall_progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Overall plan completion (0-100%)'
    )
    
    # Monitoring
    last_updated = models.DateField(auto_now=True)
    monthly_updates = models.TextField(
        blank=True,
        help_text='Monthly progress updates'
    )
    
    # Integration
    linked_pdsa_projects = models.ManyToManyField(
        'quality_audits.PDSAProject',
        blank=True,
        related_name='risk_treatment_plans'
    )
    
    # Audit Trail
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_treatment_plans'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Treatment Plan: {self.plan_name}"
    
    def budget_utilization_percentage(self):
        """Percentage of budget spent"""
        if self.total_budget > 0:
            return (self.spent_to_date / self.total_budget) * 100
        return 0
    
    def is_on_schedule(self):
        """Check if plan is on schedule based on progress vs time elapsed"""
        if self.status == 'COMPLETED':
            return True
        
        today = timezone.now().date()
        total_days = (self.target_completion_date - self.start_date).days
        elapsed_days = (today - self.start_date).days
        
        if total_days > 0:
            expected_progress = (elapsed_days / total_days) * 100
            return self.overall_progress >= expected_progress
        return True
    
    def days_remaining(self):
        """Days until target completion"""
        delta = self.target_completion_date - timezone.now().date()
        return delta.days
