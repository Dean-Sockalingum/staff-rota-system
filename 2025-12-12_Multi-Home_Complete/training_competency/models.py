"""
TQM Module 4: Training & Competency Enhancement Models

Extends the existing TrainingCourse/TrainingRecord system with:
- Competency frameworks and skills matrices
- Role-based training requirements
- Learning pathways and development plans
- Performance-linked competency assessments

Aligns with:
- Health Improvement Scotland (HIS) QMS Standards
- SSSC Registration Requirements
- Care Inspectorate Quality Framework
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from scheduling.models import Role, CareHome, TrainingCourse

User = get_user_model()


class CompetencyFramework(models.Model):
    """
    Skills matrix defining competencies required for different roles.
    Supports HIS QMS requirement for competency-based training.
    """
    
    COMPETENCY_LEVEL_CHOICES = [
        ('AWARENESS', 'Awareness - Basic understanding'),
        ('WORKING', 'Working - Can perform with supervision'),
        ('PROFICIENT', 'Proficient - Can perform independently'),
        ('EXPERT', 'Expert - Can teach and assess others'),
    ]
    
    COMPETENCY_TYPE_CHOICES = [
        ('CLINICAL', 'Clinical Skill'),
        ('TECHNICAL', 'Technical Skill'),
        ('BEHAVIORAL', 'Behavioral Competency'),
        ('LEADERSHIP', 'Leadership Competency'),
        ('REGULATORY', 'Regulatory Requirement'),
    ]
    
    # Competency Definition
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="e.g., CLIN-001, LEAD-005"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(
        help_text="Clear definition of what this competency means"
    )
    competency_type = models.CharField(max_length=20, choices=COMPETENCY_TYPE_CHOICES)
    
    # Assessment Criteria
    assessment_criteria = models.TextField(
        help_text="How this competency will be assessed (observable behaviors)"
    )
    evidence_required = models.TextField(
        blank=True,
        help_text="What evidence demonstrates competency (e.g., witness statements, portfolios)"
    )
    
    # Role Requirements
    required_for_roles = models.ManyToManyField(
        Role,
        through='RoleCompetencyRequirement',
        related_name='required_competencies'
    )
    
    # Related Training
    linked_training_courses = models.ManyToManyField(
        TrainingCourse,
        blank=True,
        related_name='competencies_addressed',
        help_text="Training courses that develop this competency"
    )
    
    # Validity & Review
    review_frequency_months = models.IntegerField(
        default=12,
        help_text="How often should this competency be reassessed?"
    )
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='competencies_created')
    
    class Meta:
        ordering = ['competency_type', 'code']
        verbose_name_plural = 'Competency Frameworks'
    
    def __str__(self):
        return f"{self.code}: {self.title}"


class RoleCompetencyRequirement(models.Model):
    """
    Defines which competencies are required for each role and at what level.
    Supports role-based training matrices.
    """
    
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    competency = models.ForeignKey(CompetencyFramework, on_delete=models.CASCADE)
    required_level = models.CharField(
        max_length=20,
        choices=CompetencyFramework.COMPETENCY_LEVEL_CHOICES
    )
    is_mandatory = models.BooleanField(
        default=True,
        help_text="Must be achieved before role can be performed independently"
    )
    grace_period_days = models.IntegerField(
        default=90,
        help_text="Days allowed to achieve competency after starting role"
    )
    
    class Meta:
        unique_together = ['role', 'competency']
        ordering = ['role', 'is_mandatory', 'competency']
    
    def __str__(self):
        return f"{self.role.name} requires {self.competency.title} at {self.required_level}"


class CompetencyAssessment(models.Model):
    """
    Records of competency assessments for individual staff members.
    Tracks skills development and performance over time.
    """
    
    ASSESSMENT_METHOD_CHOICES = [
        ('OBSERVATION', 'Direct Observation'),
        ('SIMULATION', 'Simulated Scenario'),
        ('WRITTEN', 'Written Test/Exam'),
        ('PORTFOLIO', 'Portfolio Review'),
        ('INTERVIEW', 'Professional Discussion'),
        ('PEER_REVIEW', 'Peer Assessment'),
    ]
    
    OUTCOME_CHOICES = [
        ('NOT_YET_STARTED', 'Not Yet Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPETENT', 'Competent'),
        ('HIGHLY_COMPETENT', 'Highly Competent'),
        ('NOT_YET_COMPETENT', 'Not Yet Competent - Further Development Needed'),
    ]
    
    # Who & What
    staff_member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='competency_assessments'
    )
    competency = models.ForeignKey(
        CompetencyFramework,
        on_delete=models.CASCADE,
        related_name='assessments'
    )
    
    # Assessment Details
    assessment_date = models.DateField(default=timezone.now)
    assessor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='tqm_competency_assessments_conducted'
    )
    assessment_method = models.CharField(max_length=20, choices=ASSESSMENT_METHOD_CHOICES)
    
    # Results
    achieved_level = models.CharField(
        max_length=20,
        choices=CompetencyFramework.COMPETENCY_LEVEL_CHOICES,
        blank=True
    )
    outcome = models.CharField(
        max_length=30,
        choices=OUTCOME_CHOICES,
        default='IN_PROGRESS'
    )
    
    # Evidence & Feedback
    evidence_description = models.TextField(
        blank=True,
        help_text="What evidence was reviewed/observed?"
    )
    assessor_comments = models.TextField(blank=True)
    staff_reflection = models.TextField(
        blank=True,
        help_text="Staff member's own reflection on their performance"
    )
    
    # Development Planning
    development_needs_identified = models.TextField(
        blank=True,
        help_text="Areas for further development"
    )
    action_plan = models.TextField(
        blank=True,
        help_text="Specific actions to address development needs"
    )
    
    # Review & Expiry
    next_review_date = models.DateField(
        null=True,
        blank=True,
        help_text="When should this competency be reassessed?"
    )
    expires_on = models.DateField(
        null=True,
        blank=True,
        help_text="Some competencies may expire if not used regularly"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-assessment_date']
        indexes = [
            models.Index(fields=['staff_member', '-assessment_date']),
            models.Index(fields=['competency', 'outcome']),
        ]
    
    def __str__(self):
        return f"{self.staff_member.get_full_name()} - {self.competency.title} ({self.outcome})"
    
    def is_current(self):
        """Check if this assessment is still valid"""
        if not self.next_review_date:
            return self.outcome in ['COMPETENT', 'HIGHLY_COMPETENT']
        return self.next_review_date >= timezone.now().date()


class TrainingMatrix(models.Model):
    """
    Role-specific training requirements matrix.
    Defines which training courses are mandatory/recommended for each role.
    """
    
    REQUIREMENT_TYPE_CHOICES = [
        ('MANDATORY', 'Mandatory - Must complete before working'),
        ('ESSENTIAL', 'Essential - Must complete within grace period'),
        ('RECOMMENDED', 'Recommended - Supports role performance'),
        ('OPTIONAL', 'Optional - Professional development'),
    ]
    
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='training_requirements')
    training_course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE)
    requirement_type = models.CharField(max_length=20, choices=REQUIREMENT_TYPE_CHOICES)
    
    # Timing
    must_complete_within_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="For ESSENTIAL training: days allowed after starting role"
    )
    must_complete_before_solo_work = models.BooleanField(
        default=False,
        help_text="Staff cannot work unsupervised until this is complete"
    )
    
    # Priority & Sequencing
    priority_order = models.IntegerField(
        default=1,
        help_text="Order in which training should be completed (1=highest priority)"
    )
    prerequisite_courses = models.ManyToManyField(
        TrainingCourse,
        blank=True,
        related_name='required_for_courses',
        help_text="Courses that must be completed first"
    )
    
    # Care Home Specific
    care_home = models.ForeignKey(
        CareHome,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Leave blank for organization-wide requirement"
    )
    
    # Notes
    rationale = models.TextField(
        blank=True,
        help_text="Why this training is required for this role"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['role', 'priority_order', 'training_course']
        unique_together = [['role', 'training_course', 'care_home']]
        verbose_name = 'Training Matrix Entry'
        verbose_name_plural = 'Training Matrix'
    
    def __str__(self):
        home_suffix = f" @ {self.care_home.name}" if self.care_home else ""
        return f"{self.role.name}: {self.training_course.name} ({self.requirement_type}){home_suffix}"


class LearningPathway(models.Model):
    """
    Structured learning and development pathways for career progression.
    Supports succession planning and professional development.
    """
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft - Being Developed'),
        ('ACTIVE', 'Active - Available for Enrollment'),
        ('UNDER_REVIEW', 'Under Review'),
        ('ARCHIVED', 'Archived - No Longer Active'),
    ]
    
    # Pathway Definition
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Target Audience
    from_role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pathways_from',
        help_text="Starting role (e.g., Care Assistant)"
    )
    to_role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pathways_to',
        help_text="Target role (e.g., Senior Carer)"
    )
    
    # Duration & Structure
    estimated_duration_months = models.IntegerField(
        help_text="Expected time to complete pathway"
    )
    total_learning_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Components
    required_competencies = models.ManyToManyField(
        CompetencyFramework,
        through='PathwayCompetency',
        related_name='pathways'
    )
    required_training = models.ManyToManyField(
        TrainingCourse,
        through='PathwayTraining',
        related_name='pathways'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    is_active = models.BooleanField(default=True)
    
    # Approval & Ownership
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pathways_owned',
        help_text="Learning & Development Manager responsible"
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pathways_approved'
    )
    approved_date = models.DateField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['from_role', 'to_role', 'title']
        verbose_name_plural = 'Learning Pathways'
    
    def __str__(self):
        return f"{self.title} ({self.from_role.name} → {self.to_role.name})"


class PathwayCompetency(models.Model):
    """Link between learning pathways and required competencies"""
    
    pathway = models.ForeignKey(LearningPathway, on_delete=models.CASCADE)
    competency = models.ForeignKey(CompetencyFramework, on_delete=models.CASCADE)
    sequence_order = models.IntegerField(default=1)
    required_level = models.CharField(
        max_length=20,
        choices=CompetencyFramework.COMPETENCY_LEVEL_CHOICES
    )
    
    class Meta:
        ordering = ['pathway', 'sequence_order']
        unique_together = ['pathway', 'competency']
    
    def __str__(self):
        return f"{self.pathway.title} - {self.competency.title} (Step {self.sequence_order})"


class PathwayTraining(models.Model):
    """Link between learning pathways and required training courses"""
    
    pathway = models.ForeignKey(LearningPathway, on_delete=models.CASCADE)
    training_course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE)
    sequence_order = models.IntegerField(default=1)
    is_mandatory = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['pathway', 'sequence_order']
        unique_together = ['pathway', 'training_course']
    
    def __str__(self):
        return f"{self.pathway.title} - {self.training_course.name} (Step {self.sequence_order})"


class StaffLearningPlan(models.Model):
    """
    Individual staff member's enrollment in a learning pathway.
    Tracks progress and completion status.
    """
    
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('ON_HOLD', 'On Hold'),
        ('COMPLETED', 'Completed'),
        ('WITHDRAWN', 'Withdrawn'),
    ]
    
    # Who & What
    staff_member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='learning_plans'
    )
    pathway = models.ForeignKey(
        LearningPathway,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    # Timeline
    enrollment_date = models.DateField(default=timezone.now)
    target_completion_date = models.DateField()
    actual_completion_date = models.DateField(null=True, blank=True)
    
    # Progress Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    percent_complete = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Support
    mentor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentees',
        help_text="Designated mentor/coach"
    )
    line_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports_learning'
    )
    
    # Notes & Reviews
    staff_notes = models.TextField(
        blank=True,
        help_text="Staff member's own notes and reflections"
    )
    manager_notes = models.TextField(
        blank=True,
        help_text="Line manager observations and support provided"
    )
    last_review_date = models.DateField(null=True, blank=True)
    next_review_date = models.DateField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-enrollment_date']
        unique_together = ['staff_member', 'pathway']
    
    def __str__(self):
        return f"{self.staff_member.get_full_name()} - {self.pathway.title} ({self.status})"
    
    def calculate_progress(self):
        """
        Calculate completion percentage based on:
        - Required training courses completed
        - Required competencies achieved
        """
        # This would be implemented with actual queries
        # For now, return stored value
        return self.percent_complete
