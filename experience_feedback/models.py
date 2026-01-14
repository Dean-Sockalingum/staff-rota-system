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
    STAFF_EXPERIENCE = 'STAFF_EXPERIENCE', 'Staff Experience'


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
