from django.core.management.base import BaseCommand
from scheduling.models import User, Role

class Command(BaseCommand):
    help = 'Reset admin password and verify settings'

    def handle(self, *args, **kwargs):
        try:
            user = User.objects.get(sap='ADMIN001')
            self.stdout.write(f'Found user: {user.sap} - {user.first_name} {user.last_name}')
            self.stdout.write(f'is_active: {user.is_active}')
            self.stdout.write(f'is_staff: {user.is_staff}')
            self.stdout.write(f'is_superuser: {user.is_superuser}')
            self.stdout.write(f'Role: {user.role}')
            
            # Ensure all flags are set correctly
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            user.set_password('admin')
            user.save()
            
            self.stdout.write(self.style.SUCCESS(f'✓ Password reset to "admin" for {user.sap}'))
            self.stdout.write(self.style.SUCCESS(f'✓ User flags updated'))
            
            # Test password
            if user.check_password('admin'):
                self.stdout.write(self.style.SUCCESS('✓ Password verification successful'))
            else:
                self.stdout.write(self.style.ERROR('✗ Password verification failed'))
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Admin user ADMIN001 not found'))
