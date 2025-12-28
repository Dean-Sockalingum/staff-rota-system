"""
Manager views for overtime preference management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import User
from .models_overtime import StaffOvertimePreference
from .models_multi_home import CareHome
from scheduling.models import Unit


@login_required
def overtime_preferences_list(request):
    """
    List all staff overtime preferences with filtering
    """
    # Check permissions
    if not (request.user.role and request.user.role.is_management):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('staff_dashboard')
    
    # Get filters
    search_query = request.GET.get('search', '')
    care_home_filter = request.GET.get('care_home', '')
    availability_filter = request.GET.get('availability', '')
    
    # Get all preferences
    preferences = StaffOvertimePreference.objects.select_related('staff', 'staff__role', 'staff__unit').all()
    
    # Apply filters
    if search_query:
        preferences = preferences.filter(
            Q(staff__first_name__icontains=search_query) |
            Q(staff__last_name__icontains=search_query) |
            Q(staff__sap__icontains=search_query)
        )
    
    if care_home_filter:
        preferences = preferences.filter(staff__unit__care_home__name=care_home_filter)
    
    if availability_filter == 'available':
        preferences = preferences.filter(available_for_overtime=True)
    elif availability_filter == 'unavailable':
        preferences = preferences.filter(available_for_overtime=False)
    
    # Get staff without preferences
    staff_with_prefs = preferences.values_list('staff_id', flat=True)
    staff_without_prefs = User.objects.filter(
        is_active=True,
        role__is_management=False
    ).exclude(pk__in=staff_with_prefs).count()
    
    # Statistics
    total_available = preferences.filter(available_for_overtime=True).count()
    total_preferences = preferences.count()
    
    context = {
        'preferences': preferences.order_by('staff__last_name', 'staff__first_name'),
        'care_homes': CareHome.objects.filter(is_active=True).order_by('name'),
        'search_query': search_query,
        'care_home_filter': care_home_filter,
        'availability_filter': availability_filter,
        'total_available': total_available,
        'total_preferences': total_preferences,
        'staff_without_prefs': staff_without_prefs,
    }
    
    return render(request, 'scheduling/overtime_preferences_list.html', context)


@login_required
def overtime_preference_form(request, preference_id=None):
    """
    Add or edit overtime preference for a staff member
    """
    # Check permissions
    if not (request.user.role and request.user.role.is_management):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('staff_dashboard')
    
    # Get existing preference or create new
    if preference_id:
        preference = get_object_or_404(StaffOvertimePreference, id=preference_id)
        is_new = False
    else:
        preference = None
        is_new = True
    
    if request.method == 'POST':
        # Get staff member
        staff_id = request.POST.get('staff_id')
        
        if not staff_id:
            messages.error(request, 'Please select a staff member.')
            return redirect('overtime_preference_add')
        
        staff = get_object_or_404(User, sap=staff_id)
        
        # Get or create preference
        if preference:
            pref = preference
        else:
            # Check if preference already exists for this staff member
            existing_pref = StaffOvertimePreference.objects.filter(staff=staff).first()
            if existing_pref:
                messages.info(request, f'{staff.full_name} already has overtime preferences. Redirecting to edit.')
                return redirect('overtime_preference_edit', preference_id=existing_pref.id)
            
            # Create new preference
            pref = StaffOvertimePreference.objects.create(staff=staff)
        
        # Update fields
        pref.available_for_overtime = request.POST.get('available_for_overtime') == 'on'
        pref.available_early_shifts = request.POST.get('available_early_shifts') == 'on'
        pref.available_late_shifts = False  # Not used - only day/night
        pref.available_night_shifts = request.POST.get('available_night_shifts') == 'on'
        pref.available_weekdays = request.POST.get('available_weekdays') == 'on'
        pref.available_weekends = request.POST.get('available_weekends') == 'on'
        pref.phone_number = request.POST.get('phone_number', '')
        pref.preferred_contact_method = request.POST.get('preferred_contact_method', 'PHONE')
        pref.max_hours_per_week = request.POST.get('max_hours_per_week') or None
        pref.min_notice_hours = request.POST.get('min_notice_hours', 24)
        pref.notes = request.POST.get('notes', '')
        pref.save()
        
        # Update willing to work at homes
        willing_homes = request.POST.getlist('willing_to_work_at')
        pref.willing_to_work_at.clear()
        if willing_homes:
            for home_name in willing_homes:
                try:
                    care_home = CareHome.objects.get(name=home_name)
                    # Add all units from this care home
                    units = Unit.objects.filter(care_home=care_home, is_active=True)
                    pref.willing_to_work_at.add(*units)
                except CareHome.DoesNotExist:
                    pass
        
        messages.success(request, f'Overtime preferences for {staff.full_name} have been saved.')
        return redirect('overtime_preferences_list')
    
    # GET request - show form
    # Get all active staff without preferences (for new entries)
    if is_new:
        existing_staff_ids = StaffOvertimePreference.objects.values_list('staff_id', flat=True)
        available_staff = User.objects.filter(
            is_active=True,
            role__is_management=False
        ).exclude(pk__in=existing_staff_ids).order_by('last_name', 'first_name')
    else:
        available_staff = None
    
    # Get selected homes for existing preference
    selected_homes = []
    if preference:
        # Get unique care homes from willing_to_work_at units
        for unit in preference.willing_to_work_at.all():
            if unit.care_home and unit.care_home.name not in selected_homes:
                selected_homes.append(unit.care_home.name)
    
    context = {
        'preference': preference,
        'is_new': is_new,
        'available_staff': available_staff,
        'care_homes': CareHome.objects.filter(is_active=True).order_by('name'),
        'selected_homes': selected_homes,
        'contact_methods': [
            ('PHONE', 'Phone Call'),
            ('TEXT', 'Text Message'),
            ('EMAIL', 'Email'),
            ('WHATSAPP', 'WhatsApp'),
        ],
    }
    
    return render(request, 'scheduling/overtime_preference_form.html', context)


@login_required
def overtime_preference_delete(request, preference_id):
    """
    Delete an overtime preference
    """
    # Check permissions
    if not (request.user.role and request.user.role.is_management):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('staff_dashboard')
    
    preference = get_object_or_404(StaffOvertimePreference, id=preference_id)
    staff_name = preference.staff.full_name
    
    if request.method == 'POST':
        preference.delete()
        messages.success(request, f'Overtime preferences for {staff_name} have been deleted.')
        return redirect('overtime_preferences_list')
    
    return redirect('overtime_preferences_list')
