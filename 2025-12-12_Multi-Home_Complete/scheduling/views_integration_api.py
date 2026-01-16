"""
Integration API Views
====================

API endpoints for third-party integrations.

Created: 30 December 2025
Task 41: Integration APIs
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from datetime import datetime, timedelta
import json

from .models import (
    User, Shift, Unit, CareHome, LeaveRequest,
    ShiftSwapRequest, Role
)
from .models_integrations import (
    APIClient, APIToken, DataSyncJob, WebhookEndpoint, WebhookDelivery
)
from .api_auth import require_api_scope


# ====================
# Authentication Endpoints
# ====================

@csrf_exempt
@require_http_methods(["POST"])
def api_get_token(request):
    """
    OAuth-style token endpoint.
    
    POST /api/v1/integration/auth/token
    Body: {
        "client_id": "...",
        "client_secret": "...",
        "grant_type": "client_credentials",
        "scope": ["staff:read", "shifts:read"]
    }
    """
    try:
        data = json.loads(request.body)
        client_id = data.get('client_id')
        client_secret = data.get('client_secret')
        grant_type = data.get('grant_type', 'client_credentials')
        scope = data.get('scope', [])
        
        # Validate grant type
        if grant_type != 'client_credentials':
            return JsonResponse({
                'error': 'unsupported_grant_type',
                'message': 'Only client_credentials grant type is supported'
            }, status=400)
        
        # Verify client credentials
        try:
            client = APIClient.objects.get(
                client_id=client_id,
                is_active=True,
                status='ACTIVE'
            )
            
            if not client.verify_client_secret(client_secret):
                return JsonResponse({
                    'error': 'invalid_client',
                    'message': 'Invalid client credentials'
                }, status=401)
            
        except APIClient.DoesNotExist:
            return JsonResponse({
                'error': 'invalid_client',
                'message': 'Client not found'
            }, status=401)
        
        # Generate access token
        import secrets
        access_token_value = secrets.token_urlsafe(48)
        refresh_token_value = secrets.token_urlsafe(48)
        
        # Create tokens
        access_token = APIToken.objects.create(
            client=client,
            token=access_token_value,
            token_type='ACCESS',
            scope=scope,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        refresh_token = APIToken.objects.create(
            client=client,
            token=refresh_token_value,
            token_type='REFRESH',
            scope=scope,
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        return JsonResponse({
            'access_token': access_token.token,
            'token_type': 'Bearer',
            'expires_in': 86400,  # 24 hours
            'refresh_token': refresh_token.token,
            'scope': scope
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'invalid_request',
            'message': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'server_error',
            'message': str(e)
        }, status=500)


# ====================
# Staff Data Endpoints
# ====================

@csrf_exempt
@require_http_methods(["GET"])
@require_api_scope('staff:read')
def api_list_staff(request):
    """
    List all staff members.
    
    GET /api/v1/integration/staff
    Query params:
        - unit_id: Filter by unit
        - role: Filter by role
        - active: Filter active/inactive (true/false)
        - page: Page number
        - per_page: Results per page (max 100)
    """
    try:
        # Pagination
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 50)), 100)
        offset = (page - 1) * per_page
        
        # Build query
        queryset = User.objects.select_related('role', 'unit', 'home_unit').all()
        
        # Filters
        if unit_id := request.GET.get('unit_id'):
            queryset = queryset.filter(Q(unit_id=unit_id) | Q(home_unit_id=unit_id))
        
        if role_name := request.GET.get('role'):
            queryset = queryset.filter(role__name=role_name)
        
        if active := request.GET.get('active'):
            is_active = active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
        
        # Get total count
        total_count = queryset.count()
        
        # Get paginated results
        staff_list = queryset[offset:offset + per_page]
        
        # Serialize data
        data = [{
            'sap': staff.sap,
            'first_name': staff.first_name,
            'last_name': staff.last_name,
            'full_name': staff.full_name,
            'email': staff.email,
            'phone_number': staff.phone_number,
            'role': staff.role.name if staff.role else None,
            'unit': {
                'id': staff.unit.id if staff.unit else None,
                'name': staff.unit.name if staff.unit else None,
            } if staff.unit else None,
            'home_unit': {
                'id': staff.home_unit.id if staff.home_unit else None,
                'name': staff.home_unit.name if staff.home_unit else None,
            } if staff.home_unit else None,
            'team': staff.team,
            'shift_preference': staff.shift_preference,
            'is_active': staff.is_active,
            'is_staff': staff.is_staff,
            'annual_leave_allowance': staff.annual_leave_allowance,
            'annual_leave_used': staff.annual_leave_used,
            'annual_leave_remaining': staff.annual_leave_allowance - staff.annual_leave_used,
            'created_at': staff.created_at.isoformat() if staff.created_at else None,
        } for staff in staff_list]
        
        return JsonResponse({
            'data': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_count': total_count,
                'total_pages': (total_count + per_page - 1) // per_page,
                'has_next': offset + per_page < total_count,
                'has_prev': page > 1,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'error': 'server_error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@require_api_scope('staff:read')
def api_get_staff(request, sap):
    """
    Get individual staff member details.
    
    GET /api/v1/integration/staff/{sap}
    """
    try:
        staff = User.objects.select_related('role', 'unit', 'home_unit').get(sap=sap)
        
        data = {
            'sap': staff.sap,
            'first_name': staff.first_name,
            'last_name': staff.last_name,
            'full_name': staff.full_name,
            'email': staff.email,
            'phone_number': staff.phone_number,
            'role': {
                'name': staff.role.name,
                'shift_duration_hours': staff.role.shift_duration_hours,
                'shifts_per_week': staff.role.shifts_per_week,
            } if staff.role else None,
            'unit': {
                'id': staff.unit.id,
                'name': staff.unit.name,
                'care_home': staff.unit.care_home.name if staff.unit.care_home else None,
            } if staff.unit else None,
            'home_unit': {
                'id': staff.home_unit.id,
                'name': staff.home_unit.name,
            } if staff.home_unit else None,
            'team': staff.team,
            'shift_preference': staff.shift_preference,
            'is_active': staff.is_active,
            'is_staff': staff.is_staff,
            'annual_leave': {
                'allowance': staff.annual_leave_allowance,
                'used': staff.annual_leave_used,
                'remaining': staff.annual_leave_allowance - staff.annual_leave_used,
                'year_start': staff.annual_leave_year_start.isoformat() if staff.annual_leave_year_start else None,
            },
            'created_at': staff.created_at.isoformat() if staff.created_at else None,
            'updated_at': staff.updated_at.isoformat() if staff.updated_at else None,
        }
        
        return JsonResponse({'data': data})
        
    except User.DoesNotExist:
        return JsonResponse({
            'error': 'not_found',
            'message': f'Staff member with SAP {sap} not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': 'server_error',
            'message': str(e)
        }, status=500)


# ====================
# Shift Data Endpoints
# ====================

@csrf_exempt
@require_http_methods(["GET"])
@require_api_scope('shifts:read')
def api_list_shifts(request):
    """
    List shifts with filters.
    
    GET /api/v1/integration/shifts
    Query params:
        - start_date: Filter shifts from date (YYYY-MM-DD)
        - end_date: Filter shifts to date (YYYY-MM-DD)
        - unit_id: Filter by unit
        - user_sap: Filter by staff member
        - status: Filter by status
        - page: Page number
        - per_page: Results per page (max 100)
    """
    try:
        # Pagination
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 50)), 100)
        offset = (page - 1) * per_page
        
        # Build query
        queryset = Shift.objects.select_related('user', 'unit', 'unit__care_home').all()
        
        # Filters
        if start_date := request.GET.get('start_date'):
            queryset = queryset.filter(date__gte=datetime.fromisoformat(start_date).date())
        
        if end_date := request.GET.get('end_date'):
            queryset = queryset.filter(date__lte=datetime.fromisoformat(end_date).date())
        
        if unit_id := request.GET.get('unit_id'):
            queryset = queryset.filter(unit_id=unit_id)
        
        if user_sap := request.GET.get('user_sap'):
            queryset = queryset.filter(user__sap=user_sap)
        
        if status := request.GET.get('status'):
            queryset = queryset.filter(status=status.upper())
        
        # Get total count
        total_count = queryset.count()
        
        # Get paginated results
        shifts = queryset.order_by('-date', '-start_time')[offset:offset + per_page]
        
        # Serialize data
        data = [{
            'id': shift.id,
            'date': shift.date.isoformat(),
            'start_time': shift.start_time.isoformat() if shift.start_time else None,
            'end_time': shift.end_time.isoformat() if shift.end_time else None,
            'duration_hours': shift.duration_hours,
            'status': shift.status,
            'is_overtime': shift.is_overtime,
            'is_agency': shift.is_agency,
            'staff': {
                'sap': shift.user.sap if shift.user else None,
                'full_name': shift.user.full_name if shift.user else None,
            } if shift.user else None,
            'unit': {
                'id': shift.unit.id,
                'name': shift.unit.name,
                'care_home': shift.unit.care_home.name if shift.unit.care_home else None,
            } if shift.unit else None,
            'notes': shift.notes,
            'created_at': shift.created_at.isoformat() if shift.created_at else None,
        } for shift in shifts]
        
        return JsonResponse({
            'data': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_count': total_count,
                'total_pages': (total_count + per_page - 1) // per_page,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'error': 'server_error',
            'message': str(e)
        }, status=500)


# ====================
# Leave Request Endpoints
# ====================

@csrf_exempt
@require_http_methods(["GET"])
@require_api_scope('leave:read')
def api_list_leave_requests(request):
    """
    List leave requests.
    
    GET /api/v1/integration/leave-requests
    """
    try:
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 50)), 100)
        offset = (page - 1) * per_page
        
        queryset = LeaveRequest.objects.select_related('user', 'approved_by').all()
        
        # Filters
        if user_sap := request.GET.get('user_sap'):
            queryset = queryset.filter(user__sap=user_sap)
        
        if status := request.GET.get('status'):
            queryset = queryset.filter(status=status.upper())
        
        if start_date := request.GET.get('start_date'):
            queryset = queryset.filter(start_date__gte=datetime.fromisoformat(start_date).date())
        
        total_count = queryset.count()
        leave_requests = queryset.order_by('-created_at')[offset:offset + per_page]
        
        data = [{
            'id': lr.id,
            'user': {
                'sap': lr.user.sap,
                'full_name': lr.user.full_name,
            },
            'leave_type': lr.leave_type,
            'start_date': lr.start_date.isoformat(),
            'end_date': lr.end_date.isoformat(),
            'days_requested': lr.days_requested,
            'status': lr.status,
            'reason': lr.reason,
            'approved_by': {
                'sap': lr.approved_by.sap,
                'full_name': lr.approved_by.full_name,
            } if lr.approved_by else None,
            'approved_at': lr.approved_at.isoformat() if lr.approved_at else None,
            'created_at': lr.created_at.isoformat(),
        } for lr in leave_requests]
        
        return JsonResponse({
            'data': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_count': total_count,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'error': 'server_error',
            'message': str(e)
        }, status=500)


# ====================
# Payroll Export Endpoint
# ====================

@csrf_exempt
@require_http_methods(["POST"])
@require_api_scope('payroll:export')
def api_export_payroll(request):
    """
    Export payroll data for a date range.
    
    POST /api/v1/integration/payroll/export
    Body: {
        "start_date": "2025-01-01",
        "end_date": "2025-01-31",
        "format": "csv|json",
        "unit_id": 123  // optional
    }
    """
    try:
        data = json.loads(request.body)
        start_date = datetime.fromisoformat(data['start_date']).date()
        end_date = datetime.fromisoformat(data['end_date']).date()
        export_format = data.get('format', 'json')
        unit_id = data.get('unit_id')
        
        # Get completed shifts in date range
        queryset = Shift.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            status__in=['COMPLETED', 'CONFIRMED']
        ).select_related('user', 'unit')
        
        if unit_id:
            queryset = queryset.filter(unit_id=unit_id)
        
        # Group by user
        from django.db.models import Sum
        payroll_data = queryset.values(
            'user__sap',
            'user__first_name',
            'user__last_name'
        ).annotate(
            total_hours=Sum('duration_hours'),
            overtime_hours=Sum('duration_hours', filter=Q(is_overtime=True)),
            regular_hours=Sum('duration_hours', filter=Q(is_overtime=False)),
            shift_count=Count('id')
        )
        
        results = list(payroll_data)
        
        if export_format == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                'SAP', 'First Name', 'Last Name', 'Total Hours',
                'Regular Hours', 'Overtime Hours', 'Shift Count'
            ])
            writer.writeheader()
            
            for item in results:
                writer.writerow({
                    'SAP': item['user__sap'],
                    'First Name': item['user__first_name'],
                    'Last Name': item['user__last_name'],
                    'Total Hours': item['total_hours'] or 0,
                    'Regular Hours': item['regular_hours'] or 0,
                    'Overtime Hours': item['overtime_hours'] or 0,
                    'Shift Count': item['shift_count'],
                })
            
            from django.http import HttpResponse
            response = HttpResponse(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="payroll_{start_date}_{end_date}.csv"'
            return response
        
        else:  # JSON
            return JsonResponse({
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                },
                'data': results,
                'summary': {
                    'total_staff': len(results),
                    'total_hours': sum(r['total_hours'] or 0 for r in results),
                    'total_overtime': sum(r['overtime_hours'] or 0 for r in results),
                }
            })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except KeyError as e:
        return JsonResponse({'error': f'Missing required field: {e}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ====================
# Webhook Management
# ====================

@csrf_exempt
@require_http_methods(["POST"])
@require_api_scope('webhooks:manage')
def api_create_webhook(request):
    """
    Create a new webhook endpoint.
    
    POST /api/v1/integration/webhooks
    Body: {
        "url": "https://example.com/webhook",
        "event_types": ["shift.created", "leave.approved"],
        "max_retries": 3
    }
    """
    try:
        data = json.loads(request.body)
        
        webhook = WebhookEndpoint.objects.create(
            client=request.api_client,
            url=data['url'],
            event_types=data.get('event_types', []),
            max_retries=data.get('max_retries', 3),
            retry_delay_seconds=data.get('retry_delay_seconds', 60),
        )
        
        # Generate secret
        secret = webhook.generate_secret()
        webhook.save()
        
        return JsonResponse({
            'data': {
                'id': webhook.id,
                'url': webhook.url,
                'event_types': webhook.event_types,
                'secret': secret,  # Only shown once
                'is_active': webhook.is_active,
                'created_at': webhook.created_at.isoformat(),
            }
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except KeyError as e:
        return JsonResponse({'error': f'Missing required field: {e}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ====================
# System Information
# ====================

@csrf_exempt
@require_http_methods(["GET"])
def api_get_info(request):
    """
    Get API information and client details.
    
    GET /api/v1/integration/info
    """
    try:
        client = request.api_client
        
        return JsonResponse({
            'api_version': 'v1',
            'client': {
                'id': client.client_id,
                'name': client.name,
                'type': client.get_client_type_display(),
                'organization': client.organization,
                'created_at': client.created_at.isoformat(),
            },
            'rate_limits': {
                'per_minute': client.rate_limit_per_minute,
                'per_hour': client.rate_limit_per_hour,
                'per_day': client.rate_limit_per_day,
            },
            'statistics': {
                'total_requests': client.total_requests,
                'successful_requests': client.successful_requests,
                'failed_requests': client.failed_requests,
                'success_rate': round(client.successful_requests / client.total_requests * 100, 2) if client.total_requests > 0 else 0,
                'last_used_at': client.last_used_at.isoformat() if client.last_used_at else None,
            },
            'documentation_url': '/api/v1/integration/docs',
        })
        
    except Exception as e:
        return JsonResponse({
            'error': 'server_error',
            'message': str(e)
        }, status=500)
