from decimal import Decimal

from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import AnnualLeaveEntitlement, AnnualLeaveTransaction, StaffProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_staff_profile(sender, instance, created, **kwargs):
    """Ensure every staff member has a profile record."""

    if created:
        StaffProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender='scheduling.LeaveRequest')
def handle_leave_request_status_change(sender, instance, created, **kwargs):
    """
    Automatically create leave transactions when leave requests are approved or denied.
    
    - APPROVED: Deduct hours from entitlement
    - DENIED/CANCELLED: Refund hours if previously approved
    """
    from scheduling.models import LeaveRequest
    
    # Only process annual leave requests
    if instance.leave_type != 'ANNUAL':
        return
    
    # Get the staff profile
    try:
        profile = instance.user.staff_profile
    except StaffProfile.DoesNotExist:
        # No profile, can't process leave
        return
    
    # Get current leave year entitlement
    from datetime import date
    today = date.today()
    
    # Find entitlement that covers the requested dates
    entitlement = AnnualLeaveEntitlement.objects.filter(
        profile=profile,
        leave_year_start__lte=instance.start_date,
        leave_year_end__gte=instance.end_date
    ).first()
    
    if not entitlement:
        # No entitlement found for this period
        return
    
    # Calculate hours for this request
    # Assumes contracted hours per week / 5 = hours per day
    hours_per_day = entitlement.contracted_hours_per_week / Decimal('5.0') if entitlement.contracted_hours_per_week > 0 else Decimal('7.0')
    request_hours = Decimal(instance.days_requested) * hours_per_day
    
    # Check if transaction already exists for this request
    existing_transaction = AnnualLeaveTransaction.objects.filter(
        related_request=instance
    ).first()
    
    if instance.status == 'APPROVED':
        if not existing_transaction:
            # Create deduction transaction
            new_balance = entitlement.hours_remaining - request_hours
            
            AnnualLeaveTransaction.objects.create(
                entitlement=entitlement,
                transaction_type='DEDUCTION',
                hours=-request_hours,  # Negative for deduction
                balance_after=new_balance,
                related_request=instance,
                approved_by=instance.approved_by,
                approved_at=instance.approval_date or timezone.now(),
                description=f"Annual leave approved: {instance.start_date} to {instance.end_date} ({instance.days_requested} days)",
                created_by=instance.approved_by,
            )
            
            # Recalculate entitlement balance
            entitlement.recalculate_balance()
    
    elif instance.status in ['DENIED', 'CANCELLED']:
        if existing_transaction and existing_transaction.transaction_type == 'DEDUCTION':
            # Create refund transaction (reverse the deduction)
            new_balance = entitlement.hours_remaining + abs(existing_transaction.hours)
            
            AnnualLeaveTransaction.objects.create(
                entitlement=entitlement,
                transaction_type='REFUND',
                hours=abs(existing_transaction.hours),  # Positive for refund
                balance_after=new_balance,
                related_request=instance,
                description=f"Annual leave {instance.status.lower()}: {instance.start_date} to {instance.end_date} (refund)",
                created_by=instance.approved_by,
            )
            
            # Recalculate entitlement balance
            entitlement.recalculate_balance()

