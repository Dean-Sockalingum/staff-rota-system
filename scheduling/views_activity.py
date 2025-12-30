"""
Recent Activity Feed Views - Task 55
Enhanced activity feed with real-time updates, widgets, and dashboard integration
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from .models_activity import RecentActivity, ActivityFeedWidget
from .decorators import manager_required


@login_required
def recent_activity_feed(request):
    """Main activity feed page with filters and real-time updates"""
    care_home = getattr(request.user, 'care_home', None)
    
    # Get filter parameters
    category = request.GET.get('category', '')
    priority = request.GET.get('priority', '')
    activity_type = request.GET.get('type', '')
    days = int(request.GET.get('days', 7))
    show_read = request.GET.get('show_read', 'true') == 'true'
    
    # Build queryset
    activities = RecentActivity.objects.filter(is_archived=False)
    
    # Apply filters
    if category:
        activities = activities.filter(category=category)
    
    if priority:
        activities = activities.filter(priority=priority)
    
    if activity_type:
        activities = activities.filter(activity_type=activity_type)
    
    if not show_read:
        activities = activities.filter(is_read=False)
    
    # Date filter
    if days > 0:
        since = timezone.now() - timedelta(days=days)
        activities = activities.filter(created_at__gte=since)
    
    # Care home filter (if applicable)
    if care_home and not request.user.is_superuser:
        activities = activities.filter(Q(care_home=care_home) | Q(care_home__isnull=True))
    
    # User relevance filter
    if not request.user.has_perm('scheduling.view_all_activities'):
        activities = activities.filter(
            Q(user=request.user) | 
            Q(target_user=request.user) |
            Q(care_home=care_home)
        )
    
    # Pagination
    page_size = 50
    activities = activities[:page_size]
    
    # Get statistics
    unread_count = RecentActivity.get_unread_count(user=request.user, care_home=care_home)
    
    # Category counts
    category_counts = RecentActivity.objects.filter(
        is_archived=False,
        created_at__gte=timezone.now() - timedelta(days=days)
    ).values('category').annotate(count=Count('id')).order_by('-count')
    
    context = {
        'activities': activities,
        'unread_count': unread_count,
        'category_counts': category_counts,
        'selected_category': category,
        'selected_priority': priority,
        'selected_type': activity_type,
        'selected_days': days,
        'show_read': show_read,
        'activity_categories': RecentActivity.ACTIVITY_CATEGORIES,
        'activity_types': RecentActivity.ACTIVITY_TYPES,
        'priority_levels': RecentActivity.PRIORITY_LEVELS,
    }
    
    return render(request, 'scheduling/recent_activity_feed.html', context)


@login_required
@require_http_methods(['GET'])
def activity_feed_api(request):
    """AJAX endpoint for real-time activity feed updates"""
    care_home = getattr(request.user, 'care_home', None)
    
    # Get parameters
    since_id = request.GET.get('since_id', None)
    category = request.GET.get('category', '')
    limit = int(request.GET.get('limit', 20))
    
    # Build queryset
    activities = RecentActivity.objects.filter(is_archived=False)
    
    # Get only newer activities
    if since_id:
        try:
            since_activity = RecentActivity.objects.get(id=since_id)
            activities = activities.filter(created_at__gt=since_activity.created_at)
        except RecentActivity.DoesNotExist:
            pass
    
    # Apply filters
    if category:
        activities = activities.filter(category=category)
    
    # Care home filter
    if care_home and not request.user.is_superuser:
        activities = activities.filter(Q(care_home=care_home) | Q(care_home__isnull=True))
    
    # User relevance
    if not request.user.has_perm('scheduling.view_all_activities'):
        activities = activities.filter(
            Q(user=request.user) | 
            Q(target_user=request.user) |
            Q(care_home=care_home)
        )
    
    # Limit results
    activities = activities[:limit]
    
    # Serialize activities
    activities_data = []
    for activity in activities:
        activities_data.append({
            'id': activity.id,
            'category': activity.category,
            'activity_type': activity.activity_type,
            'title': activity.title,
            'description': activity.description,
            'user': activity.user.get_full_name() if activity.user else 'System',
            'user_id': activity.user.id if activity.user else None,
            'priority': activity.priority,
            'icon': activity.get_icon_class(),
            'color': activity.get_color_class(),
            'is_read': activity.is_read,
            'is_pinned': activity.is_pinned,
            'created_at': activity.created_at.isoformat(),
            'metadata': activity.metadata,
        })
    
    return JsonResponse({
        'success': True,
        'activities': activities_data,
        'count': len(activities_data),
        'unread_count': RecentActivity.get_unread_count(user=request.user, care_home=care_home),
    })


@login_required
@require_http_methods(['POST'])
def mark_activity_read(request, activity_id):
    """Mark a single activity as read"""
    activity = get_object_or_404(RecentActivity, id=activity_id)
    
    # Check permission
    care_home = getattr(request.user, 'care_home', None)
    if not (activity.user == request.user or 
            activity.target_user == request.user or
            activity.care_home == care_home or
            request.user.is_superuser):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    activity.mark_as_read()
    
    return JsonResponse({
        'success': True,
        'unread_count': RecentActivity.get_unread_count(user=request.user, care_home=care_home),
    })


@login_required
@require_http_methods(['POST'])
def mark_all_read(request):
    """Mark all activities as read for current user"""
    care_home = getattr(request.user, 'care_home', None)
    
    activities = RecentActivity.objects.filter(
        is_archived=False,
        is_read=False
    )
    
    # Filter to user's activities
    activities = activities.filter(
        Q(user=request.user) | 
        Q(target_user=request.user) |
        Q(care_home=care_home)
    )
    
    count = activities.update(is_read=True)
    
    return JsonResponse({
        'success': True,
        'marked_count': count,
        'unread_count': 0,
    })


@login_required
@require_http_methods(['POST'])
def archive_activity(request, activity_id):
    """Archive a single activity"""
    activity = get_object_or_404(RecentActivity, id=activity_id)
    
    # Check permission (only user or managers can archive)
    care_home = getattr(request.user, 'care_home', None)
    if not (activity.user == request.user or 
            activity.target_user == request.user or
            request.user.has_perm('scheduling.delete_recentactivity')):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    activity.archive()
    
    return JsonResponse({'success': True})


@login_required
def activity_dashboard_widget(request):
    """Render activity feed widget for dashboard embedding"""
    care_home = getattr(request.user, 'care_home', None)
    
    # Get widget configuration (or use defaults)
    widget_id = request.GET.get('widget_id', None)
    
    if widget_id:
        try:
            widget = ActivityFeedWidget.objects.get(id=widget_id, user=request.user, is_active=True)
            activities = widget.get_activities()
        except ActivityFeedWidget.DoesNotExist:
            widget = None
            activities = RecentActivity.get_recent(user=request.user, care_home=care_home, limit=10)
    else:
        widget = None
        activities = RecentActivity.get_recent(user=request.user, care_home=care_home, limit=10)
    
    context = {
        'widget': widget,
        'activities': activities,
        'unread_count': RecentActivity.get_unread_count(user=request.user, care_home=care_home),
    }
    
    return render(request, 'scheduling/widgets/activity_feed.html', context)


@login_required
@manager_required
def manage_activity_widgets(request):
    """Manage activity feed widgets"""
    care_home = getattr(request.user, 'care_home', None)
    
    if request.method == 'POST':
        # Create new widget
        widget = ActivityFeedWidget.objects.create(
            name=request.POST.get('name', 'Activity Feed'),
            widget_type=request.POST.get('widget_type', 'recent'),
            size=request.POST.get('size', 'medium'),
            filter_category=request.POST.get('filter_category', ''),
            filter_priority=request.POST.get('filter_priority', ''),
            days_to_show=int(request.POST.get('days_to_show', 7)),
            show_read=request.POST.get('show_read', 'true') == 'true',
            show_icons=request.POST.get('show_icons', 'true') == 'true',
            show_timestamps=request.POST.get('show_timestamps', 'true') == 'true',
            show_user_avatars=request.POST.get('show_user_avatars', 'true') == 'true',
            auto_refresh=request.POST.get('auto_refresh', 'true') == 'true',
            refresh_interval=int(request.POST.get('refresh_interval', 30)),
            user=request.user,
            care_home=care_home,
        )
        
        return redirect('manage_activity_widgets')
    
    widgets = ActivityFeedWidget.objects.filter(user=request.user, is_active=True)
    
    context = {
        'widgets': widgets,
        'widget_types': ActivityFeedWidget.WIDGET_TYPES,
        'size_choices': ActivityFeedWidget.SIZE_CHOICES,
        'activity_categories': RecentActivity.ACTIVITY_CATEGORIES,
        'priority_levels': RecentActivity.PRIORITY_LEVELS,
    }
    
    return render(request, 'scheduling/manage_activity_widgets.html', context)


@login_required
@require_http_methods(['POST'])
def delete_activity_widget(request, widget_id):
    """Delete an activity widget"""
    widget = get_object_or_404(ActivityFeedWidget, id=widget_id, user=request.user)
    widget.delete()
    
    return JsonResponse({'success': True})


@login_required
@require_http_methods(['POST'])
def toggle_activity_pin(request, activity_id):
    """Pin/unpin an activity"""
    activity = get_object_or_404(RecentActivity, id=activity_id)
    
    # Check permission
    care_home = getattr(request.user, 'care_home', None)
    if not (activity.user == request.user or 
            activity.target_user == request.user or
            request.user.has_perm('scheduling.change_recentactivity')):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    activity.is_pinned = not activity.is_pinned
    activity.save(update_fields=['is_pinned'])
    
    return JsonResponse({
        'success': True,
        'is_pinned': activity.is_pinned,
    })


@login_required
def activity_statistics(request):
    """Activity feed statistics and analytics"""
    care_home = getattr(request.user, 'care_home', None)
    days = int(request.GET.get('days', 30))
    
    since = timezone.now() - timedelta(days=days)
    
    # Base queryset
    activities = RecentActivity.objects.filter(
        is_archived=False,
        created_at__gte=since
    )
    
    if care_home and not request.user.is_superuser:
        activities = activities.filter(Q(care_home=care_home) | Q(care_home__isnull=True))
    
    # Statistics
    total_activities = activities.count()
    unread_count = activities.filter(is_read=False).count()
    
    # Category breakdown
    category_stats = activities.values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Priority breakdown
    priority_stats = activities.values('priority').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Daily activity trend
    from django.db.models.functions import TruncDate
    daily_trend = activities.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Most active users
    active_users = activities.exclude(user__isnull=True).values(
        'user__id', 'user__first_name', 'user__last_name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    context = {
        'total_activities': total_activities,
        'unread_count': unread_count,
        'read_percentage': round((total_activities - unread_count) / total_activities * 100, 1) if total_activities > 0 else 0,
        'category_stats': category_stats,
        'priority_stats': priority_stats,
        'daily_trend': list(daily_trend),
        'active_users': active_users,
        'days': days,
    }
    
    return render(request, 'scheduling/activity_statistics.html', context)


# Helper function to create activity (use throughout the application)
def log_activity(category, activity_type, title, description='', user=None, 
                target_user=None, care_home=None, priority='normal', metadata=None, **kwargs):
    """
    Helper function to log activities throughout the application
    
    Usage:
        from scheduling.views_activity import log_activity
        
        log_activity(
            category='shift',
            activity_type='shift_created',
            title='New shift created',
            description=f'Shift for {shift.date} at {shift.care_home}',
            user=request.user,
            care_home=shift.care_home,
            priority='normal',
            metadata={'shift_id': shift.id}
        )
    """
    return RecentActivity.create_activity(
        category=category,
        activity_type=activity_type,
        title=title,
        description=description,
        user=user,
        target_user=target_user,
        care_home=care_home,
        priority=priority,
        metadata=metadata or {},
        **kwargs
    )
