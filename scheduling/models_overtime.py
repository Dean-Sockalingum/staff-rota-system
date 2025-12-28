"""
Overtime Preference Models
Tracks staff willingness to work overtime and home preferences
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class StaffOvertimePreference(models.Model):
    """
    Tracks which staff are willing to work overtime and their home preferences
    
    Features:
    - Staff can opt in/out of OT opportunities
    - Specify which homes they're willing to work at
    - Set availability patterns (weekdays, weekends, nights)
    - Track response history for smart ranking
    """
    
    staff = models.OneToOneField(
        'scheduling.User',
        on_delete=models.CASCADE,
        related_name='overtime_preference'
    )
    
    # Opt-in status
    available_for_overtime = models.BooleanField(
        default=False,
        help_text="Is this staff member willing to work overtime?"
    )
    
    # Home preferences (many-to-many)
    willing_to_work_at = models.ManyToManyField(
        'scheduling.Unit',
        related_name='overtime_staff',
        blank=True,
        help_text="Which homes is this staff member willing to work at?"
    )
    
    # Shift type preferences
    available_early_shifts = models.BooleanField(default=True)
    available_late_shifts = models.BooleanField(default=True)
    available_night_shifts = models.BooleanField(default=True)
    
    # Day preferences
    available_weekdays = models.BooleanField(default=True)
    available_weekends = models.BooleanField(default=True)
    
    # Contact preferences
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[
            ('SMS', 'Text Message'),
            ('CALL', 'Phone Call'),
            ('EMAIL', 'Email'),
            ('APP', 'Mobile App'),
        ],
        default='SMS'
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Mobile number for SMS alerts"
    )
    
    # Response tracking for smart ranking
    total_requests_sent = models.IntegerField(default=0)
    total_requests_accepted = models.IntegerField(default=0)
    total_shifts_worked = models.IntegerField(default=0)
    last_contacted = models.DateTimeField(null=True, blank=True)
    last_worked_overtime = models.DateTimeField(null=True, blank=True)
    
    # Reliability score (calculated)
    acceptance_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
        help_text="Percentage of requests accepted"
    )
    
    # Additional constraints
    max_hours_per_week = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum OT hours willing to work per week"
    )
    
    min_notice_hours = models.IntegerField(
        default=2,
        help_text="Minimum notice required (hours)"
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Additional preferences or constraints"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Staff Overtime Preference"
        verbose_name_plural = "Staff Overtime Preferences"
        ordering = ['-acceptance_rate', '-total_shifts_worked']
    
    def __str__(self):
        status = "Available" if self.available_for_overtime else "Unavailable"
        return f"{self.staff.name} - {status} for OT"
    
    def update_acceptance_rate(self):
        """Calculate and update acceptance rate"""
        if self.total_requests_sent > 0:
            rate = (self.total_requests_accepted / self.total_requests_sent) * 100
            self.acceptance_rate = round(rate, 2)
            self.save(update_fields=['acceptance_rate'])
    
    def can_work_at_home(self, unit):
        """Check if staff is willing to work at this home"""
        return self.willing_to_work_at.filter(id=unit.id).exists()
    
    def can_work_shift_type(self, shift_type):
        """Check if staff is willing to work this shift type"""
        shift_type_lower = shift_type.lower()
        if 'early' in shift_type_lower:
            return self.available_early_shifts
        elif 'late' in shift_type_lower:
            return self.available_late_shifts
        elif 'night' in shift_type_lower:
            return self.available_night_shifts
        return True
    
    def can_work_on_date(self, date):
        """Check if staff is willing to work on this date (weekday/weekend)"""
        is_weekend = date.weekday() >= 5  # Saturday=5, Sunday=6
        if is_weekend:
            return self.available_weekends
        return self.available_weekdays
    
    def get_reliability_score(self):
        """
        Calculate reliability score based on multiple factors
        Returns 0-100 score
        """
        score = 0
        
        # Acceptance rate (40% weight)
        score += float(self.acceptance_rate) * 0.4
        
        # Recent activity (30% weight)
        if self.last_worked_overtime:
            days_since = (timezone.now() - self.last_worked_overtime).days
            if days_since <= 7:
                score += 30
            elif days_since <= 14:
                score += 20
            elif days_since <= 30:
                score += 10
        
        # Total shifts worked (20% weight)
        if self.total_shifts_worked >= 50:
            score += 20
        elif self.total_shifts_worked >= 20:
            score += 15
        elif self.total_shifts_worked >= 10:
            score += 10
        elif self.total_shifts_worked >= 5:
            score += 5
        
        # Not recently contacted (10% weight - give others a turn)
        if self.last_contacted:
            days_since_contact = (timezone.now() - self.last_contacted).days
            if days_since_contact >= 7:
                score += 10
            elif days_since_contact >= 3:
                score += 5
        else:
            score += 10  # Never contacted = full points
        
        return min(100, round(score, 2))


class OvertimeCoverageRequest(models.Model):
    """
    Tracks overtime coverage requests sent to staff
    Helps analyze response patterns and improve targeting
    """
    
    # The shift that needs coverage
    unit = models.ForeignKey(
        'scheduling.Unit',
        on_delete=models.CASCADE,
        related_name='overtime_requests'
    )
    
    shift_date = models.DateField()
    shift_type = models.CharField(max_length=50)
    required_role = models.CharField(
        max_length=50,
        help_text="RN, SSW, HCA, etc."
    )
    
    # Request details
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_coverage_requests'
    )
    
    # Who was contacted
    staff_contacted = models.ManyToManyField(
        'scheduling.User',
        through='OvertimeCoverageResponse',
        related_name='overtime_requests_received'
    )
    
    # Outcome
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending Responses'),
            ('FILLED', 'Shift Filled'),
            ('UNFILLED', 'Could Not Fill'),
            ('CANCELLED', 'Request Cancelled'),
        ],
        default='PENDING'
    )
    
    filled_by = models.ForeignKey(
        'scheduling.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='overtime_shifts_filled'
    )
    
    filled_at = models.DateTimeField(null=True, blank=True)
    
    # Analytics
    total_contacted = models.IntegerField(default=0)
    total_responses = models.IntegerField(default=0)
    total_acceptances = models.IntegerField(default=0)
    
    time_to_fill_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text="How long it took to fill this shift (minutes)"
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Overtime Coverage Request"
        verbose_name_plural = "Overtime Coverage Requests"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.unit.name} - {self.shift_date} {self.shift_type} ({self.status})"
    
    def mark_filled(self, staff_member):
        """Mark this request as filled by a specific staff member"""
        self.status = 'FILLED'
        self.filled_by = staff_member
        self.filled_at = timezone.now()
        
        # Calculate time to fill
        time_diff = self.filled_at - self.created_at
        self.time_to_fill_minutes = int(time_diff.total_seconds() / 60)
        
        self.save()


class OvertimeCoverageResponse(models.Model):
    """
    Tracks individual staff responses to coverage requests
    Through model for the many-to-many relationship
    """
    
    request = models.ForeignKey(
        OvertimeCoverageRequest,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    
    staff = models.ForeignKey(
        'scheduling.User',
        on_delete=models.CASCADE,
        related_name='overtime_responses'
    )
    
    # When contacted
    contacted_at = models.DateTimeField(auto_now_add=True)
    contact_method = models.CharField(
        max_length=20,
        choices=[
            ('SMS', 'Text Message'),
            ('CALL', 'Phone Call'),
            ('EMAIL', 'Email'),
            ('APP', 'Mobile App'),
        ]
    )
    
    # Response
    responded_at = models.DateTimeField(null=True, blank=True)
    response = models.CharField(
        max_length=20,
        choices=[
            ('ACCEPTED', 'Accepted'),
            ('DECLINED', 'Declined'),
            ('NO_RESPONSE', 'No Response'),
        ],
        default='NO_RESPONSE'
    )
    
    decline_reason = models.CharField(
        max_length=100,
        blank=True,
        choices=[
            ('UNAVAILABLE', 'Not Available'),
            ('TOO_SHORT_NOTICE', 'Too Short Notice'),
            ('DIFFERENT_HOME', 'Prefer Different Home'),
            ('DIFFERENT_SHIFT', 'Prefer Different Shift'),
            ('PERSONAL', 'Personal Reasons'),
            ('OTHER', 'Other'),
        ]
    )
    
    # Ranking when sent (for analysis)
    reliability_score_when_sent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    
    class Meta:
        verbose_name = "Overtime Coverage Response"
        verbose_name_plural = "Overtime Coverage Responses"
        unique_together = ['request', 'staff']
        ordering = ['-contacted_at']
    
    def __str__(self):
        return f"{self.staff.name} - {self.response} ({self.request})"
