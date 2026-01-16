from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class StaffProfile(models.Model):
    """Extended employment record for each staff member."""

    EMPLOYMENT_STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("SUSPENDED", "Suspended"),
        ("LEAVER", "Left Organisation"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_profile",
    )
    job_title = models.CharField(max_length=150, blank=True)
    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default="ACTIVE",
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True, help_text="Populate when the staff member leaves the organisation.")

    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_phone = models.CharField(max_length=50, blank=True)

    receives_cover_alerts = models.BooleanField(
        default=False,
        help_text="If enabled this staff member will receive cover alerts via email/SMS when shifts change.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self) -> str:
        return f"Staff profile for {self.user.full_name}"


class SicknessRecord(models.Model):
    """Tracks sickness incidents including contact history and supporting documents."""

    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("AWAITING_FIT_NOTE", "Awaiting Fit Note"),
        ("RETURNED", "Returned to Work"),
        ("CLOSED", "Closed"),
    ]

    ABSENCE_WORKING_DAYS_PER_YEAR = 260  # 5 working days * 52 weeks

    profile = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE,
        related_name="sickness_records",
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reported_sickness_records",
    )
    reported_at = models.DateTimeField(default=timezone.now)
    first_working_day = models.DateField(help_text="First working day absent due to sickness.")
    estimated_return_to_work = models.DateField(
        null=True,
        blank=True,
        help_text="Expected return-to-work date.",
    )
    actual_last_working_day = models.DateField(
        null=True,
        blank=True,
        help_text="Confirmed last day of sickness absence when known.",
    )
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default="OPEN")
    reason = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    last_contacted_at = models.DateTimeField(null=True, blank=True)
    total_working_days_sick = models.PositiveIntegerField(default=0)
    separate_sickness_count_12m = models.PositiveIntegerField(default=0)
    absence_percentage_12m = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    trigger_reached = models.BooleanField(default=False)
    trigger_outcome = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-reported_at"]

    def __str__(self) -> str:
        return f"Sickness record for {self.profile.user.full_name} ({self.reported_at.date()})"

    def save(self, *args, **kwargs):
        self._update_calculated_fields()
        super().save(*args, **kwargs)
        self._flag_shifts_as_uncovered()

    def _update_calculated_fields(self):
        """Populate rolling sickness metrics before saving."""

        if self.first_working_day and (self.actual_last_working_day or self.estimated_return_to_work):
            end_date = self.actual_last_working_day or self.estimated_return_to_work
        else:
            end_date = self.actual_last_working_day or self.estimated_return_to_work or self.first_working_day

        if self.first_working_day and end_date:
            self.total_working_days_sick = self._business_days_between(self.first_working_day, end_date)

        year_ago = (timezone.now().date() - timedelta(days=365))
        recent_records_qs = self.profile.sickness_records.filter(first_working_day__gte=year_ago)
        recent_records = list(recent_records_qs.exclude(pk=self.pk))

        include_self = bool(self.first_working_day and self.first_working_day >= year_ago)
        self.separate_sickness_count_12m = len(recent_records) + (1 if include_self else 0)

        total_days = sum(record.total_working_days_sick for record in recent_records)
        if include_self:
            total_days += self.total_working_days_sick

        if total_days and self.ABSENCE_WORKING_DAYS_PER_YEAR:
            percentage = (Decimal(total_days) / Decimal(self.ABSENCE_WORKING_DAYS_PER_YEAR)) * Decimal(100)
            self.absence_percentage_12m = percentage.quantize(Decimal("0.01"))
        else:
            self.absence_percentage_12m = 0

        self.trigger_reached = self.absence_percentage_12m >= 3 or self.separate_sickness_count_12m >= 3

    def _business_days_between(self, start_date, end_date):
        """Count working days (Mon-Fri) between two dates inclusive."""

        if start_date > end_date:
            start_date, end_date = end_date, start_date

        day_count = 0
        current = start_date
        while current <= end_date:
            if current.weekday() < 5:
                day_count += 1
            current += timedelta(days=1)
        return day_count

    def _flag_shifts_as_uncovered(self):
        """Mark relevant rota entries as uncovered when sickness is logged."""

        user = getattr(self.profile, "user", None)
        if not user:
            return

        from scheduling.models import Shift  # Local import to avoid circular dependency

        end_date = self.actual_last_working_day or self.estimated_return_to_work or self.first_working_day
        if not self.first_working_day or not end_date:
            return

        Shift.objects.filter(
            user=user,
            date__gte=self.first_working_day,
            date__lte=end_date,
        ).update(status='UNCOVERED')


class MedicalCertificate(models.Model):
    """Supporting documents uploaded against a sickness record."""

    sickness_record = models.ForeignKey(
        SicknessRecord,
        on_delete=models.CASCADE,
        related_name="medical_certificates",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_medical_certificates",
    )
    file = models.FileField(upload_to="medical_certificates/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return f"Medical certificate for {self.sickness_record.profile.user.full_name}"


class ContactLogEntry(models.Model):
    """Chronological record of management contact with the staff member."""

    CONTACT_METHOD_CHOICES = [
        ("PHONE", "Phone"),
        ("SMS", "SMS"),
        ("EMAIL", "Email"),
        ("IN_PERSON", "In person"),
        ("OTHER", "Other"),
    ]

    profile = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE,
        related_name="contact_log",
    )
    sickness_record = models.ForeignKey(
        SicknessRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_entries",
        help_text="Optional link if the contact relates to an active sickness record.",
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff_contact_entries",
    )
    contact_method = models.CharField(max_length=20, choices=CONTACT_METHOD_CHOICES, default="PHONE")
    contact_datetime = models.DateTimeField(default=timezone.now)
    summary = models.TextField(help_text="Brief summary of the conversation or attempt.")
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-contact_datetime"]

    def __str__(self) -> str:
        return f"Contact with {self.profile.user.full_name} on {self.contact_datetime:%Y-%m-%d %H:%M}"


class AnnualLeaveEntitlement(models.Model):
    """Annual leave entitlement record with running balance and audit trail."""
    
    profile = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE,
        related_name="leave_entitlements",
    )
    leave_year_start = models.DateField(
        help_text="Start date of this leave year (e.g., 1st April 2025)"
    )
    leave_year_end = models.DateField(
        help_text="End date of this leave year (e.g., 31st March 2026)"
    )
    
    # Hours-based tracking for accurate pro-rata calculations
    total_entitlement_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Total annual leave entitlement in hours (e.g., 196 hours = 28 days × 7 hours)"
    )
    contracted_hours_per_week = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('35.00'),
        help_text="Contracted working hours per week for pro-rata calculations"
    )
    
    # Calculated fields - updated automatically
    hours_used = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total hours of leave used (approved requests)"
    )
    hours_pending = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total hours in pending requests"
    )
    hours_remaining = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Hours remaining = entitlement - used - pending"
    )
    
    # Carryover from previous year
    carryover_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Hours carried over from previous leave year"
    )
    carryover_expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date by which carried over leave must be used"
    )
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_leave_entitlements",
    )
    
    class Meta:
        ordering = ["-leave_year_start"]
        unique_together = [["profile", "leave_year_start"]]
    
    def __str__(self) -> str:
        return f"{self.profile.user.full_name} - Leave Year {self.leave_year_start.year}/{self.leave_year_end.year}"
    
    @property
    def total_available_hours(self):
        """Total hours including carryover"""
        return self.total_entitlement_hours + self.carryover_hours
    
    @property
    def days_entitlement(self):
        """Convert hours to days based on 12-hour shift days"""
        if self.contracted_hours_per_week == 0:
            return Decimal('0.00')
        # 35hr staff work 11.66 hrs/day, 24hr staff work 12 hrs/day
        hours_per_day = Decimal('11.66') if self.contracted_hours_per_week >= Decimal('30.00') else Decimal('12.00')
        return (self.total_entitlement_hours / hours_per_day).quantize(Decimal('0.01'))
    
    @property
    def days_used(self):
        """Convert used hours to days based on 12-hour shift days"""
        if self.contracted_hours_per_week == 0:
            return Decimal('0.00')
        # 35hr staff work 11.66 hrs/day, 24hr staff work 12 hrs/day
        hours_per_day = Decimal('11.66') if self.contracted_hours_per_week >= Decimal('30.00') else Decimal('12.00')
        return (self.hours_used / hours_per_day).quantize(Decimal('0.01'))
    
    @property
    def days_remaining(self):
        """Convert remaining hours to days based on 12-hour shift days"""
        if self.contracted_hours_per_week == 0:
            return Decimal('0.00')
        # 35hr staff work 11.66 hrs/day, 24hr staff work 12 hrs/day
        hours_per_day = Decimal('11.66') if self.contracted_hours_per_week >= Decimal('30.00') else Decimal('12.00')
        return (self.hours_remaining / hours_per_day).quantize(Decimal('0.01'))
    
    def recalculate_balance(self):
        """Recalculate hours used, pending, and remaining from related leave transactions"""
        from django.db.models import Sum, Q
        
        # Sum approved leave hours
        approved = self.leave_transactions.filter(
            transaction_type='DEDUCTION',
            related_request__status='APPROVED'
        ).aggregate(total=Sum('hours'))['total'] or Decimal('0.00')
        
        # Sum pending leave hours
        pending = self.leave_transactions.filter(
            transaction_type='DEDUCTION',
            related_request__status='PENDING'
        ).aggregate(total=Sum('hours'))['total'] or Decimal('0.00')
        
        self.hours_used = approved
        self.hours_pending = pending
        self.hours_remaining = self.total_available_hours - self.hours_used - self.hours_pending
        self.save()


class AnnualLeaveTransaction(models.Model):
    """Detailed audit trail of every leave balance change with timestamps."""
    
    TRANSACTION_TYPE_CHOICES = [
        ('INITIAL', 'Initial Entitlement'),
        ('ADJUSTMENT', 'Manual Adjustment'),
        ('CARRYOVER', 'Carryover from Previous Year'),
        ('DEDUCTION', 'Leave Request Deduction'),
        ('REFUND', 'Leave Request Cancelled/Denied'),
        ('CORRECTION', 'Error Correction'),
    ]
    
    entitlement = models.ForeignKey(
        AnnualLeaveEntitlement,
        on_delete=models.CASCADE,
        related_name="leave_transactions",
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
    )
    hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Hours added (positive) or deducted (negative)"
    )
    
    # Running balance after this transaction
    balance_after = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Hours remaining after this transaction"
    )
    
    # Reference to related leave request if applicable
    related_request = models.ForeignKey(
        'scheduling.LeaveRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leave_transactions",
        help_text="Link to the leave request that triggered this transaction"
    )
    
    # Approval tracking
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_leave_transactions",
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the request was approved (for DEDUCTION transactions)"
    )
    
    # Audit trail
    description = models.TextField(
        help_text="Description of this transaction for audit purposes"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this transaction was recorded"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_leave_transactions",
    )
    
    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self) -> str:
        sign = "+" if self.hours >= 0 else ""
        return f"{self.entitlement.profile.user.full_name} - {self.transaction_type}: {sign}{self.hours}hrs (Balance: {self.balance_after}hrs)"
    
    @property
    def hours_display(self):
        """Display hours with +/- sign"""
        return f"+{self.hours}" if self.hours > 0 else str(self.hours)
    
    @property
    def days_display(self):
        """Convert transaction hours to days for display"""
        if self.entitlement.contracted_hours_per_week == 0:
            return "0.00"
        hours_per_day = self.entitlement.contracted_hours_per_week / Decimal('5.00')
        days = (abs(self.hours) / hours_per_day).quantize(Decimal('0.01'))
        sign = "+" if self.hours > 0 else "-"
        return f"{sign}{days}"


class SicknessAbsenceSummary(models.Model):
    """Annual summary of sickness absence for each staff member with Bradford Factor."""
    
    profile = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE,
        related_name="sickness_summaries",
    )
    year = models.IntegerField(
        help_text="Calendar year for this summary"
    )
    
    # Absence metrics
    total_absence_days = models.IntegerField(
        default=0,
        help_text="Total working days lost to sickness in this year"
    )
    total_absence_instances = models.IntegerField(
        default=0,
        help_text="Number of separate sickness episodes in this year"
    )
    bradford_factor_score = models.IntegerField(
        default=0,
        help_text="Bradford Factor = Instances² × Total Days"
    )
    
    # Rolling 12-month metrics (updated monthly)
    rolling_12m_days = models.IntegerField(
        default=0,
        help_text="Total days lost in last 12 months from end of this year"
    )
    rolling_12m_instances = models.IntegerField(
        default=0,
        help_text="Number of instances in last 12 months"
    )
    rolling_12m_bradford = models.IntegerField(
        default=0,
        help_text="Bradford Factor for rolling 12 months"
    )
    
    # Trigger flags
    trigger_level_reached = models.BooleanField(
        default=False,
        help_text="True if Bradford Factor exceeds threshold (usually 200)"
    )
    trigger_threshold = models.IntegerField(
        default=200,
        help_text="Bradford Factor threshold for formal review"
    )
    
    # Review outcomes
    formal_review_conducted = models.BooleanField(default=False)
    review_date = models.DateField(null=True, blank=True)
    review_outcome = models.TextField(blank=True)
    support_plan_in_place = models.BooleanField(default=False)
    
    # Audit
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-year", "profile__user__last_name"]
        unique_together = [["profile", "year"]]
    
    def __str__(self) -> str:
        return f"{self.profile.user.full_name} - Sickness Summary {self.year} (Bradford: {self.bradford_factor_score})"
    
    def calculate_bradford_factor(self):
        """Calculate Bradford Factor: S² × D where S=instances, D=total days"""
        self.bradford_factor_score = (self.total_absence_instances ** 2) * self.total_absence_days
        self.trigger_level_reached = self.bradford_factor_score >= self.trigger_threshold
        return self.bradford_factor_score
    
    def recalculate_from_records(self, year=None):
        """Recalculate metrics from actual sickness records"""
        if year is None:
            year = self.year
        
        from datetime import date
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        
        # Get all sickness records for this year
        records = self.profile.sickness_records.filter(
            first_working_day__gte=year_start,
            first_working_day__lte=year_end,
            status__in=['RETURNED', 'CLOSED']
        )
        
        self.total_absence_instances = records.count()
        self.total_absence_days = sum(r.total_working_days_sick for r in records)
        self.calculate_bradford_factor()
        
        # Calculate rolling 12 months from year end
        rolling_start = year_end - timedelta(days=365)
        rolling_records = self.profile.sickness_records.filter(
            first_working_day__gte=rolling_start,
            first_working_day__lte=year_end,
            status__in=['RETURNED', 'CLOSED']
        )
        
        self.rolling_12m_instances = rolling_records.count()
        self.rolling_12m_days = sum(r.total_working_days_sick for r in rolling_records)
        self.rolling_12m_bradford = (self.rolling_12m_instances ** 2) * self.rolling_12m_days
        
        self.save()
