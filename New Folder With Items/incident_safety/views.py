"""
Views for Incident & Safety Management (TQM Module 2)

Implements CRUD operations and workflows for:
- Root Cause Analysis (5 Whys + Fishbone)
- Corrective & Preventive Actions (Safety Action Plan)
- Duty of Candour (Scotland Act 2016)
- Incident Trend Analysis

Complies with:
- Care Inspectorate Scotland quality indicators
- Scottish Patient Safety Programme (SPSP)
- Health Improvement Scotland (HIS) QMS
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
)
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
import csv
import json

from .models import (
    RootCauseAnalysis, SafetyActionPlan,
    DutyOfCandourRecord, IncidentTrendAnalysis
)
from scheduling.models import IncidentReport, CareHome, User


# ============================================================================
# DASHBOARD & OVERVIEW
# ============================================================================

class IncidentSafetyDashboardView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard for Module 2: Incident & Safety Management.
    
    Displays:
    - Pending RCAs
    - Overdue Safety Action Plans
    - Active Duty of Candour cases
    - Recent trend analyses
    - Key performance indicators
    """
    template_name = 'incident_safety/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get pending RCAs (incidents without completed RCA)
        context['pending_rcas'] = RootCauseAnalysis.objects.filter(
            status__in=['IN_PROGRESS', 'UNDER_REVIEW', 'REJECTED']
        ).select_related('incident', 'lead_investigator').order_by('-created_at')[:5]
        
        # Get overdue Safety Action Plans
        context['overdue_action_plans'] = SafetyActionPlan.objects.filter(
            status__in=['IDENTIFIED', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED'],
            target_completion_date__lt=timezone.now().date()
        ).select_related('incident', 'action_owner').order_by('target_completion_date')[:5]
        
        # Get active Duty of Candour cases
        context['active_doc'] = DutyOfCandourRecord.objects.filter(
            current_stage__in=['ASSESSMENT', 'NOTIFICATION', 'APOLOGY', 'INVESTIGATION']
        ).select_related('incident').order_by('-created_at')[:5]
        
        # Get recent trend analyses
        context['recent_trends'] = IncidentTrendAnalysis.objects.all().order_by('-generated_date')[:3]
        
        # KPIs
        context['stats'] = {
            'total_rcas': RootCauseAnalysis.objects.count(),
            'total_capas': SafetyActionPlan.objects.count(),
            'total_action_plans': SafetyActionPlan.objects.count(),
            'open_capas': SafetyActionPlan.objects.filter(
                status__in=['IDENTIFIED', 'ASSIGNED', 'IN_PROGRESS']
            ).count(),
            'open_action_plans': SafetyActionPlan.objects.filter(
                status__in=['IDENTIFIED', 'ASSIGNED', 'IN_PROGRESS']
            ).count(),
            'active_doc_cases': DutyOfCandourRecord.objects.filter(
                current_stage__in=['ASSESSMENT', 'NOTIFICATION', 'APOLOGY', 'INVESTIGATION', 'FEEDBACK']
            ).count(),
        }
        
        return context


# ============================================================================
# ROOT CAUSE ANALYSIS (RCA) VIEWS
# ============================================================================

class RCAListView(LoginRequiredMixin, ListView):
    """List all Root Cause Analyses with filtering."""
    model = RootCauseAnalysis
    template_name = 'incident_safety/rca_list.html'
    context_object_name = 'rcas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = RootCauseAnalysis.objects.select_related(
            'incident', 'lead_investigator'
        ).order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Search by incident
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(incident__description__icontains=search) |
                Q(identified_problems__icontains=search)
            )
        
        return queryset


class RCADetailView(LoginRequiredMixin, DetailView):
    """View detailed Root Cause Analysis."""
    model = RootCauseAnalysis
    template_name = 'incident_safety/rca_detail.html'
    context_object_name = 'rca'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get associated Safety Action Plans
        context['action_plans'] = SafetyActionPlan.objects.filter(
            root_cause_analysis=self.object
        ).order_by('-created_at')
        return context


class RCACreateView(LoginRequiredMixin, CreateView):
    """Create new Root Cause Analysis for an incident."""
    model = RootCauseAnalysis
    template_name = 'incident_safety/rca_form.html'
    fields = [
        'lead_investigator', 'investigation_team',
        'why_1', 'why_2', 'why_3', 'why_4', 'why_5',
        'factor_people', 'factor_environment',
        'factor_processes', 'factor_organization',
        'factor_external',
        'root_cause_summary', 'lessons_learned', 'evidence_reviewed',
        'recommendations'
    ]
    
    def dispatch(self, request, *args, **kwargs):
        self.incident = get_object_or_404(IncidentReport, pk=kwargs['incident_id'])
        # Check if RCA already exists
        if hasattr(self.incident, 'root_cause_analysis'):
            messages.warning(request, 'This incident already has an RCA. Please edit the existing one.')
            return redirect('incident_safety:rca_detail', pk=self.incident.root_cause_analysis.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['incident'] = self.incident
        return context
    
    def form_valid(self, form):
        form.instance.incident = self.incident
        form.instance.analysis_start_date = timezone.now().date()
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Root Cause Analysis created successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('incident_safety:rca_detail', kwargs={'pk': self.object.pk})


class RCAUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing Root Cause Analysis."""
    model = RootCauseAnalysis
    template_name = 'incident_safety/rca_form.html'
    fields = [
        'lead_investigator', 'investigation_team',
        'why_1', 'why_2', 'why_3', 'why_4', 'why_5',
        'factor_people', 'factor_environment',
        'factor_processes', 'factor_organization',
        'factor_external',
        'root_cause_summary', 'lessons_learned', 'evidence_reviewed',
        'recommendations', 'status', 'approval_comments'
    ]
    
    def form_valid(self, form):
        messages.success(self.request, 'Root Cause Analysis updated successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('incident_safety:rca_detail', kwargs={'pk': self.object.pk})


class RCADeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete Root Cause Analysis (managers only)."""
    model = RootCauseAnalysis
    template_name = 'incident_safety/rca_confirm_delete.html'
    success_url = reverse_lazy('incident_safety:rca_list')
    
    def test_func(self):
        return self.request.user.role and self.request.user.role.is_management
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Root Cause Analysis deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# CORRECTIVE & PREVENTIVE ACTION (Safety Action Plan) VIEWS
# ============================================================================

class SafetyActionPlanListView(LoginRequiredMixin, ListView):
    """List all Safety Action Plans with filtering and sorting."""
    model = SafetyActionPlan
    template_name = 'incident_safety/action_plan_list.html'
    context_object_name = 'action_plans'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        """Add no-cache headers to prevent browser caching."""
        response = super().dispatch(request, *args, **kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    
    def get_queryset(self):
        queryset = SafetyActionPlan.objects.select_related(
            'incident', 'action_owner'
        ).order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter overdue
        if self.request.GET.get('overdue') == 'true':
            queryset = queryset.filter(
                target_completion_date__lt=timezone.now().date(),
                status__in=['IDENTIFIED', 'IN_PROGRESS', 'PENDING_VERIFICATION']
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from scheduling.models import CareHome
        
        # Calculate statistics
        all_plans = SafetyActionPlan.objects.all()
        context['total_count'] = all_plans.count()
        context['active_count'] = all_plans.filter(
            status__in=['IDENTIFIED', 'IN_PROGRESS', 'ASSIGNED', 'PLANNED']
        ).count()
        context['overdue_count'] = all_plans.filter(
            target_completion_date__lt=timezone.now().date(),
            status__in=['IDENTIFIED', 'IN_PROGRESS', 'PENDING_VERIFICATION', 'ASSIGNED', 'PLANNED']
        ).count()
        context['completed_count'] = all_plans.filter(
            status__in=['VERIFIED', 'EFFECTIVE', 'CLOSED']
        ).count()
        
        # Add care homes for filter
        context['care_homes'] = CareHome.objects.all()
        
        return context


class SafetyActionPlanDetailView(LoginRequiredMixin, DetailView):
    """View detailed Safety Action Plan."""
    model = SafetyActionPlan
    template_name = 'incident_safety/action_plan_detail.html'
    context_object_name = 'capa'


class SafetyActionPlanCreateView(LoginRequiredMixin, CreateView):
    """Create new Safety Action Plan for an incident."""
    model = SafetyActionPlan
    template_name = 'incident_safety/action_plan_form.html'
    fields = [
        'root_cause_analysis', 'action_type', 'problem_statement', 'action_description',
        'expected_outcome', 'priority', 'action_owner', 'supporting_staff', 
        'target_completion_date', 'resources_required', 'barriers_identified',
        'implementation_plan'
    ]
    
    def dispatch(self, request, *args, **kwargs):
        self.incident = get_object_or_404(IncidentReport, pk=kwargs['incident_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['incident'] = self.incident
        # Get RCA if exists
        if hasattr(self.incident, 'root_cause_analysis'):
            context['rca'] = self.incident.root_cause_analysis
        return context
    
    def form_valid(self, form):
        form.instance.incident = self.incident
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Health and Safety Action Plan created: {form.instance.reference_number}')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('incident_safety:action_plan_detail', kwargs={'pk': self.object.pk})


class SafetyActionPlanUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing Safety Action Plan."""
    model = SafetyActionPlan
    template_name = 'incident_safety/action_plan_form.html'
    fields = [
        'root_cause_analysis', 'action_type', 'problem_statement', 'action_description',
        'expected_outcome', 'priority', 'status', 'action_owner', 'supporting_staff',
        'target_completion_date', 'actual_completion_date', 'percent_complete',
        'implementation_plan', 'progress_notes', 'resources_required', 
        'barriers_identified'
    ]
    
    def form_valid(self, form):
        messages.success(self.request, 'Health and Safety Action Plan updated successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('incident_safety:action_plan_detail', kwargs={'pk': self.object.pk})


class SafetyActionPlanVerifyView(LoginRequiredMixin, UpdateView):
    """Quick verify Safety Action Plan completion."""
    model = SafetyActionPlan
    template_name = 'incident_safety/action_plan_verify.html'
    context_object_name = 'action_plan'
    fields = ['verification_outcome', 'effectiveness_review_notes']
    
    def form_valid(self, form):
        form.instance.status = 'VERIFIED'
        form.instance.verified_by = self.request.user
        form.instance.verification_date = timezone.now().date()
        messages.success(self.request, 'Health and Safety Action Plan verified as effective.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('incident_safety:action_plan_detail', kwargs={'pk': self.object.pk})


class SafetyActionPlanDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete Safety Action Plan (managers only)."""
    model = SafetyActionPlan
    template_name = 'incident_safety/action_plan_confirm_delete.html'
    success_url = reverse_lazy('incident_safety:capa_list')
    
    def test_func(self):
        return self.request.user.role and self.request.user.role.is_management
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Safety Action Plan deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# DUTY OF CANDOUR (DoC) VIEWS
# ============================================================================

class DoCListView(LoginRequiredMixin, ListView):
    """List all Duty of Candour records."""
    model = DutyOfCandourRecord
    template_name = 'incident_safety/doc_list.html'
    context_object_name = 'doc_records'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = DutyOfCandourRecord.objects.select_related('incident').order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by compliance
        if self.request.GET.get('non_compliant') == 'true':
            queryset = [doc for doc in queryset if doc.get_compliance_status()['compliance_percentage'] < 100]
        
        return queryset


class DoCDetailView(LoginRequiredMixin, DetailView):
    """View detailed Duty of Candour record."""
    model = DutyOfCandourRecord
    template_name = 'incident_safety/doc_detail.html'
    context_object_name = 'doc'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['compliance'] = self.object.get_compliance_status()
        context['within_window'] = self.object.is_within_notification_window()
        return context


class DoCCreateView(LoginRequiredMixin, CreateView):
    """Create new Duty of Candour record."""
    model = DutyOfCandourRecord
    template_name = 'incident_safety/doc_form.html'
    fields = [
        'harm_level', 'family_contact_name', 'family_contact_relationship',
        'family_contact_phone', 'family_contact_email', 'family_contact_address'
    ]
    
    def dispatch(self, request, *args, **kwargs):
        self.incident = get_object_or_404(IncidentReport, pk=kwargs['incident_id'])
        # Check if DoC already exists
        if hasattr(self.incident, 'duty_of_candour'):
            messages.warning(request, 'This incident already has a Duty of Candour record.')
            return redirect('incident_safety:doc_detail', pk=self.incident.duty_of_candour.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['incident'] = self.incident
        return context
    
    def form_valid(self, form):
        form.instance.incident = self.incident
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Duty of Candour record created. Please complete notification within 24 hours.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('incident_safety:doc_detail', kwargs={'pk': self.object.pk})


class DoCUpdateView(LoginRequiredMixin, UpdateView):
    """Update Duty of Candour record."""
    model = DutyOfCandourRecord
    template_name = 'incident_safety/doc_form.html'
    fields = [
        'harm_level', 'current_stage', 'family_contact_name', 'family_contact_relationship',
        'family_contact_phone', 'family_contact_email', 'family_preferred_contact_method',
        'apology_provided', 'apology_date', 'apology_method',
        'apology_letter_sent', 'apology_letter_file',
        'investigation_findings_shared', 'findings_shared_date'
    ]
    
    def form_valid(self, form):
        messages.success(self.request, 'Duty of Candour record updated.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('incident_safety:doc_detail', kwargs={'pk': self.object.pk})


class DoCAddCommunicationView(LoginRequiredMixin, View):
    """Add communication entry to DoC record."""
    
    def post(self, request, pk):
        doc = get_object_or_404(DutyOfCandourRecord, pk=pk)
        
        communication_entry = {
            'date': timezone.now().isoformat(),
            'type': request.POST.get('type'),
            'method': request.POST.get('method'),
            'summary': request.POST.get('summary'),
            'recorded_by': request.user.get_full_name()
        }
        
        if doc.communication_log:
            doc.communication_log.append(communication_entry)
        else:
            doc.communication_log = [communication_entry]
        
        doc.save()
        messages.success(request, 'Communication logged successfully.')
        return redirect('incident_safety:doc_detail', pk=pk)


class DoCDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete Duty of Candour record (managers only)."""
    model = DutyOfCandourRecord
    template_name = 'incident_safety/doc_confirm_delete.html'
    success_url = reverse_lazy('incident_safety:doc_list')
    
    def test_func(self):
        return self.request.user.role and self.request.user.role.is_management
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Duty of Candour record deleted.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# INCIDENT TREND ANALYSIS VIEWS
# ============================================================================

class TrendAnalysisListView(LoginRequiredMixin, ListView):
    """List all trend analyses."""
    model = IncidentTrendAnalysis
    template_name = 'incident_safety/trend_list.html'
    context_object_name = 'trends'
    paginate_by = 20


class TrendAnalysisDetailView(LoginRequiredMixin, DetailView):
    """View detailed trend analysis."""
    model = IncidentTrendAnalysis
    template_name = 'incident_safety/trend_detail.html'
    context_object_name = 'trend'


class TrendAnalysisCreateView(LoginRequiredMixin, CreateView):
    """Create new trend analysis."""
    model = IncidentTrendAnalysis
    template_name = 'incident_safety/trend_form.html'
    fields = [
        'period', 'start_date', 'end_date', 'care_home', 'description',
        'total_incidents', 'incidents_by_type', 'incidents_by_severity',
        'trend_direction', 'peak_times', 'staffing_correlation',
        'recommendations', 'action_required'
    ]
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Trend analysis created successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('incident_safety:trend_detail', kwargs={'pk': self.object.pk})


class TrendAnalysisDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete trend analysis (managers only)."""
    model = IncidentTrendAnalysis
    template_name = 'incident_safety/trend_confirm_delete.html'
    success_url = reverse_lazy('incident_safety:trend_list')
    
    def test_func(self):
        return self.request.user.role and self.request.user.role.is_management
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Trend analysis deleted.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# ANALYTICS & REPORTS
# ============================================================================

class AnalyticsView(LoginRequiredMixin, TemplateView):
    """Analytics dashboard for Module 2."""
    template_name = 'incident_safety/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Safety Action Plan statistics
        context['capa_stats'] = {
            'total': SafetyActionPlan.objects.count(),
            'open': SafetyActionPlan.objects.filter(
                status__in=['IDENTIFIED', 'IN_PROGRESS']
            ).count(),
            'overdue': SafetyActionPlan.objects.filter(
                target_completion_date__lt=timezone.now().date(),
                status__in=['IDENTIFIED', 'IN_PROGRESS']
            ).count(),
            'completed_this_month': SafetyActionPlan.objects.filter(
                actual_completion_date__gte=timezone.now().date().replace(day=1)
            ).count()
        }
        
        # DoC statistics
        context['doc_stats'] = {
            'total': DutyOfCandourRecord.objects.count(),
            'active': DutyOfCandourRecord.objects.filter(
                current_stage__in=['ASSESSMENT', 'NOTIFICATION', 'APOLOGY', 'INVESTIGATION']
            ).count(),
        }
        
        return context


class ReportsView(LoginRequiredMixin, TemplateView):
    """Reports dashboard."""
    template_name = 'incident_safety/reports.html'


class ExportSafetyActionPlanView(LoginRequiredMixin, View):
    """Export Safety Action Plan list to CSV."""
    
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="capa_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Reference', 'Type', 'Priority', 'Status', 'Description',
            'Owner', 'Target Date', 'Progress %', 'Created'
        ])
        
        for capa in SafetyActionPlan.objects.select_related('action_owner'):
            writer.writerow([
                capa.reference_number,
                capa.get_action_type_display(),
                capa.get_priority_display(),
                capa.get_status_display(),
                capa.action_description,
                capa.action_owner.get_full_name() if capa.action_owner else '',
                capa.target_completion_date,
                capa.percent_complete,
                capa.created_at.strftime('%Y-%m-%d')
            ])
        
        return response


# ============================================================================
# ENHANCED RCA WORKFLOW VIEWS
# ============================================================================

@login_required
def rca_fishbone_view(request, pk):
    """Interactive Fishbone (Ishikawa) diagram for RCA."""
    rca = get_object_or_404(RootCauseAnalysis, pk=pk)
    
    # Structure data for D3.js visualization
    fishbone_data = {
        'incident': {
            'reference': rca.incident.reference_number,
            'description': rca.incident.description[:100] if rca.incident.description else '',
        },
        'categories': [
            {
                'name': 'People',
                'factors': rca.factor_people.split('\n') if rca.factor_people else [],
                'color': '#3b82f6'
            },
            {
                'name': 'Environment',
                'factors': rca.factor_environment.split('\n') if rca.factor_environment else [],
                'color': '#10b981'
            },
            {
                'name': 'Processes',
                'factors': rca.factor_processes.split('\n') if rca.factor_processes else [],
                'color': '#f59e0b'
            },
            {
                'name': 'Organization',
                'factors': rca.factor_organization.split('\n') if rca.factor_organization else [],
                'color': '#8b5cf6'
            },
            {
                'name': 'External',
                'factors': rca.factor_external.split('\n') if rca.factor_external else [],
                'color': '#ef4444'
            }
        ],
        'root_cause': rca.root_cause_summary if rca.root_cause_summary else 'To be determined'
    }
    
    context = {
        'rca': rca,
        'fishbone_data': fishbone_data,
    }
    
    return render(request, 'incident_safety/rca_fishbone.html', context)


@login_required
def rca_five_whys_view(request, pk):
    """Interactive 5 Whys analysis view."""
    rca = get_object_or_404(RootCauseAnalysis, pk=pk)
    
    whys_data = [
        {'level': 1, 'question': 'Why did this incident happen?', 'answer': rca.why_1 or ''},
        {'level': 2, 'question': 'Why did the first cause occur?', 'answer': rca.why_2 or ''},
        {'level': 3, 'question': 'Why did the second cause occur?', 'answer': rca.why_3 or ''},
        {'level': 4, 'question': 'Why did the third cause occur?', 'answer': rca.why_4 or ''},
        {'level': 5, 'question': 'Why did the fourth cause occur? (Root cause)', 'answer': rca.why_5 or ''},
    ]
    
    context = {
        'rca': rca,
        'whys_data': whys_data,
    }
    
    return render(request, 'incident_safety/rca_five_whys.html', context)


@login_required
def rca_progress_update(request, pk):
    """Update RCA progress and status."""
    rca = get_object_or_404(RootCauseAnalysis, pk=pk)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        progress_notes = request.POST.get('progress_notes')
        
        if status:
            rca.status = status
        
        if progress_notes:
            # Add to progress log (assuming we add this field)
            if not hasattr(rca, 'progress_log'):
                rca.progress_log = []
            rca.progress_log.append({
                'date': timezone.now().isoformat(),
                'user': request.user.get_full_name(),
                'notes': progress_notes
            })
        
        rca.save()
        messages.success(request, 'RCA progress updated successfully.')
        return redirect('incident_safety:rca_detail', pk=rca.pk)
    
    return redirect('incident_safety:rca_detail', pk=pk)


# ============================================================================
# LEARNING REPOSITORY VIEWS
# ============================================================================

@login_required
def learning_repository_view(request):
    """
    Learning Repository - showcases lessons learned from all RCAs.
    Searchable database of incident learnings for staff education.
    """
    # Get all approved RCAs with lessons
    rcas_with_lessons = RootCauseAnalysis.objects.filter(
        status='APPROVED',
        lessons_learned__isnull=False
    ).select_related('incident').exclude(lessons_learned='').order_by('-approved_date')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        rcas_with_lessons = rcas_with_lessons.filter(
            Q(lessons_learned__icontains=search_query) |
            Q(recommendations__icontains=search_query) |
            Q(incident__description__icontains=search_query)
        )
    
    # Category filter
    category = request.GET.get('category', '')
    if category:
        rcas_with_lessons = rcas_with_lessons.filter(incident__incident_type=category)
    
    # Group lessons by theme (simple keyword extraction)
    themes = {}
    for rca in rcas_with_lessons:
        # Extract first sentence as theme
        lesson = rca.lessons_learned
        theme = lesson.split('.')[0][:100] if lesson else 'General Learning'
        
        if theme not in themes:
            themes[theme] = []
        themes[theme].append(rca)
    
    context = {
        'rcas': rcas_with_lessons[:20],  # Paginate to 20
        'themes': themes,
        'search_query': search_query,
        'total_lessons': rcas_with_lessons.count(),
    }
    
    return render(request, 'incident_safety/learning_repository.html', context)


# ============================================================================
# ADVANCED TREND ANALYSIS
# ============================================================================

@login_required
def trend_analysis_dashboard(request):
    """
    Advanced trend analysis dashboard with Chart.js visualizations.
    Shows incident patterns, staffing correlations, and predictive insights.
    """
    from django.db.models import Count, Avg
    from django.db.models.functions import TruncMonth
    from scheduling.models import IncidentReport, CareHome
    from dateutil.relativedelta import relativedelta
    import json
    
    # Date range (default last 12 months)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)
    
    if request.GET.get('start_date'):
        start_date = timezone.datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = timezone.datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    
    # Monthly incident trends
    monthly_incidents = IncidentReport.objects.filter(
        incident_date__gte=start_date,
        incident_date__lte=end_date
    ).annotate(
        month=TruncMonth('incident_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Incidents by type
    incidents_by_type = IncidentReport.objects.filter(
        incident_date__gte=start_date,
        incident_date__lte=end_date
    ).values('incident_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Incidents by severity
    incidents_by_severity = IncidentReport.objects.filter(
        incident_date__gte=start_date,
        incident_date__lte=end_date
    ).values('severity').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # RCA completion rate
    total_serious_incidents = IncidentReport.objects.filter(
        incident_date__gte=start_date,
        incident_date__lte=end_date,
        severity__in=['CRITICAL', 'HIGH']
    ).count()
    
    completed_rcas = RootCauseAnalysis.objects.filter(
        incident__incident_date__gte=start_date,
        incident__incident_date__lte=end_date,
        status='APPROVED'
    ).count()
    
    rca_completion_rate = (completed_rcas / total_serious_incidents * 100) if total_serious_incidents > 0 else 0
    
    # Safety Action Plan effectiveness
    verified_capas = SafetyActionPlan.objects.filter(
        status='VERIFIED'
    ).count()
    total_action_plans = SafetyActionPlan.objects.count()
    capa_effectiveness_rate = (verified_capas / total_action_plans * 100) if total_action_plans > 0 else 0
    
    # Format data for Chart.js
    # Trend data for line chart
    trend_data = {
        'months': [item['month'].strftime('%b %Y') for item in monthly_incidents],
        'counts': [item['count'] for item in monthly_incidents]
    }
    
    # Severity data for doughnut chart
    severity_data = {
        'labels': [item['severity'] if item['severity'] else 'Unknown' for item in incidents_by_severity],
        'values': [item['count'] for item in incidents_by_severity]
    }
    
    # Type data for bar chart
    type_data = {
        'labels': [item['incident_type'] if item['incident_type'] else 'Unknown' for item in incidents_by_type],
        'values': [item['count'] for item in incidents_by_type]
    }
    
    # Location data (incidents by location text field)
    incidents_by_location = IncidentReport.objects.filter(
        incident_date__gte=start_date,
        incident_date__lte=end_date
    ).exclude(
        location__isnull=True
    ).exclude(
        location=''
    ).values('location').annotate(
        count=Count('id')
    ).order_by('-count')[:10]  # Top 10 locations
    
    location_data = {
        'labels': [item['location'] for item in incidents_by_location],
        'values': [item['count'] for item in incidents_by_location]
    }
    
    # RCA Performance Metrics (monthly completion rate and effectiveness)
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    # Get last 12 months of RCA data
    months_list = []
    completion_rates = []
    effectiveness_rates = []
    
    for i in range(11, -1, -1):
        month_date = end_date - relativedelta(months=i)
        month_start = month_date.replace(day=1)
        month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
        
        # Incidents requiring RCA that month
        month_serious_incidents = IncidentReport.objects.filter(
            incident_date__gte=month_start,
            incident_date__lte=month_end,
            severity__in=['CRITICAL', 'HIGH']
        ).count()
        
        # RCAs completed for those incidents
        month_completed_rcas = RootCauseAnalysis.objects.filter(
            incident__incident_date__gte=month_start,
            incident__incident_date__lte=month_end,
            status='APPROVED'
        ).count()
        
        # Action plans for that month
        month_verified_saps = SafetyActionPlan.objects.filter(
            created_at__gte=month_start,
            created_at__lte=month_end,
            status='VERIFIED'
        ).count()
        
        month_total_saps = SafetyActionPlan.objects.filter(
            created_at__gte=month_start,
            created_at__lte=month_end
        ).count()
        
        months_list.append(month_date.strftime('%b %Y'))
        completion_rates.append(
            round((month_completed_rcas / month_serious_incidents * 100), 1) if month_serious_incidents > 0 else 0
        )
        effectiveness_rates.append(
            round((month_verified_saps / month_total_saps * 100), 1) if month_total_saps > 0 else 0
        )
    
    rca_metrics = {
        'months': months_list,
        'completion_rate': completion_rates,
        'effectiveness': effectiveness_rates
    }
    
    # KPIs for insights
    kpis = {
        'incident_reduction': 15.3,  # Placeholder - could calculate from previous period
        'rca_completion_rate': rca_completion_rate,
        'action_plan_effectiveness': capa_effectiveness_rate
    }
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'trend_data': json.dumps(trend_data),
        'severity_data': json.dumps(severity_data),
        'type_data': json.dumps(type_data),
        'location_data': json.dumps(location_data),
        'rca_metrics': json.dumps(rca_metrics),
        'kpis': kpis,
        'rca_completion_rate': round(rca_completion_rate, 1),
        'capa_effectiveness_rate': round(capa_effectiveness_rate, 1),
        'total_incidents': IncidentReport.objects.filter(
            incident_date__gte=start_date,
            incident_date__lte=end_date
        ).count(),
        'serious_incidents': total_serious_incidents,
        'completed_rcas': completed_rcas,
        'care_homes': CareHome.objects.all().order_by('name'),
    }
    
    return render(request, 'incident_safety/trend_analysis_dashboard.html', context)


# ============================================================================
# DUTY OF CANDOUR WORKFLOW ENHANCEMENTS
# ============================================================================

@login_required
def doc_workflow_tracker(request, pk):
    """
    Visual workflow tracker for Duty of Candour process.
    Shows progress through the 7-stage DoC process with timeline.
    """
    doc = get_object_or_404(DutyOfCandourRecord, pk=pk)
    
    # Define workflow stages with completion status
    workflow_stages = [
        {
            'name': 'Assessment',
            'code': 'ASSESSMENT',
            'completed': doc.assessment_date is not None,
            'date': doc.assessment_date,
            'description': 'Determine if Duty of Candour applies'
        },
        {
            'name': 'Notification',
            'code': 'NOTIFICATION',
            'completed': doc.notification_date is not None,
            'date': doc.notification_date,
            'description': 'Initial contact with family (within 24 hours for serious harm)'
        },
        {
            'name': 'Apology',
            'code': 'APOLOGY',
            'completed': doc.apology_provided,
            'date': doc.apology_date,
            'description': 'Formal apology provided to family'
        },
        {
            'name': 'Investigation',
            'code': 'INVESTIGATION',
            'completed': doc.investigation_findings_shared,
            'date': None,  # Can link to RCA completion date
            'description': 'Incident investigation and RCA completed'
        },
        {
            'name': 'Feedback',
            'code': 'FEEDBACK',
            'completed': doc.findings_shared_date is not None,
            'date': doc.findings_shared_date,
            'description': 'Share investigation findings with family'
        },
        {
            'name': 'Actions',
            'code': 'ACTIONS',
            'completed': doc.actions_shared_with_family,
            'date': doc.actions_shared_date,
            'description': 'Share corrective actions with family'
        },
        {
            'name': 'Review',
            'code': 'REVIEW',
            'completed': doc.follow_up_date is not None,
            'date': doc.follow_up_date,
            'description': 'Follow-up review with family'
        },
    ]
    
    # Calculate progress percentage
    completed_stages = sum(1 for stage in workflow_stages if stage['completed'])
    progress_percentage = (completed_stages / len(workflow_stages)) * 100
    
    # Get linked RCA if exists
    linked_rca = None
    if hasattr(doc.incident, 'root_cause_analysis'):
        linked_rca = doc.incident.root_cause_analysis
    
    context = {
        'doc': doc,
        'workflow_stages': workflow_stages,
        'progress_percentage': round(progress_percentage, 1),
        'completed_stages': completed_stages,
        'total_stages': len(workflow_stages),
        'linked_rca': linked_rca,
    }
    
    return render(request, 'incident_safety/doc_workflow_tracker.html', context)
