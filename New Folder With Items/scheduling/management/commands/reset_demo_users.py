from django.core.management.base import BaseCommand
from scheduling.models import Role, User

class Command(BaseCommand):
    help = 'Reset demo user passwords'

    def handle(self, *args, **options):
        self.stdout.write('Resetting demo user passwords...')
        
        # Reset manager user
        try:
            manager_role = Role.objects.get(name='OPERATIONS_MANAGER')
            manager_user, created = User.objects.get_or_create(
                sap='MGR001',
                defaults={
                    'first_name': 'John',
                    'last_name': 'Manager',
                    'email': 'manager@staffrota.com',
                    'role': manager_role,
                    'is_staff': True,
                    'annual_leave_allowance': 28,
                }
            )
            manager_user.set_password('manager123')
            manager_user.save()
            self.stdout.write(f'✓ Manager user: MGR001 / manager123')
            
            # Reset staff user
            staff_role = Role.objects.get(name='SCW')
            staff_user, created = User.objects.get_or_create(
                sap='SCW001',
                defaults={
                    'first_name': 'Alice',
                    'last_name': 'Johnson',
                    'email': 'alice@staffrota.com',
                    'role': staff_role,
                    'annual_leave_allowance': 28,
                }
            )
            staff_user.set_password('staff123')
            staff_user.save()
            self.stdout.write(f'✓ Staff user: SCW001 / staff123')
            
            # Reset admin user
            admin_role = Role.objects.get(name='ADMIN')
            admin_user, created = User.objects.get_or_create(
                sap='ADMIN001',
                defaults={
                    'first_name': 'System',
                    'last_name': 'Administrator',
                    'email': 'admin@staffrota.com',
                    'role': admin_role,
                    'is_staff': True,
                    'is_superuser': True,
                    'annual_leave_allowance': 28,
                }
            )
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'✓ Admin user: ADMIN001 / admin123')
            
            self.stdout.write(self.style.SUCCESS('Demo users reset successfully!'))
            self.stdout.write('You can now login with:')
            self.stdout.write('  Manager: MGR001 / manager123')
            self.stdout.write('  Staff: SCW001 / staff123') 
            self.stdout.write('  Admin: ADMIN001 / admin123')
            
        except Role.DoesNotExist:
            self.stdout.write(self.style.ERROR('Roles not found. Please run: python manage.py load_initial_data first'))