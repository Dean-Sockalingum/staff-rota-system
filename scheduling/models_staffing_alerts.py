"""
Staffing Alert and Response System
Handles notifications and responses when staffing levels are below minimum
"""
from django.db import models
from django.utils import timezone
from .models import User, Shift, Unit, ShiftType
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
    
    def update_status(self):
        """Update alert status based on responses"""
        if self.is_expired and self.status == 'PENDING':
            self.status = 'EXPIRED'
        elif self.is_filled:
            self.status = 'FILLED'
        elif self.accepted_responses > 0:
            self.status = 'PARTIALLY_FILLED'
        self.save()


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
    
    def accept_shift(self, method='WEB_LOGIN'):
        """
        Accept the shift and create the actual shift in the system
        """
        if self.status == 'ACCEPTED':
            return False, "Already accepted this shift"
        
        if self.alert.is_filled:
            return False, "This alert has already been filled"
        
        if self.alert.is_expired:
            return False, "This alert has expired"
        
        # Create the shift
        try:
            shift = Shift.objects.create(
                user=self.user,
                unit=self.alert.unit,
                shift_type=self.alert.shift_type,
                date=self.alert.shift_date,
                status='SCHEDULED',
                notes=f'Created from staffing alert #{self.alert.id}'
            )
            
            # Update response
            self.status = 'ACCEPTED'
            self.response_method = method
            self.responded_at = timezone.now()
            self.shift_created = shift
            self.save()
            
            # Update alert statistics
            self.alert.accepted_responses += 1
            self.alert.total_responses += 1
            self.alert.update_status()
            
            return True, f"Shift accepted and scheduled for {self.alert.shift_date}"
            
        except Exception as e:
            return False, f"Error creating shift: {str(e)}"
    
    def decline_shift(self, reason='', method='WEB_LOGIN'):
        """
        Decline the shift
        """
        if self.status in ['ACCEPTED', 'DECLINED']:
            return False, f"Already {self.status.lower()}"
        
        self.status = 'DECLINED'
        self.response_method = method
        self.responded_at = timezone.now()
        self.decline_reason = reason
        self.save()
        
        # Update alert statistics
        self.alert.declined_responses += 1
        self.alert.total_responses += 1
        self.alert.update_status()
        
        return True, "Response recorded"
    
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
