"""
Care Inspectorate Compliance Views
Web forms for staff to complete training, induction, supervision, and incident reports
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
from datetime import date, timedelta
from decimal import Decimal

from scheduling.models import (
    TrainingCourse, TrainingRecord, InductionProgress, 
    SupervisionRecord, IncidentReport, User, CareHome, Unit
)


# ============================================================================
# TRAINING MANAGEMENT
# ============================================================================

@login_required
def my_training_dashboard(request):
    """Staff member's personal training dashboard"""
    
    # Get all training records for current user
    training_records = TrainingRecord.objects.filter(
        staff_member=request.user
    ).select_related('course').order_by('-completion_date')
    
    # Calculate training statistics
    total_training = training_records.count()
    current_training = sum(1 for r in training_records if r.get_status() == 'CURRENT')
    expiring_soon = sum(1 for r in training_records if r.get_status() == 'EXPIRING_SOON')
    expired_training = sum(1 for r in training_records if r.get_status() == 'EXPIRED')
    
    # SSSC CPD hours
    current_year = timezone.now().year
    sssc_cpd_hours = training_records.filter(
        completion_date__year=current_year,
        sssc_cpd_hours_claimed__isnull=False
    ).aggregate(total=Sum('sssc_cpd_hours_claimed'))['total'] or Decimal('0.00')
    
    # Mandatory training compliance
    mandatory_courses = TrainingCourse.objects.filter(is_mandatory=True)
    mandatory_completed = []
    mandatory_missing = []
    
    for course in mandatory_courses:
        latest_record = training_records.filter(course=course).first()
        if latest_record and latest_record.get_status() == 'CURRENT':
            mandatory_completed.append({
                'course': course,
                'record': latest_record,
                'days_until_expiry': latest_record.days_until_expiry()
            })
        else:
            mandatory_missing.append(course)
    
    context = {
        'training_records': training_records,
        'total_training': total_training,
        'current_training': current_training,
        'expiring_soon': expiring_soon,
        'expired_training': expired_training,
        'sssc_cpd_hours': sssc_cpd_hours,
        'sssc_target': Decimal('35.00'),
        'mandatory_completed': mandatory_completed,
        'mandatory_missing': mandatory_missing,
    }
    
    return render(request, 'compliance/my_training_dashboard.html', context)


@login_required
def training_compliance_dashboard(request):
    """Management view of training compliance across all homes"""
    
    # Get filters
    selected_home = request.GET.get('care_home', None)
    
    # Get mandatory courses
    mandatory_courses = TrainingCourse.objects.filter(is_mandatory=True).order_by('name')
    
    # Get care homes
    care_homes = CareHome.objects.filter(is_active=True).order_by('name')
    
    # Build compliance data by home
    home_compliance_data = []
    
    for home in care_homes:
        # Filter if specific home selected
        if selected_home and home.name != selected_home:
            continue
            
        # Get active staff for this home
        home_staff = User.objects.filter(
            unit__care_home=home,
            is_active=True
        ).distinct()
        
        total_staff = home_staff.count()
        
        # Calculate compliance for each mandatory course
        course_compliance = []
        for course in mandatory_courses:
            compliant_count = 0
            expiring_count = 0
            expired_count = 0
            missing_count = 0
            
            compliant_staff = []
            expiring_staff = []
            expired_staff = []
            missing_staff = []
            
            for staff in home_staff:
                # Get latest training record for this course
                latest_record = TrainingRecord.objects.filter(
                    staff_member=staff,
                    course=course
                ).order_by('-completion_date').first()
                
                if latest_record:
                    status = latest_record.get_status()
                    if status == 'CURRENT':
                        compliant_count += 1
                        compliant_staff.append({'staff': staff, 'record': latest_record})
                    elif status == 'EXPIRING_SOON':
                        expiring_count += 1
                        expiring_staff.append({'staff': staff, 'record': latest_record})
                    elif status == 'EXPIRED':
                        expired_count += 1
                        expired_staff.append({
                            'staff': staff, 
                            'record': latest_record,
                            'days_overdue': abs(latest_record.days_until_expiry)
                        })
                else:
                    missing_count += 1
                    missing_staff.append(staff)
            
            compliance_percentage = (compliant_count / total_staff * 100) if total_staff > 0 else 0
            
            course_compliance.append({
                'course': course,
                'compliant': compliant_count,
                'expiring': expiring_count,
                'expired': expired_count,
                'missing': missing_count,
                'total': total_staff,
                'percentage': round(compliance_percentage, 1),
                'compliant_staff': compliant_staff,
                'expiring_staff': expiring_staff,
                'expired_staff': expired_staff,
                'missing_staff': missing_staff,
            })
        
        # Calculate overall home compliance
        total_required = total_staff * mandatory_courses.count()
        total_compliant = sum(c['compliant'] for c in course_compliance)
        overall_percentage = (total_compliant / total_required * 100) if total_required > 0 else 0
        
        home_compliance_data.append({
            'home': home,
            'total_staff': total_staff,
            'course_compliance': course_compliance,
            'overall_percentage': round(overall_percentage, 1),
            'total_compliant': total_compliant,
            'total_required': total_required
        })
    
    context = {
        'home_compliance_data': home_compliance_data,
        'mandatory_courses': mandatory_courses,
        'care_homes': care_homes,
        'selected_home': selected_home,
    }
    
    return render(request, 'compliance/training_compliance_dashboard.html', context)


@login_required
def add_staff_training_record(request):
    """Manager adds training record for a staff member"""
    
    if request.method == 'POST':
        staff_id = request.POST.get('staff_member')
        course_id = request.POST.get('course')
        completion_date = request.POST.get('completion_date')
        trainer_name = request.POST.get('trainer_name', '')
        training_provider = request.POST.get('training_provider', '')
        certificate_number = request.POST.get('certificate_number', '')
        sssc_cpd_hours = request.POST.get('sssc_cpd_hours', None)
        notes = request.POST.get('notes', '')
        
        try:
            staff_member = User.objects.get(id=staff_id)
            course = TrainingCourse.objects.get(id=course_id)
            completion_date_obj = date.fromisoformat(completion_date)
            
            # Calculate expiry date based on course validity
            expiry_date = completion_date_obj + timedelta(days=course.validity_months * 30)
            
            # Create training record
            record = TrainingRecord.objects.create(
                staff_member=staff_member,
                course=course,
                completion_date=completion_date_obj,
                expiry_date=expiry_date,
                trainer_name=trainer_name,
                training_provider=training_provider,
                certificate_number=certificate_number,
                sssc_cpd_hours_claimed=Decimal(sssc_cpd_hours) if sssc_cpd_hours else None,
                notes=notes,
                created_by=request.user
            )
            
            # Handle certificate file upload
            if 'certificate_file' in request.FILES:
                record.certificate_file = request.FILES['certificate_file']
                record.save()
            
            messages.success(request, f'Training record for {staff_member.full_name} - {course.name} has been added successfully.')
            return redirect('training_compliance_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error adding training record: {str(e)}')
    
    # GET request - show form
    selected_home = request.GET.get('care_home', None)
    selected_staff_id = request.GET.get('staff', None)
    
    # Get staff members
    if selected_home:
        staff_members = User.objects.filter(
            unit__care_home__name=selected_home,
            is_active=True
        ).distinct().order_by('first_name', 'last_name')
    else:
        staff_members = User.objects.filter(
            is_active=True,
            unit__isnull=False
        ).distinct().order_by('first_name', 'last_name')
    
    courses = TrainingCourse.objects.all().order_by('category', 'name')
    care_homes = CareHome.objects.filter(is_active=True).order_by('name')
    
    context = {
        'staff_members': staff_members,
        'courses': courses,
        'care_homes': care_homes,
        'selected_home': selected_home,
        'selected_staff_id': int(selected_staff_id) if selected_staff_id else None,
    }
    
    return render(request, 'compliance/add_staff_training_record.html', context)


@login_required
def submit_training_record(request):
    """Submit a new training record"""
    
    if request.method == 'POST':
        course_id = request.POST.get('course')
        completion_date = request.POST.get('completion_date')
        trainer_name = request.POST.get('trainer_name', '')
        training_provider = request.POST.get('training_provider', '')
        certificate_number = request.POST.get('certificate_number', '')
        sssc_cpd_hours = request.POST.get('sssc_cpd_hours', None)
        notes = request.POST.get('notes', '')
        
        try:
            course = TrainingCourse.objects.get(id=course_id)
            completion_date_obj = date.fromisoformat(completion_date)
            
            # Calculate expiry date based on course validity
            expiry_date = completion_date_obj + timedelta(days=course.validity_months * 30)
            
            # Create training record
            record = TrainingRecord.objects.create(
                staff_member=request.user,
                course=course,
                completion_date=completion_date_obj,
                expiry_date=expiry_date,
                trainer_name=trainer_name,
                training_provider=training_provider,
                certificate_number=certificate_number,
                sssc_cpd_hours_claimed=Decimal(sssc_cpd_hours) if sssc_cpd_hours else None,
                notes=notes,
                created_by=request.user
            )
            
            # Handle certificate file upload
            if 'certificate_file' in request.FILES:
                record.certificate_file = request.FILES['certificate_file']
                record.save()
            
            messages.success(request, f'Training record for {course.name} has been submitted successfully.')
            return redirect('my_training_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error submitting training record: {str(e)}')
    
    # GET request - show form
    courses = TrainingCourse.objects.all().order_by('category', 'name')
    
    context = {
        'courses': courses,
    }
    
    return render(request, 'compliance/submit_training_record.html', context)


# ============================================================================
# INDUCTION TRACKING
# ============================================================================

@login_required
def my_induction_progress(request):
    """View personal induction progress"""
    
    try:
        induction = InductionProgress.objects.get(staff_member=request.user)
    except InductionProgress.DoesNotExist:
        messages.info(request, 'No induction record found. Contact your manager if you recently started.')
        return redirect('staff_dashboard')
    
    # Calculate progress
    completion_percentage = induction.get_completion_percentage()
    days_elapsed = (date.today() - induction.start_date).days
    weeks_elapsed = days_elapsed // 7
    
    context = {
        'induction': induction,
        'completion_percentage': completion_percentage,
        'weeks_elapsed': weeks_elapsed,
        'days_remaining': (induction.expected_completion_date - date.today()).days,
    }
    
    return render(request, 'compliance/my_induction_progress.html', context)


@login_required
def induction_management(request):
    """Manager view - list all staff inductions"""
    
    # Check permissions
    if not (request.user.role and request.user.role.is_management):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('staff_dashboard')
    
    # Get all induction records
    inductions = InductionProgress.objects.select_related(
        'staff_member', 'assessor'
    ).order_by('-start_date')
    
    # Calculate statistics
    total_inductions = inductions.count()
    in_progress = inductions.filter(final_assessment_complete=False).count()
    completed = inductions.filter(final_assessment_complete=True).count()
    
    # Add completion percentage to each induction
    for induction in inductions:
        induction.completion_pct = induction.get_completion_percentage()
    
    context = {
        'inductions': inductions,
        'total_inductions': total_inductions,
        'in_progress': in_progress,
        'completed': completed,
    }
    
    return render(request, 'compliance/induction_management.html', context)


@login_required
def update_induction_progress(request, induction_id):
    """Manager updates induction progress for a staff member"""
    
    # Check permissions
    if not (request.user.role and request.user.role.is_management):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('staff_dashboard')
    
    induction = get_object_or_404(InductionProgress, id=induction_id)
    
    if request.method == 'POST':
        # Update all checkbox fields
        induction.week1_orientation_complete = request.POST.get('week1_orientation_complete') == 'on'
        induction.week1_fire_safety_complete = request.POST.get('week1_fire_safety_complete') == 'on'
        induction.week1_infection_control_complete = request.POST.get('week1_infection_control_complete') == 'on'
        induction.week1_moving_handling_complete = request.POST.get('week1_moving_handling_complete') == 'on'
        induction.week1_health_safety_complete = request.POST.get('week1_health_safety_complete') == 'on'
        
        induction.week2_4_safeguarding_complete = request.POST.get('week2_4_safeguarding_complete') == 'on'
        induction.week2_4_person_centred_care_complete = request.POST.get('week2_4_person_centred_care_complete') == 'on'
        
        induction.week5_8_medication_complete = request.POST.get('week5_8_medication_complete') == 'on'
        induction.week5_8_clinical_skills_complete = request.POST.get('week5_8_clinical_skills_complete') == 'on'
        
        induction.week9_12_sssc_registration_complete = request.POST.get('week9_12_sssc_registration_complete') == 'on'
        induction.week9_12_quality_improvement_complete = request.POST.get('week9_12_quality_improvement_complete') == 'on'
        induction.week9_12_supervision_support_complete = request.POST.get('week9_12_supervision_support_complete') == 'on'
        
        # Update competency hours
        induction.personal_care_hours = Decimal(request.POST.get('personal_care_hours', 0))
        induction.meal_prep_hours = Decimal(request.POST.get('meal_prep_hours', 0))
        induction.documentation_hours = Decimal(request.POST.get('documentation_hours', 0))
        induction.medication_hours = Decimal(request.POST.get('medication_hours', 0))
        
        # Final assessment
        if request.POST.get('final_assessment_complete') == 'on':
            induction.final_assessment_complete = True
            if not induction.final_assessment_date:
                induction.final_assessment_date = date.today()
            induction.final_assessment_outcome = request.POST.get('final_assessment_outcome', '')
            induction.assessor = request.user
            
            if not induction.actual_completion_date:
                induction.actual_completion_date = date.today()
        
        induction.notes = request.POST.get('notes', '')
        induction.save()
        
        messages.success(request, f'Induction progress updated for {induction.staff_member.get_full_name()}')
        return redirect('induction_management')
    
    context = {
        'induction': induction,
        'completion_percentage': induction.get_completion_percentage(),
    }
    
    return render(request, 'compliance/update_induction_progress.html', context)


# ============================================================================
# SUPERVISION RECORDS
# ============================================================================

@login_required
def my_supervision_records(request):
    """Staff member views their supervision history"""
    
    supervisions = SupervisionRecord.objects.filter(
        staff_member=request.user
    ).select_related('supervisor').order_by('-session_date')
    
    # Calculate statistics
    total_sessions = supervisions.count()
    this_year = supervisions.filter(session_date__year=timezone.now().year).count()
    
    # Find next scheduled supervision
    next_supervision = supervisions.filter(
        next_supervision_date__gte=date.today()
    ).order_by('next_supervision_date').first()
    
    # Check if supervision is overdue (more than 6 weeks since last)
    last_supervision = supervisions.first()
    supervision_overdue = False
    if last_supervision:
        days_since_last = (date.today() - last_supervision.session_date).days
        supervision_overdue = days_since_last > 42  # 6 weeks
    
    context = {
        'supervisions': supervisions,
        'total_sessions': total_sessions,
        'this_year': this_year,
        'next_supervision': next_supervision,
        'supervision_overdue': supervision_overdue,
        'last_supervision': last_supervision,
    }
    
    return render(request, 'compliance/my_supervision_records.html', context)


@login_required
def create_supervision_record(request):
    """Supervisor creates a supervision record"""
    
    # Check permissions
    if not (request.user.role and request.user.role.is_management):
        messages.error(request, 'You do not have permission to create supervision records.')
        return redirect('staff_dashboard')
    
    if request.method == 'POST':
        try:
            staff_member_id = request.POST.get('staff_member')
            staff_member = User.objects.get(sap=staff_member_id)
            
            supervision = SupervisionRecord.objects.create(
                staff_member=staff_member,
                supervisor=request.user,
                session_date=date.fromisoformat(request.POST.get('session_date')),
                session_type=request.POST.get('session_type'),
                duration_minutes=int(request.POST.get('duration_minutes', 60)),
                
                # Wellbeing
                wellbeing_score=int(request.POST.get('wellbeing_score', 5)),
                sickness_days_since_last=int(request.POST.get('sickness_days_since_last', 0)),
                wellbeing_concerns=request.POST.get('wellbeing_concerns', ''),
                support_offered=request.POST.get('support_offered', ''),
                
                # Performance
                performance_strengths=request.POST.get('performance_strengths', ''),
                performance_development=request.POST.get('performance_development', ''),
                
                # Training
                mandatory_training_current=request.POST.get('mandatory_training_current') == 'on',
                training_needs_identified=request.POST.get('training_needs_identified', ''),
                
                # SSSC
                sssc_registration_current=request.POST.get('sssc_registration_current') == 'on',
                sssc_cpd_hours_to_date=Decimal(request.POST.get('sssc_cpd_hours_to_date', 0)),
                
                # Safeguarding
                safeguarding_concerns_discussed=request.POST.get('safeguarding_concerns_discussed') == 'on',
                safeguarding_notes=request.POST.get('safeguarding_notes', ''),
                
                # Incidents
                incidents_since_last=int(request.POST.get('incidents_since_last', 0)),
                incident_learning=request.POST.get('incident_learning', ''),
                
                # Workload
                workload_manageable=request.POST.get('workload_manageable') == 'on',
                workload_notes=request.POST.get('workload_notes', ''),
                
                # Actions
                actions_from_previous=request.POST.get('actions_from_previous', ''),
                new_actions=request.POST.get('new_actions', ''),
                
                # Probationary
                is_probationary_review=request.POST.get('is_probationary_review') == 'on',
                probation_progress=request.POST.get('probation_progress', ''),
                probation_recommendation=request.POST.get('probation_recommendation', ''),
                
                # Next supervision
                next_supervision_date=date.fromisoformat(request.POST.get('next_supervision_date')) if request.POST.get('next_supervision_date') else None,
                
                supervisor_signature_date=date.today(),
            )
            
            messages.success(request, f'Supervision record created for {staff_member.full_name}')
            return redirect('supervision_management')
            
        except Exception as e:
            messages.error(request, f'Error creating supervision record: {str(e)}')
    
    # GET request - show form
    staff_members = User.objects.filter(
        is_active=True,
        is_staff=False
    ).order_by('last_name', 'first_name')
    
    context = {
        'staff_members': staff_members,
    }
    
    return render(request, 'compliance/create_supervision_record.html', context)


@login_required
def supervision_management(request):
    """Manager view - all supervision records"""
    
    # Check permissions
    if not (request.user.role and request.user.role.is_management):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('staff_dashboard')
    
    supervisions = SupervisionRecord.objects.select_related(
        'staff_member', 'supervisor'
    ).order_by('-session_date')
    
    # Calculate statistics
    total_sessions = supervisions.count()
    this_month = supervisions.filter(
        session_date__year=timezone.now().year,
        session_date__month=timezone.now().month
    ).count()
    
    # Staff needing supervision (no session in last 6 weeks)
    six_weeks_ago = date.today() - timedelta(weeks=6)
    staff_needing_supervision = []
    
    all_staff = User.objects.filter(is_active=True, is_staff=False)
    for staff in all_staff:
        last_supervision = SupervisionRecord.objects.filter(
            staff_member=staff
        ).order_by('-session_date').first()
        
        if not last_supervision or last_supervision.session_date < six_weeks_ago:
            staff_needing_supervision.append({
                'staff': staff,
                'last_session': last_supervision.session_date if last_supervision else None,
                'days_overdue': (date.today() - last_supervision.session_date).days if last_supervision else None
            })
    
    context = {
        'supervisions': supervisions,
        'total_sessions': total_sessions,
        'this_month': this_month,
        'staff_needing_supervision': staff_needing_supervision,
    }
    
    return render(request, 'compliance/supervision_management.html', context)


@login_required
def sign_supervision_record(request, record_id):
    """Allow staff member to sign their supervision record"""
    
    supervision = get_object_or_404(SupervisionRecord, id=record_id)
    
    # Check that the user is the staff member for this record
    if supervision.staff_member != request.user:
        messages.error(request, 'You can only sign your own supervision records.')
        return redirect('my_supervision_records')
    
    # Check if already signed
    if supervision.staff_signature_date:
        messages.warning(request, 'This supervision record has already been signed.')
        return redirect('my_supervision_records')
    
    if request.method == 'POST':
        # Get optional staff comments
        staff_comments = request.POST.get('staff_comments', '')
        
        # Sign the record
        supervision.staff_signature_date = date.today()
        supervision.staff_comments = staff_comments
        supervision.save()
        
        messages.success(request, 'Supervision record signed successfully.')
        return redirect('my_supervision_records')
    
    context = {
        'supervision': supervision,
    }
    
    return render(request, 'compliance/sign_supervision_record.html', context)


# ============================================================================
# INCIDENT REPORTING
# ============================================================================

@login_required
def report_incident(request):
    """Submit a new incident report"""
    
    if request.method == 'POST':
        try:
            # Generate reference number
            last_incident = IncidentReport.objects.order_by('-id').first()
            if last_incident:
                last_num = int(last_incident.reference_number.split('-')[-1])
                ref_number = f"IR-{timezone.now().year}-{last_num + 1:04d}"
            else:
                ref_number = f"IR-{timezone.now().year}-0001"
            
            incident = IncidentReport.objects.create(
                reference_number=ref_number,
                incident_date=date.fromisoformat(request.POST.get('incident_date')),
                incident_time=request.POST.get('incident_time'),
                reported_by=request.user,
                incident_type=request.POST.get('incident_type'),
                location=request.POST.get('location', ''),
                
                # Service user
                service_user_name=request.POST.get('service_user_name', ''),
                service_user_dob=date.fromisoformat(request.POST.get('service_user_dob')) if request.POST.get('service_user_dob') else None,
                
                # Description
                description=request.POST.get('description', ''),
                witnesses=request.POST.get('witnesses', ''),
                was_witnessed=request.POST.get('was_witnessed') == 'on',
                
                # Immediate actions
                immediate_actions=request.POST.get('immediate_actions', ''),
                injuries_sustained=request.POST.get('injuries_sustained', ''),
                body_map_completed=request.POST.get('body_map_completed') == 'on',
                photos_taken=request.POST.get('photos_taken') == 'on',
                
                # Medical
                gp_contacted=request.POST.get('gp_contacted') == 'on',
                ambulance_called=request.POST.get('ambulance_called') == 'on',
                hospital_attendance=request.POST.get('hospital_attendance') == 'on',
                hospital_admission=request.POST.get('hospital_admission') == 'on',
                medical_notes=request.POST.get('medical_notes', ''),
                
                # Severity
                severity=request.POST.get('severity'),
                risk_rating=request.POST.get('risk_rating'),
            )
            
            messages.success(request, f'Incident {ref_number} has been reported successfully. A manager will review it shortly.')
            
            # Check if Care Inspectorate notification required
            if incident.requires_care_inspectorate_notification():
                messages.warning(request, 'This incident requires Care Inspectorate notification. A manager has been notified.')
            
            return redirect('my_incident_reports')
            
        except Exception as e:
            messages.error(request, f'Error reporting incident: {str(e)}')
    
    # GET request - show form
    context = {
        'incident_types': IncidentReport._meta.get_field('incident_type').choices,
        'severity_choices': IncidentReport._meta.get_field('severity').choices,
        'risk_ratings': IncidentReport._meta.get_field('risk_rating').choices,
    }
    
    return render(request, 'compliance/report_incident.html', context)


@login_required
def my_incident_reports(request):
    """View incidents reported by current user"""
    
    incidents = IncidentReport.objects.filter(
        reported_by=request.user
    ).order_by('-incident_date', '-incident_time')
    
    context = {
        'incidents': incidents,
    }
    
    return render(request, 'compliance/my_incident_reports.html', context)


@login_required
def incident_management(request):
    """Manager view - all incident reports"""
    
    # Check permissions
    if not (request.user.role and request.user.role.is_management):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('staff_dashboard')
    
    # Filter options
    filter_type = request.GET.get('filter', 'all')
    
    incidents = IncidentReport.objects.select_related('reported_by', 'manager').order_by('-incident_date', '-incident_time')
    
    if filter_type == 'open':
        incidents = incidents.filter(incident_closed=False)
    elif filter_type == 'high_risk':
        incidents = incidents.filter(risk_rating__in=['HIGH', 'CRITICAL'])
    elif filter_type == 'care_inspectorate':
        incidents = incidents.filter(care_inspectorate_notified=True)
    elif filter_type == 'pending_review':
        incidents = incidents.filter(manager_reviewed=False)
    
    # Statistics
    total_incidents = IncidentReport.objects.count()
    this_month = IncidentReport.objects.filter(
        incident_date__year=timezone.now().year,
        incident_date__month=timezone.now().month
    ).count()
    open_incidents = IncidentReport.objects.filter(incident_closed=False).count()
    requiring_ci_notification = IncidentReport.objects.filter(
        care_inspectorate_notified=False
    ).filter(
        Q(severity='DEATH') | Q(severity='MAJOR_HARM') | 
        Q(incident_type__contains='SUSPECTED_') | Q(incident_type__contains='ALLEGATION')
    ).count()
    
    context = {
        'incidents': incidents,
        'total_incidents': total_incidents,
        'this_month': this_month,
        'open_incidents': open_incidents,
        'requiring_ci_notification': requiring_ci_notification,
        'current_filter': filter_type,
    }
    
    return render(request, 'compliance/incident_management.html', context)


@login_required
def view_incident(request, incident_id):
    """View detailed incident report"""
    
    incident = get_object_or_404(
        IncidentReport.objects.select_related(
            'reported_by', 
            'manager', 
            'investigation_assigned_to', 
            'closed_by'
        ), 
        id=incident_id
    )
    
    # Check permissions - staff can view their own, managers can view all
    if incident.reported_by != request.user and not (request.user.role and request.user.role.is_management):
        messages.error(request, 'You do not have permission to view this incident.')
        return redirect('staff_dashboard')
    
    context = {
        'incident': incident,
        'can_edit': request.user.role and request.user.role.is_management,
    }
    
    return render(request, 'compliance/view_incident.html', context)
