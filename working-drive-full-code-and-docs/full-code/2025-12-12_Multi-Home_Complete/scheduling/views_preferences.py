"""
Task 50: User Preferences Views
Settings page with live preview and save functionality
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import pytz

from .models_preferences import UserPreferences


@login_required
def user_settings(request):
    """
    User settings page with tabbed interface
    Tabs: Appearance, Notifications, Regional, Privacy, Accessibility
    """
    preferences = UserPreferences.get_or_create_for_user(request.user)
    
    if request.method == 'POST':
        # Update preferences from form
        tab = request.POST.get('active_tab', 'appearance')
        
        # Appearance settings
        if 'theme' in request.POST:
            preferences.theme = request.POST.get('theme', 'light')
            preferences.compact_mode = request.POST.get('compact_mode') == 'on'
            preferences.sidebar_collapsed = request.POST.get('sidebar_collapsed') == 'on'
            preferences.dashboard_layout = request.POST.get('dashboard_layout', 'default')
            preferences.default_calendar_view = request.POST.get('default_calendar_view', 'month')
            preferences.show_calendar_week_numbers = request.POST.get('show_calendar_week_numbers') == 'on'
        
        # Notification settings
        if 'email_notifications' in request.POST or request.POST.get('save_notifications'):
            preferences.email_notifications = request.POST.get('email_notifications') == 'on'
            preferences.notify_shift_assigned = request.POST.get('notify_shift_assigned') == 'on'
            preferences.notify_shift_changed = request.POST.get('notify_shift_changed') == 'on'
            preferences.notify_leave_approved = request.POST.get('notify_leave_approved') == 'on'
            preferences.notify_shift_reminder = request.POST.get('notify_shift_reminder') == 'on'
            preferences.notify_training_due = request.POST.get('notify_training_due') == 'on'
            preferences.notify_new_message = request.POST.get('notify_new_message') == 'on'
            preferences.notify_compliance_alert = request.POST.get('notify_compliance_alert') == 'on'
            preferences.browser_notifications = request.POST.get('browser_notifications') == 'on'
            preferences.sms_notifications = request.POST.get('sms_notifications') == 'on'
        
        # Regional settings
        if 'language' in request.POST:
            preferences.language = request.POST.get('language', 'en')
            preferences.timezone = request.POST.get('timezone', 'Europe/London')
            preferences.date_format = request.POST.get('date_format', 'DD/MM/YYYY')
            preferences.time_format = request.POST.get('time_format', '24')
        
        # Privacy settings
        if 'show_profile_to_others' in request.POST or request.POST.get('save_privacy'):
            preferences.show_profile_to_others = request.POST.get('show_profile_to_others') == 'on'
            preferences.show_phone_to_others = request.POST.get('show_phone_to_others') == 'on'
        
        # Accessibility settings
        if 'high_contrast' in request.POST or request.POST.get('save_accessibility'):
            preferences.high_contrast = request.POST.get('high_contrast') == 'on'
            preferences.font_size = request.POST.get('font_size', 'medium')
            preferences.reduce_animations = request.POST.get('reduce_animations') == 'on'
        
        preferences.save()
        messages.success(request, 'Settings saved successfully!')
        
        # Return to same tab
        return redirect(f'/settings/?tab={tab}')
    
    # Get active tab from query params
    active_tab = request.GET.get('tab', 'appearance')
    
    # Get list of timezones for dropdown
    timezones = pytz.common_timezones
    
    context = {
        'preferences': preferences,
        'active_tab': active_tab,
        'timezones': timezones,
    }
    
    return render(request, 'scheduling/user_settings.html', context)


@login_required
@require_http_methods(["POST"])
def update_theme(request):
    """
    AJAX endpoint to update theme in real-time
    Returns JSON response for live preview
    """
    theme = request.POST.get('theme', 'light')
    
    if theme not in ['light', 'dark', 'auto']:
        return JsonResponse({'success': False, 'error': 'Invalid theme'}, status=400)
    
    preferences = UserPreferences.get_or_create_for_user(request.user)
    preferences.theme = theme
    preferences.save()
    
    return JsonResponse({
        'success': True,
        'theme': theme,
        'message': f'Theme changed to {theme} mode'
    })


@login_required
@require_http_methods(["POST"])
def reset_preferences(request):
    """
    Reset all preferences to defaults
    """
    preferences = UserPreferences.get_or_create_for_user(request.user)
    
    # Reset to defaults
    preferences.theme = 'light'
    preferences.compact_mode = False
    preferences.sidebar_collapsed = False
    preferences.language = 'en'
    preferences.timezone = 'Europe/London'
    preferences.date_format = 'DD/MM/YYYY'
    preferences.time_format = '24'
    preferences.email_notifications = True
    preferences.notify_shift_assigned = True
    preferences.notify_shift_changed = True
    preferences.notify_leave_approved = True
    preferences.notify_shift_reminder = True
    preferences.notify_training_due = True
    preferences.notify_new_message = True
    preferences.notify_compliance_alert = True
    preferences.browser_notifications = False
    preferences.sms_notifications = False
    preferences.dashboard_layout = 'default'
    preferences.show_calendar_week_numbers = False
    preferences.default_calendar_view = 'month'
    preferences.show_profile_to_others = True
    preferences.show_phone_to_others = True
    preferences.high_contrast = False
    preferences.font_size = 'medium'
    preferences.reduce_animations = False
    
    preferences.save()
    
    messages.success(request, 'All settings reset to defaults!')
    return redirect('/settings/')


@login_required
def export_preferences(request):
    """
    Export user preferences as JSON for backup
    """
    preferences = UserPreferences.get_or_create_for_user(request.user)
    
    data = {
        'theme': preferences.theme,
        'compact_mode': preferences.compact_mode,
        'sidebar_collapsed': preferences.sidebar_collapsed,
        'language': preferences.language,
        'timezone': preferences.timezone,
        'date_format': preferences.date_format,
        'time_format': preferences.time_format,
        'email_notifications': preferences.email_notifications,
        'notify_shift_assigned': preferences.notify_shift_assigned,
        'notify_shift_changed': preferences.notify_shift_changed,
        'notify_leave_approved': preferences.notify_leave_approved,
        'notify_shift_reminder': preferences.notify_shift_reminder,
        'notify_training_due': preferences.notify_training_due,
        'notify_new_message': preferences.notify_new_message,
        'notify_compliance_alert': preferences.notify_compliance_alert,
        'browser_notifications': preferences.browser_notifications,
        'sms_notifications': preferences.sms_notifications,
        'dashboard_layout': preferences.dashboard_layout,
        'show_calendar_week_numbers': preferences.show_calendar_week_numbers,
        'default_calendar_view': preferences.default_calendar_view,
        'show_profile_to_others': preferences.show_profile_to_others,
        'show_phone_to_others': preferences.show_phone_to_others,
        'high_contrast': preferences.high_contrast,
        'font_size': preferences.font_size,
        'reduce_animations': preferences.reduce_animations,
    }
    
    from django.http import HttpResponse
    import json
    
    response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="preferences_{request.user.sap}.json"'
    
    return response
