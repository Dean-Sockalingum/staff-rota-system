"""
TQM Module 5: Policies & Procedures Views
==========================================

Complete views for policy lifecycle management.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DeleteView
from django.utils import timezone
from django.db.models import Q, Count

from .models import (
    Policy, PolicyVersion, PolicyAcknowledgement, PolicyReview,
    Procedure, ProcedureStep, PolicyComplianceCheck, AuditTrail
)
from .forms import (
    PolicyForm, PolicyVersionForm, PolicyAcknowledgementForm,
    PolicyReviewForm, ProcedureForm, PolicyComplianceCheckForm
)


@login_required
def dashboard(request):
    """
    Policy management dashboard with overview metrics.
    """
    # Get counts and metrics
    total_policies = Policy.objects.count()
    active_policies = Policy.objects.filter(status='active').count()
    policies_needing_review = Policy.objects.filter(
        next_review_date__lte=timezone.now().date() + timezone.timedelta(days=30)
    ).count()
    
    # Pending acknowledgements for current user
    pending_acks = Policy.objects.filter(
        is_mandatory=True,
        status='active'
    ).exclude(
        acknowledgements__staff_member=request.user
    ).count()
    
    # Recent policies
    recent_policies = Policy.objects.order_by('-created_date')[:5]
    
    # Upcoming reviews
    upcoming_reviews = PolicyReview.objects.filter(
        completion_date__isnull=True,
        review_date__lte=timezone.now().date() + timezone.timedelta(days=30)
    ).order_by('review_date')[:5]
    
    context = {
        'total_policies': total_policies,
        'active_policies': active_policies,
        'policies_needing_review': policies_needing_review,
        'pending_acks': pending_acks,
        'recent_policies': recent_policies,
        'upcoming_reviews': upcoming_reviews,
    }
    return render(request, 'policies_procedures/dashboard.html', context)


@login_required
def policy_list(request):
    """
    List all policies with filtering and search.
    """
    policies = Policy.objects.all()
    
    # Filtering
    category = request.GET.get('category')
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    if category:
        policies = policies.filter(category=category)
    if status:
        policies = policies.filter(status=status)
    if search:
        policies = policies.filter(
            Q(title__icontains=search) |
            Q(policy_number__icontains=search) |
            Q(keywords__icontains=search)
        )
    
    context = {
        'policies': policies.order_by('-effective_date'),
        'categories': Policy.CATEGORY_CHOICES,
        'statuses': Policy.STATUS_CHOICES,
    }
    return render(request, 'policies_procedures/policy_list.html', context)


@login_required
def policy_detail(request, pk):
    """
    Detailed view of a single policy.
    """
    policy = get_object_or_404(Policy, pk=pk)
    
    # Get related data
    versions = policy.versions.all()
    acknowledgements = policy.acknowledgements.all()[:10]
    reviews = policy.reviews.all()[:5]
    procedures = policy.procedures.all()
    compliance_checks = policy.compliance_checks.all()[:5]
    audit_trail = policy.audit_trail.all()[:10]
    
    # Check if current user has acknowledged
    user_acknowledged = policy.acknowledgements.filter(staff_member=request.user).exists()
    
    context = {
        'policy': policy,
        'versions': versions,
        'acknowledgements': acknowledgements,
        'reviews': reviews,
        'procedures': procedures,
        'compliance_checks': compliance_checks,
        'audit_trail': audit_trail,
        'user_acknowledged': user_acknowledged,
    }
    return render(request, 'policies_procedures/policy_detail.html', context)


class PolicyCreateView(LoginRequiredMixin, CreateView):
    """Create a new policy"""
    model = Policy
    form_class = PolicyForm
    template_name = 'policies_procedures/policy_form.html'
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Policy created successfully')
        return super().form_valid(form)


class PolicyUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing policy"""
    model = Policy
    form_class = PolicyForm
    template_name = 'policies_procedures/policy_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Policy updated successfully')
        return super().form_valid(form)


class PolicyDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a policy"""
    model = Policy
    template_name = 'policies_procedures/policy_confirm_delete.html'
    success_url = reverse_lazy('policies_procedures:policy_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Policy archived successfully')
        return super().delete(request, *args, **kwargs)


@login_required
def version_history(request, pk):
    """View all versions of a policy"""
    policy = get_object_or_404(Policy, pk=pk)
    versions = policy.versions.all()
    
    context = {
        'policy': policy,
        'versions': versions,
    }
    return render(request, 'policies_procedures/version_history.html', context)


class PolicyVersionCreateView(LoginRequiredMixin, CreateView):
    """Create a new policy version"""
    model = PolicyVersion
    form_class = PolicyVersionForm
    template_name = 'policies_procedures/version_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.policy = get_object_or_404(Policy, pk=kwargs.get('policy_pk'))
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.policy = self.policy
        form.instance.created_by = self.request.user
        messages.success(self.request, 'New policy version created')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('policies_procedures:version_history', kwargs={'pk': self.policy.pk})


@login_required
def acknowledge_policy(request, pk):
    """Staff acknowledgement of policy"""
    policy = get_object_or_404(Policy, pk=pk)
    
    # Check if already acknowledged
    if policy.acknowledgements.filter(staff_member=request.user).exists():
        messages.info(request, 'You have already acknowledged this policy')
        return redirect('policies_procedures:policy_detail', pk=pk)
    
    if request.method == 'POST':
        form = PolicyAcknowledgementForm(request.POST)
        if form.is_valid():
            ack = form.save(commit=False)
            ack.policy = policy
            ack.staff_member = request.user
            ack.ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
            ack.save()
            messages.success(request, 'Policy acknowledged successfully')
            return redirect('policies_procedures:policy_detail', pk=pk)
    else:
        form = PolicyAcknowledgementForm()
    
    context = {
        'policy': policy,
        'form': form,
    }
    return render(request, 'policies_procedures/acknowledge_form.html', context)


@login_required
def my_acknowledgements(request):
    """View all policies acknowledged by current user"""
    acknowledgements = PolicyAcknowledgement.objects.filter(
        staff_member=request.user
    ).order_by('-acknowledged_date')
    
    context = {
        'acknowledgements': acknowledgements,
    }
    return render(request, 'policies_procedures/my_acknowledgements.html', context)


@login_required
def pending_acknowledgements(request):
    """View policies requiring acknowledgement"""
    # Policies that are mandatory and active but not acknowledged by user
    pending = Policy.objects.filter(
        is_mandatory=True,
        status='active'
    ).exclude(
        acknowledgements__staff_member=request.user
    )
    
    context = {
        'pending_policies': pending,
    }
    return render(request, 'policies_procedures/pending_acknowledgements.html', context)


class PolicyReviewCreateView(LoginRequiredMixin, CreateView):
    """Schedule a policy review"""
    model = PolicyReview
    form_class = PolicyReviewForm
    template_name = 'policies_procedures/review_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.policy = get_object_or_404(Policy, pk=kwargs.get('policy_pk'))
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.policy = self.policy
        form.instance.reviewer = self.request.user
        messages.success(self.request, 'Policy review scheduled')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('policies_procedures:policy_detail', kwargs={'pk': self.policy.pk})


class PolicyReviewUpdateView(LoginRequiredMixin, UpdateView):
    """Complete a policy review"""
    model = PolicyReview
    form_class = PolicyReviewForm
    template_name = 'policies_procedures/review_form.html'
    
    def form_valid(self, form):
        if not form.instance.completed_by:
            form.instance.completed_by = self.request.user
            form.instance.completion_date = timezone.now().date()
        messages.success(self.request, 'Policy review updated')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('policies_procedures:policy_detail', kwargs={'pk': self.object.policy.pk})


@login_required
def compliance_dashboard(request):
    """Compliance monitoring dashboard"""
    # Get compliance metrics
    total_checks = PolicyComplianceCheck.objects.count()
    compliant = PolicyComplianceCheck.objects.filter(compliance_status='fully_compliant').count()
    non_compliant = PolicyComplianceCheck.objects.filter(compliance_status='non_compliant').count()
    overdue_actions = PolicyComplianceCheck.objects.filter(
        completed=False,
        due_date__lt=timezone.now().date()
    ).count()
    
    # Recent checks
    recent_checks = PolicyComplianceCheck.objects.order_by('-check_date')[:10]
    
    # Policies by category compliance
    category_compliance = Policy.objects.values('category').annotate(
        total=Count('id'),
        compliant=Count('compliance_checks', filter=Q(compliance_checks__compliance_status='fully_compliant'))
    )
    
    context = {
        'total_checks': total_checks,
        'compliant': compliant,
        'non_compliant': non_compliant,
        'overdue_actions': overdue_actions,
        'recent_checks': recent_checks,
        'category_compliance': category_compliance,
    }
    return render(request, 'policies_procedures/compliance_dashboard.html', context)


class PolicyComplianceCheckCreateView(LoginRequiredMixin, CreateView):
    """Conduct a compliance check"""
    model = PolicyComplianceCheck
    form_class = PolicyComplianceCheckForm
    template_name = 'policies_procedures/compliance_form.html'
    success_url = reverse_lazy('policies_procedures:compliance_dashboard')
    
    def form_valid(self, form):
        form.instance.checker = self.request.user
        messages.success(self.request, 'Compliance check recorded')
        return super().form_valid(form)
