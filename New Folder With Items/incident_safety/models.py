"""
TQM Module 2: Incident & Safety Management

Database models for comprehensive incident reporting, investigation, and learning.
Aligned with:
- Care Inspectorate Scotland requirements
- Scottish Patient Safety Programme (SPSP)
- Duty of Candour (Scotland) Act 2016
- Health Improvement Scotland (HIS) QMS
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from scheduling.models import CareHome, IncidentReport, Resident

User = get_user_model()


class RootCauseAnalysis(models.Model):
    """
    Root Cause Analysis (RCA) for incidents using 5 Whys and Fishbone methodology.
    Supports SPSP approach to incident investigation.
    """
    
    ANALYSIS_METHOD_CHOICES = [
        ('5_WHYS', '5 Whys'),
        ('FISHBONE', 'Fishbone Diagram'),
        ('SWARM', 'SWARM Analysis'),
        ('TIMELINE', 'Timeline Analysis'),
        ('BARRIER', 'Barrier Analysis'),
    ]
    
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected - Needs Revision'),
    ]
    
    # Link to original incident
    incident = models.OneToOneField(
        IncidentReport, 
        on_delete=models.CASCADE, 
        related_name='root_cause_analysis'
    )
    
    # Analysis Details
    analysis_method = models.CharField(
        max_length=20, 
        choices=ANALYSIS_METHOD_CHOICES,
        default='5_WHYS'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='IN_PROGRESS'
    )
    
    # Team
    lead_investigator = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='rca_investigations_led'
    )
    investigation_team = models.ManyToManyField(
        User, 
        blank=True,
        related_name='rca_investigations_participated'
    )
    
    # Timeline
    investigation_start_date = models.DateField(default=timezone.now)
    investigation_end_date = models.DateField(null=True, blank=True)
    review_due_date = models.DateField(
        null=True, 
        blank=True,
        help_text="Date when this RCA should be reviewed"
    )
    
    # 5 Whys Analysis
    why_1 = models.TextField(
        blank=True,
        verbose_name="Why 1 - First Level",
        help_text="Why did this incident happen?"
    )
    why_2 = models.TextField(
        blank=True,
        verbose_name="Why 2 - Second Level",
        help_text="Why did the first cause occur?"
    )
    why_3 = models.TextField(
        blank=True,
        verbose_name="Why 3 - Third Level",
        help_text="Why did the second cause occur?"
    )
    why_4 = models.TextField(
        blank=True,
        verbose_name="Why 4 - Fourth Level",
        help_text="Why did the third cause occur?"
    )
    why_5 = models.TextField(
        blank=True,
        verbose_name="Why 5 - Root Cause",
        help_text="Why did the fourth cause occur? (Root cause identified)"
    )
    
    # Contributing Factors (Fishbone categories)
    factor_people = models.TextField(
        blank=True,
        verbose_name="People Factors",
        help_text="Staff training, competence, workload, communication"
    )
    factor_environment = models.TextField(
        blank=True,
        verbose_name="Environment Factors",
        help_text="Physical environment, equipment, facilities"
    )
    factor_processes = models.TextField(
        blank=True,
        verbose_name="Process Factors",
        help_text="Procedures, protocols, workflows, documentation"
    )
    factor_organization = models.TextField(
        blank=True,
        verbose_name="Organizational Factors",
        help_text="Management, policies, culture, resources"
    )
    factor_external = models.TextField(
        blank=True,
        verbose_name="External Factors",
        help_text="Regulations, suppliers, weather, external events"
    )
    
    # Root Cause Summary
    root_cause_summary = models.TextField(
        help_text="Clear statement of identified root cause(s)"
    )
    
    # Learning & Recommendations
    lessons_learned = models.TextField(
        help_text="Key lessons from this investigation"
    )
    recommendations = models.TextField(
        help_text="Specific recommendations to prevent recurrence"
    )
    
    # Evidence
    evidence_reviewed = models.TextField(
        blank=True,
        help_text="List of evidence reviewed (documents, interviews, data)"
    )
    attachments = models.JSONField(
        default=list,
        blank=True,
        help_text="File paths or URLs to supporting documents"
    )
    
    # Approval
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rca_approved'
    )
    approved_date = models.DateField(null=True, blank=True)
    approval_comments = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Root Cause Analysis"
        verbose_name_plural = "Root Cause Analyses"
        ordering = ['-investigation_start_date']
    
    def __str__(self):
        return f"RCA for {self.incident.reference_number}"
    
    def is_complete(self):
        """Check if RCA has all required sections completed"""
        return bool(
            self.root_cause_summary and 
            self.lessons_learned and 
            self.recommendations and
            self.status == 'APPROVED'
        )


class SafetyActionPlan(models.Model):
    """
    Safety Action Plan tracking (replaces CAPA term to avoid confusion with Care About Physical Activity).
    Ensures corrective and preventive actions are assigned, tracked, and verified for effectiveness.
    """
    
    ACTION_TYPE_CHOICES = [
        ('CORRECTIVE', 'Corrective Action - Fix existing problem'),
        ('PREVENTIVE', 'Preventive Action - Prevent future problems'),
        ('IMPROVEMENT', 'Improvement Action - Enhance process'),
    ]
    
    PRIORITY_CHOICES = [
        ('IMMEDIATE', 'Immediate (24 hours)'),
        ('HIGH', 'High (1 week)'),
        ('MEDIUM', 'Medium (1 month)'),
        ('LOW', 'Low (3 months)'),
    ]
    
    STATUS_CHOICES = [
        ('IDENTIFIED', 'Identified'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed - Awaiting Verification'),
        ('VERIFIED', 'Verified Effective'),
        ('NOT_EFFECTIVE', 'Not Effective - Needs Revision'),
        ('CLOSED', 'Closed'),
    ]
    
    # Links
    incident = models.ForeignKey(
        IncidentReport,
        on_delete=models.CASCADE,
        related_name='safety_action_plans'
    )
    root_cause_analysis = models.ForeignKey(
        RootCauseAnalysis,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='safety_action_plans'
    )
    
    # Action Details
    reference_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="e.g., HSAP-2026-001 (Health and Safety Action Plan)"
    )
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IDENTIFIED')
    
    # Description
    problem_statement = models.TextField(
        help_text="What problem is this action addressing?"
    )
    action_description = models.TextField(
        help_text="Detailed description of the action to be taken"
    )
    expected_outcome = models.TextField(
        help_text="What success looks like"
    )
    
    # Ownership
    action_owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='safety_action_plans_owned'
    )
    supporting_staff = models.ManyToManyField(
        User,
        blank=True,
        related_name='safety_action_plans_supporting'
    )
    
    # Timeline
    identified_date = models.DateField(default=timezone.now)
    target_completion_date = models.DateField()
    actual_completion_date = models.DateField(null=True, blank=True)
    
    # Implementation
    implementation_plan = models.TextField(
        blank=True,
        help_text="Step-by-step plan for implementing this action"
    )
    resources_required = models.TextField(
        blank=True,
        help_text="Budget, staff time, equipment needed"
    )
    barriers_identified = models.TextField(
        blank=True,
        help_text="Potential obstacles to implementation"
    )
    
    # Progress Tracking
    percent_complete = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    progress_notes = models.TextField(
        blank=True,
        help_text="Regular updates on progress"
    )
    
    # Verification
    verification_method = models.TextField(
        blank=True,
        help_text="How will we verify this action is effective?"
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='safety_action_plans_verified'
    )
    verification_date = models.DateField(null=True, blank=True)
    verification_outcome = models.TextField(
        blank=True,
        help_text="Was the action effective? Evidence?"
    )
    
    # Effectiveness Review (3-6 months post-implementation)
    effectiveness_review_due = models.DateField(null=True, blank=True)
    effectiveness_review_completed = models.BooleanField(default=False)
    effectiveness_review_notes = models.TextField(
        blank=True,
        help_text="Long-term effectiveness assessment"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='safety_action_plans_created'
    )
    
    class Meta:
        verbose_name = "Safety Action Plan"
        verbose_name_plural = "Safety Action Plans"
        ordering = ['priority', 'target_completion_date']
    
    def __str__(self):
        return f"{self.reference_number} - {self.action_type}"
    
    def is_overdue(self):
        """Check if action is past target completion date"""
        if self.actual_completion_date:
            return False  # Completed, not overdue
        return timezone.now().date() > self.target_completion_date
    
    def days_until_due(self):
        """Calculate days until/past due date"""
        if self.actual_completion_date:
            return None  # Completed
        delta = self.target_completion_date - timezone.now().date()
        return delta.days
    
    def save(self, *args, **kwargs):
        """Auto-generate reference number if not provided"""
        if not self.reference_number:
            # Get the last HSAP number for this year
            year = timezone.now().year
            last_hsap = SafetyActionPlan.objects.filter(
                reference_number__startswith=f'HSAP-{year}-'
            ).order_by('-reference_number').first()
            
            if last_hsap:
                last_num = int(last_hsap.reference_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.reference_number = f'HSAP-{year}-{new_num:03d}'
        
        super().save(*args, **kwargs)


class DutyOfCandourRecord(models.Model):
    """
    Duty of Candour compliance tracking as per Duty of Candour (Scotland) Act 2016.
    Ensures transparent communication with families when unintended/unexpected harm occurs.
    """
    
    HARM_LEVEL_CHOICES = [
        ('DEATH', 'Death'),
        ('SEVERE', 'Severe Harm'),
        ('MODERATE', 'Moderate Harm'),
        ('LOW', 'Low Harm'),
        ('NONE', 'No Harm'),
    ]
    
    CANDOUR_STAGE_CHOICES = [
        ('ASSESSMENT', 'Assessment - Determining if DoC applies'),
        ('NOTIFICATION', 'Notification - Initial contact with family'),
        ('APOLOGY', 'Apology - Formal apology provided'),
        ('INVESTIGATION', 'Investigation - Incident being investigated'),
        ('FEEDBACK', 'Feedback - Findings shared with family'),
        ('REVIEW', 'Review - Follow-up with family'),
        ('COMPLETE', 'Complete - All requirements met'),
    ]
    
    # Link to incident
    incident = models.OneToOneField(
        IncidentReport,
        on_delete=models.CASCADE,
        related_name='duty_of_candour'
    )
    
    # Applicability Assessment
    duty_of_candour_applies = models.BooleanField(
        default=False,
        help_text="Does this incident meet DoC criteria?"
    )
    harm_level = models.CharField(
        max_length=20,
        choices=HARM_LEVEL_CHOICES,
        help_text="Level of harm to inform DoC requirement"
    )
    assessment_rationale = models.TextField(
        help_text="Why does/doesn't DoC apply to this incident?"
    )
    assessed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='doc_assessments'
    )
    assessment_date = models.DateField(default=timezone.now)
    
    # Person Affected
    resident = models.ForeignKey(
        Resident,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Resident affected (if applicable)"
    )
    family_contact_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Primary family contact for DoC communications"
    )
    family_contact_relationship = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., Daughter, Son, Power of Attorney"
    )
    family_contact_phone = models.CharField(max_length=20, blank=True)
    family_contact_email = models.EmailField(blank=True)
    family_preferred_contact_method = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('PHONE', 'Phone Call'),
            ('EMAIL', 'Email'),
            ('IN_PERSON', 'In-Person Meeting'),
            ('LETTER', 'Written Letter'),
        ]
    )
    
    # Initial Notification (Within 24 hours for death/severe harm)
    notification_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date family was first notified"
    )
    notification_method = models.CharField(max_length=50, blank=True)
    notification_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doc_notifications_made'
    )
    notification_details = models.TextField(
        blank=True,
        help_text="Summary of initial notification conversation"
    )
    
    # Apology
    apology_provided = models.BooleanField(default=False)
    apology_date = models.DateField(null=True, blank=True)
    apology_method = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('VERBAL', 'Verbal Apology'),
            ('WRITTEN', 'Written Letter'),
            ('BOTH', 'Verbal and Written'),
        ]
    )
    apology_letter_sent = models.BooleanField(default=False)
    apology_letter_file = models.FileField(
        upload_to='duty_of_candour/apology_letters/',
        null=True,
        blank=True
    )
    
    # Investigation Sharing
    investigation_findings_shared = models.BooleanField(default=False)
    findings_shared_date = models.DateField(null=True, blank=True)
    findings_summary_provided = models.TextField(
        blank=True,
        help_text="Summary of investigation findings shared with family"
    )
    
    # Actions Taken Sharing
    actions_shared_with_family = models.BooleanField(default=False)
    actions_shared_date = models.DateField(null=True, blank=True)
    actions_summary = models.TextField(
        blank=True,
        help_text="Summary of corrective actions shared with family"
    )
    
    # Follow-up Review
    follow_up_offered = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(
        blank=True,
        help_text="Notes from follow-up meeting/contact with family"
    )
    family_questions_addressed = models.TextField(
        blank=True,
        help_text="Questions raised by family and responses"
    )
    
    # Completion
    current_stage = models.CharField(
        max_length=20,
        choices=CANDOUR_STAGE_CHOICES,
        default='ASSESSMENT'
    )
    all_requirements_met = models.BooleanField(
        default=False,
        help_text="All DoC requirements completed?"
    )
    completion_date = models.DateField(null=True, blank=True)
    
    # Documentation
    communication_log = models.JSONField(
        default=list,
        blank=True,
        help_text="Log of all communications with family (dates, method, summary)"
    )
    
    # Care Inspectorate Reporting
    reported_to_care_inspectorate = models.BooleanField(default=False)
    ci_report_date = models.DateField(null=True, blank=True)
    ci_reference = models.CharField(max_length=100, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='doc_records_created'
    )
    
    class Meta:
        verbose_name = "Duty of Candour Record"
        verbose_name_plural = "Duty of Candour Records"
        ordering = ['-incident__incident_date']
    
    def __str__(self):
        return f"DoC for {self.incident.reference_number}"
    
    def is_within_notification_window(self):
        """
        Check if initial notification was within 24 hours for severe/death cases.
        Returns: (bool, str) - (compliant, reason)
        """
        if not self.duty_of_candour_applies:
            return True, "DoC does not apply"
        
        if self.harm_level not in ['DEATH', 'SEVERE']:
            return True, "Not urgent notification required"
        
        if not self.notification_date:
            return False, "No notification date recorded"
        
        incident_date = self.incident.incident_date
        notification_date = self.notification_date
        
        delta = (notification_date - incident_date).days
        
        if delta <= 1:  # Within 24 hours
            return True, f"Notified within {delta} day(s)"
        else:
            return False, f"Notified after {delta} days (should be within 1 day)"
    
    def get_compliance_status(self):
        """
        Calculate overall DoC compliance status.
        Returns: dict with compliance checks
        """
        if not self.duty_of_candour_applies:
            return {'compliant': True, 'reason': 'DoC does not apply'}
        
        compliance = {
            'notification_timely': self.is_within_notification_window()[0],
            'apology_provided': self.apology_provided,
            'findings_shared': self.investigation_findings_shared,
            'actions_shared': self.actions_shared_with_family,
            'follow_up_offered': self.follow_up_offered,
            'all_requirements_met': self.all_requirements_met,
        }
        
        compliance['compliant'] = all(compliance.values())
        compliance['completion_percentage'] = (
            sum(1 for v in compliance.values() if v) / len(compliance) * 100
        )
        
        return compliance


class IncidentTrendAnalysis(models.Model):
    """
    Automated trend analysis for incident patterns.
    Helps identify systemic issues and prevention opportunities.
    """
    
    ANALYSIS_PERIOD_CHOICES = [
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('ANNUAL', 'Annual'),
    ]
    
    # Time Period
    period_type = models.CharField(max_length=20, choices=ANALYSIS_PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Scope
    care_home = models.ForeignKey(
        CareHome,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Leave blank for organization-wide analysis"
    )
    
    # Incident Counts
    total_incidents = models.IntegerField(default=0)
    incidents_by_type = models.JSONField(
        default=dict,
        help_text="Count of each incident type"
    )
    incidents_by_severity = models.JSONField(
        default=dict,
        help_text="Count of each severity level"
    )
    
    # Trends
    trend_vs_previous_period = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('INCREASING', 'Increasing'),
            ('STABLE', 'Stable'),
            ('DECREASING', 'Decreasing'),
        ]
    )
    percentage_change = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage change vs previous period"
    )
    
    # Top Issues
    most_common_incident_type = models.CharField(max_length=50, blank=True)
    most_common_location = models.CharField(max_length=200, blank=True)
    peak_incident_times = models.JSONField(
        default=list,
        help_text="Time of day when most incidents occur"
    )
    
    # Staffing Correlation
    average_staffing_level = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    incidents_during_low_staffing = models.IntegerField(
        default=0,
        help_text="Incidents during below-average staffing"
    )
    
    # Actions & Recommendations
    key_findings = models.TextField(
        help_text="Summary of key findings from analysis"
    )
    recommendations = models.TextField(
        help_text="Recommended actions based on trends"
    )
    
    # Follow-up
    improvement_actions_created = models.IntegerField(
        default=0,
        help_text="Number of PDSA/CAPA actions created from this analysis"
    )
    
    # Metadata
    generated_date = models.DateField(auto_now_add=True)
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='trend_analyses_generated'
    )
    
    class Meta:
        verbose_name = "Incident Trend Analysis"
        verbose_name_plural = "Incident Trend Analyses"
        ordering = ['-end_date']
        unique_together = ['period_type', 'start_date', 'end_date', 'care_home']
    
    def __str__(self):
        home_name = self.care_home.name if self.care_home else "All Homes"
        return f"{home_name} - {self.period_type} Analysis ({self.start_date} to {self.end_date})"
