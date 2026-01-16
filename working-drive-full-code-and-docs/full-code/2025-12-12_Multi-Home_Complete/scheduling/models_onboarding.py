"""
Onboarding Models
Tracks user onboarding progress and preferences
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class OnboardingProgress(models.Model):
    """
    Tracks user progress through the onboarding wizard
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='onboarding_progress'
    )
    
    # Onboarding completion flags
    welcome_completed = models.BooleanField(default=False)
    dashboard_tour_completed = models.BooleanField(default=False)
    rota_tour_completed = models.BooleanField(default=False)
    staff_tour_completed = models.BooleanField(default=False)
    ai_intro_completed = models.BooleanField(default=False)
    mobile_tips_completed = models.BooleanField(default=False)
    
    # Completion status
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # User preferences
    skip_onboarding = models.BooleanField(default=False)
    show_tooltips = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Onboarding Progress'
        verbose_name_plural = 'Onboarding Progress'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {'Completed' if self.completed else 'In Progress'}"
    
    @property
    def completion_percentage(self):
        """Calculate completion percentage"""
        total_steps = 6
        completed_steps = sum([
            self.welcome_completed,
            self.dashboard_tour_completed,
            self.rota_tour_completed,
            self.staff_tour_completed,
            self.ai_intro_completed,
            self.mobile_tips_completed,
        ])
        return int((completed_steps / total_steps) * 100)
    
    def mark_step_complete(self, step_name):
        """Mark a specific step as complete"""
        if hasattr(self, f'{step_name}_completed'):
            setattr(self, f'{step_name}_completed', True)
            self.check_full_completion()
            self.save()
    
    def check_full_completion(self):
        """Check if all steps are complete and update status"""
        if (self.welcome_completed and 
            self.dashboard_tour_completed and 
            self.rota_tour_completed and 
            self.staff_tour_completed and 
            self.ai_intro_completed and 
            self.mobile_tips_completed):
            
            if not self.completed:
                self.completed = True
                self.completed_at = timezone.now()
    
    def reset_onboarding(self):
        """Reset all onboarding progress"""
        self.welcome_completed = False
        self.dashboard_tour_completed = False
        self.rota_tour_completed = False
        self.staff_tour_completed = False
        self.ai_intro_completed = False
        self.mobile_tips_completed = False
        self.completed = False
        self.completed_at = None
        self.skip_onboarding = False
        self.save()


class OnboardingTourStep(models.Model):
    """
    Defines individual tour steps for the interactive guide
    """
    TOUR_CHOICES = [
        ('welcome', 'Welcome Tour'),
        ('dashboard', 'Dashboard Tour'),
        ('rota', 'Rota Tour'),
        ('staff', 'Staff Management Tour'),
        ('ai', 'AI Assistant Tour'),
        ('mobile', 'Mobile Tips Tour'),
    ]
    
    tour_name = models.CharField(max_length=50, choices=TOUR_CHOICES)
    step_number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Element to highlight (CSS selector)
    target_element = models.CharField(max_length=200, blank=True)
    
    # Tooltip position
    POSITION_CHOICES = [
        ('top', 'Top'),
        ('bottom', 'Bottom'),
        ('left', 'Left'),
        ('right', 'Right'),
        ('center', 'Center'),
    ]
    tooltip_position = models.CharField(
        max_length=10, 
        choices=POSITION_CHOICES, 
        default='bottom'
    )
    
    # Optional action
    action_text = models.CharField(max_length=100, blank=True)
    action_url = models.CharField(max_length=200, blank=True)
    
    # Ordering
    order = models.IntegerField(default=0)
    
    # Active status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['tour_name', 'order', 'step_number']
        unique_together = ['tour_name', 'step_number']
    
    def __str__(self):
        return f"{self.get_tour_name_display()} - Step {self.step_number}: {self.title}"


class UserTip(models.Model):
    """
    Contextual tips that appear based on user role and location
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Targeting
    ROLE_CHOICES = [
        ('all', 'All Users'),
        ('staff', 'Staff Only'),
        ('management', 'Management Only'),
        ('senior', 'Senior Management Only'),
    ]
    target_role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='all')
    
    # Page targeting (URL pattern)
    target_page = models.CharField(max_length=200, blank=True, help_text="URL pattern to show tip on")
    
    # Display settings
    TIP_TYPE_CHOICES = [
        ('info', 'Information'),
        ('tip', 'Helpful Tip'),
        ('warning', 'Warning'),
        ('success', 'Success Message'),
    ]
    tip_type = models.CharField(max_length=20, choices=TIP_TYPE_CHOICES, default='tip')
    
    # Icon (FontAwesome class)
    icon = models.CharField(max_length=50, default='fa-lightbulb')
    
    # Priority (higher = shown first)
    priority = models.IntegerField(default=0)
    
    # Active status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_target_role_display()})"
