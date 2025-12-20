"""
Head of Service Dashboard View
===============================

Aggregated multi-home dashboard for Head of Service team oversight.
Provides governance and strategic oversight across all 5 care homes for:
- Quality assurance
- Fiscal monitoring
- Staff allocation
- Compliance tracking

Access: SM (Service Manager), OM (Operations Manager), HOS (Head of Service), IDI (IDI Team)
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q, F, Prefetch
from django.db import models
from django.http import HttpResponse
from datetime import datetime, timedelta
from decimal import Decimal
import csv

from .models import Shift, Unit, User, LeaveRequest, StaffReallocation, Resident, CarePlanReview
from .models_multi_home import CareHome
# Automated workflow models - to be integrated in Phase 2
# from .models_automated_workflow import (
#     StaffingCoverRequest, ReallocationRequest, AgencyRequest
# )


@login_required
def senior_management_dashboard(request):
    """
    Head of Service Dashboard - Multi-home governance oversight
    
    Provides aggregated strategic view across all 5 care homes:
    - Orchard Grove, Meadowburn, Hawthorn House, Riverside, Victoria Gardens
    
    Restricted to: SM, OM, HOS, IDI roles
    
    Supports date range filtering via GET parameters:
    - start_date: YYYY-MM-DD format (default: today)
    - end_date: YYYY-MM-DD format (default: today)
    """
    
    # Check if user has Head of Service team permissions
    # HOS team (SM, OM, HOS, IDI) sits above home-level staff and provides governance oversight across all 5 homes
    if not (request.user.role and request.user.role.is_senior_management_team):
        return render(request, 'scheduling/access_denied.html', {
            'message': 'This dashboard is restricted to Head of Service team members only (SM, OM, HOS, IDI). Access provides governance oversight across all care homes.'
        })
    
    today = timezone.now().date()
    
    # Handle date range parameters
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    selected_home = request.GET.get('care_home', '')  # Filter by care home
    
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = today
    else:
        start_date = today
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            end_date = today
    else:
        end_date = today
    
    # Ensure start_date is before end_date
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    days_in_range = (end_date - start_date).days + 1
    
    current_month_start = today.replace(day=1)
    next_month_start = (current_month_start + timedelta(days=32)).replace(day=1)
    
    # Get all care homes with optimized prefetch for units and today's shifts
    care_homes = CareHome.objects.prefetch_related(
        'units',  # Load all units in one query
        Prefetch(
            'units__shift_set',
            queryset=Shift.objects.filter(
                date=today,
                status__in=['SCHEDULED', 'CONFIRMED']
            ).select_related('user', 'shift_type'),
            to_attr='today_shifts'
        )
    ).order_by('name')
    
    # Filter by selected home if provided
    if selected_home:
        care_homes = care_homes.filter(name=selected_home)
    
    # =================================================================
    # SECTION 1: HOME OVERVIEW - Occupancy & Capacity
    # =================================================================
    home_overview = []
    total_capacity = 0
    total_occupancy = 0
    
    for home in care_homes:
        # Use prefetched units instead of querying database
        units = [u for u in home.units.all() if u.is_active]
        unit_count = len(units)
        
        occupancy_rate = (home.current_occupancy / home.bed_capacity * 100) if home.bed_capacity > 0 else 0
        
        home_overview.append({
            'home': home,
            'display_name': home.get_name_display(),
            'occupancy': home.current_occupancy,
            'capacity': home.bed_capacity,
            'occupancy_rate': occupancy_rate,
            'units': unit_count,
            'location': home.location_address,
        })
        
        total_capacity += home.bed_capacity
        total_occupancy += home.current_occupancy
    
    overall_occupancy_rate = (total_occupancy / total_capacity * 100) if total_capacity > 0 else 0
    
    # =================================================================
    # SECTION 2: STAFFING LEVELS - Date Range Coverage
    # =================================================================
    staffing_today = []
    
    # Home-specific staffing requirements
    # Minimum = Regulatory/safety minimum (after factoring leave/sickness)
    # Ideal = Full rota when everyone scheduled (25-41 range from base model)
    home_staffing = {
        'HAWTHORN_HOUSE': {'day_min': 18, 'day_ideal': 41, 'night_min': 18, 'night_ideal': 41},
        'MEADOWBURN': {'day_min': 17, 'day_ideal': 41, 'night_min': 17, 'night_ideal': 41},
        'ORCHARD_GROVE': {'day_min': 17, 'day_ideal': 41, 'night_min': 17, 'night_ideal': 41},
        'RIVERSIDE': {'day_min': 17, 'day_ideal': 41, 'night_min': 17, 'night_ideal': 41},
        'VICTORIA_GARDENS': {'day_min': 10, 'day_ideal': 18, 'night_min': 10, 'night_ideal': 14},
    }
    
    for home in care_homes:
        # Use prefetched units and shifts
        units = [u for u in home.units.all() if u.is_active]
        
        # Collect today's shifts from prefetched data
        today_shifts = []
        for unit in units:
            if hasattr(unit, 'today_shifts'):
                today_shifts.extend(unit.today_shifts)
        
        # Count by shift type - use set to ensure unique users
        day_users = set()
        night_users = set()
        for shift in today_shifts:
            if shift.user:
                if 'DAY' in shift.shift_type.name.upper():
                    day_users.add(shift.user.pk)
                elif 'NIGHT' in shift.shift_type.name.upper():
                    night_users.add(shift.user.pk)
        
        day_shifts = len(day_users)
        night_shifts = len(night_users)
        
        # Get home-specific requirements
        requirements = home_staffing.get(home.name, {'day_min': 17, 'day_ideal': 24, 'night_min': 17, 'night_ideal': 21})
        
        # Calculate required vs actual (for TODAY only, not per day in range)
        day_required = requirements['day_min']
        night_required = requirements['night_min']
        
        day_coverage = (day_shifts / day_required * 100) if day_required > 0 else 100
        night_coverage = (night_shifts / night_required * 100) if night_required > 0 else 100
        
        staffing_today.append({
            'home': home.get_name_display(),
            'day_actual': day_shifts,
            'day_required': day_required,
            'day_coverage': day_coverage,
            'night_actual': night_shifts,
            'night_required': night_required,
            'night_coverage': night_coverage,
            'status': 'good' if day_coverage >= 100 and night_coverage >= 100 else 'critical',
        })
    
    # =================================================================
    # SECTION 3: FISCAL MONITORING - Monthly Budget Tracking
    # =================================================================
    fiscal_summary = []
    total_agency_budget = 0
    total_agency_spend = 0
    total_ot_budget = 0
    total_ot_spend = 0
    
    # Optimize: Single aggregated query for all homes at once
    all_units = []
    for home in care_homes:
        all_units.extend([u for u in home.units.all()])
    
    # Get shifts grouped by care_home in single query
    fiscal_stats = Shift.objects.filter(
        date__gte=start_date,
        date__lte=end_date,
        status__in=['SCHEDULED', 'CONFIRMED']
    ).values('unit__care_home').annotate(
        agency_count=Count('pk', filter=Q(user__isnull=True)),
        ot_count=Count('pk', filter=Q(shift_classification='OVERTIME'))
    )
    
    # Create lookup dict for quick access
    fiscal_lookup = {stat['unit__care_home']: stat for stat in fiscal_stats}
    
    for home in care_homes:
        # Get stats from aggregated query
        stats = fiscal_lookup.get(home.pk, {'agency_count': 0, 'ot_count': 0})
        agency_shifts_count = stats['agency_count']
        ot_shifts = stats['ot_count']
        
        # Estimate: £300 per agency shift (rough average)
        agency_spend = Decimal(str(agency_shifts_count * 300))
        # OT spend for date range (estimated at £25/hour, 12 hours per shift)
        ot_spend = Decimal(str(ot_shifts * 25 * 12))  # Rough estimate
        
        agency_budget = home.budget_agency_monthly
        ot_budget = home.budget_overtime_monthly
        
        agency_utilization = (float(agency_spend) / float(agency_budget) * 100) if agency_budget > 0 else 0
        ot_utilization = (float(ot_spend) / float(ot_budget) * 100) if ot_budget > 0 else 0
        
        fiscal_summary.append({
            'home': home.get_name_display(),
            'agency_budget': agency_budget,
            'agency_spend': agency_spend,
            'agency_utilization': agency_utilization,
            'ot_budget': ot_budget,
            'ot_spend': ot_spend,
            'ot_utilization': ot_utilization,
            'total_budget': agency_budget + ot_budget,
            'total_spend': agency_spend + ot_spend,
            'fiscal_status': 'good' if agency_utilization < 80 and ot_utilization < 80 else 'warning' if agency_utilization < 100 and ot_utilization < 100 else 'over_budget',
        })
        
        total_agency_budget += float(agency_budget)
        total_agency_spend += float(agency_spend)
        total_ot_budget += float(ot_budget)
        total_ot_spend += float(ot_spend)
    
    # =================================================================
    # SECTION 4: STAFFING ALERTS & CRITICAL ISSUES
    # =================================================================
    critical_alerts = []
    
    # TODO: Integrate with StaffingAlert model
    # For now, identify unfilled shifts as "alerts"
    next_week = today + timedelta(days=7)
    
    # Optimize: Get all unfilled shifts in single query, then group by home
    all_home_units = [u for home in care_homes for u in home.units.all()]
    all_unfilled = Shift.objects.filter(
        unit__in=all_home_units,
        date__gte=today,
        date__lte=next_week,
        user__isnull=True,
        status='SCHEDULED'
    ).select_related('unit', 'unit__care_home')[:25]  # Top 25 total
    
    # Group by home
    unfilled_by_home = {}
    for shift in all_unfilled:
        home_name = shift.unit.care_home.name
        if home_name not in unfilled_by_home:
            unfilled_by_home[home_name] = []
        if len(unfilled_by_home[home_name]) < 5:  # Top 5 per home
            unfilled_by_home[home_name].append(shift)
    
    for home in care_homes:
        unfilled = unfilled_by_home.get(home.name, [])
        
        for shift in unfilled:
            critical_alerts.append({
                'home': home.get_name_display(),
                'date': shift.date,
                'unit': shift.unit.name,
                'severity': 'HIGH' if shift.date <= today + timedelta(days=2) else 'MEDIUM',
                'created': shift.created_at if hasattr(shift, 'created_at') else today,
                'age_hours': ((timezone.now() - shift.created_at).total_seconds() / 3600) if hasattr(shift, 'created_at') else 0,
            })
    
    # Sort by age (oldest first)
    critical_alerts = sorted(critical_alerts, key=lambda x: x['age_hours'], reverse=True)[:20]
    
    # =================================================================
    # SECTION 5: PENDING ACTIONS - Require Management Attention
    # =================================================================
    
    # Manual review leave requests (all homes)
    manual_reviews = LeaveRequest.objects.filter(
        status='MANUAL_REVIEW'
    ).select_related('user', 'user__unit').order_by('created_at')
    
    pending_by_home = {}
    for request in manual_reviews:
        if request.user and request.user.unit:
            home = request.user.unit.care_home
            home_name = home.get_name_display() if home else 'Unknown'
            if home_name not in pending_by_home:
                pending_by_home[home_name] = []
            pending_by_home[home_name].append(request)
    
    # Pending reallocations
    pending_reallocations = StaffReallocation.objects.filter(
        status='NEEDED'
    ).select_related('target_unit', 'target_unit__care_home').count()
    
    # Unfilled cover requests (count unfilled shifts)
    unfilled_covers = Shift.objects.filter(
        date__gte=today,
        user__isnull=True,
        status='SCHEDULED'
    ).count()
    
    # =================================================================
    # SECTION 6: QUALITY METRICS
    # =================================================================
    quality_metrics = []
    
    # Last 30 days metrics
    last_30_days = today - timedelta(days=30)
    
    # Optimize: Single aggregated query for quality metrics
    quality_stats = Shift.objects.filter(
        date__gte=last_30_days,
        date__lte=today
    ).values('unit__care_home').annotate(
        total_shifts=Count('pk'),
        unfilled_shifts=Count('pk', filter=Q(user__isnull=True))
    )
    
    quality_lookup = {stat['unit__care_home']: stat for stat in quality_stats}
    
    # Get staff counts by home in single query
    staff_counts = User.objects.filter(
        is_active=True
    ).values('unit__care_home').annotate(
        staff_count=Count('pk')
    )
    staff_lookup = {stat['unit__care_home']: stat['staff_count'] for stat in staff_counts}
    
    for home in care_homes:
        # Get stats from aggregated queries
        stats = quality_lookup.get(home.pk, {'total_shifts': 0, 'unfilled_shifts': 0})
        total_shifts = stats['total_shifts']
        unfilled_shifts = stats['unfilled_shifts']
        
        agency_rate = (unfilled_shifts / total_shifts * 100) if total_shifts > 0 else 0
        
        # Staff turnover (placeholder - would need actual termination data)
        staff_count = staff_lookup.get(home.pk, 0)
        
        quality_metrics.append({
            'home': home.get_name_display(),
            'agency_rate': agency_rate,
            'staff_count': staff_count,
            'shifts_30d': total_shifts,
            'quality_score': 100 - agency_rate,  # Simple inverse for now
        })
    
    # =================================================================
    # SECTION 7: CARE PLAN COMPLIANCE - By Home
    # =================================================================
    # Always show all homes for governance reporting regardless of filter
    care_plan_compliance = []
    all_homes_for_compliance = CareHome.objects.all().order_by('name')
    
    for home in all_homes_for_compliance:
        # Get all active residents for this home
        residents = Resident.objects.filter(
            unit__care_home=home,
            is_active=True
        )
        
        total_residents = residents.count()
        
        # Get latest review for each resident
        reviews = []
        for resident in residents:
            latest_review = resident.care_plan_reviews.order_by('-due_date').first()
            if latest_review:
                reviews.append(latest_review)
        
        # Count by status
        completed = sum(1 for r in reviews if r.status == 'COMPLETED')
        overdue = sum(1 for r in reviews if r.status == 'OVERDUE')
        due_soon = sum(1 for r in reviews if r.status == 'DUE')
        upcoming = sum(1 for r in reviews if r.status == 'UPCOMING')
        in_progress = sum(1 for r in reviews if r.status == 'IN_PROGRESS')
        
        # Calculate compliance rate (completed / total reviews)
        compliance_rate = (completed / len(reviews) * 100) if reviews else 0
        overdue_rate = (overdue / len(reviews) * 100) if reviews else 0
        
        # Always add home to the list for governance visibility
        care_plan_compliance.append({
            'home': home.get_name_display(),
            'home_obj': home,
            'total_residents': total_residents,
            'total_reviews': len(reviews),
            'completed': completed,
            'overdue': overdue,
            'overdue_rate': overdue_rate,
            'due_soon': due_soon,
            'upcoming': upcoming,
            'in_progress': in_progress,
            'compliance_rate': compliance_rate,
        })
    
    # =================================================================
    # SECTION 8: STAFF VACANCIES TRACKING
    # =================================================================
    from staff_records.models import StaffProfile
    
    vacancies = []
    
    # Get all leavers in the last 90 days and upcoming leavers
    ninety_days_ago = today - timedelta(days=90)
    thirty_days_forward = today + timedelta(days=30)
    
    # Get staff profiles for leavers
    leaver_profiles = StaffProfile.objects.filter(
        employment_status='LEAVER',
        end_date__isnull=False
    ).select_related(
        'user',
        'user__role',
        'user__unit',
        'user__unit__care_home'
    ).filter(
        Q(end_date__gte=ninety_days_ago) | Q(end_date__lte=thirty_days_forward)
    ).order_by('-end_date')
    
    for profile in leaver_profiles:
        if not profile.user or not profile.user.unit or not profile.user.unit.care_home:
            continue
            
        # Calculate days vacant
        if profile.end_date <= today:
            days_vacant = (today - profile.end_date).days
            status = 'VACANT'
        else:
            days_vacant = 0
            status = 'UPCOMING'
        
        # Get contracted hours from shifts_per_week (assume 12-hour shifts)
        hours_per_week = profile.user.shifts_per_week_override or 40  # Default 40 hours
        
        vacancies.append({
            'home': profile.user.unit.care_home.get_name_display(),
            'home_obj': profile.user.unit.care_home,
            'role': profile.user.role.get_name_display() if profile.user.role else 'Unknown',
            'role_code': profile.user.role.name if profile.user.role else 'UNKNOWN',
            'staff_name': profile.user.full_name,
            'sap': profile.user.sap,
            'unit': profile.user.unit.name,
            'end_date': profile.end_date,
            'days_vacant': days_vacant,
            'hours_per_week': hours_per_week,
            'status': status,
            'severity': 'HIGH' if days_vacant > 30 else 'MEDIUM' if days_vacant > 14 else 'LOW' if status == 'VACANT' else 'INFO',
        })
    
    # Group by home for summary
    vacancies_by_home = {}
    for v in vacancies:
        home_name = v['home']
        if home_name not in vacancies_by_home:
            vacancies_by_home[home_name] = {
                'home': home_name,
                'total_vacancies': 0,
                'vacant_now': 0,
                'upcoming_leavers': 0,
                'total_hours_vacant': 0,
                'roles': {}
            }
        
        vacancies_by_home[home_name]['total_vacancies'] += 1
        
        if v['status'] == 'VACANT':
            vacancies_by_home[home_name]['vacant_now'] += 1
            vacancies_by_home[home_name]['total_hours_vacant'] += v['hours_per_week']
        else:
            vacancies_by_home[home_name]['upcoming_leavers'] += 1
        
        role = v['role_code']
        if role not in vacancies_by_home[home_name]['roles']:
            vacancies_by_home[home_name]['roles'][role] = 0
        vacancies_by_home[home_name]['roles'][role] += 1
    
    # =================================================================
    # SECTION 9: CITYWIDE SUMMARY - Weekly Overview
    # =================================================================
    # Generate 7-day view starting from start_date
    citywide_day_summary = []
    citywide_night_summary = []
    
    # Create list of dates for the week
    week_dates = [start_date + timedelta(days=i) for i in range(min(7, days_in_range))]
    
    for home in care_homes:
        units = Unit.objects.filter(care_home=home, is_active=True)
        
        # Specific staffing requirements per home (from Head of Service specification)
        home_staffing = {
            'HAWTHORN_HOUSE': {'day_sscw_min': 2, 'day_sscw_ideal': 2, 'day_min': 18, 'day_ideal': 24, 'night_sscwn_min': 2, 'night_sscwn_ideal': 2, 'night_min': 18, 'night_ideal': 21},
            'MEADOWBURN': {'day_sscw_min': 2, 'day_sscw_ideal': 2, 'day_min': 17, 'day_ideal': 24, 'night_sscwn_min': 2, 'night_sscwn_ideal': 2, 'night_min': 17, 'night_ideal': 21},
            'ORCHARD_GROVE': {'day_sscw_min': 2, 'day_sscw_ideal': 2, 'day_min': 17, 'day_ideal': 24, 'night_sscwn_min': 2, 'night_sscwn_ideal': 2, 'night_min': 17, 'night_ideal': 21},
            'RIVERSIDE': {'day_sscw_min': 2, 'day_sscw_ideal': 2, 'day_min': 17, 'day_ideal': 24, 'night_sscwn_min': 2, 'night_sscwn_ideal': 2, 'night_min': 17, 'night_ideal': 21},
            'VICTORIA_GARDENS': {'day_sscw_min': 1, 'day_sscw_ideal': 2, 'day_min': 10, 'day_ideal': 15, 'night_sscwn_min': 1, 'night_sscwn_ideal': 2, 'night_min': 10, 'night_ideal': 12},
        }
        
        requirements = home_staffing.get(home.name, {'day_sscw_min': 2, 'day_sscw_ideal': 2, 'day_min': 17, 'day_ideal': 24, 'night_sscwn_min': 2, 'night_sscwn_ideal': 2, 'night_min': 17, 'night_ideal': 21})
        
        # Day shift summary for this home
        day_data = {
            'home': home.get_name_display(),
            'home_obj': home,
            'sscw_min': requirements['day_sscw_min'],
            'sscw_ideal': requirements['day_sscw_ideal'],
            'min_required': requirements['day_min'],
            'ideal_required': requirements['day_ideal'],
            'days': []
        }
        
        # Night shift summary for this home
        night_data = {
            'home': home.get_name_display(),
            'home_obj': home,
            'sscwn_min': requirements['night_sscwn_min'],
            'sscwn_ideal': requirements['night_sscwn_ideal'],
            'min_required': requirements['night_min'],
            'ideal_required': requirements['night_ideal'],
            'days': []
        }
        
        # For each day in the week
        for date in week_dates:
            # Get shifts for this day
            day_shifts_for_date = Shift.objects.filter(
                unit__in=units,
                date=date,
                shift_type__name__icontains='DAY',
                status__in=['SCHEDULED', 'CONFIRMED']
            )
            
            night_shifts_for_date = Shift.objects.filter(
                unit__in=units,
                date=date,
                shift_type__name__icontains='NIGHT',
                status__in=['SCHEDULED', 'CONFIRMED']
            )
            
            # Count by role and type
            day_seniors = day_shifts_for_date.filter(
                user__role__name='SSCW'
            ).count()
            day_staff = day_shifts_for_date.filter(
                user__role__name__in=['SCW', 'SCA']
            ).count()
            day_leave = LeaveRequest.objects.filter(
                user__unit__in=units,
                start_date__lte=date,
                end_date__gte=date,
                status='APPROVED',
                user__shift_preference__icontains='DAY'
            ).count()
            day_agency = day_shifts_for_date.filter(
                user__sap__startswith='AGENCY'
            ).count() if day_shifts_for_date.filter(user__sap__isnull=False).exists() else 0
            day_overtime = day_shifts_for_date.filter(
                is_overtime=True
            ).count() if hasattr(day_shifts_for_date.first(), 'is_overtime') else 0
            day_absent = day_shifts_for_date.filter(
                status='ABSENT'
            ).count()
            
            night_seniors = night_shifts_for_date.filter(
                user__role__name='SSCWN'
            ).count()
            night_staff = night_shifts_for_date.filter(
                user__role__name__in=['SCWN', 'SCAN']
            ).count()
            night_leave = LeaveRequest.objects.filter(
                user__unit__in=units,
                start_date__lte=date,
                end_date__gte=date,
                status='APPROVED',
                user__shift_preference__icontains='NIGHT'
            ).count()
            night_agency = night_shifts_for_date.filter(
                user__sap__startswith='AGENCY'
            ).count() if night_shifts_for_date.filter(user__sap__isnull=False).exists() else 0
            night_overtime = night_shifts_for_date.filter(
                is_overtime=True
            ).count() if hasattr(night_shifts_for_date.first(), 'is_overtime') else 0
            night_absent = night_shifts_for_date.filter(
                status='ABSENT'
            ).count()
            
            # Add day data
            day_data['days'].append({
                'date': date,
                'day_name': date.strftime('%a'),
                'day_num': date.day,
                'seniors': day_seniors,
                'staff': day_staff,
                'leave': day_leave,
                'agency': day_agency,
                'overtime': day_overtime,
                'absent': day_absent,
                'total': day_seniors + day_staff,
            })
            
            # Add night data
            night_data['days'].append({
                'date': date,
                'day_name': date.strftime('%a'),
                'day_num': date.day,
                'seniors': night_seniors,
                'staff': night_staff,
                'leave': night_leave,
                'agency': night_agency,
                'overtime': night_overtime,
                'absent': night_absent,
                'total': night_seniors + night_staff,
            })
        
        citywide_day_summary.append(day_data)
        citywide_night_summary.append(night_data)
    
    # =================================================================
    # SECTION 8: WEEKLY SNAPSHOT - Simplified Daily Summary per Home
    # =================================================================
    # Generate simplified weekly summary showing SSCW/SSCWN and total Care staff
    weekly_snapshot = []
    
    # Get all care homes for snapshot (respect filtering)
    all_care_homes = CareHome.objects.all().order_by('name')
    if selected_home:
        all_care_homes = all_care_homes.filter(name=selected_home)
    
    for home in all_care_homes:
        units = Unit.objects.filter(care_home=home, is_active=True)
        
        # Home-specific requirements (care staff only, not including SSCW/SSCWN)
        home_staffing_config = {
            'HAWTHORN_HOUSE': {'day_min': 18, 'day_ideal': 18, 'night_min': 18, 'night_ideal': 18, 'day_sscw': 2, 'night_sscw': 2},
            'MEADOWBURN': {'day_min': 17, 'day_ideal': 17, 'night_min': 17, 'night_ideal': 17, 'day_sscw': 2, 'night_sscw': 2},
            'ORCHARD_GROVE': {'day_min': 17, 'day_ideal': 17, 'night_min': 17, 'night_ideal': 17, 'day_sscw': 2, 'night_sscw': 2},
            'RIVERSIDE': {'day_min': 17, 'day_ideal': 17, 'night_min': 17, 'night_ideal': 17, 'day_sscw': 2, 'night_sscw': 2},
            'VICTORIA_GARDENS': {'day_min': 10, 'day_ideal': 10, 'night_min': 10, 'night_ideal': 10, 'day_sscw': 1, 'night_sscw': 1},
        }
        
        requirements = home_staffing_config.get(home.name, {'day_min': 17, 'day_ideal': 17, 'night_min': 17, 'night_ideal': 17})
        
        home_snapshot = {
            'home': home.get_name_display(),
            'home_obj': home,
            'day_ideal': requirements['day_ideal'],
            'night_ideal': requirements['night_ideal'],
            'days': []
        }
        
        # For each day in the week
        for date in week_dates:
            # Day shifts
            day_shifts = Shift.objects.filter(
                unit__in=units,
                date=date,
                shift_type__name__icontains='DAY',
                status__in=['SCHEDULED', 'CONFIRMED']
            )
            
            # Count SSCW only (not SM/OM)
            day_sscw = day_shifts.filter(user__role__name='SSCW').count()
            
            # Count all care staff (SCW + SCA)
            day_care = day_shifts.filter(user__role__name__in=['SCW', 'SCA']).count()
            
            # Night shifts
            night_shifts = Shift.objects.filter(
                unit__in=units,
                date=date,
                shift_type__name__icontains='NIGHT',
                status__in=['SCHEDULED', 'CONFIRMED']
            )
            
            # Count SSCWN only
            night_sscwn = night_shifts.filter(user__role__name='SSCWN').count()
            
            # Count all night care staff (SCWN + SCAN)
            night_care = night_shifts.filter(user__role__name__in=['SCWN', 'SCAN']).count()
            
            home_snapshot['days'].append({
                'date': date,
                'day_sscw': day_sscw,
                'day_care': day_care,
                'night_sscwn': night_sscwn,
                'night_care': night_care,
            })
        
        weekly_snapshot.append(home_snapshot)
    
    # =================================================================
    # Training Compliance Summary (All Homes)
    # =================================================================
    from scheduling.models import TrainingCourse, TrainingRecord
    
    training_compliance_by_home = []
    mandatory_courses = TrainingCourse.objects.filter(is_mandatory=True)
    
    if mandatory_courses.exists():
        for home in care_homes:
            home_staff = User.objects.filter(
                unit__care_home=home,
                is_active=True
            ).distinct()
            
            total_staff = home_staff.count()
            total_required = total_staff * mandatory_courses.count()
            total_compliant = 0
            
            if total_staff > 0:
                for staff in home_staff:
                    for course in mandatory_courses:
                        latest_record = TrainingRecord.objects.filter(
                            staff_member=staff,
                            course=course
                        ).order_by('-completion_date').first()
                        
                        if latest_record and latest_record.get_status() == 'CURRENT':
                            total_compliant += 1
                
                compliance_percentage = (total_compliant / total_required * 100) if total_required > 0 else 0
                
                training_compliance_by_home.append({
                    'home': home,
                    'total_staff': total_staff,
                    'total_required': total_required,
                    'compliant': total_compliant,
                    'percentage': round(compliance_percentage, 1),
                })
    
    # =================================================================
    # Context for Template
    # =================================================================
    context = {
        'today': today,
        'current_time': timezone.now(),
        'current_month': current_month_start.strftime('%B %Y'),
        
        # Date range parameters
        'start_date': start_date,
        'end_date': end_date,
        'days_in_range': days_in_range,
        
        # Filtering
        'all_care_homes': CareHome.objects.all().order_by('name'),
        'selected_home': selected_home,
        
        # Overview
        'home_overview': home_overview,
        'total_capacity': total_capacity,
        'total_occupancy': total_occupancy,
        'overall_occupancy_rate': overall_occupancy_rate,
        'total_homes': care_homes.count(),
        
        # Staffing
        'staffing_today': staffing_today,
        
        # Fiscal
        'fiscal_summary': fiscal_summary,
        'total_agency_budget': total_agency_budget,
        'total_agency_spend': total_agency_spend,
        'total_ot_budget': total_ot_budget,
        'total_ot_spend': total_ot_spend,
        'total_budget': total_agency_budget + total_ot_budget,
        'total_spend': total_agency_spend + total_ot_spend,
        'overall_utilization': ((total_agency_spend + total_ot_spend) / (total_agency_budget + total_ot_budget) * 100) if (total_agency_budget + total_ot_budget) > 0 else 0,
        
        # Alerts & Actions
        'critical_alerts': critical_alerts,
        'pending_by_home': pending_by_home,
        'pending_reallocations': pending_reallocations,
        'unfilled_covers': unfilled_covers,
        
        # Quality
        'quality_metrics': quality_metrics,
        
        # Care Plan Compliance
        'care_plan_compliance': care_plan_compliance,
        
        # Staff Vacancies
        'vacancies': vacancies,
        'vacancies_by_home': vacancies_by_home,
        'total_vacancies': len([v for v in vacancies if v['status'] == 'VACANT']),
        'total_upcoming_leavers': len([v for v in vacancies if v['status'] == 'UPCOMING']),
        
        # Citywide Summary
        'citywide_day_summary': citywide_day_summary,
        'citywide_night_summary': citywide_night_summary,
        'week_dates': week_dates,
        
        # Weekly Snapshot - Simplified view
        'weekly_snapshot': weekly_snapshot,
        
        # Training Compliance
        'training_compliance_by_home': training_compliance_by_home,
    }
    
    return render(request, 'scheduling/senior_management_dashboard.html', context)


@login_required
def senior_dashboard_export(request):
    """
    Export senior dashboard data as CSV
    
    Supports date range filtering via GET parameters:
    - start_date: YYYY-MM-DD format (default: today)
    - end_date: YYYY-MM-DD format (default: today)
    - format: 'csv' (default)
    """
    
    # Check permissions - only Head of Service team members
    if not (request.user.role and request.user.role.is_senior_management_team):
        return HttpResponse('Access Denied - Head of Service Team Only', status=403)
    
    today = timezone.now().date()
    
    # Handle date range parameters
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = today
    else:
        start_date = today
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            end_date = today
    else:
        end_date = today
    
    # Ensure start_date is before end_date
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="senior_dashboard_{start_date}_{end_date}.csv"'
    
    writer = csv.writer(response)
    
    # Header with metadata
    writer.writerow(['Senior Management Dashboard Report'])
    writer.writerow(['Generated:', timezone.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['Date Range:', f'{start_date} to {end_date}'])
    writer.writerow([])
    
    # Get all care homes
    care_homes = CareHome.objects.all().order_by('name')
    
    # ========================================
    # SECTION 1: HOME OVERVIEW
    # ========================================
    writer.writerow(['HOME OVERVIEW'])
    writer.writerow(['Home', 'Current Occupancy', 'Bed Capacity', 'Occupancy Rate %', 'Active Units', 'Location'])
    
    for home in care_homes:
        units = Unit.objects.filter(care_home=home, is_active=True)
        occupancy_rate = (home.current_occupancy / home.bed_capacity * 100) if home.bed_capacity > 0 else 0
        
        writer.writerow([
            home.get_name_display(),
            home.current_occupancy,
            home.bed_capacity,
            f'{occupancy_rate:.1f}',
            units.count(),
            home.location_address
        ])
    
    writer.writerow([])
    
    # ========================================
    # SECTION 2: STAFFING COVERAGE
    # ========================================
    writer.writerow(['STAFFING COVERAGE'])
    writer.writerow(['Home', 'Day Shifts Actual', 'Day Shifts Required', 'Day Coverage %', 
                     'Night Shifts Actual', 'Night Shifts Required', 'Night Coverage %', 'Status'])
    
    days_in_range = (end_date - start_date).days + 1
    
    for home in care_homes:
        units = Unit.objects.filter(care_home=home, is_active=True)
        
        range_shifts = Shift.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            unit__in=units,
            status__in=['SCHEDULED', 'CONFIRMED']
        )
        
        day_shifts = range_shifts.filter(shift_type__name__icontains='DAY').count()
        night_shifts = range_shifts.filter(shift_type__name__icontains='NIGHT').count()
        
        total_required_day = sum(u.min_day_staff for u in units) * days_in_range
        total_required_night = sum(u.min_night_staff for u in units) * days_in_range
        
        day_coverage = (day_shifts / total_required_day * 100) if total_required_day > 0 else 100
        night_coverage = (night_shifts / total_required_night * 100) if total_required_night > 0 else 100
        
        status = 'GOOD' if day_coverage >= 100 and night_coverage >= 100 else 'WARNING' if day_coverage >= 80 and night_coverage >= 80 else 'CRITICAL'
        
        writer.writerow([
            home.get_name_display(),
            day_shifts,
            total_required_day,
            f'{day_coverage:.1f}',
            night_shifts,
            total_required_night,
            f'{night_coverage:.1f}',
            status
        ])
    
    writer.writerow([])
    
    # ========================================
    # SECTION 3: FISCAL SUMMARY
    # ========================================
    writer.writerow(['FISCAL SUMMARY'])
    writer.writerow(['Home', 'Agency Budget', 'Agency Spend', 'Agency Utilization %',
                     'OT Budget', 'OT Spend', 'OT Utilization %', 'Total Budget', 'Total Spend'])
    
    for home in care_homes:
        units = Unit.objects.filter(care_home=home)
        
        # Agency spend for date range
        agency_shifts_count = Shift.objects.filter(
            unit__in=units,
            date__gte=start_date,
            date__lte=end_date,
            user__isnull=True,
            status__in=['SCHEDULED', 'CONFIRMED']
        ).count()
        agency_spend = Decimal(str(agency_shifts_count * 300))
        
        # OT spend for date range
        ot_shifts = Shift.objects.filter(
            unit__in=units,
            date__gte=start_date,
            date__lte=end_date,
            shift_classification='OVERTIME'
        ).count()
        ot_spend = Decimal(str(ot_shifts * 25 * 12))
        
        agency_budget = home.budget_agency_monthly
        ot_budget = home.budget_overtime_monthly
        
        agency_utilization = (float(agency_spend) / float(agency_budget) * 100) if agency_budget > 0 else 0
        ot_utilization = (float(ot_spend) / float(ot_budget) * 100) if ot_budget > 0 else 0
        
        writer.writerow([
            home.get_name_display(),
            f'£{agency_budget}',
            f'£{agency_spend}',
            f'{agency_utilization:.1f}',
            f'£{ot_budget}',
            f'£{ot_spend}',
            f'{ot_utilization:.1f}',
            f'£{agency_budget + ot_budget}',
            f'£{agency_spend + ot_spend}'
        ])
    
    writer.writerow([])
    
    # ========================================
    # SECTION 4: DETAILED SHIFT DATA
    # ========================================
    writer.writerow(['DETAILED SHIFT DATA'])
    writer.writerow(['Date', 'Home', 'Unit', 'Staff Name', 'Staff SAP', 'Shift Type', 
                     'Classification', 'Status', 'Start Time', 'End Time'])
    
    for home in care_homes:
        units = Unit.objects.filter(care_home=home, is_active=True)
        
        shifts = Shift.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            unit__in=units
        ).select_related('user', 'shift_type', 'unit').order_by('date', 'shift_type__name')
        
        for shift in shifts:
            writer.writerow([
                shift.date,
                home.get_name_display(),
                shift.unit.name,
                f'{shift.user.first_name} {shift.user.last_name}' if shift.user else 'UNFILLED',
                shift.user.sap if shift.user else 'N/A',
                shift.shift_type.name,
                shift.shift_classification,
                shift.status,
                shift.custom_start_time or shift.shift_type.default_start_time,
                shift.custom_end_time or shift.shift_type.default_end_time
            ])
    
    return response


@login_required
def custom_report_builder(request):
    """
    Custom Report Builder - Generate reports with user-selected fields and date ranges
    
    Supports multiple output formats:
    - PDF: Professional formatted report
    - Excel: Spreadsheet with data and charts
    - CSV: Raw data export
    
    Restricted to: Senior management team only
    """
    from django.db.models import Model
    from django.apps import apps
    import json
    
    # Check permissions
    if not (request.user.role and request.user.role.is_senior_management_team):
        return render(request, 'scheduling/access_denied.html', {
            'message': 'Report builder is restricted to Head of Service team members only.'
        })
    
    if request.method == 'GET':
        # Display report builder form
        today = timezone.now().date()
        
        # Define available report types and their fields
        report_types = {
            'staffing_coverage': {
                'name': 'Staffing Coverage Report',
                'description': 'Comprehensive staffing levels, shortages, and coverage analysis',
                'fields': [
                    {'id': 'date', 'label': 'Date', 'selected': True},
                    {'id': 'care_home', 'label': 'Care Home', 'selected': True},
                    {'id': 'unit', 'label': 'Unit', 'selected': True},
                    {'id': 'shift_type', 'label': 'Shift Type (Day/Night)', 'selected': True},
                    {'id': 'scheduled_staff', 'label': 'Scheduled Staff Count', 'selected': True},
                    {'id': 'required_staff', 'label': 'Required Staff Count', 'selected': True},
                    {'id': 'shortage', 'label': 'Shortage/Surplus', 'selected': True},
                    {'id': 'sscw_count', 'label': 'SSCW/SSCWN Count', 'selected': False},
                    {'id': 'agency_count', 'label': 'Agency Staff Count', 'selected': False},
                    {'id': 'overtime_count', 'label': 'Overtime Shifts', 'selected': False},
                ]
            },
            'leave_usage': {
                'name': 'Leave Usage Report',
                'description': 'Annual leave, sickness, and other absences across homes',
                'fields': [
                    {'id': 'staff_name', 'label': 'Staff Name', 'selected': True},
                    {'id': 'staff_sap', 'label': 'Staff SAP', 'selected': True},
                    {'id': 'care_home', 'label': 'Care Home', 'selected': True},
                    {'id': 'leave_type', 'label': 'Leave Type', 'selected': True},
                    {'id': 'start_date', 'label': 'Start Date', 'selected': True},
                    {'id': 'end_date', 'label': 'End Date', 'selected': True},
                    {'id': 'days_requested', 'label': 'Days Requested', 'selected': True},
                    {'id': 'status', 'label': 'Status (Approved/Denied/Pending)', 'selected': True},
                    {'id': 'unit', 'label': 'Unit', 'selected': False},
                    {'id': 'role', 'label': 'Role', 'selected': False},
                ]
            },
            'budget_variance': {
                'name': 'Budget Variance Report',
                'description': 'Planned vs actual staffing costs, agency usage, overtime',
                'fields': [
                    {'id': 'care_home', 'label': 'Care Home', 'selected': True},
                    {'id': 'period', 'label': 'Period (Week/Month)', 'selected': True},
                    {'id': 'planned_cost', 'label': 'Planned Cost', 'selected': True},
                    {'id': 'actual_cost', 'label': 'Actual Cost', 'selected': True},
                    {'id': 'variance', 'label': 'Variance (£)', 'selected': True},
                    {'id': 'variance_percent', 'label': 'Variance (%)', 'selected': True},
                    {'id': 'agency_cost', 'label': 'Agency Cost', 'selected': False},
                    {'id': 'overtime_cost', 'label': 'Overtime Cost', 'selected': False},
                    {'id': 'regular_staff_cost', 'label': 'Regular Staff Cost', 'selected': False},
                ]
            },
            'compliance': {
                'name': 'Compliance Report',
                'description': 'Shift compliance, minimum staffing violations, care ratios',
                'fields': [
                    {'id': 'date', 'label': 'Date', 'selected': True},
                    {'id': 'care_home', 'label': 'Care Home', 'selected': True},
                    {'id': 'unit', 'label': 'Unit', 'selected': True},
                    {'id': 'shift_type', 'label': 'Shift Type', 'selected': True},
                    {'id': 'staffing_met', 'label': 'Minimum Staffing Met (Yes/No)', 'selected': True},
                    {'id': 'sscw_present', 'label': 'SSCW Present (Yes/No)', 'selected': True},
                    {'id': 'violation_type', 'label': 'Violation Type', 'selected': False},
                    {'id': 'remediation', 'label': 'Remediation Action', 'selected': False},
                ]
            },
            'incidents': {
                'name': 'Incident Summary Report',
                'description': 'Incident tracking, types, and resolutions across homes',
                'fields': [
                    {'id': 'date', 'label': 'Date', 'selected': True},
                    {'id': 'care_home', 'label': 'Care Home', 'selected': True},
                    {'id': 'unit', 'label': 'Unit', 'selected': True},
                    {'id': 'incident_type', 'label': 'Incident Type', 'selected': True},
                    {'id': 'severity', 'label': 'Severity', 'selected': True},
                    {'id': 'reported_by', 'label': 'Reported By', 'selected': False},
                    {'id': 'resolution_status', 'label': 'Resolution Status', 'selected': False},
                    {'id': 'follow_up_required', 'label': 'Follow-up Required', 'selected': False},
                ]
            },
            'comparative_analytics': {
                'name': 'Comparative Analytics Report',
                'description': 'Cross-home performance comparison and benchmarking',
                'fields': [
                    {'id': 'care_home', 'label': 'Care Home', 'selected': True},
                    {'id': 'avg_daily_staff', 'label': 'Average Daily Staff', 'selected': True},
                    {'id': 'fill_rate', 'label': 'Shift Fill Rate (%)', 'selected': True},
                    {'id': 'agency_usage_rate', 'label': 'Agency Usage Rate (%)', 'selected': True},
                    {'id': 'overtime_rate', 'label': 'Overtime Rate (%)', 'selected': True},
                    {'id': 'sickness_rate', 'label': 'Sickness Absence Rate (%)', 'selected': True},
                    {'id': 'leave_approval_rate', 'label': 'Leave Approval Rate (%)', 'selected': False},
                    {'id': 'budget_variance', 'label': 'Budget Variance (%)', 'selected': False},
                ]
            }
        }
        
        context = {
            'report_types': json.dumps(report_types),
            'report_types_dict': report_types,  # Keep dict for iteration
            'today': today,
            'all_care_homes': CareHome.objects.all().order_by('name'),
        }
        
        return render(request, 'scheduling/custom_report_builder.html', context)
    
    elif request.method == 'POST':
        # Generate and export report
        report_type = request.POST.get('report_type')
        export_format = request.POST.get('export_format', 'csv')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        selected_homes = request.POST.getlist('care_homes')
        selected_fields = request.POST.getlist('fields')
        
        # Parse dates
        from django.utils.dateparse import parse_date
        start_date = parse_date(start_date_str) if start_date_str else timezone.now().date()
        end_date = parse_date(end_date_str) if end_date_str else timezone.now().date()
        
        # Generate report data based on type
        report_data = _generate_report_data(report_type, start_date, end_date, selected_homes, selected_fields)
        
        # Export in requested format
        if export_format == 'csv':
            return _export_csv(report_type, report_data, start_date, end_date)
        elif export_format == 'excel':
            return _export_excel(report_type, report_data, start_date, end_date)
        elif export_format == 'pdf':
            return _export_pdf(report_type, report_data, start_date, end_date)
        else:
            return HttpResponse('Invalid export format', status=400)


def _generate_report_data(report_type, start_date, end_date, selected_homes, selected_fields):
    """Generate report data based on report type and parameters"""
    from django.db.models import Count, Avg, Sum, F, Q
    
    data = []
    
    # Filter homes
    if selected_homes:
        care_homes = CareHome.objects.filter(name__in=selected_homes)
    else:
        care_homes = CareHome.objects.all()
    
    if report_type == 'staffing_coverage':
        # Staffing coverage analysis - aggregated by home for high-level reporting
        for home in care_homes:
            units = Unit.objects.filter(care_home=home, is_active=True)
            
            # Get all shifts for this home across all units
            shifts = Shift.objects.filter(
                unit__care_home=home,
                unit__is_active=True,
                date__gte=start_date,
                date__lte=end_date
            ).select_related('shift_type', 'user', 'user__role')
            
            # Group by date and shift type
            current_date = start_date
            while current_date <= end_date:
                # Day shifts across all units in this home
                day_shifts = shifts.filter(
                    date=current_date,
                    shift_type__name__in=['DAY', 'DAY_SENIOR', 'DAY_ASSISTANT']
                )
                day_count = day_shifts.count()
                day_sscw = day_shifts.filter(user__role__name='SSCW').count()
                
                # Night shifts across all units in this home
                night_shifts = shifts.filter(
                    date=current_date,
                    shift_type__name__in=['NIGHT', 'NIGHT_SENIOR', 'NIGHT_ASSISTANT']
                )
                night_count = night_shifts.count()
                night_sscw = night_shifts.filter(user__role__name='SSCWN').count()
                
                # Calculate required staff as sum across all units
                day_required = sum(unit.min_day_staff for unit in units)
                night_required = sum(unit.min_night_staff for unit in units)
                
                if 'shift_type' in selected_fields:
                    # Separate rows for day and night
                    data.append({
                        'date': current_date,
                        'care_home': home.get_name_display(),
                        'shift_type': 'Day',
                        'scheduled_staff': day_count,
                        'required_staff': day_required,
                        'shortage': day_required - day_count,
                        'sscw_count': day_sscw,
                    })
                    
                    data.append({
                        'date': current_date,
                        'care_home': home.get_name_display(),
                        'shift_type': 'Night',
                        'scheduled_staff': night_count,
                        'required_staff': night_required,
                        'shortage': night_required - night_count,
                        'sscw_count': night_sscw,
                    })
                
                current_date += timedelta(days=1)
    
    elif report_type == 'leave_usage':
        # Leave usage analysis
        leave_requests = LeaveRequest.objects.filter(
            start_date__lte=end_date,
            end_date__gte=start_date,
            user__unit__care_home__in=care_homes
        ).select_related('user', 'user__unit', 'user__unit__care_home', 'user__role')
        
        for leave in leave_requests:
            data.append({
                'staff_name': leave.user.full_name,
                'staff_sap': leave.user.sap,
                'care_home': leave.user.unit.care_home.get_name_display() if leave.user.unit and leave.user.unit.care_home else 'N/A',
                'leave_type': leave.get_leave_type_display(),
                'start_date': leave.start_date,
                'end_date': leave.end_date,
                'days_requested': leave.days_requested,
                'status': leave.get_status_display(),
                'unit': leave.user.unit.get_name_display() if leave.user.unit else 'N/A',
                'role': leave.user.role.get_name_display() if leave.user.role else 'N/A',
            })
    
    elif report_type == 'comparative_analytics':
        # Cross-home comparison
        for home in care_homes:
            shifts = Shift.objects.filter(
                unit__care_home=home,
                date__gte=start_date,
                date__lte=end_date
            )
            
            total_shifts = shifts.count()
            total_days = (end_date - start_date).days + 1
            avg_daily_staff = total_shifts / total_days if total_days > 0 else 0
            
            # Calculate fill rate
            unfilled_shifts = shifts.filter(user__isnull=True).count()
            fill_rate = ((total_shifts - unfilled_shifts) / total_shifts * 100) if total_shifts > 0 else 0
            
            data.append({
                'care_home': home.get_name_display(),
                'avg_daily_staff': round(avg_daily_staff, 1),
                'fill_rate': round(fill_rate, 1),
                'agency_usage_rate': 0,  # Placeholder
                'overtime_rate': 0,  # Placeholder
                'sickness_rate': 0,  # Placeholder
            })
    
    return data


def _export_csv(report_type, report_data, start_date, end_date):
    """Export report data as CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_{start_date}_{end_date}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([f'{report_type.replace("_", " ").title()} Report'])
    writer.writerow([f'Period: {start_date} to {end_date}'])
    writer.writerow([f'Generated: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'])
    writer.writerow([])
    
    # Write column headers
    if report_data:
        writer.writerow(report_data[0].keys())
        
        # Write data rows
        for row in report_data:
            writer.writerow(row.values())
    
    return response


def _export_excel(report_type, report_data, start_date, end_date):
    """Export report data as Excel with formatting"""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, PatternFill
        from openpyxl.utils import get_column_letter
        from django.http import HttpResponse
        import io
        
        wb = Workbook()
        ws = wb.active
        ws.title = report_type[:31]  # Excel sheet name limit
        
        # Header
        ws['A1'] = f'{report_type.replace("_", " ").title()} Report'
        ws['A1'].font = Font(size=16, bold=True)
        ws['A2'] = f'Period: {start_date} to {end_date}'
        ws['A3'] = f'Generated: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'
        
        # Data header (row 5)
        if report_data:
            headers = list(report_data[0].keys())
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=5, column=col_num, value=header.replace('_', ' ').title())
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
                cell.font = Font(color='FFFFFF', bold=True)
                cell.alignment = Alignment(horizontal='center')
            
            # Data rows
            for row_num, row_data in enumerate(report_data, 6):
                for col_num, value in enumerate(row_data.values(), 1):
                    ws.cell(row=row_num, column=col_num, value=value)
            
            # Auto-adjust column widths
            for col_num in range(1, len(headers) + 1):
                ws.column_dimensions[get_column_letter(col_num)].width = 15
        
        # Save to bytes
        excel_file = io.BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)
        
        response = HttpResponse(
            excel_file.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{report_type}_{start_date}_{end_date}.xlsx"'
        
        return response
        
    except ImportError:
        # openpyxl not installed, fall back to CSV
        return _export_csv(report_type, report_data, start_date, end_date)


def _export_pdf(report_type, report_data, start_date, end_date):
    """Export report data as PDF"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from django.http import HttpResponse
        import io
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30,
        )
        
        title = Paragraph(f'{report_type.replace("_", " ").title()} Report', title_style)
        elements.append(title)
        
        # Metadata
        meta_style = styles['Normal']
        elements.append(Paragraph(f'<b>Period:</b> {start_date} to {end_date}', meta_style))
        elements.append(Paragraph(f'<b>Generated:</b> {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}', meta_style))
        elements.append(Spacer(1, 0.5*inch))
        
        # Data table
        if report_data:
            # Prepare table data
            headers = [[h.replace('_', ' ').title() for h in report_data[0].keys()]]
            data_rows = [[str(v) for v in row.values()] for row in report_data]
            table_data = headers + data_rows
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(table)
        
        # Build PDF
        doc.build(elements)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_{start_date}_{end_date}.pdf"'
        response.write(pdf_data)
        
        return response
        
    except ImportError:
        # reportlab not installed, fall back to CSV
        return _export_csv(report_type, report_data, start_date, end_date)

