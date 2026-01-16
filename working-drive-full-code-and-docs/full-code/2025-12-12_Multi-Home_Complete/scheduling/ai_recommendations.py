"""
AI Assistant - Actionable Recommendations System
Allows users to approve and execute AI-suggested staff moves with one click
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from scheduling.decorators_api import api_login_required
from datetime import datetime
import json
import logging

from scheduling.models import Shift, User, StaffReallocation, ActivityLog

logger = logging.getLogger(__name__)


@api_login_required
@require_http_methods(["POST"])
def approve_ai_recommendation(request):
    """
    API endpoint to approve and execute AI-suggested staff moves
    
    Expected JSON:
    {
        "recommendation_id": "unique_id",
        "type": "staff_move",
        "moves": [
            {
                "shift_id": 123,
                "from_unit": "HH_THISTLE_SRD",
                "to_unit": "HH_HEATHER_SRD",
                "staff_sap": "STAFF001"
            }
        ],
        "date": "2025-12-26",
        "reason": "Balance day shift coverage"
    }
    """
    
    try:
        data = json.loads(request.body)
        
        recommendation_type = data.get('type')
        moves = data.get('moves', [])
        date = data.get('date')
        reason = data.get('reason', 'AI-recommended staff reallocation')
        
        if not moves:
            return JsonResponse({
                'success': False,
                'error': 'No moves provided'
            }, status=400)
        
        # Verify user has permission
        if not (request.user.is_staff or 
                (request.user.role and request.user.role.can_manage_rota)):
            return JsonResponse({
                'success': False,
                'error': 'You do not have permission to approve staff moves'
            }, status=403)
        
        executed_moves = []
        failed_moves = []
        
        # Execute moves in a transaction (all or nothing)
        with transaction.atomic():
            for move in moves:
                try:
                    result = _execute_staff_move(
                        shift_id=move.get('shift_id'),
                        from_unit=move.get('from_unit'),
                        to_unit=move.get('to_unit'),
                        staff_sap=move.get('staff_sap'),
                        approved_by=request.user,
                        reason=reason,
                        date=date
                    )
                    
                    if result['success']:
                        executed_moves.append(result)
                    else:
                        failed_moves.append({
                            'move': move,
                            'error': result['error']
                        })
                        
                except Exception as e:
                    logger.error(f"Error executing move: {e}")
                    failed_moves.append({
                        'move': move,
                        'error': str(e)
                    })
        
        # Log the approval
        ActivityLog.objects.create(
            user=request.user,
            action_type='AI_RECOMMENDATION_APPROVED',
            description=f"Approved {len(executed_moves)} AI-recommended staff moves for {date}",
            metadata=json.dumps({
                'recommendation_type': recommendation_type,
                'date': str(date),
                'moves_executed': len(executed_moves),
                'moves_failed': len(failed_moves),
                'reason': reason
            })
        )
        
        return JsonResponse({
            'success': True,
            'executed_count': len(executed_moves),
            'failed_count': len(failed_moves),
            'executed_moves': executed_moves,
            'failed_moves': failed_moves,
            'message': f"✅ Successfully executed {len(executed_moves)} staff moves"
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in approve_ai_recommendation: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _execute_staff_move(shift_id, from_unit, to_unit, staff_sap, approved_by, reason, date):
    """
    Execute a single staff move
    
    Returns:
        dict: {'success': bool, 'message': str, 'reallocation_id': int}
    """
    try:
        # Get the shift
        shift = Shift.objects.select_related('user', 'unit').get(id=shift_id)
        
        # Verify the shift details match
        if shift.user.sap != staff_sap:
            return {
                'success': False,
                'error': f"Shift user mismatch: expected {staff_sap}, got {shift.user.sap}"
            }
        
        if shift.unit.name != from_unit:
            return {
                'success': False,
                'error': f"Unit mismatch: expected {from_unit}, got {shift.unit.name}"
            }
        
        # Get the target unit
        from scheduling.models import Unit
        target_unit = Unit.objects.get(name=to_unit)
        
        # Create reallocation record
        reallocation = StaffReallocation.objects.create(
            staff_member=shift.user,
            from_unit=shift.unit,
            to_unit=target_unit,
            shift_date=shift.date,
            shift_type=shift.shift_type,
            reason=reason,
            status='APPROVED',
            requested_by=approved_by,
            approved_by=approved_by,
            approved_at=timezone.now(),
            is_permanent=False,
            notes=f"AI-recommended move approved by {approved_by.full_name}"
        )
        
        # Update the shift
        old_unit_name = shift.unit.name
        shift.unit = target_unit
        shift.save()
        
        # Log the change
        ActivityLog.objects.create(
            user=approved_by,
            action_type='STAFF_REALLOCATED',
            description=f"Moved {shift.user.full_name} from {old_unit_name} to {to_unit} for {date}",
            metadata=json.dumps({
                'shift_id': shift_id,
                'staff_sap': staff_sap,
                'from_unit': old_unit_name,
                'to_unit': to_unit,
                'date': str(date),
                'reallocation_id': reallocation.id,
                'source': 'ai_recommendation'
            })
        )
        
        return {
            'success': True,
            'message': f"Moved {shift.user.full_name} from {old_unit_name} to {to_unit}",
            'reallocation_id': reallocation.id,
            'staff_name': shift.user.full_name,
            'from_unit': old_unit_name,
            'to_unit': to_unit
        }
        
    except Shift.DoesNotExist:
        return {
            'success': False,
            'error': f"Shift #{shift_id} not found"
        }
    except Unit.DoesNotExist:
        return {
            'success': False,
            'error': f"Target unit {to_unit} not found"
        }
    except Exception as e:
        logger.error(f"Error executing staff move: {e}")
        return {
            'success': False,
            'error': str(e)
        }


@api_login_required
@require_http_methods(["POST"])
def reject_ai_recommendation(request):
    """
    API endpoint to reject AI-suggested staff moves
    Logs the rejection for analytics
    """
    try:
        data = json.loads(request.body)
        
        recommendation_id = data.get('recommendation_id')
        reason = data.get('reason', 'User declined recommendation')
        
        # Log the rejection
        ActivityLog.objects.create(
            user=request.user,
            action_type='AI_RECOMMENDATION_REJECTED',
            description=f"Rejected AI recommendation #{recommendation_id}",
            metadata=json.dumps({
                'recommendation_id': recommendation_id,
                'reason': reason,
                'rejected_at': str(timezone.now())
            })
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Recommendation rejected'
        })
        
    except Exception as e:
        logger.error(f"Error in reject_ai_recommendation: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
