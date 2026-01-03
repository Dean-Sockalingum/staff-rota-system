"""
Week 6: Power User Features - Views
Dashboard widget customization, saved filters, and bulk operations
"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models_week6 import DashboardWidgetPreference, SavedSearchFilter, BulkOperationLog
from .models import LeaveRequest, User


@login_required
@require_http_methods(["GET"])
def get_widget_preferences(request):
    """
    Get user's dashboard widget preferences
    """
    try:
        preferences = DashboardWidgetPreference.objects.filter(
            user=request.user
        ).order_by('position')
        
        data = {
            'success': True,
            'preferences': [
                {
                    'widget_id': pref.widget_id,
                    'is_visible': pref.is_visible,
                    'position': pref.position
                }
                for pref in preferences
            ]
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def save_widget_preferences(request):
    """
    Save user's dashboard widget preferences
    """
    try:
        data = json.loads(request.body)
        preferences = data.get('preferences', [])
        
        # Delete existing preferences
        DashboardWidgetPreference.objects.filter(user=request.user).delete()
        
        # Create new preferences
        for idx, pref in enumerate(preferences):
            DashboardWidgetPreference.objects.create(
                user=request.user,
                widget_id=pref['widget_id'],
                is_visible=pref['is_visible'],
                position=idx
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Preferences saved successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_saved_filters(request):
    """
    Get user's saved search filters
    """
    try:
        filter_type = request.GET.get('filter_type')
        
        query = SavedSearchFilter.objects.filter(user=request.user)
        if filter_type:
            query = query.filter(filter_type=filter_type)
        
        filters = query.order_by('-last_used')
        
        data = {
            'success': True,
            'filters': [
                {
                    'id': f.id,
                    'name': f.name,
                    'filter_type': f.filter_type,
                    'filter_params': f.filter_params,
                    'is_default': f.is_default,
                    'use_count': f.use_count
                }
                for f in filters
            ]
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def save_search_filter(request):
    """
    Save a new search filter
    """
    try:
        data = json.loads(request.body)
        
        # If setting as default, unset other defaults
        if data.get('is_default'):
            SavedSearchFilter.objects.filter(
                user=request.user,
                filter_type=data['filter_type']
            ).update(is_default=False)
        
        filter_obj = SavedSearchFilter.objects.create(
            user=request.user,
            name=data['name'],
            filter_type=data['filter_type'],
            filter_params=data['filter_params'],
            is_default=data.get('is_default', False),
            is_shared=data.get('is_shared', False)
        )
        
        return JsonResponse({
            'success': True,
            'filter_id': filter_obj.id,
            'message': 'Filter saved successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def delete_saved_filter(request, filter_id):
    """
    Delete a saved search filter
    """
    try:
        SavedSearchFilter.objects.filter(
            id=filter_id,
            user=request.user
        ).delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Filter deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def bulk_approve_leave(request):
    """
    Bulk approve multiple leave requests
    """
    try:
        data = json.loads(request.body)
        request_ids = data.get('request_ids', [])
        
        # Check permissions
        if not request.user.role or not request.user.role.can_approve_leave:
            return JsonResponse({
                'success': False,
                'error': 'You do not have permission to approve leave requests'
            }, status=403)
        
        success_count = 0
        failure_count = 0
        failed_ids = []
        
        for request_id in request_ids:
            try:
                leave_request = LeaveRequest.objects.get(
                    id=request_id,
                    care_home=request.user.care_home
                )
                
                # Check if already approved/rejected
                if leave_request.status in ['approved', 'rejected']:
                    failure_count += 1
                    failed_ids.append(request_id)
                    continue
                
                leave_request.status = 'approved'
                leave_request.approved_by = request.user
                leave_request.save()
                success_count += 1
                
            except LeaveRequest.DoesNotExist:
                failure_count += 1
                failed_ids.append(request_id)
        
        # Log the bulk operation
        BulkOperationLog.objects.create(
            user=request.user,
            operation_type='leave_approve',
            success_count=success_count,
            failure_count=failure_count,
            details={
                'request_ids': request_ids,
                'failed_ids': failed_ids
            }
        )
        
        return JsonResponse({
            'success': True,
            'success_count': success_count,
            'failure_count': failure_count,
            'failed_ids': failed_ids,
            'message': f'Approved {success_count} leave requests'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def bulk_reject_leave(request):
    """
    Bulk reject multiple leave requests
    """
    try:
        data = json.loads(request.body)
        request_ids = data.get('request_ids', [])
        rejection_reason = data.get('reason', 'Bulk rejected')
        
        # Check permissions
        if not request.user.role or not request.user.role.can_approve_leave:
            return JsonResponse({
                'success': False,
                'error': 'You do not have permission to reject leave requests'
            }, status=403)
        
        success_count = 0
        failure_count = 0
        failed_ids = []
        
        for request_id in request_ids:
            try:
                leave_request = LeaveRequest.objects.get(
                    id=request_id,
                    care_home=request.user.care_home
                )
                
                # Check if already approved/rejected
                if leave_request.status in ['approved', 'rejected']:
                    failure_count += 1
                    failed_ids.append(request_id)
                    continue
                
                leave_request.status = 'rejected'
                leave_request.approved_by = request.user
                leave_request.notes = rejection_reason
                leave_request.save()
                success_count += 1
                
            except LeaveRequest.DoesNotExist:
                failure_count += 1
                failed_ids.append(request_id)
        
        # Log the bulk operation
        BulkOperationLog.objects.create(
            user=request.user,
            operation_type='leave_reject',
            success_count=success_count,
            failure_count=failure_count,
            details={
                'request_ids': request_ids,
                'failed_ids': failed_ids,
                'reason': rejection_reason
            }
        )
        
        return JsonResponse({
            'success': True,
            'success_count': success_count,
            'failure_count': failure_count,
            'failed_ids': failed_ids,
            'message': f'Rejected {success_count} leave requests'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def bulk_assign_training(request):
    """
    Bulk assign training to multiple staff members
    """
    try:
        data = json.loads(request.body)
        staff_ids = data.get('staff_ids', [])
        training_type = data.get('training_type')
        due_date = data.get('due_date')
        
        # Check permissions
        if not request.user.role or not request.user.role.can_manage_training:
            return JsonResponse({
                'success': False,
                'error': 'You do not have permission to assign training'
            }, status=403)
        
        from .models import TrainingRecord
        from datetime import datetime
        
        success_count = 0
        failure_count = 0
        failed_ids = []
        
        for staff_id in staff_ids:
            try:
                staff = User.objects.get(
                    id=staff_id,
                    care_home=request.user.care_home
                )
                
                # Create training record
                TrainingRecord.objects.create(
                    staff=staff,
                    training_type=training_type,
                    status='assigned',
                    due_date=datetime.fromisoformat(due_date) if due_date else None,
                    assigned_by=request.user
                )
                success_count += 1
                
            except User.DoesNotExist:
                failure_count += 1
                failed_ids.append(staff_id)
            except Exception as e:
                failure_count += 1
                failed_ids.append(staff_id)
        
        # Log the bulk operation
        BulkOperationLog.objects.create(
            user=request.user,
            operation_type='training_assign',
            success_count=success_count,
            failure_count=failure_count,
            details={
                'staff_ids': staff_ids,
                'failed_ids': failed_ids,
                'training_type': training_type,
                'due_date': due_date
            }
        )
        
        return JsonResponse({
            'success': True,
            'success_count': success_count,
            'failure_count': failure_count,
            'failed_ids': failed_ids,
            'message': f'Assigned training to {success_count} staff members'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
