"""
Task 49: Advanced Search Views
Full-text search with Elasticsearch, autocomplete, and faceted filtering
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.db import models
from elasticsearch_dsl import Q as ES_Q, Search
from elasticsearch_dsl.query import MultiMatch

from .documents import UserDocument, ShiftDocument, LeaveRequestDocument, CareHomeDocument
from .models import User, Shift, LeaveRequest, CareHome, Role


@login_required
def global_search(request):
    """
    Global search across all indexed models
    Features: full-text search, highlighting, pagination, faceted filtering
    """
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')  # all, staff, shifts, leave, homes
    page = int(request.GET.get('page', 1))
    per_page = settings.SEARCH_RESULTS_PER_PAGE
    
    context = {
        'query': query,
        'search_type': search_type,
        'page': page,
    }
    
    if not query:
        return render(request, 'scheduling/search_results.html', context)
    
    # Track search analytics (if enabled)
    if settings.SEARCH_ANALYTICS_ENABLED:
        _track_search_query(query, request.user)
    
    results = {}
    
    # Search staff
    if search_type in ('all', 'staff'):
        staff_results = _search_staff(query, page if search_type == 'staff' else 1, per_page)
        results['staff'] = staff_results
    
    # Search shifts
    if search_type in ('all', 'shifts'):
        shift_results = _search_shifts(query, page if search_type == 'shifts' else 1, per_page)
        results['shifts'] = shift_results
    
    # Search leave requests
    if search_type in ('all', 'leave'):
        leave_results = _search_leave(query, page if search_type == 'leave' else 1, per_page)
        results['leave'] = leave_results
    
    # Search care homes
    if search_type in ('all', 'homes'):
        home_results = _search_care_homes(query, page if search_type == 'homes' else 1, per_page)
        results['homes'] = home_results
    
    context['results'] = results
    context['total_results'] = sum(r.get('total', 0) for r in results.values())
    
    return render(request, 'scheduling/search_results.html', context)


@login_required
def autocomplete(request):
    """
    Autocomplete API endpoint for search suggestions
    Returns: JSON array of suggestions
    """
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')
    
    if len(query) < settings.SEARCH_AUTOCOMPLETE_MIN_LENGTH:
        return JsonResponse({'suggestions': []})
    
    suggestions = []
    
    # Staff autocomplete
    if search_type in ('all', 'staff'):
        staff_search = UserDocument.search()
        staff_search = staff_search.query(
            'multi_match',
            query=query,
            fields=['first_name', 'last_name', 'sap', 'full_name'],
            type='bool_prefix',
            fuzziness='AUTO'
        )[:5]
        
        for hit in staff_search.execute():
            suggestions.append({
                'type': 'staff',
                'label': f"{hit.full_name} ({hit.sap})",
                'value': hit.sap,
                'url': f'/staff/{hit.sap}/'
            })
    
    # Care home autocomplete
    if search_type in ('all', 'homes'):
        home_search = CareHomeDocument.search()
        home_search = home_search.query(
            'multi_match',
            query=query,
            fields=['name', 'location_address'],
            type='bool_prefix',
            fuzziness='AUTO'
        )[:5]
        
        for hit in home_search.execute():
            suggestions.append({
                'type': 'home',
                'label': hit.name,
                'value': hit.name,
                'url': f'/care-home/{hit.id}/'
            })
    
    return JsonResponse({'suggestions': suggestions})


@login_required
def advanced_search(request):
    """
    Advanced search with faceted filtering
    Filters: date range, role, care home, status
    """
    query = request.GET.get('q', '').strip()
    
    # Filter parameters
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    role_id = request.GET.get('role', '')
    care_home_id = request.GET.get('care_home', '')
    status = request.GET.get('status', '')
    
    page = int(request.GET.get('page', 1))
    per_page = settings.SEARCH_RESULTS_PER_PAGE
    
    # Build Elasticsearch query with filters
    results = {}
    
    # Advanced staff search
    if query or role_id or care_home_id:
        staff_search = UserDocument.search()
        
        if query:
            staff_search = staff_search.query(
                'multi_match',
                query=query,
                fields=['first_name^2', 'last_name^2', 'sap^3', 'email', 'full_name^2'],
                fuzziness='AUTO'
            )
        
        if role_id:
            staff_search = staff_search.filter('term', **{'role.id': role_id})
        
        if care_home_id:
            staff_search = staff_search.filter('term', **{'unit.care_home.id': care_home_id})
        
        # Pagination
        start = (page - 1) * per_page
        staff_search = staff_search[start:start + per_page]
        
        # Highlighting
        if settings.SEARCH_HIGHLIGHT_ENABLED and query:
            staff_search = staff_search.highlight('first_name', 'last_name', 'email')
        
        response = staff_search.execute()
        
        results['staff'] = {
            'hits': [_format_staff_hit(hit) for hit in response],
            'total': response.hits.total.value,
            'page': page,
            'per_page': per_page,
        }
    
    # Advanced shift search
    if query or start_date or end_date or care_home_id:
        shift_search = ShiftDocument.search()
        
        if query:
            shift_search = shift_search.query(
                'multi_match',
                query=query,
                fields=['assigned_to_name', 'assigned_to_sap', 'care_home_name', 'notes'],
                fuzziness='AUTO'
            )
        
        if start_date:
            shift_search = shift_search.filter('range', date={'gte': start_date})
        
        if end_date:
            shift_search = shift_search.filter('range', date={'lte': end_date})
        
        if care_home_id:
            shift_search = shift_search.filter('term', **{'care_home.id': care_home_id})
        
        # Pagination
        start = (page - 1) * per_page
        shift_search = shift_search[start:start + per_page]
        
        # Highlighting
        if settings.SEARCH_HIGHLIGHT_ENABLED and query:
            shift_search = shift_search.highlight('assigned_to_name', 'notes')
        
        response = shift_search.execute()
        
        results['shifts'] = {
            'hits': [_format_shift_hit(hit) for hit in response],
            'total': response.hits.total.value,
            'page': page,
            'per_page': per_page,
        }
    
    # Get facets for filters
    facets = {
        'roles': Role.objects.all().values('id', 'name'),
        'care_homes': CareHome.objects.all().values('id', 'name'),
    }
    
    context = {
        'query': query,
        'results': results,
        'facets': facets,
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'role_id': role_id,
            'care_home_id': care_home_id,
            'status': status,
        },
        'page': page,
    }
    
    return render(request, 'scheduling/advanced_search.html', context)


# ===== Helper Functions =====

def _search_staff(query, page, per_page):
    """Search staff with highlighting"""
    search = UserDocument.search()
    search = search.query(
        'multi_match',
        query=query,
        fields=['first_name^2', 'last_name^2', 'sap^3', 'email', 'full_name^2', 'role_name', 'care_home_name'],
        fuzziness='AUTO'
    )
    
    # Pagination
    start = (page - 1) * per_page
    search = search[start:start + per_page]
    
    # Highlighting
    if settings.SEARCH_HIGHLIGHT_ENABLED:
        search = search.highlight('first_name', 'last_name', 'email', 'full_name')
    
    response = search.execute()
    
    return {
        'hits': [_format_staff_hit(hit) for hit in response],
        'total': response.hits.total.value,
        'page': page,
        'per_page': per_page,
    }


def _search_shifts(query, page, per_page):
    """Search shifts with highlighting"""
    search = ShiftDocument.search()
    search = search.query(
        'multi_match',
        query=query,
        fields=['assigned_to_name^2', 'assigned_to_sap^3', 'care_home_name^2', 'shift_type_display', 'notes'],
        fuzziness='AUTO'
    )
    
    # Pagination
    start = (page - 1) * per_page
    search = search[start:start + per_page]
    
    # Highlighting
    if settings.SEARCH_HIGHLIGHT_ENABLED:
        search = search.highlight('assigned_to_name', 'care_home_name', 'notes')
    
    response = search.execute()
    
    return {
        'hits': [_format_shift_hit(hit) for hit in response],
        'total': response.hits.total.value,
        'page': page,
        'per_page': per_page,
    }


def _search_leave(query, page, per_page):
    """Search leave requests with highlighting"""
    search = LeaveRequestDocument.search()
    search = search.query(
        'multi_match',
        query=query,
        fields=['staff_name^2', 'staff_sap^3', 'reason', 'notes', 'approval_status'],
        fuzziness='AUTO'
    )
    
    # Pagination
    start = (page - 1) * per_page
    search = search[start:start + per_page]
    
    # Highlighting
    if settings.SEARCH_HIGHLIGHT_ENABLED:
        search = search.highlight('staff_name', 'reason', 'notes')
    
    response = search.execute()
    
    return {
        'hits': [_format_leave_hit(hit) for hit in response],
        'total': response.hits.total.value,
        'page': page,
        'per_page': per_page,
    }


def _search_care_homes(query, page, per_page):
    """Search care homes with highlighting"""
    search = CareHomeDocument.search()
    search = search.query(
        'multi_match',
        query=query,
        fields=['name^3', 'location_address', 'postcode', 'full_address'],
        fuzziness='AUTO'
    )
    
    # Pagination
    start = (page - 1) * per_page
    search = search[start:start + per_page]
    
    # Highlighting
    if settings.SEARCH_HIGHLIGHT_ENABLED:
        search = search.highlight('name', 'location_address', 'postcode')
    
    response = search.execute()
    
    return {
        'hits': [_format_care_home_hit(hit) for hit in response],
        'total': response.hits.total.value,
        'page': page,
        'per_page': per_page,
    }


def _format_staff_hit(hit):
    """Format staff search result"""
    return {
        'sap': hit.sap,
        'name': hit.full_name if hasattr(hit, 'full_name') else f"{hit.first_name} {hit.last_name}",
        'email': hit.email,
        'role': hit.role_name if hasattr(hit, 'role_name') else '',
        'care_home': hit.care_home_name if hasattr(hit, 'care_home_name') else '',
        'highlight': hit.meta.highlight.to_dict() if hasattr(hit.meta, 'highlight') else {},
    }


def _format_shift_hit(hit):
    """Format shift search result"""
    return {
        'id': hit.id,
        'date': hit.date,
        'start_time': hit.start_time,
        'end_time': hit.end_time,
        'shift_type': hit.shift_type_display if hasattr(hit, 'shift_type_display') else hit.shift_type,
        'assigned_to': hit.assigned_to_name if hasattr(hit, 'assigned_to_name') else '',
        'care_home': hit.care_home_name if hasattr(hit, 'care_home_name') else '',
        'highlight': hit.meta.highlight.to_dict() if hasattr(hit.meta, 'highlight') else {},
    }


def _format_leave_hit(hit):
    """Format leave request search result"""
    return {
        'id': hit.id,
        'staff_name': hit.staff_name if hasattr(hit, 'staff_name') else '',
        'start_date': hit.start_date,
        'end_date': hit.end_date,
        'reason': hit.reason,
        'status': hit.approval_status if hasattr(hit, 'approval_status') else 'Pending',
        'highlight': hit.meta.highlight.to_dict() if hasattr(hit.meta, 'highlight') else {},
    }


def _format_care_home_hit(hit):
    """Format care home search result"""
    return {
        'id': hit.meta.id,
        'name': hit.name,
        'address': hit.full_address if hasattr(hit, 'full_address') else hit.location_address,
        'phone': hit.main_phone if hasattr(hit, 'main_phone') else '',
        'email': hit.main_email if hasattr(hit, 'main_email') else '',
        'highlight': hit.meta.highlight.to_dict() if hasattr(hit.meta, 'highlight') else {},
    }


def _track_search_query(query, user):
    """
    Track search query for analytics
    Store: query, user, timestamp, result count
    """
    from .models import SearchAnalytics
    
    try:
        SearchAnalytics.objects.create(
            query=query,
            user=user,
        )
    except Exception:
        # Don't fail search if analytics fails
        pass
