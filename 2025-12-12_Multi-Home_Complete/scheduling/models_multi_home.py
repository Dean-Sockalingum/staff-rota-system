"""
Multi-Home Care Management Models
==================================

Models to support multiple care homes with centralized management.

Created: 10 December 2025
"""

from django.db import models
from django.utils import timezone
from decimal import Decimal


class CareHome(models.Model):
    """
    Represents an individual care home in the organization.
    
    Supports multi-home operations with centralized senior management oversight.
    """
    
    HOME_CHOICES = [
        ('ORCHARD_GROVE', 'Orchard Grove'),
        ('MEADOWBURN', 'Meadowburn'),
        ('HAWTHORN_HOUSE', 'Hawthorn House'),
        ('RIVERSIDE', 'Riverside'),
        ('VICTORIA_GARDENS', 'Victoria Gardens'),
    ]
    
    name = models.CharField(
        max_length=100,
        choices=HOME_CHOICES,
        unique=True
    )
    
    # Capacity
    bed_capacity = models.IntegerField(
        help_text="Total number of beds in this home"
    )
    current_occupancy = models.IntegerField(
        default=0,
        help_text="Current number of residents"
    )
    
    # Location
    location_address = models.TextField()
    postcode = models.CharField(max_length=10, blank=True)
    
    # Regulatory
    care_inspectorate_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Care Inspectorate registration number"
    )
    registration_number = models.CharField(
        max_length=50,
        blank=True
    )
    
    # Financial Budgets
    budget_agency_monthly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('9000.00'),
        help_text="Monthly agency spend budget"
    )
    budget_overtime_monthly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('5000.00'),
        help_text="Monthly overtime budget"
    )
    
    # Management
    home_manager = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_homes',
        limit_choices_to={'role__is_management': True}
    )
    
    # Contact
    main_phone = models.CharField(max_length=20, blank=True)
    main_email = models.EmailField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    opened_date = models.DateField(null=True, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Care Home'
        verbose_name_plural = 'Care Homes'
    
    def __str__(self):
        return self.get_name_display()
    
    @property
    def occupancy_rate(self):
        """Calculate occupancy percentage"""
        if self.bed_capacity == 0:
            return 0
        return (self.current_occupancy / self.bed_capacity) * 100
    
    @property
    def available_beds(self):
        """Number of available beds"""
        return self.bed_capacity - self.current_occupancy
    
    def get_current_staffing_level(self):
        """Get current total staff on shift across all units"""
        # TODO: Implement when Shift model integration is complete
        return 0
    
    def get_agency_spend_this_month(self):
        """Calculate agency spend for current month"""
        # TODO: Implement when AgencyRequest integration is complete
        return Decimal('0.00')
    
    def get_ot_spend_this_month(self):
        """Calculate OT spend for current month"""
        # TODO: Implement when OvertimeOffer integration is complete
        return Decimal('0.00')
    
    @property
    def agency_budget_status(self):
        """Check if over/under agency budget"""
        spend = self.get_agency_spend_this_month()
        variance = spend - self.budget_agency_monthly
        return {
            'budget': self.budget_agency_monthly,
            'actual': spend,
            'variance': variance,
            'variance_percent': (variance / self.budget_agency_monthly * 100) if self.budget_agency_monthly > 0 else 0,
            'status': 'OVER' if variance > 0 else 'UNDER'
        }
