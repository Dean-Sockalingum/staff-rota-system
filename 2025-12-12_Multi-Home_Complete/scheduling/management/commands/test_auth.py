from django.core.management.base import BaseCommand
from scheduling.models import User, Role
from django.contrib.auth import authenticate

class Command(BaseCommand):
    help = 'Test and fix user authentication'

    def handle(self, *args, **options):
        self.stdout.write('🔍 USER AUTHENTICATION TEST')
        self.stdout.write('=' * 50)

        # Find management users to test
        try:
            mgmt_roles = Role.objects.filter(name__in=['ADMIN', 'SM', 'OM'])
            self.stdout.write(f'Found {mgmt_roles.count()} management roles')
            
            mgmt_users = User.objects.filter(role__in=mgmt_roles, is_active=True)[:5]
            
            working_logins = []
            
            for user in mgmt_users:
                self.stdout.write(f'\n👤 Testing user: {user.sap}')
                self.stdout.write(f'   Name: {user.first_name} {user.last_name}')
                self.stdout.write(f'   Role: {user.role.get_name_display() if user.role else "No Role"}')
                self.stdout.write(f'   Active: {user.is_active}')
                
                # Test password
                password_check = user.check_password('staff123')
                self.stdout.write(f'   Password check: {"✅ PASS" if password_check else "❌ FAIL"}')
                
                # If password is wrong, fix it
                if not password_check:
                    user.set_password('staff123')
                    user.save()
                    self.stdout.write(f'   🔧 Password reset to staff123')
                    password_check = True
                
                # Test authentication
                auth_test = authenticate(username=user.sap, password='staff123')
                self.stdout.write(f'   Auth test: {"✅ SUCCESS" if auth_test else "❌ FAILED"}')
                
                if auth_test:
                    working_logins.append(user.sap)
            
            self.stdout.write('\n🎯 WORKING LOGIN CREDENTIALS:')
            if working_logins:
                for sap in working_logins:
                    self.stdout.write(f'   SAP: {sap}')
                    self.stdout.write(f'   Password: staff123')
                    self.stdout.write(f'   URL: http://127.0.0.1:8004/')
                    break  # Just show the first working one
            else:
                self.stdout.write('   ❌ No working logins found')
                
                # Create a guaranteed working admin user
                self.stdout.write('\n🔧 Creating guaranteed admin user...')
                admin_role = Role.objects.filter(name='ADMIN').first()
                if admin_role:
                    # Delete existing TEST001 if it exists
                    User.objects.filter(sap='TEST001').delete()
                    
                    test_user = User.objects.create_user(
                        sap='TEST001',
                        username='TEST001',
                        first_name='Test',
                        last_name='Admin',
                        role=admin_role,
                        email='test@example.com',
                        is_active=True
                    )
                    test_user.set_password('staff123')
                    test_user.save()
                    
                    # Verify it works
                    auth_test = authenticate(username='TEST001', password='staff123')
                    if auth_test:
                        self.stdout.write('✅ Emergency admin created successfully!')
                        self.stdout.write('   SAP: TEST001')
                        self.stdout.write('   Password: staff123')
                        self.stdout.write('   URL: http://127.0.0.1:8004/')
                    else:
                        self.stdout.write('❌ Emergency admin creation failed')
                
        except Exception as e:
            self.stdout.write(f'❌ Error: {e}')
            import traceback
            self.stdout.write(traceback.format_exc())