"""
Task 53: Document Management Views
Views for document upload, listing, downloading, and management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, JsonResponse, HttpResponse, Http404
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
import os
import mimetypes

from .models_documents import (
    Document, DocumentCategory, DocumentAccess,
    DocumentShare, DocumentComment
)
from .decorators import manager_required


@login_required
def document_list(request):
    """
    List all documents (with filtering and search)
    """
    # Get query parameters
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    access_level = request.GET.get('access_level', '')
    file_type = request.GET.get('file_type', '')
    
    # Base queryset - only show documents user can access
    documents = Document.objects.filter(is_archived=False, is_latest_version=True)
    
    # Filter by permissions
    if not request.user.is_superuser:
        # Build permission filter
        q_filter = Q(access_level='public') | Q(access_level='staff')
        
        if hasattr(request.user, 'role') and request.user.role.is_management:
            q_filter |= Q(access_level='managers')
        
        q_filter |= Q(allowed_users=request.user)
        
        documents = documents.filter(q_filter).distinct()
    
    # Apply filters
    if search_query:
        documents = documents.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    if category_id:
        documents = documents.filter(category_id=category_id)
    
    if access_level:
        documents = documents.filter(access_level=access_level)
    
    if file_type:
        documents = documents.filter(file_name__iendswith=f'.{file_type}')
    
    # Annotate with access count
    documents = documents.annotate(
        total_accesses=Count('access_logs')
    ).select_related('category', 'uploaded_by')
    
    # Pagination
    paginator = Paginator(documents, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = DocumentCategory.objects.filter(is_active=True)
    
    # Get statistics
    total_count = documents.count()
    my_uploads = Document.objects.filter(uploaded_by=request.user, is_archived=False).count()
    shared_with_me = DocumentShare.objects.filter(shared_with=request.user, is_active=True).count()
    
    context = {
        'documents': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_id,
        'access_level_filter': access_level,
        'file_type_filter': file_type,
        'total_count': total_count,
        'my_uploads': my_uploads,
        'shared_with_me': shared_with_me,
    }
    
    return render(request, 'scheduling/document_list.html', context)


@login_required
@manager_required
def document_upload(request):
    """
    Upload a new document
    """
    if request.method == 'POST':
        try:
            # Get form data
            title = request.POST.get('title')
            description = request.POST.get('description', '')
            category_id = request.POST.get('category')
            access_level = request.POST.get('access_level', 'staff')
            tags = request.POST.get('tags', '')
            file = request.FILES.get('file')
            
            if not file:
                messages.error(request, 'Please select a file to upload.')
                return redirect('scheduling:document_upload')
            
            # Create document
            document = Document.objects.create(
                title=title,
                description=description,
                file=file,
                category_id=category_id if category_id else None,
                access_level=access_level,
                tags=tags,
                uploaded_by=request.user
            )
            
            # Handle allowed users for private/confidential documents
            if access_level in ['private', 'confidential']:
                allowed_user_ids = request.POST.getlist('allowed_users')
                if allowed_user_ids:
                    document.allowed_users.set(allowed_user_ids)
            
            messages.success(request, f'Document "{document.title}" uploaded successfully.')
            return redirect('scheduling:document_detail', document_id=document.id)
        
        except Exception as e:
            messages.error(request, f'Error uploading document: {str(e)}')
            return redirect('scheduling:document_upload')
    
    # GET request - show upload form
    categories = DocumentCategory.objects.filter(is_active=True)
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'scheduling/document_upload.html', context)


@login_required
def document_detail(request, document_id):
    """
    View document details
    """
    document = get_object_or_404(Document, id=document_id)
    
    # Check permissions
    if not document.can_user_access(request.user):
        messages.error(request, 'You do not have permission to view this document.')
        return redirect('scheduling:document_list')
    
    # Log access
    DocumentAccess.objects.create(
        document=document,
        user=request.user,
        action='view',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )
    
    # Update view count
    document.view_count += 1
    document.save()
    
    # Get version history
    versions = document.get_version_history()
    
    # Get recent access logs
    access_logs = document.access_logs.all()[:20]
    
    # Get comments
    comments = document.comments.filter(is_deleted=False, parent__isnull=True)
    
    # Check if shared with me
    my_share = DocumentShare.objects.filter(
        document=document,
        shared_with=request.user,
        is_active=True
    ).first()
    
    context = {
        'document': document,
        'versions': versions,
        'access_logs': access_logs,
        'comments': comments,
        'my_share': my_share,
        'can_edit': request.user == document.uploaded_by or request.user.is_superuser,
        'can_manage': hasattr(request.user, 'role') and request.user.role.is_management,
    }
    
    return render(request, 'scheduling/document_detail.html', context)


@login_required
def document_download(request, document_id):
    """
    Download a document
    """
    document = get_object_or_404(Document, id=document_id)
    
    # Check permissions
    if not document.can_user_access(request.user):
        raise Http404("Document not found or you don't have permission.")
    
    # Log download
    DocumentAccess.objects.create(
        document=document,
        user=request.user,
        action='download',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )
    
    # Update download count
    document.download_count += 1
    document.save()
    
    # Serve file
    try:
        file_path = document.file.path
        
        # Get mime type
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # Open file and return response
        response = FileResponse(
            open(file_path, 'rb'),
            content_type=mime_type
        )
        response['Content-Disposition'] = f'attachment; filename="{document.file_name}"'
        
        return response
    
    except Exception as e:
        messages.error(request, f'Error downloading document: {str(e)}')
        return redirect('scheduling:document_detail', document_id=document_id)


@login_required
@manager_required
def document_edit(request, document_id):
    """
    Edit document metadata
    """
    document = get_object_or_404(Document, id=document_id)
    
    # Check permissions
    if request.user != document.uploaded_by and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to edit this document.')
        return redirect('scheduling:document_detail', document_id=document_id)
    
    if request.method == 'POST':
        document.title = request.POST.get('title')
        document.description = request.POST.get('description', '')
        document.tags = request.POST.get('tags', '')
        
        category_id = request.POST.get('category')
        document.category_id = category_id if category_id else None
        
        document.access_level = request.POST.get('access_level', 'staff')
        
        # Handle allowed users for private/confidential documents
        if document.access_level in ['private', 'confidential']:
            allowed_user_ids = request.POST.getlist('allowed_users')
            if allowed_user_ids:
                document.allowed_users.set(allowed_user_ids)
        
        document.save()
        
        messages.success(request, 'Document updated successfully.')
        return redirect('scheduling:document_detail', document_id=document_id)
    
    # GET request - show edit form
    categories = DocumentCategory.objects.filter(is_active=True)
    
    context = {
        'document': document,
        'categories': categories,
    }
    
    return render(request, 'scheduling/document_edit.html', context)


@login_required
@manager_required
@require_http_methods(["POST"])
def document_delete(request, document_id):
    """
    Delete (archive) a document
    """
    document = get_object_or_404(Document, id=document_id)
    
    # Check permissions
    if request.user != document.uploaded_by and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete this document.')
        return redirect('scheduling:document_detail', document_id=document_id)
    
    # Archive instead of delete
    document.is_archived = True
    document.archived_at = timezone.now()
    document.save()
    
    messages.success(request, f'Document "{document.title}" has been archived.')
    return redirect('scheduling:document_list')


@login_required
@manager_required
def document_new_version(request, document_id):
    """
    Upload a new version of an existing document
    """
    document = get_object_or_404(Document, id=document_id)
    
    # Check permissions
    if request.user != document.uploaded_by and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to update this document.')
        return redirect('scheduling:document_detail', document_id=document_id)
    
    if request.method == 'POST':
        file = request.FILES.get('file')
        
        if not file:
            messages.error(request, 'Please select a file to upload.')
            return redirect('scheduling:document_detail', document_id=document_id)
        
        # Create new version
        new_version = document.create_new_version(file, request.user)
        
        messages.success(request, f'New version (v{new_version.version}) uploaded successfully.')
        return redirect('scheduling:document_detail', document_id=new_version.id)
    
    context = {
        'document': document,
    }
    
    return render(request, 'scheduling/document_new_version.html', context)


@login_required
@manager_required
def document_share(request, document_id):
    """
    Share document with other users
    """
    document = get_object_or_404(Document, id=document_id)
    
    if request.method == 'POST':
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user_ids = request.POST.getlist('users')
        can_download = request.POST.get('can_download') == 'on'
        can_reshare = request.POST.get('can_reshare') == 'on'
        expires_days = request.POST.get('expires_days')
        max_downloads = request.POST.get('max_downloads')
        
        expires_at = None
        if expires_days:
            from datetime import timedelta
            expires_at = timezone.now() + timedelta(days=int(expires_days))
        
        max_downloads_int = int(max_downloads) if max_downloads else None
        
        # Create shares
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                
                # Check if already shared
                share, created = DocumentShare.objects.get_or_create(
                    document=document,
                    shared_with=user,
                    defaults={
                        'shared_by': request.user,
                        'can_download': can_download,
                        'can_reshare': can_reshare,
                        'expires_at': expires_at,
                        'max_downloads': max_downloads_int,
                    }
                )
                
                if not created:
                    # Update existing share
                    share.can_download = can_download
                    share.can_reshare = can_reshare
                    share.expires_at = expires_at
                    share.max_downloads = max_downloads_int
                    share.is_active = True
                    share.save()
            
            except User.DoesNotExist:
                continue
        
        messages.success(request, 'Document shared successfully.')
        return redirect('scheduling:document_detail', document_id=document_id)
    
    # GET request - show share form
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    users = User.objects.exclude(id=request.user.id).order_by('first_name', 'last_name')
    existing_shares = document.shares.filter(is_active=True)
    
    context = {
        'document': document,
        'users': users,
        'existing_shares': existing_shares,
    }
    
    return render(request, 'scheduling/document_share.html', context)


@login_required
@require_http_methods(["POST"])
def document_add_comment(request, document_id):
    """
    Add a comment to a document
    """
    document = get_object_or_404(Document, id=document_id)
    
    # Check permissions
    if not document.can_user_access(request.user):
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    content = request.POST.get('content', '').strip()
    parent_id = request.POST.get('parent_id')
    
    if not content:
        return JsonResponse({'status': 'error', 'message': 'Comment cannot be empty'}, status=400)
    
    comment = DocumentComment.objects.create(
        document=document,
        user=request.user,
        parent_id=parent_id if parent_id else None,
        content=content
    )
    
    return JsonResponse({
        'status': 'success',
        'comment': {
            'id': comment.id,
            'user': request.user.get_full_name(),
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
        }
    })


@login_required
def my_documents(request):
    """
    List documents uploaded by the current user
    """
    documents = Document.objects.filter(
        uploaded_by=request.user,
        is_archived=False,
        is_latest_version=True
    ).select_related('category').order_by('-uploaded_at')
    
    # Pagination
    paginator = Paginator(documents, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'documents': page_obj,
        'page_title': 'My Documents',
    }
    
    return render(request, 'scheduling/my_documents.html', context)


@login_required
def shared_with_me(request):
    """
    List documents shared with the current user
    """
    shares = DocumentShare.objects.filter(
        shared_with=request.user,
        is_active=True
    ).select_related('document', 'shared_by').order_by('-created_at')
    
    # Filter valid shares
    valid_shares = [share for share in shares if share.is_valid()]
    
    # Pagination
    paginator = Paginator(valid_shares, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'shares': page_obj,
        'page_title': 'Shared With Me',
    }
    
    return render(request, 'scheduling/shared_with_me.html', context)


@login_required
@manager_required
def category_manage(request):
    """
    Manage document categories
    """
    categories = DocumentCategory.objects.all().order_by('order', 'name')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'scheduling/category_manage.html', context)


@login_required
@manager_required
@require_http_methods(["POST"])
def category_create(request):
    """
    Create a new category (AJAX)
    """
    try:
        from django.utils.text import slugify
        
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        parent_id = request.POST.get('parent_id')
        
        category = DocumentCategory.objects.create(
            name=name,
            slug=slugify(name),
            description=description,
            parent_id=parent_id if parent_id else None
        )
        
        return JsonResponse({
            'status': 'success',
            'category': {
                'id': category.id,
                'name': category.name,
                'slug': category.slug
            }
        })
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
