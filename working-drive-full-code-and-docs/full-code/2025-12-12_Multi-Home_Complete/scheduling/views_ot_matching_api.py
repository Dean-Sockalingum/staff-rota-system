"""
API views for automated OT offer system
Part of Task 1: Smart Staff Availability Matching System
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
import json
import logging

from scheduling.models import Shift
from scheduling.models_automated_workflow import OvertimeOfferBatch, OvertimeOffer
from scheduling.services_ot_offers import OvertimeOfferService, auto_send_ot_offers
from scheduling.utils_overtime_intelligence import OvertimeRanker

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
def find_ot_matches(request):
    """
    Find best staff matches for a shortage shift without sending offers.
    
    POST /api/ot-matching/find-matches/
    Body: {
        "shift_id": 123,
        "num_matches": 5
    }
    
    Returns:
    {
        "success": true,
        "shift": {...},
        "matches": [
            {
                "staff": {...},
                "total_score": 92.5,
                "breakdown": {...},
                "recommendation": "Excellent match"
            }
        ]
    }
    """
    try:
        data = json.loads(request.body)
        shift_id = data.get('shift_id')
        num_matches = data.get('num_matches', 5)
        
        shift = get_object_or_404(Shift, id=shift_id)
        
        # Run matching algorithm
        ranker = OvertimeRanker(
            shift_date=shift.date,
            shift_type=shift.shift_type.shift_type,
            care_home=shift.care_home,
            unit=shift.unit
        )
        
        candidates = ranker.get_top_candidates(limit=num_matches)
        
        # Format response
        matches = []
        for candidate in candidates:
            staff = candidate['staff']
            matches.append({
                'staff': {
                    'id': staff.id,
                    'full_name': staff.full_name,
                    'role': getattr(staff.staff_profile, 'role', 'Unknown'),
                    'phone': getattr(staff, 'phone', ''),
                },
                'total_score': candidate['total_score'],
                'breakdown': candidate['breakdown'],
                'recommendation': _generate_recommendation(
                    candidate['breakdown'],
                    candidate['total_score']
                )
            })
        
        return JsonResponse({
            'success': True,
            'shift': {
                'id': shift.id,
                'date': shift.date.isoformat(),
                'shift_type': shift.shift_type.shift_type,
                'unit': shift.unit.name,
                'care_home': shift.care_home.name,
            },
            'matches': matches,
            'count': len(matches)
        })
        
    except Exception as e:
        logger.error(f"Error finding OT matches: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def send_ot_offers(request):
    """
    Create batch and automatically send OT offers to top matches.
    
    POST /api/ot-matching/send-offers/
    Body: {
        "shift_id": 123,
        "num_offers": 3,
        "escalation_timeout": 30
    }
    
    Returns:
    {
        "success": true,
        "batch_id": 456,
        "offers_sent": 3,
        "escalation_at": "2025-12-28T14:30:00Z"
    }
    """
    try:
        data = json.loads(request.body)
        shift_id = data.get('shift_id')
        num_offers = data.get('num_offers', 3)
        escalation_timeout = data.get('escalation_timeout', 30)
        
        shift = get_object_or_404(Shift, id=shift_id)
        
        # Create and send offers
        batch = OvertimeOfferService.create_and_send_offers(
            shift=shift,
            num_offers=num_offers,
            escalation_timeout=escalation_timeout,
            created_by=request.user
        )
        
        if not batch:
            return JsonResponse({
                'success': False,
                'error': 'No available staff found for this shift'
            }, status=404)
        
        # Calculate escalation time
        escalation_at = batch.created_at + timezone.timedelta(
            minutes=escalation_timeout
        )
        
        # Get offer details
        offers = []
        for offer in batch.offers.all():
            offers.append({
                'id': offer.id,
                'staff_id': offer.staff.id,
                'staff_name': offer.staff.full_name,
                'rank': offer.rank_position,
                'score': float(offer.match_score),
                'contact_method': offer.contact_method,
                'sent_at': offer.sent_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'batch_id': batch.id,
            'offers_sent': batch.num_offers_sent,
            'escalation_timeout_minutes': escalation_timeout,
            'escalation_at': escalation_at.isoformat(),
            'offers': offers
        })
        
    except Exception as e:
        logger.error(f"Error sending OT offers: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["GET"])
def get_batch_status(request, batch_id):
    """
    Get current status of an OT offer batch.
    
    GET /api/ot-matching/batch/<batch_id>/status/
    
    Returns:
    {
        "success": true,
        "batch": {...},
        "offers": [...],
        "time_until_escalation": 1200  // seconds
    }
    """
    try:
        batch = get_object_or_404(OvertimeOfferBatch, id=batch_id)
        
        # Calculate time until escalation
        time_until_escalation = None
        if batch.status == 'PENDING':
            escalation_time = batch.created_at + timezone.timedelta(
                minutes=batch.escalation_timeout_minutes
            )
            delta = (escalation_time - timezone.now()).total_seconds()
            time_until_escalation = max(0, int(delta))
        
        # Get offers
        offers = []
        for offer in batch.offers.all():
            offers.append({
                'id': offer.id,
                'staff_name': offer.staff.full_name,
                'rank': offer.rank_position,
                'score': float(offer.match_score),
                'recommendation': offer.recommendation,
                'response': offer.response,
                'responded_at': offer.responded_at.isoformat() if offer.responded_at else None,
                'decline_reason': offer.decline_reason
            })
        
        return JsonResponse({
            'success': True,
            'batch': {
                'id': batch.id,
                'status': batch.status,
                'created_at': batch.created_at.isoformat(),
                'escalated_at': batch.escalated_at.isoformat() if batch.escalated_at else None,
                'accepted_by': batch.accepted_by.full_name if batch.accepted_by else None,
            },
            'offers': offers,
            'time_until_escalation_seconds': time_until_escalation
        })
        
    except Exception as e:
        logger.error(f"Error getting batch status: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt  # For webhook/external responses
@require_http_methods(["POST"])
def respond_to_offer(request, offer_id):
    """
    Process staff response to OT offer (from SMS/email link).
    
    POST /api/ot-matching/offer/<offer_id>/respond/
    Body: {
        "response": "ACCEPTED" | "DECLINED",
        "decline_reason": "optional"
    }
    
    Returns:
    {
        "success": true,
        "message": "Offer accepted - shift assigned"
    }
    """
    try:
        data = json.loads(request.body)
        response = data.get('response', '').upper()
        decline_reason = data.get('decline_reason', '')
        
        if response not in ['ACCEPTED', 'DECLINED']:
            return JsonResponse({
                'success': False,
                'error': 'Invalid response. Must be ACCEPTED or DECLINED'
            }, status=400)
        
        success = OvertimeOfferService.process_response(
            offer_id=offer_id,
            response=response,
            decline_reason=decline_reason
        )
        
        if not success:
            return JsonResponse({
                'success': False,
                'error': 'Failed to process response'
            }, status=400)
        
        message = "Offer accepted - shift assigned" if response == 'ACCEPTED' else "Offer declined"
        
        return JsonResponse({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        logger.error(f"Error processing offer response: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def _generate_recommendation(breakdown: dict, total_score: float) -> str:
    """Helper to generate recommendation text."""
    if total_score >= 90:
        return "Excellent match - highly recommended"
    elif total_score >= 80:
        strengths = []
        if breakdown.get('availability', 0) >= 90:
            strengths.append("high availability")
        if breakdown.get('acceptance_rate', 0) >= 90:
            strengths.append("reliable responder")
        if breakdown.get('fairness', 0) >= 90:
            strengths.append("low recent OT")
        return f"Strong match - {', '.join(strengths) if strengths else 'recommended'}"
    elif total_score >= 70:
        return "Good match - suitable for coverage"
    else:
        return "Acceptable match - backup option"
