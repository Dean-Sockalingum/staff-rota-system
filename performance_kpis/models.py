"""
TQM Module 7: Performance Metrics & KPIs Models

This module provides comprehensive KPI tracking, executive dashboards, and balanced scorecard functionality
for Total Quality Management and organizational performance monitoring.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class KPICategory(models.TextChoices):
    """Categories for Key Performance Indicators aligned with Balanced Scorecard perspectives."""
    FINANCIAL = 'FINANCIAL', 'Financial'
    CUSTOMER = 'CUSTOMER', 'Customer/Service User'
    INTERNAL = 'INTERNAL', 'Internal Processes'
    LEARNING = 'LEARNING', 'Learning & Growth'
    QUALITY = 'QUALITY', 'Quality & Safety'
    COMPLIANCE = 'COMPLIANCE', 'Compliance & Regulatory'
    WORKFORCE = 'WORKFORCE', 'Workforce & Staffing'


class KPIMeasurementType(models.TextChoices):
    """Types of KPI measurements."""
    PERCENTAGE = 'PERCENTAGE', 'Percentage (%)'
    COUNT = 'COUNT', 'Count (Number)'
    CURRENCY = 'CURRENCY', 'Currency (£)'
    HOURS = 'HOURS', 'Hours'
    DAYS = 'DAYS', 'Days'
    RATIO = 'RATIO', 'Ratio'
    SCORE = 'SCORE', 'Score'


class KPITrendDirection(models.TextChoices):
    """Desired direction for KPI improvement."""
    HIGHER_BETTER = 'HIGHER_BETTER', 'Higher is Better'
    LOWER_BETTER = 'LOWER_BETTER', 'Lower is Better'
    TARGET_RANGE = 'TARGET_RANGE', 'Within Target Range'


class ReportingFrequency(models.TextChoices):
    """Frequency for KPI reporting and measurement."""
    DAILY = 'DAILY', 'Daily'
    WEEKLY = 'WEEKLY', 'Weekly'
    MONTHLY = 'MONTHLY', 'Monthly'
    QUARTERLY = 'QUARTERLY', 'Quarterly'
    ANNUALLY = 'ANNUALLY', 'Annually'


class KPIDefinition(models.Model):
    """
    Master library of KPI definitions and specifications.
    Defines what metrics are tracked, how they're measured, and their targets.
    """
    # Basic Information
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique KPI identifier (e.g., KPI-FIN-001)"
    )
    name = models.CharField(max_length=200, help_text="Short KPI name")
    description = models.TextField(help_text="Detailed description of what this KPI measures")
    
    # Classification
    category = models.CharField(
        max_length=20,
        choices=KPICategory.choices,
        help_text="Balanced Scorecard category"
    )
    measurement_type = models.CharField(
        max_length=20,
        choices=KPIMeasurementType.choices,
        help_text="Type of measurement"
    )
    trend_direction = models.CharField(
        max_length=20,
        choices=KPITrendDirection.choices,
        help_text="Desired trend direction"
    )
    
    # Calculation
    calculation_formula = models.TextField(
        help_text="Formula or method for calculating this KPI",
        blank=True
    )
    data_source = models.CharField(
        max_length=200,
        help_text="Source system or data for this KPI",
        blank=True
    )
    
    # Targets
    target_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Target value for this KPI"
    )
    threshold_red = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Red threshold (performance concern)"
    )
    threshold_amber = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amber threshold (needs improvement)"
    )
    threshold_green = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Green threshold (meets target)"
    )
    
    # Reporting
    reporting_frequency = models.CharField(
        max_length=20,
        choices=ReportingFrequency.choices,
        default='MONTHLY'
    )
    responsible_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='owned_kpis',
        help_text="Person responsible for this KPI"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    display_on_dashboard = models.BooleanField(
        default=True,
        help_text="Show this KPI on executive dashboards"
    )
    display_order = models.IntegerField(default=0, help_text="Order for dashboard display")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_kpi_definitions'
    )
    
    class Meta:
        ordering = ['category', 'display_order', 'name']
        verbose_name = 'KPI Definition'
        verbose_name_plural = 'KPI Definitions'
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_rag_status(self, value):
        """
        Determine RAG (Red/Amber/Green) status based on value and thresholds.
        """
        if value is None:
            return 'UNKNOWN'
        
        value = Decimal(str(value))
        
        if self.trend_direction == 'HIGHER_BETTER':
            if self.threshold_green and value >= self.threshold_green:
                return 'GREEN'
            elif self.threshold_amber and value >= self.threshold_amber:
                return 'AMBER'
            else:
                return 'RED'
        
        elif self.trend_direction == 'LOWER_BETTER':
            if self.threshold_green and value <= self.threshold_green:
                return 'GREEN'
            elif self.threshold_amber and value <= self.threshold_amber:
                return 'AMBER'
            else:
                return 'RED'
        
        elif self.trend_direction == 'TARGET_RANGE':
            if (self.threshold_green and self.threshold_amber and
                self.threshold_amber <= value <= self.threshold_green):
                return 'GREEN'
            else:
                return 'AMBER'
        
        return 'UNKNOWN'


class KPIMeasurement(models.Model):
    """
    Actual KPI measurements recorded over time.
    Stores historical performance data for trending and analysis.
    """
    kpi = models.ForeignKey(
        KPIDefinition,
        on_delete=models.CASCADE,
        related_name='measurements'
    )
    care_home = models.ForeignKey(
        'scheduling.CareHome',
        on_delete=models.CASCADE,
        related_name='kpi_measurements',
        null=True,
        blank=True,
        help_text="Specific care home (null for organization-wide KPIs)"
    )
    
    # Measurement Period
    measurement_date = models.DateField(help_text="Date of measurement")
    period_start = models.DateField(
        null=True,
        blank=True,
        help_text="Start of measurement period (for weekly/monthly KPIs)"
    )
    period_end = models.DateField(
        null=True,
        blank=True,
        help_text="End of measurement period"
    )
    
    # Values
    actual_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Actual measured value"
    )
    target_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Target value for this period (if different from KPI default)"
    )
    
    # Performance Analysis
    variance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Variance from target (calculated)"
    )
    variance_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Variance as percentage of target"
    )
    rag_status = models.CharField(
        max_length=10,
        choices=[
            ('GREEN', 'Green - Meets Target'),
            ('AMBER', 'Amber - Needs Improvement'),
            ('RED', 'Red - Performance Concern'),
            ('UNKNOWN', 'Unknown')
        ],
        default='UNKNOWN'
    )
    
    # Supporting Data
    numerator = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Numerator for calculated KPIs (e.g., number of incidents)"
    )
    denominator = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Denominator for calculated KPIs (e.g., total shifts)"
    )
    notes = models.TextField(blank=True, help_text="Commentary on performance")
    
    # Metadata
    recorded_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_measurements'
    )
    verified = models.BooleanField(
        default=False,
        help_text="Has this measurement been verified by management?"
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_measurements'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-measurement_date', 'kpi']
        indexes = [
            models.Index(fields=['kpi', '-measurement_date']),
            models.Index(fields=['care_home', '-measurement_date']),
            models.Index(fields=['measurement_date']),
            models.Index(fields=['rag_status']),
        ]
        unique_together = [['kpi', 'care_home', 'measurement_date']]
        verbose_name = 'KPI Measurement'
        verbose_name_plural = 'KPI Measurements'
    
    def __str__(self):
        home = f" ({self.care_home.name})" if self.care_home else ""
        return f"{self.kpi.code} - {self.measurement_date}{home}: {self.actual_value}"
    
    def save(self, *args, **kwargs):
        """Calculate variance and RAG status on save."""
        # Calculate variance
        if self.target_value is not None:
            target = self.target_value
        elif self.kpi.target_value is not None:
            target = self.kpi.target_value
        else:
            target = None
        
        if target is not None:
            self.variance = self.actual_value - target
            if target != 0:
                self.variance_percentage = (self.variance / target) * 100
        
        # Determine RAG status
        self.rag_status = self.kpi.get_rag_status(self.actual_value)
        
        super().save(*args, **kwargs)


class BalancedScorecardPerspective(models.Model):
    """
    Balanced Scorecard perspectives for strategic performance management.
    Organizes KPIs into strategic perspectives aligned with organizational goals.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    strategic_objective = models.TextField(
        help_text="High-level strategic objective for this perspective"
    )
    display_order = models.IntegerField(default=0)
    icon_class = models.CharField(
        max_length=50,
        blank=True,
        help_text="CSS icon class for dashboard display"
    )
    color_code = models.CharField(
        max_length=7,
        default='#007bff',
        help_text="Hex color code for visual identification"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Balanced Scorecard Perspective'
        verbose_name_plural = 'Balanced Scorecard Perspectives'
    
    def __str__(self):
        return self.name


class ExecutiveDashboard(models.Model):
    """
    Custom executive dashboard configurations.
    Allows different stakeholders to create personalized KPI dashboards.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='executive_dashboards'
    )
    
    # Configuration
    kpis = models.ManyToManyField(
        KPIDefinition,
        through='DashboardKPI',
        related_name='exec_dashboards'
    )
    care_homes = models.ManyToManyField(
        'scheduling.CareHome',
        blank=True,
        related_name='exec_dashboards',
        help_text="Filter to specific care homes (empty = all homes)"
    )
    
    # Display Settings
    layout = models.CharField(
        max_length=20,
        choices=[
            ('GRID', 'Grid Layout'),
            ('LIST', 'List Layout'),
            ('BALANCED_SCORECARD', 'Balanced Scorecard'),
        ],
        default='GRID'
    )
    refresh_interval = models.IntegerField(
        default=300,
        help_text="Auto-refresh interval in seconds (0 = manual only)"
    )
    
    # Sharing
    is_public = models.BooleanField(
        default=False,
        help_text="Make this dashboard visible to all users?"
    )
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='shared_dashboards',
        help_text="Specific users with access to this dashboard"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_viewed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Executive Dashboard'
        verbose_name_plural = 'Executive Dashboards'
    
    def __str__(self):
        return f"{self.name} ({self.owner.get_full_name()})"


class DashboardKPI(models.Model):
    """
    Through model for Executive Dashboard and KPI relationship.
    Controls which KPIs appear on which dashboards and their display settings.
    """
    dashboard = models.ForeignKey(ExecutiveDashboard, on_delete=models.CASCADE)
    kpi = models.ForeignKey(KPIDefinition, on_delete=models.CASCADE)
    
    # Display Configuration
    display_order = models.IntegerField(default=0)
    chart_type = models.CharField(
        max_length=20,
        choices=[
            ('GAUGE', 'Gauge Chart'),
            ('LINE', 'Line Chart'),
            ('BAR', 'Bar Chart'),
            ('AREA', 'Area Chart'),
            ('NUMBER', 'Number Only'),
        ],
        default='GAUGE'
    )
    show_trend = models.BooleanField(default=True, help_text="Show trend indicator")
    show_target = models.BooleanField(default=True, help_text="Show target line/value")
    time_range_days = models.IntegerField(
        default=90,
        help_text="Number of days of historical data to display"
    )
    
    class Meta:
        ordering = ['display_order']
        unique_together = [['dashboard', 'kpi']]
        verbose_name = 'Dashboard KPI'
        verbose_name_plural = 'Dashboard KPIs'
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.kpi.code}"


class PerformanceTarget(models.Model):
    """
    Time-bound performance targets for KPIs.
    Allows setting specific targets for different periods or strategic initiatives.
    """
    kpi = models.ForeignKey(
        KPIDefinition,
        on_delete=models.CASCADE,
        related_name='targets'
    )
    care_home = models.ForeignKey(
        'scheduling.CareHome',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='performance_targets',
        help_text="Specific care home (null for organization-wide targets)"
    )
    
    # Target Period
    target_period = models.CharField(
        max_length=20,
        choices=ReportingFrequency.choices,
        default='QUARTERLY'
    )
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Target Values
    target_value = models.DecimalField(max_digits=10, decimal_places=2)
    stretch_target = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Aspirational stretch goal"
    )
    minimum_acceptable = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum acceptable performance level"
    )
    
    # Strategic Alignment
    strategic_objective = models.TextField(
        blank=True,
        help_text="Link to organizational strategic objective"
    )
    action_plan = models.TextField(
        blank=True,
        help_text="Actions planned to achieve this target"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('DRAFT', 'Draft'),
            ('APPROVED', 'Approved'),
            ('ACTIVE', 'Active'),
            ('ACHIEVED', 'Achieved'),
            ('NOT_ACHIEVED', 'Not Achieved'),
            ('CANCELLED', 'Cancelled'),
        ],
        default='DRAFT'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_targets'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_targets'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-period_start']
        indexes = [
            models.Index(fields=['kpi', 'period_start', 'period_end']),
            models.Index(fields=['status']),
        ]
        verbose_name = 'Performance Target'
        verbose_name_plural = 'Performance Targets'
    
    def __str__(self):
        home = f" ({self.care_home.name})" if self.care_home else ""
        return f"{self.kpi.code} Target: {self.target_value} ({self.period_start} to {self.period_end}){home}"
    
    def is_current(self):
        """Check if this target is currently active."""
        today = timezone.now().date()
        return self.period_start <= today <= self.period_end and self.status == 'ACTIVE'


class BenchmarkData(models.Model):
    """
    External benchmark data for performance comparison.
    Stores industry standards, national averages, or peer group performance data.
    """
    kpi = models.ForeignKey(
        KPIDefinition,
        on_delete=models.CASCADE,
        related_name='benchmarks'
    )
    
    # Benchmark Source
    source_name = models.CharField(
        max_length=200,
        help_text="Source of benchmark data (e.g., CQC, SSSC, Industry Survey)"
    )
    source_description = models.TextField(blank=True)
    benchmark_type = models.CharField(
        max_length=20,
        choices=[
            ('NATIONAL', 'National Average'),
            ('REGIONAL', 'Regional Average'),
            ('SECTOR', 'Sector Average'),
            ('TOP_QUARTILE', 'Top Quartile'),
            ('BEST_IN_CLASS', 'Best in Class'),
            ('REGULATORY', 'Regulatory Standard'),
        ],
        default='NATIONAL'
    )
    
    # Benchmark Period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Benchmark Value
    benchmark_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Benchmark comparison value"
    )
    sample_size = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of organizations in benchmark sample"
    )
    
    # Additional Context
    methodology = models.TextField(
        blank=True,
        help_text="How the benchmark was calculated"
    )
    notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    
    class Meta:
        ordering = ['-period_start', 'kpi']
        indexes = [
            models.Index(fields=['kpi', 'period_start']),
            models.Index(fields=['benchmark_type']),
        ]
        verbose_name = 'Benchmark Data'
        verbose_name_plural = 'Benchmark Data'
    
    def __str__(self):
        return f"{self.kpi.code} - {self.source_name} ({self.benchmark_type}): {self.benchmark_value}"
