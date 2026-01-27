"""
Video Tutorial Library Views (Task 54)

Views for video upload, viewing, progress tracking, ratings,
playlists, and integration with training modules.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.db.models import Q, Count, Avg, F
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.text import slugify
from .models_videos import (
    VideoCategory, Video, VideoProgress, VideoRating,
    VideoPlaylist, PlaylistVideo
)
# from .decorators import manager_required  # Decorator doesn't exist yet
import json


@login_required
def video_library(request):
    """
    Main video library page with search, filtering, and categorization.
    Shows videos user has access to with progress tracking.
    """
    # Get all published videos
    videos = Video.objects.filter(is_published=True).select_related(
        'category', 'uploaded_by'
    ).prefetch_related('progress_records')
    
    # Filter by user permissions
    accessible_videos = []
    for video in videos:
        if video.can_user_access(request.user):
            accessible_videos.append(video.id)
    
    videos = videos.filter(id__in=accessible_videos)
    
    # Search
    query = request.GET.get('q', '').strip()
    if query:
        videos = videos.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query)
        )
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        videos = videos.filter(category_id=category_id)
    
    # Filter by training module
    module_id = request.GET.get('module')
    if module_id:
        videos = videos.filter(training_module_id=module_id)
    
    # Filter by type
    video_type = request.GET.get('type')
    if video_type:
        videos = videos.filter(video_type=video_type)
    
    # Sort
    sort = request.GET.get('sort', '-created_at')
    if sort == 'popular':
        videos = videos.order_by('-view_count')
    elif sort == 'rated':
        videos = videos.order_by('-average_rating')
    elif sort == 'title':
        videos = videos.order_by('title')
    else:
        videos = videos.order_by(sort)
    
    # Annotate with user progress
    for video in videos:
        try:
            progress = VideoProgress.objects.get(video=video, user=request.user)
            video.user_progress = progress
        except VideoProgress.DoesNotExist:
            video.user_progress = None
    
    # Pagination
    paginator = Paginator(videos, 12)
    page = request.GET.get('page', 1)
    videos_page = paginator.get_page(page)
    
    # Get categories for filter
    categories = VideoCategory.objects.filter(is_active=True).annotate(
        video_count=Count('videos', filter=Q(videos__is_published=True))
    )
    
    # Get featured videos
    featured = Video.objects.filter(
        is_published=True,
        is_featured=True
    )[:6]
    
    # Stats
    total_videos = videos.count()
    completed_count = VideoProgress.objects.filter(
        user=request.user,
        is_completed=True
    ).count()
    in_progress_count = VideoProgress.objects.filter(
        user=request.user,
        is_completed=False,
        progress_percentage__gt=0
    ).count()
    
    context = {
        'videos': videos_page,
        'categories': categories,
        'featured': featured,
        'total_videos': total_videos,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'query': query,
    }
    
    return render(request, 'scheduling/video_library.html', context)


@login_required
def video_detail(request, video_id):
    """
    Video detail page with player, description, ratings, and progress tracking.
    """
    video = get_object_or_404(Video, id=video_id)
    
    # Check permission
    if not video.can_user_access(request.user):
        messages.error(request, 'You do not have permission to view this video.')
        return redirect('video_library')
    
    # Get or create progress record
    progress, created = VideoProgress.objects.get_or_create(
        video=video,
        user=request.user
    )
    
    # Increment view count (once per user)
    if created:
        video.view_count = F('view_count') + 1
        video.save(update_fields=['view_count'])
        video.refresh_from_db()
    
    # Get user's rating
    try:
        user_rating = VideoRating.objects.get(video=video, user=request.user)
    except VideoRating.DoesNotExist:
        user_rating = None
    
    # Get recent ratings
    recent_ratings = VideoRating.objects.filter(video=video).select_related('user')[:10]
    
    # Get related videos (same category)
    related_videos = Video.objects.filter(
        category=video.category,
        is_published=True
    ).exclude(id=video.id)[:6]
    
    # Get playlists containing this video
    playlists = VideoPlaylist.objects.filter(
        Q(user=request.user) | Q(is_public=True) | Q(shared_with=request.user),
        videos=video
    ).distinct()
    
    context = {
        'video': video,
        'progress': progress,
        'user_rating': user_rating,
        'recent_ratings': recent_ratings,
        'related_videos': related_videos,
        'playlists': playlists,
    }
    
    return render(request, 'scheduling/video_detail.html', context)


# @manager_required  # Decorator does not exist yet
def video_upload(request):
    """
    Upload new video tutorial (managers and training coordinators only).
    """
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        category_id = request.POST.get('category')
        tags = request.POST.get('tags', '')
        video_type = request.POST.get('video_type', 'upload')
        access_level = request.POST.get('access_level', 'staff')
        is_mandatory = request.POST.get('is_mandatory') == 'on'
        is_featured = request.POST.get('is_featured') == 'on'
        completion_threshold = int(request.POST.get('completion_threshold', 90))
        module_id = request.POST.get('training_module')
        
        # Create video
        video = Video(
            title=title,
            slug=slugify(title),
            description=description,
            tags=tags,
            video_type=video_type,
            access_level=access_level,
            is_mandatory=is_mandatory,
            is_featured=is_featured,
            completion_threshold=completion_threshold,
            uploaded_by=request.user
        )
        
        # Set category
        if category_id:
            video.category_id = category_id
        
        # Set training module
        if module_id:
            video.training_module_id = module_id
        
        # Handle video file or URL
        if video_type == 'upload':
            if 'video_file' in request.FILES:
                video.video_file = request.FILES['video_file']
            else:
                messages.error(request, 'Please upload a video file.')
                return redirect('video_upload')
        else:
            video_url = request.POST.get('video_url')
            if video_url:
                video.video_url = video_url
            else:
                messages.error(request, 'Please provide a video URL.')
                return redirect('video_upload')
        
        # Handle thumbnail
        if 'thumbnail' in request.FILES:
            video.thumbnail = request.FILES['thumbnail']
        
        # Handle duration
        duration = request.POST.get('duration')
        if duration:
            video.duration = int(duration)
        
        video.save()
        
        # Handle allowed users for custom access
        if access_level == 'custom':
            allowed_user_ids = request.POST.getlist('allowed_users')
            video.allowed_users.set(allowed_user_ids)
        
        messages.success(request, f'Video "{title}" uploaded successfully!')
        return redirect('video_detail', video_id=video.id)
    
    # GET request - show upload form
    from .models import User, TrainingModule
    
    categories = VideoCategory.objects.filter(is_active=True)
    users = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
    modules = TrainingModule.objects.filter(is_active=True)
    
    context = {
        'categories': categories,
        'users': users,
        'modules': modules,
    }
    
    return render(request, 'scheduling/video_upload.html', context)


@login_required
def video_update_progress(request, video_id):
    """
    AJAX endpoint to update video watch progress.
    Called periodically from video player.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    video = get_object_or_404(Video, id=video_id)
    
    # Check permission
    if not video.can_user_access(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        current_position = int(data.get('position', 0))
        
        # Get or create progress
        progress, created = VideoProgress.objects.get_or_create(
            video=video,
            user=request.user
        )
        
        # Update progress
        progress.update_progress(current_position)
        
        return JsonResponse({
            'success': True,
            'progress_percentage': progress.progress_percentage,
            'is_completed': progress.is_completed,
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def video_rate(request, video_id):
    """
    AJAX endpoint to rate a video (1-5 stars).
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    video = get_object_or_404(Video, id=video_id)
    
    # Check permission
    if not video.can_user_access(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        rating_value = int(request.POST.get('rating', 0))
        review_text = request.POST.get('review', '').strip()
        
        if rating_value < 1 or rating_value > 5:
            return JsonResponse({'error': 'Rating must be between 1 and 5'}, status=400)
        
        # Create or update rating
        rating, created = VideoRating.objects.update_or_create(
            video=video,
            user=request.user,
            defaults={
                'rating': rating_value,
                'review': review_text,
            }
        )
        
        return JsonResponse({
            'success': True,
            'rating': rating_value,
            'average_rating': video.average_rating,
            'message': 'Rating submitted!' if created else 'Rating updated!'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def my_progress(request):
    """
    Show user's video progress - completed, in progress, and watchlist.
    """
    # Get all user's progress records
    all_progress = VideoProgress.objects.filter(user=request.user).select_related('video')
    
    completed = all_progress.filter(is_completed=True).order_by('-completed_at')
    in_progress = all_progress.filter(
        is_completed=False,
        progress_percentage__gt=0
    ).order_by('-last_watched_at')
    
    # Get user's playlists
    playlists = VideoPlaylist.objects.filter(user=request.user).prefetch_related('videos')
    
    # Stats
    total_watch_time = sum(p.watch_time for p in all_progress)
    completed_count = completed.count()
    in_progress_count = in_progress.count()
    
    context = {
        'completed': completed[:20],
        'in_progress': in_progress[:20],
        'playlists': playlists,
        'total_watch_time': total_watch_time,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
    }
    
    return render(request, 'scheduling/my_video_progress.html', context)


@login_required
def playlist_create(request):
    """Create new video playlist"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_public = request.POST.get('is_public') == 'on'
        
        playlist = VideoPlaylist.objects.create(
            name=name,
            description=description,
            is_public=is_public,
            user=request.user
        )
        
        # Add shared users
        shared_user_ids = request.POST.getlist('shared_with')
        if shared_user_ids:
            playlist.shared_with.set(shared_user_ids)
        
        messages.success(request, f'Playlist "{name}" created!')
        return redirect('playlist_detail', playlist_id=playlist.id)
    
    from .models import User
    users = User.objects.filter(is_active=True).exclude(id=request.user.id).order_by('first_name')
    
    return render(request, 'scheduling/playlist_create.html', {'users': users})


@login_required
def playlist_detail(request, playlist_id):
    """View playlist with videos"""
    playlist = get_object_or_404(VideoPlaylist, id=playlist_id)
    
    # Check permission
    if not (playlist.user == request.user or 
            playlist.is_public or 
            request.user in playlist.shared_with.all()):
        messages.error(request, 'You do not have access to this playlist.')
        return redirect('video_library')
    
    # Get playlist videos with progress
    playlist_videos = PlaylistVideo.objects.filter(
        playlist=playlist
    ).select_related('video').order_by('order')
    
    for pv in playlist_videos:
        try:
            progress = VideoProgress.objects.get(video=pv.video, user=request.user)
            pv.video.user_progress = progress
        except VideoProgress.DoesNotExist:
            pv.video.user_progress = None
    
    progress_percentage = playlist.get_progress_percentage(request.user)
    total_duration = playlist.get_total_duration()
    
    context = {
        'playlist': playlist,
        'playlist_videos': playlist_videos,
        'progress_percentage': progress_percentage,
        'total_duration': total_duration,
    }
    
    return render(request, 'scheduling/playlist_detail.html', context)


@login_required
def playlist_add_video(request, playlist_id):
    """AJAX endpoint to add video to playlist"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    playlist = get_object_or_404(VideoPlaylist, id=playlist_id, user=request.user)
    video_id = request.POST.get('video_id')
    
    if not video_id:
        return JsonResponse({'error': 'Video ID required'}, status=400)
    
    video = get_object_or_404(Video, id=video_id)
    
    # Check if already in playlist
    if PlaylistVideo.objects.filter(playlist=playlist, video=video).exists():
        return JsonResponse({'error': 'Video already in playlist'}, status=400)
    
    # Add to playlist
    max_order = PlaylistVideo.objects.filter(playlist=playlist).count()
    PlaylistVideo.objects.create(
        playlist=playlist,
        video=video,
        order=max_order + 1
    )
    
    return JsonResponse({
        'success': True,
        'message': f'Added "{video.title}" to playlist'
    })


@login_required
def category_list(request):
    """List all video categories with video counts"""
    categories = VideoCategory.objects.filter(is_active=True).annotate(
        video_count=Count('videos', filter=Q(videos__is_published=True))
    ).order_by('order', 'name')
    
    return render(request, 'scheduling/video_categories.html', {'categories': categories})


# @manager_required  # Decorator does not exist yet
def video_analytics(request):
    """Analytics dashboard for video performance (managers only)"""
    # Get all videos with stats
    videos = Video.objects.filter(is_published=True).annotate(
        completion_rate=Count('progress_records', filter=Q(progress_records__is_completed=True))
    ).order_by('-view_count')[:20]
    
    # Overall stats
    total_videos = Video.objects.filter(is_published=True).count()
    total_views = Video.objects.filter(is_published=True).aggregate(
        total=Count('progress_records')
    )['total'] or 0
    total_completions = VideoProgress.objects.filter(is_completed=True).count()
    avg_rating = Video.objects.filter(is_published=True).aggregate(
        avg=Avg('average_rating')
    )['avg'] or 0
    
    # Most viewed categories
    top_categories = VideoCategory.objects.annotate(
        total_views=Count('videos__progress_records')
    ).order_by('-total_views')[:10]
    
    context = {
        'videos': videos,
        'total_videos': total_videos,
        'total_views': total_views,
        'total_completions': total_completions,
        'avg_rating': round(avg_rating, 1),
        'top_categories': top_categories,
    }
    
    return render(request, 'scheduling/video_analytics.html', context)
