"""
Task 50: User Preferences Models
Customizable user settings for theme, notifications, timezone, language
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
import pytz


class UserPreferences(models.Model):
    """
    User-specific preferences for personalization and notifications
    One-to-one relationship with User model
    """
    
    THEME_CHOICES = [
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode'),
        ('auto', 'Auto (System)'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('gd', 'Gaelic'),
        ('pl', 'Polish'),
        ('ro', 'Romanian'),
    ]
    
    TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.common_timezones]
    
    # User relationship
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preferences',
        primary_key=True
    )
    
    # ===== Appearance Settings =====
    theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default='light',
        help_text='Color theme preference'
    )
    
    compact_mode = models.BooleanField(
        default=False,
        help_text='Reduce padding and spacing for compact view'
    )
    
    sidebar_collapsed = models.BooleanField(
        default=False,
        help_text='Collapse sidebar by default'
    )
    
    # ===== Regional Settings =====
    language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default='en',
        help_text='Interface language'
    )
    
    timezone = models.CharField(
        max_length=50,
        choices=TIMEZONE_CHOICES,
        default='Europe/London',
        help_text='User timezone for date/time display'
    )
    
    date_format = models.CharField(
        max_length=20,
        default='DD/MM/YYYY',
        help_text='Preferred date format'
    )
    
    time_format = models.CharField(
        max_length=10,
        choices=[('12', '12-hour'), ('24', '24-hour')],
        default='24',
        help_text='Time display format'
    )
    
    # ===== Notification Preferences =====
    email_notifications = models.BooleanField(
        default=True,
        help_text='Receive email notifications'
    )
    
    notify_shift_assigned = models.BooleanField(
        default=True,
        help_text='Notify when assigned to a shift'
    )
    
    notify_shift_changed = models.BooleanField(
        default=True,
        help_text='Notify when shift is changed or cancelled'
    )
    
    notify_leave_approved = models.BooleanField(
        default=True,
        help_text='Notify when leave request is approved/rejected'
    )
    
    notify_shift_reminder = models.BooleanField(
        default=True,
        help_text='Receive shift reminders 24 hours before'
    )
    
    notify_training_due = models.BooleanField(
        default=True,
        help_text='Notify when training is due or overdue'
    )
    
    notify_new_message = models.BooleanField(
        default=True,
        help_text='Notify when receiving new messages'
    )
    
    notify_compliance_alert = models.BooleanField(
        default=True,
        help_text='Notify about compliance issues'
    )
    
    # Browser notifications (push)
    browser_notifications = models.BooleanField(
        default=False,
        help_text='Enable browser push notifications'
    )
    
    # SMS notifications (future)
    sms_notifications = models.BooleanField(
        default=False,
        help_text='Receive SMS notifications (requires phone number)'
    )
    
    # ===== Dashboard Preferences =====
    dashboard_layout = models.CharField(
        max_length=20,
        choices=[
            ('default', 'Default Layout'),
            ('compact', 'Compact Layout'),
            ('cards', 'Card-based Layout'),
        ],
        default='default',
        help_text='Dashboard layout style'
    )
    
    show_calendar_week_numbers = models.BooleanField(
        default=False,
        help_text='Show week numbers on calendars'
    )
    
    default_calendar_view = models.CharField(
        max_length=10,
        choices=[
            ('month', 'Month View'),
            ('week', 'Week View'),
            ('day', 'Day View'),
        ],
        default='month',
        help_text='Default calendar view'
    )
    
    # ===== Privacy Settings =====
    show_profile_to_others = models.BooleanField(
        default=True,
        help_text='Allow other staff to view your profile'
    )
    
    show_phone_to_others = models.BooleanField(
        default=True,
        help_text='Show phone number to other staff'
    )
    
    # ===== Accessibility Settings =====
    high_contrast = models.BooleanField(
        default=False,
        help_text='Enable high contrast mode for better visibility'
    )
    
    font_size = models.CharField(
        max_length=10,
        choices=[
            ('small', 'Small'),
            ('medium', 'Medium'),
            ('large', 'Large'),
            ('xlarge', 'Extra Large'),
        ],
        default='medium',
        help_text='Text size preference'
    )
    
    reduce_animations = models.BooleanField(
        default=False,
        help_text='Reduce animations for motion sensitivity'
    )
    
    # ===== Timestamps =====
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scheduling_user_preferences'
        verbose_name = 'User Preferences'
        verbose_name_plural = 'User Preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.get_full_name()}"
    
    def get_timezone_obj(self):
        """Get timezone object for date/time conversions"""
        return pytz.timezone(self.timezone)
    
    def localize_datetime(self, dt):
        """Convert UTC datetime to user's timezone"""
        if dt.tzinfo is None:
            dt = timezone.make_aware(dt, timezone.utc)
        return dt.astimezone(self.get_timezone_obj())
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """Get or create preferences for a user with defaults"""
        preferences, created = cls.objects.get_or_create(user=user)
        return preferences
