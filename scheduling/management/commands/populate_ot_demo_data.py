"""
Management command to populate demo OT preference data for testing the Intelligent OT Distribution system.

Usage:
    python manage.py populate_ot_demo_data --staff-count 15
"""

from django.core.management.base import BaseCommand
import random

from scheduling.models import User
from scheduling.models_multi_home import CareHome
from scheduling.models_overtime import StaffOvertimePreference


class Command(BaseCommand):
    help = 'Populate demo OT preference data for testing Intelligent OT Distribution'

    def add_arguments(self, parser):
        parser.add_argument(
            '--staff-count',
            type=int,
            default=15,
            help='Number of staff to create OT preferences for'
        )

    def handle(self, *args, **options):
        staff_count = options['staff_count']
        
        # Get all active users
        all_staff = list(User.objects.filter(is_active=True).select_related('role', 'unit')[:staff_count])
        
        if len(all_staff) < staff_count:
            self.stdout.write(self.style.WARNING(
                f'Only {len(all_staff)} active staff found (requested {staff_count})'
            ))
        
        # Get all care homes for preference assignment
        homes = list(CareHome.objects.all())
        
        if not homes:
            self.stdout.write(self.style.ERROR('No care homes found. Please create homes first.'))
            return
        
        self.stdout.write(f'Creating OT preferences for {len(all_staff)} staff...')
        
        # Create OT preferences
        preferences_created = 0
        for staff in all_staff:
            # 70% available, 30% not available
            available_for_overtime = random.random() < 0.7
            
            # Create preference
            pref, created = StaffOvertimePreference.objects.get_or_create(
                staff=staff,
                defaults={'available_for_overtime': available_for_overtime}
            )
            
            if created:
                preferences_created += 1
                
                # Assign willing_to_work_at (preferred homes)
                home_preference_type = random.random()
                if home_preference_type < 0.5:
                    # 50% prefer all homes (no preference set - willing to work anywhere)
                    # Add all units from all homes
                    all_units = []
                    for home in homes:
                        all_units.extend(home.units.all())
                    if all_units:
                        pref.willing_to_work_at.add(*all_units)
                elif home_preference_type < 0.8:
                    # 30% prefer one specific home's units
                    selected_home = random.choice(homes)
                    pref.willing_to_work_at.add(*selected_home.units.all())
                else:
                    # 20% prefer two homes' units
                    selected_homes = random.sample(homes, min(2, len(homes)))
                    for home in selected_homes:
                        pref.willing_to_work_at.add(*home.units.all())
        
        self.stdout.write(self.style.SUCCESS(
            f'✓ Created {preferences_created} new OT preferences'
        ))
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('DEMO DATA POPULATION COMPLETE'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'Staff with OT preferences: {len(all_staff)}')
        self.stdout.write(self.style.SUCCESS('\nYou can now test the OT Intelligence system at:'))
        self.stdout.write(self.style.SUCCESS('  http://127.0.0.1:8000/ot-intelligence/'))
