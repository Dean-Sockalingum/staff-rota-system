"""
Automated OT & Agency Workflow Models
=====================================

This module contains models for the automated staffing cover workflow system.

Process Flow:
1. SicknessAbsence - Triggers the workflow
2. StaffingCoverRequest - Central orchestration
3. ReallocationRequest - Cross-home staff transfers (Priority 1)
4. OvertimeOfferBatch & OvertimeOffer - Smart OT system (Priority 2)
5. AgencyRequest - Agency escalation with auto-approval
6. LongTermCoverPlan - Strategic planning for extended absences
7. PostShiftAdministration - Consolidated post-shift admin

Created: 10 December 2025
"""

from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from decimal import Decimal
import json


class SicknessAbsence(models.Model):
    """
    Records a staff sickness absence and triggers the automated cover workflow.
    
    Automatically:
    - Updates the rota (removes staff from shifts)
    - Checks staffing levels
    - Creates cover requests for understaffed shifts
    - Detects long-term absences (≥3 shifts OR ≥5 days)
    - Initiates parallel long-term planning if needed
    """
    
    STATUS_CHOICES = [
        ('LOGGED', 'Sickness Logged'),
        ('ROTA_UPDATED', 'Rota Updated'),
        ('REQUEST_DRAFTED', 'Cover Request Drafted'),
        ('MANAGER_NOTIFIED', 'Manager Notified'),
        ('IN_PROGRESS', 'Cover Process In Progress'),
        ('RESOLVED', 'Cover Arranged'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    staff_member = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='sickness_absences'
    )
    
    # Timing
    reported_datetime = models.DateTimeField(auto_now_add=True)
    reported_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sickness_reports_made'
    )
    
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    expected_duration_days = models.IntegerField(
        help_text="Expected number of days absent"
    )
    
    # Shift tracking
    affected_shifts = models.ManyToManyField(
        'Shift',
        related_name='sickness_absences',
        blank=True
    )
    
    # Classification
    is_long_term = models.BooleanField(
        default=False,
        help_text="True if ≥3 shifts OR ≥5 days"
    )
    
    # Workflow status
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='LOGGED'
    )
    
    # Notes
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Medical certificate
    fit_note_required = models.BooleanField(default=False)
    fit_note_received = models.BooleanField(default=False)
    fit_note_date = models.DateField(null=True, blank=True)
    
    # Return to work
    actual_return_date = models.DateField(null=True, blank=True)
    return_to_work_interview_completed = models.BooleanField(default=False)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-reported_datetime']
        verbose_name = 'Sickness Absence'
        verbose_name_plural = 'Sickness Absences'
        indexes = [
            models.Index(fields=['staff_member', '-reported_datetime']),
            models.Index(fields=['status', 'is_long_term']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        staff_name = self.staff_member.full_name if hasattr(self.staff_member, 'full_name') else str(self.staff_member)
        return f"{staff_name} - {self.start_date} ({self.expected_duration_days} days)"
    
    def save(self, *args, **kwargs):
        """Auto-calculate long-term flag and trigger workflow"""
        
        # Calculate if long-term absence (only if already saved - has pk)
        if self.pk is not None:
            shift_count = self.affected_shifts.count()
            if shift_count >= 3 or self.expected_duration_days >= 5:
                self.is_long_term = True
        elif self.expected_duration_days >= 5:
            # For new records, check duration only
            self.is_long_term = True
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Trigger workflow for new absences
        if is_new and self.status == 'LOGGED':
            self.trigger_cover_workflow()
    
    def trigger_cover_workflow(self):
        """
        Step 1: Trigger the automated cover workflow
        
        Actions:
        1. Update rota (remove staff from affected shifts)
        2. Check staffing levels for each shift
        3. Create cover requests for understaffed shifts
        4. Notify manager
        5. If long-term, initiate parallel planning
        """
        from scheduling.models import Shift
        
        # Update status
        self.status = 'ROTA_UPDATED'
        self.save(update_fields=['status'])
        
        # Get affected shifts
        shifts = self.affected_shifts.all()
        
        cover_requests_created = []
        
        for shift in shifts:
            # Remove staff member from shift
            shift.assigned_staff.remove(self.staff_member)
            shift.save()
            
            # Check if shift is now understaffed
            if shift.is_understaffed():
                # Create cover request
                cover_request = self.create_cover_request(shift)
                cover_requests_created.append(cover_request)
        
        # Update status
        if cover_requests_created:
            self.status = 'REQUEST_DRAFTED'
        else:
            self.status = 'RESOLVED'  # No cover needed
        
        self.save(update_fields=['status'])
        
        # If long-term, initiate planning
        if self.is_long_term:
            self.initiate_long_term_planning()
        
        return cover_requests_created
    
    def create_cover_request(self, shift):
        """Create a staffing cover request for an understaffed shift"""
        
        cover_request = StaffingCoverRequest.objects.create(
            shift=shift,
            absence=self,
            requested_by_system=True,
            priority=self.calculate_priority(shift),
            status='PENDING_MANAGER_REVIEW',
            assigned_manager=shift.unit.manager if hasattr(shift.unit, 'manager') else None
        )
        
        # Notify manager
        cover_request.notify_manager()
        
        # Immediately start automated cover search (Steps 2 & 3)
        cover_request.initiate_automated_cover_search()
        
        # Update absence status
        self.status = 'MANAGER_NOTIFIED'
        self.save(update_fields=['status'])
        
        return cover_request
    
    def calculate_priority(self, shift):
        """Calculate priority level for cover request"""
        
        shortfall = shift.staff_shortfall()
        required = shift.required_staff_count()
        
        if shortfall >= required * 0.5:  # Missing 50%+ of required staff
            return 'CRITICAL'
        elif shortfall >= required * 0.25:  # Missing 25%+ of required staff
            return 'HIGH'
        else:
            return 'MEDIUM'
    
    def initiate_long_term_planning(self):
        """Step 4: Initiate parallel long-term cover planning"""
        
        # Create long-term cover plan
        plan = LongTermCoverPlan.objects.create(
            absence=self,
            start_date=self.start_date,
            expected_end_date=self.start_date + timedelta(days=self.expected_duration_days),
            total_shifts_affected=self.affected_shifts.count(),
            status='PLANNING_INITIATED'
        )
        
        # Generate strategy
        plan.generate_cover_strategy()
        plan.notify_manager_for_planning()
        
        return plan


class StaffingCoverRequest(models.Model):
    """
    Central orchestration for filling a staffing gap.
    
    Manages the concurrent processes:
    - Priority 1: Cross-home reallocation
    - Priority 2: OT offers
    - Escalation: Agency request
    """
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING_MANAGER_REVIEW', 'Pending Manager Review'),
        ('SEARCHING_INTERNAL', 'Searching Internal Cover'),
        ('WAITING_REALLOCATION', 'Waiting for Reallocation Response'),
        ('WAITING_OT', 'Waiting for OT Responses'),
        ('ESCALATED_TO_AGENCY', 'Escalated to Agency'),
        ('RESOLVED_REALLOCATION', 'Resolved - Reallocation'),
        ('RESOLVED_OVERTIME', 'Resolved - Overtime'),
        ('RESOLVED_AGENCY', 'Resolved - Agency'),
        ('CANCELLED', 'Cancelled'),
        ('FAILED', 'Failed to Fill'),
    ]
    
    shift = models.ForeignKey(
        'Shift',
        on_delete=models.CASCADE,
        related_name='cover_requests'
    )
    
    absence = models.ForeignKey(
        SicknessAbsence,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cover_requests'
    )
    
    # Request details
    created_datetime = models.DateTimeField(auto_now_add=True)
    requested_by_system = models.BooleanField(default=True)
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )
    
    # Workflow tracking
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='PENDING_MANAGER_REVIEW'
    )
    
    # Manager assignment
    assigned_manager = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cover_requests_assigned'
    )
    
    # Resolution tracking
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.CharField(
        max_length=50,
        blank=True,
        help_text="Method: REALLOCATION, OVERTIME, or AGENCY"
    )
    
    # Deadlines for concurrent processes
    reallocation_deadline = models.DateTimeField(null=True, blank=True)
    ot_response_deadline = models.DateTimeField(null=True, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_datetime']
        verbose_name = 'Staffing Cover Request'
        verbose_name_plural = 'Staffing Cover Requests'
        indexes = [
            models.Index(fields=['status', '-created_datetime']),
            models.Index(fields=['shift', 'status']),
            models.Index(fields=['priority', 'status']),
        ]
    
    def __str__(self):
        return f"Cover Request: {self.shift} - {self.status}"
    
    def notify_manager(self):
        """Send notification to assigned manager about cover request"""
        
        if not self.assigned_manager:
            return
        
        from scheduling.notifications import send_sms, send_email
        
        message = f"""
URGENT STAFFING GAP

Shift: {self.shift.date} {self.shift.shift_type}
Unit: {self.shift.unit.name}
Current Staffing: {self.shift.current_staff_count()}/{self.shift.required_staff_count()}
Shortfall: {self.shift.staff_shortfall()}

Automated cover process initiated.
Dashboard: {settings.SITE_URL}/staffing/cover-request/{self.id}/
"""
        
        # Send notifications
        send_email(
            to=self.assigned_manager.email,
            subject=f"URGENT: Staffing Gap - {self.shift.unit.name}",
            message=message
        )
        
        if hasattr(self.assigned_manager, 'phone_number') and self.assigned_manager.phone_number:
            send_sms(
                to=self.assigned_manager.phone_number,
                message=f"Staffing gap: {self.shift.date} {self.shift.shift_type}. Automated cover in progress. Check dashboard."
            )
    
    def initiate_automated_cover_search(self):
        """
        Steps 2 & 3: Start concurrent search processes
        
        Priority 1: Cross-home reallocation
        Priority 2: OT offers
        Both run simultaneously with 1-hour timeout
        """
        
        # Set deadlines (1 hour from now)
        deadline = timezone.now() + timedelta(hours=1)
        self.reallocation_deadline = deadline
        self.ot_response_deadline = deadline
        self.status = 'SEARCHING_INTERNAL'
        self.save()
        
        # Start Priority 1: Reallocation
        reallocation_found = self.search_cross_home_reallocation()
        
        # Start Priority 2: OT offers (concurrent)
        ot_offers_sent = self.send_smart_ot_offers()
        
        if not reallocation_found and not ot_offers_sent:
            # No internal options available - escalate immediately
            self.escalate_to_agency()
        else:
            # Monitor responses
            self.monitor_cover_responses()
    
    def search_cross_home_reallocation(self):
        """
        Step 2: Search for staff surplus across all homes
        
        Returns: True if reallocation options found, False otherwise
        """
        # Implementation will query other homes for surplus staff
        # For now, returning False to continue development
        # TODO: Implement cross-home reallocation logic
        return False
    
    def send_smart_ot_offers(self):
        """
        Step 3: Send OT offers to prioritized staff list
        
        Returns: True if offers sent, False if no eligible staff
        """
        
        eligible_staff = self.get_eligible_ot_staff()
        
        if not eligible_staff:
            return False
        
        # Create OT offer batch
        batch = OvertimeOfferBatch.objects.create(
            cover_request=self,
            response_deadline=self.ot_response_deadline,
            status='ACTIVE'
        )
        
        # Send offers to prioritized staff
        for priority_rank, staff in enumerate(eligible_staff, start=1):
            OvertimeOffer.objects.create(
                batch=batch,
                staff_member=staff,
                shift=self.shift,
                priority_rank=priority_rank,
                status='PENDING',
                sent_at=timezone.now()
            )
            
            # Send notification (will be implemented)
            # self.send_ot_offer_notification(staff, priority_rank)
        
        self.status = 'WAITING_OT'
        self.save()
        
        return True
    
    def get_eligible_ot_staff(self):
        """
        Get WTD-compliant staff prioritized by algorithm
        
        Priority weights:
        - Fair rotation: 50%
        - Qualification match: 30%
        - Proximity/experience: 20%
        """
        from scheduling.models import User
        
        # Get staff with matching role
        shift_role = self.shift.required_role if hasattr(self.shift, 'required_role') else None
        
        if not shift_role:
            return []
        
        # Base query: Active staff with matching qualification
        eligible_query = User.objects.filter(
            is_active=True,
            role=shift_role
        )
        
        eligible_staff = []
        
        for staff in eligible_query:
            # Check WTD compliance
            if not self.is_wtd_compliant(staff):
                continue
            
            # Check availability
            if self.is_staff_available(staff):
                # Calculate priority score
                score = self.calculate_ot_priority_score(staff)
                eligible_staff.append({
                    'staff': staff,
                    'score': score
                })
        
        # Sort by score (highest first) and return top 10
        eligible_staff.sort(key=lambda x: x['score'], reverse=True)
        return [item['staff'] for item in eligible_staff[:10]]
    
    def is_wtd_compliant(self, staff):
        """Check if staff is WTD compliant for this shift"""
        # Simplified check - will be enhanced
        # TODO: Implement full WTD compliance checking
        return True
    
    def is_staff_available(self, staff):
        """Check if staff is available for this shift"""
        # Check if not already scheduled at same time
        # TODO: Implement availability checking
        return True
    
    def calculate_ot_priority_score(self, staff):
        """
        Calculate priority score for OT offer
        
        Weights:
        - Fair rotation: 50% (staff with least recent OT)
        - Qualification match: 30% (exact role match)
        - Proximity/experience: 20% (same home/unit experience)
        """
        
        score = 100.0  # Start at 100
        
        # Fair rotation (50% weight) - TODO: Implement recent OT tracking
        # For now, random distribution
        fair_rotation_score = 50.0
        
        # Qualification match (30% weight)
        qualification_score = 30.0 if staff.role == self.shift.required_role else 15.0
        
        # Proximity/experience (20% weight) - TODO: Implement home/unit matching
        proximity_score = 20.0
        
        total_score = fair_rotation_score + qualification_score + proximity_score
        
        return total_score
    
    def monitor_cover_responses(self):
        """Monitor for responses from reallocation or OT offers"""
        # This will be handled by Celery tasks in production
        # For now, placeholder for development
        pass
    
    def escalate_to_agency(self):
        """Step 5: Escalate to agency with auto-approval timeout"""
        
        self.status = 'ESCALATED_TO_AGENCY'
        self.save()
        
        # Create agency request
        agency_request = AgencyRequest.objects.create(
            cover_request=self,
            shift=self.shift,
            status='PENDING_APPROVAL',
            estimated_cost=self.estimate_agency_cost()
        )
        
        # Request approval (15-minute timeout)
        agency_request.request_approval()
        
        return agency_request
    
    def estimate_agency_cost(self):
        """Estimate agency cost for this shift"""
        
        # Get agency rate from settings or default
        agency_rate = getattr(
            settings,
            'STAFFING_WORKFLOW',
            {}
        ).get('AGENCY_RATE_PER_HOUR', 30.00)
        
        duration = self.shift.duration_hours if hasattr(self.shift, 'duration_hours') else 8
        
        return Decimal(str(agency_rate)) * Decimal(str(duration))
    
    def mark_resolved(self, method, resolved_by_user=None):
        """Mark cover request as resolved"""
        
        self.resolved_at = timezone.now()
        self.resolved_by = method  # 'REALLOCATION', 'OVERTIME', or 'AGENCY'
        
        if method == 'REALLOCATION':
            self.status = 'RESOLVED_REALLOCATION'
        elif method == 'OVERTIME':
            self.status = 'RESOLVED_OVERTIME'
        elif method == 'AGENCY':
            self.status = 'RESOLVED_AGENCY'
        
        self.save()
        
        # Update related absence
        if self.absence:
            # Check if all cover requests for this absence are resolved
            unresolved = self.absence.cover_requests.exclude(
                status__startswith='RESOLVED'
            ).exists()
            
            if not unresolved:
                self.absence.status = 'RESOLVED'
                self.absence.save()


class ReallocationRequest(models.Model):
    """
    Request to reallocate staff from one home to another (Priority 1)
    """
    
    STATUS_CHOICES = [
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('DECLINED', 'Declined'),
        ('EXPIRED', 'Expired (No Response)'),
    ]
    
    cover_request = models.ForeignKey(
        StaffingCoverRequest,
        on_delete=models.CASCADE,
        related_name='reallocation_requests'
    )
    
    source_home = models.ForeignKey(
        'CareHome',
        on_delete=models.CASCADE,
        related_name='reallocations_from',
        null=True,
        blank=True
    )
    
    target_shift = models.ForeignKey(
        'Shift',
        on_delete=models.CASCADE,
        related_name='reallocation_targets'
    )
    
    # Available staff list (stored as JSON)
    available_staff_list = models.JSONField(
        default=list,
        help_text="List of staff IDs with surplus capacity"
    )
    
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='PENDING_APPROVAL'
    )
    
    response_deadline = models.DateTimeField()
    responded_at = models.DateTimeField(null=True, blank=True)
    
    selected_staff = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reallocations_selected'
    )
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Reallocation Request'
        verbose_name_plural = 'Reallocation Requests'
    
    def __str__(self):
        return f"Reallocation: {self.source_home} → {self.target_shift.unit.home if hasattr(self.target_shift.unit, 'home') else 'Target'}"


class OvertimeOfferBatch(models.Model):
    """
    Batch of OT offers sent for a specific cover request (Priority 2)
    """
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active - Awaiting Responses'),
        ('ACCEPTED', 'Accepted - Shift Filled'),
        ('EXPIRED', 'Expired - No Responses'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    cover_request = models.ForeignKey(
        StaffingCoverRequest,
        on_delete=models.CASCADE,
        related_name='ot_offer_batches'
    )
    
    response_deadline = models.DateTimeField()
    
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Overtime Offer Batch'
        verbose_name_plural = 'Overtime Offer Batches'
    
    def __str__(self):
        return f"OT Batch: {self.cover_request.shift} - {self.status}"
    
    def check_responses(self):
        """Check for accepted offers"""
        
        accepted_offers = self.offers.filter(status='ACCEPTED').first()
        
        if accepted_offers:
            self.mark_as_accepted(accepted_offers)
            return True
        
        # Check if deadline expired
        if timezone.now() > self.response_deadline:
            self.mark_as_expired()
            return False
        
        return None  # Still waiting
    
    def mark_as_accepted(self, accepted_offer):
        """Process OT acceptance"""
        
        self.status = 'ACCEPTED'
        self.save()
        
        # Assign staff to shift
        self.cover_request.shift.assigned_staff.add(accepted_offer.staff_member)
        
        # Mark cover request as resolved
        self.cover_request.mark_resolved('OVERTIME', accepted_offer.staff_member)
        
        # Cancel other offers
        self.offers.exclude(id=accepted_offer.id).update(status='CANCELLED')
    
    def mark_as_expired(self):
        """No responses received - escalate to agency"""
        
        self.status = 'EXPIRED'
        self.save()
        
        # Escalate to agency
        self.cover_request.escalate_to_agency()


class OvertimeOffer(models.Model):
    """
    Individual OT offer to a staff member
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Response'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
    ]
    
    batch = models.ForeignKey(
        OvertimeOfferBatch,
        on_delete=models.CASCADE,
        related_name='offers'
    )
    
    staff_member = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='ot_offers_received'
    )
    
    shift = models.ForeignKey(
        'Shift',
        on_delete=models.CASCADE,
        related_name='ot_offers'
    )
    
    priority_rank = models.IntegerField(
        help_text="1 = highest priority based on algorithm"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    sent_at = models.DateTimeField()
    responded_at = models.DateTimeField(null=True, blank=True)
    
    # Payment details
    ot_rate_multiplier = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('1.5')
    )
    
    estimated_payment = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['batch', 'priority_rank']
        verbose_name = 'Overtime Offer'
        verbose_name_plural = 'Overtime Offers'
    
    def __str__(self):
        return f"OT Offer: {self.staff_member.full_name} - Rank {self.priority_rank} - {self.status}"
    
    def accept(self):
        """Staff accepts OT offer"""
        
        self.status = 'ACCEPTED'
        self.responded_at = timezone.now()
        self.save()
        
        # Notify batch to process acceptance
        self.batch.check_responses()
    
    def decline(self):
        """Staff declines OT offer"""
        
        self.status = 'DECLINED'
        self.responded_at = timezone.now()
        self.save()


class AgencyRequest(models.Model):
    """
    Agency escalation request with simplified approval chain:
    JP (Senior Officer Mailbox) → Auto-Approve (15-minute timeout)
    """
    
    STATUS_CHOICES = [
        ('PENDING_APPROVAL', 'Pending Senior Officer Approval'),
        ('APPROVED', 'Approved'),
        ('AUTO_APPROVED', 'Auto-Approved (Timeout)'),
        ('DECLINED', 'Declined'),
        ('SENT_TO_AGENCY', 'Sent to Agency'),
        ('FILLED', 'Filled by Agency'),
    ]
    
    cover_request = models.ForeignKey(
        StaffingCoverRequest,
        on_delete=models.CASCADE,
        related_name='agency_requests'
    )
    
    shift = models.ForeignKey(
        'Shift',
        on_delete=models.CASCADE,
        related_name='agency_requests'
    )
    
    # Simplified approval workflow
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='PENDING_APPROVAL'
    )
    
    # Approval tracking
    approval_deadline = models.DateTimeField()
    approved_by = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Name of approver or 'SYSTEM_AUTO_APPROVAL'"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Agency details
    preferred_agency = models.ForeignKey(
        'AgencyCompany',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agency_requests'
    )
    
    estimated_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Estimated cost for this shift"
    )
    
    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    escalation_log = models.JSONField(
        default=list,
        help_text="Log of all escalation actions"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Agency Request'
        verbose_name_plural = 'Agency Requests'
        indexes = [
            models.Index(fields=['status', 'approval_deadline']),
        ]
    
    def __str__(self):
        return f"Agency Request: {self.shift} - {self.status}"
    
    def save(self, *args, **kwargs):
        """Set 15-minute approval deadline for new requests"""
        
        if not self.pk:  # New request
            self.approval_deadline = timezone.now() + timedelta(minutes=15)
        
        super().save(*args, **kwargs)
    
    def request_approval(self):
        """Send approval request to Senior Officer Mailbox"""
        
        from scheduling.notifications import send_email, send_sms
        
        message = f"""
╔════════════════════════════════════════════════════════╗
║  URGENT: AGENCY REQUEST APPROVAL REQUIRED              ║
╚════════════════════════════════════════════════════════╝

Shift Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date/Time: {self.shift.date} - {self.shift.shift_type}
Unit: {self.shift.unit.name}

Staffing Situation:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current: {self.shift.current_staff_count()}/{self.shift.required_staff_count()}
Shortfall: {self.shift.staff_shortfall()} staff

Internal Cover Attempts (Failed):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ Cross-home reallocation: No surplus available
✗ Overtime offers: No responses received (1 hour timeout)

Agency Solution:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Estimated Cost: £{self.estimated_cost}

⚠️  AUTO-APPROVAL IN 15 MINUTES IF NO RESPONSE

Dashboard: {settings.SITE_URL}/staffing/agency-request/{self.id}/approve/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Send to Senior Officer Mailbox
        senior_officer_email = getattr(
            settings,
            'STAFFING_WORKFLOW',
            {}
        ).get('SENIOR_OFFICER_EMAIL', 'senior.officer@organization.com')
        
        send_email(
            to=senior_officer_email,
            subject=f"URGENT: Agency Approval - {self.shift.unit.name}",
            message=message,
            priority='high'
        )
        
        # Log action
        self.escalation_log.append({
            'timestamp': str(timezone.now()),
            'action': 'APPROVAL_REQUESTED',
            'sent_to': senior_officer_email,
            'deadline': str(self.approval_deadline)
        })
        self.save()
        
        # Start monitoring for timeout (will be Celery task in production)
        # self.monitor_approval_timeout.delay(self.id)
    
    def auto_approve_timeout(self):
        """Auto-approve after 15-minute timeout"""
        
        self.status = 'AUTO_APPROVED'
        self.approved_by = 'SYSTEM_AUTO_APPROVAL'
        self.approved_at = timezone.now()
        
        # Log auto-approval
        self.escalation_log.append({
            'timestamp': str(timezone.now()),
            'action': 'AUTO_APPROVED',
            'reason': '15-minute timeout expired - no manual approval received'
        })
        
        self.save()
        
        # Send notification
        self.send_auto_approval_notification()
        
        # Send to agency
        self.send_to_agency()
    
    def send_auto_approval_notification(self):
        """Alert senior management of auto-approval"""
        
        from scheduling.notifications import send_email
        
        message = f"""
NOTICE: AGENCY REQUEST AUTO-APPROVED

An agency request was automatically approved due to the 15-minute
approval timeout expiring.

Shift: {self.shift.date} - {self.shift.shift_type}
Unit: {self.shift.unit.name}
Cost: £{self.estimated_cost}
Status: Request sent to agency

This is an automated safety mechanism to ensure shift coverage.
"""
        
        senior_officer_email = getattr(
            settings,
            'STAFFING_WORKFLOW',
            {}
        ).get('SENIOR_OFFICER_EMAIL', 'senior.officer@organization.com')
        
        send_email(
            to=senior_officer_email,
            subject=f"AUTO-APPROVED: Agency Request - {self.shift.unit.name}",
            message=message,
            priority='high'
        )
    
    def approve(self, approved_by_name):
        """Manual approval by Senior Officer"""
        
        self.status = 'APPROVED'
        self.approved_by = approved_by_name
        self.approved_at = timezone.now()
        
        self.escalation_log.append({
            'timestamp': str(timezone.now()),
            'action': 'MANUALLY_APPROVED',
            'approved_by': approved_by_name,
            'time_to_approve_minutes': (timezone.now() - self.created_at).seconds / 60
        })
        
        self.save()
        
        # Send to agency
        self.send_to_agency()
    
    def decline(self, declined_by_name, reason):
        """Manual decline by Senior Officer"""
        
        self.status = 'DECLINED'
        
        self.escalation_log.append({
            'timestamp': str(timezone.now()),
            'action': 'DECLINED',
            'declined_by': declined_by_name,
            'reason': reason
        })
        
        self.save()
    
    def send_to_agency(self):
        """Send approved request to agency"""
        
        self.status = 'SENT_TO_AGENCY'
        self.save()
        
        # TODO: Implement agency booking creation and API integration
        # For now, just log the action
        self.escalation_log.append({
            'timestamp': str(timezone.now()),
            'action': 'SENT_TO_AGENCY',
            'estimated_cost': str(self.estimated_cost)
        })
        self.save()
        
        # Mark cover request as resolved
        self.cover_request.mark_resolved('AGENCY')


class LongTermCoverPlan(models.Model):
    """
    Strategic planning for long-term absences (≥3 shifts OR ≥5 days)
    Runs in parallel with immediate cover requests
    """
    
    STATUS_CHOICES = [
        ('PLANNING_INITIATED', 'Planning Initiated'),
        ('STRATEGY_GENERATED', 'Strategy Generated'),
        ('MANAGER_REVIEW', 'Awaiting Manager Review'),
        ('APPROVED', 'Approved'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]
    
    absence = models.OneToOneField(
        SicknessAbsence,
        on_delete=models.CASCADE,
        related_name='long_term_plan'
    )
    
    start_date = models.DateField()
    expected_end_date = models.DateField()
    total_shifts_affected = models.IntegerField()
    
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='PLANNING_INITIATED'
    )
    
    # Cover strategy (AI-generated recommendation)
    strategy = models.JSONField(
        null=True,
        blank=True,
        help_text="Recommended mix of reallocation/OT/agency"
    )
    
    # Budget tracking
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Long-Term Cover Plan'
        verbose_name_plural = 'Long-Term Cover Plans'
    
    def __str__(self):
        return f"Long-Term Plan: {self.absence.staff_member.full_name} - {self.total_shifts_affected} shifts"
    
    def generate_cover_strategy(self):
        """
        AI-powered strategy generation
        
        Recommends optimal mix of:
        - Reallocation (zero cost)
        - Overtime (1.5x cost)
        - Agency (highest cost)
        """
        
        # Simplified strategy for initial implementation
        # TODO: Implement AI/ML-based optimization
        
        total_shifts = self.total_shifts_affected
        
        # Assume success rates based on historical data (placeholder)
        reallocation_rate = 0.3  # 30% success rate
        ot_rate = 0.4  # 40% success rate
        agency_rate = 1.0  # 100% success rate (always available)
        
        reallocation_shifts = int(total_shifts * reallocation_rate)
        ot_shifts = int(total_shifts * ot_rate)
        agency_shifts = total_shifts - reallocation_shifts - ot_shifts
        
        # Cost estimates
        avg_shift_hours = 8
        avg_hourly_rate = 12
        ot_multiplier = 1.5
        agency_hourly_rate = 30
        
        reallocation_cost = 0
        ot_cost = ot_shifts * avg_shift_hours * avg_hourly_rate * ot_multiplier
        agency_cost = agency_shifts * avg_shift_hours * agency_hourly_rate
        
        strategy = {
            'total_shifts': total_shifts,
            'duration_days': (self.expected_end_date - self.start_date).days,
            'recommended_approach': [
                {
                    'method': 'REALLOCATION',
                    'shifts': reallocation_shifts,
                    'estimated_cost': reallocation_cost,
                    'success_probability': reallocation_rate
                },
                {
                    'method': 'OVERTIME',
                    'shifts': ot_shifts,
                    'estimated_cost': ot_cost,
                    'success_probability': ot_rate
                },
                {
                    'method': 'AGENCY',
                    'shifts': agency_shifts,
                    'estimated_cost': agency_cost,
                    'success_probability': agency_rate
                }
            ],
            'total_estimated_cost': reallocation_cost + ot_cost + agency_cost,
            'generated_at': str(timezone.now())
        }
        
        self.strategy = strategy
        self.estimated_cost = Decimal(str(strategy['total_estimated_cost']))
        self.status = 'STRATEGY_GENERATED'
        self.save()
        
        return strategy
    
    def notify_manager_for_planning(self):
        """Alert manager about long-term absence and recommended strategy"""
        
        from scheduling.notifications import send_email
        
        if not self.absence.staff_member.unit or not hasattr(self.absence.staff_member.unit, 'manager'):
            return
        
        manager = self.absence.staff_member.unit.manager
        
        message = f"""
LONG-TERM ABSENCE DETECTED

Staff Member: {self.absence.staff_member.full_name}
Duration: {(self.expected_end_date - self.start_date).days} days
Shifts Affected: {self.total_shifts_affected}

Automated long-term planning has been initiated.
Estimated Total Cost: £{self.estimated_cost}

View Strategy: {settings.SITE_URL}/staffing/long-term-plan/{self.id}/
"""
        
        send_email(
            to=manager.email,
            subject=f"Long-Term Absence Planning: {self.absence.staff_member.full_name}",
            message=message
        )


class PostShiftAdministration(models.Model):
    """
    Consolidated post-shift administration form
    
    Single data entry point that auto-populates:
    - AMAR (attendance management)
    - Rota (actual staffing)
    - Payroll (OT/agency costs)
    """
    
    shift = models.OneToOneField(
        'Shift',
        on_delete=models.CASCADE,
        related_name='post_shift_admin'
    )
    
    completed_at = models.DateTimeField(auto_now_add=True)
    completed_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='post_shift_admins_completed'
    )
    
    # Sickness absence confirmation
    sickness_confirmed = models.BooleanField(default=False)
    sickness_notes = models.TextField(blank=True)
    
    # Off duty updates
    off_duty_changes = models.JSONField(
        default=list,
        help_text="List of any off-duty changes made"
    )
    
    # OT details
    overtime_worked = models.BooleanField(default=False)
    ot_staff = models.ManyToManyField(
        'User',
        related_name='ot_admin_records',
        blank=True
    )
    ot_hours_confirmed = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Agency details
    agency_used = models.BooleanField(default=False)
    agency_staff_details = models.JSONField(
        null=True,
        blank=True,
        help_text="Details of agency staff used"
    )
    agency_hours_confirmed = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True
    )
    agency_cost_actual = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Auto-population status
    amar_updated = models.BooleanField(default=False)
    rota_updated = models.BooleanField(default=False)
    payroll_updated = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-completed_at']
        verbose_name = 'Post-Shift Administration'
        verbose_name_plural = 'Post-Shift Administration Records'
    
    def __str__(self):
        return f"Post-Shift Admin: {self.shift} - {self.completed_at.date()}"
    
    def save(self, *args, **kwargs):
        """Auto-populate systems on save"""
        
        super().save(*args, **kwargs)
        
        # Auto-populate systems
        if not self.amar_updated:
            self.update_amar()
        
        if not self.rota_updated:
            self.update_rota()
        
        if not self.payroll_updated:
            self.update_payroll()
    
    def update_amar(self):
        """Update AMAR system"""
        # TODO: Implement AMAR integration
        self.amar_updated = True
        self.save(update_fields=['amar_updated'])
    
    def update_rota(self):
        """Update rota with confirmed details"""
        # TODO: Implement rota update logic
        self.rota_updated = True
        self.save(update_fields=['rota_updated'])
    
    def update_payroll(self):
        """Update payroll system"""
        # TODO: Implement payroll integration
        self.payroll_updated = True
        self.save(update_fields=['payroll_updated'])


# ============================================================================
# ENHANCED AGENCY COORDINATION - TASK 2
# ============================================================================

class AgencyBlastBatch(models.Model):
    """
    Multi-agency blast request with response tracking (Task 2)
    Sends simultaneous requests to multiple agencies
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Responses'),
        ('PARTIAL', 'Partial Responses Received'),
        ('BOOKED', 'Booked with Agency'),
        ('TIMEOUT', 'Deadline Expired'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    agency_request = models.ForeignKey(
        AgencyRequest,
        on_delete=models.CASCADE,
        related_name='blast_batches'
    )
    
    response_deadline = models.DateTimeField(
        help_text="Deadline for agency responses (default 30 min)"
    )
    
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    budget_limit = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Maximum acceptable rate for auto-booking"
    )
    
    # Booking details (when filled)
    booked_agency = models.ForeignKey(
        'AgencyCompany',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booked_blasts'
    )
    
    final_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Final agreed rate"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Agency Blast Batch'
        verbose_name_plural = 'Agency Blast Batches'
        indexes = [
            models.Index(fields=['status', 'response_deadline']),
        ]
    
    def __str__(self):
        return f"Agency Blast: {self.agency_request.shift} - {self.status}"
    
    def get_response_summary(self):
        """Get summary of all agency responses"""
        
        responses = self.agency_responses.all()
        
        return {
            'total': responses.count(),
            'pending': responses.filter(status='SENT').count(),
            'accepted': responses.filter(status='ACCEPTED').count(),
            'quoted': responses.filter(status='QUOTED').count(),
            'declined': responses.filter(status='DECLINED').count(),
            'booked': responses.filter(status='BOOKED').count(),
        }


class AgencyResponse(models.Model):
    """
    Individual agency response to blast request
    """
    
    STATUS_CHOICES = [
        ('SENT', 'Email Sent'),
        ('EMAIL_FAILED', 'Email Delivery Failed'),
        ('OPENED', 'Email Opened'),
        ('ACCEPTED', 'Accepted at Budget Rate'),
        ('QUOTED', 'Custom Quote Provided'),
        ('DECLINED', 'Declined'),
        ('BOOKED', 'Booking Confirmed'),
        ('CANCELLED', 'Cancelled - Filled by Another'),
    ]
    
    blast_batch = models.ForeignKey(
        AgencyBlastBatch,
        on_delete=models.CASCADE,
        related_name='agency_responses'
    )
    
    agency = models.ForeignKey(
        'AgencyCompany',
        on_delete=models.CASCADE,
        related_name='agency_responses'
    )
    
    rank = models.IntegerField(
        help_text="Priority rank (1=highest)"
    )
    
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='SENT'
    )
    
    quoted_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Rate quoted by agency (if provided)"
    )
    
    sent_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    response_time_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text="Minutes between sent and response"
    )
    
    class Meta:
        ordering = ['rank']
        verbose_name = 'Agency Response'
        verbose_name_plural = 'Agency Responses'
        unique_together = [['blast_batch', 'agency']]
    
    def __str__(self):
        return f"{self.agency.name} - Rank {self.rank} - {self.status}"
    
    def save(self, *args, **kwargs):
        """Calculate response time on save"""
        
        if self.responded_at and not self.response_time_minutes:
            delta = self.responded_at - self.sent_at
            self.response_time_minutes = int(delta.total_seconds() / 60)
        
        super().save(*args, **kwargs)
