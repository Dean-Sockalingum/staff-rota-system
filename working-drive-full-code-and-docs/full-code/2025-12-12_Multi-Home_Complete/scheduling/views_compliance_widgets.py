"""
Compliance Widget Views - Task 56
Views for rendering and managing compliance dashboard widgets
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count, Avg, F
from datetime import date, timedelta, datetime
from decimal import Decimal
import json

from scheduling.models import (
    ComplianceMetric, ComplianceWidget, CareHome, Unit, User,
    TrainingRecord, TrainingCourse, SupervisionRecord,
    InductionProgress, IncidentReport, Shift
)


# ============================================================================
# COMPLIANCE METRIC CALCULATION
# ============================================================================

def calculate_training_compliance(care_home=None, unit=None):
    """
    Calculate training compliance metrics.
    Returns: ComplianceMetric object or dict of metric data
    """
    # Get staff queryset
    staff = User.objects.filter(is_active=True, profile__isnull=False)
    if care_home:
        staff = staff.filter(profile__care_home=care_home)
    if unit:
        staff = staff.filter(profile__units=unit)
    
    total_staff = staff.count()
    if total_staff == 0:
        return None
    
    # Get mandatory courses
    mandatory_courses = TrainingCourse.objects.filter(
        is_mandatory=True,
        is_active=True
    )
    
    total_required = total_staff * mandatory_courses.count()
    
    # Count completed training (not expired)
    today = date.today()
    compliant_records = TrainingRecord.objects.filter(
        user__in=staff,
        course__in=mandatory_courses,
        status='COMPLETED',
        expiry_date__gte=today
    ).count()
    
    # Count expiring soon (within 30 days)
    at_risk_records = TrainingRecord.objects.filter(
        user__in=staff,
        course__in=mandatory_courses,
        status='COMPLETED',
        expiry_date__lt=today + timedelta(days=30),
        expiry_date__gte=today
    ).count()
    
    # Count expired
    non_compliant_records = TrainingRecord.objects.filter(
        user__in=staff,
        course__in=mandatory_courses
    ).filter(
        Q(status='EXPIRED') | Q(expiry_date__lt=today)
    ).count()
    
    # Calculate percentage
    current_value = (compliant_records / total_required * 100) if total_required > 0 else 0
    
    # Get previous value (from 30 days ago)
    try:
        previous_metric = ComplianceMetric.objects.filter(
            care_home=care_home,
            unit=unit,
            category='training',
            calculation_date__lt=timezone.now() - timedelta(days=30)
        ).order_by('-calculation_date').first()
        previous_value = previous_metric.current_value if previous_metric else None
    except:
        previous_value = None
    
    # Build notes
    notes_list = []
    if at_risk_records > 0:
        notes_list.append(f"{at_risk_records} certifications expire within 30 days")
    if non_compliant_records > 0:
        notes_list.append(f"{non_compliant_records} expired certifications need renewal")
    
    return {
        'care_home': care_home,
        'unit': unit,
        'category': 'training',
        'metric_name': 'Mandatory Training Compliance',
        'current_value': Decimal(str(round(current_value, 2))),
        'target_value': Decimal('95.00'),
        'compliant_count': compliant_records,
        'at_risk_count': at_risk_records,
        'non_compliant_count': non_compliant_records,
        'total_count': total_required,
        'previous_value': previous_value,
        'period_start': today - timedelta(days=90),
        'period_end': today,
        'notes': '; '.join(notes_list) if notes_list else '',
        'ci_relevant': True,
        'ci_theme': 'staff_team',
    }


def calculate_supervision_compliance(care_home=None, unit=None):
    """Calculate supervision compliance (required quarterly for care staff)"""
    # Get care staff only
    staff = User.objects.filter(
        is_active=True,
        profile__isnull=False,
        profile__role__name__in=['Senior Carer', 'Carer', 'Night Carer']
    )
    if care_home:
        staff = staff.filter(profile__care_home=care_home)
    if unit:
        staff = staff.filter(profile__units=unit)
    
    total_staff = staff.count()
    if total_staff == 0:
        return None
    
    # Supervision required every 90 days
    cutoff_date = date.today() - timedelta(days=90)
    
    compliant_count = 0
    at_risk_count = 0
    non_compliant_count = 0
    
    for member in staff:
        last_supervision = SupervisionRecord.objects.filter(
            user=member,
            status='COMPLETED'
        ).order_by('-supervision_date').first()
        
        if last_supervision:
            days_since = (date.today() - last_supervision.supervision_date).days
            if days_since <= 90:
                compliant_count += 1
            elif days_since <= 105:  # 15-day grace period
                at_risk_count += 1
            else:
                non_compliant_count += 1
        else:
            non_compliant_count += 1
    
    current_value = (compliant_count / total_staff * 100) if total_staff > 0 else 0
    
    # Get previous value
    try:
        previous_metric = ComplianceMetric.objects.filter(
            care_home=care_home,
            unit=unit,
            category='supervision',
            calculation_date__lt=timezone.now() - timedelta(days=30)
        ).order_by('-calculation_date').first()
        previous_value = previous_metric.current_value if previous_metric else None
    except:
        previous_value = None
    
    notes_list = []
    if at_risk_count > 0:
        notes_list.append(f"{at_risk_count} staff due for supervision within 15 days")
    if non_compliant_count > 0:
        notes_list.append(f"{non_compliant_count} staff overdue for supervision")
    
    return {
        'care_home': care_home,
        'unit': unit,
        'category': 'supervision',
        'metric_name': 'Supervision Compliance (Quarterly)',
        'current_value': Decimal(str(round(current_value, 2))),
        'target_value': Decimal('90.00'),
        'compliant_count': compliant_count,
        'at_risk_count': at_risk_count,
        'non_compliant_count': non_compliant_count,
        'total_count': total_staff,
        'previous_value': previous_value,
        'period_start': cutoff_date,
        'period_end': date.today(),
        'notes': '; '.join(notes_list) if notes_list else '',
        'ci_relevant': True,
        'ci_theme': 'staff_team',
    }


def calculate_wtd_compliance(care_home=None, unit=None):
    """Calculate Working Time Directive compliance (48-hour average over 17 weeks)"""
    # Get all staff
    staff = User.objects.filter(is_active=True, profile__isnull=False)
    if care_home:
        staff = staff.filter(profile__care_home=care_home)
    if unit:
        staff = staff.filter(profile__units=unit)
    
    total_staff = staff.count()
    if total_staff == 0:
        return None
    
    # Check last 17 weeks (119 days)
    start_date = date.today() - timedelta(days=119)
    
    compliant_count = 0
    at_risk_count = 0
    non_compliant_count = 0
    
    for member in staff:
        shifts = Shift.objects.filter(
            user=member,
            date__gte=start_date,
            date__lte=date.today()
        )
        
        total_hours = sum([
            (shift.end_time.hour - shift.start_time.hour) 
            for shift in shifts 
            if shift.end_time and shift.start_time
        ])
        
        weekly_average = total_hours / 17 if total_hours > 0 else 0
        
        if weekly_average <= 48:
            compliant_count += 1
        elif weekly_average <= 52:  # Within 4 hours of limit
            at_risk_count += 1
        else:
            non_compliant_count += 1
    
    current_value = (compliant_count / total_staff * 100) if total_staff > 0 else 0
    
    # Get previous value
    try:
        previous_metric = ComplianceMetric.objects.filter(
            care_home=care_home,
            unit=unit,
            category='wtd',
            calculation_date__lt=timezone.now() - timedelta(days=30)
        ).order_by('-calculation_date').first()
        previous_value = previous_metric.current_value if previous_metric else None
    except:
        previous_value = None
    
    notes_list = []
    if at_risk_count > 0:
        notes_list.append(f"{at_risk_count} staff approaching 48-hour average")
    if non_compliant_count > 0:
        notes_list.append(f"{non_compliant_count} staff exceeding WTD limits")
    
    return {
        'care_home': care_home,
        'unit': unit,
        'category': 'wtd',
        'metric_name': 'Working Time Directive Compliance',
        'current_value': Decimal(str(round(current_value, 2))),
        'target_value': Decimal('100.00'),
        'compliant_count': compliant_count,
        'at_risk_count': at_risk_count,
        'non_compliant_count': non_compliant_count,
        'total_count': total_staff,
        'previous_value': previous_value,
        'period_start': start_date,
        'period_end': date.today(),
        'notes': '; '.join(notes_list) if notes_list else '',
        'ci_relevant': True,
        'ci_theme': 'staff_team',
    }


def calculate_induction_compliance(care_home=None, unit=None):
    """Calculate induction completion rates for new staff"""
    # Get staff with active inductions (started within last 90 days)
    cutoff_date = date.today() - timedelta(days=90)
    
    inductions = InductionProgress.objects.filter(
        start_date__gte=cutoff_date,
        user__is_active=True
    )
    
    if care_home:
        inductions = inductions.filter(user__profile__care_home=care_home)
    if unit:
        inductions = inductions.filter(user__profile__units=unit)
    
    total_count = inductions.count()
    if total_count == 0:
        return None
    
    compliant_count = inductions.filter(completion_date__isnull=False).count()
    at_risk_count = inductions.filter(
        completion_date__isnull=True,
        start_date__lte=date.today() - timedelta(days=60)  # Over 60 days without completion
    ).count()
    non_compliant_count = total_count - compliant_count - at_risk_count
    
    current_value = (compliant_count / total_count * 100) if total_count > 0 else 0
    
    # Get previous value
    try:
        previous_metric = ComplianceMetric.objects.filter(
            care_home=care_home,
            unit=unit,
            category='induction',
            calculation_date__lt=timezone.now() - timedelta(days=30)
        ).order_by('-calculation_date').first()
        previous_value = previous_metric.current_value if previous_metric else None
    except:
        previous_value = None
    
    notes_list = []
    if at_risk_count > 0:
        notes_list.append(f"{at_risk_count} inductions in progress over 60 days")
    if non_compliant_count > 0:
        notes_list.append(f"{non_compliant_count} inductions not yet completed")
    
    return {
        'care_home': care_home,
        'unit': unit,
        'category': 'induction',
        'metric_name': 'Induction Completion Rate',
        'current_value': Decimal(str(round(current_value, 2))),
        'target_value': Decimal('95.00'),
        'compliant_count': compliant_count,
        'at_risk_count': at_risk_count,
        'non_compliant_count': non_compliant_count,
        'total_count': total_count,
        'previous_value': previous_value,
        'period_start': cutoff_date,
        'period_end': date.today(),
        'notes': '; '.join(notes_list) if notes_list else '',
        'ci_relevant': True,
        'ci_theme': 'staff_team',
    }


@login_required
def refresh_compliance_metrics(request, care_home_id=None):
    """
    Refresh all compliance metrics for a care home.
    Can be called manually or via AJAX.
    """
    if care_home_id:
        care_home = get_object_or_404(CareHome, id=care_home_id)
    else:
        care_home = None
    
    # Calculate all metrics
    metrics_data = [
        calculate_training_compliance(care_home),
        calculate_supervision_compliance(care_home),
        calculate_wtd_compliance(care_home),
        calculate_induction_compliance(care_home),
    ]
    
    # Save metrics to database
    created_count = 0
    for data in metrics_data:
        if data:
            metric, created = ComplianceMetric.objects.update_or_create(
                care_home=data['care_home'],
                unit=data.get('unit'),
                category=data['category'],
                period_start=data['period_start'],
                period_end=data['period_end'],
                defaults=data
            )
            if created:
                created_count += 1
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Refreshed {len(metrics_data)} compliance metrics',
            'created_count': created_count
        })
    
    messages.success(request, f'Refreshed {len(metrics_data)} compliance metrics')
    return redirect('compliance_dashboard')


# ============================================================================
# WIDGET DISPLAY VIEWS
# ============================================================================

@login_required
def compliance_dashboard(request):
    """Main compliance dashboard with all active widgets"""
    user_home = None
    if hasattr(request.user, 'profile') and request.user.profile.care_home:
        user_home = request.user.profile.care_home
    
    # Get widgets for this user
    widgets = ComplianceWidget.objects.filter(
        is_active=True
    ).filter(
        Q(is_public=True) | Q(created_by=request.user)
    )
    
    # Filter by user's home if applicable
    if user_home and not request.user.is_manager:
        widgets = widgets.filter(Q(care_home=user_home) | Q(care_home__isnull=True))
    
    widgets = widgets.order_by('display_order', 'name')
    
    context = {
        'widgets': widgets,
        'user_home': user_home,
        'can_manage': request.user.is_manager or request.user.is_staff,
    }
    
    return render(request, 'scheduling/compliance_dashboard.html', context)


@login_required
def widget_data_api(request, widget_id):
    """
    AJAX endpoint to get widget data (for auto-refresh).
    Returns JSON with metrics for the specified widget.
    """
    widget = get_object_or_404(ComplianceWidget, id=widget_id, is_active=True)
    
    # Check permissions
    if not widget.is_public and widget.created_by != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get metrics for this widget
    metrics = widget.get_metrics()
    
    # Serialize metrics
    metrics_data = []
    for metric in metrics[:10]:  # Limit to 10 metrics per widget
        metrics_data.append({
            'id': metric.id,
            'metric_name': metric.metric_name,
            'current_value': float(metric.current_value),
            'target_value': float(metric.target_value),
            'status': metric.status,
            'status_color': metric.get_status_color(),
            'status_icon': metric.get_status_icon(),
            'compliant_count': metric.compliant_count,
            'at_risk_count': metric.at_risk_count,
            'non_compliant_count': metric.non_compliant_count,
            'total_count': metric.total_count,
            'trend_direction': metric.trend_direction,
            'trend_icon': metric.get_trend_icon(),
            'notes': metric.notes,
            'calculation_date': metric.calculation_date.isoformat(),
            'ci_theme': metric.get_ci_theme_display() if metric.ci_theme else '',
        })
    
    return JsonResponse({
        'widget_id': widget.id,
        'widget_name': widget.name,
        'widget_type': widget.widget_type,
        'metrics': metrics_data,
        'last_updated': timezone.now().isoformat(),
        'needs_refresh': widget.needs_refresh(),
    })


@login_required
@user_passes_test(lambda u: u.is_manager or u.is_staff)
def manage_widgets(request):
    """Manage compliance widgets (create, edit, delete)"""
    widgets = ComplianceWidget.objects.filter(
        created_by=request.user
    ).order_by('display_order', 'name')
    
    context = {
        'widgets': widgets,
    }
    
    return render(request, 'scheduling/manage_compliance_widgets.html', context)


@login_required
@user_passes_test(lambda u: u.is_manager or u.is_staff)
def create_widget(request):
    """Create a new compliance widget"""
    if request.method == 'POST':
        # Get form data
        widget = ComplianceWidget.objects.create(
            name=request.POST.get('name'),
            widget_type=request.POST.get('widget_type'),
            title=request.POST.get('title'),
            size=request.POST.get('size', 'medium'),
            category_filter=request.POST.get('category_filter', ''),
            show_trend=request.POST.get('show_trend') == 'on',
            show_counts=request.POST.get('show_counts') == 'on',
            show_ci_theme=request.POST.get('show_ci_theme') == 'on',
            auto_refresh=request.POST.get('auto_refresh') == 'on',
            refresh_interval=int(request.POST.get('refresh_interval', 300)),
            is_public=request.POST.get('is_public') == 'on',
            created_by=request.user,
        )
        
        # Set care_home if provided
        if request.POST.get('care_home_id'):
            widget.care_home_id = request.POST.get('care_home_id')
            widget.save()
        
        messages.success(request, f'Widget "{widget.name}" created successfully')
        return redirect('manage_compliance_widgets')
    
    # GET request - show form
    care_homes = CareHome.objects.filter(is_active=True)
    
    context = {
        'care_homes': care_homes,
        'widget_types': ComplianceWidget.WIDGET_TYPE_CHOICES,
        'size_choices': ComplianceWidget.SIZE_CHOICES,
        'category_choices': ComplianceMetric.CATEGORY_CHOICES,
    }
    
    return render(request, 'scheduling/create_compliance_widget.html', context)


@login_required
@user_passes_test(lambda u: u.is_manager or u.is_staff)
def delete_widget(request, widget_id):
    """Delete a compliance widget"""
    widget = get_object_or_404(ComplianceWidget, id=widget_id, created_by=request.user)
    
    if request.method == 'POST':
        widget_name = widget.name
        widget.delete()
        messages.success(request, f'Widget "{widget_name}" deleted')
        return redirect('manage_compliance_widgets')
    
    return render(request, 'scheduling/delete_compliance_widget.html', {'widget': widget})


@login_required
def compliance_report(request):
    """Generate comprehensive compliance report for Care Inspectorate"""
    user_home = None
    if hasattr(request.user, 'profile') and request.user.profile.care_home:
        user_home = request.user.profile.care_home
    
    # Get latest metrics for user's home
    metrics = ComplianceMetric.objects.filter(care_home=user_home).order_by(
        'category', '-calculation_date'
    ).distinct('category')
    
    # Calculate overall compliance score
    if metrics.exists():
        overall_score = metrics.aggregate(Avg('current_value'))['current_value__avg']
    else:
        overall_score = 0
    
    # Get red flags (non-compliant metrics)
    red_flags = metrics.filter(status='red')
    
    context = {
        'user_home': user_home,
        'metrics': metrics,
        'overall_score': round(overall_score, 1) if overall_score else 0,
        'red_flags': red_flags,
        'report_date': date.today(),
    }
    
    return render(request, 'scheduling/compliance_report.html', context)
