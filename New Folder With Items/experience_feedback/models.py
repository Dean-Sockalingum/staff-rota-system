"""
TQM Module 3: Experience & Feedback Models

This module provides comprehensive resident and family experience tracking, including:
- Satisfaction surveys (resident and family)
- Complaints management with resolution tracking
- Experience-Based Co-Design (EBCD) touchpoint mapping
- Quality of Life (QoL) outcome measures
- Feedback analysis and trending
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class SurveyType(models.TextChoices):
    """Types of satisfaction surveys."""
    RESIDENT_ADMISSION = 'RESIDENT_ADMISSION', 'Resident - Admission'
    RESIDENT_ONGOING = 'RESIDENT_ONGOING', 'Resident - Ongoing Care'
    RESIDENT_DISCHARGE = 'RESIDENT_DISCHARGE', 'Resident - Discharge'
    FAMILY_ADMISSION = 'FAMILY_ADMISSION', 'Family - Admission'
    FAMILY_ONGOING = 'FAMILY_ONGOING', 'Family - Ongoing Care'
    FAMILY_BEREAVEMENT = 'FAMILY_BEREAVEMENT', 'Family - Bereavement'
    STAFF_EXPERIENCE = 'STAFF_EXPERIENCE', 'Staff - Experience Survey'
    PROFESSIONAL_PARTNERSHIP = 'PROFESSIONAL_PARTNERSHIP', 'Professional - Partnership Survey'


class ComplaintSeverity(models.TextChoices):
    """Severity levels for complaints."""
    LOW = 'LOW', 'Low - Minor Concern'
    MEDIUM = 'MEDIUM', 'Medium - Moderate Issue'
    HIGH = 'HIGH', 'High - Serious Matter'
    CRITICAL = 'CRITICAL', 'Critical - Safeguarding/Safety'


class ComplaintStatus(models.TextChoices):
    """Status of complaint investigation."""
    RECEIVED = 'RECEIVED', 'Received'
    ACKNOWLEDGED = 'ACKNOWLEDGED', 'Acknowledged'
    INVESTIGATING = 'INVESTIGATING', 'Under Investigation'
    AWAITING_RESPONSE = 'AWAITING_RESPONSE', 'Awaiting Response'
    RESOLVED = 'RESOLVED', 'Resolved'
    ESCALATED = 'ESCALATED', 'Escalated'
    CLOSED = 'CLOSED', 'Closed'


class TouchpointCategory(models.TextChoices):
    """EBCD touchpoint categories."""
    ADMISSION = 'ADMISSION', 'Admission & Moving In'
    DAILY_CARE = 'DAILY_CARE', 'Daily Care Routines'
    ACTIVITIES = 'ACTIVITIES', 'Activities & Social'
    MEALS = 'MEALS', 'Meals & Nutrition'
    MEDICAL = 'MEDICAL', 'Medical Care & Health'
    FAMILY_VISIT = 'FAMILY_VISIT', 'Family Visits'
    END_OF_LIFE = 'END_OF_LIFE', 'End of Life Care'
    ENVIRONMENT = 'ENVIRONMENT', 'Physical Environment'


class SatisfactionSurvey(models.Model):
    """
    Resident and family satisfaction surveys.
    Captures structured feedback across multiple dimensions of care quality.
    """
    # Survey Metadata
    survey_type = models.CharField(
        max_length=30,
        choices=SurveyType.choices,
        help_text="Type of satisfaction survey"
    )
    survey_date = models.DateField(default=timezone.now)
    
    # Respondent Information
    care_home = models.ForeignKey(
        'scheduling.CareHome',
        on_delete=models.CASCADE,
        related_name='satisfaction_surveys'
    )
    resident = models.ForeignKey(
        'scheduling.Resident',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='satisfaction_surveys',
        help_text="Resident being surveyed or whose care is being assessed"
    )
    respondent_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name of person completing survey (optional for anonymity)"
    )
    relationship_to_resident = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., Self, Daughter, Son, Power of Attorney"
    )
    is_anonymous = models.BooleanField(
        default=False,
        help_text="Anonymous survey (no identifying information)"
    )
    
    # Overall Satisfaction (1-5 Likert scale)
    overall_satisfaction = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Overall satisfaction (1=Very Dissatisfied, 5=Very Satisfied)"
    )
    
    # Core Dimensions (1-5 Likert scale)
    quality_of_care = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Quality of care provided"
    )
    staff_attitude = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Staff friendliness and professionalism"
    )
    communication = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Communication with staff and management"
    )
    environment_cleanliness = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Cleanliness and maintenance of environment"
    )
    meals_nutrition = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Quality and variety of meals"
    )
    activities_engagement = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Activities and social engagement opportunities"
    )
    dignity_respect = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Dignity and respect shown to residents"
    )
    safety_security = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Feeling of safety and security"
    )
    
    # Net Promoter Score
    likelihood_recommend = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        null=True,
        blank=True,
        help_text="How likely to recommend? (0=Not at all, 10=Extremely likely)"
    )
    
    # Qualitative Feedback
    what_works_well = models.TextField(
        blank=True,
        help_text="What aspects of care work well?"
    )
    areas_for_improvement = models.TextField(
        blank=True,
        help_text="What could be improved?"
    )
    additional_comments = models.TextField(
        blank=True,
        help_text="Any other comments or feedback"
    )
    
    # Response Handling
    requires_followup = models.BooleanField(
        default=False,
        help_text="Does this survey require follow-up action?"
    )
    followup_assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_survey_followups'
    )
    followup_completed = models.BooleanField(default=False)
    followup_notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_surveys'
    )
    
    class Meta:
        ordering = ['-survey_date', '-created_at']
        indexes = [
            models.Index(fields=['care_home', '-survey_date']),
            models.Index(fields=['survey_type', '-survey_date']),
            models.Index(fields=['resident', '-survey_date']),
            models.Index(fields=['-survey_date']),
        ]
        verbose_name = 'Satisfaction Survey'
        verbose_name_plural = 'Satisfaction Surveys'
    
    def __str__(self):
        respondent = self.respondent_name if self.respondent_name else "Anonymous"
        return f"{self.get_survey_type_display()} - {respondent} ({self.survey_date})"
    
    def get_average_score(self):
        """Calculate average score across all rated dimensions."""
        scores = [
            self.overall_satisfaction,
            self.quality_of_care,
            self.staff_attitude,
            self.communication,
            self.environment_cleanliness,
            self.meals_nutrition,
            self.activities_engagement,
            self.dignity_respect,
            self.safety_security,
        ]
        valid_scores = [s for s in scores if s is not None]
        return sum(valid_scores) / len(valid_scores) if valid_scores else 0
    
    def get_nps_category(self):
        """Calculate Net Promoter Score category."""
        if self.likelihood_recommend is None:
            return None
        if self.likelihood_recommend >= 9:
            return 'PROMOTER'
        elif self.likelihood_recommend >= 7:
            return 'PASSIVE'
        else:
            return 'DETRACTOR'


class Complaint(models.Model):
    """
    Formal complaints tracking and resolution management.
    Complies with Scottish care home complaints procedures.
    """
    # Complaint Identification
    complaint_reference = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique complaint reference number"
    )
    care_home = models.ForeignKey(
        'scheduling.CareHome',
        on_delete=models.CASCADE,
        related_name='complaints'
    )
    
    # Complainant Information
    complainant_name = models.CharField(max_length=200)
    complainant_relationship = models.CharField(
        max_length=100,
        help_text="Relationship to resident (e.g., Son, Daughter, Resident themselves)"
    )
    complainant_contact = models.CharField(
        max_length=200,
        blank=True,
        help_text="Phone or email for contact"
    )
    resident = models.ForeignKey(
        'scheduling.Resident',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaints',
        help_text="Resident the complaint relates to"
    )
    
    # Complaint Details
    date_received = models.DateField(default=timezone.now)
    complaint_category = models.CharField(
        max_length=50,
        choices=[
            ('CARE_QUALITY', 'Quality of Care'),
            ('STAFF_CONDUCT', 'Staff Conduct/Attitude'),
            ('SAFETY', 'Safety Concern'),
            ('ENVIRONMENT', 'Facilities/Environment'),
            ('COMMUNICATION', 'Communication'),
            ('MEALS', 'Meals/Nutrition'),
            ('ACTIVITIES', 'Activities/Social Life'),
            ('MEDICATION', 'Medication Management'),
            ('PERSONAL_CARE', 'Personal Care'),
            ('DIGNITY', 'Dignity/Respect'),
            ('FINANCIAL', 'Financial/Fees'),
            ('OTHER', 'Other'),
        ],
        default='OTHER'
    )
    severity = models.CharField(
        max_length=20,
        choices=ComplaintSeverity.choices,
        default='MEDIUM'
    )
    
    complaint_description = models.TextField(
        help_text="Detailed description of the complaint"
    )
    desired_outcome = models.TextField(
        blank=True,
        help_text="What outcome does the complainant want?"
    )
    
    # Status Tracking
    status = models.CharField(
        max_length=30,
        choices=ComplaintStatus.choices,
        default='RECEIVED'
    )
    date_acknowledged = models.DateField(
        null=True,
        blank=True,
        help_text="Date acknowledgement sent (should be within 3 working days)"
    )
    target_resolution_date = models.DateField(
        null=True,
        blank=True,
        help_text="Target date for resolution (typically 20 working days)"
    )
    actual_resolution_date = models.DateField(
        null=True,
        blank=True,
        help_text="Actual date complaint was resolved"
    )
    
    # Assignment
    investigating_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='investigating_complaints'
    )
    
    # Investigation Findings
    investigation_notes = models.TextField(
        blank=True,
        help_text="Investigation findings and actions taken"
    )
    root_cause = models.TextField(
        blank=True,
        help_text="Root cause analysis of the complaint"
    )
    lessons_learned = models.TextField(
        blank=True,
        help_text="Lessons learned and improvements made"
    )
    
    # Resolution
    resolution_details = models.TextField(
        blank=True,
        help_text="How the complaint was resolved"
    )
    complainant_satisfied = models.BooleanField(
        null=True,
        blank=True,
        help_text="Was the complainant satisfied with the resolution?"
    )
    
    # Escalation
    escalated_to_care_inspectorate = models.BooleanField(
        default=False,
        help_text="Was this escalated to Care Inspectorate?"
    )
    escalation_date = models.DateField(null=True, blank=True)
    escalation_reference = models.CharField(max_length=50, blank=True)
    
    # Linked Records
    related_incident = models.ForeignKey(
        'scheduling.IncidentReport',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_complaints',
        help_text="Link to related incident report if applicable"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_complaints'
    )
    
    class Meta:
        ordering = ['-date_received']
        indexes = [
            models.Index(fields=['care_home', '-date_received']),
            models.Index(fields=['status', '-date_received']),
            models.Index(fields=['severity', '-date_received']),
            models.Index(fields=['-date_received']),
        ]
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'
    
    def __str__(self):
        return f"{self.complaint_reference} - {self.complainant_name} ({self.date_received})"
    
    def is_overdue(self):
        """Check if complaint resolution is overdue."""
        if self.status in ['RESOLVED', 'CLOSED']:
            return False
        if self.target_resolution_date:
            return timezone.now().date() > self.target_resolution_date
        return False
    
    def days_since_received(self):
        """Calculate days since complaint was received."""
        return (timezone.now().date() - self.date_received).days
    
    def acknowledgement_within_target(self):
        """Check if acknowledgement was sent within 3 working days."""
        if not self.date_acknowledged:
            return False
        days_diff = (self.date_acknowledged - self.date_received).days
        return days_diff <= 3


class ComplaintInvestigationStage(models.Model):
    """
    Track multi-stage investigation process for complaints.
    Ensures thorough investigation with clear accountability.
    """
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='investigation_stages'
    )
    
    stage_name = models.CharField(
        max_length=100,
        choices=[
            ('INITIAL_REVIEW', 'Initial Review & Triage'),
            ('EVIDENCE_GATHERING', 'Evidence Gathering'),
            ('STAFF_INTERVIEWS', 'Staff Interviews'),
            ('RESIDENT_INTERVIEW', 'Resident/Family Interview'),
            ('DOCUMENTATION_REVIEW', 'Documentation Review'),
            ('ROOT_CAUSE_ANALYSIS', 'Root Cause Analysis'),
            ('ACTION_PLAN', 'Action Plan Development'),
            ('IMPLEMENTATION', 'Action Implementation'),
            ('FOLLOW_UP', 'Follow-up & Verification'),
            ('CLOSURE', 'Closure & Feedback'),
        ],
        help_text="Stage of the investigation process"
    )
    
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_investigation_stages'
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
            ('BLOCKED', 'Blocked'),
        ],
        default='PENDING'
    )
    
    start_date = models.DateField(null=True, blank=True)
    target_completion = models.DateField(null=True, blank=True)
    actual_completion = models.DateField(null=True, blank=True)
    
    findings = models.TextField(
        blank=True,
        help_text="Findings from this investigation stage"
    )
    evidence_collected = models.TextField(
        blank=True,
        help_text="Evidence collected during this stage"
    )
    actions_required = models.TextField(
        blank=True,
        help_text="Actions required as a result of this stage"
    )
    
    sequence_order = models.IntegerField(
        default=0,
        help_text="Order in the investigation process"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['complaint', 'sequence_order']
        verbose_name = 'Investigation Stage'
        verbose_name_plural = 'Investigation Stages'
    
    def __str__(self):
        return f"{self.complaint.complaint_reference} - {self.get_stage_name_display()}"
    
    def is_overdue(self):
        """Check if stage is overdue."""
        if self.status == 'COMPLETED':
            return False
        if self.target_completion:
            return timezone.now().date() > self.target_completion
        return False


class ComplaintStakeholder(models.Model):
    """
    Track stakeholders involved in complaint investigation.
    Ensures all relevant parties are consulted and kept informed.
    """
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='stakeholders'
    )
    
    stakeholder_type = models.CharField(
        max_length=30,
        choices=[
            ('COMPLAINANT', 'Complainant'),
            ('RESIDENT', 'Resident'),
            ('FAMILY_MEMBER', 'Family Member'),
            ('STAFF_WITNESS', 'Staff Witness'),
            ('CARE_MANAGER', 'Care Manager'),
            ('SENIOR_MANAGEMENT', 'Senior Management'),
            ('EXTERNAL_PROFESSIONAL', 'External Professional'),
            ('CARE_INSPECTORATE', 'Care Inspectorate'),
            ('LOCAL_AUTHORITY', 'Local Authority'),
            ('POLICE', 'Police'),
            ('OTHER', 'Other'),
        ],
        help_text="Type of stakeholder"
    )
    
    name = models.CharField(max_length=200)
    role_title = models.CharField(max_length=100, blank=True)
    contact_details = models.CharField(max_length=200, blank=True)
    
    involvement_description = models.TextField(
        help_text="How is this person involved in the complaint?"
    )
    
    date_contacted = models.DateField(null=True, blank=True)
    statement_received = models.BooleanField(default=False)
    statement_date = models.DateField(null=True, blank=True)
    statement_notes = models.TextField(blank=True)
    
    requires_update = models.BooleanField(
        default=False,
        help_text="Does this stakeholder require updates on progress?"
    )
    last_updated = models.DateField(null=True, blank=True)
    update_frequency = models.CharField(
        max_length=20,
        choices=[
            ('DAILY', 'Daily'),
            ('WEEKLY', 'Weekly'),
            ('FORTNIGHTLY', 'Fortnightly'),
            ('MONTHLY', 'Monthly'),
            ('AS_NEEDED', 'As Needed'),
        ],
        default='WEEKLY',
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_stakeholders'
    )
    
    class Meta:
        ordering = ['complaint', 'stakeholder_type', 'name']
        verbose_name = 'Complaint Stakeholder'
        verbose_name_plural = 'Complaint Stakeholders'
    
    def __str__(self):
        return f"{self.name} ({self.get_stakeholder_type_display()}) - {self.complaint.complaint_reference}"


class EBCDTouchpoint(models.Model):
    """
    Experience-Based Co-Design touchpoint mapping.
    Identifies key moments in the resident journey that matter most.
    """
    care_home = models.ForeignKey(
        'scheduling.CareHome',
        on_delete=models.CASCADE,
        related_name='ebcd_touchpoints'
    )
    
    # Touchpoint Definition
    touchpoint_name = models.CharField(
        max_length=200,
        help_text="Name of this touchpoint (e.g., 'First Morning Wake Up')"
    )
    category = models.CharField(
        max_length=30,
        choices=TouchpointCategory.choices,
        help_text="Category of care journey"
    )
    description = models.TextField(
        help_text="Description of what happens at this touchpoint"
    )
    sequence_order = models.IntegerField(
        default=0,
        help_text="Order in the resident journey"
    )
    
    # Importance & Emotional Impact
    importance_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="How important is this touchpoint? (1=Low, 5=Critical)"
    )
    emotional_impact = models.CharField(
        max_length=20,
        choices=[
            ('VERY_POSITIVE', 'Very Positive'),
            ('POSITIVE', 'Positive'),
            ('NEUTRAL', 'Neutral'),
            ('NEGATIVE', 'Negative'),
            ('VERY_NEGATIVE', 'Very Negative'),
        ],
        default='NEUTRAL',
        help_text="Typical emotional impact on residents/families"
    )
    
    # Current State
    current_experience_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Current experience quality (1=Poor, 5=Excellent)"
    )
    pain_points = models.TextField(
        blank=True,
        help_text="Known problems or challenges at this touchpoint"
    )
    
    # Desired State
    improvement_ideas = models.TextField(
        blank=True,
        help_text="Ideas for improving this touchpoint"
    )
    target_experience_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Target experience quality (1=Poor, 5=Excellent)"
    )
    
    # Co-Design Participation
    residents_consulted = models.IntegerField(
        default=0,
        help_text="Number of residents consulted about this touchpoint"
    )
    families_consulted = models.IntegerField(
        default=0,
        help_text="Number of family members consulted"
    )
    staff_consulted = models.IntegerField(
        default=0,
        help_text="Number of staff consulted"
    )
    
    # Implementation
    improvements_implemented = models.TextField(
        blank=True,
        help_text="Improvements that have been implemented"
    )
    implementation_date = models.DateField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Is this touchpoint still being monitored?"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    
    class Meta:
        ordering = ['care_home', 'category', 'sequence_order']
        indexes = [
            models.Index(fields=['care_home', 'category']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = 'EBCD Touchpoint'
        verbose_name_plural = 'EBCD Touchpoints'
    
    def __str__(self):
        return f"{self.touchpoint_name} ({self.get_category_display()})"
    
    def get_improvement_gap(self):
        """Calculate gap between current and target experience."""
        if self.current_experience_rating and self.target_experience_rating:
            return self.target_experience_rating - self.current_experience_rating
        return None


class QualityOfLifeAssessment(models.Model):
    """
    Quality of Life (QoL) outcome measures for residents.
    Uses validated tools like DEMQOL, EQ-5D, or custom assessments.
    """
    resident = models.ForeignKey(
        'scheduling.Resident',
        on_delete=models.CASCADE,
        related_name='qol_assessments'
    )
    assessment_date = models.DateField(default=timezone.now)
    
    # Assessment Type
    assessment_tool = models.CharField(
        max_length=50,
        choices=[
            ('DEMQOL', 'DEMQOL (Dementia Quality of Life)'),
            ('EQ5D', 'EQ-5D-5L (EuroQol)'),
            ('WHOQOL', 'WHOQOL-BREF'),
            ('QUALID', 'QUALID (Quality of Life in Dementia)'),
            ('CUSTOM', 'Custom Care Home Assessment'),
        ],
        default='CUSTOM'
    )
    
    # Core QoL Dimensions (1-5 scale)
    physical_health = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Physical health and mobility"
    )
    psychological_wellbeing = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Mood, anxiety, happiness"
    )
    social_relationships = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Relationships with others, social engagement"
    )
    independence_autonomy = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Ability to make choices and maintain independence"
    )
    environment_comfort = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Physical environment and comfort"
    )
    
    # Additional Dimensions
    pain_discomfort = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Level of pain/discomfort (1=Severe, 5=None)"
    )
    cognitive_function = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Memory and cognitive ability"
    )
    meaningful_activity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Engagement in meaningful activities"
    )
    spiritual_needs = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Spiritual and cultural needs met"
    )
    
    # Overall QoL Score
    overall_qol_score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Overall QoL score (calculated or assessed)"
    )
    
    # Assessment Context
    assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='qol_assessments'
    )
    assessment_method = models.CharField(
        max_length=20,
        choices=[
            ('SELF_REPORT', 'Self-Report by Resident'),
            ('PROXY', 'Proxy (Family/Staff)'),
            ('OBSERVATION', 'Observation'),
            ('COMBINED', 'Combined Methods'),
        ],
        default='COMBINED'
    )
    
    # Qualitative Notes
    strengths_noted = models.TextField(
        blank=True,
        help_text="Areas where QoL is good"
    )
    concerns_noted = models.TextField(
        blank=True,
        help_text="Areas of concern or decline"
    )
    interventions_recommended = models.TextField(
        blank=True,
        help_text="Recommended interventions to improve QoL"
    )
    
    # Follow-up
    requires_review = models.BooleanField(
        default=False,
        help_text="Does this assessment require management review?"
    )
    review_completed = models.BooleanField(default=False)
    next_assessment_due = models.DateField(
        null=True,
        blank=True,
        help_text="When should the next assessment occur?"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-assessment_date', 'resident']
        indexes = [
            models.Index(fields=['resident', '-assessment_date']),
            models.Index(fields=['-assessment_date']),
        ]
        verbose_name = 'Quality of Life Assessment'
        verbose_name_plural = 'Quality of Life Assessments'
    
    def __str__(self):
        return f"QoL Assessment - {self.resident.full_name} ({self.assessment_date})"
    
    def calculate_composite_score(self):
        """Calculate composite QoL score from all dimensions."""
        scores = [
            self.physical_health,
            self.psychological_wellbeing,
            self.social_relationships,
            self.independence_autonomy,
            self.environment_comfort,
        ]
        
        # Add optional dimensions if present
        if self.pain_discomfort:
            scores.append(self.pain_discomfort)
        if self.cognitive_function:
            scores.append(self.cognitive_function)
        if self.meaningful_activity:
            scores.append(self.meaningful_activity)
        if self.spiritual_needs:
            scores.append(self.spiritual_needs)
        
        return Decimal(sum(scores) / len(scores)) if scores else Decimal('0.00')
    
    def save(self, *args, **kwargs):
        """Auto-calculate overall score if not provided."""
        if not self.overall_qol_score:
            self.overall_qol_score = self.calculate_composite_score()
        super().save(*args, **kwargs)


class FeedbackTheme(models.Model):
    """
    Thematic analysis of feedback across surveys and complaints.
    Identifies recurring themes and trends in resident/family feedback.
    """
    care_home = models.ForeignKey(
        'scheduling.CareHome',
        on_delete=models.CASCADE,
        related_name='feedback_themes'
    )
    
    # Theme Definition
    theme_name = models.CharField(
        max_length=200,
        help_text="Name of the feedback theme"
    )
    theme_category = models.CharField(
        max_length=50,
        choices=[
            ('POSITIVE', 'Positive Feedback'),
            ('CONCERN', 'Area of Concern'),
            ('SUGGESTION', 'Improvement Suggestion'),
            ('COMPLAINT', 'Complaint Theme'),
        ],
        default='CONCERN'
    )
    description = models.TextField(
        help_text="Description of this theme and examples"
    )
    
    # Frequency & Trend
    occurrences_count = models.IntegerField(
        default=0,
        help_text="Number of times this theme has appeared in feedback"
    )
    first_identified = models.DateField(default=timezone.now)
    last_occurrence = models.DateField(null=True, blank=True)
    trend_direction = models.CharField(
        max_length=20,
        choices=[
            ('INCREASING', 'Increasing'),
            ('STABLE', 'Stable'),
            ('DECREASING', 'Decreasing'),
        ],
        null=True,
        blank=True
    )
    
    # Response & Action
    action_plan = models.TextField(
        blank=True,
        help_text="Action plan to address this theme"
    )
    actions_taken = models.TextField(
        blank=True,
        help_text="Actions that have been taken"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_feedback_themes'
    )
    
    # Impact Assessment
    impact_on_satisfaction = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Impact on overall satisfaction (1=Low, 5=High)"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Is this theme still being monitored?"
    )
    resolved_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date theme was resolved or closed"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_feedback_themes'
    )
    
    class Meta:
        ordering = ['-occurrences_count', '-last_occurrence']
        indexes = [
            models.Index(fields=['care_home', 'is_active']),
            models.Index(fields=['theme_category', '-occurrences_count']),
        ]
        verbose_name = 'Feedback Theme'
        verbose_name_plural = 'Feedback Themes'
    
    def __str__(self):
        return f"{self.theme_name} ({self.occurrences_count} occurrences)"


class YouSaidWeDidAction(models.Model):
    """
    'You Said, We Did' response tracking.
    
    Demonstrates responsiveness to feedback by documenting what was said
    and what actions were taken in response. Critical for Care Inspectorate
    evidence of person-centered approach and continuous improvement.
    """
    care_home = models.ForeignKey(
        'scheduling.CareHome',
        on_delete=models.CASCADE,
        related_name='yswda_actions'
    )
    
    # Source of Feedback
    source_type = models.CharField(
        max_length=30,
        choices=[
            ('SURVEY', 'Satisfaction Survey'),
            ('COMPLAINT', 'Complaint'),
            ('MEETING', 'Resident/Family Meeting'),
            ('INFORMAL', 'Informal Feedback'),
            ('SUGGESTION_BOX', 'Suggestion Box'),
            ('CARE_REVIEW', 'Care Review Meeting'),
        ],
        help_text="Where did this feedback come from?"
    )
    
    # Link to source (optional)
    related_survey = models.ForeignKey(
        SatisfactionSurvey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='yswda_actions'
    )
    related_complaint = models.ForeignKey(
        Complaint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='yswda_actions'
    )
    related_theme = models.ForeignKey(
        FeedbackTheme,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='yswda_actions'
    )
    
    # "YOU SAID..." - The Feedback
    you_said = models.TextField(
        help_text="What residents/families told us (the feedback received)"
    )
    feedback_date = models.DateField(
        default=timezone.now,
        help_text="When was this feedback received?"
    )
    who_said_it = models.CharField(
        max_length=200,
        blank=True,
        help_text="Who provided the feedback (optional for anonymity)"
    )
    
    # Categorization
    category = models.CharField(
        max_length=50,
        choices=[
            ('CARE_QUALITY', 'Quality of Care'),
            ('STAFF', 'Staff & Staffing'),
            ('ACTIVITIES', 'Activities & Social'),
            ('MEALS', 'Meals & Nutrition'),
            ('ENVIRONMENT', 'Environment & Facilities'),
            ('COMMUNICATION', 'Communication'),
            ('FAMILY_INVOLVEMENT', 'Family Involvement'),
            ('DIGNITY_RESPECT', 'Dignity & Respect'),
            ('SAFETY', 'Safety & Security'),
            ('OTHER', 'Other'),
        ],
        default='OTHER'
    )
    
    sentiment = models.CharField(
        max_length=20,
        choices=[
            ('POSITIVE', 'Positive - Compliment'),
            ('CONCERN', 'Concern - Area for Improvement'),
            ('COMPLAINT', 'Complaint - Issue to Resolve'),
            ('SUGGESTION', 'Suggestion - New Idea'),
        ],
        default='CONCERN'
    )
    
    # "WE DID..." - The Response/Action
    we_did = models.TextField(
        help_text="What we did in response to this feedback",
        blank=True
    )
    action_taken_date = models.DateField(
        null=True,
        blank=True,
        help_text="When was the action completed?"
    )
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='yswda_responsible'
    )
    
    # Status & Impact
    status = models.CharField(
        max_length=20,
        choices=[
            ('RECEIVED', 'Feedback Received'),
            ('ACKNOWLEDGED', 'Acknowledged'),
            ('IN_PROGRESS', 'Action In Progress'),
            ('COMPLETED', 'Action Completed'),
            ('ONGOING', 'Ongoing Monitoring'),
            ('NO_ACTION', 'No Action Required'),
        ],
        default='RECEIVED'
    )
    
    impact_assessment = models.TextField(
        blank=True,
        help_text="What impact did this action have?"
    )
    
    # Communication & Visibility
    communicated_to_residents = models.BooleanField(
        default=False,
        help_text="Has this been communicated to residents/families?"
    )
    communicated_date = models.DateField(
        null=True,
        blank=True
    )
    communication_method = models.CharField(
        max_length=50,
        blank=True,
        help_text="How was it communicated? (e.g., notice board, newsletter, meeting)"
    )
    
    display_on_board = models.BooleanField(
        default=True,
        help_text="Display on 'You Said, We Did' notice board?"
    )
    display_until = models.DateField(
        null=True,
        blank=True,
        help_text="Display until this date (leave blank for indefinite)"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='yswda_created'
    )
    
    class Meta:
        ordering = ['-feedback_date']
        verbose_name = 'You Said, We Did Action'
        verbose_name_plural = 'You Said, We Did Actions'
        indexes = [
            models.Index(fields=['care_home', 'display_on_board', 'display_until']),
            models.Index(fields=['status', '-feedback_date']),
        ]
    
    def __str__(self):
        return f"YSWDA: {self.you_said[:50]}... [{self.status}]"
    
    def is_displayable(self):
        """Check if this should be displayed on notice board"""
        if not self.display_on_board:
            return False
        if self.display_until and self.display_until < timezone.now().date():
            return False
        return True
    
    def days_since_feedback(self):
        """Calculate days since feedback was received"""
        delta = timezone.now().date() - self.feedback_date
        return delta.days
    
    def days_to_action(self):
        """Calculate days from feedback to action completion"""
        if self.action_taken_date and self.feedback_date:
            delta = self.action_taken_date - self.feedback_date
            return delta.days
        return None


# ============================================================================
# SURVEY DISTRIBUTION MODELS
# ============================================================================

class SurveyDistributionSchedule(models.Model):
    """
    Automated survey distribution schedule.
    Defines when and how surveys should be sent to residents/families.
    """
    schedule_name = models.CharField(
        max_length=200,
        help_text="Name for this distribution schedule"
    )
    care_home = models.ForeignKey(
        'scheduling.CareHome',
        on_delete=models.CASCADE,
        related_name='survey_schedules'
    )
    survey_type = models.CharField(
        max_length=30,
        choices=SurveyType.choices,
        help_text="Type of survey to distribute"
    )
    
    # Scheduling
    is_active = models.BooleanField(
        default=True,
        help_text="Is this schedule currently active?"
    )
    distribution_frequency = models.CharField(
        max_length=20,
        choices=[
            ('ADMISSION', 'On Admission'),
            ('DISCHARGE', 'On Discharge'),
            ('WEEKLY', 'Weekly'),
            ('MONTHLY', 'Monthly'),
            ('QUARTERLY', 'Quarterly'),
            ('BIANNUAL', 'Every 6 Months'),
            ('ANNUAL', 'Annually'),
        ],
        default='QUARTERLY',
        help_text="How often to send surveys"
    )
    
    # For periodic surveys
    day_of_week = models.IntegerField(
        null=True,
        blank=True,
        choices=[
            (0, 'Monday'),
            (1, 'Tuesday'),
            (2, 'Wednesday'),
            (3, 'Thursday'),
            (4, 'Friday'),
            (5, 'Saturday'),
            (6, 'Sunday'),
        ],
        help_text="Day of week for weekly surveys"
    )
    day_of_month = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text="Day of month for monthly/quarterly/annual surveys"
    )
    
    # For event-based surveys (admission/discharge)
    days_after_event = models.IntegerField(
        default=7,
        help_text="Days after admission/discharge to send survey"
    )
    
    # Distribution channels
    send_via_email = models.BooleanField(
        default=True,
        help_text="Send survey links via email"
    )
    send_via_sms = models.BooleanField(
        default=False,
        help_text="Send survey links via SMS"
    )
    print_qr_code = models.BooleanField(
        default=True,
        help_text="Generate QR code for printed materials"
    )
    
    # Recipients
    send_to_residents = models.BooleanField(
        default=True,
        help_text="Send to residents directly"
    )
    send_to_families = models.BooleanField(
        default=True,
        help_text="Send to family contacts"
    )
    
    # Email template customization
    email_subject = models.CharField(
        max_length=200,
        default="We'd love your feedback",
        help_text="Email subject line"
    )
    email_intro = models.TextField(
        default="Your feedback helps us improve our care. Please take a few minutes to complete this survey.",
        help_text="Introduction text for email"
    )
    
    # Reminders
    send_reminder = models.BooleanField(
        default=True,
        help_text="Send reminder to non-respondents"
    )
    reminder_days = models.IntegerField(
        default=7,
        help_text="Days after initial send to send reminder"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_survey_schedules'
    )
    last_run = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When was this schedule last executed?"
    )
    next_run = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When will this schedule next run?"
    )
    
    class Meta:
        ordering = ['care_home', 'survey_type']
        verbose_name = 'Survey Distribution Schedule'
        verbose_name_plural = 'Survey Distribution Schedules'
    
    def __str__(self):
        return f"{self.schedule_name} - {self.get_survey_type_display()}"


class SurveyDistribution(models.Model):
    """
    Individual survey distribution record.
    Tracks each survey sent to a recipient with response tracking.
    """
    schedule = models.ForeignKey(
        SurveyDistributionSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='distributions',
        help_text="The schedule that generated this distribution (if applicable)"
    )
    
    care_home = models.ForeignKey(
        'scheduling.CareHome',
        on_delete=models.CASCADE,
        related_name='survey_distributions'
    )
    survey_type = models.CharField(
        max_length=30,
        choices=SurveyType.choices
    )
    
    # Recipient
    resident = models.ForeignKey(
        'scheduling.Resident',
        on_delete=models.CASCADE,
        related_name='survey_distributions',
        help_text="Resident this survey is about"
    )
    recipient_name = models.CharField(
        max_length=200,
        help_text="Name of person receiving survey"
    )
    recipient_email = models.EmailField(
        blank=True,
        help_text="Email address for survey link"
    )
    recipient_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Phone number for SMS survey link"
    )
    recipient_type = models.CharField(
        max_length=20,
        choices=[
            ('RESIDENT', 'Resident'),
            ('FAMILY', 'Family Member'),
            ('POWER_OF_ATTORNEY', 'Power of Attorney'),
            ('OTHER', 'Other'),
        ],
        default='FAMILY'
    )
    
    # Survey link and QR code
    survey_token = models.CharField(
        max_length=64,
        unique=True,
        help_text="Unique token for survey link"
    )
    qr_code_generated = models.BooleanField(
        default=False,
        help_text="Has QR code been generated?"
    )
    qr_code_path = models.CharField(
        max_length=255,
        blank=True,
        help_text="Path to generated QR code image"
    )
    
    # Distribution tracking
    sent_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When was survey sent?"
    )
    sent_via = models.CharField(
        max_length=20,
        choices=[
            ('EMAIL', 'Email'),
            ('SMS', 'SMS'),
            ('BOTH', 'Email & SMS'),
            ('QR_PRINTED', 'QR Code Printed'),
            ('MANUAL', 'Manual Distribution'),
        ],
        blank=True
    )
    
    # Response tracking
    response_received = models.BooleanField(
        default=False,
        help_text="Has recipient responded?"
    )
    response_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When did recipient respond?"
    )
    completed_survey = models.ForeignKey(
        SatisfactionSurvey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='distribution_record',
        help_text="Link to completed survey"
    )
    
    # Reminder tracking
    reminder_sent = models.BooleanField(
        default=False,
        help_text="Has reminder been sent?"
    )
    reminder_sent_date = models.DateTimeField(
        null=True,
        blank=True
    )
    
    # Email delivery tracking
    email_delivered = models.BooleanField(
        default=False,
        help_text="Was email successfully delivered?"
    )
    email_opened = models.BooleanField(
        default=False,
        help_text="Did recipient open email?"
    )
    email_bounced = models.BooleanField(
        default=False,
        help_text="Did email bounce?"
    )
    
    # SMS delivery tracking
    sms_delivered = models.BooleanField(
        default=False,
        help_text="Was SMS successfully delivered?"
    )
    sms_failed = models.BooleanField(
        default=False,
        help_text="Did SMS fail to send?"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(
        blank=True,
        help_text="Any notes about this distribution"
    )
    
    class Meta:
        ordering = ['-sent_date']
        verbose_name = 'Survey Distribution'
        verbose_name_plural = 'Survey Distributions'
        indexes = [
            models.Index(fields=['care_home', '-sent_date']),
            models.Index(fields=['survey_token']),
            models.Index(fields=['response_received', '-sent_date']),
        ]
    
    def __str__(self):
        return f"{self.get_survey_type_display()} → {self.recipient_name} ({self.sent_date})"
    
    def get_survey_url(self):
        """Get the public survey URL for this distribution"""
        from django.urls import reverse
        return reverse('experience_feedback:public_survey', kwargs={'token': self.survey_token})
    
    def days_since_sent(self):
        """Calculate days since survey was sent"""
        if self.sent_date:
            delta = timezone.now() - self.sent_date
            return delta.days
        return None
    
    def response_time_days(self):
        """Calculate days from send to response"""
        if self.sent_date and self.response_date:
            delta = self.response_date - self.sent_date
            return delta.days
        return None
    
    def needs_reminder(self):
        """Check if this distribution needs a reminder"""
        if self.response_received or self.reminder_sent:
            return False
        if not self.sent_date:
            return False
        
        # Get reminder threshold from schedule or default to 7 days
        reminder_threshold = 7
        if self.schedule and self.schedule.send_reminder:
            reminder_threshold = self.schedule.reminder_days
        
        days_since = self.days_since_sent()
        return days_since and days_since >= reminder_threshold


# ============================================================================
# FAMILY ENGAGEMENT PORTAL MODELS
# ============================================================================

class FamilyMember(models.Model):
    """
    Family member user account for the family engagement portal.
    Separate from staff users, provides secure access to view their loved one's care information.
    """
    # User Account
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='family_member_profile',
        help_text="Django user account for family member login"
    )
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Relationship
    resident = models.ForeignKey(
        'scheduling.Resident',
        on_delete=models.CASCADE,
        related_name='family_members',
        help_text="Resident this family member is associated with"
    )
    relationship = models.CharField(
        max_length=100,
        help_text="e.g., Daughter, Son, Spouse, Power of Attorney"
    )
    is_primary_contact = models.BooleanField(
        default=False,
        help_text="Is this the primary family contact for the resident?"
    )
    is_power_of_attorney = models.BooleanField(
        default=False,
        help_text="Does this person have Power of Attorney?"
    )
    
    # Portal Access
    portal_access_granted = models.BooleanField(default=True)
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('FULL', 'Full Access'),
            ('LIMITED', 'Limited Access'),
            ('VIEW_ONLY', 'View Only'),
        ],
        default='FULL'
    )
    
    # Communication Preferences
    receive_email_notifications = models.BooleanField(default=True)
    receive_sms_notifications = models.BooleanField(default=False)
    receive_survey_requests = models.BooleanField(default=True)
    
    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='family_members_created'
    )
    
    class Meta:
        ordering = ['resident', 'last_name', 'first_name']
        verbose_name = 'Family Member'
        verbose_name_plural = 'Family Members'
        indexes = [
            models.Index(fields=['resident', 'is_primary_contact']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.relationship} of {self.resident})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class FamilyMessage(models.Model):
    """
    Messages between family members and care staff.
    Provides secure, documented communication channel.
    """
    # Message Metadata
    family_member = models.ForeignKey(
        FamilyMember,
        on_delete=models.CASCADE,
        related_name='messages_sent'
    )
    resident = models.ForeignKey(
        'scheduling.Resident',
        on_delete=models.CASCADE,
        related_name='family_messages'
    )
    care_home = models.ForeignKey(
        'scheduling.CareHome',
        on_delete=models.CASCADE,
        related_name='family_messages'
    )
    
    # Message Content
    subject = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(
        max_length=50,
        choices=[
            ('GENERAL', 'General Enquiry'),
            ('CARE', 'Care Question'),
            ('MEDICAL', 'Medical Information'),
            ('VISIT', 'Visit Arrangement'),
            ('ACTIVITIES', 'Activities & Social'),
            ('FEEDBACK', 'Feedback'),
            ('OTHER', 'Other'),
        ],
        default='GENERAL'
    )
    
    # Response Tracking
    staff_responded = models.BooleanField(default=False)
    responder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='family_messages_responded'
    )
    response_text = models.TextField(blank=True)
    response_date = models.DateTimeField(null=True, blank=True)
    
    # Audit Fields
    sent_date = models.DateTimeField(auto_now_add=True)
    read_by_staff = models.BooleanField(default=False)
    read_date = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(
        max_length=20,
        choices=[
            ('LOW', 'Low Priority'),
            ('MEDIUM', 'Medium Priority'),
            ('HIGH', 'High Priority'),
            ('URGENT', 'Urgent'),
        ],
        default='MEDIUM'
    )
    
    class Meta:
        ordering = ['-sent_date']
        verbose_name = 'Family Message'
        verbose_name_plural = 'Family Messages'
        indexes = [
            models.Index(fields=['care_home', '-sent_date']),
            models.Index(fields=['resident', '-sent_date']),
            models.Index(fields=['staff_responded', '-sent_date']),
        ]
    
    def __str__(self):
        return f"{self.subject} from {self.family_member.get_full_name()} ({self.sent_date})"
    
    def days_since_sent(self):
        """Calculate days since message was sent"""
        delta = timezone.now() - self.sent_date
        return delta.days
    
    def response_time_days(self):
        """Calculate days from send to response"""
        if self.response_date:
            delta = self.response_date - self.sent_date
            return delta.days
        return None


class FamilyPortalActivity(models.Model):
    """
    Audit log for family portal activity.
    Tracks all family member interactions for security and compliance.
    """
    family_member = models.ForeignKey(
        FamilyMember,
        on_delete=models.CASCADE,
        related_name='portal_activity'
    )
    activity_type = models.CharField(
        max_length=50,
        choices=[
            ('LOGIN', 'Login'),
            ('LOGOUT', 'Logout'),
            ('VIEW_DASHBOARD', 'Viewed Dashboard'),
            ('VIEW_SURVEYS', 'Viewed Surveys'),
            ('COMPLETE_SURVEY', 'Completed Survey'),
            ('SEND_MESSAGE', 'Sent Message'),
            ('VIEW_MESSAGE', 'Viewed Message'),
            ('DOWNLOAD_DOCUMENT', 'Downloaded Document'),
            ('VIEW_CARE_PLAN', 'Viewed Care Plan'),
        ]
    )
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Family Portal Activity'
        verbose_name_plural = 'Family Portal Activities'
        indexes = [
            models.Index(fields=['family_member', '-timestamp']),
            models.Index(fields=['activity_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.family_member.get_full_name()} - {self.get_activity_type_display()} ({self.timestamp})"
