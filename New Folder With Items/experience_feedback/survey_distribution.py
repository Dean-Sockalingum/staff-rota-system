"""
Survey Distribution Utilities

Provides tools for distributing satisfaction surveys:
- QR code generation
- Unique token generation
- Survey link creation
- Email/SMS preparation
"""

import qrcode
import secrets
import hashlib
from io import BytesIO
from pathlib import Path
from django.conf import settings
from django.urls import reverse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def generate_survey_token():
    """
    Generate a cryptographically secure unique token for survey links.
    
    Returns:
        str: 64-character hexadecimal token
    """
    return secrets.token_hex(32)


def generate_qr_code(survey_url, filename=None):
    """
    Generate a QR code for a survey URL.
    
    Args:
        survey_url (str): Full URL to the survey
        filename (str, optional): Filename to save as. If None, auto-generates.
    
    Returns:
        str: Path to saved QR code image
    """
    # Create QR code
    qr = qrcode.QRCode(
        version=1,  # Controls size (1 is smallest)
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(survey_url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Generate filename if not provided
    if not filename:
        # Use hash of URL to create unique but deterministic filename
        url_hash = hashlib.md5(survey_url.encode()).hexdigest()[:16]
        filename = f"qr_codes/survey_{url_hash}.png"
    
    # Save to storage
    path = default_storage.save(filename, ContentFile(buffer.read()))
    
    return path


def get_survey_url(token, request=None):
    """
    Get the full absolute URL for a survey token.
    
    Args:
        token (str): Survey distribution token
        request (HttpRequest, optional): Request object to build absolute URL
    
    Returns:
        str: Full URL to survey
    """
    from django.contrib.sites.shortcuts import get_current_site
    
    # Get relative URL
    relative_url = reverse('experience_feedback:public_survey', kwargs={'token': token})
    
    if request:
        # Build absolute URL from request
        return request.build_absolute_uri(relative_url)
    else:
        # Build absolute URL from settings
        protocol = 'https' if settings.SECURE_SSL_REDIRECT else 'http'
        domain = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost:8000'
        return f"{protocol}://{domain}{relative_url}"


def create_survey_distribution(
    schedule,
    resident,
    recipient_name,
    recipient_email='',
    recipient_phone='',
    recipient_type='FAMILY',
    generate_qr=True
):
    """
    Create a new survey distribution record with token and optional QR code.
    
    Args:
        schedule: SurveyDistributionSchedule instance
        resident: Resident instance
        recipient_name: Name of survey recipient
        recipient_email: Email address (optional)
        recipient_phone: Phone number (optional)
        recipient_type: Type of recipient (RESIDENT, FAMILY, etc.)
        generate_qr: Whether to generate QR code
    
    Returns:
        SurveyDistribution: Created distribution record
    """
    from .models import SurveyDistribution
    
    # Generate unique token
    token = generate_survey_token()
    
    # Create distribution record
    distribution = SurveyDistribution.objects.create(
        schedule=schedule,
        care_home=schedule.care_home,
        survey_type=schedule.survey_type,
        resident=resident,
        recipient_name=recipient_name,
        recipient_email=recipient_email,
        recipient_phone=recipient_phone,
        recipient_type=recipient_type,
        survey_token=token,
    )
    
    # Generate QR code if requested
    if generate_qr:
        survey_url = get_survey_url(token)
        qr_path = generate_qr_code(survey_url, f"qr_codes/survey_{distribution.id}.png")
        distribution.qr_code_path = qr_path
        distribution.qr_code_generated = True
        distribution.save()
    
    return distribution


def get_email_content(distribution, request=None):
    """
    Generate email content for a survey distribution.
    
    Args:
        distribution: SurveyDistribution instance
        request: HttpRequest for building absolute URLs
    
    Returns:
        dict: Dictionary with 'subject', 'body_text', 'body_html'
    """
    survey_url = get_survey_url(distribution.survey_token, request)
    
    # Get customization from schedule or use defaults
    if distribution.schedule:
        subject = distribution.schedule.email_subject
        intro = distribution.schedule.email_intro
    else:
        subject = "We'd love your feedback"
        intro = "Your feedback helps us improve our care. Please take a few minutes to complete this survey."
    
    # Plain text version
    body_text = f"""
Dear {distribution.recipient_name},

{intro}

Survey Type: {distribution.get_survey_type_display()}
Resident: {distribution.resident.full_name}
Care Home: {distribution.care_home.name}

Please click the link below to complete the survey:
{survey_url}

This survey should take approximately 5-10 minutes to complete.

Your feedback is confidential and will be used to improve our services.

Thank you for your time,
{distribution.care_home.name}
"""
    
    # HTML version
    body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f8f9fa; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #28a745; color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
        .info {{ background-color: white; padding: 15px; border-left: 4px solid #007bff; margin: 15px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #6c757d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Satisfaction Survey</h1>
        </div>
        <div class="content">
            <p>Dear {distribution.recipient_name},</p>
            <p>{intro}</p>
            
            <div class="info">
                <p><strong>Survey Type:</strong> {distribution.get_survey_type_display()}</p>
                <p><strong>Resident:</strong> {distribution.resident.full_name}</p>
                <p><strong>Care Home:</strong> {distribution.care_home.name}</p>
            </div>
            
            <p style="text-align: center;">
                <a href="{survey_url}" class="button">Complete Survey Now</a>
            </p>
            
            <p style="font-size: 0.9em; color: #6c757d;">
                This survey should take approximately 5-10 minutes to complete.
                Your feedback is confidential and will be used to improve our services.
            </p>
            
            <p style="font-size: 0.85em; color: #6c757d;">
                If the button doesn't work, copy and paste this link into your browser:<br>
                <a href="{survey_url}">{survey_url}</a>
            </p>
        </div>
        <div class="footer">
            <p>Thank you for your time,<br>{distribution.care_home.name}</p>
        </div>
    </div>
</body>
</html>
"""
    
    return {
        'subject': subject,
        'body_text': body_text.strip(),
        'body_html': body_html,
    }


def get_sms_content(distribution, request=None):
    """
    Generate SMS content for a survey distribution.
    
    Args:
        distribution: SurveyDistribution instance
        request: HttpRequest for building absolute URLs
    
    Returns:
        str: SMS message text (max 160 characters for standard SMS)
    """
    survey_url = get_survey_url(distribution.survey_token, request)
    
    # Keep SMS short - use URL shortener in production
    message = f"""
{distribution.care_home.name}: Please complete our satisfaction survey for {distribution.resident.first_name}. 
{survey_url}
Thank you!
""".strip()
    
    # Warn if message is too long
    if len(message) > 160:
        # Use a shortened version
        message = f"{distribution.care_home.name}: Survey: {survey_url}"
    
    return message


def prepare_batch_distributions(schedule, residents_queryset):
    """
    Prepare batch survey distributions for multiple residents.
    
    Args:
        schedule: SurveyDistributionSchedule instance
        residents_queryset: QuerySet of Resident objects
    
    Returns:
        list: List of created SurveyDistribution instances
    """
    distributions = []
    
    for resident in residents_queryset:
        # Try to get family contact information
        # This assumes residents have a related family contact model
        # Adjust based on your actual data model
        
        # For now, create placeholders - you'll need to customize this
        # based on your actual Resident and FamilyContact relationships
        
        distribution = create_survey_distribution(
            schedule=schedule,
            resident=resident,
            recipient_name=f"Family of {resident.full_name}",
            recipient_email='',  # Would come from resident.primary_contact.email
            recipient_phone='',  # Would come from resident.primary_contact.phone
            recipient_type='FAMILY',
            generate_qr=schedule.print_qr_code
        )
        distributions.append(distribution)
    
    return distributions
