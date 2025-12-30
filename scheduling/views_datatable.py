"""
Enhanced data table views with advanced filtering, sorting, and bulk actions
Task 45: Data Table Enhancements
"""
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q

from .models import Shift, Staff, LeaveRequest, Unit, CareHome
from .data_table_utils import (
    AdvancedTableProcessor, DataTableExport,
    BulkActions, DataTableFilter, DataTableSort
)
import json


@login_required
@require_http_methods(["GET", "POST"])
def enhanced_shifts_table(request):
    """
    Enhanced shifts table with advanced filtering, sorting, and export
    """
    if request.method == "POST":
        # Handle bulk actions
        action = request.POST.get('action')
        selected_ids = BulkActions.get_selected_ids(request)
        
        if action and selected_ids:
            queryset = Shift.objects.filter(id__in=selected_ids)
            
            # Execute bulk action
            if action == 'delete':
                result = BulkActions.execute_bulk_action(queryset, 'delete')
            elif action == 'update_type':
                shift_type = request.POST.get('shift_type')
                result = BulkActions.execute_bulk_action(
                    queryset, 'update',
                    {'fields': {'shift_type_id': shift_type}}
                )
            elif action == 'assign_staff':
                staff_id = request.POST.get('staff_id')
                result = BulkActions.execute_bulk_action(
                    queryset, 'update',
                    {'fields': {'staff_id': staff_id}}
                )
            else:
                result = {'success': False, 'message': 'Unknown action'}
            
            return JsonResponse(result)
    
    # Base queryset
    queryset = Shift.objects.select_related('home', 'unit', 'staff', 'shift_type')
    
    # Apply user permissions
    if hasattr(request.user, 'staff_profile'):
        queryset = queryset.filter(home=request.user.staff_profile.home)
    
    # Check for export request
    export_format = request.GET.get('export')
    if export_format:
        # Apply filters and sorting before export
        filters = DataTableFilter.parse_request_filters(request)
        if filters:
            queryset = DataTableFilter.apply_filters(queryset, filters)
        
        sort_columns = DataTableSort.parse_request_sorting(request)
        if sort_columns:
            queryset = DataTableSort.apply_sorting(queryset, sort_columns)
        
        # Define export columns
        columns = [
            {'field': 'date', 'label': 'Date'},
            {'field': 'start_time', 'label': 'Start Time'},
            {'field': 'end_time', 'label': 'End Time'},
            {'field': 'home.name', 'label': 'Home'},
            {'field': 'unit.name', 'label': 'Unit'},
            {'field': 'shift_type.name', 'label': 'Shift Type'},
            {'field': 'staff.get_full_name', 'label': 'Staff'},
            {'field': 'staff.sap', 'label': 'SAP'},
        ]
        
        if export_format == 'csv':
            csv_content = DataTableExport.export_to_csv(queryset, columns, 'shifts_export.csv')
            response = HttpResponse(csv_content, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="shifts_{timezone.now().strftime("%Y%m%d")}.csv"'
            return response
        
        elif export_format == 'json':
            json_content = DataTableExport.export_to_json(queryset, columns)
            response = HttpResponse(json_content, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="shifts_{timezone.now().strftime("%Y%m%d")}.json"'
            return response
    
    # Process table request (filtering, sorting, pagination)
    default_sort = [{'field': 'date', 'direction': 'desc'}]
    result = AdvancedTableProcessor.process_request(queryset, request, default_sort)
    
    # Get filter options
    homes = CareHome.objects.all()
    units = Unit.objects.all()
    
    context = {
        'shifts': result['items'],
        'total': result['total'],
        'page': result['page'],
        'per_page': result['per_page'],
        'total_pages': result['total_pages'],
        'has_previous': result['has_previous'],
        'has_next': result['has_next'],
        'filters': result['filters'],
        'sort': result['sort'],
        'homes': homes,
        'units': units,
    }
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Convert shifts to dict for JSON serialization
        shifts_data = [{
            'id': shift.id,
            'date': shift.date.isoformat(),
            'start_time': shift.start_time.strftime('%H:%M'),
            'end_time': shift.end_time.strftime('%H:%M'),
            'home': shift.home.name,
            'unit': shift.unit.name if shift.unit else '',
            'shift_type': shift.shift_type.name if shift.shift_type else '',
            'staff': shift.staff.get_full_name() if shift.staff else 'Vacant',
            'staff_sap': shift.staff.sap if shift.staff else '',
        } for shift in result['items']]
        
        return JsonResponse({
            'data': shifts_data,
            'total': result['total'],
            'page': result['page'],
            'total_pages': result['total_pages'],
        })
    
    return render(request, 'scheduling/enhanced_shifts_table.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def enhanced_staff_table(request):
    """
    Enhanced staff table with advanced filtering, sorting, and export
    """
    if request.method == "POST":
        # Handle bulk actions
        action = request.POST.get('action')
        selected_ids = BulkActions.get_selected_ids(request)
        
        if action and selected_ids:
            queryset = Staff.objects.filter(id__in=selected_ids)
            
            # Execute bulk action
            if action == 'archive':
                result = BulkActions.execute_bulk_action(queryset, 'archive')
            elif action == 'activate':
                result = BulkActions.execute_bulk_action(
                    queryset, 'update',
                    {'fields': {'is_active': True}}
                )
            elif action == 'deactivate':
                result = BulkActions.execute_bulk_action(
                    queryset, 'update',
                    {'fields': {'is_active': False}}
                )
            else:
                result = {'success': False, 'message': 'Unknown action'}
            
            return JsonResponse(result)
    
    # Base queryset
    queryset = Staff.objects.select_related('user', 'home', 'primary_unit').prefetch_related('qualified_units')
    
    # Apply user permissions
    if hasattr(request.user, 'staff_profile') and not request.user.is_superuser:
        queryset = queryset.filter(home=request.user.staff_profile.home)
    
    # Check for export request
    export_format = request.GET.get('export')
    if export_format:
        # Apply filters and sorting before export
        filters = DataTableFilter.parse_request_filters(request)
        if filters:
            queryset = DataTableFilter.apply_filters(queryset, filters)
        
        sort_columns = DataTableSort.parse_request_sorting(request)
        if sort_columns:
            queryset = DataTableSort.apply_sorting(queryset, sort_columns)
        
        # Define export columns
        columns = [
            {'field': 'sap', 'label': 'SAP'},
            {'field': 'get_full_name', 'label': 'Name'},
            {'field': 'user.email', 'label': 'Email'},
            {'field': 'home.name', 'label': 'Home'},
            {'field': 'primary_unit.name', 'label': 'Primary Unit'},
            {'field': 'role', 'label': 'Role'},
            {'field': 'contract_hours', 'label': 'Contract Hours'},
            {'field': 'is_active', 'label': 'Active'},
        ]
        
        if export_format == 'csv':
            csv_content = DataTableExport.export_to_csv(queryset, columns)
            response = HttpResponse(csv_content, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="staff_{timezone.now().strftime("%Y%m%d")}.csv"'
            return response
        
        elif export_format == 'json':
            json_content = DataTableExport.export_to_json(queryset, columns)
            response = HttpResponse(json_content, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="staff_{timezone.now().strftime("%Y%m%d")}.json"'
            return response
    
    # Process table request
    default_sort = [{'field': 'sap', 'direction': 'asc'}]
    result = AdvancedTableProcessor.process_request(queryset, request, default_sort)
    
    # Get filter options
    homes = CareHome.objects.all()
    units = Unit.objects.all()
    
    context = {
        'staff_list': result['items'],
        'total': result['total'],
        'page': result['page'],
        'per_page': result['per_page'],
        'total_pages': result['total_pages'],
        'has_previous': result['has_previous'],
        'has_next': result['has_next'],
        'filters': result['filters'],
        'sort': result['sort'],
        'homes': homes,
        'units': units,
    }
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        staff_data = [{
            'id': staff.id,
            'sap': staff.sap,
            'name': staff.get_full_name(),
            'email': staff.user.email,
            'home': staff.home.name if staff.home else '',
            'primary_unit': staff.primary_unit.name if staff.primary_unit else '',
            'role': staff.role,
            'contract_hours': float(staff.contract_hours) if staff.contract_hours else 0,
            'is_active': staff.is_active,
        } for staff in result['items']]
        
        return JsonResponse({
            'data': staff_data,
            'total': result['total'],
            'page': result['page'],
            'total_pages': result['total_pages'],
        })
    
    return render(request, 'scheduling/enhanced_staff_table.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def enhanced_leave_table(request):
    """
    Enhanced leave requests table with advanced filtering, sorting, and bulk actions
    """
    if request.method == "POST":
        # Handle bulk actions
        action = request.POST.get('action')
        selected_ids = BulkActions.get_selected_ids(request)
        
        if action and selected_ids:
            queryset = LeaveRequest.objects.filter(id__in=selected_ids)
            
            # Execute bulk action
            if action == 'approve':
                result = BulkActions.execute_bulk_action(
                    queryset, 'update',
                    {'fields': {
                        'status': 'approved',
                        'approved_by': request.user,
                        'approval_date': timezone.now()
                    }}
                )
            elif action == 'reject':
                result = BulkActions.execute_bulk_action(
                    queryset, 'update',
                    {'fields': {
                        'status': 'rejected',
                        'approved_by': request.user,
                        'approval_date': timezone.now()
                    }}
                )
            elif action == 'cancel':
                result = BulkActions.execute_bulk_action(
                    queryset, 'update',
                    {'fields': {'status': 'cancelled'}}
                )
            else:
                result = {'success': False, 'message': 'Unknown action'}
            
            return JsonResponse(result)
    
    # Base queryset
    queryset = LeaveRequest.objects.select_related(
        'staff', 'staff__user', 'staff__home', 'approved_by', 'leave_type'
    )
    
    # Apply user permissions
    if hasattr(request.user, 'staff_profile') and not request.user.is_superuser:
        queryset = queryset.filter(staff__home=request.user.staff_profile.home)
    
    # Check for export request
    export_format = request.GET.get('export')
    if export_format:
        # Apply filters and sorting before export
        filters = DataTableFilter.parse_request_filters(request)
        if filters:
            queryset = DataTableFilter.apply_filters(queryset, filters)
        
        sort_columns = DataTableSort.parse_request_sorting(request)
        if sort_columns:
            queryset = DataTableSort.apply_sorting(queryset, sort_columns)
        
        # Define export columns
        columns = [
            {'field': 'staff.sap', 'label': 'SAP'},
            {'field': 'staff.get_full_name', 'label': 'Staff Name'},
            {'field': 'leave_type.name', 'label': 'Leave Type'},
            {'field': 'start_date', 'label': 'Start Date'},
            {'field': 'end_date', 'label': 'End Date'},
            {'field': 'status', 'label': 'Status'},
            {'field': 'approved_by.get_full_name', 'label': 'Approved By'},
            {'field': 'approval_date', 'label': 'Approval Date'},
        ]
        
        if export_format == 'csv':
            csv_content = DataTableExport.export_to_csv(queryset, columns)
            response = HttpResponse(csv_content, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="leave_requests_{timezone.now().strftime("%Y%m%d")}.csv"'
            return response
        
        elif export_format == 'json':
            json_content = DataTableExport.export_to_json(queryset, columns)
            response = HttpResponse(json_content, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="leave_requests_{timezone.now().strftime("%Y%m%d")}.json"'
            return response
    
    # Process table request
    default_sort = [{'field': 'start_date', 'direction': 'desc'}]
    result = AdvancedTableProcessor.process_request(queryset, request, default_sort)
    
    context = {
        'leave_requests': result['items'],
        'total': result['total'],
        'page': result['page'],
        'per_page': result['per_page'],
        'total_pages': result['total_pages'],
        'has_previous': result['has_previous'],
        'has_next': result['has_next'],
        'filters': result['filters'],
        'sort': result['sort'],
    }
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        leave_data = [{
            'id': leave.id,
            'staff_sap': leave.staff.sap,
            'staff_name': leave.staff.get_full_name(),
            'leave_type': leave.leave_type.name if leave.leave_type else '',
            'start_date': leave.start_date.isoformat(),
            'end_date': leave.end_date.isoformat(),
            'status': leave.status,
            'approved_by': leave.approved_by.get_full_name() if leave.approved_by else '',
            'approval_date': leave.approval_date.isoformat() if leave.approval_date else '',
        } for leave in result['items']]
        
        return JsonResponse({
            'data': leave_data,
            'total': result['total'],
            'page': result['page'],
            'total_pages': result['total_pages'],
        })
    
    return render(request, 'scheduling/enhanced_leave_table.html', context)
