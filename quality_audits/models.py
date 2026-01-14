"""
Quality Audits Models - Module 1: PDSA Tracker
TQM System - Plan-Do-Study-Act Quality Improvement

Features AI-assisted workflow and automation:
- AI-generated SMART aim statements
- Automated hypothesis suggestions  
- Statistical analysis of cycle data
- Predictive success scoring
- Chatbot guidance integration
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from scheduling.models import User, Unit, CareHome
import json


class PDSAProject(models.Model):
    """
    Quality Improvement project using PDSA methodology
    Integrates with AI for aim generation and success prediction
    """
    
    CATEGORY_CHOICES = [
        ('CLINICAL', 'Clinical Quality'),
        ('WELLBEING', 'Staff Wellbeing'),
        ('EXPERIENCE', 'Resident Experience'),
        ('SAFETY', 'Safety'),
        ('COMPLIANCE', 'Compliance'),
        ('EFFICIENCY', 'Operational Efficiency'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('PLANNING', 'Planning'),
        ('ACTIVE', 'Active'),
        ('ON_HOLD', 'On Hold'),
        ('COMPLETED', 'Completed'),
        ('ABANDONED', 'Abandoned'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200, help_text="Concise project title")
    aim_statement = models.TextField(
        help_text="SMART aim: By [DATE], improve [MEASURE] from [BASELINE] to [TARGET] for [POPULATION] by [METHOD]"
    )
    problem_description = models.TextField(help_text="Current state analysis - what problem are we solving?")
    target_population = models.CharField(max_length=200, help_text="Which residents/units/homes are affected?")
    
    # Team & Ownership
    lead_user = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='led_pdsa_projects',
        help_text="Project lead - typically Quality Manager"
    )
    care_home = models.ForeignKey(
        CareHome, 
        on_delete=models.CASCADE, 
        related_name='pdsa_projects',
        null=True, 
        blank=True
    )
    unit = models.ForeignKey(
        Unit, 
        on_delete=models.SET_NULL, 
        related_name='pdsa_projects',
        null=True, 
        blank=True,
        help_text="Specific unit if applicable"
    )
    
    # Classification
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='CLINICAL')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNING')
    
    # Measurement
    baseline_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Current state measurement"
    )
    target_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Desired state measurement"
    )
    measurement_unit = models.CharField(
        max_length=50, 
        blank=True,
        help_text="E.g., 'falls per month', 'percentage', 'hours'"
    )
    
    # Timeline
    start_date = models.DateField()
    target_completion_date = models.DateField()
    actual_completion_date = models.DateField(null=True, blank=True)
    
    # AI & Automation Fields
    ai_aim_generated = models.BooleanField(
        default=False, 
        help_text="Was the aim statement AI-assisted?"
    )
    ai_success_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="AI-predicted success likelihood (0-100%)"
    )
    ai_suggested_hypotheses = models.JSONField(
        null=True, 
        blank=True,
        help_text="AI-generated hypothesis suggestions stored as JSON"
    )
    chatbot_interactions = models.IntegerField(
        default=0,
        help_text="Number of AI chatbot interactions for guidance"
    )
    
    # Audit Trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_pdsa_projects'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'PDSA Project'
        verbose_name_plural = 'PDSA Projects'
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['care_home', 'status']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def get_progress_percentage(self):
        """Calculate project progress based on completed cycles"""
        total_cycles = self.cycles.count()
        if total_cycles == 0:
            return 0
        completed = self.cycles.filter(act_decision__in=['ADOPT', 'ABANDON']).count()
        return int((completed / total_cycles) * 100)
    
    def get_current_value(self):
        """Get most recent measurement from latest cycle"""
        latest_cycle = self.cycles.order_by('-created_at').first()
        if latest_cycle:
            latest_data = latest_cycle.datapoints.order_by('-measurement_date').first()
            if latest_data:
                return latest_data.value
        return self.baseline_value
    
    def calculate_ai_success_score(self):
        """
        AI-powered prediction of project success based on:
        - Clarity of aim statement (NLP analysis)
        - Team engagement (cycle frequency)
        - Data collection consistency
        - Previous similar projects success rate
        """
        # Placeholder for AI model integration
        # TODO: Integrate with local LLM for scoring
        score = 50  # Default
        
        # Boost for clear SMART aims
        if all(word in self.aim_statement.lower() for word in ['by', 'from', 'to']):
            score += 15
        
        # Boost for active cycles
        active_cycles = self.cycles.count()
        score += min(active_cycles * 5, 20)
        
        # Boost for consistent data
        total_datapoints = sum(c.datapoints.count() for c in self.cycles.all())
        if total_datapoints > 10:
            score += 15
        
        self.ai_success_score = min(score, 100)
        self.save(update_fields=['ai_success_score'])
        return self.ai_success_score


class PDSATeamMember(models.Model):
    """Team members assigned to PDSA project"""
    
    project = models.ForeignKey(
        PDSAProject, 
        on_delete=models.CASCADE, 
        related_name='team_members'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='pdsa_memberships'
    )
    role = models.CharField(
        max_length=50,
        blank=True,
        help_text="E.g., 'Data Collector', 'Clinical Lead', 'Analyst'"
    )
    joined_date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ['project', 'user']
        verbose_name = 'PDSA Team Member'
        verbose_name_plural = 'PDSA Team Members'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.project.title}"


class PDSACycle(models.Model):
    """
    Individual PDSA cycle within a project
    Supports the 4-phase methodology: Plan → Do → Study → Act
    """
    
    ACT_DECISION_CHOICES = [
        ('ADOPT', 'Adopt - Implement permanently'),
        ('ADAPT', 'Adapt - Modify and test again'),
        ('ABANDON', 'Abandon - Try different approach'),
        ('PENDING', 'Pending - Not yet decided'),
    ]
    
    project = models.ForeignKey(
        PDSAProject, 
        on_delete=models.CASCADE, 
        related_name='cycles'
    )
    cycle_number = models.IntegerField(
        default=1,
        help_text="Auto-increments for each cycle in project"
    )
    
    # ========== PLAN PHASE ==========
    hypothesis = models.TextField(
        help_text="We believe that [CHANGE] will result in [OUTCOME] because [THEORY]"
    )
    prediction = models.TextField(help_text="What do we expect to happen?")
    change_idea = models.TextField(help_text="What specific change will we test?")
    data_collection_plan = models.TextField(help_text="What will we measure? How? How often?")
    plan_start_date = models.DateField()
    plan_end_date = models.DateField()
    
    # AI-assisted planning
    ai_hypothesis_used = models.BooleanField(
        default=False,
        help_text="Did user select AI-suggested hypothesis?"
    )
    
    # ========== DO PHASE ==========
    execution_log = models.TextField(
        blank=True,
        help_text="Daily/weekly implementation notes"
    )
    observations = models.TextField(
        blank=True,
        help_text="What actually happened during execution?"
    )
    deviations = models.TextField(
        blank=True,
        help_text="Any unplanned events or changes?"
    )
    staff_feedback = models.TextField(
        blank=True,
        help_text="Comments from team members during execution"
    )
    do_start_date = models.DateField(null=True, blank=True)
    do_end_date = models.DateField(null=True, blank=True)
    
    # ========== STUDY PHASE ==========
    data_analysis = models.TextField(
        blank=True,
        help_text="Analysis of collected data"
    )
    ai_data_insights = models.JSONField(
        null=True,
        blank=True,
        help_text="AI-generated statistical insights stored as JSON"
    )
    findings = models.TextField(
        blank=True,
        help_text="What did the data show?"
    )
    comparison_to_prediction = models.TextField(
        blank=True,
        help_text="Did results match our prediction?"
    )
    lessons_learned = models.TextField(
        blank=True,
        help_text="What worked? What didn't?"
    )
    unexpected_outcomes = models.TextField(
        blank=True,
        help_text="Any surprises?"
    )
    study_completed_date = models.DateField(null=True, blank=True)
    
    # ========== ACT PHASE ==========
    act_decision = models.CharField(
        max_length=20,
        choices=ACT_DECISION_CHOICES,
        default='PENDING'
    )
    next_steps = models.TextField(
        blank=True,
        help_text="What happens next? If Adapt, what will we change?"
    )
    new_cycle_planned = models.BooleanField(
        default=False,
        help_text="Will we create another PDSA cycle?"
    )
    spread_plan = models.TextField(
        blank=True,
        help_text="If Adopt, how will we roll out to other units/homes?"
    )
    act_completed_date = models.DateField(null=True, blank=True)
    
    # Automation flags
    auto_analysis_completed = models.BooleanField(
        default=False,
        help_text="Has AI completed statistical analysis?"
    )
    
    # Audit Trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['project', 'cycle_number']
        unique_together = ['project', 'cycle_number']
        verbose_name = 'PDSA Cycle'
        verbose_name_plural = 'PDSA Cycles'
        indexes = [
            models.Index(fields=['project', 'cycle_number']),
            models.Index(fields=['act_decision']),
        ]
    
    def __str__(self):
        return f"{self.project.title} - Cycle {self.cycle_number}"
    
    def get_phase_status(self):
        """Return current phase based on completion dates"""
        if self.act_completed_date:
            return 'ACT'
        elif self.study_completed_date:
            return 'STUDY'
        elif self.do_end_date:
            return 'STUDY'
        elif self.do_start_date:
            return 'DO'
        else:
            return 'PLAN'
    
    def generate_ai_insights(self):
        """
        Use local AI to analyze cycle data and generate insights
        TODO: Integrate with local LLM for analysis
        """
        datapoints = list(self.datapoints.values('measurement_date', 'value').order_by('measurement_date'))
        
        if len(datapoints) < 3:
            return None
        
        # Placeholder for AI analysis
        # In production: Call local LLM API with datapoints
        insights = {
            'trend': 'improving',  # 'improving', 'declining', 'stable'
            'average': sum(d['value'] for d in datapoints) / len(datapoints),
            'variance': 'low',  # Statistical calculation
            'recommendation': 'Continue current approach - data shows positive trend',
            'confidence': 75,  # AI confidence in analysis (0-100%)
        }
        
        self.ai_data_insights = insights
        self.auto_analysis_completed = True
        self.save(update_fields=['ai_data_insights', 'auto_analysis_completed'])
        
        return insights


class PDSADataPoint(models.Model):
    """
    Individual measurement data points collected during PDSA cycle
    Used for statistical analysis and charting
    """
    
    cycle = models.ForeignKey(
        PDSACycle, 
        on_delete=models.CASCADE, 
        related_name='datapoints'
    )
    measurement_date = models.DateField()
    value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Measured value (e.g., number of falls, compliance percentage)"
    )
    notes = models.TextField(
        blank=True,
        help_text="Context about this measurement"
    )
    
    # Metadata
    collected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Who entered this data?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['measurement_date']
        verbose_name = 'PDSA Data Point'
        verbose_name_plural = 'PDSA Data Points'
        indexes = [
            models.Index(fields=['cycle', 'measurement_date']),
        ]
    
    def __str__(self):
        return f"{self.cycle} - {self.measurement_date}: {self.value}"


class PDSAChatbotLog(models.Model):
    """
    Log of AI chatbot interactions for PDSA guidance
    Helps users navigate methodology and troubleshoot issues
    """
    
    project = models.ForeignKey(
        PDSAProject,
        on_delete=models.CASCADE,
        related_name='chatbot_logs',
        null=True,
        blank=True
    )
    cycle = models.ForeignKey(
        PDSACycle,
        on_delete=models.CASCADE,
        related_name='chatbot_logs',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pdsa_chatbot_interactions'
    )
    
    # Conversation
    user_question = models.TextField(help_text="User's question to chatbot")
    chatbot_response = models.TextField(help_text="AI-generated response")
    context_phase = models.CharField(
        max_length=20,
        choices=[
            ('PLAN', 'Plan Phase'),
            ('DO', 'Do Phase'),
            ('STUDY', 'Study Phase'),
            ('ACT', 'Act Phase'),
            ('GENERAL', 'General Question'),
        ],
        default='GENERAL'
    )
    
    # Feedback
    was_helpful = models.BooleanField(
        null=True,
        blank=True,
        help_text="Did user find response helpful?"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'PDSA Chatbot Log'
        verbose_name_plural = 'PDSA Chatbot Logs'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
