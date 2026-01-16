"""
Shift Swap API Views - Task 3
REST endpoints for intelligent shift swap auto-approval system
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
import json
import logging

from scheduling.services_shift_swap_validator import ShiftSwapValidator
from scheduling.models import ShiftSwapRequest, Shift, User
from scheduling.notifications import send_email


logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
@csrf_exempt
def create_swap_request(request):
    """
    Create new shift swap request with auto-validation
    
    POST /api/shift-swaps/create/
    
    Body:
    {
        "requesting_user_id": 123,
        "target_user_id": 456,
        "requesting_shift_id": 789,
        "target_shift_id": 101,
        "reason": "Family commitment - need to swap weekend"
    }
    
    Returns:
    {
        "swap_request_id": 999,
        "status": "AUTO_APPROVED",
        "automated_decision": true,
        "message": "Swap auto-approved by system",
        "validation_results": {
            "role_match": {"pass": true, "message": "..."},
            "qualification_match": {"pass": true, "score": 100, "message": "..."},
            "wdt_compliance": {"pass": true, "message": "..."},
            "coverage_maintained": {"pass": true, "message": "..."},
            "no_conflicts": {"pass": true, "message": "..."}
        }
    }
    
    or
    
    {
        "swap_request_id": 999,
        "status": "DENIED",
        "automated_decision": true,
        "denial_reason": "Role mismatch: SCW cannot swap with RN - skills mismatch",
        "validation_results": {...}
    }
    """
    
    try:
        data = json.loads(request.body)
        
        requesting_user_id = data.get('requesting_user_id')
        target_user_id = data.get('target_user_id')
        requesting_shift_id = data.get('requesting_shift_id')
        target_shift_id = data.get('target_shift_id')
        reason = data.get('reason', '')
        
        # Validate required fields
        if not all([requesting_user_id, target_user_id, requesting_shift_id, target_shift_id]):
            return JsonResponse({
                'error': 'Missing required fields: requesting_user_id, target_user_id, requesting_shift_id, target_shift_id'
            }, status=400)
        
        # Get objects
        try:
            requesting_user = User.objects.get(id=requesting_user_id)
            target_user = User.objects.get(id=target_user_id)
            requesting_shift = Shift.objects.get(id=requesting_shift_id)
            target_shift = Shift.objects.get(id=target_shift_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid user ID'}, status=404)
        except Shift.DoesNotExist:
            return JsonResponse({'error': 'Invalid shift ID'}, status=404)
        
        # Create swap request
        with transaction.atomic():
            swap_request = ShiftSwapRequest.objects.create(
                requesting_user=requesting_user,
                target_user=target_user,
                requesting_shift=requesting_shift,
                target_shift=target_shift,
                reason=reason,
                status='PENDING'
            )
            
            # Run auto-validation
            validation_result = ShiftSwapValidator.validate_swap_request(swap_request)
            
            # Apply decision
            ShiftSwapValidator.apply_swap_decision(swap_request, validation_result)
            
            # Send notifications
            _send_swap_notifications(swap_request, validation_result)
        
        # Build response
        return JsonResponse({
            'swap_request_id': swap_request.id,
            'status': swap_request.status,
            'automated_decision': swap_request.automated_decision,
            'denial_reason': swap_request.denial_reason,
            'message': _get_status_message(swap_request.status),
            'validation_results': validation_result['validation_results'],
            'created_at': swap_request.created_at.isoformat()
        })
    
    except Exception as e:
        logger.exception(f"Error creating swap request: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error',
            'details': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_swap_status(request, swap_request_id):
    """
    Get detailed status of swap request
    
    GET /api/shift-swaps/<id>/status/
    
    Returns:
    {
        "swap_request_id": 999,
        "status": "AUTO_APPROVED",
        "automated_decision": true,
        "requesting_user": {
            "id": 123,
            "name": "John Smith",
            "shift": {
                "date": "2025-12-28",
                "time": "07:00-19:00",
                "unit": "Orchard Grove"
            }
        },
        "target_user": {
            "id": 456,
            "name": "Jane Doe",
            "shift": {
                "date": "2025-12-29",
                "time": "19:00-07:00",
                "unit": "Victoria Gardens"
            }
        },
        "reason": "Family commitment",
        "created_at": "2025-12-28T10:00:00Z",
        "approval_date": "2025-12-28T10:00:05Z",
        "approval_notes": "Auto-approved by intelligent validation system",
        "qualification_score": 100,
        "wdt_compliant": true
    }
    """
    
    try:
        swap_request = ShiftSwapRequest.objects.select_related(
            'requesting_user',
            'target_user',
            'requesting_shift__unit',
            'target_shift__unit',
            'approved_by'
        ).get(id=swap_request_id)
        
    except ShiftSwapRequest.DoesNotExist:
        return JsonResponse({
            'error': 'Swap request not found'
        }, status=404)
    
    # Build response
    response_data = {
        'swap_request_id': swap_request.id,
        'status': swap_request.status,
        'automated_decision': swap_request.automated_decision,
        'requesting_user': {
            'id': swap_request.requesting_user.id,
            'name': swap_request.requesting_user.get_full_name(),
            'shift': {
                'id': swap_request.requesting_shift.id,
                'date': swap_request.requesting_shift.date.isoformat(),
                'time': f"{swap_request.requesting_shift.start_time.strftime('%H:%M')}-{swap_request.requesting_shift.end_time.strftime('%H:%M')}",
                'unit': swap_request.requesting_shift.unit.name,
                'role': swap_request.requesting_shift.role
            }
        },
        'target_user': {
            'id': swap_request.target_user.id,
            'name': swap_request.target_user.get_full_name(),
            'shift': {
                'id': swap_request.target_shift.id,
                'date': swap_request.target_shift.date.isoformat(),
                'time': f"{swap_request.target_shift.start_time.strftime('%H:%M')}-{swap_request.target_shift.end_time.strftime('%H:%M')}",
                'unit': swap_request.target_shift.unit.name,
                'role': swap_request.target_shift.role
            }
        },
        'reason': swap_request.reason,
        'created_at': swap_request.created_at.isoformat(),
        'qualification_score': float(swap_request.qualification_match_score),
        'wdt_compliant': swap_request.wdt_compliance_check,
        'role_mismatch': swap_request.role_mismatch
    }
    
    if swap_request.denial_reason:
        response_data['denial_reason'] = swap_request.denial_reason
    
    if swap_request.approval_date:
        response_data['approval_date'] = swap_request.approval_date.isoformat()
        response_data['approval_notes'] = swap_request.approval_notes
        
        if swap_request.approved_by:
            response_data['approved_by'] = swap_request.approved_by.get_full_name()
        else:
            response_data['approved_by'] = 'System Auto-Approval'
    
    return JsonResponse(response_data)


@require_http_methods(["GET"])
def list_my_swaps(request):
    """
    List all swap requests for authenticated user
    
    GET /api/shift-swaps/my-swaps/
    
    Query params:
    - user_id: User ID (required)
    - status: Filter by status (optional)
    - limit: Max results (default 20)
    
    Returns:
    {
        "swaps": [
            {
                "swap_request_id": 999,
                "status": "AUTO_APPROVED",
                "type": "REQUESTING",
                "partner": "Jane Doe",
                "my_shift": "28 Dec 07:00-19:00 at Orchard Grove",
                "their_shift": "29 Dec 19:00-07:00 at Victoria Gardens",
                "created_at": "2025-12-28T10:00:00Z",
                "automated": true
            },
            ...
        ],
        "total": 5
    }
    """
    
    user_id = request.GET.get('user_id')
    status_filter = request.GET.get('status')
    limit = int(request.GET.get('limit', 20))
    
    if not user_id:
        return JsonResponse({'error': 'user_id required'}, status=400)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Invalid user_id'}, status=404)
    
    # Get swaps where user is either requester or target
    from django.db.models import Q
    
    query = ShiftSwapRequest.objects.filter(
        Q(requesting_user=user) | Q(target_user=user)
    ).select_related(
        'requesting_user',
        'target_user',
        'requesting_shift__unit',
        'target_shift__unit'
    )
    
    if status_filter:
        query = query.filter(status=status_filter)
    
    swaps = query.order_by('-created_at')[:limit]
    
    # Build results
    swaps_list = []
    for swap in swaps:
        is_requester = (swap.requesting_user == user)
        
        swaps_list.append({
            'swap_request_id': swap.id,
            'status': swap.status,
            'type': 'REQUESTING' if is_requester else 'TARGET',
            'partner': swap.target_user.get_full_name() if is_requester else swap.requesting_user.get_full_name(),
            'my_shift': _format_shift(swap.requesting_shift if is_requester else swap.target_shift),
            'their_shift': _format_shift(swap.target_shift if is_requester else swap.requesting_shift),
            'created_at': swap.created_at.isoformat(),
            'automated': swap.automated_decision,
            'denial_reason': swap.denial_reason if swap.status == 'DENIED' else None
        })
    
    return JsonResponse({
        'swaps': swaps_list,
        'total': len(swaps_list)
    })


@require_http_methods(["POST"])
@csrf_exempt
def manual_approve_swap(request, swap_request_id):
    """
    Manually approve swap request (manager override)
    
    POST /api/shift-swaps/<id>/manual-approve/
    
    Body:
    {
        "approved_by_user_id": 789,
        "notes": "Approved due to staff request despite minor qualification gap"
    }
    
    Returns:
    {
        "status": "APPROVED",
        "message": "Swap manually approved",
        "approved_by": "Sarah Johnson",
        "approval_date": "2025-12-28T14:30:00Z"
    }
    """
    
    try:
        data = json.loads(request.body)
        approved_by_user_id = data.get('approved_by_user_id')
        notes = data.get('notes', '')
        
        if not approved_by_user_id:
            return JsonResponse({'error': 'approved_by_user_id required'}, status=400)
        
        try:
            swap_request = ShiftSwapRequest.objects.get(id=swap_request_id)
            approved_by = User.objects.get(id=approved_by_user_id)
        except ShiftSwapRequest.DoesNotExist:
            return JsonResponse({'error': 'Swap request not found'}, status=404)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid approved_by_user_id'}, status=404)
        
        # Check if already approved/denied
        if swap_request.status in ['APPROVED', 'AUTO_APPROVED', 'DENIED']:
            return JsonResponse({
                'error': f'Cannot manually approve swap with status: {swap_request.status}'
            }, status=400)
        
        # Execute approval
        with transaction.atomic():
            swap_request.status = 'APPROVED'
            swap_request.management_approved = True
            swap_request.approved_by = approved_by
            swap_request.approval_date = timezone.now()
            swap_request.approval_notes = notes
            swap_request.save()
            
            # Execute the swap
            ShiftSwapValidator._execute_swap(swap_request)
        
        # Send notifications
        _send_approval_notification(swap_request)
        
        logger.info(
            f"Swap request {swap_request_id} manually approved by "
            f"{approved_by.get_full_name()}"
        )
        
        return JsonResponse({
            'status': swap_request.status,
            'message': 'Swap manually approved',
            'approved_by': approved_by.get_full_name(),
            'approval_date': swap_request.approval_date.isoformat(),
            'notes': notes
        })
    
    except Exception as e:
        logger.exception(f"Error in manual_approve_swap: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error',
            'details': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def deny_swap(request, swap_request_id):
    """
    Deny swap request
    
    POST /api/shift-swaps/<id>/deny/
    
    Body:
    {
        "denied_by_user_id": 789,
        "reason": "Operational requirements - cannot approve at this time"
    }
    
    Returns:
    {
        "status": "DENIED",
        "message": "Swap request denied",
        "denied_by": "Sarah Johnson",
        "denial_reason": "..."
    }
    """
    
    try:
        data = json.loads(request.body)
        denied_by_user_id = data.get('denied_by_user_id')
        reason = data.get('reason', 'Denied by manager')
        
        if not denied_by_user_id:
            return JsonResponse({'error': 'denied_by_user_id required'}, status=400)
        
        try:
            swap_request = ShiftSwapRequest.objects.get(id=swap_request_id)
            denied_by = User.objects.get(id=denied_by_user_id)
        except ShiftSwapRequest.DoesNotExist:
            return JsonResponse({'error': 'Swap request not found'}, status=404)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid denied_by_user_id'}, status=404)
        
        # Check if already approved
        if swap_request.status in ['APPROVED', 'AUTO_APPROVED']:
            return JsonResponse({
                'error': f'Cannot deny approved swap'
            }, status=400)
        
        # Execute denial
        swap_request.status = 'DENIED'
        swap_request.denial_reason = reason
        swap_request.approved_by = denied_by
        swap_request.approval_date = timezone.now()
        swap_request.approval_notes = f"Denied by {denied_by.get_full_name()}: {reason}"
        swap_request.save()
        
        # Send notifications
        _send_denial_notification(swap_request)
        
        logger.info(
            f"Swap request {swap_request_id} denied by "
            f"{denied_by.get_full_name()}: {reason}"
        )
        
        return JsonResponse({
            'status': swap_request.status,
            'message': 'Swap request denied',
            'denied_by': denied_by.get_full_name(),
            'denial_reason': reason
        })
    
    except Exception as e:
        logger.exception(f"Error in deny_swap: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error',
            'details': str(e)
        }, status=500)


# Helper functions

def _get_status_message(status):
    """Get user-friendly status message"""
    
    messages = {
        'AUTO_APPROVED': 'Swap auto-approved by system - shifts have been swapped',
        'MANUAL_REVIEW': 'Swap requires manager review - awaiting approval',
        'DENIED': 'Swap request denied - see denial reason',
        'APPROVED': 'Swap approved by manager - shifts have been swapped',
        'CANCELLED': 'Swap request cancelled',
        'PENDING': 'Swap request submitted - under review'
    }
    
    return messages.get(status, f'Status: {status}')


def _format_shift(shift):
    """Format shift for display"""
    
    return (
        f"{shift.date.strftime('%d %b')} "
        f"{shift.start_time.strftime('%H:%M')}-{shift.end_time.strftime('%H:%M')} "
        f"at {shift.unit.name}"
    )


def _send_swap_notifications(swap_request, validation_result):
    """Send email notifications based on swap status"""
    
    if swap_request.status == 'AUTO_APPROVED':
        _send_auto_approval_notification(swap_request)
    elif swap_request.status == 'DENIED':
        _send_auto_denial_notification(swap_request, validation_result)
    elif swap_request.status == 'MANUAL_REVIEW':
        _send_manual_review_notification(swap_request)


def _send_auto_approval_notification(swap_request):
    """Send notification for auto-approved swap"""
    
    subject = "✅ Shift Swap Auto-Approved"
    
    message = f"""
    Your shift swap has been automatically approved!
    
    {swap_request.requesting_user.get_full_name()}:
    - Giving up: {_format_shift(swap_request.requesting_shift)}
    - Taking: {_format_shift(swap_request.target_shift)}
    
    {swap_request.target_user.get_full_name()}:
    - Giving up: {_format_shift(swap_request.target_shift)}
    - Taking: {_format_shift(swap_request.requesting_shift)}
    
    The swap has been completed - check your updated rota.
    """
    
    # Send to both users
    for user in [swap_request.requesting_user, swap_request.target_user]:
        send_email(
            to_email=user.email,
            subject=subject,
            html_body=f"<pre>{message}</pre>"
        )


def _send_auto_denial_notification(swap_request, validation_result):
    """Send notification for auto-denied swap"""
    
    subject = "❌ Shift Swap Auto-Denied"
    
    message = f"""
    Your shift swap request was automatically denied.
    
    Reason: {swap_request.denial_reason}
    
    If you believe this is an error, please contact your manager.
    """
    
    send_email(
        to_email=swap_request.requesting_user.email,
        subject=subject,
        html_body=f"<pre>{message}</pre>"
    )


def _send_manual_review_notification(swap_request):
    """Send notification that swap requires manual review"""
    
    subject = "⏳ Shift Swap Awaiting Manager Review"
    
    message = f"""
    Your shift swap request requires manager review.
    
    This is usually approved within 24 hours.
    You'll receive an email when a decision is made.
    """
    
    send_email(
        to_email=swap_request.requesting_user.email,
        subject=subject,
        html_body=f"<pre>{message}</pre>"
    )


def _send_approval_notification(swap_request):
    """Send notification for manual approval"""
    
    subject = "✅ Shift Swap Approved by Manager"
    
    message = f"""
    Your shift swap has been approved by {swap_request.approved_by.get_full_name()}.
    
    Notes: {swap_request.approval_notes}
    
    The swap has been completed - check your updated rota.
    """
    
    for user in [swap_request.requesting_user, swap_request.target_user]:
        send_email(
            to_email=user.email,
            subject=subject,
            html_body=f"<pre>{message}</pre>"
        )


def _send_denial_notification(swap_request):
    """Send notification for manual denial"""
    
    subject = "❌ Shift Swap Denied"
    
    message = f"""
    Your shift swap request has been denied.
    
    Reason: {swap_request.denial_reason}
    
    Please contact your manager if you have questions.
    """
    
    send_email(
        to_email=swap_request.requesting_user.email,
        subject=subject,
        html_body=f"<pre>{message}</pre>"
    )
