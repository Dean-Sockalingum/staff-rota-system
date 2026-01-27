"""
Views for the PDSA Tracker (TQM Module 1).

This module provides all views for the Quality Audits app, including:
- Dashboard and project management views
- PDSA cycle management views
- Data point collection views
- ML-powered feature views (SMART aim generation, hypothesis suggestions, etc.)
- Team management views
- Reporting and export views
- JSON API endpoints for charts and real-time data

Author: Dean Sockalingum
Created: 2026-01-13
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.db.models import Count, Q, Avg, Max, Case, When, Value, IntegerField
from django.utils import timezone
from datetime import timedelta
import json

from .models import (
    PDSAProject, PDSACycle, PDSATeamMember, PDSADataPoint, PDSAChatbotLog,
    QualityImprovementAction, QIAUpdate, QIAReview
)
from .ml.smart_aim_generator import SMARTAimGenerator
from .ml.hypothesis_suggester import HypothesisSuggester
from .ml.data_analyzer import PDSADataAnalyzer
from .ml.success_predictor import PDSASuccessPredictor
from .ml.pdsa_chatbot import PDSAChatbot


# ============================================================================
# DASHBOARD VIEWS
# ============================================================================

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard for PDSA Tracker.
    
    Displays:
    - Summary statistics (total projects, active cycles, success rate)
    - Recent projects and cycles
    - Upcoming review dates
    - Quick access to ML features
    """
    template_name = 'quality_audits/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get projects accessible by user
        user = self.request.user
        projects = PDSAProject.objects.filter(
            Q(created_by=user) | Q(team_members__user=user)
        ).distinct()
        
        # Summary statistics
        context['total_projects'] = projects.count()
        context['active_projects'] = projects.filter(status='active').count()
        context['completed_projects'] = projects.filter(status='completed').count()
        
        # Cycles statistics
        all_cycles = PDSACycle.objects.filter(project__in=projects)
        context['total_cycles'] = all_cycles.count()
        context['active_cycles'] = all_cycles.filter(act_completed_date__isnull=True).count()
        
        # Success metrics
        completed_cycles = all_cycles.filter(act_completed_date__isnull=False)
        if completed_cycles.exists():
            context['avg_success_score'] = completed_cycles.aggregate(
                Avg('ai_success_score')
            )['ai_success_score__avg'] or 0
        else:
            context['avg_success_score'] = 0
        
        # Recent activity
        context['recent_projects'] = projects.order_by('-created_at')[:5]
        context['recent_cycles'] = all_cycles.order_by('-created_at')[:5]
        
        # Upcoming reviews (cycles near completion in next 7 days)
        next_week = timezone.now() + timedelta(days=7)
        context['upcoming_reviews'] = all_cycles.filter(
            act_completed_date__isnull=True,
            study_completed_date__isnull=False
        ).order_by('-study_completed_date')[:5]
        
        return context


# ============================================================================
# PROJECT CRUD VIEWS
# ============================================================================

class ProjectListView(LoginRequiredMixin, ListView):
    """List all PDSA projects accessible by the current user."""
    model = PDSAProject
    template_name = 'quality_audits/project_list.html'
    context_object_name = 'projects'
    paginate_by = 20
    
    def get_queryset(self):
        """Filter projects by user access and optional search/filter params."""
        user = self.request.user
        queryset = PDSAProject.objects.filter(
            Q(created_by=user) | Q(team_members__user=user)
        ).distinct().select_related('created_by').prefetch_related('team_members')
        
        # Search by project title or aim
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(aim_statement__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by care home
        care_home = self.request.GET.get('care_home', '')
        if care_home:
            queryset = queryset.filter(care_home__id=care_home)
        
        # Sort
        sort = self.request.GET.get('sort', '-created_at')
        queryset = queryset.order_by(sort)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['sort'] = self.request.GET.get('sort', '-created_at')
        return context


class ProjectDetailView(LoginRequiredMixin, DetailView):
    """Display detailed view of a PDSA project."""
    model = PDSAProject
    template_name = 'quality_audits/project_detail.html'
    context_object_name = 'project'
    
    def get_queryset(self):
        """Ensure user has access to this project."""
        user = self.request.user
        return PDSAProject.objects.filter(
            Q(created_by=user) | Q(team_members__user=user)
        ).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        
        # Get all cycles for this project
        context['cycles'] = project.cycles.all().order_by('-created_at')
        
        # Calculate project metrics
        cycles = project.cycles.all()
        context['total_cycles'] = cycles.count()
        context['completed_cycles'] = cycles.filter(act_completed_date__isnull=False).count()
        context['active_cycles'] = cycles.filter(act_completed_date__isnull=True).count()
        
        # Get all data points across all cycles
        all_data_points = PDSADataPoint.objects.filter(
            cycle__project=project
        ).order_by('measurement_date')
        context['total_data_points'] = all_data_points.count()
        
        # Calculate days since start
        if project.start_date:
            context['days_active'] = (timezone.now().date() - project.start_date).days
        
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """Create a new PDSA project."""
    model = PDSAProject
    template_name = 'quality_audits/project_form.html'
    fields = [
        'title', 'aim_statement', 'problem_description', 'target_population',
        'care_home', 'unit', 'category', 'priority',
        'baseline_value', 'target_value', 'measurement_unit',
        'start_date', 'target_completion_date'
    ]
    
    def form_valid(self, form):
        """Set the lead_user and generate AI aim if requested."""
        form.instance.lead_user = self.request.user
        
        # Check if AI aim generation was requested
        generate_ai = self.request.POST.get('generate_ai_aim', False)
        if generate_ai and form.instance.aim_statement:
            try:
                aim_generator = SMARTAimGenerator()
                improved_aim = aim_generator.improve_aim(form.instance.aim_statement)
                form.instance.aim_statement = improved_aim['improved_aim']
                form.instance.ai_aim_generated = True
                messages.success(
                    self.request,
                    f"AI-enhanced SMART aim generated (SMART score: {improved_aim['smartness_score']}%)"
                )
            except Exception as e:
                messages.warning(
                    self.request,
                    f"Could not generate AI aim: {str(e)}"
                )
        
        messages.success(self.request, f"Project '{form.instance.title}' created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('quality_audits:project_detail', kwargs={'pk': self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing PDSA project."""
    model = PDSAProject
    template_name = 'quality_audits/project_form.html'
    fields = [
        'title', 'aim_statement', 'problem_description', 'target_population',
        'care_home', 'unit', 'category', 'priority', 'status',
        'baseline_value', 'target_value', 'measurement_unit',
        'start_date', 'target_completion_date', 'actual_completion_date'
    ]
    
    def test_func(self):
        """Only allow project lead to edit."""
        project = self.get_object()
        return project.lead_user == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, f"Project '{form.instance.title}' updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('quality_audits:project_detail', kwargs={'pk': self.object.pk})


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a PDSA project."""
    model = PDSAProject
    template_name = 'quality_audits/project_confirm_delete.html'
    success_url = reverse_lazy('quality_audits:project_list')
    
    def test_func(self):
        """Only allow project lead to delete."""
        project = self.get_object()
        return project.lead_user == self.request.user
    
    def delete(self, request, *args, **kwargs):
        project = self.get_object()
        messages.success(request, f"Project '{project.title}' deleted successfully!")
        return super().delete(request, *args, **kwargs)


# ============================================================================
# PDSA CYCLE CRUD VIEWS
# ============================================================================

class CycleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a new PDSA cycle for a project."""
    model = PDSACycle
    template_name = 'quality_audits/cycle_form.html'
    fields = [
        'cycle_number', 'cycle_objective', 'plan_hypothesis', 'plan_changes',
        'plan_prediction', 'plan_data_collection', 'do_implementation_start',
        'do_implementation_end', 'do_observations', 'do_challenges',
        'study_data_analysis', 'study_findings', 'study_unexpected_results',
        'act_decision', 'act_next_steps', 'act_completed_date'
    ]
    
    def dispatch(self, request, *args, **kwargs):
        """Get the project and ensure user has access."""
        self.project = get_object_or_404(PDSAProject, pk=kwargs['project_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def test_func(self):
        """Only allow project creator or team members to add cycles."""
        user = self.request.user
        return self.project.created_by == user or self.project.team_members.filter(user=user).exists()
    
    def form_valid(self, form):
        form.instance.project = self.project
        
        # Auto-increment cycle number if not provided
        if not form.instance.cycle_number:
            last_cycle = self.project.cycles.order_by('-cycle_number').first()
            form.instance.cycle_number = (last_cycle.cycle_number + 1) if last_cycle else 1
        
        messages.success(self.request, f"Cycle #{form.instance.cycle_number} created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('quality_audits:cycle_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context


class CycleDetailView(LoginRequiredMixin, DetailView):
    """Display detailed view of a PDSA cycle."""
    model = PDSACycle
    template_name = 'quality_audits/cycle_detail.html'
    context_object_name = 'cycle'
    
    def get_queryset(self):
        """Ensure user has access to this cycle's project."""
        user = self.request.user
        return PDSACycle.objects.filter(
            Q(project__created_by=user) | Q(project__team_members__user=user)
        ).distinct().select_related('project')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cycle = self.object
        
        # Get all data points for this cycle
        data_points = cycle.data_points.all().order_by('measurement_date')
        context['data_points'] = data_points
        context['data_point_count'] = data_points.count()
        
        # Calculate cycle duration
        if cycle.do_implementation_start and cycle.do_implementation_end:
            context['cycle_duration'] = (
                cycle.do_implementation_end - cycle.do_implementation_start
            ).days
        
        return context


class CycleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing PDSA cycle."""
    model = PDSACycle
    template_name = 'quality_audits/cycle_form.html'
    fields = [
        'cycle_number', 'cycle_objective', 'plan_hypothesis', 'plan_changes',
        'plan_prediction', 'plan_data_collection', 'do_implementation_start',
        'do_implementation_end', 'do_observations', 'do_challenges',
        'study_data_analysis', 'study_findings', 'study_unexpected_results',
        'act_decision', 'act_next_steps', 'act_completed_date'
    ]
    
    def test_func(self):
        """Only allow project creator or team members to edit."""
        cycle = self.get_object()
        user = self.request.user
        project = cycle.project
        return project.created_by == user or project.team_members.filter(user=user).exists()
    
    def form_valid(self, form):
        messages.success(self.request, f"Cycle #{form.instance.cycle_number} updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('quality_audits:cycle_detail', kwargs={'pk': self.object.pk})


class CycleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a PDSA cycle."""
    model = PDSACycle
    template_name = 'quality_audits/cycle_confirm_delete.html'
    
    def test_func(self):
        """Only project creator can delete cycles."""
        cycle = self.get_object()
        return cycle.project.created_by == self.request.user
    
    def get_success_url(self):
        cycle = self.get_object()
        messages.success(self.request, f"Cycle #{cycle.cycle_number} deleted successfully!")
        return reverse('quality_audits:project_detail', kwargs={'pk': cycle.project.pk})


# ============================================================================
# DATA POINT VIEWS
# ============================================================================

class DataPointCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Add a data point to a PDSA cycle."""
    model = PDSADataPoint
    template_name = 'quality_audits/datapoint_form.html'
    fields = ['measurement_date', 'measurement_value', 'notes']
    
    def dispatch(self, request, *args, **kwargs):
        """Get the cycle and ensure user has access."""
        self.cycle = get_object_or_404(PDSACycle, pk=kwargs['cycle_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def test_func(self):
        """Only allow project creator or team members to add data."""
        user = self.request.user
        project = self.cycle.project
        return project.created_by == user or project.team_members.filter(user=user).exists()
    
    def form_valid(self, form):
        form.instance.cycle = self.cycle
        form.instance.recorded_by = self.request.user
        messages.success(self.request, "Data point added successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('quality_audits:cycle_detail', kwargs={'pk': self.cycle.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cycle'] = self.cycle
        return context


class DataPointUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update a data point."""
    model = PDSADataPoint
    template_name = 'quality_audits/datapoint_form.html'
    fields = ['measurement_date', 'measurement_value', 'notes']
    
    def test_func(self):
        """Only allow data recorder or project creator to edit."""
        data_point = self.get_object()
        user = self.request.user
        return (data_point.recorded_by == user or 
                data_point.cycle.project.created_by == user)
    
    def form_valid(self, form):
        messages.success(self.request, "Data point updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('quality_audits:cycle_detail', kwargs={'pk': self.object.cycle.pk})


class DataPointDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a data point."""
    model = PDSADataPoint
    template_name = 'quality_audits/datapoint_confirm_delete.html'
    
    def test_func(self):
        """Only allow data recorder or project creator to delete."""
        data_point = self.get_object()
        user = self.request.user
        return (data_point.recorded_by == user or 
                data_point.cycle.project.created_by == user)
    
    def get_success_url(self):
        data_point = self.get_object()
        messages.success(self.request, "Data point deleted successfully!")
        return reverse('quality_audits:cycle_detail', kwargs={'pk': data_point.cycle.pk})


# ============================================================================
# ML FEATURE VIEWS
# ============================================================================

class GenerateSMARTAimView(LoginRequiredMixin, View):
    """Generate or improve a SMART aim using AI."""
    
    def post(self, request, *args, **kwargs):
        """Process AJAX request to generate SMART aim."""
        try:
            data = json.loads(request.body)
            rough_aim = data.get('aim', '')
            
            if not rough_aim:
                return JsonResponse({
                    'success': False,
                    'error': 'No aim provided'
                }, status=400)
            
            # Generate improved aim
            aim_generator = SMARTAimGenerator()
            result = aim_generator.improve_aim(rough_aim)
            
            return JsonResponse({
                'success': True,
                'improved_aim': result['improved_aim'],
                'smartness_score': result['smartness_score'],
                'suggestions': result['suggestions']
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class SuggestHypothesesView(LoginRequiredMixin, View):
    """Suggest hypotheses for a PDSA cycle using AI."""
    
    def post(self, request, *args, **kwargs):
        """Process AJAX request to suggest hypotheses."""
        try:
            data = json.loads(request.body)
            project_context = data.get('context', '')
            
            if not project_context:
                return JsonResponse({
                    'success': False,
                    'error': 'No context provided'
                }, status=400)
            
            # Generate hypotheses
            suggester = HypothesisSuggester()
            hypotheses = suggester.suggest_hypotheses(project_context, num_suggestions=5)
            
            return JsonResponse({
                'success': True,
                'hypotheses': hypotheses
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class AnalyzeCycleDataView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Analyze PDSA cycle data using statistical methods."""
    
    def test_func(self):
        """Ensure user has access to the cycle."""
        cycle = get_object_or_404(PDSACycle, pk=self.kwargs['cycle_pk'])
        user = self.request.user
        project = cycle.project
        return project.created_by == user or project.team_members.filter(user=user).exists()
    
    def get(self, request, *args, **kwargs):
        """Analyze cycle data and return results."""
        try:
            cycle = get_object_or_404(PDSACycle, pk=kwargs['cycle_pk'])
            
            # Get data points
            data_points = cycle.data_points.all().order_by('measurement_date')
            
            if data_points.count() < 3:
                return JsonResponse({
                    'success': False,
                    'error': 'Need at least 3 data points for analysis'
                }, status=400)
            
            # Perform analysis
            analyzer = PDSADataAnalyzer()
            analysis = analyzer.analyze_cycle_data(cycle.id)
            
            return JsonResponse({
                'success': True,
                'analysis': analysis
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class PredictSuccessView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Predict success probability for a PDSA project."""
    
    def test_func(self):
        """Ensure user has access to the project."""
        project = get_object_or_404(PDSAProject, pk=self.kwargs['project_pk'])
        user = self.request.user
        return project.created_by == user or project.team_members.filter(user=user).exists()
    
    def get(self, request, *args, **kwargs):
        """Predict project success."""
        try:
            project = get_object_or_404(PDSAProject, pk=kwargs['project_pk'])
            
            # Check if model is trained
            predictor = PDSASuccessPredictor()
            if not predictor.model_trained:
                return JsonResponse({
                    'success': False,
                    'error': 'Model not yet trained. Need historical data.',
                    'suggestion': 'Complete more projects to train the model'
                }, status=400)
            
            # Predict success
            prediction = predictor.predict_success(project.id)
            
            # Update project with prediction
            project.ai_success_score = prediction['success_probability'] * 100
            project.save(update_fields=['ai_success_score'])
            
            return JsonResponse({
                'success': True,
                'prediction': prediction
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class PDSAChatbotView(LoginRequiredMixin, View):
    """Interactive chatbot for PDSA guidance."""
    
    def post(self, request, *args, **kwargs):
        """Process chatbot question."""
        try:
            data = json.loads(request.body)
            question = data.get('question', '')
            project_id = data.get('project_id', None)
            
            if not question:
                return JsonResponse({
                    'success': False,
                    'error': 'No question provided'
                }, status=400)
            
            # Get response from chatbot
            chatbot = PDSAChatbot()
            response = chatbot.ask(question, project_id=project_id)
            
            # Log interaction if project_id provided
            if project_id:
                try:
                    project = PDSAProject.objects.get(pk=project_id)
                    PDSAChatbotLog.objects.create(
                        project=project,
                        user=request.user,
                        question=question,
                        answer=response['answer'],
                        confidence_score=response.get('confidence', 0)
                    )
                except PDSAProject.DoesNotExist:
                    pass
            
            return JsonResponse({
                'success': True,
                'answer': response['answer'],
                'confidence': response.get('confidence', 0),
                'sources': response.get('sources', [])
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


# ============================================================================
# TEAM MANAGEMENT VIEWS
# ============================================================================

class TeamMemberCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Add a team member to a project."""
    
    def post(self, request, *args, **kwargs):
        """Add team member."""
        try:
            project = get_object_or_404(PDSAProject, pk=kwargs['project_pk'])
            
            # Check permission
            if project.created_by != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Only project creator can add team members'
                }, status=403)
            
            data = json.loads(request.body)
            user_id = data.get('user_id')
            role = data.get('role', 'member')
            
            if not user_id:
                return JsonResponse({
                    'success': False,
                    'error': 'User ID required'
                }, status=400)
            
            # Add team member
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = get_object_or_404(User, pk=user_id)
            
            team_member, created = PDSATeamMember.objects.get_or_create(
                project=project,
                user=user,
                defaults={'role': role}
            )
            
            if not created:
                return JsonResponse({
                    'success': False,
                    'error': 'User already on team'
                }, status=400)
            
            messages.success(request, f"{user.get_full_name()} added to team!")
            
            return JsonResponse({
                'success': True,
                'member_id': team_member.id,
                'member_name': user.get_full_name(),
                'role': role
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def test_func(self):
        """Only project creator can add members."""
        project = get_object_or_404(PDSAProject, pk=self.kwargs['project_pk'])
        return project.created_by == self.request.user


class TeamMemberDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Remove a team member from a project."""
    model = PDSATeamMember
    
    def test_func(self):
        """Only project creator can remove members."""
        member = self.get_object()
        return member.project.created_by == self.request.user
    
    def delete(self, request, *args, **kwargs):
        member = self.get_object()
        project = member.project
        user_name = member.user.get_full_name()
        
        member.delete()
        
        messages.success(request, f"{user_name} removed from team!")
        
        return JsonResponse({
            'success': True,
            'message': f'{user_name} removed from team'
        })


# ============================================================================
# REPORTING & EXPORT VIEWS
# ============================================================================

class ReportsView(LoginRequiredMixin, TemplateView):
    """Reports dashboard."""
    template_name = 'quality_audits/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        projects = PDSAProject.objects.filter(
            Q(created_by=user) | Q(team_members__user=user)
        ).distinct()
        
        context['projects'] = projects
        context['total_projects'] = projects.count()
        context['completed_projects_count'] = projects.filter(status='COMPLETED').count()
        context['active_projects_count'] = projects.filter(status='ACTIVE').count()
        
        return context


class ProjectReportPDFView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Generate PDF report for a project."""
    
    def test_func(self):
        """Ensure user has access."""
        project = get_object_or_404(PDSAProject, pk=self.kwargs['project_pk'])
        user = self.request.user
        return project.created_by == user or project.team_members.filter(user=user).exists()
    
    def get(self, request, *args, **kwargs):
        """Generate and return PDF."""
        # TODO: Implement PDF generation using reportlab or weasyprint
        # For now, return a placeholder
        return HttpResponse(
            "PDF generation not yet implemented. Coming soon!",
            content_type="text/plain"
        )


class CycleReportPDFView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Generate PDF report for a cycle."""
    
    def test_func(self):
        """Ensure user has access."""
        cycle = get_object_or_404(PDSACycle, pk=self.kwargs['cycle_pk'])
        user = self.request.user
        project = cycle.project
        return project.created_by == user or project.team_members.filter(user=user).exists()
    
    def get(self, request, *args, **kwargs):
        """Generate and return PDF."""
        # TODO: Implement PDF generation
        return HttpResponse(
            "PDF generation not yet implemented. Coming soon!",
            content_type="text/plain"
        )


# ============================================================================
# API ENDPOINTS FOR CHARTS & DATA
# ============================================================================

class ProjectStatusAPIView(LoginRequiredMixin, View):
    """API endpoint for project status data (for charts)."""
    
    def get(self, request, *args, **kwargs):
        """Return project status summary as JSON."""
        try:
            project = get_object_or_404(PDSAProject, pk=kwargs['project_pk'])
            
            # Check access
            user = request.user
            if not (project.created_by == user or project.team_members.filter(user=user).exists()):
                return JsonResponse({
                    'success': False,
                    'error': 'Access denied'
                }, status=403)
            
            # Gather statistics
            cycles = project.cycles.all()
            
            data = {
                'project_name': project.project_name,
                'status': project.status,
                'total_cycles': cycles.count(),
                'completed_cycles': cycles.filter(act_completed_date__isnull=False).count(),
                'active_cycles': cycles.filter(act_completed_date__isnull=True).count(),
                'baseline_value': float(project.baseline_value) if project.baseline_value else None,
                'target_value': float(project.target_value) if project.target_value else None,
                'measurement_unit': project.measurement_unit,
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'ai_success_score': float(project.ai_success_score) if project.ai_success_score else None,
            }
            
            return JsonResponse({'success': True, 'data': data})
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class CycleChartDataAPIView(LoginRequiredMixin, View):
    """API endpoint for cycle chart data (run charts, control charts)."""
    
    def get(self, request, *args, **kwargs):
        """Return cycle data points for charting."""
        try:
            cycle = get_object_or_404(PDSACycle, pk=kwargs['cycle_pk'])
            
            # Check access
            user = request.user
            project = cycle.project
            if not (project.created_by == user or project.team_members.filter(user=user).exists()):
                return JsonResponse({
                    'success': False,
                    'error': 'Access denied'
                }, status=403)
            
            # Get data points
            data_points = cycle.data_points.all().order_by('measurement_date')
            
            chart_data = {
                'labels': [dp.measurement_date.isoformat() for dp in data_points],
                'values': [float(dp.measurement_value) for dp in data_points],
                'baseline': float(project.baseline_value) if project.baseline_value else None,
                'target': float(project.target_value) if project.target_value else None,
                'measurement_unit': project.measurement_unit,
            }
            
            return JsonResponse({'success': True, 'data': chart_data})
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


# ============================================================================
# QIA (QUALITY IMPROVEMENT ACTIONS) VIEWS
# ============================================================================


class QIADashboardView(LoginRequiredMixin, TemplateView):
    """
    QIA Dashboard - Overview of all Quality Improvement Actions
    """
    template_name = 'quality_audits/qia_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Filter QIAs based on user's care home access
        if user.is_superuser or user.role in ['DIRECTOR', 'HEAD_OF_SERVICE']:
            qias = QualityImprovementAction.objects.all()
        else:
            # Staff can see QIAs from their care homes
            user_homes = user.care_homes.all() if hasattr(user, 'care_homes') else []
            qias = QualityImprovementAction.objects.filter(care_home__in=user_homes)
        
        # Status summary
        context['total_qias'] = qias.count()
        context['identified'] = qias.filter(status='IDENTIFIED').count()
        context['in_progress'] = qias.filter(
            status__in=['PLANNED', 'APPROVED', 'IMPLEMENTING', 'IMPLEMENTED']
        ).count()
        context['verified'] = qias.filter(status='VERIFIED').count()
        context['closed'] = qias.filter(status='CLOSED').count()
        
        # Priority breakdown
        context['critical'] = qias.filter(priority='CRITICAL').count()
        context['high'] = qias.filter(priority='HIGH').count()
        context['medium'] = qias.filter(priority='MEDIUM').count()
        context['low'] = qias.filter(priority='LOW').count()
        
        # Overdue QIAs
        today = timezone.now().date()
        context['overdue_qias'] = qias.filter(
            target_completion_date__lt=today
        ).exclude(status__in=['CLOSED', 'REJECTED']).order_by('target_completion_date')[:10]
        
        # Recent QIAs
        context['recent_qias'] = qias.order_by('-created_at')[:10]
        
        # Source type breakdown
        context['source_breakdown'] = qias.values('source_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Action type breakdown
        context['corrective_count'] = qias.filter(action_type='CORRECTIVE').count()
        context['preventive_count'] = qias.filter(action_type='PREVENTIVE').count()
        
        # My QIAs (where user is responsible)
        context['my_qias'] = qias.filter(responsible_person=user).exclude(
            status__in=['CLOSED', 'REJECTED']
        ).order_by('target_completion_date')[:5]
        
        return context


class QIAListView(LoginRequiredMixin, ListView):
    """List all QIAs with filtering and search"""
    model = QualityImprovementAction
    template_name = 'quality_audits/qia_list.html'
    context_object_name = 'qias'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter by user's access
        if not (user.is_superuser or user.role in ['DIRECTOR', 'HEAD_OF_SERVICE']):
            user_homes = user.care_homes.all() if hasattr(user, 'care_homes') else []
            queryset = queryset.filter(care_home__in=user_homes)
        
        # Apply filters from GET parameters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        source_type = self.request.GET.get('source_type')
        if source_type:
            queryset = queryset.filter(source_type=source_type)
        
        action_type = self.request.GET.get('action_type')
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(qia_reference__icontains=search) |
                Q(title__icontains=search) |
                Q(problem_description__icontains=search)
            )
        
        return queryset.select_related('care_home', 'responsible_person').order_by('-created_at')


class QIADetailView(LoginRequiredMixin, DetailView):
    """QIA detail view with full information and timeline"""
    model = QualityImprovementAction
    template_name = 'quality_audits/qia_detail.html'
    context_object_name = 'qia'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qia = self.object
        
        # Get updates and reviews
        context['updates'] = qia.updates.all().order_by('-update_date')
        context['reviews'] = qia.reviews.all().order_by('-review_date')
        
        # Calculate progress
        context['days_remaining'] = qia.days_until_due
        context['is_overdue'] = qia.is_overdue
        
        # Status history from updates
        context['status_history'] = qia.updates.exclude(
            status_change=''
        ).order_by('-update_date')[:5]
        
        return context


class QIACreateView(LoginRequiredMixin, CreateView):
    """Create new QIA"""
    model = QualityImprovementAction
    template_name = 'quality_audits/qia_form.html'
    fields = [
        'title', 'action_type', 'source_type', 'source_reference',
        'problem_description', 'root_cause', 'impact_analysis',
        'action_plan', 'success_criteria', 'resources_needed',
        'care_home', 'responsible_person', 'team_members',
        'planned_start_date', 'target_completion_date',
        'priority', 'verification_method', 'regulatory_requirement',
        'requires_ci_notification'
    ]
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = 'IDENTIFIED'
        messages.success(self.request, f'QIA {form.instance.qia_reference} created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('quality_audits:qia_detail', kwargs={'pk': self.object.pk})


class QIAUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing QIA"""
    model = QualityImprovementAction
    template_name = 'quality_audits/qia_form.html'
    fields = [
        'title', 'problem_description', 'root_cause', 'impact_analysis',
        'action_plan', 'success_criteria', 'resources_needed',
        'responsible_person', 'team_members',
        'planned_start_date', 'target_completion_date',
        'priority', 'status', 'percent_complete', 'progress_notes',
        'verification_method', 'regulatory_requirement',
        'requires_ci_notification', 'ci_notification_date'
    ]
    
    def form_valid(self, form):
        messages.success(self.request, f'QIA {self.object.qia_reference} updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('quality_audits:qia_detail', kwargs={'pk': self.object.pk})


class QIAProgressUpdateView(LoginRequiredMixin, CreateView):
    """Add progress update to QIA"""
    model = QIAUpdate
    template_name = 'quality_audits/qia_update_form.html'
    fields = ['status_change', 'percent_complete', 'update_notes', 'evidence_description']
    
    def dispatch(self, request, *args, **kwargs):
        self.qia = get_object_or_404(QualityImprovementAction, pk=kwargs['qia_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['qia'] = self.qia
        return context
    
    def form_valid(self, form):
        form.instance.qia = self.qia
        form.instance.updated_by = self.request.user
        
        # Update QIA's percent_complete
        self.qia.percent_complete = form.instance.percent_complete
        self.qia.save()
        
        messages.success(self.request, 'Progress update added successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('quality_audits:qia_detail', kwargs={'pk': self.qia.pk})


class QIAVerifyView(LoginRequiredMixin, CreateView):
    """Create effectiveness review for QIA"""
    model = QIAReview
    template_name = 'quality_audits/qia_review_form.html'
    fields = [
        'is_effective', 'effectiveness_rating', 'effectiveness_evidence',
        'is_sustainable', 'sustainability_plan',
        'follow_up_required', 'follow_up_actions',
        'lessons_learned', 'recommend_spread', 'spread_notes',
        'approved_for_closure', 'closure_notes'
    ]
    
    def dispatch(self, request, *args, **kwargs):
        self.qia = get_object_or_404(QualityImprovementAction, pk=kwargs['qia_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['qia'] = self.qia
        return context
    
    def form_valid(self, form):
        form.instance.qia = self.qia
        form.instance.reviewer = self.request.user
        
        # Update QIA status based on review
        if form.instance.approved_for_closure:
            self.qia.status = 'CLOSED'
            self.qia.actual_completion_date = timezone.now().date()
        else:
            self.qia.status = 'VERIFIED'
        
        self.qia.effectiveness_rating = form.instance.effectiveness_rating
        self.qia.effectiveness_notes = form.instance.effectiveness_evidence
        self.qia.verification_date = timezone.now().date()
        self.qia.verified_by = self.request.user
        self.qia.save()
        
        messages.success(self.request, 'QIA review completed successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('quality_audits:qia_detail', kwargs={'pk': self.qia.pk})


class QIADeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete QIA (only for superusers/directors)"""
    model = QualityImprovementAction
    template_name = 'quality_audits/qia_confirm_delete.html'
    success_url = reverse_lazy('quality_audits:qia_list')
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role in ['DIRECTOR', 'HEAD_OF_SERVICE']
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, f'QIA {self.get_object().qia_reference} deleted successfully!')
        return super().delete(request, *args, **kwargs)


@login_required
def generate_qia_evidence_pack(request):
    """Generate and download QIA evidence pack PDF"""
    from datetime import datetime
    from django.http import FileResponse
    from .evidence_pack_generator import QIAEvidencePackGenerator
    import os
    
    # Get filter parameters from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    qi_filter = request.GET.get('qi')
    source_filter = request.GET.get('source')
    priority_filter = request.GET.get('priority')
    
    # Parse dates
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            messages.error(request, 'Invalid start date format')
            return redirect('quality_audits:qia_dashboard')
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            messages.error(request, 'Invalid end date format')
            return redirect('quality_audits:qia_dashboard')
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'QIA_Evidence_Pack_{timestamp}.pdf'
    
    try:
        # Generate the evidence pack
        generator = QIAEvidencePackGenerator(filename=filename)
        pdf_path = generator.generate(
            start_date=start_date_obj,
            end_date=end_date_obj,
            qi_filter=qi_filter,
            source_filter=source_filter,
            priority_filter=priority_filter
        )
        
        # Return PDF as download
        response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Clean up the file after sending
        # Note: In production, consider using celery task to clean up later
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error generating evidence pack: {str(e)}')
        return redirect('quality_audits:qia_dashboard')
