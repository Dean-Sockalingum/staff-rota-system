"""
Views for Incident & Safety Management (TQM Module 2)

Implements CRUD operations and workflows for:
- Root Cause Analysis (5 Whys + Fishbone)
- Corrective & Preventive Actions (CAPA)
- Duty of Candour (Scotland Act 2016)
- Incident Trend Analysis

Complies with:
- Care Inspectorate Scotland quality indicators
- Scottish Patient Safety Programme (SPSP)
- Health Improvement Scotland (HIS) QMS
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
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

from .models import (
    RootCauseAnalysis, CorrectivePreventiveAction,
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
    - Overdue CAPAs
    - Active Duty of Candour cases
    - Recent trend analyses
    - Key performance indicators
    """
    template_name = 'incident_safety/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get pending RCAs (incidents without completed RCA)
        context['pending_rcas'] = RootCauseAnalysis.objects.filter(
            approval_status__in=['DRAFT', 'UNDER_REVIEW', 'NEEDS_REVISION']
        ).select_related('incident', 'lead_investigator').order_by('-created_at')[:5]
        
        # Get overdue CAPAs
        context['overdue_capas'] = CorrectivePreventiveAction.objects.filter(
            status__in=['IDENTIFIED', 'IN_PROGRESS', 'PENDING_VERIFICATION'],
            target_completion_date__lt=timezone.now().date()
        ).select_related('incident', 'action_owner').order_by('target_completion_date')[:5]
        
        # Get active Duty of Candour cases
        context['active_doc'] = DutyOfCandourRecord.objects.filter(
            status__in=['ASSESSMENT', 'NOTIFICATION', 'APOLOGY', 'INVESTIGATION']
        ).select_related('incident').order_by('-created_at')[:5]
        
        # Get recent trend analyses
        context['recent_trends'] = IncidentTrendAnalysis.objects.all().order_by('-created_at')[:3]
        
        # KPIs
        context['stats'] = {
            'total_rcas': RootCauseAnalysis.objects.count(),
            'total_capas': CorrectivePreventiveAction.objects.count(),
            'open_capas': CorrectivePreventiveAction.objects.filter(
                status__in=['IDENTIFIED', 'IN_PROGRESS']
            ).count(),
            'active_doc_cases': DutyOfCandourRecord.objects.filter(
                status__in=['ASSESSMENT', 'NOTIFICATION', 'APOLOGY', 'INVESTIGATION']
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
            queryset = queryset.filter(approval_status=status)
        
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
        # Get associated CAPAs
        context['capas'] = CorrectivePreventiveAction.objects.filter(
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
        'contributing_factor_people', 'contributing_factor_environment',
        'contributing_factor_processes', 'contributing_factor_organizational',
        'contributing_factor_external',
        'identified_problems', 'root_causes', 'evidence_collected',
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
        'contributing_factor_people', 'contributing_factor_environment',
        'contributing_factor_processes', 'contributing_factor_organizational',
        'contributing_factor_external',
        'identified_problems', 'root_causes', 'evidence_collected',
        'recommendations', 'approval_status', 'reviewer_comments'
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
# CORRECTIVE & PREVENTIVE ACTION (CAPA) VIEWS
# ============================================================================

class CAPAListView(LoginRequiredMixin, ListView):
    """List all CAPAs with filtering and sorting."""
    model = CorrectivePreventiveAction
    template_name = 'incident_safety/capa_list.html'
    context_object_name = 'capas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = CorrectivePreventiveAction.objects.select_related(
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


class CAPADetailView(LoginRequiredMixin, DetailView):
    """View detailed CAPA."""
    model = CorrectivePreventiveAction
    template_name = 'incident_safety/capa_detail.html'
    context_object_name = 'capa'


class CAPACreateView(LoginRequiredMixin, CreateView):
    """Create new CAPA for an incident."""
    model = CorrectivePreventiveAction
    template_name = 'incident_safety/capa_form.html'
    fields = [
        'root_cause_analysis', 'action_type', 'description', 'priority',
        'action_owner', 'supporting_staff', 'target_completion_date',
        'resources_required', 'success_criteria'
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
        messages.success(self.request, f'CAPA created: {form.instance.reference_number}')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('incident_safety:capa_detail', kwargs={'pk': self.object.pk})


class CAPAUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing CAPA."""
    model = CorrectivePreventiveAction
    template_name = 'incident_safety/capa_form.html'
    fields = [
        'description', 'priority', 'status', 'action_owner', 'supporting_staff',
        'target_completion_date', 'actual_completion_date', 'progress_percentage',
        'implementation_notes', 'verification_evidence', 'effectiveness_review',
        'resources_required', 'success_criteria'
    ]
    
    def form_valid(self, form):
        messages.success(self.request, 'CAPA updated successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('incident_safety:capa_detail', kwargs={'pk': self.object.pk})


class CAPAVerifyView(LoginRequiredMixin, UpdateView):
    """Quick verify CAPA completion."""
    model = CorrectivePreventiveAction
    template_name = 'incident_safety/capa_verify.html'
    fields = ['verification_evidence', 'effectiveness_review']
    
    def form_valid(self, form):
        form.instance.status = 'VERIFIED_EFFECTIVE'
        form.instance.verified_by = self.request.user
        form.instance.verified_date = timezone.now().date()
        messages.success(self.request, 'CAPA verified as effective.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('incident_safety:capa_detail', kwargs={'pk': self.object.pk})


class CAPADeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete CAPA (managers only)."""
    model = CorrectivePreventiveAction
    template_name = 'incident_safety/capa_confirm_delete.html'
    success_url = reverse_lazy('incident_safety:capa_list')
    
    def test_func(self):
        return self.request.user.role and self.request.user.role.is_management
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'CAPA deleted successfully.')
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
        'harm_level', 'status', 'family_contact_name', 'family_contact_relationship',
        'family_contact_phone', 'family_contact_email', 'family_contact_address',
        'verbal_apology_given', 'verbal_apology_date', 'verbal_apology_by',
        'written_apology_sent', 'written_apology_date', 'apology_letter',
        'investigation_findings_shared', 'investigation_findings_date'
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
        
        if doc.family_communication_log:
            doc.family_communication_log.append(communication_entry)
        else:
            doc.family_communication_log = [communication_entry]
        
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
        
        # CAPA statistics
        context['capa_stats'] = {
            'total': CorrectivePreventiveAction.objects.count(),
            'open': CorrectivePreventiveAction.objects.filter(
                status__in=['IDENTIFIED', 'IN_PROGRESS']
            ).count(),
            'overdue': CorrectivePreventiveAction.objects.filter(
                target_completion_date__lt=timezone.now().date(),
                status__in=['IDENTIFIED', 'IN_PROGRESS']
            ).count(),
            'completed_this_month': CorrectivePreventiveAction.objects.filter(
                actual_completion_date__gte=timezone.now().date().replace(day=1)
            ).count()
        }
        
        # DoC statistics
        context['doc_stats'] = {
            'total': DutyOfCandourRecord.objects.count(),
            'active': DutyOfCandourRecord.objects.filter(
                status__in=['ASSESSMENT', 'NOTIFICATION', 'APOLOGY', 'INVESTIGATION']
            ).count(),
        }
        
        return context


class ReportsView(LoginRequiredMixin, TemplateView):
    """Reports dashboard."""
    template_name = 'incident_safety/reports.html'


class ExportCAPAView(LoginRequiredMixin, View):
    """Export CAPA list to CSV."""
    
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="capa_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Reference', 'Type', 'Priority', 'Status', 'Description',
            'Owner', 'Target Date', 'Progress %', 'Created'
        ])
        
        for capa in CorrectivePreventiveAction.objects.select_related('action_owner'):
            writer.writerow([
                capa.reference_number,
                capa.get_action_type_display(),
                capa.get_priority_display(),
                capa.get_status_display(),
                capa.description,
                capa.action_owner.get_full_name() if capa.action_owner else '',
                capa.target_completion_date,
                capa.progress_percentage,
                capa.created_at.strftime('%Y-%m-%d')
            ])
        
        return response
