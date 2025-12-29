"""
Celery periodic tasks for automated workflow monitoring

These tasks run at regular intervals to monitor deadlines and trigger
automated actions (OT offer expiry, agency auto-approval, etc.)

Author: Dean Sockalingum
Created: 2025-01-18
"""

from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
import logging

logger = logging.getLogger('scheduling.workflow')


# ==================== OT Offer Deadline Monitoring ====================

@shared_task
def monitor_ot_offer_deadlines():
    """
    Check for expired OT offers every minute
    
    Runs: Every 1 minute via Celery Beat
    Purpose: Expire pending OT offers past their 1-hour deadline
    """
    from scheduling.models import OvertimeOffer, OvertimeOfferBatch
    
    now = timezone.now()
    
    # Find all pending offers past their deadline
    expired_offers = OvertimeOffer.objects.filter(
        status='PENDING',
        batch__response_deadline__lt=now
    )
    
    expired_count = 0
    
    for offer in expired_offers:
        logger.info(f"⏰ Expiring OT offer #{offer.id} for {offer.staff_member.full_name}")
        offer.status = 'EXPIRED'
        offer.save()
        expired_count += 1
    
    if expired_count > 0:
        logger.info(f"✅ Expired {expired_count} OT offers")
        
        # Check if any batches are now fully expired and need escalation
        _check_batch_escalation()
    
    return {
        'task': 'monitor_ot_offer_deadlines',
        'expired_offers': expired_count,
        'timestamp': now.isoformat()
    }


def _check_batch_escalation():
    """Check if any OT batches need escalation after full expiry"""
    from scheduling.models import OvertimeOfferBatch, StaffingCoverRequest
    from scheduling.workflow_orchestrator import handle_timeout
    
    # Find batches where all offers are expired/declined
    batches = OvertimeOfferBatch.objects.filter(
        cover_request__status__in=['OT_OFFERED', 'REALLOCATION_OFFERED']
    )
    
    for batch in batches:
        pending_count = batch.offers.filter(status='PENDING').count()
        
        if pending_count == 0:  # All offers processed
            logger.info(f"🔄 All OT offers processed for batch #{batch.id}, checking escalation")
            
            # Check if any reallocation requests are still pending
            cover_request = batch.cover_request
            pending_reallocations = cover_request.reallocation_requests.filter(
                status='PENDING'
            ).count()
            
            if pending_reallocations == 0:
                # Both Priority 1 and 2 have failed, escalate
                logger.warning(f"⚠️  Priority 1 & 2 failed, escalating CoverRequest #{cover_request.id}")
                handle_timeout(cover_request)


# ==================== Agency Approval Monitoring ====================

@shared_task
def monitor_agency_approval_deadlines():
    """
    Check for expired agency approval requests every minute
    
    Runs: Every 1 minute via Celery Beat
    Purpose: Auto-approve agency requests after 15-minute deadline
    """
    from scheduling.models import AgencyRequest
    from scheduling.workflow_orchestrator import auto_approve_agency_timeout
    from rotasystems.settings import STAFFING_WORKFLOW
    
    # Only run if auto-approve is enabled
    if not STAFFING_WORKFLOW.get('AUTO_APPROVE_AGENCY_TIMEOUT', False):
        return {
            'task': 'monitor_agency_approval_deadlines',
            'auto_approve_disabled': True
        }
    
    now = timezone.now()
    
    # Find all pending agency requests past their deadline
    expired_requests = AgencyRequest.objects.filter(
        approval_status='PENDING_APPROVAL',
        approval_deadline__lt=now
    )
    
    auto_approved_count = 0
    
    for request in expired_requests:
        logger.info(f"🤖 Auto-approving agency request #{request.id} after timeout")
        auto_approve_agency_timeout(request)
        auto_approved_count += 1
    
    if auto_approved_count > 0:
        logger.warning(f"⚠️  Auto-approved {auto_approved_count} agency requests due to timeout")
    
    return {
        'task': 'monitor_agency_approval_deadlines',
        'auto_approved': auto_approved_count,
        'timestamp': now.isoformat()
    }


# ==================== Reallocation Request Monitoring ====================

@shared_task
def monitor_reallocation_deadlines():
    """
    Check for expired reallocation requests every minute
    
    Runs: Every 1 minute via Celery Beat
    Purpose: Expire pending reallocation requests past their deadline
    """
    from scheduling.models import ReallocationRequest
    
    now = timezone.now()
    
    # Find all pending reallocation requests past their deadline
    expired_requests = ReallocationRequest.objects.filter(
        status='PENDING',
        response_deadline__lt=now
    )
    
    expired_count = 0
    
    for request in expired_requests:
        logger.info(f"⏰ Expiring reallocation request #{request.id} for {request.staff_member.full_name}")
        request.status = 'EXPIRED'
        request.save()
        expired_count += 1
    
    if expired_count > 0:
        logger.info(f"✅ Expired {expired_count} reallocation requests")
    
    return {
        'task': 'monitor_reallocation_deadlines',
        'expired_requests': expired_count,
        'timestamp': now.isoformat()
    }


# ==================== Post-Shift Admin Reminders ====================

@shared_task
def send_post_shift_admin_reminders():
    """
    Send reminders for post-shift administration
    
    Runs: Daily at 09:00 via Celery Beat
    Purpose: Remind staff to complete post-shift admin forms
    """
    from scheduling.models import PostShiftAdministration, Shift
    from scheduling.notifications import notify_post_shift_admin_required
    from datetime import date, timedelta
    
    # Find shifts from yesterday that need post-shift admin
    yesterday = date.today() - timedelta(days=1)
    
    # Find shifts that were covered by workflow but don't have post-shift admin
    yesterday_shifts = Shift.objects.filter(
        date=yesterday,
        shift_classification__in=['OVERTIME', 'AGENCY']
    ).exclude(
        postshiftadministration__isnull=False  # Exclude if already created
    )
    
    reminder_count = 0
    
    for shift in yesterday_shifts:
        # Send reminder notification
        logger.info(f"📨 Sending post-shift admin reminder for shift on {shift.date}")
        notify_post_shift_admin_required(shift)
        reminder_count += 1
    
    # Also find incomplete post-shift admin records
    incomplete_admin = PostShiftAdministration.objects.filter(
        status__in=['PENDING_REVIEW', 'PARTIALLY_COMPLETED'],
        shift__date__lt=date.today()
    )
    
    for admin in incomplete_admin:
        logger.warning(f"⚠️  Incomplete post-shift admin #{admin.id} for shift on {admin.shift.date}")
    
    return {
        'task': 'send_post_shift_admin_reminders',
        'reminders_sent': reminder_count,
        'incomplete_records': incomplete_admin.count(),
        'timestamp': timezone.now().isoformat()
    }


# ==================== Workflow Health Monitoring ====================

@shared_task
def monitor_workflow_health():
    """
    Monitor overall workflow health and send alerts
    
    Runs: Every 5 minutes via Celery Beat
    Purpose: Detect stuck workflows and send alerts to admins
    """
    from scheduling.models import StaffingCoverRequest
    from scheduling.notifications import notify_workflow_alert
    from datetime import timedelta
    
    now = timezone.now()
    issues = []
    
    # Find cover requests stuck in pending state for > 2 hours
    stuck_requests = StaffingCoverRequest.objects.filter(
        status__in=['PENDING', 'REALLOCATION_OFFERED', 'OT_OFFERED'],
        created_at__lt=now - timedelta(hours=2)
    )
    
    if stuck_requests.exists():
        issues.append(f"{stuck_requests.count()} cover requests stuck for > 2 hours")
        for request in stuck_requests:
            logger.error(f"❌ STUCK WORKFLOW: CoverRequest #{request.id} created {request.created_at}")
    
    # Find agency requests pending approval for > 30 minutes
    from scheduling.models import AgencyRequest
    stuck_agency = AgencyRequest.objects.filter(
        approval_status='PENDING_APPROVAL',
        requested_at__lt=now - timedelta(minutes=30)
    )
    
    if stuck_agency.exists():
        issues.append(f"{stuck_agency.count()} agency requests pending > 30 min")
        for request in stuck_agency:
            logger.error(f"❌ STUCK AGENCY: AgencyRequest #{request.id} pending {request.requested_at}")
    
    # Find unresolved cover requests for shifts happening today
    from datetime import date
    today = date.today()
    
    today_unresolved = StaffingCoverRequest.objects.filter(
        absence__shift__date=today,
        status__in=['PENDING', 'REALLOCATION_OFFERED', 'OT_OFFERED', 'AGENCY_REQUESTED']
    )
    
    if today_unresolved.exists():
        issues.append(f"URGENT: {today_unresolved.count()} unresolved requests for TODAY")
        for request in today_unresolved:
            logger.critical(f"🚨 URGENT: CoverRequest #{request.id} for shift TODAY at {request.absence.shift.start_time}")
    
    # Send alert if issues detected
    if issues:
        logger.warning(f"⚠️  Workflow health check: {len(issues)} issues detected")
        # In production, this would send email/SMS to admins
        # notify_workflow_alert(issues)
    
    return {
        'task': 'monitor_workflow_health',
        'issues_detected': len(issues),
        'issues': issues,
        'timestamp': now.isoformat()
    }


# ==================== Long-Term Absence Review ====================

@shared_task
def review_long_term_absences():
    """
    Daily review of long-term absences and cover plans
    
    Runs: Daily at 08:00 via Celery Beat
    Purpose: Update long-term cover plans and send status reports
    """
    from scheduling.models import StaffingCoverRequest, LongTermCoverPlan
    from datetime import date, timedelta
    
    # Find active long-term cover plans
    active_plans = LongTermCoverPlan.objects.filter(
        cover_request__status='RESOLVED',
        cover_request__absence__end_date__gte=date.today()
    )
    
    for plan in active_plans:
        logger.info(f"📋 Reviewing long-term plan #{plan.id} for {plan.cover_request.absence.staff_member.full_name}")
        
        # Calculate actual costs to date
        resolved_requests = plan.cover_request.absence.staffingcoverrequest_set.filter(
            status='RESOLVED'
        )
        
        actual_cost = sum(r.total_cost for r in resolved_requests if r.total_cost)
        
        # Compare to estimated
        if plan.estimated_total_cost and actual_cost > plan.estimated_total_cost * Decimal('1.2'):
            logger.warning(f"⚠️  Long-term plan #{plan.id} 20% over budget: £{actual_cost} vs £{plan.estimated_total_cost}")
    
    return {
        'task': 'review_long_term_absences',
        'active_plans': active_plans.count(),
        'timestamp': timezone.now().isoformat()
    }


# ==================== WTD Compliance Monitoring ====================

@shared_task
def monitor_wdt_compliance():
    """
    Monitor staff approaching WTD limits
    
    Runs: Weekly on Sundays at 20:00 via Celery Beat
    Purpose: Flag staff approaching 48hr/week or rest period violations
    """
    from scheduling.wdt_compliance import calculate_weekly_hours, calculate_rolling_average_hours
    from scheduling.models import User
    from datetime import date, timedelta
    
    today = date.today()
    warnings = []
    
    # Check all active staff
    active_staff = User.objects.filter(
        is_active=True,
        userprofile__role__in=['RN', 'HCA', 'SC', 'AC', 'CA']
    )
    
    for staff in active_staff:
        # Check current week hours
        weekly_hours = calculate_weekly_hours(staff, today, weeks=1)
        
        if weekly_hours > Decimal('45'):  # Approaching 48hr limit
            warnings.append(f"{staff.full_name}: {weekly_hours}hrs this week (approaching limit)")
            logger.warning(f"⚠️  {staff.full_name} has {weekly_hours} hours this week")
        
        # Check 17-week rolling average
        rolling_avg = calculate_rolling_average_hours(staff, weeks=17)
        
        if rolling_avg > Decimal('46'):  # Approaching 48hr average
            warnings.append(f"{staff.full_name}: {rolling_avg}hrs rolling average (approaching limit)")
            logger.warning(f"⚠️  {staff.full_name} has {rolling_avg} hours rolling average")
    
    if warnings:
        logger.info(f"📊 WTD Compliance: {len(warnings)} staff approaching limits")
    
    return {
        'task': 'monitor_wdt_compliance',
        'warnings': len(warnings),
        'details': warnings,
        'timestamp': timezone.now().isoformat()
    }


# ==================== Workflow Statistics Generation ====================

@shared_task
def generate_weekly_workflow_report():
    """
    Generate comprehensive weekly workflow statistics
    
    Runs: Weekly on Mondays at 09:00 via Celery Beat
    Purpose: Create executive summary report for management
    """
    from scheduling.workflow_orchestrator import get_workflow_summary
    from datetime import date, timedelta
    
    # Last 7 days
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    
    summary = get_workflow_summary(start_date, end_date)
    
    logger.info("=" * 80)
    logger.info(f"📊 WEEKLY WORKFLOW REPORT: {start_date} to {end_date}")
    logger.info("=" * 80)
    logger.info(f"Absences: {summary['absences']['total']} total, {summary['absences']['long_term']} long-term")
    logger.info(f"Cover Requests: {summary['cover_requests']['total']} total, {summary['cover_requests']['resolved']} resolved ({summary['cover_requests']['resolution_rate']}%)")
    logger.info(f"Resolution: {summary['resolution_methods']['by_reallocation']} reallocation, {summary['resolution_methods']['by_overtime']} OT, {summary['resolution_methods']['by_agency']} agency")
    logger.info(f"Costs: £{summary['costs']['total']:.2f} total (Reallocation: £{summary['costs']['reallocation']:.2f}, OT: £{summary['costs']['overtime']:.2f}, Agency: £{summary['costs']['agency']:.2f})")
    logger.info(f"Performance: {summary['performance']['average_resolution_hours']:.1f}hrs avg resolution, {summary['performance']['reallocation_success_rate']:.1f}% zero-cost resolution")
    logger.info(f"Savings: £{summary['savings']['total_saved']:.2f} - {summary['savings']['description']}")
    logger.info("=" * 80)
    
    # In production, this would send email to management
    # send_management_report(summary)
    
    return {
        'task': 'generate_weekly_workflow_report',
        'summary': summary,
        'timestamp': timezone.now().isoformat()
    }


# ==================== TASK 21: Email Notification Tasks ====================

@shared_task
def send_shift_reminders():
    """
    Send reminder emails for shifts starting in 24 hours
    Scheduled to run every hour via Celery Beat
    """
    from scheduling.models import Shift
    from scheduling.email_notifications import send_shift_reminder_email
    
    logger.info("Starting shift reminder task")
    
    # Get tomorrow's date (24 hours from now)
    tomorrow = timezone.now() + timedelta(hours=24)
    tomorrow_date = tomorrow.date()
    
    # Get all shifts for tomorrow
    shifts = Shift.objects.filter(
        date=tomorrow_date
    ).select_related('staff', 'shift_type', 'unit', 'care_home')
    
    sent_count = 0
    failed_count = 0
    
    for shift in shifts:
        if shift.staff and shift.staff.email:
            try:
                if send_shift_reminder_email(shift):
                    sent_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Error sending reminder for shift {shift.id}: {str(e)}")
                failed_count += 1
    
    logger.info(f"Shift reminder task complete: {sent_count} sent, {failed_count} failed")
    return f"Sent {sent_count} reminders, {failed_count} failed"


@shared_task
def send_weekly_rotas():
    """
    Send weekly schedule emails to all staff
    Scheduled to run every Sunday at 18:00 via Celery Beat
    """
    from scheduling.models import Shift, User
    from scheduling.email_notifications import send_weekly_rota_email
    
    logger.info("Starting weekly rota email task")
    
    # Get next Monday
    today = timezone.now().date()
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    
    week_start = today + timedelta(days=days_until_monday)
    week_end = week_start + timedelta(days=6)
    
    # Get all active staff with email
    staff_members = User.objects.filter(
        is_active=True,
        email__isnull=False
    ).exclude(email='')
    
    sent_count = 0
    failed_count = 0
    
    for staff in staff_members:
        # Get their shifts for the week
        shifts = Shift.objects.filter(
            staff=staff,
            date__range=[week_start, week_end]
        ).select_related('shift_type', 'unit', 'care_home').order_by('date', 'start_time')
        
        try:
            if send_weekly_rota_email(staff, week_start, shifts):
                sent_count += 1
            else:
                failed_count += 1
        except Exception as e:
            logger.error(f"Error sending weekly rota to {staff.email}: {str(e)}")
            failed_count += 1
    
    logger.info(f"Weekly rota task complete: {sent_count} sent, {failed_count} failed")
    return f"Sent {sent_count} weekly rotas, {failed_count} failed"

