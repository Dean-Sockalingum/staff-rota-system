"""
TQM Module 5: Document & Policy Management Views

Views for document repository, policy lifecycle, version control, and staff acknowledgements.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, FileResponse
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from decimal import Decimal

from .models import (
    DocumentCategory, Document, DocumentVersion, DocumentReview,
    StaffAcknowledgement, DocumentAttachment, PolicyImpactAssessment
)
from scheduling.models import CareHome, User


@login_required
def document_dashboard(request):
    """Main dashboard for document management with metrics and recent activity."""
    # Get date ranges
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Filter by care home if specified
    care_home_id = request.GET.get('care_home')
    care_home = None
    if care_home_id:
        care_home = get_object_or_404(CareHome, id=care_home_id)
    
    # Base querysets
    documents_qs = Document.objects.all()
    reviews_qs = DocumentReview.objects.all()
    acknowledgements_qs = StaffAcknowledgement.objects.all()
    
    if care_home:
        documents_qs = documents_qs.filter(Q(care_home=care_home) | Q(care_home__isnull=True))
        reviews_qs = reviews_qs.filter(Q(document__care_home=care_home) | Q(document__care_home__isnull=True))
        acknowledgements_qs = acknowledgements_qs.filter(Q(document__care_home=care_home) | Q(document__care_home__isnull=True))
    
    # Document metrics
    total_documents = documents_qs.count()
    published_documents = documents_qs.filter(status='PUBLISHED').count()
    draft_documents = documents_qs.filter(status='DRAFT').count()
    
    # Review metrics
    overdue_reviews = [d for d in documents_qs if d.is_overdue_for_review()]
    upcoming_reviews = documents_qs.filter(
        next_review_date__lte=today + timedelta(days=30),
        next_review_date__gt=today
    ).count()
    
    # Acknowledgement metrics
    pending_acknowledgements = acknowledgements_qs.filter(acknowledged_at__isnull=True).count()
    overdue_acknowledgements = [a for a in acknowledgements_qs.filter(acknowledged_at__isnull=True) if a.is_overdue()]
    
    # Recent activity
    recent_documents = documents_qs.order_by('-created_at')[:5]
    recent_reviews = reviews_qs.order_by('-due_date')[:5]
    recent_acknowledgements = acknowledgements_qs.filter(
        acknowledged_at__isnull=False
    ).order_by('-acknowledged_at')[:5]
    
    # Document type distribution
    doc_types = documents_qs.values('document_type').annotate(count=Count('id')).order_by('-count')
    
    context = {
        'care_homes': CareHome.objects.all(),
        'selected_care_home': care_home,
        'total_documents': total_documents,
        'published_documents': published_documents,
        'draft_documents': draft_documents,
        'overdue_reviews_count': len(overdue_reviews),
        'upcoming_reviews': upcoming_reviews,
        'pending_acknowledgements': pending_acknowledgements,
        'overdue_acknowledgements_count': len(overdue_acknowledgements),
        'recent_documents': recent_documents,
        'recent_reviews': recent_reviews,
        'recent_acknowledgements': recent_acknowledgements,
        'doc_types': doc_types,
        'page_title': 'Document & Policy Management',
    }
    
    return render(request, 'document_management/dashboard.html', context)


@login_required
def document_list(request):
    """List all documents with filtering and search."""
    documents = Document.objects.all().select_related('category', 'owner', 'care_home')
    
    # Filtering
    document_type = request.GET.get('document_type')
    status = request.GET.get('status')
    category_id = request.GET.get('category')
    care_home_id = request.GET.get('care_home')
    search = request.GET.get('search')
    review_status = request.GET.get('review_status')
    
    if document_type:
        documents = documents.filter(document_type=document_type)
    if status:
        documents = documents.filter(status=status)
    if category_id:
        documents = documents.filter(category_id=category_id)
    if care_home_id:
        if care_home_id == 'org_wide':
            documents = documents.filter(care_home__isnull=True)
        else:
            documents = documents.filter(care_home_id=care_home_id)
    if search:
        documents = documents.filter(
            Q(title__icontains=search) |
            Q(document_code__icontains=search) |
            Q(summary__icontains=search) |
            Q(keywords__icontains=search)
        )
    
    # Review status filter
    if review_status == 'overdue':
        documents = [d for d in documents if d.is_overdue_for_review()]
    elif review_status == 'due_soon':
        today = timezone.now().date()
        documents = documents.filter(
            next_review_date__lte=today + timedelta(days=30),
            next_review_date__gt=today
        )
    
    context = {
        'documents': documents,
        'categories': DocumentCategory.objects.filter(is_active=True),
        'care_homes': CareHome.objects.all(),
        'page_title': 'Documents & Policies',
    }
    
    return render(request, 'document_management/document_list.html', context)


@login_required
def document_detail(request, pk):
    """Display detailed view of a document with versions, reviews, and acknowledgements."""
    document = get_object_or_404(
        Document.objects.select_related('category', 'owner', 'approver', 'care_home'),
        pk=pk
    )
    
    # Get related data
    versions = document.versions.all().order_by('-created_at')
    reviews = document.reviews.all().order_by('-due_date')
    attachments = document.attachments.all()
    acknowledgements = document.acknowledgement_requirements.all().select_related('staff_member')
    
    # Calculate acknowledgement stats
    ack_stats = None
    if document.requires_acknowledgement and document.status == 'PUBLISHED':
        total = acknowledgements.count()
        acknowledged = acknowledgements.filter(acknowledged_at__isnull=False).count()
        pending = total - acknowledged
        overdue = len([a for a in acknowledgements if a.is_overdue()])
        
        ack_stats = {
            'total': total,
            'acknowledged': acknowledged,
            'pending': pending,
            'overdue': overdue,
            'rate': document.acknowledgement_rate(),
        }
    
    # Get impact assessment if exists
    impact_assessment = None
    if document.document_type in ['POLICY', 'PROCEDURE']:
        try:
            impact_assessment = document.impact_assessment
        except PolicyImpactAssessment.DoesNotExist:
            pass
    
    context = {
        'document': document,
        'versions': versions,
        'reviews': reviews,
        'attachments': attachments,
        'acknowledgements': acknowledgements[:10],  # Limit display
        'ack_stats': ack_stats,
        'impact_assessment': impact_assessment,
        'page_title': f'{document.document_code} - {document.title}',
    }
    
    return render(request, 'document_management/document_detail.html', context)


@login_required
def my_acknowledgements(request):
    """View pending and completed acknowledgements for the logged-in user."""
    acknowledgements = StaffAcknowledgement.objects.filter(
        staff_member=request.user
    ).select_related('document').order_by('-required_by')
    
    # Separate pending and completed
    pending = acknowledgements.filter(acknowledged_at__isnull=True)
    completed = acknowledgements.filter(acknowledged_at__isnull=False)
    
    # Count overdue
    overdue_count = len([a for a in pending if a.is_overdue()])
    
    context = {
        'pending_acknowledgements': pending,
        'completed_acknowledgements': completed,
        'overdue_count': overdue_count,
        'page_title': 'My Document Acknowledgements',
    }
    
    return render(request, 'document_management/my_acknowledgements.html', context)


@login_required
def acknowledge_document(request, pk):
    """Acknowledge reading and understanding a document."""
    acknowledgement = get_object_or_404(
        StaffAcknowledgement,
        pk=pk,
        staff_member=request.user
    )
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        quiz_score = request.POST.get('quiz_score')
        
        # Convert quiz score to Decimal if provided
        if quiz_score:
            try:
                quiz_score = Decimal(quiz_score)
            except:
                quiz_score = None
        
        acknowledgement.acknowledge(
            method='ONLINE',
            quiz_score=quiz_score,
            notes=notes
        )
        
        messages.success(
            request,
            f'Thank you for acknowledging {acknowledgement.document.document_code}.'
        )
        return redirect('document_management:my_acknowledgements')
    
    context = {
        'acknowledgement': acknowledgement,
        'document': acknowledgement.document,
        'page_title': f'Acknowledge: {acknowledgement.document.title}',
    }
    
    return render(request, 'document_management/acknowledge_document.html', context)


@login_required
def version_history(request, document_pk):
    """View version history for a document with comparison capability."""
    document = get_object_or_404(Document, pk=document_pk)
    versions = document.versions.all().order_by('-created_at')
    
    # Get two versions for comparison if specified
    compare_from = request.GET.get('compare_from')
    compare_to = request.GET.get('compare_to')
    
    comparison = None
    if compare_from and compare_to:
        version_from = get_object_or_404(DocumentVersion, pk=compare_from, document=document)
        version_to = get_object_or_404(DocumentVersion, pk=compare_to, document=document)
        
        comparison = {
            'from': version_from,
            'to': version_to,
        }
    
    context = {
        'document': document,
        'versions': versions,
        'comparison': comparison,
        'page_title': f'Version History: {document.document_code}',
    }
    
    return render(request, 'document_management/version_history.html', context)


@login_required
def review_list(request):
    """List all document reviews with filtering."""
    reviews = DocumentReview.objects.all().select_related('document', 'reviewer')
    
    # Filtering
    review_type = request.GET.get('review_type')
    status = request.GET.get('status')
    reviewer_id = request.GET.get('reviewer')
    
    if review_type:
        reviews = reviews.filter(review_type=review_type)
    if status == 'complete':
        reviews = reviews.filter(is_complete=True)
    elif status == 'incomplete':
        reviews = reviews.filter(is_complete=False)
    elif status == 'overdue':
        reviews = [r for r in reviews.filter(is_complete=False) if r.is_overdue()]
    if reviewer_id:
        reviews = reviews.filter(reviewer_id=reviewer_id)
    
    context = {
        'reviews': reviews,
        'reviewers': User.objects.filter(is_active=True).order_by('first_name'),
        'page_title': 'Document Reviews',
    }
    
    return render(request, 'document_management/review_list.html', context)


@login_required
def category_list(request):
    """List all document categories with document counts."""
    categories = DocumentCategory.objects.filter(is_active=True).prefetch_related('documents')
    
    # Add document counts
    for category in categories:
        category.doc_count = category.documents.count()
    
    context = {
        'categories': categories,
        'page_title': 'Document Categories',
    }
    
    return render(request, 'document_management/category_list.html', context)


# JSON API Endpoints for Chart.js

@login_required
def document_stats_data(request):
    """JSON endpoint for document statistics charts."""
    care_home_id = request.GET.get('care_home')
    
    # Base queryset
    documents = Document.objects.all()
    if care_home_id:
        documents = documents.filter(Q(care_home_id=care_home_id) | Q(care_home__isnull=True))
    
    # Status distribution
    status_data = documents.values('status').annotate(count=Count('id'))
    status_distribution = {
        'labels': [item['status'] for item in status_data],
        'counts': [item['count'] for item in status_data],
    }
    
    # Document type distribution
    type_data = documents.values('document_type').annotate(count=Count('id'))
    type_distribution = {
        'labels': [item['document_type'] for item in type_data],
        'counts': [item['count'] for item in type_data],
    }
    
    # Review status (overdue, due soon, current)
    today = timezone.now().date()
    overdue = len([d for d in documents if d.is_overdue_for_review()])
    due_soon = documents.filter(
        next_review_date__lte=today + timedelta(days=30),
        next_review_date__gt=today
    ).count()
    current = documents.filter(next_review_date__gt=today + timedelta(days=30)).count()
    
    review_status = {
        'labels': ['Overdue', 'Due Soon (30 days)', 'Current'],
        'counts': [overdue, due_soon, current],
    }
    
    return JsonResponse({
        'status_distribution': status_distribution,
        'type_distribution': type_distribution,
        'review_status': review_status,
    })


@login_required
def acknowledgement_stats_data(request):
    """JSON endpoint for acknowledgement statistics."""
    care_home_id = request.GET.get('care_home')
    
    # Base queryset - only published documents requiring acknowledgement
    documents = Document.objects.filter(
        status='PUBLISHED',
        requires_acknowledgement=True
    )
    
    if care_home_id:
        documents = documents.filter(Q(care_home_id=care_home_id) | Q(care_home__isnull=True))
    
    # Calculate rates
    rates = []
    labels = []
    
    for doc in documents[:10]:  # Limit to 10 most recent
        rate = doc.acknowledgement_rate()
        if rate is not None:
            labels.append(doc.document_code)
            rates.append(rate)
    
    return JsonResponse({
        'labels': labels,
        'rates': rates,
    })


@login_required
def compliance_framework_data(request):
    """JSON endpoint for compliance framework coverage."""
    # Get all documents with compliance frameworks
    documents = Document.objects.exclude(compliance_frameworks=[])
    
    # Count documents by framework
    framework_counts = {}
    for doc in documents:
        for framework in doc.compliance_frameworks:
            framework_counts[framework] = framework_counts.get(framework, 0) + 1
    
    # Sort by count
    sorted_frameworks = sorted(framework_counts.items(), key=lambda x: x[1], reverse=True)
    
    return JsonResponse({
        'labels': [item[0] for item in sorted_frameworks],
        'counts': [item[1] for item in sorted_frameworks],
    })
