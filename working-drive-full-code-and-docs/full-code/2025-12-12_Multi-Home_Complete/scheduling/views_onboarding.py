"""
Onboarding Views
Interactive onboarding wizard and tours for new users
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.urls import reverse
from django.db import models
from .decorators_api import api_login_required

from .models_onboarding import OnboardingProgress, OnboardingTourStep, UserTip


@login_required
def onboarding_check(request):
    """
    Check if user needs onboarding and redirect accordingly
    Called after login
    """
    progress, created = OnboardingProgress.objects.get_or_create(user=request.user)
    
    # If user has skipped or completed onboarding, continue to dashboard
    if progress.skip_onboarding or progress.completed:
        if request.user.role and request.user.role.is_management:
            return redirect('manager_dashboard')
        return redirect('staff_dashboard')
    
    # Start onboarding
    return redirect('onboarding_welcome')


@login_required
def onboarding_welcome(request):
    """
    Welcome screen - introduces the system and user's role
    """
    progress, created = OnboardingProgress.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'start':
            progress.mark_step_complete('welcome')
            return redirect('onboarding_dashboard_tour')
        
        elif action == 'skip':
            progress.skip_onboarding = True
            progress.save()
            messages.info(request, "You can restart the tour anytime from your settings.")
            
            if request.user.role and request.user.role.is_management:
                return redirect('manager_dashboard')
            return redirect('staff_dashboard')
    
    # Determine user role for personalized welcome
    is_management = request.user.role and request.user.role.is_management
    is_senior = request.user.role and request.user.role.name in ['Service Manager', 'OM']
    
    context = {
        'progress': progress,
        'is_management': is_management,
        'is_senior': is_senior,
        'user': request.user,
    }
    
    return render(request, 'scheduling/onboarding/welcome.html', context)


@login_required
def onboarding_dashboard_tour(request):
    """
    Interactive tour of the dashboard
    """
    progress = get_object_or_404(OnboardingProgress, user=request.user)
    
    # Get tour steps
    tour_steps = OnboardingTourStep.objects.filter(
        tour_name='dashboard',
        is_active=True
    )
    
    is_management = request.user.role and request.user.role.is_management
    
    context = {
        'progress': progress,
        'tour_steps': tour_steps,
        'is_management': is_management,
        'next_url': reverse('onboarding_rota_tour'),
    }
    
    return render(request, 'scheduling/onboarding/dashboard_tour.html', context)


@login_required
def onboarding_rota_tour(request):
    """
    Interactive tour of the rota view
    """
    progress = get_object_or_404(OnboardingProgress, user=request.user)
    
    tour_steps = OnboardingTourStep.objects.filter(
        tour_name='rota',
        is_active=True
    )
    
    is_management = request.user.role and request.user.role.is_management
    
    context = {
        'progress': progress,
        'tour_steps': tour_steps,
        'is_management': is_management,
        'next_url': reverse('onboarding_staff_tour') if is_management else reverse('onboarding_ai_intro'),
    }
    
    return render(request, 'scheduling/onboarding/rota_tour.html', context)


@login_required
def onboarding_staff_tour(request):
    """
    Interactive tour of staff management (managers only)
    """
    progress = get_object_or_404(OnboardingProgress, user=request.user)
    
    # Only for management users
    if not (request.user.role and request.user.role.is_management):
        return redirect('onboarding_ai_intro')
    
    tour_steps = OnboardingTourStep.objects.filter(
        tour_name='staff',
        is_active=True
    )
    
    context = {
        'progress': progress,
        'tour_steps': tour_steps,
        'next_url': reverse('onboarding_ai_intro'),
    }
    
    return render(request, 'scheduling/onboarding/staff_tour.html', context)


@login_required
def onboarding_ai_intro(request):
    """
    Introduction to AI Assistant features
    """
    progress = get_object_or_404(OnboardingProgress, user=request.user)
    
    tour_steps = OnboardingTourStep.objects.filter(
        tour_name='ai',
        is_active=True
    )
    
    is_management = request.user.role and request.user.role.is_management
    
    # Example AI commands based on role
    if is_management:
        example_commands = [
            "Show me unfilled shifts this week",
            "Who's off sick today?",
            "Generate next week's rota",
            "Show compliance status for all homes",
        ]
    else:
        example_commands = [
            "Show my upcoming shifts",
            "Request leave for next Friday",
            "Swap my shift on Monday",
            "Show my leave balance",
        ]
    
    context = {
        'progress': progress,
        'tour_steps': tour_steps,
        'is_management': is_management,
        'example_commands': example_commands,
        'next_url': reverse('onboarding_mobile_tips'),
    }
    
    return render(request, 'scheduling/onboarding/ai_intro.html', context)


@login_required
def onboarding_mobile_tips(request):
    """
    Mobile app features and tips
    """
    progress = get_object_or_404(OnboardingProgress, user=request.user)
    
    context = {
        'progress': progress,
        'next_url': reverse('onboarding_complete'),
    }
    
    return render(request, 'scheduling/onboarding/mobile_tips.html', context)


@login_required
def onboarding_complete(request):
    """
    Onboarding completion screen
    """
    progress = get_object_or_404(OnboardingProgress, user=request.user)
    
    # Mark all steps as complete
    progress.welcome_completed = True
    progress.dashboard_tour_completed = True
    progress.rota_tour_completed = True
    progress.staff_tour_completed = True
    progress.ai_intro_completed = True
    progress.mobile_tips_completed = True
    progress.check_full_completion()
    progress.save()
    
    is_management = request.user.role and request.user.role.is_management
    
    if request.method == 'POST':
        if is_management:
            return redirect('manager_dashboard')
        return redirect('staff_dashboard')
    
    context = {
        'progress': progress,
        'is_management': is_management,
    }
    
    return render(request, 'scheduling/onboarding/complete.html', context)


@login_required
@require_http_methods(["POST"])
def onboarding_mark_step_complete(request):
    """
    API endpoint to mark individual steps as complete
    """
    progress = get_object_or_404(OnboardingProgress, user=request.user)
    step_name = request.POST.get('step')
    
    if step_name:
        progress.mark_step_complete(step_name)
        return JsonResponse({
            'success': True,
            'completion_percentage': progress.completion_percentage
        })
    
    return JsonResponse({'success': False, 'error': 'No step specified'}, status=400)


@login_required
@require_http_methods(["POST"])
def onboarding_skip(request):
    """
    Skip onboarding entirely
    """
    progress = get_object_or_404(OnboardingProgress, user=request.user)
    progress.skip_onboarding = True
    progress.save()
    
    is_management = request.user.role and request.user.role.is_management
    redirect_url = 'manager_dashboard' if is_management else 'staff_dashboard'
    
    return JsonResponse({
        'success': True,
        'redirect_url': reverse(redirect_url)
    })


@login_required
@require_http_methods(["POST"])
def onboarding_reset(request):
    """
    Reset onboarding progress (for re-running the tour)
    """
    progress = get_object_or_404(OnboardingProgress, user=request.user)
    progress.reset_onboarding()
    
    messages.success(request, "Onboarding tour has been reset. Welcome back!")
    return redirect('onboarding_welcome')


@login_required
def get_contextual_tips(request):
    """
    API endpoint to get contextual tips for current page
    """
    current_path = request.GET.get('path', '')
    user = request.user
    
    # Determine user role
    if user.role and user.role.is_management:
        if user.role.name in ['Service Manager', 'OM']:
            role_filter = ['all', 'management', 'senior']
        else:
            role_filter = ['all', 'management']
    else:
        role_filter = ['all', 'staff']
    
    # Get tips for this role and page
    tips = UserTip.objects.filter(
        is_active=True,
        target_role__in=role_filter
    )
    
    # Filter by page if specified
    if current_path:
        tips = tips.filter(
            models.Q(target_page='') | models.Q(target_page__icontains=current_path)
        )
    
    tips_data = [{
        'title': tip.title,
        'content': tip.content,
        'type': tip.tip_type,
        'icon': tip.icon,
    } for tip in tips[:3]]  # Limit to 3 tips
    
    return JsonResponse({'tips': tips_data})


# API endpoints for onboarding wizard
@api_login_required
@require_http_methods(["POST"])
def update_onboarding_progress(request):
    """
    API endpoint to update onboarding progress
    """
    import json
    progress = get_object_or_404(OnboardingProgress, user=request.user)
    data = json.loads(request.body)
    
    step_name = data.get('step')
    if step_name:
        progress.mark_step_complete(step_name)
        return JsonResponse({
            'success': True,
            'completion_percentage': progress.completion_percentage
        })
    
    return JsonResponse({'success': False, 'error': 'No step specified'}, status=400)


@api_login_required
@require_http_methods(["GET"])
def get_onboarding_progress(request):
    """
    API endpoint to get user's onboarding progress
    """
    progress, created = OnboardingProgress.objects.get_or_create(user=request.user)
    
    return JsonResponse({
        'success': True,
        'progress': {
            'welcome_completed': progress.welcome_completed,
            'dashboard_tour_completed': progress.dashboard_tour_completed,
            'rota_tour_completed': progress.rota_tour_completed,
            'staff_tour_completed': progress.staff_tour_completed,
            'ai_intro_completed': progress.ai_intro_completed,
            'mobile_tips_completed': progress.mobile_tips_completed,
            'completed': progress.completed,
            'skip_onboarding': progress.skip_onboarding,
            'completion_percentage': progress.completion_percentage,
        }
    })


@api_login_required
@require_http_methods(["POST"])
def mark_onboarding_step_complete(request):
    """
    API endpoint to mark individual onboarding step as complete
    """
    import json
    progress = get_object_or_404(OnboardingProgress, user=request.user)
    data = json.loads(request.body)
    
    step_name = data.get('step')
    if step_name:
        progress.mark_step_complete(step_name)
        return JsonResponse({
            'success': True,
            'completion_percentage': progress.completion_percentage
        })
    
    return JsonResponse({'success': False, 'error': 'No step specified'}, status=400)


@api_login_required
@require_http_methods(["GET"])
def get_user_tips(request):
    """
    API endpoint to get contextual tips for current page
    """
    current_path = request.GET.get('path', '')
    user = request.user
    
    # Determine user role
    if user.role and user.role.is_management:
        if user.role.name in ['Service Manager', 'OM']:
            role_filter = ['all', 'management', 'senior']
        else:
            role_filter = ['all', 'management']
    else:
        role_filter = ['all', 'staff']
    
    # Get tips for this role and page
    tips = UserTip.objects.filter(
        is_active=True,
        target_role__in=role_filter
    )
    
    # Filter by page if specified
    if current_path:
        tips = tips.filter(
            models.Q(target_page='') | models.Q(target_page__icontains=current_path)
        )
    
    tips_data = [{
        'title': tip.title,
        'content': tip.content,
        'type': tip.tip_type,
        'icon': tip.icon,
    } for tip in tips[:3]]  # Limit to 3 tips
    
    return JsonResponse({'success': True, 'tips': tips_data})


def onboarding_resume(request):
    """
    Resume onboarding from last completed step
    """
    progress = get_object_or_404(OnboardingProgress, user=request.user)
    
    # Find the first incomplete step and redirect there
    if not progress.welcome_completed:
        return redirect('onboarding_welcome')
    elif not progress.dashboard_tour_completed:
        return redirect('onboarding_dashboard_tour')
    elif progress.completed:
        # Already complete, go to dashboard
        if request.user.role and request.user.role.is_management:
            return redirect('manager_dashboard')
        return redirect('staff_dashboard')
    else:
        return redirect('onboarding_welcome')

