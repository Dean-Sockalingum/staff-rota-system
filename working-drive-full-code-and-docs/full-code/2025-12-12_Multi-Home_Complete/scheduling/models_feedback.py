"""
User Feedback and Testing Questionnaire Models
================================================

Collects structured feedback from demo users to guide system iterations.

Created: 19 December 2025
"""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class DemoFeedback(models.Model):
    """
    Structured feedback from demo system testing
    """
    
    USER_ROLE_CHOICES = [
        ('STAFF', 'Care Staff Member'),
        ('SENIOR', 'Senior Carer'),
        ('MANAGER', 'Unit Manager'),
        ('HOS', 'Head of Service'),
        ('ADMIN', 'Administrative Staff'),
        ('OTHER', 'Other'),
    ]
    
    # User Information
    submitted_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='demo_feedback'
    )
    user_role = models.CharField(max_length=20, choices=USER_ROLE_CHOICES)
    care_home = models.CharField(max_length=100, blank=True, help_text="Which care home do you work at?")
    
    # Session Information
    submitted_at = models.DateTimeField(default=timezone.now)
    session_duration_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text="How long did you use the demo?"
    )
    
    # === SECTION 1: Overall Experience ===
    overall_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Overall experience (1=Poor, 5=Excellent)"
    )
    ease_of_use = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="How easy was the system to use? (1=Very Difficult, 5=Very Easy)"
    )
    would_recommend = models.BooleanField(
        default=True,
        help_text="Would you recommend this system to colleagues?"
    )
    
    # === SECTION 2: Feature-Specific Ratings ===
    rota_viewing_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Viewing shift rotas (1=Poor, 5=Excellent)"
    )
    shift_swapping_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Shift swap requests (1=Poor, 5=Excellent)"
    )
    leave_request_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Leave request process (1=Poor, 5=Excellent)"
    )
    ai_assistant_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="AI Assistant chatbot (1=Poor, 5=Excellent)"
    )
    dashboard_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Dashboard overview (1=Poor, 5=Excellent)"
    )
    mobile_experience_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Mobile/tablet experience (1=Poor, 5=Excellent)"
    )
    
    # === SECTION 3: Most/Least Useful Features ===
    most_useful_features = models.TextField(
        blank=True,
        help_text="Which features did you find most useful and why?"
    )
    least_useful_features = models.TextField(
        blank=True,
        help_text="Which features did you find least useful and why?"
    )
    missing_features = models.TextField(
        blank=True,
        help_text="What features are missing that you need?"
    )
    
    # === SECTION 4: Specific Improvements ===
    navigation_issues = models.TextField(
        blank=True,
        help_text="Any difficulties navigating the system?"
    )
    confusing_areas = models.TextField(
        blank=True,
        help_text="What was confusing or unclear?"
    )
    design_feedback = models.TextField(
        blank=True,
        help_text="Feedback on layout, colors, typography?"
    )
    
    # === SECTION 5: Current System Comparison ===
    currently_use_system = models.CharField(
        max_length=200,
        blank=True,
        help_text="What system do you currently use (if any)?"
    )
    better_than_current = models.CharField(
        max_length=20,
        choices=[
            ('MUCH_BETTER', 'Much Better'),
            ('BETTER', 'Somewhat Better'),
            ('SAME', 'About the Same'),
            ('WORSE', 'Somewhat Worse'),
            ('MUCH_WORSE', 'Much Worse'),
            ('NO_CURRENT', 'No Current System'),
        ],
        blank=True
    )
    what_makes_it_better = models.TextField(
        blank=True,
        help_text="What makes this system better/worse than your current system?"
    )
    
    # === SECTION 6: Implementation Readiness ===
    ready_to_use_daily = models.BooleanField(
        default=False,
        help_text="Is this system ready for daily use?"
    )
    concerns_before_rollout = models.TextField(
        blank=True,
        help_text="Any concerns before full rollout?"
    )
    training_needs = models.TextField(
        blank=True,
        help_text="What training would you need?"
    )
    
    # === SECTION 7: Open Feedback ===
    bugs_encountered = models.TextField(
        blank=True,
        help_text="Describe any bugs or errors you encountered"
    )
    additional_comments = models.TextField(
        blank=True,
        help_text="Any other feedback, suggestions, or comments?"
    )
    
    # === SECTION 8: Follow-up ===
    willing_to_followup = models.BooleanField(
        default=False,
        help_text="Can we contact you for follow-up questions?"
    )
    contact_email = models.EmailField(
        blank=True,
        help_text="Email for follow-up (optional)"
    )
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Demo Feedback'
        verbose_name_plural = 'Demo Feedback Responses'
    
    def __str__(self):
        role = self.get_user_role_display()
        date = self.submitted_at.strftime('%Y-%m-%d')
        return f"{role} - {date} - Overall: {self.overall_rating}/5"
    
    @property
    def average_feature_rating(self):
        """Calculate average rating across all feature ratings"""
        ratings = [
            self.rota_viewing_rating,
            self.shift_swapping_rating,
            self.leave_request_rating,
            self.ai_assistant_rating,
            self.dashboard_rating,
            self.mobile_experience_rating,
        ]
        valid_ratings = [r for r in ratings if r is not None]
        if not valid_ratings:
            return None
        return round(sum(valid_ratings) / len(valid_ratings), 1)
    
    @property
    def sentiment_score(self):
        """Simple sentiment score based on ratings and boolean fields"""
        score = self.overall_rating * 2  # Max 10 points
        score += self.ease_of_use  # Max 5 points
        if self.would_recommend:
            score += 3
        if self.ready_to_use_daily:
            score += 2
        # Max possible: 20 points
        return score
    
    @property
    def needs_attention(self):
        """Flag feedback that needs immediate attention"""
        if self.overall_rating <= 2:
            return True
        if self.ease_of_use <= 2:
            return True
        if not self.ready_to_use_daily and self.concerns_before_rollout:
            return True
        if self.bugs_encountered and len(self.bugs_encountered) > 50:
            return True
        return False


class FeatureRequest(models.Model):
    """
    Standalone feature requests from users
    """
    
    PRIORITY_CHOICES = [
        ('LOW', 'Nice to Have'),
        ('MEDIUM', 'Important'),
        ('HIGH', 'Critical'),
        ('URGENT', 'Blocking Issue'),
    ]
    
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('REVIEWING', 'Under Review'),
        ('PLANNED', 'Planned'),
        ('IN_PROGRESS', 'In Development'),
        ('TESTING', 'Testing'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Not Planned'),
    ]
    
    # Request Details
    title = models.CharField(max_length=200)
    description = models.TextField()
    requested_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='feature_requests'
    )
    requested_at = models.DateTimeField(default=timezone.now)
    
    # Categorization
    category = models.CharField(
        max_length=50,
        choices=[
            ('ROTA', 'Rota Management'),
            ('LEAVE', 'Leave Management'),
            ('STAFF', 'Staff Management'),
            ('REPORTING', 'Reports & Analytics'),
            ('MOBILE', 'Mobile Experience'),
            ('INTEGRATION', 'System Integration'),
            ('PERFORMANCE', 'Performance/Speed'),
            ('UI_UX', 'User Interface'),
            ('OTHER', 'Other'),
        ]
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )
    
    # Votes & Support
    votes = models.IntegerField(default=0)
    
    # Status Tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NEW'
    )
    assigned_to = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_feature_requests'
    )
    
    # Implementation
    estimated_hours = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Notes
    admin_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-priority', '-votes', '-requested_at']
        verbose_name = 'Feature Request'
        verbose_name_plural = 'Feature Requests'
    
    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"
