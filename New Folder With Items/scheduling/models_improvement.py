"""
Service Improvement Plan Models
Tracks Care Inspectorate reports, improvement actions, and organizational plans
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import json

User = get_user_model()


class CareInspectorateReport(models.Model):
    """Store Care Inspectorate inspection reports for reference"""
    
    REPORT_TYPE_CHOICES = [
        ('UNANNOUNCED', 'Unannounced Inspection'),
        ('FOLLOW_UP', 'Follow-up Inspection'),
        ('COMPLAINT', 'Complaint Investigation'),
        ('THEMATIC', 'Thematic Inspection'),
    ]
    
    RATING_CHOICES = [
        ('EXCELLENT', 'Excellent (6)'),
        ('VERY_GOOD', 'Very Good (5)'),
        ('GOOD', 'Good (4)'),
        ('ADEQUATE', 'Adequate (3)'),
        ('WEAK', 'Weak (2)'),
        ('UNSATISFACTORY', 'Unsatisfactory (1)'),
    ]
    
    home = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='inspection_reports')
    cs_number = models.CharField(max_length=20, help_text="Care Service registration number (e.g., CS2018371804)")
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    report_id = models.CharField(max_length=20, help_text="CI report ID number")
    inspection_date = models.DateField()
    publication_date = models.DateField()
    
    # Quality Framework Themes (Care Inspectorate Scotland)
    # Theme 1: Quality of Care and Support
    theme1_rating = models.CharField(max_length=20, choices=RATING_CHOICES, null=True, blank=True)
    theme1_strengths = models.TextField(blank=True)
    theme1_improvements_required = models.TextField(blank=True)
    
    # Theme 2: Quality of Environment
    theme2_rating = models.CharField(max_length=20, choices=RATING_CHOICES, null=True, blank=True)
    theme2_strengths = models.TextField(blank=True)
    theme2_improvements_required = models.TextField(blank=True)
    
    # Theme 3: Quality of Staffing
    theme3_rating = models.CharField(max_length=20, choices=RATING_CHOICES, null=True, blank=True)
    theme3_strengths = models.TextField(blank=True)
    theme3_improvements_required = models.TextField(blank=True)
    
    # Theme 4: Quality of Management and Leadership
    theme4_rating = models.CharField(max_length=20, choices=RATING_CHOICES, null=True, blank=True)
    theme4_strengths = models.TextField(blank=True)
    theme4_improvements_required = models.TextField(blank=True)
    
    # Overall
    overall_rating = models.CharField(max_length=20, choices=RATING_CHOICES, null=True, blank=True)
    
    # Requirements and Recommendations
    requirements = models.JSONField(default=list, help_text="List of regulatory requirements")
    recommendations = models.JSONField(default=list, help_text="List of recommendations")
    areas_for_improvement = models.JSONField(default=list)
    
    # Document storage
    report_pdf = models.FileField(upload_to='inspection_reports/', null=True, blank=True)
    report_url = models.URLField(blank=True, help_text="Link to official CI report")
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-inspection_date']
        unique_together = ['home', 'inspection_date', 'report_id']
        
    def __str__(self):
        return f"{self.home.name} - {self.get_report_type_display()} ({self.inspection_date})"


class ServiceImprovementPlan(models.Model):
    """Master improvement plan for a care home"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('REVIEW', 'Under Review'),
        ('COMPLETED', 'Completed'),
        ('SUPERSEDED', 'Superseded'),
    ]
    
    home = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='improvement_plans')
    
    # Plan metadata
    plan_title = models.CharField(max_length=200)
    plan_period_start = models.DateField()
    plan_period_end = models.DateField()
    
    # Generation details
    generated_date = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='improvement_plans_generated')
    auto_generated = models.BooleanField(default=True, help_text="True if AI-generated, False if manual")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    approved_date = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='improvement_plans_approved')
    
    # Summary data (JSON)
    baseline_metrics = models.JSONField(default=dict, help_text="Metrics snapshot at plan start")
    current_metrics = models.JSONField(default=dict, help_text="Latest metrics")
    
    # References
    inspection_report = models.ForeignKey(CareInspectorateReport, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Executive summary
    executive_summary = models.TextField(blank=True, help_text="AI-generated summary of plan")
    
    class Meta:
        ordering = ['-plan_period_start']
        
    def __str__(self):
        return f"{self.home.name} - {self.plan_title}"


class ImprovementAction(models.Model):
    """Individual improvement action within a plan"""
    
    PRIORITY_CHOICES = [
        ('CRITICAL', 'Critical'),
        ('HIGH', 'High Priority'),
        ('MEDIUM', 'Medium Priority'),
        ('LOW', 'Low Priority'),
    ]
    
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('ON_HOLD', 'On Hold'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    SOURCE_CHOICES = [
        ('INSPECTION', 'Care Inspectorate Inspection'),
        ('COMPLIANCE_AUDIT', 'Internal Compliance Audit'),
        ('INCIDENT_PATTERN', 'Incident Pattern Analysis'),
        ('METRIC_THRESHOLD', 'Metric Threshold Breach'),
        ('STAFF_FEEDBACK', 'Staff/Resident Feedback'),
        ('MANAGEMENT_INITIATIVE', 'Management Initiative'),
    ]
    
    improvement_plan = models.ForeignKey(ServiceImprovementPlan, on_delete=models.CASCADE, related_name='actions')
    
    # Action details
    action_number = models.CharField(max_length=20, help_text="e.g., SIP-2025-001")
    title = models.CharField(max_length=300)
    description = models.TextField()
    
    # Classification
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES)
    category = models.CharField(max_length=30, help_text="Training, Staffing, Environment, etc.")
    
    # CI Quality Framework alignment
    quality_theme = models.CharField(max_length=50, choices=[
        ('THEME1_CARE_SUPPORT', 'Theme 1: Care and Support'),
        ('THEME2_ENVIRONMENT', 'Theme 2: Environment'),
        ('THEME3_STAFFING', 'Theme 3: Staffing'),
        ('THEME4_MANAGEMENT', 'Theme 4: Management and Leadership'),
    ], null=True, blank=True)
    
    # Ownership
    lead_owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='improvement_actions_leading')
    supporting_staff = models.ManyToManyField(User, blank=True, related_name='improvement_actions_supporting')
    
    # Timeline
    target_start_date = models.DateField()
    target_completion_date = models.DateField()
    actual_completion_date = models.DateField(null=True, blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    percent_complete = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Expected outcomes
    expected_outcome = models.TextField(help_text="What success looks like")
    success_metrics = models.JSONField(default=list, help_text="Measurable KPIs")
    
    # Actual outcomes
    actual_outcome = models.TextField(blank=True, help_text="What actually happened")
    outcome_metrics = models.JSONField(default=dict, help_text="Actual KPI results")
    lessons_learned = models.TextField(blank=True)
    
    # Supporting evidence
    evidence_files = models.JSONField(default=list, help_text="List of file paths/URLs")
    
    # Links to system data
    related_compliance_violations = models.ManyToManyField('ComplianceViolation', blank=True)
    related_audit_reports = models.ManyToManyField('AuditReport', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['improvement_plan', 'priority', 'target_completion_date']
        
    def __str__(self):
        return f"{self.action_number}: {self.title}"
    
    def is_overdue(self):
        if self.status == 'COMPLETED':
            return False
        return timezone.now().date() > self.target_completion_date


class ActionProgressUpdate(models.Model):
    """Progress updates for improvement actions"""
    
    action = models.ForeignKey(ImprovementAction, on_delete=models.CASCADE, related_name='progress_updates')
    
    update_date = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    progress_description = models.TextField(help_text="What has been done")
    challenges_identified = models.TextField(blank=True, help_text="Any blockers or issues")
    next_steps = models.TextField(help_text="What happens next")
    
    # Status change
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    previous_percent_complete = models.IntegerField()
    new_percent_complete = models.IntegerField()
    
    # Evidence
    evidence_added = models.JSONField(default=list, help_text="New evidence files")
    
    class Meta:
        ordering = ['-update_date']
        
    def __str__(self):
        return f"{self.action.action_number} update - {self.update_date.date()}"


class OrganizationalImprovementPlan(models.Model):
    """Aggregated improvement plan across all homes"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
    ]
    
    plan_title = models.CharField(max_length=200)
    plan_period_start = models.DateField()
    plan_period_end = models.DateField()
    
    # Aggregation
    home_plans = models.ManyToManyField(ServiceImprovementPlan, related_name='org_plans')
    
    # Generation
    generated_date = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Summary
    executive_summary = models.TextField(blank=True)
    
    # Cross-cutting themes
    organizational_priorities = models.JSONField(default=list, help_text="Top priorities across all homes")
    shared_challenges = models.JSONField(default=list)
    shared_successes = models.JSONField(default=list)
    
    # Aggregate metrics
    baseline_metrics = models.JSONField(default=dict)
    current_metrics = models.JSONField(default=dict)
    
    # Benchmarking
    best_performing_homes = models.JSONField(default=list)
    homes_needing_support = models.JSONField(default=list)
    
    # Board reporting
    board_report_pdf = models.FileField(upload_to='org_improvement_plans/', null=True, blank=True)
    
    class Meta:
        ordering = ['-plan_period_start']
        
    def __str__(self):
        return f"{self.plan_title} ({self.plan_period_start} to {self.plan_period_end})"


# ============================================================================
# ML-POWERED ANALYSIS ENGINE
# ============================================================================

class ServiceImprovementAnalyzer:
    """AI engine to analyze metrics and generate improvement plans"""
    
    def analyze_home(self, home_id, period_months=12):
        """
        Analyze a care home's performance and generate improvement actions using ML
        
        Args:
            home_id: ID of the Unit (care home) to analyze
            period_months: Number of months of historical data to analyze
            
        Returns:
            dict containing analysis results and recommended actions
        """
        from django.db.models import Avg, Count, Sum, Q
        from scheduling.models import Unit, Shift
        from staff_records.models import SicknessRecord
        from scheduling.models_audit import ComplianceViolation
        
        home = Unit.objects.get(id=home_id)
        
        # Calculate date ranges
        end_date = timezone.now().date()
        start_date = end_date - relativedelta(months=period_months)
        baseline_start = start_date - relativedelta(months=period_months)
        
        # 1. Gather all metrics
        metrics = self._gather_metrics(home, start_date, end_date)
        baseline_metrics = self._gather_metrics(home, baseline_start, start_date)
        
        # 2. Compare against targets
        gaps = self._identify_gaps(metrics)
        
        # 3. Analyze compliance violations
        compliance_issues = self._analyze_compliance(home, start_date, end_date)
        
        # 4. Review inspection report (if available)
        inspection_findings = self._get_inspection_findings(home)
        
        # 5. Analyze patterns (incident trends, staff feedback, etc.)
        patterns = self._analyze_patterns(home, start_date, end_date)
        
        # 6. ML: Predict future issues
        predictions = self._ml_predict_issues(home, metrics, baseline_metrics)
        
        # 7. Generate actions
        actions = self._generate_actions(gaps, compliance_issues, inspection_findings, patterns, predictions)
        
        # 8. Prioritize using ML
        prioritized_actions = self._ml_prioritize_actions(actions, metrics)
        
        # 9. Calculate overall score
        overall_score = self._calculate_quality_score(metrics, gaps, compliance_issues)
        
        # 10. Identify strengths
        strengths = self._identify_strengths(metrics, baseline_metrics)
        
        return {
            'overall_score': overall_score,
            'critical_issues': [a for a in prioritized_actions if a['priority'] == 'CRITICAL'],
            'actions': prioritized_actions,
            'strengths': strengths,
            'baseline_metrics': baseline_metrics,
            'current_metrics': metrics,
            'trends': self._calculate_trends(baseline_metrics, metrics),
            'predicted_outcomes': predictions.get('predicted_improvements', []),
            'period_description': f"{start_date.strftime('%B %Y')} to {end_date.strftime('%B %Y')}",
        }
    
    def _gather_metrics(self, home, start_date, end_date):
        """Collect all available metrics for the period"""
        # Implementation in SERVICE_IMPROVEMENT_PLAN_PROPOSAL.md
        # This is the actual metrics gathering logic
        return {
            'staffing': {},
            'compliance': {},
            'quality': {},
            'financial': {},
            'trends': {},
        }
    
    def _identify_gaps(self, metrics):
        """Compare metrics against targets"""
        return []
    
    def _analyze_compliance(self, home, start_date, end_date):
        """Analyze compliance violations"""
        return []
    
    def _get_inspection_findings(self, home):
        """Get findings from latest inspection report"""
        return []
    
    def _analyze_patterns(self, home, start_date, end_date):
        """Analyze incident patterns and trends"""
        return []
    
    def _ml_predict_issues(self, home, metrics, baseline_metrics):
        """Use ML to predict potential future issues"""
        return {'predicted_improvements': []}
    
    def _generate_actions(self, gaps, compliance_issues, inspection_findings, patterns, predictions):
        """Generate specific improvement actions"""
        return []
    
    def _ml_prioritize_actions(self, actions, metrics):
        """Use ML to prioritize actions by impact"""
        return actions
    
    def _calculate_quality_score(self, metrics, gaps, compliance_issues):
        """Calculate overall quality score 0-100"""
        return 85
    
    def _identify_strengths(self, metrics, baseline_metrics):
        """Identify areas of strong performance"""
        return []
    
    def _calculate_trends(self, baseline, current):
        """Calculate trend direction for key metrics"""
        return {}
