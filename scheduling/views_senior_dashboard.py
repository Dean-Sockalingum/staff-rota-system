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
from django.db.models import Count, Sum, Avg, Q, F
from django.http import HttpResponse
from datetime import datetime, timedelta
from decimal import Decimal
import csv

from .models import Shift, Unit, User, LeaveRequest, StaffReallocation
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
    
    # Get all care homes
    care_homes = CareHome.objects.all().order_by('name')
    
    # =================================================================
    # SECTION 1: HOME OVERVIEW - Occupancy & Capacity
    # =================================================================
    home_overview = []
    total_capacity = 0
    total_occupancy = 0
    
    for home in care_homes:
        units = Unit.objects.filter(care_home=home, is_active=True)
        unit_count = units.count()
        
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
    
    # Home-specific staffing requirements (must match citywide summary)
    home_staffing = {
        'HAWTHORN_HOUSE': {'day_min': 18, 'day_ideal': 24, 'night_min': 18, 'night_ideal': 21},
        'MEADOWBURN': {'day_min': 17, 'day_ideal': 24, 'night_min': 17, 'night_ideal': 21},
        'ORCHARD_GROVE': {'day_min': 17, 'day_ideal': 24, 'night_min': 17, 'night_ideal': 21},
        'RIVERSIDE': {'day_min': 17, 'day_ideal': 24, 'night_min': 17, 'night_ideal': 21},
        'VICTORIA_GARDENS': {'day_min': 10, 'day_ideal': 15, 'night_min': 10, 'night_ideal': 12},
    }
    
    for home in care_homes:
        units = Unit.objects.filter(care_home=home, is_active=True)
        
        # Shifts for this home in date range
        range_shifts = Shift.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            unit__in=units,
            status__in=['SCHEDULED', 'CONFIRMED']
        )
        
        # Count by shift type
        day_shifts = range_shifts.filter(shift_type__name__icontains='DAY').count()
        night_shifts = range_shifts.filter(shift_type__name__icontains='NIGHT').count()
        
        # Get home-specific requirements
        requirements = home_staffing.get(home.name, {'day_min': 17, 'day_ideal': 24, 'night_min': 17, 'night_ideal': 21})
        
        # Calculate required vs actual (per day in range) using correct minimums
        total_required_day = requirements['day_min'] * days_in_range
        total_required_night = requirements['night_min'] * days_in_range
        
        day_coverage = (day_shifts / total_required_day * 100) if total_required_day > 0 else 100
        night_coverage = (night_shifts / total_required_night * 100) if total_required_night > 0 else 100
        
        staffing_today.append({
            'home': home.get_name_display(),
            'day_actual': day_shifts,
            'day_required': total_required_day,
            'day_coverage': day_coverage,
            'night_actual': night_shifts,
            'night_required': total_required_night,
            'night_coverage': night_coverage,
            'status': 'good' if day_coverage >= 100 and night_coverage >= 100 else 'warning' if day_coverage >= 80 and night_coverage >= 80 else 'critical',
        })
    
    # =================================================================
    # SECTION 3: FISCAL MONITORING - Monthly Budget Tracking
    # =================================================================
    fiscal_summary = []
    total_agency_budget = 0
    total_agency_spend = 0
    total_ot_budget = 0
    total_ot_spend = 0
    
    for home in care_homes:
        units = Unit.objects.filter(care_home=home)
        
        # Agency spend for date range
        # TODO: Integrate with AgencyBooking model when ready
        # For now, estimate based on agency shifts
        agency_shifts_count = Shift.objects.filter(
            unit__in=units,
            date__gte=start_date,
            date__lte=end_date,
            user__isnull=True,  # Placeholder for agency detection
            status__in=['SCHEDULED', 'CONFIRMED']
        ).count()
        # Estimate: £300 per agency shift (rough average)
        agency_spend = Decimal(str(agency_shifts_count * 300))
        
        # OT spend for date range (estimated at £25/hour, 12 hours per shift)
        ot_shifts = Shift.objects.filter(
            unit__in=units,
            date__gte=start_date,
            date__lte=end_date,
            shift_classification='OVERTIME'
        ).count()
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
    for home in care_homes:
        units = Unit.objects.filter(care_home=home)
        
        # Unfilled shifts in the next 7 days as alerts
        unfilled = Shift.objects.filter(
            unit__in=units,
            date__gte=today,
            date__lte=next_week,
            user__isnull=True,
            status='SCHEDULED'
        ).select_related('unit')[:5]  # Top 5 per home
        
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
    
    for home in care_homes:
        units = Unit.objects.filter(care_home=home)
        
        # Last 30 days metrics
        last_30_days = today - timedelta(days=30)
        
        # Agency usage rate
        # TODO: Integrate with AgencyBooking when ready
        total_shifts = Shift.objects.filter(
            unit__in=units,
            date__gte=last_30_days,
            date__lte=today
        ).count()
        
        # For now, estimate agency as unfilled shifts
        unfilled_shifts = Shift.objects.filter(
            unit__in=units,
            date__gte=last_30_days,
            date__lte=today,
            user__isnull=True
        ).count()
        
        agency_rate = (unfilled_shifts / total_shifts * 100) if total_shifts > 0 else 0
        
        # Staff turnover (placeholder - would need actual termination data)
        staff_count = User.objects.filter(unit__in=units, is_active=True).count()
        
        quality_metrics.append({
            'home': home.get_name_display(),
            'agency_rate': agency_rate,
            'staff_count': staff_count,
            'shifts_30d': total_shifts,
            'quality_score': 100 - agency_rate,  # Simple inverse for now
        })
    
    # =================================================================
    # SECTION 7: CITYWIDE SUMMARY - Weekly Overview
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
            
            # Debug output
            if date.day == 15:
                print(f"DEBUG {home.name} Dec 15: day_seniors={day_seniors}, day_staff={day_staff}, total_day_shifts={day_shifts_for_date.count()}")
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
        
        # Citywide Summary
        'citywide_day_summary': citywide_day_summary,
        'citywide_night_summary': citywide_night_summary,
        'week_dates': week_dates,
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
