"""
Recent Activity Feed Enhancement - Task 55
Real-time activity tracking with WebSocket support, enhanced UI, and dashboard widgets
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

User = get_user_model()


class RecentActivity(models.Model):
    """Enhanced activity tracking with icons, colors, and real-time updates"""
    
    ACTIVITY_CATEGORIES = [
        ('shift', 'Shift Management'),
        ('staff', 'Staff Management'),
        ('leave', 'Leave Requests'),
        ('training', 'Training & Development'),
        ('document', 'Documents'),
        ('compliance', 'Compliance'),
        ('system', 'System Events'),
        ('workflow', 'Workflows'),
        ('communication', 'Communications'),
    ]
    
    ACTIVITY_TYPES = [
        # Shift activities
        ('shift_created', 'Shift Created'),
        ('shift_updated', 'Shift Updated'),
        ('shift_deleted', 'Shift Deleted'),
        ('shift_assigned', 'Shift Assigned'),
        ('shift_cancelled', 'Shift Cancelled'),
        ('shift_filled', 'Shift Filled'),
        
        # Staff activities
        ('staff_added', 'Staff Added'),
        ('staff_updated', 'Staff Updated'),
        ('staff_deleted', 'Staff Deleted'),
        ('staff_activated', 'Staff Activated'),
        ('staff_deactivated', 'Staff Deactivated'),
        
        # Leave activities
        ('leave_requested', 'Leave Requested'),
        ('leave_approved', 'Leave Approved'),
        ('leave_rejected', 'Leave Rejected'),
        ('leave_cancelled', 'Leave Cancelled'),
        
        # Training activities
        ('training_assigned', 'Training Assigned'),
        ('training_completed', 'Training Completed'),
        ('training_expired', 'Training Expired'),
        ('certification_earned', 'Certification Earned'),
        
        # Document activities
        ('document_uploaded', 'Document Uploaded'),
        ('document_updated', 'Document Updated'),
        ('document_deleted', 'Document Deleted'),
        ('document_shared', 'Document Shared'),
        
        # Compliance activities
        ('compliance_alert', 'Compliance Alert'),
        ('compliance_resolved', 'Compliance Resolved'),
        ('review_completed', 'Review Completed'),
        
        # Workflow activities
        ('workflow_started', 'Workflow Started'),
        ('workflow_completed', 'Workflow Completed'),
        ('workflow_failed', 'Workflow Failed'),
        
        # Communication activities
        ('notification_sent', 'Notification Sent'),
        ('email_sent', 'Email Sent'),
        ('sms_sent', 'SMS Sent'),
        
        # System activities
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('settings_changed', 'Settings Changed'),
        ('error_occurred', 'Error Occurred'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Core fields
    category = models.CharField(max_length=20, choices=ACTIVITY_CATEGORIES, db_index=True)
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # User and target
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='recent_activities')
    target_user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='targeted_activities')
    
    # Metadata
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='normal', db_index=True)
    icon = models.CharField(max_length=50, default='fa-bell', help_text='FontAwesome icon class')
    color = models.CharField(max_length=20, default='primary', help_text='Bootstrap color class')
    
    # Related objects (generic tracking)
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    
    # Additional data (JSON for flexibility)
    metadata = models.JSONField(default=dict, blank=True, help_text='Additional activity data')
    
    # Organization
    care_home = models.ForeignKey('CareHome', on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    
    # Status
    is_read = models.BooleanField(default=False, db_index=True)
    is_pinned = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text='Auto-archive after this date')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['care_home', '-created_at']),
            models.Index(fields=['priority', '-created_at']),
            models.Index(fields=['is_read', '-created_at']),
            models.Index(fields=['-created_at', 'category', 'is_archived']),
        ]
        verbose_name = 'Recent Activity'
        verbose_name_plural = 'Recent Activities'
    
    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.title}"
    
    def get_icon_class(self):
        """Get FontAwesome icon class based on activity type"""
        icon_map = {
            'shift_created': 'fa-calendar-plus',
            'shift_updated': 'fa-calendar-edit',
            'shift_deleted': 'fa-calendar-times',
            'shift_assigned': 'fa-user-check',
            'shift_cancelled': 'fa-ban',
            'shift_filled': 'fa-check-circle',
            'staff_added': 'fa-user-plus',
            'staff_updated': 'fa-user-edit',
            'staff_deleted': 'fa-user-times',
            'staff_activated': 'fa-user-check',
            'staff_deactivated': 'fa-user-slash',
            'leave_requested': 'fa-calendar-alt',
            'leave_approved': 'fa-check',
            'leave_rejected': 'fa-times',
            'leave_cancelled': 'fa-ban',
            'training_assigned': 'fa-graduation-cap',
            'training_completed': 'fa-award',
            'training_expired': 'fa-exclamation-triangle',
            'certification_earned': 'fa-certificate',
            'document_uploaded': 'fa-file-upload',
            'document_updated': 'fa-file-edit',
            'document_deleted': 'fa-file-times',
            'document_shared': 'fa-share-alt',
            'compliance_alert': 'fa-exclamation-circle',
            'compliance_resolved': 'fa-check-circle',
            'review_completed': 'fa-clipboard-check',
            'workflow_started': 'fa-play-circle',
            'workflow_completed': 'fa-check-circle',
            'workflow_failed': 'fa-times-circle',
            'notification_sent': 'fa-bell',
            'email_sent': 'fa-envelope',
            'sms_sent': 'fa-sms',
            'user_login': 'fa-sign-in-alt',
            'user_logout': 'fa-sign-out-alt',
            'settings_changed': 'fa-cog',
            'error_occurred': 'fa-bug',
        }
        return icon_map.get(self.activity_type, self.icon)
    
    def get_color_class(self):
        """Get Bootstrap color class based on priority and type"""
        if self.priority == 'urgent':
            return 'danger'
        elif self.priority == 'high':
            return 'warning'
        elif self.priority == 'low':
            return 'secondary'
        
        # Category-based colors
        color_map = {
            'shift': 'primary',
            'staff': 'info',
            'leave': 'warning',
            'training': 'success',
            'document': 'secondary',
            'compliance': 'danger',
            'system': 'dark',
            'workflow': 'purple',
            'communication': 'info',
        }
        return color_map.get(self.category, self.color)
    
    def mark_as_read(self):
        """Mark activity as read"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
    
    def archive(self):
        """Archive activity"""
        if not self.is_archived:
            self.is_archived = True
            self.save(update_fields=['is_archived'])
    
    @classmethod
    def create_activity(cls, category, activity_type, title, description='', user=None, 
                       care_home=None, priority='normal', metadata=None, **kwargs):
        """Helper method to create activity with validation"""
        return cls.objects.create(
            category=category,
            activity_type=activity_type,
            title=title,
            description=description,
            user=user,
            care_home=care_home,
            priority=priority,
            metadata=metadata or {},
            **kwargs
        )
    
    @classmethod
    def get_unread_count(cls, user=None, care_home=None):
        """Get count of unread activities"""
        queryset = cls.objects.filter(is_archived=False, is_read=False)
        if user:
            queryset = queryset.filter(models.Q(user=user) | models.Q(target_user=user))
        if care_home:
            queryset = queryset.filter(care_home=care_home)
        return queryset.count()
    
    @classmethod
    def get_recent(cls, user=None, care_home=None, category=None, days=7, limit=50, include_read=True):
        """Get recent activities with filters"""
        from datetime import timedelta
        
        queryset = cls.objects.filter(is_archived=False)
        
        # Date filter
        if days:
            since = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(created_at__gte=since)
        
        # User filter
        if user:
            queryset = queryset.filter(models.Q(user=user) | models.Q(target_user=user))
        
        # Care home filter
        if care_home:
            queryset = queryset.filter(care_home=care_home)
        
        # Category filter
        if category:
            queryset = queryset.filter(category=category)
        
        # Read filter
        if not include_read:
            queryset = queryset.filter(is_read=False)
        
        # Limit
        return queryset[:limit]
    
    @classmethod
    def cleanup_old_activities(cls, days=90):
        """Archive activities older than specified days"""
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=days)
        return cls.objects.filter(created_at__lt=cutoff_date, is_archived=False).update(is_archived=True)


class ActivityFeedWidget(models.Model):
    """Configurable activity feed widgets for dashboards"""
    
    WIDGET_TYPES = [
        ('recent', 'Recent Activities'),
        ('category', 'Category-Specific Feed'),
        ('user', 'User Activities'),
        ('priority', 'Priority Activities'),
        ('unread', 'Unread Activities'),
    ]
    
    SIZE_CHOICES = [
        ('small', 'Small (5 items)'),
        ('medium', 'Medium (10 items)'),
        ('large', 'Large (20 items)'),
    ]
    
    # Widget configuration
    name = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default='medium')
    
    # Filters
    filter_category = models.CharField(max_length=20, blank=True, help_text='Filter by category')
    filter_priority = models.CharField(max_length=10, blank=True, help_text='Filter by priority')
    days_to_show = models.IntegerField(default=7, help_text='Number of days to display')
    show_read = models.BooleanField(default=True, help_text='Include read activities')
    
    # Display options
    show_icons = models.BooleanField(default=True)
    show_timestamps = models.BooleanField(default=True)
    show_user_avatars = models.BooleanField(default=True)
    auto_refresh = models.BooleanField(default=True, help_text='Auto-refresh with AJAX')
    refresh_interval = models.IntegerField(default=30, help_text='Refresh interval in seconds')
    
    # Access control
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='activity_widgets')
    care_home = models.ForeignKey('CareHome', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Ordering
    order = models.IntegerField(default=0, help_text='Display order on dashboard')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Activity Feed Widget'
        verbose_name_plural = 'Activity Feed Widgets'
    
    def __str__(self):
        return f"{self.name} ({self.get_widget_type_display()})"
    
    def get_max_items(self):
        """Get max items based on size"""
        size_map = {'small': 5, 'medium': 10, 'large': 20}
        return size_map.get(self.size, 10)
    
    def get_activities(self):
        """Get activities based on widget configuration"""
        queryset = RecentActivity.objects.filter(is_archived=False)
        
        # Apply filters
        if self.filter_category:
            queryset = queryset.filter(category=self.filter_category)
        
        if self.filter_priority:
            queryset = queryset.filter(priority=self.filter_priority)
        
        if not self.show_read:
            queryset = queryset.filter(is_read=False)
        
        # Date filter
        if self.days_to_show:
            from datetime import timedelta
            since = timezone.now() - timedelta(days=self.days_to_show)
            queryset = queryset.filter(created_at__gte=since)
        
        # Care home filter
        if self.care_home:
            queryset = queryset.filter(care_home=self.care_home)
        
        # Widget type specific filters
        if self.widget_type == 'user':
            queryset = queryset.filter(models.Q(user=self.user) | models.Q(target_user=self.user))
        elif self.widget_type == 'priority':
            queryset = queryset.filter(priority__in=['high', 'urgent'])
        elif self.widget_type == 'unread':
            queryset = queryset.filter(is_read=False)
        
        return queryset[:self.get_max_items()]
