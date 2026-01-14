"""
TQM Module 4: Training & Competency Views

Provides views for:
- Competency framework management
- Staff competency assessments
- Learning pathway enrollment and tracking
- Skills matrix visualization
- Training requirement management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg, F
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from .models import (
    CompetencyFramework,
    RoleCompetencyRequirement,
    CompetencyAssessment,
    TrainingMatrix,
    LearningPathway,
    PathwayCompetency,
    PathwayTraining,
    StaffLearningPlan
)
from scheduling.models import User, Role, TrainingCourse


@login_required
def dashboard(request):
    """
    Main dashboard showing competency overview and staff development status
    """
    user = request.user
    
    # Get user's role competencies
    if user.role:
        required_competencies = RoleCompetencyRequirement.objects.filter(
            role=user.role
        ).select_related('competency')
        total_required = required_competencies.count()
    else:
        required_competencies = RoleCompetencyRequirement.objects.none()
        total_required = 0
    
    # Get user's assessments
    assessments = CompetencyAssessment.objects.filter(
        staff_member=user
    ).select_related('competency', 'assessor').order_by('-assessment_date')[:5]
    
    # Get user's learning plans
    learning_plans = StaffLearningPlan.objects.filter(
        staff_member=user
    ).select_related('pathway', 'mentor').order_by('-enrollment_date')
    
    # Get available pathways for user's role
    if user.role:
        available_pathways = LearningPathway.objects.filter(
            from_role=user.role,
            status='ACTIVE',
            is_active=True
        )
    else:
        available_pathways = LearningPathway.objects.none()
    
    # Calculate competency completion stats
    completed_competencies = CompetencyAssessment.objects.filter(
        staff_member=user,
        outcome__in=['COMPETENT', 'HIGHLY_COMPETENT']
    ).values('competency').distinct().count()
    
    completion_percentage = round((completed_competencies / total_required * 100) if total_required > 0 else 0)
    
    context = {
        'required_competencies': required_competencies,
        'recent_assessments': assessments,
        'learning_plans': learning_plans,
        'available_pathways': available_pathways,
        'total_required': total_required,
        'completed_competencies': completed_competencies,
        'completion_percentage': completion_percentage,
    }
    
    return render(request, 'training_competency/dashboard.html', context)


@login_required
def competency_list(request):
    """
    List all competency frameworks with filtering
    """
    competencies = CompetencyFramework.objects.filter(is_active=True)
    
    # Filter by type
    comp_type = request.GET.get('type')
    if comp_type:
        competencies = competencies.filter(competency_type=comp_type)
    
    # Filter by role
    role_id = request.GET.get('role')
    if role_id:
        competencies = competencies.filter(required_for_roles__id=role_id)
    
    # Search
    search = request.GET.get('search')
    if search:
        competencies = competencies.filter(
            Q(title__icontains=search) |
            Q(code__icontains=search) |
            Q(description__icontains=search)
        )
    
    competencies = competencies.distinct().order_by('competency_type', 'code')
    
    context = {
        'competencies': competencies,
        'competency_types': CompetencyFramework.COMPETENCY_TYPE_CHOICES,
        'roles': Role.objects.all(),
    }
    
    return render(request, 'training_competency/competency_list.html', context)


@login_required
def competency_detail(request, pk):
    """
    Detailed view of a competency framework
    """
    competency = get_object_or_404(CompetencyFramework, pk=pk)
    
    # Get user's assessment for this competency
    user_assessment = CompetencyAssessment.objects.filter(
        staff_member=request.user,
        competency=competency
    ).order_by('-assessment_date').first()
    
    # Get related roles
    role_requirements = RoleCompetencyRequirement.objects.filter(
        competency=competency
    ).select_related('role')
    
    # Get linked training courses
    training_courses = competency.linked_training_courses.all()
    
    context = {
        'competency': competency,
        'user_assessment': user_assessment,
        'role_requirements': role_requirements,
        'training_courses': training_courses,
        'competency_levels': CompetencyFramework.COMPETENCY_LEVEL_CHOICES,
    }
    
    return render(request, 'training_competency/competency_detail.html', context)


@login_required
def my_assessments(request):
    """
    View all assessments for the current user
    """
    assessments = CompetencyAssessment.objects.filter(
        staff_member=request.user
    ).select_related('competency', 'assessor').order_by('-assessment_date')
    
    # Group by outcome
    stats = {
        'total': assessments.count(),
        'competent': assessments.filter(outcome__in=['COMPETENT', 'HIGHLY_COMPETENT']).count(),
        'in_progress': assessments.filter(outcome='IN_PROGRESS').count(),
        'not_yet_competent': assessments.filter(outcome='NOT_YET_COMPETENT').count(),
    }
    
    context = {
        'assessments': assessments,
        'stats': stats,
    }
    
    return render(request, 'training_competency/my_assessments.html', context)


@login_required
def learning_pathways(request):
    """
    Browse available learning pathways
    """
    pathways = LearningPathway.objects.filter(
        status='ACTIVE',
        is_active=True
    )
    
    # Filter by from_role (starting role)
    from_role_id = request.GET.get('from_role')
    if from_role_id:
        pathways = pathways.filter(from_role_id=from_role_id)
    
    # Filter by to_role (target role)
    to_role_id = request.GET.get('to_role')
    if to_role_id:
        pathways = pathways.filter(to_role_id=to_role_id)
    
    pathways = pathways.select_related('from_role', 'to_role', 'owner').order_by('from_role', 'to_role')
    
    context = {
        'pathways': pathways,
        'roles': Role.objects.all(),
    }
    
    return render(request, 'training_competency/learning_pathways.html', context)


@login_required
def pathway_detail(request, pk):
    """
    Detailed view of a learning pathway
    """
    pathway = get_object_or_404(LearningPathway, pk=pk)
    
    # Get required competencies with sequence
    pathway_competencies = PathwayCompetency.objects.filter(
        pathway=pathway
    ).select_related('competency').order_by('sequence_order')
    
    # Get required training with sequence
    pathway_training = PathwayTraining.objects.filter(
        pathway=pathway
    ).select_related('training_course').order_by('sequence_order')
    
    # Check if user is enrolled
    user_plan = StaffLearningPlan.objects.filter(
        staff_member=request.user,
        pathway=pathway
    ).first()
    
    # Check user's progress on competencies
    if user_plan:
        user_assessments = CompetencyAssessment.objects.filter(
            staff_member=request.user,
            competency__in=[pc.competency for pc in pathway_competencies],
            outcome__in=['COMPETENT', 'HIGHLY_COMPETENT']
        ).values_list('competency_id', flat=True)
        
        for pc in pathway_competencies:
            pc.user_completed = pc.competency.id in user_assessments
    
    context = {
        'pathway': pathway,
        'pathway_competencies': pathway_competencies,
        'pathway_training': pathway_training,
        'user_plan': user_plan,
    }
    
    return render(request, 'training_competency/pathway_detail.html', context)


@login_required
def enroll_pathway(request, pk):
    """
    Enroll in a learning pathway
    """
    pathway = get_object_or_404(LearningPathway, pk=pk)
    
    # Check if already enrolled
    existing_plan = StaffLearningPlan.objects.filter(
        staff_member=request.user,
        pathway=pathway
    ).first()
    
    if existing_plan:
        messages.warning(request, f'You are already enrolled in "{pathway.title}"')
    else:
        # Create new learning plan
        plan = StaffLearningPlan.objects.create(
            staff_member=request.user,
            pathway=pathway,
            enrollment_date=timezone.now().date(),
            status='PLANNED',
            line_manager=request.user.role.reports_to if request.user.role and hasattr(request.user.role, 'reports_to') else None,
            target_completion_date=timezone.now().date() + timedelta(days=pathway.estimated_duration_months * 30)
        )
        messages.success(request, f'Successfully enrolled in "{pathway.title}"')
        return redirect('training_competency:my_learning_plans')
    
    return redirect('training_competency:pathway_detail', pk=pk)


@login_required
def my_learning_plans(request):
    """
    View all learning plans for the current user
    """
    plans = StaffLearningPlan.objects.filter(
        staff_member=request.user
    ).select_related('pathway', 'mentor', 'line_manager').order_by('-enrollment_date')
    
    context = {
        'plans': plans,
    }
    
    return render(request, 'training_competency/my_learning_plans.html', context)


@login_required
def skills_matrix(request):
    """
    Skills matrix view showing staff competency levels across different areas
    """
    # Get all staff
    staff = User.objects.filter(
        is_active=True,
        role__isnull=False
    ).select_related('role')
    
    # Filter by role if specified
    role_id = request.GET.get('role')
    if role_id:
        staff = staff.filter(role_id=role_id)
    
    # Get all active competencies
    competencies = CompetencyFramework.objects.filter(is_active=True).order_by('competency_type', 'code')
    
    # Filter by competency type
    comp_type = request.GET.get('type')
    if comp_type:
        competencies = competencies.filter(competency_type=comp_type)
    
    # Build matrix data
    matrix_data = []
    for staff_member in staff:
        row = {
            'staff': staff_member,
            'competencies': []
        }
        
        for competency in competencies:
            # Get latest assessment
            assessment = CompetencyAssessment.objects.filter(
                staff_member=staff_member,
                competency=competency
            ).order_by('-assessment_date').first()
            
            row['competencies'].append({
                'competency': competency,
                'assessment': assessment,
                'level': assessment.achieved_level if assessment else None,
                'outcome': assessment.outcome if assessment else None,
            })
        
        matrix_data.append(row)
    
    context = {
        'matrix_data': matrix_data,
        'competencies': competencies,
        'roles': Role.objects.all(),
        'competency_types': CompetencyFramework.COMPETENCY_TYPE_CHOICES,
    }
    
    return render(request, 'training_competency/skills_matrix.html', context)


@login_required
def training_requirements(request):
    """
    View training requirements by role
    """
    # Get all roles with training requirements
    roles = Role.objects.all().order_by('name')
    
    selected_role_id = request.GET.get('role')
    selected_role = None
    requirements = []
    
    if selected_role_id:
        selected_role = get_object_or_404(Role, pk=selected_role_id)
        requirements = TrainingMatrix.objects.filter(
            role=selected_role
        ).select_related('training_course', 'care_home').order_by('priority_order', 'requirement_type')
    
    context = {
        'roles': roles,
        'selected_role': selected_role,
        'requirements': requirements,
    }
    
    return render(request, 'training_competency/training_requirements.html', context)
