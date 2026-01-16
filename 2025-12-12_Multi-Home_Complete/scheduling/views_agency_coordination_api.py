"""
Agency Coordination API Views - Task 2
REST endpoints for multi-agency blast system
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import json
import logging

from scheduling.services_agency_coordination import AgencyCoordinationService
from scheduling.models_automated_workflow import (
    AgencyRequest, AgencyBlastBatch, AgencyResponse
)
from scheduling.models import AgencyCompany


logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
@csrf_exempt
def send_agency_blast(request):
    """
    Create and send multi-agency blast request
    
    POST /api/agency-coordination/send-blast/
    
    Body:
    {
        "agency_request_id": 123,
        "max_agencies": 3,
        "timeout_minutes": 30
    }
    
    Returns:
    {
        "blast_batch_id": "batch_xyz123",
        "agencies_contacted": 3,
        "response_deadline": "2025-12-28T15:00:00Z",
        "budget_limit": "200.00",
        "agencies": [
            {"name": "ABC Staffing", "rank": 1},
            {"name": "XYZ Healthcare", "rank": 2},
            {"name": "123 Agency", "rank": 3}
        ]
    }
    """
    
    try:
        data = json.loads(request.body)
        
        agency_request_id = data.get('agency_request_id')
        max_agencies = data.get('max_agencies', 3)
        timeout_minutes = data.get('timeout_minutes', 30)
        
        if not agency_request_id:
            return JsonResponse({
                'error': 'agency_request_id required'
            }, status=400)
        
        # Create blast batch
        blast_batch = AgencyCoordinationService.create_agency_blast(
            agency_request_id=agency_request_id,
            max_agencies=max_agencies,
            timeout_minutes=timeout_minutes
        )
        
        # Build response
        agencies_list = []
        for response in blast_batch.agency_responses.all():
            agencies_list.append({
                'id': response.agency.id,
                'name': response.agency.name,
                'rank': response.rank,
                'contact_email': response.agency.contact_email,
                'status': response.status
            })
        
        return JsonResponse({
            'blast_batch_id': blast_batch.id,
            'agencies_contacted': len(agencies_list),
            'response_deadline': blast_batch.response_deadline.isoformat(),
            'budget_limit': str(blast_batch.budget_limit),
            'agencies': agencies_list,
            'status': blast_batch.status
        })
    
    except ValueError as e:
        logger.error(f"Validation error in send_agency_blast: {str(e)}")
        return JsonResponse({
            'error': str(e)
        }, status=400)
    
    except Exception as e:
        logger.exception(f"Error in send_agency_blast: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error',
            'details': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_blast_status(request, blast_batch_id):
    """
    Get real-time status of agency blast batch
    
    GET /api/agency-coordination/blast/<id>/status/
    
    Returns:
    {
        "blast_batch_id": 123,
        "status": "PENDING",
        "shift": {...},
        "response_deadline": "2025-12-28T15:00:00Z",
        "time_remaining": "18 minutes",
        "budget_limit": "200.00",
        "responses": [
            {
                "agency": "ABC Staffing",
                "rank": 1,
                "status": "ACCEPTED",
                "quoted_rate": "200.00",
                "responded_at": "2025-12-28T14:05:00Z",
                "response_time": "5 minutes"
            },
            {
                "agency": "XYZ Healthcare",
                "rank": 2,
                "status": "QUOTED",
                "quoted_rate": "225.00",
                "responded_at": "2025-12-28T14:10:00Z",
                "response_time": "10 minutes"
            },
            {
                "agency": "123 Agency",
                "rank": 3,
                "status": "SENT",
                "responded_at": null
            }
        ],
        "summary": {
            "total": 3,
            "pending": 1,
            "accepted": 1,
            "quoted": 1,
            "declined": 0,
            "booked": 0
        }
    }
    """
    
    try:
        blast_batch = AgencyBlastBatch.objects.select_related(
            'agency_request__shift__unit__home',
            'booked_agency'
        ).get(id=blast_batch_id)
        
    except AgencyBlastBatch.DoesNotExist:
        return JsonResponse({
            'error': 'Blast batch not found'
        }, status=404)
    
    # Calculate time remaining
    now = timezone.now()
    if blast_batch.response_deadline > now:
        delta = blast_batch.response_deadline - now
        minutes_remaining = int(delta.total_seconds() / 60)
        time_remaining = f"{minutes_remaining} minutes"
    else:
        time_remaining = "EXPIRED"
    
    # Build shift details
    shift = blast_batch.agency_request.shift
    shift_info = {
        'id': shift.id,
        'date': shift.date.isoformat(),
        'start_time': shift.start_time.strftime('%H:%M'),
        'end_time': shift.end_time.strftime('%H:%M'),
        'role': shift.role,
        'home': shift.unit.home.name if hasattr(shift.unit, 'home') else 'N/A'
    }
    
    # Build responses list
    responses_list = []
    for response in blast_batch.agency_responses.select_related('agency').all():
        response_info = {
            'agency_response_id': response.id,
            'agency': response.agency.name,
            'rank': response.rank,
            'status': response.status,
            'quoted_rate': str(response.quoted_rate) if response.quoted_rate else None,
            'sent_at': response.sent_at.isoformat(),
            'responded_at': response.responded_at.isoformat() if response.responded_at else None,
        }
        
        if response.response_time_minutes:
            response_info['response_time'] = f"{response.response_time_minutes} minutes"
        
        responses_list.append(response_info)
    
    # Get summary
    summary = blast_batch.get_response_summary()
    
    return JsonResponse({
        'blast_batch_id': blast_batch.id,
        'status': blast_batch.status,
        'shift': shift_info,
        'response_deadline': blast_batch.response_deadline.isoformat(),
        'time_remaining': time_remaining,
        'budget_limit': str(blast_batch.budget_limit),
        'booked_agency': blast_batch.booked_agency.name if blast_batch.booked_agency else None,
        'final_rate': str(blast_batch.final_rate) if blast_batch.final_rate else None,
        'responses': responses_list,
        'summary': summary
    })


@require_http_methods(["POST"])
@csrf_exempt
def agency_response_webhook(request, response_id, action):
    """
    Agency response webhook - accept or provide quote
    
    POST /api/agency-coordination/response/<id>/accept/
    POST /api/agency-coordination/response/<id>/quote/
    
    Body (for quote):
    {
        "quoted_rate": 225.50
    }
    
    Returns:
    {
        "status": "BOOKED",
        "message": "Booking confirmed with ABC Staffing",
        "shift_id": 123,
        "rate": 200.00
    }
    
    or
    
    {
        "status": "PENDING_APPROVAL",
        "message": "Quote submitted - awaiting manager approval",
        "quoted_rate": 225.50,
        "budget": 200.00
    }
    """
    
    try:
        # Determine response type from URL
        if action == 'accept':
            response_type = 'ACCEPT'
            quoted_rate = None
        elif action == 'quote':
            response_type = 'QUOTE'
            data = json.loads(request.body)
            quoted_rate = data.get('quoted_rate')
            
            if not quoted_rate:
                return JsonResponse({
                    'error': 'quoted_rate required for quote action'
                }, status=400)
        else:
            return JsonResponse({
                'error': f'Invalid action: {action}. Use "accept" or "quote"'
            }, status=400)
        
        # Process response
        result = AgencyCoordinationService.process_agency_response(
            response_id=response_id,
            response_type=response_type,
            quoted_rate=quoted_rate
        )
        
        return JsonResponse(result)
    
    except ValueError as e:
        logger.error(f"Validation error in agency_response_webhook: {str(e)}")
        return JsonResponse({
            'error': str(e)
        }, status=400)
    
    except Exception as e:
        logger.exception(f"Error in agency_response_webhook: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error',
            'details': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def manual_book_agency(request, response_id):
    """
    Manually approve and book an agency quote
    (Manager override when quote exceeds auto-book threshold)
    
    POST /api/agency-coordination/response/<id>/manual-book/
    
    Body:
    {
        "approved_by": "John Smith (OM)",
        "notes": "Approved due to urgent coverage need"
    }
    
    Returns:
    {
        "status": "BOOKED",
        "message": "Manual booking confirmed",
        "agency": "ABC Staffing",
        "rate": 225.50
    }
    """
    
    try:
        data = json.loads(request.body)
        approved_by = data.get('approved_by', 'Manager')
        notes = data.get('notes', '')
        
        # Get response
        agency_response = AgencyResponse.objects.select_related(
            'blast_batch', 'agency'
        ).get(id=response_id)
        
        # Check if valid for manual booking
        if agency_response.status not in ['QUOTED', 'ACCEPTED']:
            return JsonResponse({
                'error': f'Cannot book response with status: {agency_response.status}'
            }, status=400)
        
        # Perform booking
        result = AgencyCoordinationService._auto_book_agency(agency_response)
        
        # Log manual approval
        logger.info(
            f"Manual booking approved by {approved_by} for "
            f"{agency_response.agency.name} at £{agency_response.quoted_rate}. "
            f"Notes: {notes}"
        )
        
        result['approved_by'] = approved_by
        result['notes'] = notes
        
        return JsonResponse(result)
    
    except AgencyResponse.DoesNotExist:
        return JsonResponse({
            'error': 'Agency response not found'
        }, status=404)
    
    except Exception as e:
        logger.exception(f"Error in manual_book_agency: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error',
            'details': str(e)
        }, status=500)


@require_http_methods(["GET"])
def list_active_blasts(request):
    """
    List all active agency blast batches
    
    GET /api/agency-coordination/active-blasts/
    
    Query params:
    - status: Filter by status (PENDING, PARTIAL, etc.)
    - limit: Max results (default 20)
    
    Returns:
    {
        "blasts": [
            {
                "blast_batch_id": 123,
                "shift": {...},
                "status": "PENDING",
                "agencies_contacted": 3,
                "responses_received": 1,
                "time_remaining": "15 minutes"
            },
            ...
        ],
        "total": 5
    }
    """
    
    # Get filters
    status_filter = request.GET.get('status')
    limit = int(request.GET.get('limit', 20))
    
    # Build query
    query = AgencyBlastBatch.objects.select_related(
        'agency_request__shift__unit__home'
    ).prefetch_related('agency_responses')
    
    if status_filter:
        query = query.filter(status=status_filter)
    
    blasts = query[:limit]
    
    # Build results
    blasts_list = []
    now = timezone.now()
    
    for blast in blasts:
        shift = blast.agency_request.shift
        summary = blast.get_response_summary()
        
        # Calculate time remaining
        if blast.response_deadline > now:
            delta = blast.response_deadline - now
            minutes_remaining = int(delta.total_seconds() / 60)
            time_remaining = f"{minutes_remaining} minutes"
        else:
            time_remaining = "EXPIRED"
        
        blasts_list.append({
            'blast_batch_id': blast.id,
            'shift': {
                'id': shift.id,
                'date': shift.date.isoformat(),
                'time': f"{shift.start_time.strftime('%H:%M')}-{shift.end_time.strftime('%H:%M')}",
                'role': shift.role,
                'home': shift.unit.home.name if hasattr(shift.unit, 'home') else 'N/A'
            },
            'status': blast.status,
            'agencies_contacted': summary['total'],
            'responses_received': summary['accepted'] + summary['quoted'] + summary['declined'],
            'time_remaining': time_remaining,
            'budget_limit': str(blast.budget_limit)
        })
    
    return JsonResponse({
        'blasts': blasts_list,
        'total': len(blasts_list)
    })
