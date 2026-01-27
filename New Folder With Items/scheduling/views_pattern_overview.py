"""
Pattern Overview - Excel-style scrollable establishment view
Shows 3-week rota patterns for all staff positions
Allows marking positions as VACANCY when staff leave
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict
import json

from .models import User, Shift, Unit, CareHome, Notification, LeaveRequest
from .models_multi_home import CareHome as MultiHomeCareHome
from .models_automated_workflow import SicknessAbsence
from .workflow_orchestrator import trigger_absence_workflow
from staff_records.models import SicknessRecord, StaffProfile


@login_required
def pattern_overview(request):
    """
    Pattern Overview View - Excel-style scrollable establishment view
    Shows all staff positions with their 3-week shift patterns
    """
    # Check permissions
    if not (request.user.role and request.user.role.can_manage_rota):
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, 'You do not have permission to view the pattern overview.')
        return redirect('staff_dashboard')
    
    # Get filter parameters
    selected_home = request.GET.get('care_home', 'all')
    selected_unit = request.GET.get('unit', 'all')
    selected_shift_type = request.GET.get('shift_type', 'all')
    
    # Get all care homes
    care_homes = MultiHomeCareHome.objects.all().order_by('name')
    
    # Get units based on selected care home
    units = Unit.objects.filter(is_active=True)
    if selected_home != 'all':
        units = units.filter(care_home__name=selected_home)
    
    # Calculate date range for 3-week view
    # Use Jan 27, 2026 as base date (Monday) - matches our import
    base_date = datetime(2026, 1, 27).date()
    end_date = base_date + timedelta(days=20)  # 21 days total (3 weeks)
    
    # Generate date columns
    date_range = []
    current = base_date
    while current <= end_date:
        date_range.append({
            'date': current,
            'day_name': current.strftime('%a'),
            'day_num': current.day,
        })
        current += timedelta(days=1)
    
    # Get staff and their shifts
    staff_query = User.objects.filter(is_active=True)
    
    # Filter by care home
    if selected_home != 'all':
        staff_query = staff_query.filter(unit__care_home__name=selected_home)
    
    # Filter by unit (handle both clean names like "Bluebell" and full names like "MEADOWBURN_Bluebell")
    if selected_unit != 'all':
        # Check if it's a clean name (no underscores) or full name (has underscores)
        if '_' in selected_unit:
            # Full name provided
            staff_query = staff_query.filter(unit__name=selected_unit)
        else:
            # Clean name provided - match units ending with this name
            staff_query = staff_query.filter(unit__name__endswith=selected_unit)
    
    # Order by unit, then role, then name
    staff_query = staff_query.select_related('unit', 'role', 'unit__care_home').order_by(
        'unit__name',
        'role__name', 
        'first_name',
        'last_name'
    )
    
    # Get all shifts for the date range
    shifts_query = Shift.objects.filter(
        date__range=[base_date, end_date]
    ).select_related('user', 'shift_type')
    
    # Filter shifts by care home/unit
    if selected_home != 'all':
        shifts_query = shifts_query.filter(unit__care_home__name=selected_home)
    if selected_unit != 'all':
        # Same logic for shifts
        if '_' in selected_unit:
            shifts_query = shifts_query.filter(unit__name=selected_unit)
        else:
            shifts_query = shifts_query.filter(unit__name__endswith=selected_unit)
    
    # Organize shifts by user and date
    shifts_by_user_date = defaultdict(dict)
    for shift in shifts_query:
        shifts_by_user_date[shift.user.id][shift.date] = shift
    
    # Pre-calculate unit positions for color assignment based on ALL units in the home
    # This ensures colors stay consistent regardless of filtering
    unit_to_position = {}
    
    # Get ALL active units for the selected home (not just those with visible shifts/staff)
    all_units_query = Unit.objects.filter(is_active=True)
    if selected_home != 'all':
        all_units_query = all_units_query.filter(care_home__name=selected_home)
    
    # Sort ALL units alphabetically and assign color positions
    sorted_all_units = sorted(all_units_query, key=lambda u: u.name)
    for position, unit in enumerate(sorted_all_units, start=1):
        full_unit_name = unit.name
        clean_name = full_unit_name.split('_')[-1] if '_' in full_unit_name else full_unit_name
        # Position wraps if more than 9 units (colors 1-9 cycle)
        color_position = ((position - 1) % 9) + 1
        unit_to_position[full_unit_name] = color_position
        unit_to_position[clean_name] = color_position  # Also map clean name
    
    # Build staff pattern data grouped by unit
    units_data = defaultdict(list)
    
    for staff in staff_query:
        # Build pattern for this staff member
        pattern = []
        has_day_shifts = False
        has_night_shifts = False
        
        for day_info in date_range:
            date = day_info['date']
            shift = shifts_by_user_date.get(staff.id, {}).get(date)
            
            if shift:
                # Get unit name for the shift
                full_unit_name = shift.unit.name if shift.unit else staff.unit.name if staff.unit else 'Unassigned'
                shift_type_name = shift.shift_type.name.upper()
                
                # Strip home prefix to get clean unit name (e.g., "HAWTHORN_HOUSE_Pear" -> "Pear")
                # Split by underscore and take the last part
                clean_unit_name = full_unit_name.split('_')[-1] if '_' in full_unit_name else full_unit_name
                
                # Determine if it's a night shift for styling
                is_night = 'NIGHT' in shift_type_name
                
                # Track shift types for filtering
                if is_night:
                    has_night_shifts = True
                else:
                    has_day_shifts = True
            else:
                full_unit_name = ''
                clean_unit_name = ''
                is_night = False
            
            pattern.append({
                'date': date,
                'unit_name': full_unit_name,  # Full name for backend operations
                'clean_unit_name': clean_unit_name,  # Display name without home prefix
                'has_shift': bool(shift),
                'is_night': is_night,
                'shift_id': shift.id if shift else None,
                'color_position': unit_to_position.get(clean_unit_name, 1)  # Position-based color (1-9)
            })
        
        # Apply shift type filter
        if selected_shift_type == 'day' and not has_day_shifts:
            continue  # Skip night-only staff
        if selected_shift_type == 'night' and not has_night_shifts:
            continue  # Skip day-only staff
        
        # Calculate hours per week (based on shifts in 3-week period)
        total_shifts = sum(1 for p in pattern if p['has_shift'])
        hours_per_week = (total_shifts * 12) / 3 if total_shifts > 0 else 0  # Assuming 12hr shifts
        
        staff_data = {
            'id': staff.id,
            'sap': staff.sap,
            'name': staff.get_full_name(),
            'first_name': staff.first_name,
            'last_name': staff.last_name,
            'role': staff.role.name if staff.role else '',
            'team': staff.team if staff.team else '',
            'hours_per_week': round(hours_per_week),
            'unit': staff.unit.name if staff.unit else '',
            'pattern': pattern,
            'is_vacancy': staff.first_name.upper() == 'VACANCY' or staff.last_name.upper() == 'VACANCY'
        }
        
        unit_name = staff.unit.name if staff.unit else 'Unassigned'
        units_data[unit_name].append(staff_data)
    
    # Create a dict with clean unit names for display
    # Use the pre-calculated positions
    units_data_clean = {}
    
    for full_unit_name, staff_list in units_data.items():
        # Strip home prefix (e.g., "HAWTHORN_HOUSE_Pear" -> "Pear")
        clean_name = full_unit_name.split('_')[-1] if '_' in full_unit_name else full_unit_name
        
        # Get the pre-calculated color position
        color_position = unit_to_position.get(clean_name, 1)
        
        units_data_clean[clean_name] = {
            'full_name': full_unit_name,
            'clean_name': clean_name,
            'staff_list': staff_list,
            'color_position': color_position  # For CSS class: unit-pos-1, unit-pos-2, etc.
        }
    
    # Get unique units for this home (for legend and dropdowns)
    # Build a mapping of unit names to their color positions
    unit_color_map = {}
    for clean_name, unit_info in units_data_clean.items():
        unit_color_map[clean_name] = unit_info['color_position']
    
    # Get unique units for this home (for legend and dropdowns)
    unique_units = set()
    for staff in staff_query:
        if staff.unit:
            clean_unit = staff.unit.name.split('_')[-1] if '_' in staff.unit.name else staff.unit.name
            unique_units.add(clean_unit)
    unique_units = sorted(list(unique_units))
    
    # Get ALL units for the selected home (for modal dropdown - unfiltered)
    # Calculate color positions for ALL units alphabetically, not just those with shifts
    all_home_units_query = Unit.objects.filter(is_active=True)
    if selected_home != 'all':
        all_home_units_query = all_home_units_query.filter(care_home__name=selected_home)
    
    # Build sorted list and assign color positions
    all_home_units = []
    sorted_all_units = sorted(all_home_units_query, key=lambda u: u.name)
    for position, unit in enumerate(sorted_all_units, start=1):
        clean_name = unit.name.split('_')[-1] if '_' in unit.name else unit.name
        color_position = ((position - 1) % 9) + 1  # Assign positions 1-9, cycling
        all_home_units.append({
            'name': clean_name,
            'full_name': unit.name,
            'color_position': color_position
        })
    
    # Build legend data with colors
    legend_data = []
    for unit_name in unique_units:
        legend_data.append({
            'name': unit_name,
            'color_position': unit_color_map.get(unit_name, 1)
        })
    
    # Get selected home label
    if selected_home == 'all':
        selected_home_label = 'All Homes'
    else:
        home_obj = care_homes.filter(name=selected_home).first()
        selected_home_label = home_obj.get_name_display() if home_obj else selected_home
    
    context = {
        'date_range': date_range,
        'units_data': units_data_clean,
        'unique_units': unique_units,
        'all_home_units': all_home_units,  # All units for modal dropdown
        'legend_data': legend_data,  # Units with their color positions
        'unit_color_map': unit_color_map,  # Map of unit names to color positions
        'base_date': base_date,
        'end_date': end_date,
        'care_homes': care_homes,
        'units': units,
        'selected_home': selected_home,
        'selected_home_label': selected_home_label,
        'selected_unit': selected_unit,
        'selected_shift_type': selected_shift_type,
        'total_positions': staff_query.count(),
        'total_vacancies': staff_query.filter(
            first_name__iexact='VACANCY'
        ).count() + staff_query.filter(
            last_name__iexact='VACANCY'
        ).count(),
    }
    
    response = render(request, 'scheduling/pattern_overview.html', context)
    # Prevent browser caching of this page
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@login_required
@require_POST
def toggle_vacancy_status(request):
    """
    AJAX endpoint to toggle a staff position between filled and VACANCY
    """
    import json
    
    try:
        data = json.loads(request.body)
        staff_id = data.get('staff_id')
        set_as_vacancy = data.get('set_as_vacancy', True)
        
        staff = User.objects.get(id=staff_id)
        
        # Check permissions
        if not (request.user.role and request.user.role.can_manage_rota):
            return JsonResponse({
                'success': False,
                'error': 'Permission denied'
            }, status=403)
        
        with transaction.atomic():
            if set_as_vacancy:
                # Mark as vacancy - keep original data in a backup field if needed
                # For now, just change name to VACANCY
                staff.first_name = 'VACANCY'
                staff.last_name = f'{staff.role.name if staff.role else "POSITION"}'
                staff.is_active = False  # Make inactive so they don't show in normal lists
                staff.save()
                
                message = f'Position marked as VACANCY: {staff.role.name if staff.role else "Unknown role"}'
            else:
                # Would need UI to collect new staff details
                # For now, just return error
                return JsonResponse({
                    'success': False,
                    'error': 'Filling vacancy requires full staff details. Use Staff Management to add new staff.'
                })
        
        return JsonResponse({
            'success': True,
            'message': message,
            'staff_id': staff.id,
            'new_name': staff.get_full_name()
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Staff member not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_POST
@login_required
def update_shift_unit(request):
    """
    API endpoint to update a shift's unit OR mark as leave/absence
    Handles:
    - Unit reassignment (unit name)
    - Annual leave (LEAVE_ANNUAL)
    - Sickness (LEAVE_SICK - triggers workflow automation)
    - Unauthorised leave (LEAVE_UNAUTHORISED)
    """
    # Check permissions
    if not (request.user.role and request.user.role.can_manage_rota):
        return JsonResponse({
            'success': False,
            'error': 'You do not have permission to update shifts'
        }, status=403)
    
    try:
        data = json.loads(request.body)
        shift_id = data.get('shift_id')
        unit_name = data.get('unit_name')
        
        if not shift_id or not unit_name:
            return JsonResponse({
                'success': False,
                'error': 'Missing shift_id or unit_name'
            }, status=400)
        
        # Get the shift
        shift = Shift.objects.get(id=shift_id)
        
        # Check if it's a leave type
        if unit_name.startswith('LEAVE_'):
            leave_type = unit_name.replace('LEAVE_', '')
            
            with transaction.atomic():
                if leave_type == 'SICK':
                    # Mark shift as uncovered
                    shift.status = 'UNCOVERED'
                    shift.save()
                    
                    # Create or update sickness absence record (workflow system)
                    absence, created = SicknessAbsence.objects.get_or_create(
                        staff_member=shift.user,
                        start_date=shift.date,
                        defaults={
                            'reported_by': request.user,
                            'expected_duration_days': 1,
                            'end_date': shift.date,
                            'status': 'LOGGED'
                        }
                    )
                    
                    if not created:
                        # Update existing absence to include this date
                        if absence.end_date and shift.date > absence.end_date:
                            absence.end_date = shift.date
                            days_diff = (absence.end_date - absence.start_date).days + 1
                            absence.expected_duration_days = days_diff
                            absence.save()
                    
                    # Add shift to affected shifts
                    absence.affected_shifts.add(shift)
                    
                    # Also create SicknessRecord in staff_records app (for Bradford Factor tracking)
                    try:
                        # Get or create StaffProfile
                        staff_profile, _ = StaffProfile.objects.get_or_create(
                            user=shift.user,
                            defaults={
                                'date_of_birth': shift.user.date_of_birth if hasattr(shift.user, 'date_of_birth') else None,
                                'contact_number': shift.user.phone_number if hasattr(shift.user, 'phone_number') else '',
                            }
                        )
                        
                        # Create or update SicknessRecord
                        sickness_record, sr_created = SicknessRecord.objects.get_or_create(
                            profile=staff_profile,
                            first_working_day=shift.date,
                            defaults={
                                'reported_by': request.user,
                                'reported_at': timezone.now(),
                                'status': 'OPEN',
                                'reason': f'Sickness reported via Pattern Overview for {shift.date.strftime("%d %b %Y")}',
                                'estimated_return_to_work': shift.date + timedelta(days=1)
                            }
                        )
                        
                        if not sr_created:
                            # Update existing record
                            if sickness_record.actual_last_working_day and shift.date > sickness_record.first_working_day:
                                sickness_record.actual_last_working_day = shift.date
                                sickness_record.save()
                        
                        sickness_msg = "Bradford Factor record updated." if not sr_created else "Bradford Factor record created."
                    except Exception as e:
                        sickness_msg = f"Warning: Bradford tracking failed ({str(e)})"
                    
                    # Trigger automated workflow (reallocation, OT offers, manager notifications)
                    try:
                        workflow_result = trigger_absence_workflow(absence)
                        workflow_msg = "Automated cover workflow triggered" if workflow_result.get('success') else "Workflow triggered with warnings"
                    except Exception as e:
                        workflow_msg = f"Workflow trigger failed: {str(e)}"
                    
                    # Create management notification
                    try:
                        Notification.objects.create(
                            user=shift.user.unit.care_home.head_of_service if hasattr(shift.user.unit.care_home, 'head_of_service') else None,
                            notification_type='SICKNESS',
                            title=f'Sickness Absence: {shift.user.full_name}',
                            message=f'{shift.user.full_name} reported sick for {shift.date.strftime("%d %b %Y")}. {workflow_msg} {sickness_msg}',
                            priority='HIGH',
                            action_url=f'/admin/scheduling/sicknessabsence/{absence.id}/change/'
                        )
                    except:
                        pass  # Notification optional
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Sickness recorded for {shift.user.full_name}. {workflow_msg} {sickness_msg}',
                        'display_text': 'SICK',
                        'leave_type': 'SICK'
                    })
                    
                elif leave_type == 'ANNUAL':
                    # Mark shift as uncovered (staff on annual leave)
                    shift.status = 'UNCOVERED'
                    shift.save()
                    
                    # Create or update LeaveRequest for this date
                    leave_request, created = LeaveRequest.objects.get_or_create(
                        user=shift.user,
                        start_date=shift.date,
                        end_date=shift.date,
                        leave_type='ANNUAL',
                        defaults={
                            'days_requested': 1,
                            'status': 'APPROVED',  # Auto-approve from rota
                            'approved_by': request.user,
                            'approval_date': timezone.now(),
                            'approval_notes': 'Approved via Pattern Overview rota allocation',
                            'reason': 'Annual leave allocated via rota'
                        }
                    )
                    
                    # Calculate if user has enough leave remaining
                    remaining = shift.user.annual_leave_remaining
                    warning_msg = ''
                    if remaining < 0:
                        warning_msg = f' ⚠️ WARNING: {shift.user.full_name} now has {abs(remaining)} days OVER their allowance!'
                    
                    # Create notification for management
                    try:
                        Notification.objects.create(
                            user=shift.user.unit.care_home.head_of_service if hasattr(shift.user.unit.care_home, 'head_of_service') else None,
                            notification_type='LEAVE',
                            title=f'Annual Leave: {shift.user.full_name}',
                            message=f'{shift.user.full_name} marked as annual leave for {shift.date.strftime("%d %b %Y")}. Remaining: {remaining} days.{warning_msg}',
                            priority='HIGH' if remaining < 0 else 'MEDIUM',
                            action_url=f'/admin/scheduling/leaverequest/{leave_request.id}/change/'
                        )
                    except:
                        pass  # Notification optional
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Annual leave recorded for {shift.user.full_name}. Remaining: {remaining} days.{warning_msg}',
                        'display_text': 'A/L',
                        'leave_type': 'ANNUAL',
                        'remaining_days': remaining
                    })
                    
                elif leave_type == 'UNAUTHORISED':
                    # Mark shift as uncovered
                    shift.status = 'UNCOVERED'
                    shift.save()
                    
                    # Create LeaveRequest marked as unauthorised (for tracking)
                    try:
                        unauthorised_leave = LeaveRequest.objects.create(
                            user=shift.user,
                            start_date=shift.date,
                            end_date=shift.date,
                            leave_type='OTHER',  # Use OTHER category for unauthorised
                            days_requested=1,
                            status='DENIED',  # Mark as denied since it's unauthorised
                            approved_by=request.user,
                            approval_date=timezone.now(),
                            approval_notes='UNAUTHORISED ABSENCE - marked via Pattern Overview. Disciplinary action may be required.',
                            reason='Unauthorised absence - no approval given'
                        )
                        leave_msg = f"Absence record created (ID: {unauthorised_leave.id})."
                    except Exception as e:
                        leave_msg = f"Warning: Could not create absence record ({str(e)})"
                    
                    # Create urgent notification for management
                    try:
                        Notification.objects.create(
                            user=shift.user.unit.care_home.head_of_service if hasattr(shift.user.unit.care_home, 'head_of_service') else None,
                            notification_type='ALERT',
                            title=f'⚠️ Unauthorised Absence: {shift.user.full_name}',
                            message=f'{shift.user.full_name} marked as unauthorised leave for {shift.date.strftime("%d %b %Y")}. {leave_msg} Disciplinary action may be required.',
                            priority='URGENT',
                            action_url=f'/admin/scheduling/leaverequest/{unauthorised_leave.id}/change/' if 'unauthorised_leave' in locals() else f'/admin/scheduling/shift/{shift.id}/change/'
                        )
                    except:
                        pass  # Notification optional
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Unauthorised leave recorded. Management notified. {leave_msg}',
                        'display_text': 'UNAUTH',
                        'leave_type': 'UNAUTHORISED'
                    })
        
        else:
            # Regular unit change
            # Get the unit (handle both full names like "HAWTHORN_HOUSE_Thistle" and clean names like "Thistle")
            unit = None
            if '_' in unit_name:
                # Full name provided
                unit = Unit.objects.get(name=unit_name, is_active=True)
            else:
                # Clean name provided - find matching unit in the shift's staff's care home
                staff_home = shift.user.unit.care_home if shift.user and shift.user.unit else None
                if staff_home:
                    # Try to find unit ending with the clean name in the same home
                    units = Unit.objects.filter(
                        care_home=staff_home,
                        is_active=True,
                        name__endswith=unit_name
                    )
                    if units.exists():
                        unit = units.first()
            
            if not unit:
                return JsonResponse({
                    'success': False,
                    'error': f'Unit "{unit_name}" not found'
                }, status=404)
            
            # Update the shift
            with transaction.atomic():
                shift.unit = unit
                shift.status = 'SCHEDULED'  # Reset status when moving units
                shift.save()
            
            # Return clean unit name for display
            clean_name = unit.name.split('_')[-1] if '_' in unit.name else unit.name
            
            return JsonResponse({
                'success': True,
                'message': f'Shift updated to {clean_name}',
                'unit_name': clean_name,
                'full_unit_name': unit.name
            })
        
    except Shift.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Shift not found'
        }, status=404)
    except Unit.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Unit "{unit_name}" not found'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
