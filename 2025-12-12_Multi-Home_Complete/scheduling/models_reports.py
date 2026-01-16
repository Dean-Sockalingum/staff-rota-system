"""
Custom Report Builder Models
============================

Models for custom report templates and configurations.

Created: 30 December 2025
Task 40: Custom Report Builder
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()


class CustomReportTemplate(models.Model):
    """
    Custom report template definition.
    
    Stores report configuration including data sources, filters, grouping,
    sorting, and formatting options.
    """
    
    REPORT_TYPE_CHOICES = [
        ('STAFF', 'Staff Report'),
        ('SHIFTS', 'Shifts Report'),
        ('LEAVE', 'Leave Report'),
        ('BUDGET', 'Budget Report'),
        ('COMPLIANCE', 'Compliance Report'),
        ('CUSTOM', 'Custom Query Report'),
    ]
    
    EXPORT_FORMAT_CHOICES = [
        ('PDF', 'PDF Document'),
        ('EXCEL', 'Excel Spreadsheet'),
        ('CSV', 'CSV File'),
        ('JSON', 'JSON Data'),
    ]
    
    # Template identification
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    
    # Ownership and sharing
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='custom_created_reports'
    )
    is_public = models.BooleanField(
        default=False,
        help_text='Make this report available to all users'
    )
    shared_with_roles = models.JSONField(
        default=list,
        help_text='List of role names that can access this report'
    )
    
    # Report configuration
    data_sources = models.JSONField(
        help_text='Base model and related fields to query'
    )
    filters = models.JSONField(
        default=dict,
        help_text='Filter conditions in JSON format'
    )
    grouping = models.JSONField(
        default=dict,
        help_text='Grouping and aggregation configuration'
    )
    sorting = models.JSONField(
        default=list,
        help_text='Sorting configuration'
    )
    columns = models.JSONField(
        default=list,
        help_text='Column definitions for display'
    )
    formatting = models.JSONField(
        default=dict,
        help_text='Display formatting options'
    )
    
    # Export settings
    default_export_format = models.CharField(
        max_length=10,
        choices=EXPORT_FORMAT_CHOICES,
        default='EXCEL'
    )
    
    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, blank=True)
    schedule_config = models.JSONField(default=dict)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Usage tracking
    run_count = models.IntegerField(default=0)
    avg_execution_time = models.FloatField(default=0.0)
    last_run_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by', '-created_at']),
            models.Index(fields=['is_public']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"
    
    def increment_run_count(self, execution_time):
        """Update run statistics"""
        if self.run_count == 0:
            self.avg_execution_time = execution_time
        else:
            total_time = self.avg_execution_time * self.run_count
            self.avg_execution_time = (total_time + execution_time) / (self.run_count + 1)
        
        self.run_count += 1
        self.last_run_at = timezone.now()
        self.save()


class CustomSavedReport(models.Model):
    """
    Saved instance of a generated report.
    
    Stores the results and metadata from executing a report template.
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('GENERATING', 'Generating'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    template = models.ForeignKey(
        CustomReportTemplate,
        on_delete=models.CASCADE,
        related_name='saved_reports'
    )
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_custom_reports'
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    
    # Execution details
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    parameters = models.JSONField(
        default=dict,
        help_text='Parameters used for this report generation'
    )
    
    # Report data
    data = models.JSONField(
        default=list,
        help_text='Generated report data rows'
    )
    row_count = models.IntegerField(default=0)
    
    # Export details
    export_format = models.CharField(max_length=10, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.IntegerField(default=0)
    
    # Performance metrics
    execution_time = models.FloatField(default=0.0)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['template', '-generated_at']),
            models.Index(fields=['generated_by', '-generated_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.template.name} - {self.generated_at.strftime('%Y-%m-%d %H:%M')}"


class ReportDataSource(models.Model):
    """
    Available data sources for report building.
    
    Defines which models and fields can be queried.
    """
    
    model_name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Field definitions
    fields = models.JSONField(
        help_text='Available fields with types and labels'
    )
    relationships = models.JSONField(
        default=dict,
        help_text='Related models that can be joined'
    )
    
    # Access control
    required_permission = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Display order
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['sort_order', 'display_name']
    
    def __str__(self):
        return self.display_name


class ReportSchedule(models.Model):
    """
    Scheduled report generation and delivery.
    """
    
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
    ]
    
    template = models.OneToOneField(
        CustomReportTemplate,
        on_delete=models.CASCADE,
        related_name='schedule'
    )
    
    # Schedule configuration
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    run_time = models.TimeField()
    day_of_week = models.IntegerField(null=True, blank=True)  # 0=Monday
    day_of_month = models.IntegerField(null=True, blank=True)
    quarter_month = models.IntegerField(null=True, blank=True)  # 1-3
    year_month = models.IntegerField(null=True, blank=True)  # 1-12
    
    # Delivery configuration
    email_recipients = models.JSONField(default=list)
    export_format = models.CharField(max_length=10)
    
    # Tracking
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['next_run']
    
    def __str__(self):
        return f"{self.template.name} - {self.get_frequency_display()}"


class ReportFavorite(models.Model):
    """
    User's favorite reports for quick access.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_custom_reports'
    )
    template = models.ForeignKey(
        CustomReportTemplate,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'template']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.template.name}"
