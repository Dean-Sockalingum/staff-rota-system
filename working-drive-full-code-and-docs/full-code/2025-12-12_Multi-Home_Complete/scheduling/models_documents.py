"""
Task 53: Document Management Models
Models for document storage, versioning, permissions, and categories
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import os
import hashlib


def document_upload_path(instance, filename):
    """
    Generate upload path for documents
    Format: documents/{year}/{month}/{category}/{filename}
    """
    now = timezone.now()
    category = instance.category.slug if instance.category else 'uncategorized'
    return f'documents/{now.year}/{now.month:02d}/{category}/{filename}'


class DocumentCategory(models.Model):
    """
    Categories for organizing documents
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fa-folder', help_text="FontAwesome icon class")
    color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scheduling_document_category'
        verbose_name = 'Document Category'
        verbose_name_plural = 'Document Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def get_full_path(self):
        """Get full category path"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class Document(models.Model):
    """
    Main document model with file storage and metadata
    """
    
    ACCESS_LEVEL_CHOICES = [
        ('public', 'Public - All users can view'),
        ('staff', 'Staff Only - All staff can view'),
        ('managers', 'Managers Only - Only managers can view'),
        ('private', 'Private - Only specified users'),
        ('confidential', 'Confidential - Restricted access'),
    ]
    
    # Basic information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # File information
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[FileExtensionValidator(
            allowed_extensions=[
                'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
                'txt', 'csv', 'jpg', 'jpeg', 'png', 'gif',
                'zip', 'rar', '7z'
            ]
        )]
    )
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField(help_text="File size in bytes")
    file_type = models.CharField(max_length=100)
    file_hash = models.CharField(max_length=64, help_text="SHA-256 hash of file")
    
    # Organization
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    # Access control
    access_level = models.CharField(
        max_length=20,
        choices=ACCESS_LEVEL_CHOICES,
        default='staff'
    )
    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='accessible_documents'
    )
    allowed_roles = models.JSONField(
        default=list,
        help_text="List of role names that can access this document"
    )
    
    # Metadata
    version = models.IntegerField(default=1)
    is_latest_version = models.BooleanField(default=True)
    previous_version = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='newer_versions'
    )
    
    # Tracking
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Statistics
    download_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    
    # Status
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'scheduling_document'
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['-uploaded_at']),
            models.Index(fields=['category', '-uploaded_at']),
            models.Index(fields=['access_level']),
            models.Index(fields=['is_latest_version', 'is_archived']),
        ]
    
    def __str__(self):
        return f"{self.title} (v{self.version})"
    
    def save(self, *args, **kwargs):
        """Override save to calculate file metadata"""
        if self.file and not self.file_name:
            self.file_name = os.path.basename(self.file.name)
            self.file_size = self.file.size
            self.file_type = self.get_file_extension()
            
            # Calculate file hash
            if hasattr(self.file, 'read'):
                self.file.seek(0)
                file_hash = hashlib.sha256()
                for chunk in self.file.chunks():
                    file_hash.update(chunk)
                self.file_hash = file_hash.hexdigest()
                self.file.seek(0)
        
        super().save(*args, **kwargs)
    
    def get_file_extension(self):
        """Get file extension from filename"""
        return os.path.splitext(self.file_name)[1].lower().lstrip('.')
    
    def get_file_icon(self):
        """Get FontAwesome icon based on file type"""
        ext = self.get_file_extension()
        
        icon_map = {
            'pdf': 'fa-file-pdf',
            'doc': 'fa-file-word',
            'docx': 'fa-file-word',
            'xls': 'fa-file-excel',
            'xlsx': 'fa-file-excel',
            'ppt': 'fa-file-powerpoint',
            'pptx': 'fa-file-powerpoint',
            'txt': 'fa-file-alt',
            'csv': 'fa-file-csv',
            'jpg': 'fa-file-image',
            'jpeg': 'fa-file-image',
            'png': 'fa-file-image',
            'gif': 'fa-file-image',
            'zip': 'fa-file-archive',
            'rar': 'fa-file-archive',
            '7z': 'fa-file-archive',
        }
        
        return icon_map.get(ext, 'fa-file')
    
    def get_file_size_display(self):
        """Get human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def can_user_access(self, user):
        """Check if user has permission to access this document"""
        if user.is_superuser:
            return True
        
        if self.access_level == 'public':
            return True
        
        if self.access_level == 'staff' and user.is_authenticated:
            return True
        
        if self.access_level == 'managers':
            return hasattr(user, 'role') and user.role.is_management
        
        if self.access_level == 'private':
            return user in self.allowed_users.all()
        
        if self.access_level == 'confidential':
            # Check if user is in allowed users or has allowed role
            if user in self.allowed_users.all():
                return True
            if hasattr(user, 'role') and user.role.name in self.allowed_roles:
                return True
            return False
        
        return False
    
    def create_new_version(self, new_file, updated_by):
        """Create a new version of this document"""
        # Mark current version as not latest
        self.is_latest_version = False
        self.save()
        
        # Create new version
        new_doc = Document.objects.create(
            title=self.title,
            description=self.description,
            file=new_file,
            category=self.category,
            tags=self.tags,
            access_level=self.access_level,
            version=self.version + 1,
            is_latest_version=True,
            previous_version=self,
            uploaded_by=updated_by,
        )
        
        # Copy allowed users
        new_doc.allowed_users.set(self.allowed_users.all())
        new_doc.allowed_roles = self.allowed_roles.copy()
        new_doc.save()
        
        return new_doc
    
    def get_version_history(self):
        """Get all versions of this document"""
        versions = []
        current = self
        
        # Get newer versions
        while current.newer_versions.exists():
            current = current.newer_versions.first()
            versions.insert(0, current)
        
        # Get older versions
        current = self
        versions.append(current)
        while current.previous_version:
            current = current.previous_version
            versions.append(current)
        
        return versions


class DocumentAccess(models.Model):
    """
    Track document access/downloads for audit trail
    """
    
    ACTION_CHOICES = [
        ('view', 'Viewed'),
        ('download', 'Downloaded'),
        ('preview', 'Previewed'),
        ('share', 'Shared'),
    ]
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='access_logs'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='document_accesses'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    accessed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'scheduling_document_access'
        verbose_name = 'Document Access Log'
        verbose_name_plural = 'Document Access Logs'
        ordering = ['-accessed_at']
        indexes = [
            models.Index(fields=['document', '-accessed_at']),
            models.Index(fields=['user', '-accessed_at']),
        ]
    
    def __str__(self):
        user_name = self.user.get_full_name() if self.user else 'Anonymous'
        return f"{user_name} {self.get_action_display()} {self.document.title} at {self.accessed_at}"


class DocumentShare(models.Model):
    """
    Document sharing with expiration and download limits
    """
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='shares'
    )
    shared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='shared_documents'
    )
    shared_with = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents_shared_with_me'
    )
    
    # Share settings
    can_download = models.BooleanField(default=True)
    can_reshare = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    max_downloads = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of downloads allowed (null = unlimited)"
    )
    
    # Tracking
    download_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'scheduling_document_share'
        verbose_name = 'Document Share'
        verbose_name_plural = 'Document Shares'
        ordering = ['-created_at']
        unique_together = ['document', 'shared_with']
    
    def __str__(self):
        return f"{self.document.title} shared with {self.shared_with.get_full_name()}"
    
    def is_valid(self):
        """Check if share is still valid"""
        if not self.is_active:
            return False
        
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        
        if self.max_downloads and self.download_count >= self.max_downloads:
            return False
        
        return True
    
    def revoke(self):
        """Revoke the share"""
        self.is_active = False
        self.revoked_at = timezone.now()
        self.save()


class DocumentComment(models.Model):
    """
    Comments on documents for collaboration
    """
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='document_comments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    content = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'scheduling_document_comment'
        verbose_name = 'Document Comment'
        verbose_name_plural = 'Document Comments'
        ordering = ['created_at']
    
    def __str__(self):
        user_name = self.user.get_full_name() if self.user else 'Anonymous'
        return f"Comment by {user_name} on {self.document.title}"
