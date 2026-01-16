from django.contrib import admin
from django.core.mail import send_mail
from django.contrib import messages
from django.utils.html import format_html
from django.utils import timezone
from .models import EmailConfiguration
import traceback


@admin.register(EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        'provider',
        'from_email',
        'host',
        'port',
        'is_active',
        'last_test_status_display',
        'updated_at'
    ]
    
    list_filter = ['provider', 'is_active', 'last_test_status']
    
    search_fields = ['from_email', 'host', 'username']
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'last_test_date',
        'last_test_status',
        'last_test_message',
        'password_display'
    ]
    
    fieldsets = (
        ('Email Provider', {
            'fields': ('provider',),
            'description': 'Select your email provider. Common settings will be auto-filled.'
        }),
        ('Connection Settings', {
            'fields': ('host', 'port', 'use_tls', 'use_ssl'),
            'description': 'SMTP server connection details.'
        }),
        ('Authentication', {
            'fields': ('username', 'password', 'password_display'),
            'description': 'SMTP credentials. Password is encrypted in database.'
        }),
        ('Email Settings', {
            'fields': ('from_email',),
            'description': 'Default sender email address.'
        }),
        ('Status', {
            'fields': ('is_active', 'last_test_date', 'last_test_status', 'last_test_message'),
            'description': 'Configuration status and test results.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['test_email_configuration', 'activate_configuration', 'deactivate_configuration']
    
    class Media:
        js = ('admin/js/email_config_admin.js',)
    
    def password_display(self, obj):
        """Display masked password"""
        if obj.password:
            return format_html('<code>••••••••••••</code> <small>(Encrypted)</small>')
        return '-'
    password_display.short_description = 'Password (Encrypted)'
    
    def last_test_status_display(self, obj):
        """Display test status with color coding"""
        if not obj.last_test_status:
            return format_html('<span style="color: gray;">Not tested</span>')
        
        colors = {
            'success': 'green',
            'failed': 'red',
            'warning': 'orange',
        }
        
        color = colors.get(obj.last_test_status, 'gray')
        icon = '✓' if obj.last_test_status == 'success' else '✗'
        
        return format_html(
            '<span style="color: {};">{} {}</span>',
            color,
            icon,
            obj.last_test_status.upper()
        )
    last_test_status_display.short_description = 'Test Status'
    
    def test_email_configuration(self, request, queryset):
        """Test email configuration by sending a test email"""
        if queryset.count() != 1:
            self.message_user(
                request,
                'Please select exactly one configuration to test.',
                level=messages.WARNING
            )
            return
        
        config = queryset.first()
        
        # Temporarily activate this config for testing
        from django.conf import settings
        from django.core.mail.backends.smtp import EmailBackend
        
        try:
            # Create temporary SMTP backend with this config
            backend = EmailBackend(
                host=config.host,
                port=config.port,
                username=config.username,
                password=config.get_decrypted_password(),
                use_tls=config.use_tls,
                use_ssl=config.use_ssl,
                fail_silently=False,
            )
            
            # Send test email
            test_email = request.user.email or 'admin@localhost'
            
            backend.send_messages([
                send_mail(
                    subject='Staff Rota System - Email Configuration Test',
                    message=f'''This is a test email from the Staff Rota System.

Email Configuration Details:
- Provider: {config.get_provider_display()}
- Host: {config.host}
- Port: {config.port}
- TLS: {config.use_tls}
- SSL: {config.use_ssl}
- From: {config.from_email}
- Test Date: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}

If you received this email, your email configuration is working correctly!

You can now activate this configuration to use it for:
- Leave request notifications
- 2FA authentication codes
- Password reset emails
- Shift change notifications

--
Staff Rota System
Automated Email Test
''',
                    from_email=config.from_email,
                    recipient_list=[test_email],
                    fail_silently=False,
                )
            ])
            
            # Update test status
            config.last_test_date = timezone.now()
            config.last_test_status = 'success'
            config.last_test_message = f'Test email sent successfully to {test_email}'
            config.save(update_fields=['last_test_date', 'last_test_status', 'last_test_message'])
            
            self.message_user(
                request,
                format_html(
                    '✓ Test email sent successfully to <strong>{}</strong>. Check your inbox!',
                    test_email
                ),
                level=messages.SUCCESS
            )
            
        except Exception as e:
            # Update test status with error
            config.last_test_date = timezone.now()
            config.last_test_status = 'failed'
            config.last_test_message = f'Error: {str(e)}\n\n{traceback.format_exc()}'
            config.save(update_fields=['last_test_date', 'last_test_status', 'last_test_message'])
            
            self.message_user(
                request,
                format_html(
                    '✗ Email test failed: <strong>{}</strong>. Check configuration settings.',
                    str(e)
                ),
                level=messages.ERROR
            )
    
    test_email_configuration.short_description = '✉ Test Email Configuration (Send Test Email)'
    
    def activate_configuration(self, request, queryset):
        """Activate selected configuration"""
        if queryset.count() != 1:
            self.message_user(
                request,
                'Please select exactly one configuration to activate.',
                level=messages.WARNING
            )
            return
        
        config = queryset.first()
        
        # Deactivate all other configs
        EmailConfiguration.objects.filter(is_active=True).update(is_active=False)
        
        # Activate this config
        config.is_active = True
        config.save()
        
        self.message_user(
            request,
            format_html(
                '✓ Email configuration <strong>{}</strong> is now active.',
                config
            ),
            level=messages.SUCCESS
        )
    
    activate_configuration.short_description = '✓ Activate Configuration'
    
    def deactivate_configuration(self, request, queryset):
        """Deactivate selected configurations"""
        count = queryset.filter(is_active=True).update(is_active=False)
        
        self.message_user(
            request,
            f'✓ Deactivated {count} configuration(s). System will use console email backend.',
            level=messages.SUCCESS
        )
    
    deactivate_configuration.short_description = '✗ Deactivate Configuration'
    
    def save_model(self, request, obj, form, change):
        """Custom save handling"""
        # Auto-fill provider defaults if provider changed
        if 'provider' in form.changed_data and not change:
            defaults = EmailConfiguration.get_provider_defaults(obj.provider)
            obj.host = defaults['host']
            obj.port = defaults['port']
            obj.use_tls = defaults['use_tls']
            obj.use_ssl = defaults['use_ssl']
        
        super().save_model(request, obj, form, change)
        
        # Show helpful message
        if obj.is_active:
            self.message_user(
                request,
                format_html(
                    '✓ Configuration saved and activated. <strong>Test it</strong> using the "Test Email Configuration" action.',
                ),
                level=messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                'Configuration saved. Activate it to start using for email notifications.',
                level=messages.INFO
            )
