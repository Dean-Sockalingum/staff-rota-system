"""
Compliance Monitoring Service

Monitors staff certifications, runs compliance checks,
tracks regulatory requirements, and generates audit trails.
"""

from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal


def check_certification_expiry(care_home=None, days_ahead=90):
    """
    Check for certifications expiring within specified days
    
    Returns: Dictionary with expiring and expired certifications
    """
    from .models import StaffCertification, User
    
    today = timezone.now().date()
    expiry_threshold = today + timedelta(days=days_ahead)
    
    # Filter certifications
    certifications = StaffCertification.objects.all()
    if care_home:
        certifications = certifications.filter(staff_member__care_home=care_home)
    
    # Find expiring certifications
    expiring_soon = certifications.filter(
        expiry_date__gte=today,
        expiry_date__lte=expiry_threshold,
        status__in=['VALID', 'EXPIRING_SOON']
    ).order_by('expiry_date')
    
    # Find expired certifications
    expired = certifications.filter(
        expiry_date__lt=today,
        status='EXPIRED'
    ).order_by('expiry_date')
    
    # Group by staff member
    staff_with_expiring = {}
    for cert in expiring_soon:
        staff_id = cert.staff_member.id
        if staff_id not in staff_with_expiring:
            staff_with_expiring[staff_id] = {
                'staff': cert.staff_member,
                'certifications': []
            }
        staff_with_expiring[staff_id]['certifications'].append(cert)
    
    staff_with_expired = {}
    for cert in expired:
        staff_id = cert.staff_member.id
        if staff_id not in staff_with_expired:
            staff_with_expired[staff_id] = {
                'staff': cert.staff_member,
                'certifications': []
            }
        staff_with_expired[staff_id]['certifications'].append(cert)
    
    # Count critical certifications
    critical_types = ['PVG', 'SSSC', 'FIRST_AID', 'MEDICATION', 'SAFEGUARDING']
    critical_expiring = expiring_soon.filter(certification_type__in=critical_types).count()
    critical_expired = expired.filter(certification_type__in=critical_types).count()
    
    return {
        'expiring_soon_count': expiring_soon.count(),
        'expired_count': expired.count(),
        'critical_expiring': critical_expiring,
        'critical_expired': critical_expired,
        'expiring_soon': list(expiring_soon),
        'expired': list(expired),
        'staff_with_expiring': list(staff_with_expiring.values()),
        'staff_with_expired': list(staff_with_expired.values()),
        'days_ahead': days_ahead,
    }


def check_training_compliance(care_home=None, unit=None):
    """
    Check training compliance for staff
    
    Returns: Dictionary with compliance statistics
    """
    from .models import TrainingRecord, User
    
    # Get staff
    staff = User.objects.filter(is_active=True)
    if care_home:
        staff = staff.filter(care_home=care_home)
    if unit:
        staff = staff.filter(units=unit)
    
    total_staff = staff.count()
    
    # Check mandatory training
    mandatory_courses = [
        'Safeguarding Adults',
        'Fire Safety',
        'First Aid',
        'Manual Handling',
        'Infection Control',
    ]
    
    compliance_by_course = {}
    overall_compliant = 0
    
    for course_name in mandatory_courses:
        completed_staff = staff.filter(
            training_records__course__title=course_name,
            training_records__status='COMPLETED'
        ).distinct().count()
        
        compliance_rate = (completed_staff / total_staff * 100) if total_staff > 0 else 0
        
        compliance_by_course[course_name] = {
            'completed': completed_staff,
            'total': total_staff,
            'compliance_rate': compliance_rate,
            'non_compliant': total_staff - completed_staff,
        }
    
    # Calculate overall compliance
    # Staff compliant if they have all mandatory courses
    for staff_member in staff:
        completed_courses = staff_member.training_records.filter(
            course__title__in=mandatory_courses,
            status='COMPLETED'
        ).values_list('course__title', flat=True)
        
        if set(mandatory_courses).issubset(set(completed_courses)):
            overall_compliant += 1
    
    overall_compliance_rate = (overall_compliant / total_staff * 100) if total_staff > 0 else 0
    
    # Find staff with missing training
    staff_missing_training = []
    for staff_member in staff:
        completed_courses = set(staff_member.training_records.filter(
            course__title__in=mandatory_courses,
            status='COMPLETED'
        ).values_list('course__title', flat=True))
        
        missing_courses = set(mandatory_courses) - completed_courses
        
        if missing_courses:
            staff_missing_training.append({
                'staff': staff_member,
                'missing_courses': list(missing_courses),
                'missing_count': len(missing_courses),
            })
    
    # Sort by number of missing courses (most missing first)
    staff_missing_training.sort(key=lambda x: x['missing_count'], reverse=True)
    
    return {
        'total_staff': total_staff,
        'overall_compliant': overall_compliant,
        'overall_compliance_rate': overall_compliance_rate,
        'overall_non_compliant': total_staff - overall_compliant,
        'compliance_by_course': compliance_by_course,
        'staff_missing_training': staff_missing_training,
        'mandatory_courses': mandatory_courses,
    }


def calculate_compliance_score(care_home=None, unit=None):
    """
    Calculate overall compliance score (0-100)
    
    Returns: Dictionary with compliance score and breakdown
    """
    # Get certification compliance
    cert_data = check_certification_expiry(care_home, days_ahead=90)
    
    # Get training compliance
    training_data = check_training_compliance(care_home, unit)
    
    # Calculate certification score (0-40 points)
    # Deduct points for expired and expiring certifications
    from .models import StaffCertification
    total_certs = StaffCertification.objects.filter(
        staff_member__care_home=care_home
    ).count() if care_home else 0
    
    if total_certs > 0:
        expired_penalty = (cert_data['expired_count'] / total_certs * 20)  # Max 20 points
        expiring_penalty = (cert_data['expiring_soon_count'] / total_certs * 10)  # Max 10 points
        critical_penalty = (cert_data['critical_expired'] * 5)  # 5 points per critical expired
        
        cert_score = max(0, 40 - expired_penalty - expiring_penalty - critical_penalty)
    else:
        cert_score = 40  # No certifications tracked = full points
    
    # Calculate training score (0-40 points)
    training_score = training_data['overall_compliance_rate'] * 0.4
    
    # Calculate staffing ratio score (0-20 points)
    # This would check if required staffing levels are met
    # For now, assume 15/20
    staffing_score = 15
    
    # Total compliance score
    total_score = cert_score + training_score + staffing_score
    
    # Determine compliance level
    if total_score >= 90:
        compliance_level = 'EXCELLENT'
        compliance_color = 'success'
    elif total_score >= 75:
        compliance_level = 'GOOD'
        compliance_color = 'info'
    elif total_score >= 60:
        compliance_level = 'ACCEPTABLE'
        compliance_color = 'warning'
    else:
        compliance_level = 'POOR'
        compliance_color = 'danger'
    
    return {
        'total_score': round(total_score, 2),
        'cert_score': round(cert_score, 2),
        'training_score': round(training_score, 2),
        'staffing_score': staffing_score,
        'compliance_level': compliance_level,
        'compliance_color': compliance_color,
        'cert_data': cert_data,
        'training_data': training_data,
    }


def run_compliance_check(care_home, check_type, check_name, description, checked_by):
    """
    Run a compliance check and create record
    
    Returns: ComplianceCheck object
    """
    from .models import ComplianceCheck
    
    today = timezone.now().date()
    
    if check_type == 'TRAINING':
        # Run training compliance check
        training_data = check_training_compliance(care_home)
        
        status = 'PASS' if training_data['overall_compliance_rate'] >= 90 else 'FAIL'
        compliance_score = training_data['overall_compliance_rate']
        violations = training_data['overall_non_compliant']
        
        findings = f"Overall compliance: {compliance_score:.1f}%\n"
        findings += f"Compliant staff: {training_data['overall_compliant']}/{training_data['total_staff']}\n\n"
        findings += "Course breakdown:\n"
        for course, data in training_data['compliance_by_course'].items():
            findings += f"- {course}: {data['compliance_rate']:.1f}% ({data['completed']}/{data['total']})\n"
        
        severity = 'LOW' if compliance_score >= 90 else 'MEDIUM' if compliance_score >= 75 else 'HIGH'
        
    elif check_type == 'CERTIFICATION':
        # Run certification check
        cert_data = check_certification_expiry(care_home, days_ahead=30)
        
        status = 'PASS' if cert_data['critical_expired'] == 0 else 'FAIL'
        violations = cert_data['expired_count'] + cert_data['critical_expiring']
        
        # Calculate compliance score
        from .models import StaffCertification
        total_certs = StaffCertification.objects.filter(
            staff_member__care_home=care_home
        ).count()
        
        if total_certs > 0:
            compliance_score = ((total_certs - cert_data['expired_count']) / total_certs * 100)
        else:
            compliance_score = 100
        
        findings = f"Expired certifications: {cert_data['expired_count']}\n"
        findings += f"Expiring within 30 days: {cert_data['expiring_soon_count']}\n"
        findings += f"Critical expired: {cert_data['critical_expired']}\n"
        findings += f"Critical expiring: {cert_data['critical_expiring']}\n"
        
        severity = 'CRITICAL' if cert_data['critical_expired'] > 0 else 'HIGH' if cert_data['expired_count'] > 5 else 'MEDIUM'
        
    else:
        # Generic check
        status = 'IN_PROGRESS'
        compliance_score = None
        violations = 0
        findings = ""
        severity = 'MEDIUM'
    
    # Determine if action required
    action_required = status == 'FAIL' or violations > 0
    
    # Create compliance check
    check = ComplianceCheck.objects.create(
        care_home=care_home,
        check_type=check_type,
        check_name=check_name,
        description=description,
        check_date=today,
        status=status,
        severity=severity,
        compliance_score=compliance_score,
        findings=findings,
        violations_found=violations,
        action_required=action_required,
        checked_by=checked_by,
    )
    
    return check


def get_overdue_certifications(care_home=None, staff_member=None):
    """
    Get list of overdue certifications that need renewal
    
    Returns: List of overdue certifications
    """
    from .models import StaffCertification
    
    today = timezone.now().date()
    
    # Filter certifications
    certifications = StaffCertification.objects.filter(
        expiry_date__lt=today,
        status='EXPIRED'
    )
    
    if care_home:
        certifications = certifications.filter(staff_member__care_home=care_home)
    if staff_member:
        certifications = certifications.filter(staff_member=staff_member)
    
    certifications = certifications.select_related('staff_member').order_by('expiry_date')
    
    overdue_list = []
    for cert in certifications:
        days_overdue = (today - cert.expiry_date).days
        
        overdue_list.append({
            'certification': cert,
            'staff_member': cert.staff_member,
            'certification_type': cert.get_certification_type_display(),
            'expiry_date': cert.expiry_date,
            'days_overdue': days_overdue,
            'is_critical': cert.certification_type in ['PVG', 'SSSC', 'FIRST_AID', 'MEDICATION', 'SAFEGUARDING'],
        })
    
    return overdue_list


def generate_compliance_report(care_home, start_date=None, end_date=None):
    """
    Generate comprehensive compliance report
    
    Returns: Dictionary with report data
    """
    if not end_date:
        end_date = timezone.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=90)
    
    # Get compliance score
    compliance_data = calculate_compliance_score(care_home)
    
    # Get certification data
    cert_data = check_certification_expiry(care_home, days_ahead=90)
    
    # Get training data
    training_data = check_training_compliance(care_home)
    
    # Get recent compliance checks
    from .models import ComplianceCheck
    recent_checks = ComplianceCheck.objects.filter(
        care_home=care_home,
        check_date__gte=start_date,
        check_date__lte=end_date
    ).order_by('-check_date')[:10]
    
    # Calculate check statistics
    total_checks = recent_checks.count()
    passed_checks = recent_checks.filter(status='PASS').count()
    failed_checks = recent_checks.filter(status='FAIL').count()
    
    pass_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    # Get overdue certifications
    overdue_certs = get_overdue_certifications(care_home)
    
    # Identify areas needing attention
    areas_needing_attention = []
    
    if cert_data['critical_expired'] > 0:
        areas_needing_attention.append({
            'area': 'Critical Certifications',
            'severity': 'CRITICAL',
            'description': f"{cert_data['critical_expired']} critical certifications have expired",
            'action': 'Immediate renewal required for PVG, SSSC, or other critical certifications',
        })
    
    if training_data['overall_compliance_rate'] < 80:
        areas_needing_attention.append({
            'area': 'Training Compliance',
            'severity': 'HIGH',
            'description': f"Overall training compliance is {training_data['overall_compliance_rate']:.1f}%",
            'action': f"{training_data['overall_non_compliant']} staff need mandatory training",
        })
    
    if cert_data['expiring_soon_count'] > 10:
        areas_needing_attention.append({
            'area': 'Certification Renewals',
            'severity': 'MEDIUM',
            'description': f"{cert_data['expiring_soon_count']} certifications expiring within 90 days",
            'action': 'Schedule renewal sessions for expiring certifications',
        })
    
    return {
        'care_home': care_home,
        'start_date': start_date,
        'end_date': end_date,
        'compliance_score': compliance_data['total_score'],
        'compliance_level': compliance_data['compliance_level'],
        'cert_data': cert_data,
        'training_data': training_data,
        'recent_checks': recent_checks,
        'total_checks': total_checks,
        'passed_checks': passed_checks,
        'failed_checks': failed_checks,
        'pass_rate': pass_rate,
        'overdue_certifications': overdue_certs,
        'areas_needing_attention': areas_needing_attention,
    }


def send_expiry_alerts(care_home=None, days_ahead=30):
    """
    Send alerts for certifications expiring soon
    
    Returns: Number of alerts sent
    """
    from .models import StaffCertification
    from django.core.mail import send_mail
    from django.conf import settings
    
    today = timezone.now().date()
    alert_date = today + timedelta(days=days_ahead)
    
    # Find certifications that need alerts
    certifications = StaffCertification.objects.filter(
        expiry_date__lte=alert_date,
        expiry_date__gte=today,
        alert_sent=False,
        status__in=['VALID', 'EXPIRING_SOON']
    )
    
    if care_home:
        certifications = certifications.filter(staff_member__care_home=care_home)
    
    alerts_sent = 0
    
    for cert in certifications:
        days_until_expiry = (cert.expiry_date - today).days
        
        # Send email to staff member
        if cert.staff_member.email:
            subject = f"Certification Expiring Soon: {cert.get_certification_type_display()}"
            message = f"""
Dear {cert.staff_member.get_full_name()},

Your {cert.get_certification_type_display()} certification is expiring in {days_until_expiry} days.

Certification Details:
- Type: {cert.get_certification_type_display()}
- Expiry Date: {cert.expiry_date}
- Issuing Body: {cert.issuing_body}

Please arrange for renewal as soon as possible to maintain compliance.

Thank you,
{care_home.name if care_home else 'Staff Rota System'}
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [cert.staff_member.email],
                    fail_silently=True,
                )
                
                # Mark alert as sent
                cert.alert_sent = True
                cert.alert_sent_at = timezone.now()
                cert.save()
                
                alerts_sent += 1
            except Exception as e:
                print(f"Failed to send alert for certification {cert.id}: {e}")
    
    return alerts_sent
