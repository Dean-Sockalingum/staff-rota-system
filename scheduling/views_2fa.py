"""
Task 48: Two-Factor Authentication (2FA) Views
Handles TOTP setup, verification, backup codes, and 2FA enforcement
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .decorators_api import api_login_required
from django_otp import user_has_device
from django_otp.decorators import otp_required
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django.views.decorators.http import require_http_methods
from django.conf import settings
import qrcode
import io
import base64
from django.utils import timezone
import secrets


@login_required
def two_factor_setup(request):
    """
    Display 2FA setup page with QR code for authenticator app
    """
    user = request.user
    
    # Check if user already has 2FA enabled
    has_2fa = user_has_device(user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'enable':
            # Create new TOTP device
            device = TOTPDevice.objects.create(
                user=user,
                name=f"{user.get_full_name()}'s Authenticator",
                confirmed=False  # Not confirmed until first successful verification
            )
            
            # Generate backup codes
            static_device = StaticDevice.objects.create(
                user=user,
                name=f"{user.get_full_name()}'s Backup Codes",
                confirmed=False
            )
            
            # Create 10 backup codes
            backup_codes = []
            for _ in range(10):
                code = secrets.token_hex(4).upper()  # 8-character hex code
                StaticToken.objects.create(device=static_device, token=code)
                backup_codes.append(code)
            
            # Store backup codes in session to display once
            request.session['backup_codes'] = backup_codes
            request.session['totp_device_id'] = device.id
            
            messages.success(request, "2FA setup initiated. Scan the QR code with your authenticator app.")
            return redirect('scheduling:two_factor_setup')
        
        elif action == 'verify':
            # Verify TOTP token
            device_id = request.session.get('totp_device_id')
            token = request.POST.get('token', '').strip()
            
            if device_id and token:
                try:
                    device = TOTPDevice.objects.get(id=device_id, user=user, confirmed=False)
                    
                    if device.verify_token(token):
                        # Token is valid - confirm the device
                        device.confirmed = True
                        device.save()
                        
                        # Also confirm the backup codes device
                        StaticDevice.objects.filter(user=user, confirmed=False).update(confirmed=True)
                        
                        # Clear session data
                        if 'totp_device_id' in request.session:
                            del request.session['totp_device_id']
                        
                        messages.success(request, "✅ Two-Factor Authentication enabled successfully!")
                        return redirect('scheduling:two_factor_setup')
                    else:
                        messages.error(request, "Invalid verification code. Please try again.")
                except TOTPDevice.DoesNotExist:
                    messages.error(request, "2FA device not found. Please start setup again.")
    
    # Get current device info
    totp_device = None
    backup_codes = request.session.pop('backup_codes', None)
    device_id = request.session.get('totp_device_id')
    
    if device_id:
        try:
            totp_device = TOTPDevice.objects.get(id=device_id, user=user)
        except TOTPDevice.DoesNotExist:
            pass
    elif has_2fa:
        # Get confirmed device
        totp_device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
    
    # Generate QR code for TOTP device
    qr_code_data = None
    if totp_device and not totp_device.confirmed:
        # Generate provisioning URI for authenticator app
        # Format: otpauth://totp/LABEL?secret=SECRET&issuer=ISSUER
        label = f"StaffRota:{user.get_full_name()}"
        secret = totp_device.config_url  # django-otp provides this
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(secret)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for embedding in HTML
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_code_data = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'has_2fa': has_2fa,
        'totp_device': totp_device,
        'qr_code_data': qr_code_data,
        'backup_codes': backup_codes,
        'requires_2fa': _user_requires_2fa(user),
    }
    
    return render(request, 'scheduling/two_factor_setup.html', context)


@login_required
@require_http_methods(["POST"])
def two_factor_disable(request):
    """
    Disable 2FA for current user
    """
    user = request.user
    
    # Delete all TOTP devices
    TOTPDevice.objects.filter(user=user).delete()
    
    # Delete all backup code devices
    StaticDevice.objects.filter(user=user).delete()
    
    messages.success(request, "Two-Factor Authentication has been disabled.")
    return redirect('scheduling:two_factor_setup')


@login_required
def two_factor_verify(request):
    """
    Verify 2FA token during login (second step)
    """
    user = request.user
    
    # Check if user is already verified
    if user.is_verified():
        return redirect('scheduling:dashboard')
    
    if request.method == 'POST':
        token = request.POST.get('token', '').strip()
        use_backup = request.POST.get('use_backup', False)
        
        if token:
            # Try TOTP device first
            totp_devices = TOTPDevice.objects.filter(user=user, confirmed=True)
            for device in totp_devices:
                if device.verify_token(token):
                    # Mark user as verified in session
                    request.session['_otp_verified'] = True
                    request.session['_otp_device_id'] = device.id
                    messages.success(request, "✅ Two-Factor Authentication verified!")
                    
                    # Redirect to intended page or dashboard
                    next_url = request.session.pop('next_after_2fa', None)
                    return redirect(next_url or 'scheduling:dashboard')
            
            # Try backup codes if TOTP failed
            static_devices = StaticDevice.objects.filter(user=user, confirmed=True)
            for device in static_devices:
                for static_token in device.token_set.all():
                    if static_token.token == token:
                        # Backup code is valid - use it once and delete
                        static_token.delete()
                        
                        request.session['_otp_verified'] = True
                        request.session['_otp_device_id'] = device.id
                        messages.success(request, "✅ Backup code accepted!")
                        messages.warning(request, f"You have {device.token_set.count()} backup codes remaining.")
                        
                        next_url = request.session.pop('next_after_2fa', None)
                        return redirect(next_url or 'scheduling:dashboard')
            
            messages.error(request, "Invalid verification code. Please try again.")
    
    # Count remaining backup codes
    backup_count = 0
    static_device = StaticDevice.objects.filter(user=user, confirmed=True).first()
    if static_device:
        backup_count = static_device.token_set.count()
    
    context = {
        'backup_count': backup_count,
    }
    
    return render(request, 'scheduling/two_factor_verify.html', context)


@login_required
def regenerate_backup_codes(request):
    """
    Regenerate backup codes (invalidates old ones)
    """
    if request.method != 'POST':
        return redirect('scheduling:two_factor_setup')
    
    user = request.user
    
    # Delete old backup codes
    StaticDevice.objects.filter(user=user).delete()
    
    # Create new backup codes device
    static_device = StaticDevice.objects.create(
        user=user,
        name=f"{user.get_full_name()}'s Backup Codes",
        confirmed=True
    )
    
    # Generate 10 new backup codes
    backup_codes = []
    for _ in range(10):
        code = secrets.token_hex(4).upper()
        StaticToken.objects.create(device=static_device, token=code)
        backup_codes.append(code)
    
    # Store in session to display once
    request.session['backup_codes'] = backup_codes
    
    messages.success(request, "New backup codes generated. Save them securely!")
    return redirect('scheduling:two_factor_setup')


def _user_requires_2fa(user):
    """
    Check if user is required to have 2FA enabled
    Managers and admins must have 2FA
    """
    # Check if user is staff/superuser
    if user.is_staff or user.is_superuser:
        return True
    
    # Check if user has manager role
    try:
        if hasattr(user, 'staffprofile'):
            profile = user.staffprofile
            if profile.role and 'Manager' in profile.role.name:
                return True
    except:
        pass
    
    return False


@api_login_required
def two_factor_status(request):
    """
    API endpoint to check 2FA status (for AJAX calls)
    """
    user = request.user
    
    has_2fa = user_has_device(user)
    requires_2fa = _user_requires_2fa(user)
    is_verified = user.is_verified() if hasattr(user, 'is_verified') else False
    
    # Count devices
    totp_count = TOTPDevice.objects.filter(user=user, confirmed=True).count()
    backup_count = 0
    static_device = StaticDevice.objects.filter(user=user, confirmed=True).first()
    if static_device:
        backup_count = static_device.token_set.count()
    
    return JsonResponse({
        'has_2fa': has_2fa,
        'requires_2fa': requires_2fa,
        'is_verified': is_verified,
        'totp_devices': totp_count,
        'backup_codes_remaining': backup_count,
    })
