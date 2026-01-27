from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from datetime import datetime, time, timedelta

# This class manages the creation of users and superusers
class CustomUserManager(BaseUserManager):
    def create_user(self, sap, password=None, **extra_fields):
        if not sap:
            raise ValueError('The SAP number must be set')
        user = self.model(sap=sap, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, sap, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(sap, password, **extra_fields)

# Table 2: Roles
class Role(models.Model):
    ROLE_CHOICES = [
        ('OPERATIONS_MANAGER', 'Operations Manager'),
        ('SSCW', 'Senior Social Care Worker'),
        ('SCW', 'Social Care Worker'),
        ('SCA', 'Social Care Assistant'),
    ]
    
    PERMISSION_LEVEL_CHOICES = [
        ('FULL', 'Full Access - SM/OM can approve, manage rotas, view all data'),
        ('MOST', 'Most Access - SSCW can view schedules, team data, submit requests'),
        ('LIMITED', 'Limited Access - Staff can view own info, submit requests only'),
    ]
    
    name = models.CharField(max_length=100, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)
    is_management = models.BooleanField(default=False)
    is_senior_management_team = models.BooleanField(
        default=False, 
        help_text="Head of Service team member (SM, OM, HOS, IDI) with governance oversight across all homes"
    )
    can_approve_leave = models.BooleanField(default=False)
    can_manage_rota = models.BooleanField(default=False)
    required_headcount = models.IntegerField(default=0, help_text="Target number of staff required for this role")
    permission_level = models.CharField(
        max_length=20,
        choices=PERMISSION_LEVEL_CHOICES,
        default='LIMITED',
        help_text="Access level for home-specific dashboards"
    )
    
    # Color coding for role display
    COLOR_CHOICES = [
        ('#e74c3c', 'Red'),
        ('#3498db', 'Blue'), 
        ('#2ecc71', 'Green'),
        ('#9b59b6', 'Purple'),
        ('#f39c12', 'Orange'),
        ('#e67e22', 'Dark Orange'),
    ]
    color_code = models.CharField(max_length=7, choices=COLOR_CHOICES, default='#3498db')

    def save(self, *args, **kwargs):
        """Auto-set management permissions based on role name"""
        # SM, OM, and ADMIN should have full management permissions
        if self.name in ['SM', 'OM', 'ADMIN']:
            self.is_management = True
            self.can_approve_leave = True
            self.can_manage_rota = True
            self.permission_level = 'FULL'
            # ADMIN should also be senior management team
            if self.name == 'ADMIN':
                self.is_senior_management_team = True
        else:
            # All other roles should NOT have management permissions
            self.is_management = False
            if self.name not in ['SM', 'OM', 'HOS', 'IDI', 'ADMIN']:
                self.is_senior_management_team = False
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_name_display()
    
    @property
    def current_headcount(self):
        """Return current number of active staff in this role"""
        return self.user_set.filter(is_active=True).count()
    
    @property
    def staffing_percentage(self):
        """Return current staffing level as percentage of required"""
        if self.required_headcount == 0:
            return 100
        return round((self.current_headcount / self.required_headcount) * 100, 1)

# Table 1: Users (replaces the default Django user model)
class User(AbstractBaseUser, PermissionsMixin):
    TEAM_CHOICES = [
        ('A', 'Team A'),
        ('B', 'Team B'),
        ('C', 'Team C'),
    ]
    
    SHIFT_PREFERENCE_CHOICES = [
        ('DAY', 'Day Shift Preferred'),
        ('NIGHT', 'Night Shift Preferred'),
        ('NO_PREFERENCE', 'No Preference'),
        # Legacy choices for backward compatibility
        ('DAY_SENIOR', 'Day Shift (SSCW/SCW)'),
        ('DAY_ASSISTANT', 'Day Shift (SCA)'),
        ('NIGHT_SENIOR', 'Night Shift (SSCW/SCW)'),
        ('NIGHT_ASSISTANT', 'Night Shift (SCA)'),
    ]
    
    # SAP number validator - must be exactly 6 digits
    sap_validator = RegexValidator(
        regex=r'^\d{6}$',
        message='SAP number must be exactly 6 digits (e.g., 123456)',
        code='invalid_sap'
    )
    
    sap = models.CharField(
        max_length=6, 
        unique=True, 
        primary_key=True,
        validators=[sap_validator],
        help_text='6-digit SAP number (e.g., 123456)'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.ForeignKey('Unit', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_staff')
    home_unit = models.ForeignKey('Unit', on_delete=models.SET_NULL, null=True, blank=True, related_name='permanent_staff', help_text="Permanent home unit for this staff member")
    team = models.CharField(max_length=1, choices=TEAM_CHOICES, blank=True, null=True)
    shift_preference = models.CharField(max_length=15, choices=SHIFT_PREFERENCE_CHOICES, null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)  # Indexed for performance
    is_staff = models.BooleanField(default=False)
    
    # Task 22: SMS Notification Preferences
    sms_notifications_enabled = models.BooleanField(default=False, help_text='Enable SMS notifications for urgent alerts')
    sms_emergency_only = models.BooleanField(default=False, help_text='Only send SMS for emergency/critical alerts')
    sms_opted_in_date = models.DateTimeField(null=True, blank=True, help_text='Date when user opted in to SMS notifications')
    
    # Annual leave tracking
    annual_leave_allowance = models.IntegerField(default=28)  # Days per year
    annual_leave_used = models.IntegerField(default=0)
    annual_leave_year_start = models.DateField(default=timezone.now)
    
    # Shift pattern override - allows individual staff to have different shift patterns
    shifts_per_week_override = models.IntegerField(null=True, blank=True, help_text="Override default shifts per week for this staff member")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'sap'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    def clean(self):
        """Validate SAP number is exactly 6 digits"""
        super().clean()
        if self.sap:
            # Remove any whitespace
            self.sap = str(self.sap).strip()
            
            # Check if it's exactly 6 digits
            if not self.sap.isdigit() or len(self.sap) != 6:
                raise ValidationError({
                    'sap': 'SAP number must be exactly 6 digits (e.g., 123456). Please do not use alphanumeric codes like "SCW1081".'
                })
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation"""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def id(self):
        """Backward compatibility - Django code often expects 'id' field"""
        return self.pk

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.sap})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        """Return full name (compatibility method for Django's AbstractUser API)"""
        return self.full_name
    
    @property
    def annual_leave_remaining(self):
        """Calculate remaining annual leave including approved and pending requests"""
        # Get total days from approved and pending annual leave requests
        from django.db.models import Sum
        allocated_days = self.leave_requests.filter(
            leave_type='ANNUAL',
            status__in=['APPROVED', 'PENDING']
        ).aggregate(total=Sum('days_requested'))['total'] or 0
        
        return self.annual_leave_allowance - allocated_days
    
    @property
    def annual_leave_approved(self):
        """Calculate approved annual leave days"""
        from django.db.models import Sum
        return self.leave_requests.filter(
            leave_type='ANNUAL',
            status='APPROVED'
        ).aggregate(total=Sum('days_requested'))['total'] or 0
    
    @property
    def annual_leave_pending(self):
        """Calculate pending annual leave days"""
        from django.db.models import Sum
        return self.leave_requests.filter(
            leave_type='ANNUAL',
            status='PENDING'
        ).aggregate(total=Sum('days_requested'))['total'] or 0
    
    @property
    def shifts_per_week(self):
        """Number of shifts this user works per week"""
        # Use override if set, otherwise use role default
        if self.shifts_per_week_override is not None:
            return self.shifts_per_week_override
            
        # Default based on role
        if self.role:
            if self.role.name in ['SCW', 'SSCW']:
                return 3
            elif self.role.name == 'SCA':
                return 2
        return 0
    
    def has_permission_level(self, required_level):
        """Check if user has required permission level or higher"""
        if not self.role:
            return False
        
        level_hierarchy = {'FULL': 3, 'MOST': 2, 'LIMITED': 1}
        user_level = level_hierarchy.get(self.role.permission_level, 0)
        required = level_hierarchy.get(required_level, 0)
        return user_level >= required
    
    def can_access_home(self, care_home):
        """Check if user can access a specific care home's dashboard"""
        # Senior management team can access all homes
        if self.role and self.role.is_senior_management_team:
            return True
        
        # Regular staff can only access their assigned home
        if self.unit and self.unit.care_home:
            return self.unit.care_home == care_home
        
        return False
    
    @property
    def assigned_care_home(self):
        """Get the care home this user is assigned to"""
        if self.unit and self.unit.care_home:
            return self.unit.care_home
        return None
    
    @property
    def care_home(self):
        """Backward compatibility alias for assigned_care_home"""
        return self.assigned_care_home
    
    @property
    def care_home_access(self):
        """
        Backward compatibility property for legacy code expecting many-to-many care_home_access.
        Returns a QuerySet-like object that supports .add() and .all()
        """
        class CareHomeAccessCompat:
            def __init__(self, user):
                self.user = user
            
            def add(self, care_home):
                """Legacy compatibility - no-op since access is now via unit"""
                pass
            
            def all(self):
                """Returns care homes the user can access"""
                from django.db.models import Q
                if not self.user.unit or not self.user.unit.care_home:
                    return CareHome.objects.none()
                # If senior management, return all homes, else return assigned home
                if self.user.role and self.user.role.is_senior_management_team:
                    return CareHome.objects.all()
                return CareHome.objects.filter(pk=self.user.unit.care_home.pk)
        
        return CareHomeAccessCompat(self)

# Table 3: Units/Departments
class Unit(models.Model):
    UNIT_CHOICES = [
        # Orchard Grove units (9 units: 8 care + 1 MGMT)
        ('OG_BRAMLEY', 'Bramley'),
        ('OG_CHERRY', 'Cherry'),
        ('OG_GRAPE', 'Grape'),
        ('OG_ORANGE', 'Orange'),
        ('OG_PEACH', 'Peach'),
        ('OG_PEAR', 'Pear'),
        ('OG_PLUM', 'Plum'),
        ('OG_STRAWBERRY', 'Strawberry'),
        ('OG_MGMT', 'Mgmt'),
        
        # Hawthorn House units (9 units: 8 care + 1 MGMT)
        ('HH_BLUEBELL', 'Bluebell'),
        ('HH_DAISY', 'Daisy'),
        ('HH_HEATHER', 'Heather'),
        ('HH_IRIS', 'Iris'),
        ('HH_PRIMROSE', 'Primrose'),
        ('HH_SNOWDROP_SRD', 'Snowdrop (SRD)'),
        ('HH_THISTLE_SRD', 'Thistle (SRD)'),
        ('HH_VIOLET', 'Violet'),
        ('HH_MGMT', 'Mgmt'),
        
        # Meadowburn units (9 units: 8 care + 1 MGMT)
        ('MB_ASTER', 'Aster'),
        ('MB_BLUEBELL', 'Bluebell'),
        ('MB_CORNFLOWER', 'Cornflower'),
        ('MB_DAISY', 'Daisy'),
        ('MB_FOXGLOVE', 'Foxglove'),
        ('MB_HONEYSUCKLE', 'Honeysuckle'),
        ('MB_MARIGOLD', 'Marigold'),
        ('MB_POPPY_SRD', 'Poppy (SRD)'),
        ('MB_MGMT', 'Mgmt'),
        
        # Riverside units (9 units: 8 care + 1 MGMT)
        ('RS_DAFFODIL', 'Daffodil'),
        ('RS_HEATHER', 'Heather'),
        ('RS_JASMINE', 'Jasmine'),
        ('RS_LILY', 'Lily'),
        ('RS_LOTUS', 'Lotus'),
        ('RS_MAPLE', 'Maple'),
        ('RS_ORCHID', 'Orchid'),
        ('RS_ROSE', 'Rose'),
        ('RS_MGMT', 'Mgmt'),
        
        # Victoria Gardens units (6 units: 5 care + 1 MGMT)
        ('VG_AZALEA', 'Azalea'),
        ('VG_CROCUS', 'Crocus'),
        ('VG_LILY', 'Lily'),
        ('VG_ROSE', 'Rose'),
        ('VG_TULIP', 'Tulip'),
        ('VG_MGMT', 'Mgmt'),
    ]
    
    name = models.CharField(max_length=50, choices=UNIT_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Care Home Assignment
    care_home = models.ForeignKey(
        'CareHome',
        on_delete=models.CASCADE,
        related_name='units',
        null=True,  # Nullable for backward compatibility with existing tests
        blank=True,
        help_text='Care home this unit belongs to'
    )
    
    # Minimum staffing requirements
    min_day_staff = models.IntegerField(default=2)
    min_night_staff = models.IntegerField(default=1)
    min_weekend_staff = models.IntegerField(default=2)
    
    # Ideal staffing for optimal coverage
    ideal_day_staff = models.IntegerField(default=3, help_text='Ideal day staff count for optimal coverage')
    ideal_night_staff = models.IntegerField(default=2, help_text='Ideal night staff count for optimal coverage')

    class Meta:
        indexes = [
            models.Index(fields=['care_home', 'is_active']),  # Dashboard home filtering
        ]

    def __str__(self):
        return self.get_name_display()

# Table 4: Shift Types
class ShiftType(models.Model):
    SHIFT_CHOICES = [
        ('DAY_SENIOR', 'Day Shift (SSCW/SCW)'),
        ('DAY_ASSISTANT', 'Day Shift (SCA)'),
        ('NIGHT_SENIOR', 'Night Shift (SSCW/SCW)'),
        ('NIGHT_ASSISTANT', 'Night Shift (SCA)'),
        ('ADMIN', 'Supernumerary Admin Day'),
    ]
    
    name = models.CharField(max_length=50, choices=SHIFT_CHOICES, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=4, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    # Which roles can work this shift type
    applicable_roles = models.CharField(max_length=100, default='SSCW,SCW,SCA', help_text="Comma-separated role names")
    
    # Color coding for display
    color_code = models.CharField(max_length=7, default='#3498db')  # Hex color

    def __str__(self):
        return f"{self.get_name_display()} ({self.start_time} - {self.end_time})"
    
    def get_applicable_roles_list(self):
        """Return list of roles that can work this shift"""
        return [role.strip() for role in self.applicable_roles.split(',')]

class StaffingRequirement(models.Model):
    SHIFT_PERIOD_CHOICES = [
        ('DAY', 'Day'),
        ('NIGHT', 'Night'),
    ]

    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='staffing_requirements')
    shift_period = models.CharField(max_length=5, choices=SHIFT_PERIOD_CHOICES)
    shifts_per_week = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)])
    target_staff = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('role', 'shift_period', 'shifts_per_week')
        ordering = ['role__name', 'shift_period', '-shifts_per_week']

    def __str__(self):
        shift_label = dict(self.SHIFT_PERIOD_CHOICES).get(self.shift_period, self.shift_period)
        return f"{self.role.get_name_display()} {shift_label.lower()} {self.shifts_per_week} shifts"

# Table 5: Scheduled Shifts

class Shift(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('CONFIRMED', 'Confirmed'),
        ('UNCOVERED', 'Uncovered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    SHIFT_TYPE_CHOICES = [
        ('REGULAR', 'Regular Shift'),
        ('OVERTIME', 'Overtime'),
        ('AGENCY', 'Agency Staff'),
    ]
    
    SHIFT_PATTERN_CHOICES = [
        ('DAY_0800_2000', '08:00 - 20:00 (Day Shift)'),
        ('NIGHT_2000_0800', '20:00 - 08:00 (Night Shift)'),
        ('CUSTOM', 'Custom Times'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shifts')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    shift_type = models.ForeignKey(ShiftType, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)  # Indexed for date range queries
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED', db_index=True)  # Indexed for filtering
    
    # Shift classification for additional staffing
    shift_classification = models.CharField(max_length=20, choices=SHIFT_TYPE_CHOICES, default='REGULAR', help_text="Regular, Overtime, or Agency")
    
    # Shift time pattern validation
    shift_pattern = models.CharField(max_length=20, choices=SHIFT_PATTERN_CHOICES, default='DAY_0800_2000', help_text="Standard shift pattern")
    
    # Override times if needed (for flexibility and custom patterns)
    custom_start_time = models.TimeField(blank=True, null=True, help_text="Required if shift_pattern is CUSTOM")
    custom_end_time = models.TimeField(blank=True, null=True, help_text="Required if shift_pattern is CUSTOM")
    
    # Agency tracking for billing
    agency_company = models.ForeignKey('AgencyCompany', on_delete=models.SET_NULL, null=True, blank=True, help_text="Required if shift_classification is AGENCY")
    agency_staff_name = models.CharField(max_length=200, blank=True, help_text="Name of agency staff member")
    agency_hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Actual rate charged for this shift")
    
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_shifts')
    
    # Migration field - Track overtime shifts for rota health scoring
    is_overtime = models.BooleanField(
        default=False,
        db_index=True,
        help_text="True if this is an overtime shift (beyond contracted hours)"
    )

    class Meta:
        unique_together = ['user', 'date', 'shift_type']
        ordering = ['date', 'shift_type__start_time']
        indexes = [
            models.Index(fields=['date', 'unit']),  # Common query pattern
            models.Index(fields=['user', 'date']),  # Staff schedule queries
            models.Index(fields=['date', 'shift_type']),  # Shift type reports
            models.Index(fields=['date', 'status']),  # Dashboard filtering by date and status
            models.Index(fields=['unit', 'date', 'status']),  # Home-specific date queries
        ]

    def __str__(self):
        return f"{self.user.full_name} - {self.shift_type.name} - {self.date}"
    
    @property
    def start_time(self):
        """Get actual start time based on pattern or custom"""
        if self.shift_pattern == 'CUSTOM' and self.custom_start_time:
            return self.custom_start_time
        elif self.shift_pattern == 'DAY_0800_2000':
            return time(8, 0)
        elif self.shift_pattern == 'NIGHT_2000_0800':
            return time(20, 0)
        return self.custom_start_time or self.shift_type.start_time
    
    @property
    def end_time(self):
        """Get actual end time based on pattern or custom"""
        if self.shift_pattern == 'CUSTOM' and self.custom_end_time:
            return self.custom_end_time
        elif self.shift_pattern == 'DAY_0800_2000':
            return time(20, 0)
        elif self.shift_pattern == 'NIGHT_2000_0800':
            return time(8, 0)
        return self.custom_end_time or self.shift_type.end_time
    
    @property
    def duration_hours(self):
        """Calculate shift duration in hours"""
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        
        # Handle overnight shifts
        if self.end_time < self.start_time:
            end += timedelta(days=1)
        
        duration = end - start
        return duration.total_seconds() / 3600
    
    @property
    def is_additional_staffing(self):
        """Check if this is overtime or agency (additional cost)"""
        return self.shift_classification in ['OVERTIME', 'AGENCY']
    
    @property
    def matches_preference(self):
        """Check if this shift matches the user's shift preference"""
        return self.user.shift_preference == self.shift_type.name

# Table 6: Leave Requests
class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('ANNUAL', 'Annual Leave'),
        ('SICK', 'Sick Leave'),
        ('PERSONAL', 'Personal Leave'),
        ('EMERGENCY', 'Emergency Leave'),
        ('TRAINING', 'Training'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DENIED', 'Denied'),
        ('CANCELLED', 'Cancelled'),
        ('MANUAL_REVIEW', 'Manual Review Required'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField(db_index=True)  # Indexed for date range queries
    end_date = models.DateField(db_index=True)  # Indexed for date range queries
    days_requested = models.IntegerField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)  # Indexed for filtering by status
    
    # Approval workflow
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    approval_date = models.DateTimeField(blank=True, null=True)
    approval_notes = models.TextField(blank=True, null=True)
    
    # Automated checking flags
    is_blackout_period = models.BooleanField(default=False)
    causes_staffing_shortfall = models.BooleanField(default=False)
    automated_decision = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.full_name} - {self.leave_type} ({self.start_date} to {self.end_date})"

# Table 7: Shift Swap Requests
class ShiftSwapRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('AUTO_APPROVED', 'Auto-Approved'),  # Task 3: Auto-approval status
        ('APPROVED', 'Approved'),
        ('DENIED', 'Denied'),
        ('CANCELLED', 'Cancelled'),
        ('MANUAL_REVIEW', 'Manual Review Required'),
    ]
    
    requesting_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swap_requests_made')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swap_requests_received')
    requesting_shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='swap_requests_from')
    target_shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='swap_requests_to')
    
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Approval workflow
    target_user_approved = models.BooleanField(default=False)
    management_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_swaps')
    approval_date = models.DateTimeField(blank=True, null=True)
    approval_notes = models.TextField(blank=True, null=True)
    
    # Auto-approval fields (Task 3 - Intelligent Shift Swap Auto-Approval)
    automated_decision = models.BooleanField(default=False, help_text="True if auto-approved by system")
    qualification_match_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="0-100 score for qualification match")
    wdt_compliance_check = models.BooleanField(default=False, help_text="WTD compliance verified")
    role_mismatch = models.BooleanField(default=False, help_text="Flags different roles requiring manual review")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.requesting_user.full_name} wants to swap with {self.target_user.full_name}"

# Table 8: Blackout Periods (when leave cannot be taken)
class BlackoutPeriod(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    units = models.ManyToManyField(Unit, blank=True)  # Empty = applies to all units
    reason = models.TextField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"

# Table 9: Staff Reallocations (tracking when staff are moved between units)
class StaffReallocation(models.Model):
    STATUS_CHOICES = [
        ('NEEDED', 'Reallocation Needed'),
        ('ASSIGNED', 'Staff Assigned'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    original_shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='reallocations_from')
    target_unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    target_date = models.DateField()
    target_shift_type = models.ForeignKey(ShiftType, on_delete=models.CASCADE)
    
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEEDED')
    reason = models.TextField()  # e.g., "Cover for approved annual leave"
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_reallocations')

    def __str__(self):
        return f"Reallocation needed: {self.target_unit.name} on {self.target_date}"

# Table 10: System Activity Log
class ActivityLog(models.Model):
    ACTION_TYPES = [
        ('LEAVE_APPROVED', 'Leave Request Approved'),
        ('LEAVE_DENIED', 'Leave Request Denied'),
        ('SWAP_APPROVED', 'Shift Swap Approved'),
        ('SHIFT_CREATED', 'Shift Created'),
        ('SHIFT_CANCELLED', 'Shift Cancelled'),
        ('REALLOCATION_ASSIGNED', 'Staff Reallocation Assigned'),
        ('AUTO_APPROVAL', 'Automatic Approval'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    description = models.TextField()
    automated = models.BooleanField(default=False)
    
    # Generic relation fields for linking to any model
    related_object_type = models.CharField(max_length=50, blank=True, null=True)
    related_object_id = models.IntegerField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_logs')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.full_name} - {self.action_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


# AI Assistant Query Log
class AIQueryLog(models.Model):
    RESPONSE_TYPE_CHOICES = [
        ('vacancy', 'Vacancy Report'),
        ('staff_query', 'Staff Query'),
        ('careplan', 'Care Plan Query'),
        ('home_performance', 'Home Performance'),
        ('staffing_report', 'Staffing Report'),
        ('leave_report', 'Leave Report'),
        ('sickness', 'Sickness Report'),
        ('shortage', 'Staffing Shortage'),
        ('agency', 'Agency Usage'),
        ('error', 'Error/Unknown'),
    ]
    
    query = models.TextField(help_text="User's query text")
    success = models.BooleanField(default=False, help_text="Whether query was understood and answered")
    response_type = models.CharField(max_length=30, choices=RESPONSE_TYPE_CHOICES, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True, help_text="Error message if query failed")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_queries')
    response_time_ms = models.IntegerField(null=True, blank=True, help_text="Response time in milliseconds")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['success', '-created_at']),
            models.Index(fields=['response_type', '-created_at']),
        ]
    
    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.query[:50]} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


# Import audit and compliance models
from .models_audit import (
    DataChangeLog,
    ComplianceRule,
    ComplianceCheck,
    ComplianceViolation,
    AuditReport,
    SystemAccessLog,
)

# Care Inspectorate compliance models are defined below in this file
# Care Inspectorate Compliance Models
# These models store data from Care Inspectorate compliance templates

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


# ============================================================================
# TRAINING & DEVELOPMENT MODELS
# ============================================================================

class TrainingCourse(models.Model):
    """Master list of all training courses available"""
    
    CATEGORY_CHOICES = [
        ('ESSENTIAL', 'Essential Mandatory Training'),
        ('PERSON_CENTRED', 'Person-Centred Care'),
        ('CLINICAL', 'Clinical Skills'),
        ('SPECIALIST', 'Specialist Training'),
    ]
    
    FREQUENCY_CHOICES = [
        ('ANNUAL', 'Annual'),
        ('2_YEAR', 'Every 2 Years'),
        ('3_YEAR', 'Every 3 Years'),
        ('ONCE', 'One-time Only'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    validity_months = models.IntegerField(help_text="Number of months before renewal required")
    is_mandatory = models.BooleanField(default=False)
    requires_competency_assessment = models.BooleanField(default=False)
    requires_certificate = models.BooleanField(default=True)
    minimum_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # SSSC CPD eligible
    sssc_cpd_eligible = models.BooleanField(default=True)
    sssc_cpd_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class TrainingRecord(models.Model):
    """Individual training completion records for staff"""
    
    STATUS_CHOICES = [
        ('CURRENT', 'Current'),
        ('EXPIRING_SOON', 'Expiring Soon (< 30 days)'),
        ('EXPIRED', 'Expired'),
        ('BOOKED', 'Booked - Awaiting Completion'),
        ('IN_PROGRESS', 'In Progress'),
    ]
    
    staff_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='training_records')
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE)
    
    completion_date = models.DateField()
    expiry_date = models.DateField()
    
    trainer_name = models.CharField(max_length=200, blank=True)
    training_provider = models.CharField(max_length=200, blank=True)
    
    certificate_number = models.CharField(max_length=100, blank=True)
    certificate_file = models.FileField(upload_to='training_certificates/', null=True, blank=True)
    
    # Competency assessment
    competency_assessed = models.BooleanField(default=False)
    competency_assessor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                           related_name='competency_assessments_conducted')
    competency_date = models.DateField(null=True, blank=True)
    competency_outcome = models.CharField(max_length=20, choices=[
        ('COMPETENT', 'Competent'),
        ('NOT_YET_COMPETENT', 'Not Yet Competent'),
    ], blank=True)
    
    # SSSC CPD tracking
    sssc_cpd_hours_claimed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='training_records_created')
    
    class Meta:
        ordering = ['-completion_date']
        unique_together = ['staff_member', 'course', 'completion_date']
        
    def __str__(self):
        return f"{self.staff_member.full_name} - {self.course.name} ({self.completion_date})"
    
    def get_status(self):
        """Calculate current status based on expiry date"""
        today = timezone.now().date()
        if self.expiry_date < today:
            return 'EXPIRED'
        elif (self.expiry_date - today).days <= 30:
            return 'EXPIRING_SOON'
        else:
            return 'CURRENT'
    
    def days_until_expiry(self):
        """Calculate days until training expires"""
        return (self.expiry_date - timezone.now().date()).days


class InductionProgress(models.Model):
    """Track 12-week induction checklist progress"""
    
    staff_member = models.OneToOneField(User, on_delete=models.CASCADE, related_name='induction_progress')
    
    start_date = models.DateField()
    expected_completion_date = models.DateField()
    actual_completion_date = models.DateField(null=True, blank=True)
    
    # Week 1 - Essential Induction
    week1_orientation_complete = models.BooleanField(default=False)
    week1_fire_safety_complete = models.BooleanField(default=False)
    week1_infection_control_complete = models.BooleanField(default=False)
    week1_moving_handling_complete = models.BooleanField(default=False)
    week1_health_safety_complete = models.BooleanField(default=False)
    
    # Weeks 2-4 - Foundation Care
    week2_4_safeguarding_complete = models.BooleanField(default=False)
    week2_4_person_centred_care_complete = models.BooleanField(default=False)
    
    # Weeks 5-8 - Specialist Skills
    week5_8_medication_complete = models.BooleanField(default=False)
    week5_8_clinical_skills_complete = models.BooleanField(default=False)
    
    # Weeks 9-12 - Professional Development
    week9_12_sssc_registration_complete = models.BooleanField(default=False)
    week9_12_quality_improvement_complete = models.BooleanField(default=False)
    week9_12_supervision_support_complete = models.BooleanField(default=False)
    
    # Competency hours
    personal_care_hours = models.DecimalField(max_digits=5, decimal_places=1, default=0, 
                                             help_text="Target: 20 hours")
    meal_prep_hours = models.DecimalField(max_digits=5, decimal_places=1, default=0,
                                         help_text="Target: 10 hours")
    documentation_hours = models.DecimalField(max_digits=5, decimal_places=1, default=0,
                                             help_text="Target: 10 hours")
    medication_hours = models.DecimalField(max_digits=5, decimal_places=1, default=0,
                                          help_text="Target: 10 hours (if applicable)")
    
    # Final assessment
    final_assessment_complete = models.BooleanField(default=False)
    final_assessment_date = models.DateField(null=True, blank=True)
    final_assessment_outcome = models.CharField(max_length=20, choices=[
        ('COMPETENT', 'Competent'),
        ('NOT_YET_COMPETENT', 'Not Yet Competent'),
        ('EXTENDED', 'Induction Extended'),
    ], blank=True)
    
    assessor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='induction_assessments')
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Induction Progress Records"
        
    def __str__(self):
        return f"Induction: {self.staff_member.full_name} (Started: {self.start_date})"
    
    def get_completion_percentage(self):
        """Calculate overall induction completion percentage"""
        total_sections = 12
        completed_sections = sum([
            self.week1_orientation_complete,
            self.week1_fire_safety_complete,
            self.week1_infection_control_complete,
            self.week1_moving_handling_complete,
            self.week1_health_safety_complete,
            self.week2_4_safeguarding_complete,
            self.week2_4_person_centred_care_complete,
            self.week5_8_medication_complete,
            self.week5_8_clinical_skills_complete,
            self.week9_12_sssc_registration_complete,
            self.week9_12_quality_improvement_complete,
            self.week9_12_supervision_support_complete,
        ])
        return round((completed_sections / total_sections) * 100, 1)


class SupervisionRecord(models.Model):
    """Track staff supervision sessions"""
    
    SESSION_TYPE_CHOICES = [
        ('PROBATIONARY', 'Probationary (Monthly)'),
        ('REGULAR', 'Regular (Monthly/6-weekly)'),
        ('AD_HOC', 'Ad-hoc'),
        ('RETURN_TO_WORK', 'Return to Work'),
    ]
    
    staff_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supervision_sessions')
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supervisions_conducted')
    
    session_date = models.DateField()
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES)
    duration_minutes = models.IntegerField()
    
    # Wellbeing
    wellbeing_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)],
                                         help_text="1-10 scale")
    sickness_days_since_last = models.IntegerField(default=0)
    wellbeing_concerns = models.TextField(blank=True)
    support_offered = models.TextField(blank=True)
    
    # Performance
    performance_strengths = models.TextField(blank=True)
    performance_development = models.TextField(blank=True)
    
    # Training
    mandatory_training_current = models.BooleanField(default=True)
    training_needs_identified = models.TextField(blank=True)
    
    # SSSC
    sssc_registration_current = models.BooleanField(default=True)
    sssc_cpd_hours_to_date = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    
    # Safeguarding
    safeguarding_concerns_discussed = models.BooleanField(default=False)
    safeguarding_notes = models.TextField(blank=True)
    
    # Incidents
    incidents_since_last = models.IntegerField(default=0)
    incident_learning = models.TextField(blank=True)
    
    # Workload
    workload_manageable = models.BooleanField(default=True)
    workload_notes = models.TextField(blank=True)
    
    # Actions
    actions_from_previous = models.TextField(blank=True)
    new_actions = models.TextField(blank=True)
    
    # Probationary review (if applicable)
    is_probationary_review = models.BooleanField(default=False)
    probation_progress = models.CharField(max_length=30, choices=[
        ('EXCEEDING', 'Exceeding Expectations'),
        ('MEETING', 'Meeting Expectations'),
        ('SOME_CONCERNS', 'Some Concerns'),
        ('SERIOUS_CONCERNS', 'Serious Concerns'),
    ], blank=True)
    probation_recommendation = models.CharField(max_length=30, choices=[
        ('CONTINUE', 'Continue Probation'),
        ('EXTEND', 'Extend Probation'),
        ('CONFIRM', 'Confirm Permanent Employment'),
    ], blank=True)
    
    # Next supervision
    next_supervision_date = models.DateField(null=True, blank=True)
    
    # Sign-off
    staff_signature_date = models.DateField(null=True, blank=True)
    supervisor_signature_date = models.DateField(null=True, blank=True)
    staff_comments = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-session_date']
        
    def __str__(self):
        return f"Supervision: {self.staff_member.full_name} - {self.session_date}"


# ============================================================================
# INCIDENT REPORTING MODELS
# ============================================================================

class IncidentReport(models.Model):
    """Incident reporting for Care Inspectorate compliance"""
    
    INCIDENT_TYPE_CHOICES = [
        # Falls & Physical Injuries
        ('FALL_UNWITNESSED', 'Fall - Unwitnessed'),
        ('FALL_WITNESSED', 'Fall - Witnessed'),
        ('FALL_BED', 'Fall - From Bed'),
        ('FALL_CHAIR', 'Fall - From Chair'),
        ('FALL_BATHROOM', 'Fall - In Bathroom'),
        ('SLIP_TRIP', 'Slip/Trip'),
        ('PHYSICAL_INJURY', 'Physical Injury (Not Fall)'),
        
        # Clinical/Medical
        ('MED_ERROR_OMISSION', 'Medication Error - Omission'),
        ('MED_ERROR_WRONG_DOSE', 'Medication Error - Wrong Dose'),
        ('MED_ERROR_WRONG_MED', 'Medication Error - Wrong Medication'),
        ('MED_ERROR_WRONG_TIME', 'Medication Error - Wrong Time'),
        ('MED_ERROR_WRONG_PERSON', 'Medication Error - Wrong Person'),
        ('CONTROLLED_DRUG', 'Controlled Drug Discrepancy'),
        ('CHOKING', 'Choking Incident'),
        ('SEIZURE', 'Seizure'),
        ('DIABETIC_EMERGENCY', 'Diabetic Emergency'),
        ('ALLERGIC_REACTION', 'Allergic Reaction'),
        ('PRESSURE_ULCER', 'Pressure Ulcer'),
        ('UNEXPLAINED_INJURY', 'Unexplained Bruising/Injury'),
        ('MEDICAL_EMERGENCY', 'Medical Emergency'),
        ('HEALTH_DETERIORATION', 'Deterioration in Health'),
        
        # Challenging Behaviour
        ('AGGRESSION_STAFF', 'Physical Aggression Toward Staff'),
        ('AGGRESSION_SERVICE_USER', 'Physical Aggression Toward Service User'),
        ('VERBAL_AGGRESSION', 'Verbal Aggression'),
        ('SEXUAL_BEHAVIOUR', 'Sexual Behaviour Concerns'),
        ('PROPERTY_DAMAGE', 'Property Damage'),
        ('SELF_HARM', 'Self-Harm'),
        ('ABSCONDING', 'Absconding/Missing Person'),
        
        # Safeguarding
        ('SUSPECTED_PHYSICAL_ABUSE', 'Suspected Physical Abuse'),
        ('SUSPECTED_PSYCHOLOGICAL_ABUSE', 'Suspected Psychological/Emotional Abuse'),
        ('SUSPECTED_FINANCIAL_ABUSE', 'Suspected Financial Abuse'),
        ('SUSPECTED_NEGLECT', 'Suspected Neglect'),
        ('SUSPECTED_SEXUAL_ABUSE', 'Suspected Sexual Abuse'),
        ('SUSPECTED_DISCRIMINATORY_ABUSE', 'Suspected Discriminatory Abuse'),
        ('SUSPECTED_INSTITUTIONAL_ABUSE', 'Suspected Institutional Abuse'),
        ('SELF_NEGLECT', 'Self-Neglect'),
        ('ALLEGATION_AGAINST_STAFF', 'Allegation Against Staff Member'),
        
        # Health & Safety
        ('FIRE_ALARM', 'Fire Alarm Activation'),
        ('EQUIPMENT_FAILURE', 'Equipment Failure'),
        ('BUILDING_ISSUE', 'Building/Facilities Issue'),
        ('INFECTION_OUTBREAK', 'Infection Control Outbreak'),
        ('FOOD_SAFETY', 'Food Safety Incident'),
        ('SECURITY_BREACH', 'Security Breach'),
        ('VISITOR_INCIDENT', 'Visitor Incident'),
        ('STAFF_INJURY', 'Staff Injury'),
        
        # Near Miss
        ('NEAR_MISS', 'Near Miss - No Harm'),
    ]
    
    SEVERITY_CHOICES = [
        ('NO_HARM', 'No Harm'),
        ('LOW_HARM', 'Low Harm - Minor Injury'),
        ('MODERATE_HARM', 'Moderate Harm - Medical Intervention Required'),
        ('MAJOR_HARM', 'Major Harm - Hospitalization'),
        ('DEATH', 'Death'),
    ]
    
    RISK_RATING_CHOICES = [
        ('LOW', 'Low (Green)'),
        ('MODERATE', 'Moderate (Amber)'),
        ('HIGH', 'High (Red)'),
        ('CRITICAL', 'Critical (Purple)'),
    ]
    
    # Basic Details
    reference_number = models.CharField(max_length=50, unique=True)
    incident_date = models.DateField()
    incident_time = models.TimeField()
    reported_date = models.DateField(auto_now_add=True)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='incidents_reported')
    
    incident_type = models.CharField(max_length=50, choices=INCIDENT_TYPE_CHOICES)
    location = models.CharField(max_length=200)
    
    # Service User (if applicable)
    service_user_name = models.CharField(max_length=200, blank=True)
    service_user_dob = models.DateField(null=True, blank=True)
    
    # Description
    description = models.TextField(help_text="Factual, objective description of what happened")
    witnesses = models.TextField(blank=True)
    was_witnessed = models.BooleanField(default=False)
    
    # Immediate Actions
    immediate_actions = models.TextField(blank=True)
    injuries_sustained = models.TextField(blank=True)
    body_map_completed = models.BooleanField(default=False)
    photos_taken = models.BooleanField(default=False)
    
    # Medical Intervention
    gp_contacted = models.BooleanField(default=False)
    ambulance_called = models.BooleanField(default=False)
    hospital_attendance = models.BooleanField(default=False)
    hospital_admission = models.BooleanField(default=False)
    medical_notes = models.TextField(blank=True)
    
    # Severity & Risk
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    risk_rating = models.CharField(max_length=20, choices=RISK_RATING_CHOICES)
    
    # External Notifications
    care_inspectorate_notified = models.BooleanField(default=False)
    care_inspectorate_ref = models.CharField(max_length=100, blank=True)
    police_notified = models.BooleanField(default=False)
    police_crime_ref = models.CharField(max_length=100, blank=True)
    local_authority_notified = models.BooleanField(default=False)
    safeguarding_alert_raised = models.BooleanField(default=False)
    
    # Investigation
    investigation_required = models.BooleanField(default=False)
    investigation_assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                                  related_name='investigations_assigned')
    investigation_due_date = models.DateField(null=True, blank=True)
    investigation_complete = models.BooleanField(default=False)
    investigation_findings = models.TextField(blank=True)
    
    # Learning & Actions
    lessons_learned = models.TextField(blank=True)
    preventive_actions = models.TextField(blank=True)
    
    # Closure
    incident_closed = models.BooleanField(default=False)
    closed_date = models.DateField(null=True, blank=True)
    closed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='incidents_closed')
    
    # Manager Review
    manager_reviewed = models.BooleanField(default=False)
    manager_review_date = models.DateField(null=True, blank=True)
    manager_comments = models.TextField(blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='incidents_reviewed')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-incident_date', '-incident_time']
        
    def __str__(self):
        return f"{self.reference_number} - {self.get_incident_type_display()} ({self.incident_date})"
    
    def requires_care_inspectorate_notification(self):
        """Check if this incident meets Care Inspectorate notification criteria"""
        notification_types = [
            'DEATH', 'MAJOR_HARM', 'SUSPECTED_PHYSICAL_ABUSE', 'SUSPECTED_PSYCHOLOGICAL_ABUSE',
            'SUSPECTED_FINANCIAL_ABUSE', 'SUSPECTED_NEGLECT', 'SUSPECTED_SEXUAL_ABUSE',
            'SUSPECTED_DISCRIMINATORY_ABUSE', 'SUSPECTED_INSTITUTIONAL_ABUSE',
            'ALLEGATION_AGAINST_STAFF', 'INFECTION_OUTBREAK'
        ]
        return self.severity == 'DEATH' or self.severity == 'MAJOR_HARM' or \
               any(self.incident_type.startswith(t) for t in notification_types)


# Agency Company Model for tracking external staffing providers
class AgencyCompany(models.Model):
    name = models.CharField(max_length=200, unique=True)
    contact_person = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    hourly_rate_day = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="Standard day shift hourly rate")
    hourly_rate_night = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="Standard night shift hourly rate")
    account_number = models.CharField(max_length=100, blank=True, help_text="For billing purposes")
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Agency Companies"
        ordering = ['name']
    
    def __str__(self):
        return self.name


# ============================================================================
# CARE PLAN REVIEW MODELS
# ============================================================================

class Resident(models.Model):
    """
    Resident model for care plan review tracking
    120 residents total across 8 units (15 per unit)
    """
    # Basic Information
    resident_id = models.CharField(max_length=50, unique=True, help_text="Unique resident identifier")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    
    # Accommodation
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name='residents')
    room_number = models.CharField(max_length=10, help_text="Room number (1-15 per unit)")
    
    # Admission
    admission_date = models.DateField(help_text="Date resident was admitted to the home")
    
    # Care Team
    keyworker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='keyworker_residents',
                                 help_text="Care staff responsible for this resident's reviews")
    unit_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='managed_residents',
                                    help_text="SSCW/SSCWN responsible for oversight")
    
    # Status
    is_active = models.BooleanField(default=True, help_text="False if resident has been discharged/deceased")
    discharge_date = models.DateField(null=True, blank=True)
    discharge_reason = models.CharField(max_length=200, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['unit', 'room_number']
        
    def __str__(self):
        return f"{self.first_name} {self.last_name} - Room {self.room_number} ({self.unit.name})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def days_since_admission(self):
        """Calculate days since admission"""
        from datetime import date
        if not self.admission_date:
            return 0
        return (date.today() - self.admission_date).days
    
    @property
    def initial_review_due(self):
        """4 weeks after admission"""
        from datetime import timedelta
        return self.admission_date + timedelta(weeks=4)
    
    def get_next_review_due_date(self):
        """Calculate when next review is due"""
        from datetime import date, timedelta
        
        # Get most recent completed review
        last_review = self.care_plan_reviews.filter(
            status='COMPLETED'
        ).order_by('-completed_date').first()
        
        if not last_review:
            # No completed reviews - use 4-week initial review
            return self.initial_review_due
        
        # After initial review, 6-monthly reviews
        return last_review.completed_date + timedelta(days=183)  # ~6 months


class CarePlanReview(models.Model):
    """
    Care Plan Review tracking with compliance monitoring
    - Initial review: 4 weeks after admission
    - Subsequent reviews: Every 6 months
    """
    
    REVIEW_TYPE_CHOICES = [
        ('INITIAL', '4-Week Initial Review'),
        ('SIX_MONTH', '6-Monthly Review'),
        ('UNSCHEDULED', 'Unscheduled Review'),
    ]
    
    STATUS_CHOICES = [
        ('UPCOMING', 'Upcoming'),
        ('DUE', 'Due Soon (7 days)'),
        ('OVERDUE', 'Overdue'),
        ('IN_PROGRESS', 'In Progress'),
        ('PENDING_APPROVAL', 'Pending Manager Approval'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Basic Information
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='care_plan_reviews')
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPE_CHOICES)
    
    # Scheduling
    due_date = models.DateField(db_index=True, help_text="Date review is due by")  # Indexed for compliance queries
    scheduled_date = models.DateField(null=True, blank=True, db_index=True, help_text="Date review is scheduled for")  # Indexed for scheduling
    
    # Responsibility
    keyworker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='assigned_reviews',
                                 help_text="Keyworker responsible for this review")
    unit_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                    related_name='reviews_to_approve',
                                    help_text="Manager responsible for approval")
    
    # Status & Completion
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UPCOMING', db_index=True)  # Indexed for status filtering
    started_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True, db_index=True)  # Indexed for completion reports
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='completed_reviews')
    
    # Manager Approval
    manager_approved = models.BooleanField(default=False)
    manager_approval_date = models.DateField(null=True, blank=True)
    manager_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='approved_reviews')
    manager_comments = models.TextField(blank=True)
    
    # Review Content
    care_needs_assessment = models.TextField(blank=True, help_text="Assessment of current care needs")
    goals_progress = models.TextField(blank=True, help_text="Progress towards care plan goals")
    changes_required = models.TextField(blank=True, help_text="Changes to care plan required")
    family_involvement = models.TextField(blank=True, help_text="Family/NOK involvement notes")
    
    # Compliance Tracking
    days_overdue = models.IntegerField(default=0, help_text="Automatically calculated")
    is_compliant = models.BooleanField(default=True, help_text="False if review is overdue")
    
    # Alerts Sent
    alert_7_days_sent = models.BooleanField(default=False)
    alert_due_sent = models.BooleanField(default=False)
    alert_overdue_sent = models.BooleanField(default=False)
    alert_manager_escalated = models.BooleanField(default=False)
    
    # Audit Trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='created_careplan_reviews')
    
    # Documentation
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['due_date', 'resident__unit']
        
    def __str__(self):
        return f"{self.resident.full_name} - {self.get_review_type_display()} (Due: {self.due_date})"
    
    def save(self, *args, **kwargs):
        """Auto-update status and compliance flags on save"""
        from datetime import date
        
        today = date.today()
        
        # Calculate days overdue
        if self.due_date and not self.completed_date:
            days_diff = (today - self.due_date).days
            self.days_overdue = max(0, days_diff)
            
            # Update status based on dates
            if days_diff > 0:
                self.status = 'OVERDUE'
                self.is_compliant = False
            elif days_diff >= -7:
                self.status = 'DUE'
            elif self.status not in ['IN_PROGRESS', 'PENDING_APPROVAL', 'COMPLETED', 'CANCELLED']:
                self.status = 'UPCOMING'
        
        # If completed, mark as compliant
        if self.completed_date and self.manager_approved:
            self.status = 'COMPLETED'
            self.is_compliant = True
            self.days_overdue = 0
        
        super().save(*args, **kwargs)
    
    @property
    def days_until_due(self):
        """Calculate days until review is due (negative if overdue)"""
        from datetime import date
        if not self.due_date:
            return None
        return (self.due_date - date.today()).days
    
    def get_status_display_color(self):
        """Return Bootstrap color class for status"""
        status_colors = {
            'UPCOMING': 'info',
            'DUE': 'warning',
            'OVERDUE': 'danger',
            'IN_PROGRESS': 'primary',
            'PENDING_APPROVAL': 'warning',
            'COMPLETED': 'success',
            'CANCELLED': 'secondary',
        }
        return status_colors.get(self.status, 'secondary')


class CarePlanReviewDocument(models.Model):
    """Supporting documents for care plan reviews"""
    review = models.ForeignKey(CarePlanReview, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=100, help_text="e.g., Assessment Form, Family Notes")
    file = models.FileField(upload_to='careplan_reviews/%Y/%m/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.document_type} - {self.review}"


# ========================================
# STAFFING ALERT MODELS
# ========================================
import uuid

class StaffingAlert(models.Model):
    """
    Alert sent when staffing is below minimum requirements
    """
    ALERT_STATUS = [
        ('PENDING', 'Pending Responses'),
        ('PARTIALLY_FILLED', 'Partially Filled'),
        ('FILLED', 'Fully Filled'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    ALERT_TYPE = [
        ('SHORTAGE', 'Staff Shortage'),
        ('ABSENCE', 'Last Minute Absence'),
        ('EMERGENCY', 'Emergency Cover'),
    ]
    
    # Alert Details
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE, default='SHORTAGE')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='staffing_alerts')
    shift_date = models.DateField()
    shift_type = models.ForeignKey(ShiftType, on_delete=models.CASCADE)
    
    # Staffing Numbers
    required_staff = models.IntegerField(help_text="Minimum staff required")
    current_staff = models.IntegerField(help_text="Currently scheduled staff")
    shortage = models.IntegerField(help_text="Number of additional staff needed")
    
    # Status
    status = models.CharField(max_length=20, choices=ALERT_STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                  related_name='created_alerts')
    expires_at = models.DateTimeField(help_text="Alert expires after this time")
    
    # Response Tracking
    total_responses = models.IntegerField(default=0)
    accepted_responses = models.IntegerField(default=0)
    declined_responses = models.IntegerField(default=0)
    
    # Notifications Sent
    sms_sent = models.IntegerField(default=0, help_text="Number of SMS sent")
    email_sent = models.IntegerField(default=0, help_text="Number of emails sent")
    
    # Additional Info
    message = models.TextField(blank=True, help_text="Custom message to staff")
    priority = models.IntegerField(default=5, help_text="1-10, higher is more urgent")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['shift_date', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.unit.get_name_display()} - {self.shift_date} ({self.shortage} short)"
    
    @property
    def is_filled(self):
        """Check if all positions are filled"""
        return self.accepted_responses >= self.shortage
    
    @property
    def is_expired(self):
        """Check if alert has expired"""
        return timezone.now() > self.expires_at
    
    @property
    def positions_remaining(self):
        """Calculate how many positions still need filling"""
        return max(0, self.shortage - self.accepted_responses)
    
    @property
    def responses_pending(self):
        """Count pending responses"""
        return self.responses.filter(status='PENDING').count()
    
    @property
    def is_overfilled(self):
        """Check if more positions accepted than needed (shouldn't happen with safeguards)"""
        return self.accepted_responses > self.shortage
    
    def update_status(self):
        """
        Update alert status based on responses and current state
        
        SAFEGUARDS:
        - Automatically marks FILLED when shortage met
        - Marks EXPIRED if past expiration time
        - Prevents further acceptances when filled
        """
        from django.db import transaction
        
        with transaction.atomic():
            # Get fresh data with lock
            alert = StaffingAlert.objects.select_for_update().get(pk=self.pk)
            
            # Priority order of status updates
            if alert.status == 'CANCELLED':
                # Don't change cancelled alerts
                return
            
            if alert.accepted_responses >= alert.shortage:
                # FILLED takes priority - prevents further acceptances
                alert.status = 'FILLED'
            elif alert.is_expired and alert.status in ['PENDING', 'PARTIALLY_FILLED']:
                alert.status = 'EXPIRED'
            elif alert.accepted_responses > 0:
                alert.status = 'PARTIALLY_FILLED'
            else:
                alert.status = 'PENDING'
            
            alert.save()
    
    def cancel_alert(self, reason=''):
        """
        Cancel an alert and prevent further acceptances
        Manager can call this if alert is no longer needed
        """
        from django.db import transaction
        
        with transaction.atomic():
            alert = StaffingAlert.objects.select_for_update().get(pk=self.pk)
            alert.status = 'CANCELLED'
            if reason:
                alert.message = f"{alert.message}\n\nCANCELLED: {reason}"
            alert.save()
            
            # Optionally notify pending responders that alert is cancelled
            return True


class StaffingAlertResponse(models.Model):
    """
    Individual staff member's response to a staffing alert
    """
    RESPONSE_STATUS = [
        ('PENDING', 'Pending Response'),
        ('ACCEPTED', 'Accepted Shift'),
        ('DECLINED', 'Declined Shift'),
        ('EXPIRED', 'No Response (Expired)'),
        ('WITHDRAWN', 'Acceptance Withdrawn'),
    ]
    
    RESPONSE_METHOD = [
        ('EMAIL_LINK', 'Email Link Click'),
        ('SMS_LINK', 'SMS Link Click'),
        ('WEB_LOGIN', 'Web Login'),
        ('PHONE', 'Phone Call'),
        ('MANUAL', 'Manually Added'),
    ]
    
    # Alert and User
    alert = models.ForeignKey(StaffingAlert, on_delete=models.CASCADE, 
                             related_name='responses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                            related_name='alert_responses')
    
    # Response Details
    status = models.CharField(max_length=20, choices=RESPONSE_STATUS, default='PENDING')
    response_method = models.CharField(max_length=20, choices=RESPONSE_METHOD, 
                                      blank=True, null=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    # Unique token for email/SMS links
    response_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Communication Tracking
    email_sent_at = models.DateTimeField(null=True, blank=True)
    sms_sent_at = models.DateTimeField(null=True, blank=True)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Shift Created (if accepted)
    shift_created = models.ForeignKey(Shift, on_delete=models.SET_NULL, 
                                     null=True, blank=True,
                                     related_name='alert_response')
    
    # Reason for decline (optional)
    decline_reason = models.CharField(max_length=200, blank=True)
    
    # Additional notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['alert', 'user']
        indexes = [
            models.Index(fields=['response_token']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.alert} ({self.status})"
    
    @property
    def response_date(self):
        """Return the date when response was given"""
        return self.responded_at if self.responded_at else None
    
    def accept_shift(self, method='WEB_LOGIN'):
        """
        Accept the shift and create the actual shift in the system
        
        SAFEGUARDS AGAINST OVERSTAFFING:
        1. Database row-level locking (select_for_update) prevents race conditions
        2. Pre-validation checks before creating shift
        3. Atomic transaction ensures consistency
        4. Re-checks positions after acquiring lock
        5. Automatically marks alert as FILLED when shortage met
        """
        from django.db import transaction
        
        # Pre-validation (fast checks without lock)
        if self.status == 'ACCEPTED':
            raise Exception("Already accepted this shift")
        
        if self.alert.is_expired:
            raise Exception("This alert has expired")
        
        # Use database transaction with row-level locking to prevent race conditions
        try:
            with transaction.atomic():
                # CRITICAL: Lock the alert row to prevent simultaneous acceptances
                # This ensures only one person can accept at a time
                alert = StaffingAlert.objects.select_for_update().get(pk=self.alert.pk)
                
                # Re-check if already filled (after acquiring lock)
                if alert.accepted_responses >= alert.shortage:
                    raise Exception(
                        f"This alert has already been filled. "
                        f"{alert.accepted_responses} positions accepted out of {alert.shortage} needed."
                    )
                
                # Check if alert status prevents acceptance
                if alert.status in ['FILLED', 'CANCELLED']:
                    raise Exception(f"This alert is {alert.status.lower()} and no longer accepting responses")
                
                # Double-check this user hasn't already accepted
                # (shouldn't happen due to unique_together, but extra safety)
                if self.status == 'ACCEPTED':
                    raise Exception("Already accepted this shift")
                
                # Verify user isn't already scheduled for this date/unit/shift
                existing_shift = Shift.objects.filter(
                    user=self.user,
                    date=alert.shift_date,
                    unit=alert.unit,
                    shift_type=alert.shift_type,
                    status__in=['SCHEDULED', 'CONFIRMED']
                ).first()
                
                if existing_shift:
                    raise Exception(
                        f"You are already scheduled for {alert.shift_type.get_name_display()} "
                        f"on {alert.shift_date} at {alert.unit.get_name_display()}"
                    )
                
                # All checks passed - create the shift
                shift = Shift.objects.create(
                    user=self.user,
                    unit=alert.unit,
                    shift_type=alert.shift_type,
                    date=alert.shift_date,
                    status='SCHEDULED',
                    notes=f'Created from staffing alert #{alert.id} - Auto-accepted via {method}'
                )
                
                # Update response record
                self.status = 'ACCEPTED'
                self.response_method = method
                self.responded_at = timezone.now()
                self.shift_created = shift
                self.save()
                
                # Update alert statistics (still within locked transaction)
                alert.accepted_responses += 1
                alert.total_responses += 1
                
                # Auto-close alert if now fully staffed
                if alert.accepted_responses >= alert.shortage:
                    alert.status = 'FILLED'
                elif alert.accepted_responses > 0:
                    alert.status = 'PARTIALLY_FILLED'
                
                alert.save()
                
                # Transaction commits here - all changes are atomic
                return shift
                
        except Shift.DoesNotExist:
            raise Exception("Alert not found")
        except Exception as e:
            # Re-raise with context
            raise Exception(f"Cannot accept shift: {str(e)}")
    
    def decline_shift(self, reason='', method='WEB_LOGIN'):
        """
        Decline the shift
        """
        if self.status in ['ACCEPTED', 'DECLINED']:
            return
        
        self.status = 'DECLINED'
        self.response_method = method
        self.responded_at = timezone.now()
        self.decline_reason = reason
        self.save()
        
        # Update alert statistics
        self.alert.declined_responses += 1
        self.alert.total_responses += 1
        self.alert.update_status()
    
    def withdraw_acceptance(self, reason=''):
        """
        Withdraw a previously accepted shift (within reasonable time)
        """
        if self.status != 'ACCEPTED':
            return False, "No acceptance to withdraw"
        
        if self.shift_created:
            # Delete the created shift
            self.shift_created.delete()
        
        self.status = 'WITHDRAWN'
        self.notes += f"\nWithdrawn: {reason}"
        self.save()
        
        # Update alert statistics
        self.alert.accepted_responses -= 1
        self.alert.update_status()
        
        return True, "Acceptance withdrawn"


class StaffingAlertTemplate(models.Model):
    """
    Templates for staffing alert messages
    """
    TEMPLATE_TYPE = [
        ('SMS', 'SMS Message'),
        ('EMAIL', 'Email Message'),
        ('PUSH', 'Push Notification'),
    ]
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE)
    subject = models.CharField(max_length=200, blank=True, help_text="For emails")
    message_template = models.TextField(
        help_text="Use {variables} like {unit}, {date}, {shift_type}, {shortage}"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['template_type', 'name']
    
    def __str__(self):
        return f"{self.template_type} - {self.name}"
    
    def render(self, context):
        """Render the template with given context"""
        message = self.message_template
        for key, value in context.items():
            message = message.replace(f'{{{key}}}', str(value))
        return message


# Import automated workflow models
from .models_automated_workflow import (
    SicknessAbsence,
    StaffingCoverRequest,
    ReallocationRequest,
    OvertimeOfferBatch,
    OvertimeOffer,
    AgencyRequest,
    LongTermCoverPlan,
    PostShiftAdministration,
)


# Import multi-home management models
from .models_multi_home import CareHome


# ==============================================================================
# MACHINE LEARNING MODELS (Phase 6.2 - ML Forecasting)
# ==============================================================================

class StaffingForecast(models.Model):
    """
    Store Prophet ML forecasts for staffing demand prediction
    
    Scottish Design Principles:
    - Transparent: Store interpretable components (trend, weekly, yearly)
    - User-Centered: Confidence intervals for OM/SM risk assessment
    - Evidence-Based: Prophet model with validation metrics
    - GDPR Compliant: No personal data, aggregated predictions only
    
    Usage:
    - Dashboard: Show 30-day forecasts to OM/SM
    - Planning: Compare predicted vs actual demand
    - Alerts: Notify when demand exceeds capacity
    """
    
    # Location
    care_home = models.ForeignKey(CareHome, on_delete=models.CASCADE, related_name='forecasts')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='forecasts')
    forecast_date = models.DateField(db_index=True, help_text="Date being forecasted")
    
    # Predictions
    predicted_shifts = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Predicted number of shifts needed"
    )
    confidence_lower = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Lower bound of 80% confidence interval"
    )
    confidence_upper = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Upper bound of 80% confidence interval"
    )
    
    # Prophet Components (for debugging/transparency)
    trend_component = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Long-term trend (increasing/decreasing demand)"
    )
    weekly_component = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Day-of-week effect (weekend reduction, etc.)"
    )
    yearly_component = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Seasonal effect (winter pressure, summer holidays)"
    )
    
    # Metadata
    model_version = models.CharField(
        max_length=50, 
        default='1.0',
        help_text="Prophet model version used for this forecast"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When forecast was generated"
    )
    
    # Validation metrics (from model training)
    mae = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Mean Absolute Error from validation (shifts/day)"
    )
    mape = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Mean Absolute Percentage Error from validation (%)"
    )
    
    class Meta:
        unique_together = ('care_home', 'unit', 'forecast_date', 'model_version')
        ordering = ['forecast_date', 'care_home', 'unit']
        indexes = [
            models.Index(fields=['forecast_date', 'care_home']),
            models.Index(fields=['forecast_date', 'unit']),
            models.Index(fields=['care_home', 'unit', 'forecast_date']),
        ]
        verbose_name = "Staffing Forecast"
        verbose_name_plural = "Staffing Forecasts"
    
    def __str__(self):
        return f"{self.care_home.name}/{self.unit.name} - {self.forecast_date}: {self.predicted_shifts:.1f} shifts"
    
    @property
    def uncertainty_range(self):
        """Calculate the width of the confidence interval"""
        return float(self.confidence_upper - self.confidence_lower)
    
    @property
    def is_high_uncertainty(self):
        """Flag forecasts with wide confidence intervals (>50% of prediction)"""
        if self.predicted_shifts > 0:
            return (self.uncertainty_range / float(self.predicted_shifts)) > 0.5
        return False
    
    def is_actual_within_ci(self, actual_shifts):
        """
        Check if actual demand fell within predicted confidence interval
        
        Args:
            actual_shifts: Actual number of shifts on forecast_date
            
        Returns:
            bool: True if actual within [lower, upper]
        """
        return self.confidence_lower <= actual_shifts <= self.confidence_upper


class ProphetModelMetrics(models.Model):
    """
    Track Prophet forecasting model performance in production
    
    Stores:
    - Forecast accuracy (MAPE)
    - Distribution drift scores
    - Model versioning
    - Retrain audit trail
    """
    
    care_home = models.ForeignKey(
        'CareHome',
        on_delete=models.CASCADE,
        related_name='prophet_metrics'
    )
    unit = models.ForeignKey(
        'Unit',
        on_delete=models.CASCADE,
        related_name='prophet_metrics'
    )
    forecast_date = models.DateField(
        db_index=True,
        help_text="Date the forecast was made for"
    )
    actual_value = models.FloatField(
        help_text="Actual number of shifts on forecast_date"
    )
    forecast_value = models.FloatField(
        help_text="Predicted number of shifts"
    )
    mape = models.FloatField(
        help_text="Mean Absolute Percentage Error for this forecast",
        validators=[MinValueValidator(0.0)]
    )
    drift_score = models.FloatField(
        null=True,
        blank=True,
        help_text="KS test p-value indicating distribution drift (lower = more drift)"
    )
    model_version = models.CharField(
        max_length=50,
        help_text="Prophet model version identifier (e.g., 'v1.2024-12-15')"
    )
    model_version_date = models.DateField(
        help_text="Date the model was trained"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'scheduling_prophet_model_metrics'
        ordering = ['-forecast_date', '-created_at']
        indexes = [
            models.Index(fields=['care_home', 'unit', 'forecast_date']),
            models.Index(fields=['model_version_date']),
            models.Index(fields=['mape']),
        ]
        verbose_name = "Prophet Model Metric"
        verbose_name_plural = "Prophet Model Metrics"
    
    def __str__(self):
        return f"{self.care_home.name}/{self.unit.name} - {self.forecast_date}: MAPE {self.mape:.1f}%"
    
    @property
    def is_accurate(self):
        """Flag if MAPE is within acceptable threshold (< 30%)"""
        return self.mape < 30.0
    
    @property
    def has_drift(self):
        """Flag if drift is statistically significant (p < 0.05)"""
        if self.drift_score is None:
            return False
        return self.drift_score < 0.05


# ============================================================================
# TASK 11: AI ASSISTANT FEEDBACK & LEARNING SYSTEM
# Import models from feedback_learning module
# ============================================================================

from .feedback_learning import AIQueryFeedback, UserPreference


# ============================================================================
# TASK 27: CUSTOM REPORT BUILDER
# Models for saving report templates and scheduling automated reports
# ============================================================================

class SavedReport(models.Model):
    """Store custom report templates created by users"""
    REPORT_TYPE_CHOICES = [
        ('STAFFING', 'Staffing Report'),
        ('LEAVE', 'Leave Report'),
        ('SHIFTS', 'Shift Report'),
        ('TRAINING', 'Training Report'),
        ('COMPLIANCE', 'Compliance Report'),
        ('INCIDENTS', 'Incident Report'),
        ('RESIDENTS', 'Resident Report'),
        ('CUSTOM', 'Custom Report'),
    ]
    
    OUTPUT_FORMAT_CHOICES = [
        ('PDF', 'PDF Document'),
        ('EXCEL', 'Excel Spreadsheet'),
        ('CSV', 'CSV File'),
    ]
    
    name = models.CharField(max_length=200, help_text="Template name")
    description = models.TextField(blank=True, null=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, default='CUSTOM')
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='created_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Report Configuration (stored as JSON)
    selected_fields = models.JSONField(
        default=list,
        help_text="List of field names to include in report"
    )
    filters = models.JSONField(
        default=dict,
        help_text="Filter criteria (date ranges, homes, units, staff, etc.)"
    )
    grouping = models.JSONField(
        default=dict,
        help_text="Grouping and aggregation settings"
    )
    sorting = models.JSONField(
        default=list,
        help_text="Sort order for report data"
    )
    
    output_format = models.CharField(max_length=10, choices=OUTPUT_FORMAT_CHOICES, default='PDF')
    is_public = models.BooleanField(
        default=False,
        help_text="Allow other managers to use this template"
    )
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Saved Report Template'
        verbose_name_plural = 'Saved Report Templates'
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


class ScheduledReport(models.Model):
    """Schedule automated report generation and delivery"""
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
    ]
    
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    report_template = models.ForeignKey(
        SavedReport,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='scheduled_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='WEEKLY')
    weekday = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        null=True,
        blank=True,
        help_text="Day of week for weekly reports (0=Monday, 6=Sunday)"
    )
    day_of_month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        null=True,
        blank=True,
        help_text="Day of month for monthly reports"
    )
    time_of_day = models.TimeField(default=time(9, 0), help_text="Time to generate report")
    
    recipients = models.JSONField(
        default=list,
        help_text="List of email addresses to send report to"
    )
    
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['next_run']
        verbose_name = 'Scheduled Report'
        verbose_name_plural = 'Scheduled Reports'
    
    def __str__(self):
        return f"{self.report_template.name} - {self.get_frequency_display()}"
    
    def calculate_next_run(self):
        """Calculate next run time based on frequency"""
        from datetime import datetime, timedelta
        now = timezone.now()
        
        if self.frequency == 'DAILY':
            next_run = now.replace(hour=self.time_of_day.hour, minute=self.time_of_day.minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        
        elif self.frequency == 'WEEKLY':
            days_ahead = self.weekday - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=self.time_of_day.hour, minute=self.time_of_day.minute, second=0, microsecond=0)
        
        elif self.frequency == 'MONTHLY':
            next_run = now.replace(day=self.day_of_month, hour=self.time_of_day.hour, minute=self.time_of_day.minute, second=0, microsecond=0)
            if next_run <= now:
                # Move to next month
                if now.month == 12:
                    next_run = next_run.replace(year=now.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=now.month + 1)
        
        elif self.frequency == 'QUARTERLY':
            # Find next quarter start (Jan, Apr, Jul, Oct)
            quarter_months = [1, 4, 7, 10]
            current_quarter_month = min([m for m in quarter_months if m >= now.month], default=quarter_months[0])
            if current_quarter_month <= now.month:
                next_year = now.year + 1
                next_month = quarter_months[0]
            else:
                next_year = now.year
                next_month = current_quarter_month
            next_run = now.replace(year=next_year, month=next_month, day=self.day_of_month or 1, hour=self.time_of_day.hour, minute=self.time_of_day.minute, second=0, microsecond=0)
        
        else:
            next_run = now + timedelta(days=7)
        
        self.next_run = next_run
        self.save(update_fields=['next_run'])
        return next_run


# ============================================================================
# TASK 28: KPI TRACKING SYSTEM
# Models for defining KPIs, setting targets, and tracking performance
# ============================================================================

class KPIDefinition(models.Model):
    """Define Key Performance Indicators for tracking"""
    CATEGORY_CHOICES = [
        ('STAFFING', 'Staffing Metrics'),
        ('OCCUPANCY', 'Occupancy Metrics'),
        ('FINANCIAL', 'Financial Metrics'),
        ('COMPLIANCE', 'Compliance Metrics'),
        ('QUALITY', 'Quality of Care'),
        ('EFFICIENCY', 'Operational Efficiency'),
    ]
    
    CALCULATION_TYPE_CHOICES = [
        ('PERCENTAGE', 'Percentage'),
        ('COUNT', 'Count'),
        ('AVERAGE', 'Average'),
        ('RATIO', 'Ratio'),
        ('CURRENCY', 'Currency Amount'),
    ]
    
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
    ]
    
    name = models.CharField(max_length=200, help_text="KPI name (e.g., 'Staff Turnover Rate')")
    description = models.TextField(help_text="What this KPI measures and why it matters")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    calculation_type = models.CharField(max_length=20, choices=CALCULATION_TYPE_CHOICES)
    
    # Calculation formula (stored as reference, actual calculation in service layer)
    formula_description = models.TextField(
        help_text="Human-readable formula (e.g., '(Staff Left / Total Staff) * 100')"
    )
    
    # Measurement settings
    measurement_frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='MONTHLY',
        help_text="How often this KPI should be measured"
    )
    
    # Target direction (higher is better or lower is better)
    higher_is_better = models.BooleanField(
        default=True,
        help_text="True if higher values are better, False if lower values are better"
    )
    
    # Alert thresholds
    critical_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Critical alert threshold"
    )
    warning_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Warning alert threshold"
    )
    
    # Scope
    care_home = models.ForeignKey(
        'CareHome',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Specific care home (null for system-wide KPI)"
    )
    unit = models.ForeignKey(
        'Unit',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Specific unit (null for home-wide or system-wide KPI)"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_kpis')
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'KPI Definition'
        verbose_name_plural = 'KPI Definitions'
    
    def __str__(self):
        scope = f" - {self.care_home.name}" if self.care_home else " - System-wide"
        return f"{self.name}{scope}"


class KPITarget(models.Model):
    """Set targets for KPIs by period"""
    kpi = models.ForeignKey(KPIDefinition, on_delete=models.CASCADE, related_name='targets')
    
    # Target period
    year = models.IntegerField(help_text="Target year")
    quarter = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        null=True,
        blank=True,
        help_text="Quarter (1-4) for quarterly targets"
    )
    month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        null=True,
        blank=True,
        help_text="Month (1-12) for monthly targets"
    )
    
    # Target values
    target_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Target value to achieve"
    )
    stretch_target = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Ambitious stretch target"
    )
    minimum_acceptable = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum acceptable performance"
    )
    
    notes = models.TextField(blank=True, null=True, help_text="Target setting rationale or context")
    
    set_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='set_kpi_targets')
    set_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-year', '-quarter', '-month']
        unique_together = [['kpi', 'year', 'quarter', 'month']]
        verbose_name = 'KPI Target'
        verbose_name_plural = 'KPI Targets'
    
    def __str__(self):
        period = f"{self.year}"
        if self.quarter:
            period += f" Q{self.quarter}"
        if self.month:
            period += f" M{self.month}"
        return f"{self.kpi.name} - {period}: {self.target_value}"


class KPIMeasurement(models.Model):
    """Record actual KPI measurements"""
    STATUS_CHOICES = [
        ('EXCELLENT', 'Exceeds Target'),
        ('GOOD', 'Meets Target'),
        ('WARNING', 'Below Target'),
        ('CRITICAL', 'Critical Threshold Breached'),
    ]
    
    kpi = models.ForeignKey(KPIDefinition, on_delete=models.CASCADE, related_name='measurements')
    
    # Measurement period
    measurement_date = models.DateField(help_text="Date of measurement")
    period_start = models.DateField(help_text="Start of measurement period")
    period_end = models.DateField(help_text="End of measurement period")
    
    # Measured value
    measured_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Actual measured value"
    )
    
    # Context data (stored as JSON for flexibility)
    calculation_details = models.JSONField(
        default=dict,
        help_text="Breakdown of how value was calculated (numerator, denominator, etc.)"
    )
    
    # Performance assessment
    target_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Target value at time of measurement"
    )
    variance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Difference from target (measured - target)"
    )
    variance_percentage = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage variance from target"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        help_text="Performance status vs target"
    )
    
    # Alerts
    alert_generated = models.BooleanField(
        default=False,
        help_text="True if this measurement triggered an alert"
    )
    alert_message = models.TextField(
        blank=True,
        null=True,
        help_text="Alert message if threshold breached"
    )
    
    # Metadata
    measured_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='kpi_measurements',
        help_text="User who recorded measurement (null for automated)"
    )
    measured_at = models.DateTimeField(auto_now_add=True)
    is_automated = models.BooleanField(
        default=True,
        help_text="True if automatically calculated, False if manually entered"
    )
    
    class Meta:
        ordering = ['-measurement_date']
        unique_together = [['kpi', 'measurement_date']]
        verbose_name = 'KPI Measurement'
        verbose_name_plural = 'KPI Measurements'
        indexes = [
            models.Index(fields=['kpi', '-measurement_date']),
            models.Index(fields=['status', 'alert_generated']),
        ]
    
    def __str__(self):
        return f"{self.kpi.name} - {self.measurement_date}: {self.measured_value} ({self.status})"


# ==========================================================================================
# DATA VISUALIZATION MODELS (PHASE 3 - TASK 29)
# Interactive dashboard builder with customizable widgets
# ==========================================================================================

class DashboardLayout(models.Model):
    """
    Custom dashboard layout configuration
    Allows managers to create personalized dashboards with widgets
    """
    name = models.CharField(max_length=200, help_text="Dashboard name")
    description = models.TextField(blank=True, help_text="Dashboard description")
    
    # Owner
    created_by = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='dashboards',
        help_text="Dashboard creator"
    )
    
    # Scope
    care_home = models.ForeignKey(
        'CareHome',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='dashboards',
        help_text="Specific care home (null for system-wide)"
    )
    
    # Layout configuration (JSON)
    layout_config = models.JSONField(
        default=dict,
        help_text="Grid layout configuration (rows, columns, widget positions)"
    )
    
    # Sharing
    is_public = models.BooleanField(
        default=False,
        help_text="Share with other managers"
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Set as default dashboard for care home"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Dashboard Layout'
        verbose_name_plural = 'Dashboard Layouts'
    
    def __str__(self):
        scope = f" - {self.care_home.name}" if self.care_home else " (System)"
        return f"{self.name}{scope}"


class ChartWidget(models.Model):
    """
    Individual chart/visualization widget
    Can be added to dashboards for custom views
    """
    CHART_TYPES = [
        ('LINE', 'Line Chart'),
        ('BAR', 'Bar Chart'),
        ('PIE', 'Pie Chart'),
        ('DOUGHNUT', 'Doughnut Chart'),
        ('RADAR', 'Radar Chart'),
        ('HEATMAP', 'Heat Map'),
        ('GAUGE', 'Gauge'),
        ('TABLE', 'Data Table'),
        ('STAT_CARD', 'Stat Card'),
    ]
    
    DATA_SOURCES = [
        ('STAFF_COUNT', 'Staff Count'),
        ('SHIFT_COUNT', 'Shift Count'),
        ('OCCUPANCY', 'Occupancy Rate'),
        ('LEAVE_REQUESTS', 'Leave Requests'),
        ('TRAINING_STATUS', 'Training Status'),
        ('AGENCY_USAGE', 'Agency Usage'),
        ('OVERTIME_HOURS', 'Overtime Hours'),
        ('TURNOVER_RATE', 'Staff Turnover'),
        ('COMPLIANCE_RATE', 'Compliance Rate'),
        ('INCIDENT_COUNT', 'Incident Count'),
        ('KPI_METRIC', 'KPI Metric'),
        ('CUSTOM_QUERY', 'Custom Query'),
    ]
    
    REFRESH_INTERVALS = [
        ('MANUAL', 'Manual Only'),
        ('REALTIME', 'Real-time'),
        ('5MIN', 'Every 5 Minutes'),
        ('15MIN', 'Every 15 Minutes'),
        ('1HOUR', 'Every Hour'),
        ('1DAY', 'Daily'),
    ]
    
    # Widget identification
    dashboard = models.ForeignKey(
        'DashboardLayout',
        on_delete=models.CASCADE,
        related_name='widgets',
        help_text="Parent dashboard"
    )
    title = models.CharField(max_length=200, help_text="Widget title")
    
    # Visualization type
    chart_type = models.CharField(
        max_length=20,
        choices=CHART_TYPES,
        default='LINE',
        help_text="Type of chart/visualization"
    )
    
    # Data configuration
    data_source = models.CharField(
        max_length=50,
        choices=DATA_SOURCES,
        help_text="Primary data source"
    )
    data_config = models.JSONField(
        default=dict,
        help_text="Data source configuration (filters, aggregation, grouping)"
    )
    
    # Chart styling (JSON)
    chart_config = models.JSONField(
        default=dict,
        help_text="Chart.js configuration (colors, labels, options)"
    )
    
    # Position & size
    grid_position = models.JSONField(
        default=dict,
        help_text="Position in dashboard grid (row, col, rowspan, colspan)"
    )
    
    # Behavior
    refresh_interval = models.CharField(
        max_length=20,
        choices=REFRESH_INTERVALS,
        default='MANUAL',
        help_text="How often to refresh data"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['dashboard', 'grid_position']
        verbose_name = 'Chart Widget'
        verbose_name_plural = 'Chart Widgets'
    
    def __str__(self):
        return f"{self.title} ({self.get_chart_type_display()}) - {self.dashboard.name}"


class DataVisualization(models.Model):
    """
    Saved visualization configuration for reuse
    Can be shared across dashboards
    """
    VISUALIZATION_TYPES = [
        ('STAFFING_HEATMAP', 'Staffing Heat Map'),
        ('SHIFT_TIMELINE', 'Shift Timeline'),
        ('OCCUPANCY_TREND', 'Occupancy Trend'),
        ('TRAINING_MATRIX', 'Training Matrix'),
        ('LEAVE_CALENDAR', 'Leave Calendar'),
        ('AGENCY_BREAKDOWN', 'Agency Breakdown'),
        ('COST_ANALYSIS', 'Cost Analysis'),
        ('PERFORMANCE_RADAR', 'Performance Radar'),
        ('CUSTOM', 'Custom Visualization'),
    ]
    
    # Identification
    name = models.CharField(max_length=200, help_text="Visualization name")
    description = models.TextField(blank=True)
    visualization_type = models.CharField(
        max_length=50,
        choices=VISUALIZATION_TYPES,
        help_text="Type of visualization"
    )
    
    # Configuration
    config = models.JSONField(
        default=dict,
        help_text="Complete visualization configuration"
    )
    
    # Sharing
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='visualizations',
        help_text="Creator"
    )
    is_public = models.BooleanField(
        default=False,
        help_text="Share with other managers"
    )
    
    # Scope
    care_home = models.ForeignKey(
        'CareHome',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='visualizations',
        help_text="Specific care home (null for system-wide)"
    )
    
    # Usage tracking
    use_count = models.IntegerField(
        default=0,
        help_text="Number of times used in dashboards"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Data Visualization'
        verbose_name_plural = 'Data Visualizations'
    
    def __str__(self):
        return f"{self.name} ({self.get_visualization_type_display()})"


# ==========================================================================================
# TREND ANALYSIS MODELS (PHASE 3 - TASK 30)
# Statistical analysis, seasonality detection, anomaly detection
# ==========================================================================================

class TrendAnalysis(models.Model):
    """
    Trend analysis results for metrics over time
    Tracks historical patterns and forecasts
    """
    METRIC_TYPES = [
        ('STAFF_COUNT', 'Staff Count'),
        ('SHIFT_VOLUME', 'Shift Volume'),
        ('OCCUPANCY', 'Occupancy Rate'),
        ('AGENCY_USAGE', 'Agency Usage'),
        ('OVERTIME', 'Overtime Hours'),
        ('TURNOVER', 'Staff Turnover'),
        ('LEAVE_REQUESTS', 'Leave Requests'),
        ('INCIDENTS', 'Incident Count'),
        ('TRAINING_COMPLETION', 'Training Completion'),
        ('COST', 'Cost Metrics'),
    ]
    
    TREND_DIRECTIONS = [
        ('INCREASING', 'Increasing'),
        ('DECREASING', 'Decreasing'),
        ('STABLE', 'Stable'),
        ('VOLATILE', 'Volatile'),
    ]
    
    # Identification
    metric_type = models.CharField(
        max_length=50,
        choices=METRIC_TYPES,
        help_text="Type of metric analyzed"
    )
    name = models.CharField(max_length=200, help_text="Analysis name")
    description = models.TextField(blank=True)
    
    # Scope
    care_home = models.ForeignKey(
        'CareHome',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='trend_analyses',
        help_text="Specific care home (null for system-wide)"
    )
    unit = models.ForeignKey(
        'Unit',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='trend_analyses',
        help_text="Specific unit (null for wider scope)"
    )
    
    # Analysis period
    start_date = models.DateField(help_text="Analysis start date")
    end_date = models.DateField(help_text="Analysis end date")
    
    # Trend results
    trend_direction = models.CharField(
        max_length=20,
        choices=TREND_DIRECTIONS,
        help_text="Overall trend direction"
    )
    slope = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="Linear regression slope"
    )
    r_squared = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Coefficient of determination (goodness of fit)"
    )
    
    # Statistical data (JSON)
    time_series_data = models.JSONField(
        default=dict,
        help_text="Raw time series data points {date: value}"
    )
    decomposition = models.JSONField(
        default=dict,
        help_text="Trend, seasonal, residual components"
    )
    statistics = models.JSONField(
        default=dict,
        help_text="Mean, median, std dev, min, max, etc."
    )
    
    # Forecast
    forecast_data = models.JSONField(
        default=dict,
        help_text="Predicted future values"
    )
    confidence_interval = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Forecast confidence level (%)"
    )
    
    # Metadata
    analyzed_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='trend_analyses',
        help_text="User who ran analysis"
    )
    analyzed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-analyzed_at']
        verbose_name = 'Trend Analysis'
        verbose_name_plural = 'Trend Analyses'
    
    def __str__(self):
        scope = f" - {self.care_home.name}" if self.care_home else ""
        return f"{self.name}{scope} ({self.start_date} to {self.end_date})"


class SeasonalityPattern(models.Model):
    """
    Detected seasonal patterns in metrics
    Identifies recurring patterns (daily, weekly, monthly)
    """
    PATTERN_TYPES = [
        ('DAILY', 'Daily Pattern'),
        ('WEEKLY', 'Weekly Pattern'),
        ('MONTHLY', 'Monthly Pattern'),
        ('QUARTERLY', 'Quarterly Pattern'),
        ('YEARLY', 'Yearly Pattern'),
    ]
    
    # Link to analysis
    trend_analysis = models.ForeignKey(
        'TrendAnalysis',
        on_delete=models.CASCADE,
        related_name='seasonality_patterns',
        help_text="Parent trend analysis"
    )
    
    # Pattern details
    pattern_type = models.CharField(
        max_length=20,
        choices=PATTERN_TYPES,
        help_text="Type of seasonal pattern"
    )
    strength = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Pattern strength (0-100%)"
    )
    
    # Pattern data (JSON)
    pattern_data = models.JSONField(
        default=dict,
        help_text="Pattern values by period (e.g., by day of week)"
    )
    peak_periods = models.JSONField(
        default=list,
        help_text="Periods with highest values"
    )
    trough_periods = models.JSONField(
        default=list,
        help_text="Periods with lowest values"
    )
    
    # Statistical significance
    p_value = models.DecimalField(
        max_digits=6,
        decimal_places=5,
        null=True,
        blank=True,
        help_text="Statistical significance (p-value)"
    )
    is_significant = models.BooleanField(
        default=False,
        help_text="True if pattern is statistically significant"
    )
    
    # Metadata
    detected_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-strength']
        verbose_name = 'Seasonality Pattern'
        verbose_name_plural = 'Seasonality Patterns'
    
    def __str__(self):
        return f"{self.get_pattern_type_display()} - {self.strength}% strength"


class AnomalyDetection(models.Model):
    """
    Detected anomalies in metrics
    Identifies unusual patterns or outliers
    """
    ANOMALY_TYPES = [
        ('SPIKE', 'Spike (Sudden Increase)'),
        ('DROP', 'Drop (Sudden Decrease)'),
        ('OUTLIER', 'Outlier (Statistical)'),
        ('SHIFT', 'Level Shift'),
        ('TREND_CHANGE', 'Trend Change'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    # Link to analysis
    trend_analysis = models.ForeignKey(
        'TrendAnalysis',
        on_delete=models.CASCADE,
        related_name='anomalies',
        help_text="Parent trend analysis"
    )
    
    # Anomaly details
    anomaly_type = models.CharField(
        max_length=20,
        choices=ANOMALY_TYPES,
        help_text="Type of anomaly detected"
    )
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_LEVELS,
        default='MEDIUM',
        help_text="Severity level"
    )
    
    # Occurrence
    detected_date = models.DateField(help_text="Date of anomaly")
    actual_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Actual value at anomaly"
    )
    expected_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Expected value (from trend)"
    )
    deviation = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Deviation from expected"
    )
    deviation_percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Percentage deviation"
    )
    
    # Statistical measures
    z_score = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Standard deviations from mean"
    )
    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Detection confidence (%)"
    )
    
    # Context
    description = models.TextField(
        blank=True,
        help_text="Description of anomaly and potential causes"
    )
    
    # Alert status
    alert_generated = models.BooleanField(
        default=False,
        help_text="True if alert was sent"
    )
    acknowledged = models.BooleanField(
        default=False,
        help_text="True if anomaly acknowledged by manager"
    )
    acknowledged_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_anomalies',
        help_text="User who acknowledged"
    )
    acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When acknowledged"
    )
    
    # Metadata
    detected_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-severity', '-detected_date']
        verbose_name = 'Anomaly Detection'
        verbose_name_plural = 'Anomaly Detections'
        indexes = [
            models.Index(fields=['trend_analysis', '-detected_date']),
            models.Index(fields=['severity', 'acknowledged']),
        ]
    
    def __str__(self):
        return f"{self.get_anomaly_type_display()} on {self.detected_date} ({self.severity})"


# ============================================================================
# SHIFT PATTERN ANALYSIS MODELS (Phase 3 - Task 31)
# ============================================================================

class ShiftPattern(models.Model):
    """
    Store identified shift patterns and staffing trends
    """
    PATTERN_TYPE_CHOICES = [
        ('PEAK', 'Peak Period'),
        ('TROUGH', 'Trough Period'),
        ('BALANCED', 'Balanced Coverage'),
        ('UNDERSTAFFED', 'Understaffed'),
        ('OVERSTAFFED', 'Overstaffed'),
    ]
    
    DAY_OF_WEEK_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    care_home = models.ForeignKey('CareHome', on_delete=models.CASCADE, null=True, blank=True)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, null=True, blank=True)
    
    # Pattern identification
    pattern_type = models.CharField(max_length=20, choices=PATTERN_TYPE_CHOICES)
    day_of_week = models.IntegerField(choices=DAY_OF_WEEK_CHOICES, null=True, blank=True)
    shift_type = models.CharField(max_length=20, blank=True)  # EARLY, LATE, NIGHT, etc.
    
    # Analysis period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Pattern metrics
    average_staff_count = models.DecimalField(max_digits=6, decimal_places=2)
    required_staff_count = models.DecimalField(max_digits=6, decimal_places=2)
    coverage_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # Coverage %
    
    # Pattern data (JSON)
    pattern_data = models.JSONField(
        default=dict,
        help_text='Daily staffing levels and trends'
    )
    
    # Frequency and recurrence
    frequency = models.IntegerField(
        default=0,
        help_text='Number of times this pattern occurs'
    )
    is_recurring = models.BooleanField(default=False)
    
    # Recommendations
    recommendation = models.TextField(blank=True)
    priority = models.CharField(
        max_length=20,
        choices=[
            ('LOW', 'Low Priority'),
            ('MEDIUM', 'Medium Priority'),
            ('HIGH', 'High Priority'),
            ('CRITICAL', 'Critical Priority'),
        ],
        default='MEDIUM'
    )
    
    # Metadata
    analyzed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Shift Pattern'
        verbose_name_plural = 'Shift Patterns'
        ordering = ['-analyzed_at', 'day_of_week']
        indexes = [
            models.Index(fields=['care_home', 'pattern_type']),
            models.Index(fields=['day_of_week', 'shift_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_pattern_type_display()})"


class CoverageGap(models.Model):
    """
    Track identified coverage gaps in staffing
    """
    SEVERITY_CHOICES = [
        ('LOW', 'Low Severity'),
        ('MEDIUM', 'Medium Severity'),
        ('HIGH', 'High Severity'),
        ('CRITICAL', 'Critical Severity'),
    ]
    
    shift_pattern = models.ForeignKey(
        ShiftPattern,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='coverage_gaps'
    )
    
    care_home = models.ForeignKey('CareHome', on_delete=models.CASCADE)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, null=True, blank=True)
    
    # Gap identification
    gap_date = models.DateField()
    shift_type = models.CharField(max_length=20)
    
    # Staffing levels
    required_staff = models.IntegerField()
    actual_staff = models.IntegerField()
    gap_size = models.IntegerField(help_text='Required - Actual')
    gap_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Severity and impact
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    impact_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Impact score (0-100)'
    )
    
    # Resolution
    is_filled = models.BooleanField(default=False)
    filled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='filled_gaps'
    )
    filled_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    # Alerts
    alert_sent = models.BooleanField(default=False)
    alert_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    detected_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Coverage Gap'
        verbose_name_plural = 'Coverage Gaps'
        ordering = ['-gap_date', '-severity']
        indexes = [
            models.Index(fields=['care_home', 'gap_date']),
            models.Index(fields=['severity', 'is_filled']),
            models.Index(fields=['-gap_date', 'shift_type']),
        ]
    
    def __str__(self):
        return f"Gap on {self.gap_date} ({self.shift_type}): {self.gap_size} staff short"


class WorkloadDistribution(models.Model):
    """
    Analyze and track workload distribution across staff and shifts
    """
    shift_pattern = models.ForeignKey(
        ShiftPattern,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='workload_distributions'
    )
    
    care_home = models.ForeignKey('CareHome', on_delete=models.CASCADE)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, null=True, blank=True)
    
    # Analysis period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Workload metrics (JSON)
    distribution_data = models.JSONField(
        default=dict,
        help_text='Workload distribution by staff, shift type, day of week'
    )
    
    # Balance metrics
    balance_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Distribution balance score (0-100, higher is better)'
    )
    gini_coefficient = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        help_text='Gini coefficient for inequality (0-1, lower is better)',
        null=True,
        blank=True
    )
    
    # Staff workload
    average_shifts_per_staff = models.DecimalField(max_digits=6, decimal_places=2)
    max_shifts_per_staff = models.IntegerField()
    min_shifts_per_staff = models.IntegerField()
    standard_deviation = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Shift type distribution
    shift_type_balance = models.JSONField(
        default=dict,
        help_text='Distribution across EARLY, LATE, NIGHT, etc.'
    )
    
    # Recommendations
    recommendations = models.TextField(blank=True)
    
    # Fairness indicators
    is_balanced = models.BooleanField(
        default=False,
        help_text='True if distribution is considered fair/balanced'
    )
    unfairness_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Unfairness score (0-100, lower is better)'
    )
    
    # Metadata
    analyzed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Workload Distribution'
        verbose_name_plural = 'Workload Distributions'
        ordering = ['-analyzed_at']
        indexes = [
            models.Index(fields=['care_home', '-analyzed_at']),
            models.Index(fields=['is_balanced']),
        ]
    
    def __str__(self):
        return f"Workload Distribution ({self.start_date} to {self.end_date})"


# ============================================================================
# COST ANALYTICS MODELS (Phase 3 - Task 32)
# ============================================================================

class CostAnalysis(models.Model):
    """
    Store cost analysis results for staffing expenses
    """
    COST_CATEGORY_CHOICES = [
        ('TOTAL', 'Total Staffing Cost'),
        ('PERMANENT', 'Permanent Staff Cost'),
        ('AGENCY', 'Agency Staff Cost'),
        ('OVERTIME', 'Overtime Cost'),
        ('TRAINING', 'Training Cost'),
        ('BENEFITS', 'Benefits Cost'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    care_home = models.ForeignKey('CareHome', on_delete=models.CASCADE, null=True, blank=True)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, null=True, blank=True)
    
    # Analysis period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Cost breakdown
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    permanent_staff_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    agency_staff_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    training_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    benefits_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Shift counts
    total_shifts = models.IntegerField(default=0)
    permanent_shifts = models.IntegerField(default=0)
    agency_shifts = models.IntegerField(default=0)
    overtime_shifts = models.IntegerField(default=0)
    
    # Cost per shift metrics
    cost_per_shift = models.DecimalField(max_digits=8, decimal_places=2)
    permanent_cost_per_shift = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    agency_cost_per_shift = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Efficiency metrics
    agency_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Percentage of shifts filled by agency staff'
    )
    cost_efficiency_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Cost efficiency score (0-100, higher is better)'
    )
    
    # Detailed cost data (JSON)
    cost_breakdown_data = models.JSONField(
        default=dict,
        help_text='Daily cost breakdown and trends'
    )
    
    # Cost categories distribution
    cost_by_category = models.JSONField(
        default=dict,
        help_text='Cost distribution by category'
    )
    
    # Savings opportunities
    potential_savings = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Potential cost savings identified'
    )
    savings_recommendations = models.TextField(blank=True)
    
    # Metadata
    analyzed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Cost Analysis'
        verbose_name_plural = 'Cost Analyses'
        ordering = ['-analyzed_at']
        indexes = [
            models.Index(fields=['care_home', '-analyzed_at']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.name} (£{self.total_cost:,.2f})"


class AgencyCostComparison(models.Model):
    """
    Compare agency vs permanent staff costs
    """
    cost_analysis = models.ForeignKey(
        CostAnalysis,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='agency_comparisons'
    )
    
    care_home = models.ForeignKey('CareHome', on_delete=models.CASCADE)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, null=True, blank=True)
    
    # Analysis period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Agency costs
    agency_total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    agency_shift_count = models.IntegerField()
    agency_cost_per_shift = models.DecimalField(max_digits=8, decimal_places=2)
    agency_hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Permanent costs
    permanent_total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    permanent_shift_count = models.IntegerField()
    permanent_cost_per_shift = models.DecimalField(max_digits=8, decimal_places=2)
    permanent_hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Comparison metrics
    cost_difference = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Agency cost - Permanent cost'
    )
    cost_difference_percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text='Percentage difference'
    )
    
    # Premium analysis
    agency_premium = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text='Agency premium over permanent (percentage)'
    )
    total_premium_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Total extra cost paid for agency staff'
    )
    
    # Potential savings
    if_all_permanent_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Cost if all shifts were permanent'
    )
    potential_monthly_savings = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Potential savings per month'
    )
    
    # Recommendations
    recommendation = models.TextField(blank=True)
    priority = models.CharField(
        max_length=20,
        choices=[
            ('LOW', 'Low Priority'),
            ('MEDIUM', 'Medium Priority'),
            ('HIGH', 'High Priority'),
            ('CRITICAL', 'Critical Priority'),
        ],
        default='MEDIUM'
    )
    
    # Metadata
    analyzed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Agency Cost Comparison'
        verbose_name_plural = 'Agency Cost Comparisons'
        ordering = ['-analyzed_at']
        indexes = [
            models.Index(fields=['care_home', '-analyzed_at']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"Agency vs Permanent ({self.start_date} to {self.end_date})"


class BudgetForecast(models.Model):
    """
    Budget forecasting for staffing costs
    """
    FORECAST_METHOD_CHOICES = [
        ('LINEAR', 'Linear Regression'),
        ('AVERAGE', 'Historical Average'),
        ('SEASONAL', 'Seasonal Adjustment'),
        ('TREND', 'Trend Analysis'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    care_home = models.ForeignKey('CareHome', on_delete=models.CASCADE, null=True, blank=True)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, null=True, blank=True)
    
    # Historical period
    historical_start_date = models.DateField()
    historical_end_date = models.DateField()
    
    # Forecast period
    forecast_start_date = models.DateField()
    forecast_end_date = models.DateField()
    forecast_months = models.IntegerField(help_text='Number of months forecasted')
    
    # Forecast method
    forecast_method = models.CharField(max_length=20, choices=FORECAST_METHOD_CHOICES)
    
    # Historical costs
    historical_total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    historical_average_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Forecasted costs
    forecasted_total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    forecasted_monthly_average = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Forecast breakdown (JSON)
    monthly_forecast = models.JSONField(
        default=dict,
        help_text='Month-by-month forecast data'
    )
    
    # Confidence and accuracy
    confidence_level = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Forecast confidence (0-100%)'
    )
    margin_of_error = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text='Margin of error (±%)'
    )
    
    # Budget targets
    budget_target = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Target budget for period'
    )
    budget_variance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Forecast - Target'
    )
    is_within_budget = models.BooleanField(
        default=False,
        help_text='True if forecast is within budget'
    )
    
    # Trend analysis
    trend_direction = models.CharField(
        max_length=20,
        choices=[
            ('INCREASING', 'Increasing'),
            ('DECREASING', 'Decreasing'),
            ('STABLE', 'Stable'),
        ],
        default='STABLE'
    )
    trend_percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text='Trend change percentage'
    )
    
    # Recommendations
    recommendations = models.TextField(blank=True)
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('LOW', 'Low Risk'),
            ('MEDIUM', 'Medium Risk'),
            ('HIGH', 'High Risk'),
            ('CRITICAL', 'Critical Risk'),
        ],
        default='LOW'
    )
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Budget Forecast'
        verbose_name_plural = 'Budget Forecasts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['care_home', '-created_at']),
            models.Index(fields=['forecast_start_date', 'forecast_end_date']),
        ]
    
    def __str__(self):
        return f"{self.name} (£{self.forecasted_total_cost:,.2f})"


# ========================
# Compliance Monitoring Models
# Phase 3 - Task 33
# ========================

class StaffCertification(models.Model):
    """
    Track staff certifications and their expiry dates
    """
    CERTIFICATION_TYPES = [
        ('FIRST_AID', 'First Aid'),
        ('MANUAL_HANDLING', 'Manual Handling'),
        ('FIRE_SAFETY', 'Fire Safety'),
        ('FOOD_HYGIENE', 'Food Hygiene'),
        ('MEDICATION', 'Medication Administration'),
        ('SAFEGUARDING', 'Safeguarding'),
        ('INFECTION_CONTROL', 'Infection Control'),
        ('DEMENTIA_CARE', 'Dementia Care'),
        ('PALLIATIVE_CARE', 'Palliative Care'),
        ('PVG', 'PVG Scheme'),
        ('SSSC', 'SSSC Registration'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('VALID', 'Valid'),
        ('EXPIRING_SOON', 'Expiring Soon'),
        ('EXPIRED', 'Expired'),
        ('PENDING', 'Pending Renewal'),
    ]
    
    staff_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certifications')
    certification_type = models.CharField(max_length=50, choices=CERTIFICATION_TYPES)
    certification_name = models.CharField(max_length=200)
    
    issue_date = models.DateField()
    expiry_date = models.DateField()
    renewal_date = models.DateField(null=True, blank=True, help_text="Expected renewal date")
    
    issuing_body = models.CharField(max_length=200, blank=True)
    certificate_number = models.CharField(max_length=100, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='VALID')
    
    # File attachment
    certificate_file = models.FileField(upload_to='certificates/', null=True, blank=True)
    
    # Alert settings
    days_before_expiry_alert = models.IntegerField(default=30, help_text="Days before expiry to send alert")
    alert_sent = models.BooleanField(default=False)
    alert_sent_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_certifications')
    
    class Meta:
        verbose_name = 'Staff Certification'
        verbose_name_plural = 'Staff Certifications'
        ordering = ['expiry_date']
        indexes = [
            models.Index(fields=['staff_member', 'expiry_date']),
            models.Index(fields=['certification_type', 'status']),
            models.Index(fields=['expiry_date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.staff_member.get_full_name()} - {self.get_certification_type_display()}"
    
    def save(self, *args, **kwargs):
        """Auto-update status based on expiry date"""
        from django.utils import timezone
        today = timezone.now().date()
        days_until_expiry = (self.expiry_date - today).days
        
        if days_until_expiry < 0:
            self.status = 'EXPIRED'
        elif days_until_expiry <= self.days_before_expiry_alert:
            self.status = 'EXPIRING_SOON'
        else:
            self.status = 'VALID'
        
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if certification has expired"""
        from django.utils import timezone
        return self.expiry_date < timezone.now().date()
    
    def days_until_expiry(self):
        """Calculate days until expiry"""
        from django.utils import timezone
        return (self.expiry_date - timezone.now().date()).days


class RegulatoryCheck(models.Model):
    """
    Track regulatory compliance checks and their results
    """
    CHECK_TYPES = [
        ('TRAINING', 'Training Compliance'),
        ('CERTIFICATION', 'Certification Check'),
        ('STAFFING_RATIO', 'Staffing Ratio'),
        ('DOCUMENTATION', 'Documentation Review'),
        ('HEALTH_SAFETY', 'Health & Safety'),
        ('CARE_STANDARDS', 'Care Standards'),
        ('MEDICATION', 'Medication Management'),
        ('FIRE_SAFETY', 'Fire Safety'),
        ('INFECTION_CONTROL', 'Infection Control'),
    ]
    
    STATUS_CHOICES = [
        ('PASS', 'Pass'),
        ('FAIL', 'Fail'),
        ('WARNING', 'Warning'),
        ('IN_PROGRESS', 'In Progress'),
    ]
    
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    care_home = models.ForeignKey('CareHome', on_delete=models.CASCADE, related_name='regulatory_checks')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, blank=True, related_name='regulatory_checks')
    
    check_type = models.CharField(max_length=50, choices=CHECK_TYPES)
    check_name = models.CharField(max_length=200)
    description = models.TextField()
    
    check_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MEDIUM')
    
    # Results
    compliance_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Compliance score (0-100%)"
    )
    findings = models.TextField(blank=True, help_text="Detailed findings from the check")
    violations_found = models.IntegerField(default=0)
    
    # Actions
    action_required = models.BooleanField(default=False)
    action_plan = models.TextField(blank=True)
    action_deadline = models.DateField(null=True, blank=True)
    action_completed = models.BooleanField(default=False)
    action_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    checked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='regulatory_checks_performed')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='regulatory_checks_reviewed')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Regulatory Check'
        verbose_name_plural = 'Regulatory Checks'
        ordering = ['-check_date']
        indexes = [
            models.Index(fields=['care_home', '-check_date']),
            models.Index(fields=['check_type', 'status']),
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['due_date', 'action_completed']),
        ]
    
    def __str__(self):
        return f"{self.check_name} - {self.check_date} ({self.get_status_display()})"
    
    def is_overdue(self):
        """Check if compliance check is overdue"""
        from django.utils import timezone
        if self.due_date and not self.action_completed:
            return self.due_date < timezone.now().date()
        return False


class AuditTrail(models.Model):
    """
    Track system audit trail for compliance and security
    """
    ACTION_TYPES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('APPROVE', 'Approve'),
        ('REJECT', 'Reject'),
        ('OVERRIDE', 'Override'),
    ]
    
    ENTITY_TYPES = [
        ('SHIFT', 'Shift'),
        ('STAFF', 'Staff'),
        ('LEAVE', 'Leave Request'),
        ('SWAP', 'Shift Swap'),
        ('CERTIFICATION', 'Certification'),
        ('COMPLIANCE', 'Compliance Check'),
        ('REPORT', 'Report'),
        ('COST', 'Cost Analysis'),
        ('FORECAST', 'Budget Forecast'),
        ('USER', 'User'),
        ('SYSTEM', 'System'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_trail')
    care_home = models.ForeignKey('CareHome', on_delete=models.CASCADE, related_name='audit_trails')
    
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPES)
    entity_id = models.IntegerField(null=True, blank=True, help_text="ID of the affected entity")
    
    description = models.TextField()
    
    # Before/After state for changes
    before_state = models.JSONField(null=True, blank=True, help_text="State before change")
    after_state = models.JSONField(null=True, blank=True, help_text="State after change")
    
    # Request details
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    # Compliance flags
    is_sensitive = models.BooleanField(default=False, help_text="Contains sensitive data")
    requires_review = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_reviews')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Audit Trail Entry'
        verbose_name_plural = 'Audit Trail Entries'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['care_home', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action_type', 'entity_type']),
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['is_sensitive', 'reviewed']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.get_action_type_display()} {self.get_entity_type_display()} at {self.timestamp}"
    
    @classmethod
    def log_action(cls, user, care_home, action_type, entity_type, description, entity_id=None, 
                   before_state=None, after_state=None, ip_address=None, user_agent=None, 
                   is_sensitive=False, requires_review=False):
        """
        Convenience method to create audit log entries
        """
        return cls.objects.create(
            user=user,
            care_home=care_home,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            before_state=before_state,
            after_state=after_state,
            ip_address=ip_address,
            user_agent=user_agent,
            is_sensitive=is_sensitive,
            requires_review=requires_review,
        )


# ========================
# Staff Performance Models
# Phase 3 - Task 34
# ========================

class AttendanceRecord(models.Model):
    """Track staff attendance and punctuality"""
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('LATE', 'Late'),
        ('ABSENT', 'Absent'),
        ('SICK', 'Sick Leave'),
        ('AUTHORIZED', 'Authorized Absence'),
        ('UNAUTHORIZED', 'Unauthorized Absence'),
    ]
    
    staff_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='attendance_records')
    
    date = models.DateField()
    shift_type = models.CharField(max_length=20)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENT')
    
    # Time tracking
    scheduled_start = models.TimeField()
    actual_start = models.TimeField(null=True, blank=True)
    scheduled_end = models.TimeField()
    actual_end = models.TimeField(null=True, blank=True)
    
    # Punctuality
    minutes_late = models.IntegerField(default=0, help_text="Minutes late for shift start")
    minutes_early_departure = models.IntegerField(default=0, help_text="Minutes left before shift end")
    
    # Completion
    shift_completed = models.BooleanField(default=True)
    completion_notes = models.TextField(blank=True)
    
    # Documentation
    reason_for_absence = models.TextField(blank=True)
    documentation_provided = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_attendance')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'
        ordering = ['-date']
        unique_together = ['staff_member', 'shift']
        indexes = [
            models.Index(fields=['staff_member', '-date']),
            models.Index(fields=['date', 'status']),
            models.Index(fields=['shift', 'status']),
        ]
    
    def __str__(self):
        return f"{self.staff_member.get_full_name()} - {self.date} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """Calculate punctuality metrics"""
        if self.actual_start and self.scheduled_start:
            from datetime import datetime, timedelta
            scheduled = datetime.combine(self.date, self.scheduled_start)
            actual = datetime.combine(self.date, self.actual_start)
            diff = (actual - scheduled).total_seconds() / 60
            self.minutes_late = max(0, int(diff))
            
        if self.actual_end and self.scheduled_end:
            from datetime import datetime, timedelta
            scheduled = datetime.combine(self.date, self.scheduled_end)
            actual = datetime.combine(self.date, self.actual_end)
            diff = (scheduled - actual).total_seconds() / 60
            self.minutes_early_departure = max(0, int(diff))
        
        super().save(*args, **kwargs)


class StaffPerformance(models.Model):
    """Track staff performance metrics and scores"""
    staff_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_records')
    care_home = models.ForeignKey('CareHome', on_delete=models.CASCADE, related_name='staff_performance')
    
    # Period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Attendance Metrics
    total_shifts = models.IntegerField(default=0)
    shifts_attended = models.IntegerField(default=0)
    shifts_late = models.IntegerField(default=0)
    shifts_absent = models.IntegerField(default=0)
    unauthorized_absences = models.IntegerField(default=0)
    
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Percentage (0-100)")
    punctuality_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Percentage (0-100)")
    
    # Completion Metrics
    shifts_completed = models.IntegerField(default=0)
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Percentage (0-100)")
    
    # Time Metrics
    total_minutes_late = models.IntegerField(default=0)
    average_minutes_late = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Performance Scores
    attendance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Score 0-100")
    punctuality_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Score 0-100")
    completion_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Score 0-100")
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Score 0-100")
    
    # Rating
    RATING_CHOICES = [
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('SATISFACTORY', 'Satisfactory'),
        ('NEEDS_IMPROVEMENT', 'Needs Improvement'),
        ('POOR', 'Poor'),
    ]
    performance_rating = models.CharField(max_length=20, choices=RATING_CHOICES, default='SATISFACTORY')
    
    # Feedback
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    manager_notes = models.TextField(blank=True)
    
    # Review
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='performance_reviews_given')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Staff Performance'
        verbose_name_plural = 'Staff Performance Records'
        ordering = ['-period_end']
        unique_together = ['staff_member', 'period_start', 'period_end']
        indexes = [
            models.Index(fields=['staff_member', '-period_end']),
            models.Index(fields=['care_home', 'performance_rating']),
            models.Index(fields=['overall_score']),
        ]
    
    def __str__(self):
        return f"{self.staff_member.get_full_name()} - {self.period_start} to {self.period_end} ({self.overall_score})"
    
    def calculate_scores(self):
        """Calculate all performance scores"""
        # Attendance Score (0-100)
        if self.total_shifts > 0:
            self.attendance_rate = (self.shifts_attended / self.total_shifts) * 100
            self.attendance_score = self.attendance_rate
            
            # Punctuality Score (0-100) - penalize lateness
            on_time_shifts = self.shifts_attended - self.shifts_late
            self.punctuality_rate = (on_time_shifts / self.total_shifts) * 100 if self.total_shifts > 0 else 100
            self.punctuality_score = self.punctuality_rate
            
            # Completion Score (0-100)
            self.completion_rate = (self.shifts_completed / self.total_shifts) * 100
            self.completion_score = self.completion_rate
        else:
            self.attendance_rate = 100
            self.attendance_score = 100
            self.punctuality_rate = 100
            self.punctuality_score = 100
            self.completion_rate = 100
            self.completion_score = 100
        
        # Average minutes late
        if self.shifts_late > 0:
            self.average_minutes_late = self.total_minutes_late / self.shifts_late
        else:
            self.average_minutes_late = 0
        
        # Overall Score (weighted average)
        self.overall_score = (
            self.attendance_score * 0.4 +  # 40% weight
            self.punctuality_score * 0.3 +  # 30% weight
            self.completion_score * 0.3     # 30% weight
        )
        
        # Determine rating
        if self.overall_score >= 90:
            self.performance_rating = 'EXCELLENT'
        elif self.overall_score >= 75:
            self.performance_rating = 'GOOD'
        elif self.overall_score >= 60:
            self.performance_rating = 'SATISFACTORY'
        elif self.overall_score >= 40:
            self.performance_rating = 'NEEDS_IMPROVEMENT'
        else:
            self.performance_rating = 'POOR'
        
        self.save()


class PerformanceReview(models.Model):
    """Formal performance review records"""
    REVIEW_TYPES = [
        ('PROBATION', 'Probation Review'),
        ('QUARTERLY', 'Quarterly Review'),
        ('ANNUAL', 'Annual Review'),
        ('DISCIPLINARY', 'Disciplinary Review'),
        ('EXCELLENCE', 'Excellence Recognition'),
    ]
    
    staff_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='formal_reviews')
    care_home = models.ForeignKey('CareHome', on_delete=models.CASCADE, related_name='performance_reviews')
    
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPES)
    review_date = models.DateField()
    
    # Linked performance record
    performance_record = models.ForeignKey(StaffPerformance, on_delete=models.SET_NULL, null=True, blank=True, related_name='formal_reviews')
    
    # Scores (manager assessment)
    quality_of_work = models.IntegerField(default=5, help_text="Score 1-10")
    reliability = models.IntegerField(default=5, help_text="Score 1-10")
    teamwork = models.IntegerField(default=5, help_text="Score 1-10")
    communication = models.IntegerField(default=5, help_text="Score 1-10")
    professionalism = models.IntegerField(default=5, help_text="Score 1-10")
    
    # Comments
    achievements = models.TextField(blank=True)
    concerns = models.TextField(blank=True)
    development_goals = models.TextField(blank=True)
    action_plan = models.TextField(blank=True)
    
    # Staff feedback
    staff_comments = models.TextField(blank=True)
    staff_acknowledged = models.BooleanField(default=False)
    staff_acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    # Outcome
    OUTCOME_CHOICES = [
        ('CONTINUE', 'Continue as Normal'),
        ('IMPROVE', 'Improvement Plan'),
        ('PROMOTE', 'Promotion Recommended'),
        ('WARNING', 'Formal Warning'),
        ('TERMINATE', 'Termination Recommended'),
    ]
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, default='CONTINUE')
    
    # Review details
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reviews_conducted')
    next_review_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Performance Review'
        verbose_name_plural = 'Performance Reviews'
        ordering = ['-review_date']
        indexes = [
            models.Index(fields=['staff_member', '-review_date']),
            models.Index(fields=['review_type', 'outcome']),
        ]
    
    def __str__(self):
        return f"{self.staff_member.get_full_name()} - {self.get_review_type_display()} ({self.review_date})"
    
    def average_score(self):
        """Calculate average score across all categories"""
        scores = [
            self.quality_of_work,
            self.reliability,
            self.teamwork,
            self.communication,
            self.professionalism,
        ]
        return sum(scores) / len(scores) if scores else 0


# =============================================================================
# TASK 35: PREDICTIVE LEAVE FORECASTING
# =============================================================================

class LeaveForecast(models.Model):
    """Predictive leave forecast for a staff member"""
    
    FORECAST_TYPE_CHOICES = [
        ('ANNUAL', 'Annual Leave'),
        ('SICK', 'Sick Leave'),
        ('PERSONAL', 'Personal Leave'),
        ('ALL', 'All Leave Types'),
    ]
    
    CONFIDENCE_LEVEL_CHOICES = [
        ('HIGH', 'High (>80%)'),
        ('MEDIUM', 'Medium (60-80%)'),
        ('LOW', 'Low (<60%)'),
    ]
    
    staff_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_forecasts')
    care_home = models.ForeignKey('CareHome', on_delete=models.CASCADE)
    forecast_type = models.CharField(max_length=20, choices=FORECAST_TYPE_CHOICES, default='ALL')
    
    # Forecast period
    forecast_date = models.DateField()
    forecast_start = models.DateField()
    forecast_end = models.DateField()
    
    # Predictions
    predicted_days = models.IntegerField(help_text="Predicted leave days in period")
    predicted_peak_month = models.CharField(max_length=20, blank=True, help_text="Month with highest predicted leave")
    predicted_pattern = models.TextField(blank=True, help_text="Description of predicted pattern")
    
    # Historical data used
    historical_period_months = models.IntegerField(default=12, help_text="Months of history analyzed")
    total_historical_days = models.IntegerField(default=0)
    average_days_per_month = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Confidence & accuracy
    confidence_level = models.CharField(max_length=10, choices=CONFIDENCE_LEVEL_CHOICES, default='MEDIUM')
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="0-100%")
    prediction_range_min = models.IntegerField(help_text="Minimum predicted days")
    prediction_range_max = models.IntegerField(help_text="Maximum predicted days")
    
    # Factors influencing forecast
    seasonal_factor = models.BooleanField(default=False, help_text="Seasonal pattern detected")
    trend_factor = models.CharField(max_length=20, blank=True, help_text="INCREASING/DECREASING/STABLE")
    special_events = models.TextField(blank=True, help_text="Known events affecting forecast")
    
    # Recommendations
    impact_level = models.CharField(max_length=20, default='MEDIUM', 
                                   choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('CRITICAL', 'Critical')])
    recommended_actions = models.TextField(blank=True)
    coverage_requirements = models.TextField(blank=True, help_text="Suggested coverage needs")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-forecast_date', '-created_at']
        indexes = [
            models.Index(fields=['staff_member', 'forecast_date']),
            models.Index(fields=['care_home', 'forecast_type']),
            models.Index(fields=['confidence_level', 'impact_level']),
        ]
    
    def __str__(self):
        return f"{self.staff_member.get_full_name()} - {self.get_forecast_type_display()} ({self.forecast_start} to {self.forecast_end})"


class LeavePattern(models.Model):
    """Identified leave patterns for analytics"""
    
    PATTERN_TYPE_CHOICES = [
        ('SEASONAL', 'Seasonal (e.g., summer, winter)'),
        ('MONTHLY', 'Monthly recurring'),
        ('WEEKLY', 'Weekly recurring'),
        ('EVENT_BASED', 'Event-based (e.g., school holidays)'),
        ('RANDOM', 'No clear pattern'),
    ]
    
    staff_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_patterns')
    care_home = models.ForeignKey('CareHome', on_delete=models.CASCADE)
    
    pattern_type = models.CharField(max_length=20, choices=PATTERN_TYPE_CHOICES)
    pattern_name = models.CharField(max_length=100)
    pattern_description = models.TextField()
    
    # Pattern details
    typical_duration_days = models.IntegerField(help_text="Typical leave duration")
    frequency_per_year = models.DecimalField(max_digits=5, decimal_places=2, help_text="How often per year")
    preferred_months = models.JSONField(default=list, blank=True, help_text="List of preferred months (1-12)")
    preferred_days_of_week = models.JSONField(default=list, blank=True, help_text="List of preferred days (0-6)")
    
    # Statistical data
    occurrences_found = models.IntegerField(default=0, help_text="Number of times pattern occurred")
    pattern_strength = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="0-100% strength")
    last_occurrence = models.DateField(null=True, blank=True)
    
    # Analysis period
    analyzed_from = models.DateField()
    analyzed_to = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-pattern_strength', '-created_at']
        indexes = [
            models.Index(fields=['staff_member', 'pattern_type']),
            models.Index(fields=['care_home', '-pattern_strength']),
        ]
    
    def __str__(self):
        return f"{self.staff_member.get_full_name()} - {self.pattern_name}"


class LeaveImpactAnalysis(models.Model):
    """Analysis of leave impact on staffing and operations"""
    
    IMPACT_SEVERITY_CHOICES = [
        ('MINIMAL', 'Minimal (<10% impact)'),
        ('MODERATE', 'Moderate (10-25% impact)'),
        ('SIGNIFICANT', 'Significant (25-50% impact)'),
        ('SEVERE', 'Severe (>50% impact)'),
    ]
    
    care_home = models.ForeignKey('CareHome', on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, blank=True)
    
    # Analysis period
    analysis_date = models.DateField(auto_now_add=True)
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Leave statistics
    total_leave_days = models.IntegerField(default=0)
    staff_on_leave_count = models.IntegerField(default=0)
    concurrent_leave_peak = models.IntegerField(default=0, help_text="Max staff on leave at once")
    concurrent_leave_peak_date = models.DateField(null=True, blank=True)
    
    # Impact metrics
    impact_severity = models.CharField(max_length=20, choices=IMPACT_SEVERITY_CHOICES, default='MINIMAL')
    coverage_gap_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime_hours_required = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    agency_shifts_needed = models.IntegerField(default=0)
    estimated_cost_impact = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Risk assessment
    understaffing_days = models.IntegerField(default=0, help_text="Days below minimum staffing")
    critical_skill_gaps = models.TextField(blank=True, help_text="Missing critical skills/roles")
    risk_level = models.CharField(max_length=20, default='LOW',
                                  choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('CRITICAL', 'Critical')])
    
    # Recommendations
    mitigation_strategies = models.TextField(blank=True)
    recommended_hires = models.IntegerField(default=0, help_text="Suggested additional staff")
    suggested_policy_changes = models.TextField(blank=True)
    
    # Detailed data
    impact_by_day = models.JSONField(default=dict, blank=True, help_text="Daily impact breakdown")
    affected_staff_list = models.JSONField(default=list, blank=True, help_text="List of affected staff IDs")
    
    class Meta:
        ordering = ['-analysis_date', '-risk_level']
        indexes = [
            models.Index(fields=['care_home', 'period_start']),
            models.Index(fields=['risk_level', 'impact_severity']),
        ]
    
    def __str__(self):
        return f"{self.care_home.name} - Impact Analysis ({self.period_start} to {self.period_end})"


# ==================== TASK 36: REAL-TIME COLLABORATION MODELS ====================

class Notification(models.Model):
    """
    Real-time notifications for users about system events
    """
    NOTIFICATION_TYPES = [
        ('SHIFT_ASSIGNED', 'Shift Assigned'),
        ('SHIFT_CHANGED', 'Shift Changed'),
        ('SHIFT_CANCELLED', 'Shift Cancelled'),
        ('LEAVE_APPROVED', 'Leave Request Approved'),
        ('LEAVE_REJECTED', 'Leave Request Rejected'),
        ('SWAP_REQUEST', 'Shift Swap Request'),
        ('SWAP_APPROVED', 'Swap Approved'),
        ('SWAP_REJECTED', 'Swap Rejected'),
        ('MESSAGE_RECEIVED', 'Message Received'),
        ('MENTION', 'Mentioned in Message'),
        ('COMPLIANCE_ALERT', 'Compliance Alert'),
        ('PERFORMANCE_REVIEW', 'Performance Review Due'),
        ('CERTIFICATION_EXPIRY', 'Certification Expiring'),
        ('SYSTEM_ALERT', 'System Alert'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='NORMAL')
    
    # Related objects (optional)
    related_shift = models.ForeignKey('Shift', on_delete=models.SET_NULL, null=True, blank=True)
    related_leave_request = models.ForeignKey('LeaveRequest', on_delete=models.SET_NULL, null=True, blank=True)
    related_swap = models.ForeignKey('ShiftSwapRequest', on_delete=models.SET_NULL, null=True, blank=True)
    related_message = models.ForeignKey('Message', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Action URL (where to redirect when clicked)
    action_url = models.CharField(max_length=500, blank=True)
    
    # Status tracking
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
            models.Index(fields=['recipient', 'notification_type']),
            models.Index(fields=['priority', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.recipient.username} - {self.get_notification_type_display()}"
    
    @property
    def user(self):
        """Backward compatibility property - alias for recipient"""
        return self.recipient
    
    @user.setter
    def user(self, value):
        """Backward compatibility setter - sets recipient"""
        self.recipient = value
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class Message(models.Model):
    """
    Real-time messaging between users
    """
    MESSAGE_TYPES = [
        ('DIRECT', 'Direct Message'),
        ('GROUP', 'Group Message'),
        ('SYSTEM', 'System Message'),
        ('ANNOUNCEMENT', 'Announcement'),
    ]
    
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='DIRECT')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipients = models.ManyToManyField(User, related_name='received_messages')
    
    subject = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    
    # Thread support
    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    thread_id = models.CharField(max_length=50, blank=True)  # For grouping related messages
    
    # Related objects (optional - for context)
    related_shift = models.ForeignKey('Shift', on_delete=models.SET_NULL, null=True, blank=True)
    related_leave_request = models.ForeignKey('LeaveRequest', on_delete=models.SET_NULL, null=True, blank=True)
    care_home = models.ForeignKey('CareHome', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Attachments/metadata
    attachment_url = models.CharField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict, blank=True)  # For mentions, tags, etc.
    
    # Status
    is_important = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', '-created_at']),
            models.Index(fields=['thread_id', '-created_at']),
            models.Index(fields=['message_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.username} - {self.subject or 'No subject'} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    def get_reply_count(self):
        """Get number of replies to this message"""
        return self.replies.count()


class SystemActivity(models.Model):
    """
    Extended activity feed tracking all system actions for transparency and audit
    """
    ACTIVITY_TYPES = [
        ('SHIFT_CREATED', 'Shift Created'),
        ('SHIFT_UPDATED', 'Shift Updated'),
        ('SHIFT_DELETED', 'Shift Deleted'),
        ('SHIFT_ASSIGNED', 'Shift Assigned'),
        ('LEAVE_REQUESTED', 'Leave Requested'),
        ('LEAVE_APPROVED', 'Leave Approved'),
        ('LEAVE_REJECTED', 'Leave Rejected'),
        ('SWAP_REQUESTED', 'Swap Requested'),
        ('SWAP_APPROVED', 'Swap Approved'),
        ('SWAP_REJECTED', 'Swap Rejected'),
        ('STAFF_ADDED', 'Staff Added'),
        ('STAFF_UPDATED', 'Staff Updated'),
        ('USER_LOGIN', 'User Login'),
        ('USER_LOGOUT', 'User Logout'),
        ('COMPLIANCE_CHECK', 'Compliance Check'),
        ('REPORT_GENERATED', 'Report Generated'),
        ('SYSTEM_CONFIG', 'System Configuration Changed'),
        ('MESSAGE_SENT', 'Message Sent'),
        ('NOTIFICATION_CREATED', 'Notification Created'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='system_activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.TextField()
    
    # Related objects
    care_home = models.ForeignKey('CareHome', on_delete=models.SET_NULL, null=True, blank=True)
    related_shift = models.ForeignKey('Shift', on_delete=models.SET_NULL, null=True, blank=True)
    related_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities_about')
    related_leave_request = models.ForeignKey('LeaveRequest', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Change tracking
    old_value = models.JSONField(default=dict, blank=True)  # State before change
    new_value = models.JSONField(default=dict, blank=True)  # State after change
    
    # Additional metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'System Activities'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['care_home', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else 'System'
        return f"{user_str} - {self.get_activity_type_display()} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class UserPresence(models.Model):
    """
    Track user online/offline status for real-time collaboration
    """
    STATUS_CHOICES = [
        ('ONLINE', 'Online'),
        ('AWAY', 'Away'),
        ('BUSY', 'Busy'),
        ('OFFLINE', 'Offline'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='presence')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OFFLINE')
    
    # Activity tracking
    last_seen = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    current_page = models.CharField(max_length=200, blank=True)  # Current page/view user is on
    
    # Custom status
    custom_status = models.CharField(max_length=100, blank=True)  # e.g., "In a meeting", "On shift"
    status_emoji = models.CharField(max_length=10, blank=True)  # e.g., "🏥", "☕"
    
    # Session tracking
    session_id = models.CharField(max_length=100, blank=True)
    device_info = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'last_seen']),
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()}"
    
    def is_online(self):
        """Check if user is currently online (active in last 5 minutes)"""
        from datetime import timedelta
        if self.status == 'OFFLINE':
            return False
        time_threshold = timezone.now() - timedelta(minutes=5)
        return self.last_seen >= time_threshold
    
    def set_status(self, status, custom_message=None):
        """Update user status"""
        self.status = status
        if custom_message:
            self.custom_status = custom_message
        self.last_activity = timezone.now()
        self.save()


# ==================== TASK 37: MULTI-LANGUAGE SUPPORT MODELS ====================

class UserLanguagePreference(models.Model):
    """
    Store user language preferences for multi-language support
    """
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('gd', 'Scottish Gaelic (Gàidhlig)'),
        ('cy', 'Welsh (Cymraeg)'),
        ('pl', 'Polish (Polski)'),
        ('ro', 'Romanian (Română)'),
        ('es', 'Spanish (Español)'),
        ('ar', 'Arabic (العربية)'),
        ('ur', 'Urdu (اردو)'),
        ('zh-hans', 'Simplified Chinese (简体中文)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='language_preference')
    language_code = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    
    # Formatting preferences
    date_format = models.CharField(max_length=20, default='%d/%m/%Y', help_text='Date format string')
    time_format = models.CharField(max_length=20, default='%H:%M', help_text='Time format string (24h by default)')
    use_12_hour = models.BooleanField(default=False, help_text='Use 12-hour clock format')
    
    # Regional settings
    timezone = models.CharField(max_length=50, default='Europe/London')
    currency_symbol = models.CharField(max_length=5, default='£')
    
    # Auto-detection preferences
    auto_detect_language = models.BooleanField(default=False, help_text='Auto-detect language from browser')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'language_code']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_language_code_display()}"
    
    def get_language_name(self):
        """Get the native name of the selected language"""
        return dict(self.LANGUAGE_CHOICES).get(self.language_code, 'English')


class Translation(models.Model):
    """
    Custom translations for care home-specific terms
    """
    key = models.CharField(max_length=200, db_index=True, help_text='Translation key')
    language_code = models.CharField(max_length=10, choices=UserLanguagePreference.LANGUAGE_CHOICES)
    translated_text = models.TextField(help_text='Translated text')
    
    # Context
    context = models.CharField(max_length=100, blank=True, help_text='Context for translation (e.g., "shift", "report")')
    care_home = models.ForeignKey('CareHome', on_delete=models.CASCADE, null=True, blank=True,
                                  help_text='Care home-specific translation (optional)')
    
    # Status
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_translations')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_translations')
    
    class Meta:
        unique_together = ['key', 'language_code', 'care_home']
        ordering = ['key', 'language_code']
        indexes = [
            models.Index(fields=['key', 'language_code']),
            models.Index(fields=['care_home', 'language_code']),
        ]
    
    def __str__(self):
        care_home_str = f" ({self.care_home.name})" if self.care_home else ""
        return f"{self.key} [{self.language_code}]{care_home_str}"


# Import report models (Task 40)
from .models_reports import (
    CustomReportTemplate,
    CustomSavedReport,
    ReportDataSource,
    ReportSchedule,
    ReportFavorite
)

# Import integration models (Task 41)
from .models_integrations import (
    APIClient,
    APIToken,
    APIRateLimit,
    APIRequestLog,
    WebhookEndpoint,
    WebhookDelivery,
    DataSyncJob
)

# Health Monitoring Models
from .models_health_monitoring import (
    SystemHealthMetric,
    PerformanceLog,
    ErrorLog,
    SystemUptime,
    HealthCheckEndpoint,
    HealthCheckResult,
    AlertRule
)

# User Preferences Models (Task 50)
from .models_preferences import (
    UserPreferences
)


# ===== Task 49: Search Analytics Model =====

class SearchAnalytics(models.Model):
    """
    Track search queries for analytics and improvement
    Used to identify popular searches, failed searches, and search patterns
    """
    query = models.CharField(max_length=255, help_text="Search query entered by user")
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="User who performed the search"
    )
    search_type = models.CharField(
        max_length=50,
        default='all',
        help_text="Type of search: all, staff, shifts, leave, homes"
    )
    result_count = models.IntegerField(
        default=0,
        help_text="Number of results returned"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'scheduling_search_analytics'
        verbose_name = 'Search Analytics'
        verbose_name_plural = 'Search Analytics'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['query']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.query} ({self.result_count} results) - {self.timestamp}"


# Import workflow models (Task 52)
from .models_workflow import (
    WorkflowTemplate,
    Workflow,
    WorkflowStep,
    WorkflowExecution,
    WorkflowStepExecution,
    WorkflowTrigger
)

# Import document models (Task 53)
from .models_documents import (
    DocumentCategory,
    Document,
    DocumentAccess,
    DocumentShare,
    DocumentComment
)

# Import video models (Task 54)
from .models_videos import (
    VideoCategory,
    Video,
    VideoProgress,
    VideoRating,
    VideoPlaylist,
    PlaylistVideo
)

# Task 55: Recent Activity Feed models
from .models_activity import (
    RecentActivity,
    ActivityFeedWidget
)

# Task 56: Compliance Dashboard Widgets models
from .models_compliance_widgets import (
    ComplianceMetric,
    ComplianceWidget
)

# Overtime preference and coverage models
from .models_overtime import (
    StaffOvertimePreference,
    OvertimeCoverageRequest,
    OvertimeCoverageResponse
)

# Week 6: Power User Features
from .models_week6 import (
    DashboardWidgetPreference,
    SavedSearchFilter,
    BulkOperationLog
)
