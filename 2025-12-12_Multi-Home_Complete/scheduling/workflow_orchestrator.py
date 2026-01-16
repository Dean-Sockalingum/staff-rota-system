"""
Workflow Orchestrator - Steps 1-3
Manages the automated staffing workflow from absence trigger through OT offers

Step 1: Absence triggers workflow
Step 2: Concurrent Priority 1 (Reallocation) & Priority 2 (OT offers)
Step 3: Monitor responses and resolve or escalate
"""

from datetime import timedelta
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


# ==================== STEP 1: Absence Workflow Trigger ====================

def trigger_absence_workflow(sickness_absence):
    """
    STEP 1: Trigger automated workflow when sickness absence is recorded
    
    This is called automatically when SicknessAbsence is saved
    
    Args:
        sickness_absence: SicknessAbsence instance
        
    Returns:
        dict: {
            'success': bool,
            'cover_request': StaffingCoverRequest instance or None,
            'workflow_started': bool,
            'errors': list of str
        }
    """
    from scheduling.models import StaffingCoverRequest, Shift
    
    logger.info(f"🚨 STEP 1: Absence workflow triggered for {sickness_absence.staff_member.full_name} on {sickness_absence.start_date}")
    
    errors = []
    
    try:
        with transaction.atomic():
            # Get the shift(s) affected
            affected_shifts = Shift.objects.filter(
                user=sickness_absence.staff_member,
                date__gte=sickness_absence.start_date,
                date__lte=sickness_absence.end_date,
                status__in=['SCHEDULED', 'CONFIRMED']
            )
            
            if not affected_shifts.exists():
                logger.warning(f"   ⚠️  No scheduled shifts found for {sickness_absence.staff_member.full_name} between {sickness_absence.start_date} and {sickness_absence.end_date}")
                errors.append("No scheduled shifts found for this absence period")
                return {
                    'success': False,
                    'cover_request': None,
                    'workflow_started': False,
                    'errors': errors
                }
            
            # Update shift statuses to UNCOVERED
            affected_count = affected_shifts.count()
            affected_shifts.update(status='UNCOVERED')
            logger.info(f"   ✓ Marked {affected_count} shift(s) as UNCOVERED")
            
            # Check if this is long-term absence (for logging only - not stored in model)
            is_long_term = _is_long_term_absence(sickness_absence, affected_shifts)
            
            # Create cover request for the first shift (primary)
            # Additional shifts will be handled separately or in batch
            # Re-query to get the first shift (since affected_shifts queryset may be stale after update)
            primary_shift = Shift.objects.filter(
                user=sickness_absence.staff_member,
                date__gte=sickness_absence.start_date,
                date__lte=sickness_absence.end_date,
                status='UNCOVERED'
            ).order_by('date').first()
            
            if not primary_shift:
                logger.error(f"   ❌ Could not find primary shift after marking as UNCOVERED")
                errors.append("Failed to identify primary shift for cover request")
                return {
                    'success': False,
                    'cover_request': None,
                    'workflow_started': False,
                    'errors': errors
                }
            
            cover_request = StaffingCoverRequest.objects.create(
                absence=sickness_absence,
                shift=primary_shift,
                status='PENDING',
                created_at=timezone.now()
            )
            
            logger.info(f"   ✓ Created StaffingCoverRequest #{cover_request.id}")
            
            # If long-term, flag for AI planning
            if is_long_term:
                logger.info(f"   ⚠️  Long-term absence detected ({affected_count} shifts)")
                # Long-term planning will be triggered in Step 4
            
            # Start concurrent Priority 1 & 2 processes
            concurrent_result = execute_concurrent_search(cover_request, primary_shift)
            
            return {
                'success': True,
                'cover_request': cover_request,
                'workflow_started': True,
                'affected_shifts': affected_count,
                'is_long_term': is_long_term,
                'concurrent_result': concurrent_result,
                'errors': []
            }
            
    except Exception as e:
        logger.error(f"❌ Error triggering absence workflow: {str(e)}", exc_info=True)
        errors.append(f"Workflow trigger failed: {str(e)}")
        return {
            'success': False,
            'cover_request': None,
            'workflow_started': False,
            'errors': errors
        }


def _is_long_term_absence(sickness_absence, affected_shifts):
    """
    Determine if this is a long-term absence requiring special planning
    
    Criteria: ≥3 shifts OR ≥5 days
    """
    shift_threshold = settings.STAFFING_WORKFLOW.get('LONG_TERM_SHIFT_THRESHOLD', 3)
    day_threshold = settings.STAFFING_WORKFLOW.get('LONG_TERM_DAY_THRESHOLD', 5)
    
    shift_count = affected_shifts.count()
    days = (sickness_absence.end_date - sickness_absence.start_date).days + 1
    
    return shift_count >= shift_threshold or days >= day_threshold


# ==================== STEP 2: Concurrent Priority 1 & 2 ====================

def execute_concurrent_search(cover_request, shift):
    """
    STEP 2: Execute Priority 1 (Reallocation) and Priority 2 (OT) concurrently
    
    Both processes run simultaneously to maximize speed
    First one to get acceptance resolves the request
    
    Args:
        cover_request: StaffingCoverRequest instance
        shift: Shift instance that needs coverage
        
    Returns:
        dict: Results of both processes
    """
    logger.info(f"🔄 STEP 2: Starting concurrent Priority 1 (Reallocation) & Priority 2 (OT)")
    
    concurrent_enabled = settings.STAFFING_WORKFLOW.get('CONCURRENT_REALLOCATION_AND_OT', True)
    
    if concurrent_enabled:
        # Run both processes
        reallocation_result = execute_reallocation_search(cover_request, shift)
        ot_result = execute_ot_offer_batch(cover_request, shift)
        
        # Update cover request status
        cover_request.status = 'REALLOCATION_OFFERED'
        cover_request.save()
        
        return {
            'reallocation': reallocation_result,
            'ot_offers': ot_result,
            'concurrent': True
        }
    else:
        # Sequential: Try reallocation first, then OT
        reallocation_result = execute_reallocation_search(cover_request, shift)
        
        # Only try OT if reallocation found no candidates
        if reallocation_result['requests_sent'] == 0:
            ot_result = execute_ot_offer_batch(cover_request, shift)
            cover_request.status = 'OT_OFFERED'
        else:
            ot_result = {'offers_sent': 0, 'message': 'Skipped - reallocation in progress'}
            cover_request.status = 'REALLOCATION_OFFERED'
        
        cover_request.save()
        
        return {
            'reallocation': reallocation_result,
            'ot_offers': ot_result,
            'concurrent': False
        }


def execute_reallocation_search(cover_request, shift):
    """
    Priority 1: Search for staff reallocation (zero cost)
    
    Args:
        cover_request: StaffingCoverRequest instance
        shift: Shift instance
        
    Returns:
        dict: Reallocation search results
    """
    from scheduling.reallocation_search import (
        find_eligible_staff_for_reallocation,
        create_reallocation_requests
    )
    
    logger.info(f"   🔍 Priority 1: Searching for reallocation candidates...")
    
    try:
        # Find eligible staff across care homes
        eligible_staff = find_eligible_staff_for_reallocation(shift)
        
        logger.info(f"   ✓ Found {len(eligible_staff)} eligible staff for reallocation")
        
        if len(eligible_staff) > 0:
            # Create reallocation requests (top 5)
            max_requests = 5
            created_requests = create_reallocation_requests(
                shift,
                cover_request,
                eligible_staff,
                max_requests
            )
            
            logger.info(f"   ✓ Sent {len(created_requests)} reallocation requests")
            
            return {
                'success': True,
                'eligible_count': len(eligible_staff),
                'requests_sent': len(created_requests),
                'requests': created_requests,
                'top_candidates': eligible_staff[:max_requests]
            }
        else:
            logger.info(f"   ⚠️  No eligible staff found for reallocation")
            return {
                'success': True,
                'eligible_count': 0,
                'requests_sent': 0,
                'requests': [],
                'message': 'No eligible staff for reallocation'
            }
            
    except Exception as e:
        logger.error(f"   ❌ Reallocation search failed: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'eligible_count': 0,
            'requests_sent': 0
        }


def execute_ot_offer_batch(cover_request, shift):
    """
    Priority 2: Send OT offers to eligible staff
    
    Args:
        cover_request: StaffingCoverRequest instance
        shift: Shift instance
        
    Returns:
        dict: OT offer batch results
    """
    from scheduling.models import OvertimeOfferBatch, OvertimeOffer, User
    from scheduling.ot_priority import get_top_ot_candidates
    from scheduling.notifications import notify_ot_offer
    
    logger.info(f"   💰 Priority 2: Preparing OT offers...")
    
    try:
        # Get all active staff (excluding those already scheduled)
        available_staff = shift.get_available_staff_for_date()
        
        # Get top candidates based on priority scoring + WTD compliance
        max_offers = settings.STAFFING_WORKFLOW.get('MAX_OT_OFFERS_PER_BATCH', 20)
        top_candidates = get_top_ot_candidates(shift, available_staff, max_offers)
        
        logger.info(f"   ✓ Identified {len(top_candidates)} WTD-compliant OT candidates")
        
        if len(top_candidates) == 0:
            logger.warning(f"   ⚠️  No WTD-compliant staff available for OT")
            return {
                'success': True,
                'offers_sent': 0,
                'message': 'No WTD-compliant staff available',
                'batch': None
            }
        
        # Create OT offer batch
        ot_response_hours = settings.STAFFING_WORKFLOW.get('OT_RESPONSE_WINDOW_HOURS', 1)
        deadline = timezone.now() + timedelta(hours=ot_response_hours)
        
        batch = OvertimeOfferBatch.objects.create(
            cover_request=cover_request,
            shift=shift,
            response_deadline=deadline,
            offers_sent=0,
            responses_received=0,
            accepted_count=0
        )
        
        # Create individual offers
        offers_created = []
        for candidate_data in top_candidates:
            staff_member = candidate_data['staff_member']
            
            offer = OvertimeOffer.objects.create(
                batch=batch,
                staff_member=staff_member,
                shift=shift,
                priority_score=candidate_data['total_score'],
                fair_rotation_score=candidate_data['fair_rotation'],
                qualification_score=candidate_data['qualification'],
                proximity_score=candidate_data['proximity'],
                hourly_rate=shift.calculate_ot_rate(),
                estimated_cost=Decimal(str(shift.duration_hours)) * shift.calculate_ot_rate(),
                response_deadline=deadline,
                status='PENDING'
            )
            
            # Send notification
            notify_ot_offer(staff_member, shift, batch.id, deadline)
            
            offers_created.append(offer)
        
        # Update batch count
        batch.offers_sent = len(offers_created)
        batch.save()
        
        # Update cover request
        cover_request.status = 'OT_OFFERED'
        cover_request.save()
        
        logger.info(f"   ✓ Sent {len(offers_created)} OT offers (Batch #{batch.id})")
        logger.info(f"   ⏰ Response deadline: {deadline.strftime('%H:%M on %d/%m/%Y')}")
        
        return {
            'success': True,
            'offers_sent': len(offers_created),
            'batch': batch,
            'offers': offers_created,
            'deadline': deadline,
            'top_candidates': top_candidates[:10]  # Top 10 for reporting
        }
        
    except Exception as e:
        logger.error(f"   ❌ OT offer batch failed: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'offers_sent': 0,
            'batch': None
        }


# ==================== STEP 3: Response Monitoring ====================

def process_reallocation_response(reallocation_request, response_status, responded_by=None):
    """
    STEP 3a: Process staff response to reallocation request
    
    Args:
        reallocation_request: ReallocationRequest instance
        response_status: 'ACCEPTED' or 'DECLINED'
        responded_by: User who responded (optional)
        
    Returns:
        dict: Processing result
    """
    from scheduling.models import Shift
    from scheduling.notifications import notify_cover_resolution
    
    logger.info(f"📥 Processing reallocation response: {response_status}")
    
    try:
        with transaction.atomic():
            # Update request status
            reallocation_request.status = response_status
            reallocation_request.responded_at = timezone.now()
            reallocation_request.save()
            
            if response_status == 'ACCEPTED':
                # Update the shift with new staff
                shift = reallocation_request.target_shift
                shift.user = reallocation_request.selected_staff
                shift.status = 'CONFIRMED'
                shift.shift_classification = 'REGULAR'  # Reallocation is regular rate
                shift.save()
                
                # Mark cover request as RESOLVED
                cover_request = reallocation_request.cover_request
                cover_request.status = 'RESOLVED_REALLOCATION'
                cover_request.resolved_by = 'REALLOCATION'
                cover_request.resolved_at = timezone.now()
                cover_request.save()
                
                # Cancel any pending OT offers for this shift
                _cancel_pending_ot_offers(cover_request)
                
                # Send confirmation notification
                notify_cover_resolution(
                    cover_request,
                    'Reallocation',
                    reallocation_request.selected_staff
                )
                
                logger.info(f"   ✅ Shift covered via reallocation (zero cost)")
                
                return {
                    'success': True,
                    'resolved': True,
                    'method': 'REALLOCATION',
                    'cost': Decimal('0')
                }
            
            else:  # DECLINED
                logger.info(f"   ❌ Reallocation declined by {reallocation_request.selected_staff.full_name}")
                
                # Check if any other reallocation requests are pending
                cover_request = reallocation_request.cover_request
                other_pending = cover_request.reallocation_requests.filter(
                    status='PENDING'
                ).exists()
                
                if not other_pending:
                    logger.info(f"   ⚠️  All reallocation requests declined or expired")
                
                return {
                    'success': True,
                    'resolved': False,
                    'other_pending': other_pending
                }
                
    except Exception as e:
        logger.error(f"❌ Error processing reallocation response: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


def process_ot_offer_response(ot_offer, response_status):
    """
    STEP 3b: Process staff response to OT offer
    
    Args:
        ot_offer: OvertimeOffer instance
        response_status: 'ACCEPTED' or 'DECLINED'
        
    Returns:
        dict: Processing result
    """
    from scheduling.models import Shift
    from scheduling.notifications import notify_ot_acceptance, notify_cover_resolution
    
    logger.info(f"📥 Processing OT offer response: {response_status}")
    
    try:
        with transaction.atomic():
            # Update offer status
            ot_offer.status = response_status
            ot_offer.responded_at = timezone.now()
            ot_offer.save()
            
            # Get batch
            batch = ot_offer.batch
            
            if response_status == 'ACCEPTED':
                batch.status = 'ACCEPTED'
                batch.save()
                
                # Update the shift
                shift = ot_offer.shift
                shift.user = ot_offer.staff_member
                shift.status = 'CONFIRMED'
                shift.shift_classification = 'OVERTIME'
                shift.save()
                
                # Mark cover request as RESOLVED
                cover_request = batch.cover_request
                cover_request.status = 'RESOLVED_OVERTIME'
                cover_request.resolved_by = 'OVERTIME'
                cover_request.resolved_at = timezone.now()
                cover_request.save()
                
                # Cancel other pending offers
                _cancel_pending_ot_offers(cover_request, exclude_offer=ot_offer)
                
                # Cancel any pending reallocation requests
                _cancel_pending_reallocations(cover_request)
                
                # Send notifications
                notify_ot_acceptance(ot_offer, ot_offer.staff_member, shift)
                notify_cover_resolution(cover_request, 'Overtime', ot_offer.staff_member)
                
                logger.info(f"   ✅ Shift covered via OT (Cost: £{ot_offer.estimated_payment or 0})")
                
                return {
                    'success': True,
                    'resolved': True,
                    'method': 'OVERTIME',
                    'cost': ot_offer.estimated_payment or Decimal('0')
                }
            
            else:  # DECLINED
                batch.save()
                
                logger.info(f"   ❌ OT offer declined by {ot_offer.staff_member.full_name}")
                
                # Check if any other offers are pending
                other_pending = batch.offers.filter(status='PENDING').exists()
                
                return {
                    'success': True,
                    'resolved': False,
                    'other_pending': other_pending
                }
                
    except Exception as e:
        logger.error(f"❌ Error processing OT response: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


# ==================== Helper Functions ====================

def _cancel_pending_ot_offers(cover_request, exclude_offer=None):
    """Cancel all pending OT offers for a cover request"""
    from scheduling.models import OvertimeOffer
    
    offers_to_cancel = OvertimeOffer.objects.filter(
        batch__cover_request=cover_request,
        status='PENDING'
    )
    
    if exclude_offer:
        offers_to_cancel = offers_to_cancel.exclude(id=exclude_offer.id)
    
    cancelled_count = offers_to_cancel.update(
        status='CANCELLED',
        responded_at=timezone.now()
    )
    
    if cancelled_count > 0:
        logger.info(f"   ✓ Cancelled {cancelled_count} pending OT offers")


def _cancel_pending_reallocations(cover_request):
    """Cancel all pending reallocation requests for a cover request"""
    cancelled_count = cover_request.reallocation_requests.filter(
        status='PENDING'
    ).update(
        status='CANCELLED',
        responded_at=timezone.now()
    )
    
    if cancelled_count > 0:
        logger.info(f"   ✓ Cancelled {cancelled_count} pending reallocation requests")


def get_workflow_status(cover_request):
    """
    Get current status of workflow for a cover request
    
    Returns:
        dict: Comprehensive status information
    """
    from scheduling.models import ReallocationRequest, OvertimeOfferBatch
    
    # Reallocation status
    reallocation_requests = cover_request.reallocation_requests.all()
    reallocation_status = {
        'total': reallocation_requests.count(),
        'pending': reallocation_requests.filter(status='PENDING').count(),
        'accepted': reallocation_requests.filter(status='ACCEPTED').count(),
        'declined': reallocation_requests.filter(status='DECLINED').count(),
        'expired': reallocation_requests.filter(status='EXPIRED').count(),
    }
    
    # OT offers status
    ot_batches = OvertimeOfferBatch.objects.filter(cover_request=cover_request)
    ot_status = {
        'batches': ot_batches.count(),
        'total_offers': sum(batch.offers_sent for batch in ot_batches),
        'responses': sum(batch.responses_received for batch in ot_batches),
        'accepted': sum(batch.accepted_count for batch in ot_batches),
    }
    
    return {
        'cover_request_id': cover_request.id,
        'status': cover_request.status,
        'is_resolved': cover_request.status == 'RESOLVED',
        'is_long_term': cover_request.is_long_term,
        'reallocation': reallocation_status,
        'ot_offers': ot_status,
        'resolution_method': cover_request.resolved_by,
        'assigned_staff': cover_request.assigned_staff.full_name if cover_request.assigned_staff else None,
        'total_cost': float(cover_request.total_cost) if cover_request.total_cost else 0,
        'created_at': cover_request.created_at,
        'resolved_at': cover_request.resolved_at,
    }


# ==================== STEP 4: Timeout Handling ====================

def handle_timeout(cover_request):
    """
    STEP 4: Handle timeout when no responses received within deadline
    
    Called by Celery task after 1-hour OT deadline expires
    
    Args:
        cover_request: StaffingCoverRequest instance
        
    Returns:
        dict: Timeout handling result
    """
    from scheduling.models import OvertimeOfferBatch
    
    logger.info(f"⏰ STEP 4: Handling timeout for CoverRequest #{cover_request.id}")
    
    try:
        # Mark expired reallocation requests
        expired_reallocations = cover_request.reallocation_requests.filter(
            status='PENDING'
        ).update(
            status='EXPIRED',
            responded_at=timezone.now()
        )
        
        # Mark expired OT offers
        expired_offers = 0
        for batch in OvertimeOfferBatch.objects.filter(cover_request=cover_request):
            # Check if batch deadline has expired
            if batch.response_deadline < timezone.now():
                expired_count = batch.offers.filter(
                    status='PENDING'
                ).update(
                    status='EXPIRED',
                    responded_at=timezone.now()
                )
                expired_offers += expired_count
                batch.status = 'EXPIRED'
                batch.save()
        
        logger.info(f"   ✓ Expired {expired_reallocations} reallocation requests")
        logger.info(f"   ✓ Expired {expired_offers} OT offers")
        
        # Check if this is long-term - trigger planning if needed
        # Determine if long-term based on affected shifts count
        from scheduling.models import SicknessAbsence
        try:
            absence = cover_request.absence
            affected_shifts_count = absence.affected_shifts.count()
            is_long_term = affected_shifts_count >= 3
        except Exception:
            is_long_term = False
        
        if is_long_term:
            logger.info(f"   ⚠️  Long-term absence - triggering AI planning")
            long_term_result = create_long_term_plan(cover_request)
        else:
            long_term_result = None
        
        # Escalate to agency (Priority 3)
        logger.info(f"   🚨 Escalating to Priority 3: Agency Request")
        agency_result = escalate_to_agency(cover_request)
        
        return {
            'success': True,
            'expired_reallocations': expired_reallocations,
            'expired_ot_offers': expired_offers,
            'long_term_plan': long_term_result,
            'agency_escalation': agency_result
        }
        
    except Exception as e:
        logger.error(f"❌ Error handling timeout: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


# ==================== STEP 5: Long-Term Planning ====================

def create_long_term_plan(cover_request):
    """
    STEP 5: Create AI-powered long-term cover plan for extended absences
    
    Triggered when absence is ≥3 shifts OR ≥5 days
    
    Args:
        cover_request: StaffingCoverRequest instance
        
    Returns:
        dict: Long-term plan details
    """
    from scheduling.models import LongTermCoverPlan, Shift
    from scheduling.notifications import notify_long_term_cover_plan
    
    logger.info(f"🤖 STEP 5: Creating long-term cover plan...")
    
    try:
        absence = cover_request.absence
        
        # Get all affected shifts
        affected_shifts = Shift.objects.filter(
            user=absence.staff_member,
            date__gte=absence.start_date,
            date__lte=absence.end_date,
            status__in=['SCHEDULED', 'CONFIRMED', 'UNCOVERED']
        ).order_by('date')
        
        shift_count = affected_shifts.count()
        days_span = (absence.end_date - absence.start_date).days + 1
        
        # Calculate estimated costs for different strategies
        costs = _estimate_long_term_costs(affected_shifts)
        
        # Generate AI recommendation
        # In production, this would use ML/AI to analyze historical patterns
        # For now, use rule-based logic
        recommended_strategy = _generate_cover_strategy(shift_count, days_span, costs)
        
        # Create long-term plan
        plan = LongTermCoverPlan.objects.create(
            absence=absence,
            start_date=absence.start_date,
            expected_end_date=absence.end_date,
            total_shifts_affected=shift_count,
            status='PLANNING_INITIATED',
            strategy={
                **recommended_strategy,
                'total_cost': float(recommended_strategy.get('total_cost', 0)),
                'confidence': float(recommended_strategy.get('confidence', 0))
            },
            estimated_cost=recommended_strategy.get('total_cost', Decimal('0'))
        )
        
        logger.info(f"   ✓ Created LongTermCoverPlan #{plan.id}")
        logger.info(f"   📊 Strategy: {recommended_strategy.get('summary', 'N/A')}")
        logger.info(f"   💷 Estimated cost: £{plan.estimated_cost}")
        
        # Notify stakeholders
        notify_long_term_cover_plan(absence, plan)
        
        return {
            'success': True,
            'plan': plan,
            'shifts_affected': shift_count,
            'days_span': days_span,
            'strategy': recommended_strategy
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating long-term plan: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


def _estimate_long_term_costs(shifts):
    """Estimate costs for different cover strategies"""
    shift_count = shifts.count()
    avg_duration = sum(s.duration_hours for s in shifts) / shift_count if shift_count > 0 else 12
    
    # Rough estimates
    reallocation_cost = Decimal('0')  # Zero cost
    ot_cost = Decimal(str(avg_duration)) * Decimal('15.00') * Decimal('1.5') * shift_count  # £15/hr base * 1.5 OT
    agency_cost = Decimal(str(avg_duration)) * Decimal('15.00') * Decimal('1.8') * shift_count  # £15/hr * 1.8 agency
    
    return {
        'reallocation': reallocation_cost,
        'overtime': ot_cost,
        'agency': agency_cost
    }


def _generate_cover_strategy(shift_count, days_span, costs):
    """Generate recommended cover strategy based on duration and costs"""
    
    if shift_count <= 3:
        # Short-term: Mix of reallocation and OT
        return {
            'summary': 'Mix of internal reallocation and overtime',
            'reallocation_count': 1,
            'ot_count': 2,
            'agency_count': 0,
            'temp_hire': False,
            'total_cost': costs['overtime'] * Decimal('0.67'),  # 2/3 OT
            'confidence': Decimal('0.85'),
            'notes': 'Short-term absence - prioritize internal solutions'
        }
    elif shift_count <= 7 or days_span <= 14:
        # Medium-term: More OT, some agency
        return {
            'summary': 'Primarily overtime with minimal agency backup',
            'reallocation_count': 1,
            'ot_count': 5,
            'agency_count': 1,
            'temp_hire': False,
            'total_cost': (costs['overtime'] * Decimal('0.71')) + (costs['agency'] * Decimal('0.14')),
            'confidence': Decimal('0.75'),
            'notes': 'Medium-term - blend OT and agency to manage costs and prevent staff fatigue'
        }
    else:
        # Long-term: Consider temp hire
        return {
            'summary': 'Temporary hire recommended for extended absence',
            'reallocation_count': 0,
            'ot_count': 2,
            'agency_count': 3,
            'temp_hire': True,
            'total_cost': costs['agency'] * Decimal('0.60'),  # Temp hire cheaper than continuous agency
            'confidence': Decimal('0.90'),
            'notes': f'Extended absence ({days_span} days, {shift_count} shifts) - temporary hire most cost-effective'
        }


# ==================== STEP 6: Agency Escalation ====================

def escalate_to_agency(cover_request):
    """
    STEP 6: Escalate to agency request (Priority 3)
    
    Requires Senior Officer approval within 15 minutes
    
    Args:
        cover_request: StaffingCoverRequest instance
        
    Returns:
        dict: Agency escalation result
    """
    from scheduling.models import AgencyRequest, Shift
    from scheduling.notifications import notify_agency_request_senior_officer
    
    logger.info(f"🏥 STEP 6: Escalating to Agency Request (Priority 3)")
    
    try:
        with transaction.atomic():
            # Get the shift that needs coverage
            shift = cover_request.shift
            
            # Calculate approval deadline (15 minutes)
            approval_timeout = settings.STAFFING_WORKFLOW.get('AGENCY_APPROVAL_TIMEOUT_MINUTES', 15)
            approval_deadline = timezone.now() + timedelta(minutes=approval_timeout)
            
            # Estimate agency cost
            agency_multiplier = Decimal(str(settings.STAFFING_WORKFLOW.get('AGENCY_HOURLY_RATE_MULTIPLIER', 1.8)))
            base_rate = Decimal('15.00')  # Default estimate
            estimated_cost = Decimal(str(shift.duration_hours)) * base_rate * agency_multiplier
            
            # Create agency request
            agency_request = AgencyRequest.objects.create(
                cover_request=cover_request,
                shift=shift,
                approval_deadline=approval_deadline,
                estimated_cost=estimated_cost,
                preferred_agency=None,  # Can be set based on unit preferences
                status='PENDING_APPROVAL'
            )
            
            # Update cover request status
            cover_request.status = 'AGENCY_REQUESTED'
            cover_request.save()
            
            logger.info(f"   ✓ Created AgencyRequest #{agency_request.id}")
            logger.info(f"   ⏰ Approval deadline: {approval_deadline.strftime('%H:%M on %d/%m/%Y')}")
            logger.info(f"   💷 Estimated cost: £{estimated_cost}")
            
            # Send urgent notification to Senior Officer
            notify_agency_request_senior_officer(agency_request, shift)
            
            logger.info(f"   📧 Sent urgent approval request to Senior Officer")
            
            return {
                'success': True,
                'agency_request': agency_request,
                'approval_deadline': approval_deadline,
                'estimated_cost': estimated_cost
            }
            
    except Exception as e:
        logger.error(f"❌ Error escalating to agency: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


def process_senior_officer_approval(agency_request, approved, approved_by=None, notes=''):
    """
    Process Senior Officer's approval/denial of agency request
    
    Args:
        agency_request: AgencyRequest instance
        approved: bool - True for approve, False for deny
        approved_by: User who approved (optional)
        notes: Approval notes
        
    Returns:
        dict: Approval processing result
    """
    from scheduling.models import Shift
    from scheduling.notifications import notify_cover_resolution
    
    logger.info(f"�� Processing Senior Officer approval: {'APPROVED' if approved else 'DENIED'}")
    
    try:
        with transaction.atomic():
            agency_request.responded_at = timezone.now()
            agency_request.approved_by = approved_by.full_name if approved_by else 'Senior Officer'
            agency_request.approval_notes = notes
            
            if approved:
                # Check if this is an auto-approval
                if 'AUTO-APPROVED' in notes:
                    agency_request.status = 'AUTO_APPROVED'
                else:
                    agency_request.status = 'APPROVED'
                agency_request.save()
                
                # Update shift to agency
                shift = agency_request.shift
                shift.shift_classification = 'AGENCY'
                shift.status = 'CONFIRMED'
                # Agency details will be filled when agency confirms
                shift.save()
                
                # Mark cover request as resolved
                cover_request = agency_request.cover_request
                cover_request.status = 'RESOLVED_AGENCY'
                cover_request.resolved_by = 'AGENCY'
                cover_request.resolved_at = timezone.now()
                cover_request.save()
                
                logger.info(f"   ✅ Agency approved - shift will be covered by agency")
                
                # Notify resolution
                notify_cover_resolution(cover_request, 'Agency', None)
                
                return {
                    'success': True,
                    'approved': True,
                    'method': 'AGENCY',
                    'cost': agency_request.estimated_cost
                }
            else:
                # Denied - need alternative solution
                agency_request.status = 'DENIED'
                agency_request.save()
                
                logger.warning(f"   ❌ Agency request DENIED by Senior Officer")
                logger.warning(f"   Reason: {notes}")
                
                # This is critical - shift still needs coverage
                # Could trigger manual review or escalate further
                
                return {
                    'success': True,
                    'approved': False,
                    'requires_manual_intervention': True,
                    'denial_reason': notes
                }
                
    except Exception as e:
        logger.error(f"❌ Error processing approval: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


def auto_approve_agency_timeout(agency_request):
    """
    Auto-approve agency request after 15-minute timeout
    
    Called by Celery task
    
    Args:
        agency_request: AgencyRequest instance
        
    Returns:
        dict: Auto-approval result
    """
    from scheduling.notifications import notify_agency_auto_approved
    
    logger.info(f"⚡ Auto-approving agency request #{agency_request.id} after timeout")
    
    if agency_request.status != 'PENDING_APPROVAL':
        logger.warning(f"   ⚠️  Request already processed: {agency_request.status}")
        return {
            'success': False,
            'message': f'Already processed: {agency_request.status}'
        }
    
    # Check if deadline passed
    if timezone.now() < agency_request.approval_deadline:
        logger.warning(f"   ⚠️  Deadline not reached yet")
        return {
            'success': False,
            'message': 'Deadline not reached'
        }
    
    # Auto-approve
    result = process_senior_officer_approval(
        agency_request,
        approved=True,
        approved_by=None,
        notes='AUTO-APPROVED: No response within 15-minute approval window'
    )
    
    # Send notification about auto-approval
    notify_agency_auto_approved(agency_request, agency_request.shift)
    
    logger.info(f"   ✅ Agency request auto-approved")
    
    return result



# ==================== STEP 7: Resolution & Confirmation ====================

def resolve_cover_request(cover_request, resolved_by, assigned_staff=None, actual_cost=None):
    """
    STEP 7: Mark cover request as resolved and finalize details
    
    Args:
        cover_request: StaffingCoverRequest instance
        resolved_by: 'REALLOCATION', 'OVERTIME', or 'AGENCY'
        assigned_staff: User instance who will cover the shift (None for agency)
        actual_cost: Decimal actual cost (optional, uses estimated if not provided)
    
    Returns:
        dict: Resolution result
    """
    from scheduling.notifications import notify_cover_resolution
    
    logger.info(f"✅ STEP 7: Resolving cover request via {resolved_by}")
    
    try:
        with transaction.atomic():
            # Update status based on resolution method
            if resolved_by == 'REALLOCATION':
                cover_request.status = 'RESOLVED_REALLOCATION'
            elif resolved_by == 'OVERTIME':
                cover_request.status = 'RESOLVED_OVERTIME'
            elif resolved_by == 'AGENCY':
                cover_request.status = 'RESOLVED_AGENCY'
            else:
                cover_request.status = 'RESOLVED'
            
            cover_request.resolved_by = resolved_by
            cover_request.resolved_at = timezone.now()
            cover_request.save()
            
            # Send resolution notification
            notify_cover_resolution(cover_request, resolved_by, assigned_staff)
            
            # Schedule post-shift admin reminder
            _schedule_post_shift_admin_reminder(cover_request)
            
            logger.info(f"   ✅ CoverRequest #{cover_request.id} resolved")
            if assigned_staff:
                staff_name = assigned_staff.full_name if hasattr(assigned_staff, 'full_name') else str(assigned_staff)
                logger.info(f"   👤 Assigned: {staff_name}")
            else:
                logger.info(f"   👤 Assigned: Agency Staff")
            
            return {
                'success': True,
                'cover_request_id': cover_request.id,
                'resolved_by': resolved_by,
                'assigned_staff': assigned_staff.full_name if assigned_staff and hasattr(assigned_staff, 'full_name') else 'Agency',
                'resolved_at': cover_request.resolved_at
            }
            
    except Exception as e:
        logger.error(f"❌ Error resolving cover request: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


def _schedule_post_shift_admin_reminder(cover_request):
    """Schedule reminder for post-shift administration"""
    from scheduling.notifications import notify_post_shift_admin_required
    
    # Calculate when to send reminder (day after shift)
    shift = cover_request.shift
    reminder_date = shift.date + timedelta(days=1)
    
    # In production, this would create a scheduled task
    # For now, just log it
    logger.info(f"   📅 Post-shift admin reminder scheduled for {reminder_date}")


# ==================== STEP 8: Post-Shift Administration ====================

def create_post_shift_admin(shift, cover_request=None, actual_staff_assigned=None, actual_hours_worked=None, actual_cost=None, admin_notes=''):
    """
    STEP 8: Create post-shift administration record
    
    Auto-populates AMAR, Rota, and Payroll data from workflow
    
    Args:
        shift: Shift instance that was completed
        cover_request: StaffingCoverRequest instance (if applicable)
        actual_staff_assigned: User who actually worked (may differ from scheduled)
        actual_hours_worked: Decimal actual hours (if different from scheduled)
        actual_cost: Decimal actual cost incurred
        admin_notes: Any administrative notes
        
    Returns:
        dict: Post-shift admin result
    """
    from scheduling.models import PostShiftAdministration
    from scheduling.notifications import notify_post_shift_admin_required
    
    logger.info(f"📝 STEP 8: Creating post-shift administration for {shift.date}")
    
    try:
        with transaction.atomic():
            # Auto-populate from shift and workflow data
            original_staff = None
            cover_method = None
            
            if cover_request:
                original_staff = cover_request.absence.staff_member
                cover_method = cover_request.resolved_by
            
            # Use actual or scheduled values
            staff_worked = actual_staff_assigned or shift.user
            hours_worked = actual_hours_worked or Decimal(str(shift.duration_hours))
            
            # Calculate cost if not provided
            if actual_cost is None:
                if shift.shift_classification == 'OVERTIME':
                    actual_cost = hours_worked * shift.calculate_ot_rate()
                elif shift.shift_classification == 'AGENCY' and shift.agency_hourly_rate:
                    actual_cost = hours_worked * shift.agency_hourly_rate
                elif shift.shift_classification == 'REGULAR':
                    actual_cost = Decimal('0')  # Regular shift, no additional cost
                else:
                    actual_cost = hours_worked * Decimal('12.50')  # Default estimate
            
            # Check for discrepancies
            discrepancy_flags = []
            
            # Get estimated cost from workflow records
            estimated_cost = Decimal('0')
            if cover_request:
                # Check for overtime offer through batches
                for batch in cover_request.ot_offer_batches.all():
                    ot_offer = batch.offers.filter(status='ACCEPTED').first()
                    if ot_offer:
                        estimated_cost = ot_offer.estimated_payment
                        break
                
                # Check for agency request if no OT found
                if estimated_cost == 0 and cover_request.agency_requests.exists():
                    agency_req = cover_request.agency_requests.first()
                    estimated_cost = agency_req.estimated_cost
            
            if estimated_cost > 0:
                cost_diff = abs(actual_cost - estimated_cost)
                if cost_diff > Decimal('10.00'):  # More than £10 difference
                    discrepancy_flags.append(f'Cost variance: £{cost_diff}')
            
            if actual_hours_worked and abs(actual_hours_worked - Decimal(str(shift.duration_hours))) > Decimal('0.5'):
                discrepancy_flags.append(f'Hours variance: {abs(actual_hours_worked - Decimal(str(shift.duration_hours)))} hours')
            
            has_discrepancies = len(discrepancy_flags) > 0
            
            # Determine if OT or agency was used
            used_overtime = cover_method == 'OVERTIME'
            used_agency = cover_method == 'AGENCY'
            
            # Create post-shift admin record with correct model fields
            post_admin = PostShiftAdministration.objects.create(
                shift=shift,
                completed_by=None,  # Will be filled by actual admin user
                sickness_confirmed=bool(cover_request),  # True if this was sickness cover
                sickness_notes=admin_notes if cover_request else '',
                overtime_worked=used_overtime,
                ot_hours_confirmed=hours_worked if used_overtime else None,
                agency_used=used_agency,
                agency_hours_confirmed=hours_worked if used_agency else None,
                agency_cost_actual=actual_cost if used_agency else None,
                amar_updated=False,  # Will be updated by save() method
                rota_updated=False,
                payroll_updated=False
            )
            
            # Add OT staff if applicable
            if used_overtime and actual_staff_assigned:
                post_admin.ot_staff.add(actual_staff_assigned)
            
            # Add agency staff details if applicable
            if used_agency and actual_staff_assigned:
                post_admin.agency_staff_details = {
                    'staff_name': actual_staff_assigned.full_name,
                    'cost': str(actual_cost),
                    'hours': str(hours_worked)
                }
                post_admin.save()
            
            logger.info(f"   ✅ Created PostShiftAdministration #{post_admin.id}")
            logger.info(f"   👤 Staff: {staff_worked.full_name}")
            logger.info(f"   ⏰ Hours: {hours_worked}")
            logger.info(f"   💷 Cost: £{actual_cost}")
            
            if has_discrepancies:
                logger.warning(f"   ⚠️  Discrepancies detected: {'; '.join(discrepancy_flags)}")
            
            return {
                'success': True,
                'post_admin_id': post_admin.id,
                'staff': staff_worked.full_name,
                'hours_worked': float(hours_worked),
                'cost': float(actual_cost),
                'has_discrepancies': has_discrepancies,
                'discrepancies': discrepancy_flags
            }
            
    except Exception as e:
        logger.error(f"❌ Error creating post-shift admin: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


def finalize_post_shift_admin(post_admin, amar_updated=True, rota_updated=True, payroll_updated=True, completed_by=None):
    """
    Finalize post-shift administration after all updates are complete
    
    Args:
        post_admin: PostShiftAdministration instance
        amar_updated: bool - AMAR system updated
        rota_updated: bool - Rota system updated
        payroll_updated: bool - Payroll system updated
        completed_by: User who completed the admin
        
    Returns:
        dict: Finalization result
    """
    logger.info(f"✔️  Finalizing post-shift admin #{post_admin.id}")
    
    try:
        post_admin.amar_updated = amar_updated
        post_admin.rota_updated = rota_updated
        post_admin.payroll_updated = payroll_updated
        post_admin.completed_by = completed_by
        post_admin.completed_at = timezone.now()
        
        # Update status
        if amar_updated and rota_updated and payroll_updated:
            post_admin.status = 'COMPLETED'
        else:
            post_admin.status = 'PARTIALLY_COMPLETED'
        
        post_admin.save()
        
        logger.info(f"   ✅ Post-shift admin finalized: {post_admin.status}")
        
        return {
            'success': True,
            'status': post_admin.status,
            'all_systems_updated': amar_updated and rota_updated and payroll_updated
        }
        
    except Exception as e:
        logger.error(f"❌ Error finalizing post-shift admin: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


# ==================== Workflow Summary & Reporting ====================

def get_workflow_summary(start_date=None, end_date=None, care_home=None):
    """
    Get comprehensive workflow summary for reporting
    
    Args:
        start_date: Start date for report (optional)
        end_date: End date for report (optional)
        care_home: CareHome instance to filter by (optional)
        
    Returns:
        dict: Comprehensive workflow statistics
    """
    from scheduling.models import StaffingCoverRequest, SicknessAbsence
    
    # Default to last 30 days if no dates provided
    if end_date is None:
        end_date = timezone.now().date()
    if start_date is None:
        start_date = end_date - timedelta(days=30)
    
    # Base queryset
    absences = SicknessAbsence.objects.filter(
        start_date__gte=start_date,
        end_date__lte=end_date
    )
    
    cover_requests = StaffingCoverRequest.objects.filter(
        created_at__gte=timezone.make_aware(timezone.datetime.combine(start_date, timezone.datetime.min.time())),
        created_at__lte=timezone.make_aware(timezone.datetime.combine(end_date, timezone.datetime.max.time()))
    )
    
    # Filter by care home if specified
    if care_home:
        absences = absences.filter(shift__unit__care_home=care_home)
        cover_requests = cover_requests.filter(absence__shift__unit__care_home=care_home)
    
    # Calculate statistics
    total_absences = absences.count()
    total_cover_requests = cover_requests.count()
    
    resolved_requests = cover_requests.filter(status='RESOLVED')
    resolution_stats = {
        'total_resolved': resolved_requests.count(),
        'by_reallocation': resolved_requests.filter(resolved_by ='REALLOCATION').count(),
        'by_overtime': resolved_requests.filter(resolved_by ='OVERTIME').count(),
        'by_agency': resolved_requests.filter(resolved_by ='AGENCY').count(),
    }
    
    # Cost analysis
    total_cost = sum(r.total_cost for r in resolved_requests if r.total_cost)
    reallocation_cost = Decimal('0')  # Always zero
    ot_cost = sum(r.total_cost for r in resolved_requests.filter(resolved_by ='OVERTIME') if r.total_cost)
    agency_cost = sum(r.total_cost for r in resolved_requests.filter(resolved_by ='AGENCY') if r.total_cost)
    
    # Average resolution time
    resolution_times = [(r.resolved_at - r.created_at).total_seconds() / 3600 
                       for r in resolved_requests if r.resolved_at]
    avg_resolution_hours = sum(resolution_times) / len(resolution_times) if resolution_times else 0
    
    # Success metrics
    resolution_rate = (resolved_requests.count() / total_cover_requests * 100) if total_cover_requests > 0 else 0
    reallocation_rate = (resolution_stats['by_reallocation'] / resolved_requests.count() * 100) if resolved_requests.count() > 0 else 0
    
    return {
        'period': {
            'start_date': start_date,
            'end_date': end_date,
            'days': (end_date - start_date).days + 1
        },
        'absences': {
            'total': total_absences,
            'long_term': SicknessAbsence.objects.filter(
                long_term_plan__isnull=False,
                start_date__gte=start_date,
                start_date__lte=end_date
            ).count()
        },
        'cover_requests': {
            'total': total_cover_requests,
            'resolved': resolved_requests.count(),
            'pending': cover_requests.filter(status__in=['PENDING', 'REALLOCATION_OFFERED', 'OT_OFFERED', 'AGENCY_REQUESTED']).count(),
            'resolution_rate': round(resolution_rate, 1)
        },
        'resolution_methods': resolution_stats,
        'costs': {
            'total': float(total_cost),
            'reallocation': float(reallocation_cost),
            'overtime': float(ot_cost),
            'agency': float(agency_cost),
            'average_per_request': float(total_cost / resolved_requests.count()) if resolved_requests.count() > 0 else 0
        },
        'performance': {
            'average_resolution_hours': round(avg_resolution_hours, 2),
            'reallocation_success_rate': round(reallocation_rate, 1),
            'zero_cost_resolution_rate': round(reallocation_rate, 1)  # Same as reallocation
        },
        'savings': {
            'total_saved': float(agency_cost * Decimal('0.3')),  # Estimated 30% savings vs all-agency
            'description': f'Estimated savings from {resolution_stats["by_reallocation"]} reallocations and optimized OT'
        }
    }


def get_staff_workflow_participation(staff_member, days=30):
    """
    Get staff member's participation in workflow (OT offers, reallocations)
    
    Args:
        staff_member: User instance
        days: Number of days to look back
        
    Returns:
        dict: Staff participation statistics
    """
    from scheduling.models import OvertimeOffer, ReallocationRequest
    
    since_date = timezone.now() - timedelta(days=days)
    
    # OT participation
    ot_offers_received = OvertimeOffer.objects.filter(
        staff_member=staff_member,
        batch__created_at__gte=since_date
    )
    
    ot_stats = {
        'total_offers': ot_offers_received.count(),
        'accepted': ot_offers_received.filter(status='ACCEPTED').count(),
        'declined': ot_offers_received.filter(status='DECLINED').count(),
        'expired': ot_offers_received.filter(status='EXPIRED').count(),
        'response_rate': 0
    }
    
    if ot_stats['total_offers'] > 0:
        ot_stats['response_rate'] = round(
            (ot_stats['accepted'] + ot_stats['declined']) / ot_stats['total_offers'] * 100, 1
        )
    
    # Reallocation participation
    reallocation_requests = ReallocationRequest.objects.filter(
        staff_member=staff_member,
        created_at__gte=since_date
    )
    
    reallocation_stats = {
        'total_requests': reallocation_requests.count(),
        'accepted': reallocation_requests.filter(status='ACCEPTED').count(),
        'declined': reallocation_requests.filter(status='DECLINED').count(),
        'expired': reallocation_requests.filter(status='EXPIRED').count()
    }
    
    return {
        'staff_member': staff_member.full_name,
        'period_days': days,
        'overtime': ot_stats,
        'reallocation': reallocation_stats,
        'total_participations': ot_stats['accepted'] + reallocation_stats['accepted']
    }

