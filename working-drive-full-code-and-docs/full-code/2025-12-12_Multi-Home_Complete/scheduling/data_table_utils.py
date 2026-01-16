"""
Enhanced data table utilities for advanced filtering, sorting, and export
Task 45: Data Table Enhancements
"""
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
import csv
import json
from io import StringIO


class DataTableFilter:
    """
    Advanced filtering for data tables with support for multiple filter types
    """
    
    FILTER_OPERATORS = {
        'equals': lambda field, value: Q(**{field: value}),
        'not_equals': lambda field, value: ~Q(**{field: value}),
        'contains': lambda field, value: Q(**{f'{field}__icontains': value}),
        'starts_with': lambda field, value: Q(**{f'{field}__istartswith': value}),
        'ends_with': lambda field, value: Q(**{f'{field}__iendswith': value}),
        'greater_than': lambda field, value: Q(**{f'{field}__gt': value}),
        'greater_than_or_equal': lambda field, value: Q(**{f'{field}__gte': value}),
        'less_than': lambda field, value: Q(**{f'{field}__lt': value}),
        'less_than_or_equal': lambda field, value: Q(**{f'{field}__lte': value}),
        'in': lambda field, value: Q(**{f'{field}__in': value.split(',')}),
        'between': lambda field, value: Q(**{f'{field}__range': value.split(',')}),
        'is_null': lambda field, value: Q(**{f'{field}__isnull': True}),
        'is_not_null': lambda field, value: Q(**{f'{field}__isnull': False}),
        'date_equals': lambda field, value: Q(**{f'{field}__date': value}),
        'date_range': lambda field, value: Q(**{f'{field}__date__range': value.split(',')}),
    }
    
    @staticmethod
    def apply_filters(queryset, filters):
        """
        Apply multiple filters to a queryset
        
        Args:
            queryset: Django QuerySet
            filters: List of dict with keys: field, operator, value
                Example: [
                    {'field': 'name', 'operator': 'contains', 'value': 'John'},
                    {'field': 'date', 'operator': 'date_range', 'value': '2025-01-01,2025-01-31'}
                ]
        
        Returns:
            Filtered QuerySet
        """
        q_objects = Q()
        
        for filter_item in filters:
            field = filter_item.get('field')
            operator = filter_item.get('operator', 'equals')
            value = filter_item.get('value')
            
            if field and value is not None:
                filter_func = DataTableFilter.FILTER_OPERATORS.get(operator)
                if filter_func:
                    q_objects &= filter_func(field, value)
        
        return queryset.filter(q_objects)
    
    @staticmethod
    def parse_request_filters(request):
        """
        Parse filters from request GET/POST parameters
        
        Expects parameters in format:
        - filter[0][field]=name
        - filter[0][operator]=contains
        - filter[0][value]=John
        """
        filters = []
        filter_data = request.GET.get('filters') or request.POST.get('filters')
        
        if filter_data:
            try:
                filters = json.loads(filter_data)
            except json.JSONDecodeError:
                pass
        
        return filters


class DataTableSort:
    """
    Advanced sorting for data tables with multi-column support
    """
    
    @staticmethod
    def apply_sorting(queryset, sort_columns):
        """
        Apply sorting to queryset
        
        Args:
            queryset: Django QuerySet
            sort_columns: List of dict with keys: field, direction
                Example: [
                    {'field': 'name', 'direction': 'asc'},
                    {'field': 'created_at', 'direction': 'desc'}
                ]
        
        Returns:
            Sorted QuerySet
        """
        order_by = []
        
        for sort_item in sort_columns:
            field = sort_item.get('field')
            direction = sort_item.get('direction', 'asc')
            
            if field:
                prefix = '-' if direction == 'desc' else ''
                order_by.append(f'{prefix}{field}')
        
        if order_by:
            return queryset.order_by(*order_by)
        
        return queryset
    
    @staticmethod
    def parse_request_sorting(request):
        """
        Parse sorting from request GET/POST parameters
        
        Expects parameters in format:
        - sort[0][field]=name
        - sort[0][direction]=asc
        """
        sort_columns = []
        sort_data = request.GET.get('sort') or request.POST.get('sort')
        
        if sort_data:
            try:
                sort_columns = json.loads(sort_data)
            except json.JSONDecodeError:
                pass
        
        return sort_columns


class DataTablePagination:
    """
    Pagination for data tables
    """
    
    @staticmethod
    def paginate(queryset, page=1, per_page=25):
        """
        Paginate queryset
        
        Args:
            queryset: Django QuerySet
            page: Page number (1-indexed)
            per_page: Items per page
        
        Returns:
            Dict with keys: items, total, page, per_page, total_pages
        """
        total = queryset.count()
        total_pages = (total + per_page - 1) // per_page
        
        start = (page - 1) * per_page
        end = start + per_page
        
        items = list(queryset[start:end])
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_previous': page > 1,
            'has_next': page < total_pages,
        }


class DataTableExport:
    """
    Export data tables to various formats
    """
    
    @staticmethod
    def export_to_csv(queryset, columns, filename='export.csv'):
        """
        Export queryset to CSV
        
        Args:
            queryset: Django QuerySet
            columns: List of dict with keys: field, label
                Example: [
                    {'field': 'name', 'label': 'Name'},
                    {'field': 'email', 'label': 'Email Address'}
                ]
            filename: Output filename
        
        Returns:
            CSV string content
        """
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        headers = [col['label'] for col in columns]
        writer.writerow(headers)
        
        # Write data rows
        for obj in queryset:
            row = []
            for col in columns:
                field = col['field']
                
                # Handle nested fields (e.g., 'user.email')
                value = obj
                for part in field.split('.'):
                    if hasattr(value, part):
                        value = getattr(value, part)
                    elif isinstance(value, dict):
                        value = value.get(part)
                    else:
                        value = ''
                        break
                
                # Handle callable fields
                if callable(value):
                    value = value()
                
                row.append(str(value) if value is not None else '')
            
            writer.writerow(row)
        
        return output.getvalue()
    
    @staticmethod
    def export_to_json(queryset, columns):
        """
        Export queryset to JSON
        
        Args:
            queryset: Django QuerySet
            columns: List of dict with keys: field, label
        
        Returns:
            JSON string
        """
        data = []
        
        for obj in queryset:
            item = {}
            for col in columns:
                field = col['field']
                label = col['label']
                
                # Handle nested fields
                value = obj
                for part in field.split('.'):
                    if hasattr(value, part):
                        value = getattr(value, part)
                    elif isinstance(value, dict):
                        value = value.get(part)
                    else:
                        value = None
                        break
                
                # Handle callable fields
                if callable(value):
                    value = value()
                
                # Convert to JSON-serializable format
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                
                item[label] = value
            
            data.append(item)
        
        return json.dumps(data, indent=2, default=str)


class BulkActions:
    """
    Bulk actions handler for data tables
    """
    
    @staticmethod
    def execute_bulk_action(queryset, action, params=None):
        """
        Execute a bulk action on selected items
        
        Args:
            queryset: Django QuerySet of selected items
            action: Action to perform (delete, update, archive, etc.)
            params: Additional parameters for the action
        
        Returns:
            Dict with keys: success, message, count
        """
        params = params or {}
        count = queryset.count()
        
        try:
            if action == 'delete':
                queryset.delete()
                return {
                    'success': True,
                    'message': f'Successfully deleted {count} item(s)',
                    'count': count
                }
            
            elif action == 'update':
                # Update specified fields
                update_fields = params.get('fields', {})
                queryset.update(**update_fields)
                return {
                    'success': True,
                    'message': f'Successfully updated {count} item(s)',
                    'count': count
                }
            
            elif action == 'archive':
                # Archive items (soft delete)
                queryset.update(is_archived=True, archived_at=timezone.now())
                return {
                    'success': True,
                    'message': f'Successfully archived {count} item(s)',
                    'count': count
                }
            
            elif action == 'restore':
                # Restore archived items
                queryset.update(is_archived=False, archived_at=None)
                return {
                    'success': True,
                    'message': f'Successfully restored {count} item(s)',
                    'count': count
                }
            
            else:
                return {
                    'success': False,
                    'message': f'Unknown action: {action}',
                    'count': 0
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error executing bulk action: {str(e)}',
                'count': 0
            }
    
    @staticmethod
    def get_selected_ids(request):
        """
        Get selected item IDs from request
        
        Expects parameter 'selected_ids' as comma-separated list or JSON array
        """
        selected_ids = request.POST.get('selected_ids', '')
        
        if selected_ids:
            try:
                # Try parsing as JSON array
                ids = json.loads(selected_ids)
            except json.JSONDecodeError:
                # Fall back to comma-separated string
                ids = [id.strip() for id in selected_ids.split(',') if id.strip()]
            
            return [int(id) for id in ids if str(id).isdigit()]
        
        return []


class AdvancedTableProcessor:
    """
    Combine all data table operations into a single processor
    """
    
    @staticmethod
    def process_request(queryset, request, default_sort=None):
        """
        Process a data table request with filtering, sorting, and pagination
        
        Args:
            queryset: Django QuerySet
            request: Django request object
            default_sort: Default sort columns if none specified
        
        Returns:
            Dict with processed data and metadata
        """
        # Apply filters
        filters = DataTableFilter.parse_request_filters(request)
        if filters:
            queryset = DataTableFilter.apply_filters(queryset, filters)
        
        # Apply sorting
        sort_columns = DataTableSort.parse_request_sorting(request)
        if not sort_columns and default_sort:
            sort_columns = default_sort
        if sort_columns:
            queryset = DataTableSort.apply_sorting(queryset, sort_columns)
        
        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 25))
        
        # Paginate
        result = DataTablePagination.paginate(queryset, page, per_page)
        
        # Add filter and sort info to result
        result['filters'] = filters
        result['sort'] = sort_columns
        
        return result
