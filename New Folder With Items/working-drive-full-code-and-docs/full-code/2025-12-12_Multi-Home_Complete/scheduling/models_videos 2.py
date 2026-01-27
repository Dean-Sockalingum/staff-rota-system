"""
Video Tutorial Library Models (Task 54)

Models for managing video tutorials with upload, categorization,
progress tracking, and integration with training modules.
"""

from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
import os


def video_upload_path(instance, filename):
    """Generate upload path for video files: videos/{category}/{year}/{month}/{filename}"""
    category = instance.category.slug if instance.category else 'uncategorized'
    now = timezone.now()
    return f'videos/{category}/{now.year}/{now.month:02d}/{filename}'


def thumbnail_upload_path(instance, filename):
    """Generate upload path for video thumbnails"""
    category = instance.category.slug if instance.category else 'uncategorized'
    now = timezone.now()
    return f'videos/thumbnails/{category}/{now.year}/{now.month:02d}/{filename}'


class VideoCategory(models.Model):
    """
    Categories for organizing video tutorials.
    Supports hierarchical structure with parent-child relationships.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='subcategories'
    )
    icon = models.CharField(
        max_length=50,
        default='fa-folder',
        help_text='FontAwesome icon class (e.g., fa-folder, fa-video)'
    )
    color = models.CharField(
        max_length=7,
        default='#007bff',
        help_text='Hex color code for category badge'
    )
    order = models.IntegerField(default=0, help_text='Display order (lower numbers first)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Video Categories'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['parent', 'order']),
            models.Index(fields=['is_active', 'order']),
        ]
    
    def __str__(self):
        return self.get_full_path()
    
    def get_full_path(self):
        """Get full category path (e.g., 'Training > Safety > Fire Safety')"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name
    
    def get_video_count(self):
        """Get total number of videos in this category and subcategories"""
        count = self.videos.filter(is_published=True).count()
        for subcategory in self.subcategories.all():
            count += subcategory.get_video_count()
        return count


class Video(models.Model):
    """
    Main video tutorial model with file storage, metadata, and permissions.
    Supports both uploaded videos and external links (YouTube, Vimeo).
    """
    VIDEO_TYPE_CHOICES = [
        ('upload', 'Uploaded Video'),
        ('youtube', 'YouTube Video'),
        ('vimeo', 'Vimeo Video'),
        ('external', 'External Link'),
    ]
    
    ACCESS_LEVEL_CHOICES = [
        ('public', 'Public - All users'),
        ('staff', 'Staff - All authenticated staff'),
        ('managers', 'Managers - Managers only'),
        ('trainers', 'Trainers - Training coordinators only'),
        ('custom', 'Custom - Specific users/roles'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        VideoCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='videos'
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text='Comma-separated tags for search and filtering'
    )
    
    # Video Source
    video_type = models.CharField(
        max_length=20,
        choices=VIDEO_TYPE_CHOICES,
        default='upload'
    )
    video_file = models.FileField(
        upload_to=video_upload_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'ogg', 'mov', 'avi'])],
        help_text='Upload video file (MP4, WebM, OGG, MOV, AVI)'
    )
    video_url = models.URLField(
        max_length=500,
        blank=True,
        help_text='External video URL (YouTube, Vimeo, etc.)'
    )
    
    # Thumbnail
    thumbnail = models.ImageField(
        upload_to=thumbnail_upload_path,
        null=True,
        blank=True,
        help_text='Custom thumbnail image (auto-generated if not provided)'
    )
    
    # Metadata
    duration = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text='Video duration in seconds'
    )
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        help_text='File size in bytes (for uploaded videos)'
    )
    
    # Access Control
    access_level = models.CharField(
        max_length=20,
        choices=ACCESS_LEVEL_CHOICES,
        default='staff'
    )
    allowed_users = models.ManyToManyField(
        'User',
        blank=True,
        related_name='accessible_videos',
        help_text='Users with access to this video (for custom access level)'
    )
    allowed_roles = models.JSONField(
        default=list,
        blank=True,
        help_text='Roles with access to this video (for custom access level)'
    )
    
    # Training Integration
    training_module = models.ForeignKey(
        'TrainingCourse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tutorial_videos',
        help_text='Link to training course for integration'
    )
    is_mandatory = models.BooleanField(
        default=False,
        help_text='Is this video mandatory for completion?'
    )
    completion_threshold = models.IntegerField(
        default=90,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text='Percentage of video that must be watched to mark as complete'
    )
    
    # Publishing
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text='Show in featured section')
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Stats
    view_count = models.IntegerField(default=0)
    completion_count = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    
    # Tracking
    uploaded_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_videos'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['is_published', '-created_at']),
            models.Index(fields=['is_featured', '-created_at']),
            models.Index(fields=['training_module', 'is_published']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Auto-publish timestamp and calculate file size"""
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        elif not self.is_published:
            self.published_at = None
        
        # Calculate file size for uploaded videos
        if self.video_file and not self.file_size:
            try:
                self.file_size = self.video_file.size
            except:
                pass
        
        super().save(*args, **kwargs)
    
    def can_user_access(self, user):
        """Check if user has permission to view this video"""
        if not self.is_published:
            return user.is_staff or user == self.uploaded_by
        
        if self.access_level == 'public':
            return True
        
        if not user.is_authenticated:
            return False
        
        if self.access_level == 'staff':
            return True
        
        if self.access_level == 'managers':
            return user.is_management
        
        if self.access_level == 'trainers':
            return user.is_training_coordinator or user.is_management
        
        if self.access_level == 'custom':
            if self.allowed_users.filter(id=user.id).exists():
                return True
            if hasattr(user, 'role') and user.role in self.allowed_roles:
                return True
        
        return False
    
    def get_embed_url(self):
        """Get embeddable URL for external videos"""
        if self.video_type == 'youtube' and self.video_url:
            # Extract video ID from various YouTube URL formats
            if 'youtu.be/' in self.video_url:
                video_id = self.video_url.split('youtu.be/')[-1].split('?')[0]
            elif 'watch?v=' in self.video_url:
                video_id = self.video_url.split('watch?v=')[-1].split('&')[0]
            else:
                return self.video_url
            return f'https://www.youtube.com/embed/{video_id}'
        
        elif self.video_type == 'vimeo' and self.video_url:
            # Extract video ID from Vimeo URL
            video_id = self.video_url.split('vimeo.com/')[-1].split('?')[0]
            return f'https://player.vimeo.com/video/{video_id}'
        
        return self.video_url
    
    def get_duration_display(self):
        """Format duration as HH:MM:SS or MM:SS"""
        if not self.duration:
            return 'Unknown'
        
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        
        if hours > 0:
            return f'{hours:02d}:{minutes:02d}:{seconds:02d}'
        return f'{minutes:02d}:{seconds:02d}'
    
    def get_file_size_display(self):
        """Format file size in human-readable format"""
        if not self.file_size:
            return 'Unknown'
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f'{self.file_size:.1f} {unit}'
            self.file_size /= 1024.0
        return f'{self.file_size:.1f} TB'


class VideoProgress(models.Model):
    """
    Track user progress watching videos.
    Records watch time, completion status, and last watched position.
    """
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='progress_records')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='video_progress')
    
    # Progress Tracking
    watch_time = models.IntegerField(
        default=0,
        help_text='Total seconds watched (excluding rewinds)'
    )
    last_position = models.IntegerField(
        default=0,
        help_text='Last watched position in seconds'
    )
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Percentage of video watched'
    )
    
    # Completion
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    first_watched_at = models.DateTimeField(auto_now_add=True)
    last_watched_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['video', 'user']
        ordering = ['-last_watched_at']
        indexes = [
            models.Index(fields=['user', '-last_watched_at']),
            models.Index(fields=['video', 'is_completed']),
            models.Index(fields=['user', 'is_completed']),
        ]
    
    def __str__(self):
        return f'{self.user.get_full_name()} - {self.video.title} ({self.progress_percentage}%)'
    
    def update_progress(self, current_position):
        """Update progress based on current playback position"""
        if not self.video.duration:
            return
        
        # Update last position
        self.last_position = current_position
        
        # Calculate progress percentage
        self.progress_percentage = min(100, int((current_position / self.video.duration) * 100))
        
        # Check completion
        if self.progress_percentage >= self.video.completion_threshold and not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.video.completion_count += 1
            self.video.save(update_fields=['completion_count'])
        
        self.save()


class VideoRating(models.Model):
    """
    User ratings for videos (1-5 stars).
    Used to calculate average rating and provide feedback.
    """
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='video_ratings')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5 stars'
    )
    review = models.TextField(blank=True, help_text='Optional review text')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['video', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['video', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f'{self.user.get_full_name()} - {self.video.title} ({self.rating}★)'
    
    def save(self, *args, **kwargs):
        """Update video average rating when saving"""
        super().save(*args, **kwargs)
        self.update_video_rating()
    
    def delete(self, *args, **kwargs):
        """Update video average rating when deleting"""
        super().delete(*args, **kwargs)
        self.update_video_rating()
    
    def update_video_rating(self):
        """Recalculate video average rating"""
        ratings = VideoRating.objects.filter(video=self.video)
        if ratings.exists():
            avg = ratings.aggregate(models.Avg('rating'))['rating__avg']
            self.video.average_rating = round(avg, 1)
        else:
            self.video.average_rating = 0.0
        self.video.save(update_fields=['average_rating'])


class VideoPlaylist(models.Model):
    """
    User-created playlists for organizing videos.
    Can be private or shared with other users.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='video_playlists')
    videos = models.ManyToManyField(
        Video,
        through='PlaylistVideo',
        related_name='playlists'
    )
    
    # Sharing
    is_public = models.BooleanField(default=False, help_text='Public playlists visible to all users')
    shared_with = models.ManyToManyField(
        'User',
        blank=True,
        related_name='shared_playlists',
        help_text='Users with access to this playlist'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_public', '-created_at']),
        ]
    
    def __str__(self):
        return f'{self.name} ({self.user.get_full_name()})'
    
    def get_total_duration(self):
        """Calculate total duration of all videos in playlist"""
        total = 0
        for video in self.videos.all():
            if video.duration:
                total += video.duration
        return total
    
    def get_progress_percentage(self, user):
        """Calculate user's progress through this playlist"""
        videos = self.videos.filter(is_published=True)
        if not videos.exists():
            return 0
        
        completed = VideoProgress.objects.filter(
            video__in=videos,
            user=user,
            is_completed=True
        ).count()
        
        return int((completed / videos.count()) * 100)


class PlaylistVideo(models.Model):
    """Through model for playlist videos with ordering"""
    playlist = models.ForeignKey(VideoPlaylist, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    order = models.IntegerField(default=0, help_text='Display order in playlist')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'added_at']
        unique_together = ['playlist', 'video']
        indexes = [
            models.Index(fields=['playlist', 'order']),
        ]
    
    def __str__(self):
        return f'{self.playlist.name} - {self.video.title} (#{self.order})'
