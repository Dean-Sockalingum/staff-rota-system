"""
Reset passwords for Head of Service users
"""
from django.core.management.base import BaseCommand
from scheduling.models import User, Role


class Command(BaseCommand):
    help = 'Reset passwords for Head of Service team members (SM, OM, HOS, IDI)'

    def handle(self, *args, **options):
        # Get all roles with is_senior_management_team = 1
        hos_roles = Role.objects.filter(is_senior_management_team=True)
        
        # Get all users with those roles
        hos_users = User.objects.filter(role__in=hos_roles)
        
        self.stdout.write(self.style.WARNING(f'Found {hos_users.count()} Head of Service users'))
        
        # Reset password to "password" for each user
        password = "password"
        count = 0
        
        for user in hos_users:
            user.set_password(password)
            user.save()
            self.stdout.write(f'  ✓ Reset password for {user.sap} ({user.full_name}) - Role: {user.role.name}')
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully reset passwords for {count} users'))
        self.stdout.write(self.style.SUCCESS(f'Password: "{password}"'))
        self.stdout.write(self.style.SUCCESS('\nYou can now login with:'))
        self.stdout.write('  - SM0001 (Les Dorson)')
        self.stdout.write('  - OM0001 (Wyn Thomas)')
        self.stdout.write('  - OM0002 (Jessie Jones)')
