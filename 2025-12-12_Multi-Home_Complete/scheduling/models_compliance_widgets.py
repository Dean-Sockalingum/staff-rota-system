"""
Compliance Dashboard Widgets - Task 56
Embeddable, configurable compliance monitoring widgets with real-time metrics
"""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta
from decimal import Decimal


class ComplianceMetric(models.Model):
    """
    Stores calculated compliance metrics for dashboard widgets.
    Metrics are refreshed periodically and cached for performance.
    """
    
    # Metric Categories
    CATEGORY_CHOICES = [
        ('training', 'Training Compliance'),
        ('supervision', 'Supervision Compliance'),
        ('wtd', 'Working Time Directive'),
        ('incidents', 'Incident Management'),
        ('induction', 'Induction Progress'),
        ('medication', 'Medication Administration'),
        ('safeguarding', 'Safeguarding'),
        ('care_plans', 'Care Plan Reviews'),
        ('overall', 'Overall Compliance'),
    ]
    
    # Status Indicators (Traffic Light System)
    STATUS_CHOICES = [
        ('green', 'Compliant'),         # ≥95%
        ('amber', 'At Risk'),            # 85-94%
        ('red', 'Non-Compliant'),        # <85%
    ]
    
    # Core Fields
    care_home = models.ForeignKey(
        'CareHome',
        on_delete=models.CASCADE,
        related_name='compliance_metrics',
        help_text='Care home this metric applies to (null = organization-wide)'
    )
    unit = models.ForeignKey(
        'Unit',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='compliance_metrics',
        help_text='Specific unit (optional, for unit-level metrics)'
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        db_index=True,
        help_text='Type of compliance metric'
    )
    
    # Metric Data
    metric_name = models.CharField(
        max_length=200,
        help_text='Display name for the metric (e.g., "Mandatory Training Completion")'
    )
    current_value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Current compliance percentage (0-100)'
    )
    target_value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=95.0,
        help_text='Target compliance percentage (default 95%)'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        help_text='Traffic light status based on current_value vs target'
    )
    
    # Supporting Data
    compliant_count = models.IntegerField(
        default=0,
        help_text='Number of compliant items/staff'
    )
    at_risk_count = models.IntegerField(
        default=0,
        help_text='Number of items/staff at risk (e.g., expiring soon)'
    )
    non_compliant_count = models.IntegerField(
        default=0,
        help_text='Number of non-compliant items/staff'
    )
    total_count = models.IntegerField(
        default=0,
        help_text='Total items/staff assessed'
    )
    
    # Trend Data
    previous_value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Previous period value for trend calculation'
    )
    trend_direction = models.CharField(
        max_length=10,
        choices=[
            ('up', 'Improving'),
            ('down', 'Declining'),
            ('stable', 'Stable'),
        ],
        null=True,
        blank=True,
        help_text='Trend direction compared to previous period'
    )
    
    # Metadata
    calculation_date = models.DateTimeField(
        auto_now=True,
        help_text='When this metric was last calculated'
    )
    period_start = models.DateField(
        help_text='Start date of measurement period'
    )
    period_end = models.DateField(
        help_text='End date of measurement period'
    )
    notes = models.TextField(
        blank=True,
        help_text='Additional context or alerts (e.g., "2 staff certifications expire this week")'
    )
    
    # Care Inspectorate Specific
    ci_relevant = models.BooleanField(
        default=True,
        help_text='Is this metric relevant for Care Inspectorate inspections?'
    )
    ci_theme = models.CharField(
        max_length=100,
        blank=True,
        choices=[
            ('care_wellbeing', 'Care and Wellbeing'),
            ('staff_team', 'Staff Team'),
            ('leadership', 'Leadership and Management'),
            ('environment', 'Environment'),
            ('planning', 'Planning'),
        ],
        help_text='Related Care Inspectorate quality theme'
    )
    
    class Meta:
        ordering = ['-calculation_date', 'category', 'care_home']
        verbose_name = 'Compliance Metric'
        verbose_name_plural = 'Compliance Metrics'
        indexes = [
            models.Index(fields=['care_home', 'category', '-calculation_date']),
            models.Index(fields=['unit', 'category', '-calculation_date']),
            models.Index(fields=['status', '-calculation_date']),
            models.Index(fields=['ci_relevant', 'care_home']),
        ]
    
    def __str__(self):
        home_name = self.care_home.name if self.care_home else 'All Homes'
        return f"{self.metric_name} - {home_name}: {self.current_value}%"
    
    def save(self, *args, **kwargs):
        """Auto-calculate status based on current_value vs target"""
        if self.current_value >= self.target_value:
            self.status = 'green'
        elif self.current_value >= (self.target_value - 10):  # Within 10% of target
            self.status = 'amber'
        else:
            self.status = 'red'
        
        # Calculate trend direction
        if self.previous_value is not None:
            diff = self.current_value - self.previous_value
            if diff > 1:
                self.trend_direction = 'up'
            elif diff < -1:
                self.trend_direction = 'down'
            else:
                self.trend_direction = 'stable'
        
        super().save(*args, **kwargs)
    
    def get_status_color(self):
        """Return Bootstrap color class for status"""
        return {
            'green': 'success',
            'amber': 'warning',
            'red': 'danger',
        }.get(self.status, 'secondary')
    
    def get_status_icon(self):
        """Return FontAwesome icon for status"""
        return {
            'green': 'fa-check-circle',
            'amber': 'fa-exclamation-triangle',
            'red': 'fa-times-circle',
        }.get(self.status, 'fa-question-circle')
    
    def get_trend_icon(self):
        """Return FontAwesome icon for trend"""
        return {
            'up': 'fa-arrow-up',
            'down': 'fa-arrow-down',
            'stable': 'fa-minus',
        }.get(self.trend_direction, 'fa-minus')
    
    @classmethod
    def get_latest_for_home(cls, care_home, category=None):
        """Get most recent metrics for a care home"""
        metrics = cls.objects.filter(care_home=care_home)
        if category:
            metrics = metrics.filter(category=category)
        return metrics.order_by('category', '-calculation_date').distinct('category')
    
    @classmethod
    def get_red_flags(cls, care_home=None):
        """Get all red (non-compliant) metrics"""
        metrics = cls.objects.filter(status='red')
        if care_home:
            metrics = metrics.filter(care_home=care_home)
        return metrics.order_by('-calculation_date')


class ComplianceWidget(models.Model):
    """
    Configurable compliance dashboard widgets.
    Can be embedded in various dashboards with customizable display options.
    """
    
    # Widget Types
    WIDGET_TYPE_CHOICES = [
        ('single_metric', 'Single Metric Card'),           # One large metric
        ('category_summary', 'Category Summary'),          # All metrics for one category
        ('traffic_light', 'Traffic Light Grid'),           # Grid of all metrics with colors
        ('trend_chart', 'Trend Chart'),                    # Line chart showing trends
        ('red_flags', 'Red Flags Alert'),                  # Only non-compliant metrics
        ('ci_dashboard', 'CI Inspection Dashboard'),       # Care Inspectorate themed
    ]
    
    # Display Sizes
    SIZE_CHOICES = [
        ('small', 'Small (4 cols)'),
        ('medium', 'Medium (6 cols)'),
        ('large', 'Large (8 cols)'),
        ('full', 'Full Width (12 cols)'),
    ]
    
    # Core Configuration
    name = models.CharField(
        max_length=200,
        help_text='Widget name for management (not displayed to users)'
    )
    widget_type = models.CharField(
        max_length=50,
        choices=WIDGET_TYPE_CHOICES,
        help_text='Type of widget display'
    )
    size = models.CharField(
        max_length=20,
        choices=SIZE_CHOICES,
        default='medium',
        help_text='Widget size (Bootstrap columns)'
    )
    
    # Content Filters
    care_home = models.ForeignKey(
        'CareHome',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='compliance_widgets',
        help_text='Filter to specific care home (null = all homes)'
    )
    unit = models.ForeignKey(
        'Unit',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='compliance_widgets',
        help_text='Filter to specific unit'
    )
    category_filter = models.CharField(
        max_length=50,
        blank=True,
        help_text='Show only metrics from this category (blank = all categories)'
    )
    metric_ids = models.JSONField(
        null=True,
        blank=True,
        help_text='Specific metric IDs to display (for single_metric type)'
    )
    
    # Display Options
    title = models.CharField(
        max_length=200,
        help_text='Widget title displayed to users'
    )
    show_trend = models.BooleanField(
        default=True,
        help_text='Show trend arrows/indicators'
    )
    show_counts = models.BooleanField(
        default=True,
        help_text='Show compliant/non-compliant counts'
    )
    show_ci_theme = models.BooleanField(
        default=False,
        help_text='Show Care Inspectorate theme labels'
    )
    show_last_updated = models.BooleanField(
        default=True,
        help_text='Show last calculation timestamp'
    )
    
    # Auto-Refresh
    auto_refresh = models.BooleanField(
        default=True,
        help_text='Auto-refresh widget data via AJAX'
    )
    refresh_interval = models.IntegerField(
        default=300,
        validators=[MinValueValidator(30), MaxValueValidator(3600)],
        help_text='Auto-refresh interval in seconds (30-3600, default 5 min)'
    )
    
    # Access Control
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_compliance_widgets'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Is this widget currently active?'
    )
    is_public = models.BooleanField(
        default=False,
        help_text='Can all users see this widget? (False = creator only)'
    )
    
    # Ordering
    display_order = models.IntegerField(
        default=0,
        help_text='Display order on dashboards (lower = first)'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Compliance Widget'
        verbose_name_plural = 'Compliance Widgets'
    
    def __str__(self):
        return f"{self.name} ({self.get_widget_type_display()})"
    
    def get_size_class(self):
        """Return Bootstrap column class"""
        return {
            'small': 'col-lg-4 col-md-6',
            'medium': 'col-lg-6 col-md-12',
            'large': 'col-lg-8 col-md-12',
            'full': 'col-12',
        }.get(self.size, 'col-lg-6')
    
    def get_metrics(self):
        """Get metrics for this widget based on filters"""
        from scheduling.models import ComplianceMetric
        
        # Start with all metrics
        metrics = ComplianceMetric.objects.all()
        
        # Apply filters
        if self.care_home:
            metrics = metrics.filter(care_home=self.care_home)
        if self.unit:
            metrics = metrics.filter(unit=self.unit)
        if self.category_filter:
            metrics = metrics.filter(category=self.category_filter)
        if self.metric_ids:
            metrics = metrics.filter(id__in=self.metric_ids)
        
        # Get latest for each category
        metrics = metrics.order_by('category', '-calculation_date')
        
        # For red_flags widget, only show non-compliant
        if self.widget_type == 'red_flags':
            metrics = metrics.filter(status='red')
        
        return metrics
    
    def needs_refresh(self):
        """Check if widget data needs refresh based on metric calculation dates"""
        if not self.auto_refresh:
            return False
        
        metrics = self.get_metrics()
        if not metrics.exists():
            return True
        
        # Check if any metric is older than refresh_interval
        oldest_metric = metrics.order_by('calculation_date').first()
        if oldest_metric:
            age = timezone.now() - oldest_metric.calculation_date
            return age.total_seconds() > self.refresh_interval
        
        return False
