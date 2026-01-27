from django.db import models
from django.core.exceptions import ValidationError
from cryptography.fernet import Fernet
import os


class EmailConfiguration(models.Model):
    """
    Email configuration model for UI-based SMTP setup.
    Allows HSCP administrators to configure email without editing .env files.
    """
    
    PROVIDER_CHOICES = [
        ('gmail', 'Gmail'),
        ('sendgrid', 'SendGrid'),
        ('microsoft365', 'Microsoft 365 / Outlook'),
        ('custom', 'Custom SMTP Server'),
    ]
    
    # Provider selection
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        default='custom',
        help_text='Select your email provider. This will auto-fill common settings.'
    )
    
    # Connection settings
    host = models.CharField(
        max_length=255,
        help_text='SMTP server hostname (e.g., smtp.gmail.com, smtp.sendgrid.net)'
    )
    
    port = models.IntegerField(
        default=587,
        help_text='SMTP server port (587 for TLS, 465 for SSL, 25 for unencrypted)'
    )
    
    use_tls = models.BooleanField(
        default=True,
        help_text='Use TLS encryption (recommended for port 587)'
    )
    
    use_ssl = models.BooleanField(
        default=False,
        help_text='Use SSL encryption (for port 465). Do not use with TLS.'
    )
    
    # Authentication
    username = models.EmailField(
        help_text='SMTP username (usually your email address)'
    )
    
    password = models.CharField(
        max_length=512,
        help_text='SMTP password or app password (will be encrypted in database)'
    )
    
    # Email settings
    from_email = models.EmailField(
        help_text='Default "From" email address (e.g., noreply@yourdomain.com)'
    )
    
    # Status
    is_active = models.BooleanField(
        default=False,
        help_text='Only one configuration can be active at a time'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Test results
    last_test_date = models.DateTimeField(null=True, blank=True)
    last_test_status = models.CharField(max_length=20, null=True, blank=True)
    last_test_message = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Email Configuration'
        verbose_name_plural = 'Email Configurations'
        ordering = ['-is_active', '-updated_at']
    
    def __str__(self):
        active_status = ' (ACTIVE)' if self.is_active else ''
        return f'{self.get_provider_display()} - {self.from_email}{active_status}'
    
    def clean(self):
        """Validate configuration settings"""
        errors = {}
        
        # Cannot use both TLS and SSL
        if self.use_tls and self.use_ssl:
            errors['use_tls'] = 'Cannot use both TLS and SSL. Choose one.'
            errors['use_ssl'] = 'Cannot use both TLS and SSL. Choose one.'
        
        # Port validation
        if self.use_tls and self.port == 465:
            errors['port'] = 'Port 465 is typically for SSL, not TLS. Use port 587 for TLS.'
        
        if self.use_ssl and self.port == 587:
            errors['port'] = 'Port 587 is typically for TLS, not SSL. Use port 465 for SSL.'
        
        # Only one active configuration allowed
        if self.is_active:
            active_configs = EmailConfiguration.objects.filter(is_active=True)
            if self.pk:
                active_configs = active_configs.exclude(pk=self.pk)
            if active_configs.exists():
                errors['is_active'] = 'Another configuration is already active. Deactivate it first.'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Encrypt password before saving"""
        # Encrypt password if it's being changed and is not already encrypted
        if self.pk is None or self._password_changed():
            self.password = self._encrypt_password(self.password)
        
        # Deactivate other configs if this one is being activated
        if self.is_active:
            EmailConfiguration.objects.filter(is_active=True).update(is_active=False)
        
        super().save(*args, **kwargs)
    
    def _password_changed(self):
        """Check if password field has changed"""
        if self.pk is None:
            return True
        try:
            old_instance = EmailConfiguration.objects.get(pk=self.pk)
            return old_instance.password != self.password
        except EmailConfiguration.DoesNotExist:
            return True
    
    def _get_encryption_key(self):
        """Get or generate encryption key"""
        # Try to get key from environment
        key = os.environ.get('EMAIL_ENCRYPTION_KEY')
        
        if not key:
            # Generate a new key if none exists
            # WARNING: This should be stored in .env in production
            key = Fernet.generate_key().decode()
            print(f"WARNING: Generated new encryption key. Add to .env: EMAIL_ENCRYPTION_KEY={key}")
        
        return key.encode() if isinstance(key, str) else key
    
    def _encrypt_password(self, raw_password):
        """Encrypt password for storage"""
        if not raw_password:
            return ''
        
        # Check if already encrypted (starts with 'gAAAAA')
        if raw_password.startswith('gAAAAA'):
            return raw_password
        
        try:
            key = self._get_encryption_key()
            cipher = Fernet(key)
            encrypted = cipher.encrypt(raw_password.encode())
            return encrypted.decode()
        except Exception as e:
            print(f"Encryption error: {e}")
            return raw_password
    
    def get_decrypted_password(self):
        """Decrypt password for use"""
        if not self.password:
            return ''
        
        try:
            key = self._get_encryption_key()
            cipher = Fernet(key)
            decrypted = cipher.decrypt(self.password.encode())
            return decrypted.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            # Return as-is if decryption fails (might be plain text in dev)
            return self.password
    
    @classmethod
    def get_provider_defaults(cls, provider):
        """Get default settings for common providers"""
        defaults = {
            'gmail': {
                'host': 'smtp.gmail.com',
                'port': 587,
                'use_tls': True,
                'use_ssl': False,
            },
            'sendgrid': {
                'host': 'smtp.sendgrid.net',
                'port': 587,
                'use_tls': True,
                'use_ssl': False,
            },
            'microsoft365': {
                'host': 'smtp-mail.outlook.com',
                'port': 587,
                'use_tls': True,
                'use_ssl': False,
            },
            'custom': {
                'host': '',
                'port': 587,
                'use_tls': True,
                'use_ssl': False,
            },
        }
        return defaults.get(provider, defaults['custom'])

# Create your models here.
