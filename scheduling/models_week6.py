"""
Week 6: Power User Features - Models
Dashboard widget preferences and saved search filters
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class DashboardWidgetPreference(models.Model):
    """
    User preferences for which dashboard widgets to show/hide
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='widget_preferences'
    )
    
    widget_id = models.CharField(
        max_length=50,
        help_text='Unique identifier for the widget (e.g., sickness_widget, training_widget)'
    )
    
    is_visible = models.BooleanField(
        default=True,
        help_text='Whether the widget is visible on the dashboard'
    )
    
    position = models.IntegerField(
        default=0,
        help_text='Display order (lower numbers appear first)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scheduling_dashboard_widget_preference'
        verbose_name = 'Dashboard Widget Preference'
        verbose_name_plural = 'Dashboard Widget Preferences'
        unique_together = ['user', 'widget_id']
        ordering = ['position', 'widget_id']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.widget_id} ({'visible' if self.is_visible else 'hidden'})"


class SavedSearchFilter(models.Model):
    """
    Saved search/filter presets for quick access
    """
    FILTER_TYPES = [
        ('staff', 'Staff Search'),
        ('rota', 'Rota Filter'),
        ('leave', 'Leave Requests'),
        ('training', 'Training Records'),
        ('sickness', 'Sickness Records'),
        ('reports', 'Report Filters'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_filters'
    )
    
    name = models.CharField(
        max_length=100,
        help_text='Filter name (e.g., "My Team Sickness", "This Week Rota")'
    )
    
    filter_type = models.CharField(
        max_length=20,
        choices=FILTER_TYPES,
        help_text='Type of filter/search'
    )
    
    filter_params = models.JSONField(
        help_text='Saved filter parameters as JSON'
    )
    
    is_default = models.BooleanField(
        default=False,
        help_text='Auto-apply this filter when viewing the page'
    )
    
    is_shared = models.BooleanField(
        default=False,
        help_text='Share with other users in the same care home'
    )
    
    use_count = models.IntegerField(
        default=0,
        help_text='How many times this filter has been applied'
    )
    
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When this filter was last applied'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scheduling_saved_search_filter'
        verbose_name = 'Saved Search Filter'
        verbose_name_plural = 'Saved Search Filters'
        ordering = ['-last_used', '-use_count', 'name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.name} ({self.get_filter_type_display()})"
    
    def apply(self):
        """Mark filter as used"""
        self.use_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['use_count', 'last_used'])


class BulkOperationLog(models.Model):
    """
    Log of bulk operations performed by users (for audit trail)
    """
    OPERATION_TYPES = [
        ('leave_approve', 'Bulk Leave Approval'),
        ('leave_reject', 'Bulk Leave Rejection'),
        ('training_assign', 'Bulk Training Assignment'),
        ('training_complete', 'Bulk Training Completion'),
        ('shift_assign', 'Bulk Shift Assignment'),
        ('staff_notify', 'Bulk Staff Notification'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bulk_operations'
    )
    
    operation_type = models.CharField(
        max_length=30,
        choices=OPERATION_TYPES
    )
    
    item_count = models.IntegerField(
        help_text='Number of items processed'
    )
    
    success_count = models.IntegerField(
        default=0,
        help_text='Number of successful operations'
    )
    
    failure_count = models.IntegerField(
        default=0,
        help_text='Number of failed operations'
    )
    
    details = models.JSONField(
        help_text='Operation details (IDs, reasons, etc.)'
    )
    
    executed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'scheduling_bulk_operation_log'
        verbose_name = 'Bulk Operation Log'
        verbose_name_plural = 'Bulk Operation Logs'
        ordering = ['-executed_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_operation_type_display()} ({self.success_count}/{self.item_count} successful)"
