"""
Management command to clone Orchard Grove staff to new homes.

Creates identical staff structure for Meadowburn, Hawthorn House, and Riverside.
Each home gets the same roles, units, and team structure as Orchard Grove.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import User, Unit, ShiftType
from scheduling.models_multi_home import CareHome
import re


class Command(BaseCommand):
    help = 'Clone Orchard Grove staff to Meadowburn, Hawthorn House, and Riverside'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("🏥 CLONE STAFF TO NEW HOMES"))
        self.stdout.write("="*70 + "\n")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("🔍 DRY RUN MODE - No data will be created\n"))
        
        # Get source and target homes
        try:
            orchard_grove = CareHome.objects.get(name='ORCHARD_GROVE')
            meadowburn = CareHome.objects.get(name='MEADOWBURN')
            hawthorn = CareHome.objects.get(name='HAWTHORN_HOUSE')
            riverside = CareHome.objects.get(name='RIVERSIDE')
        except CareHome.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
            return
        
        target_homes = [
            (meadowburn, 'Meadowburn', 'MEADOW'),
            (hawthorn, 'Hawthorn House', 'HAWTHORN'),
            (riverside, 'Riverside', 'RIVERSIDE'),
        ]
        
        # Get Orchard Grove staff
        og_staff = User.objects.filter(
            unit__care_home=orchard_grove,
            is_active=True
        ).select_related('unit', 'role').order_by('unit__name', 'last_name')
        
        total_og_staff = og_staff.count()
        self.stdout.write(f"📊 Source: {orchard_grove.get_name_display()}")
        self.stdout.write(f"   Staff count: {total_og_staff}\n")
        
        # Get unit mapping for Orchard Grove
        og_units = Unit.objects.filter(care_home=orchard_grove, is_active=True)
        
        # Find highest current SAP number
        all_saps = User.objects.filter(sap__isnull=False).values_list('sap', flat=True)
        numeric_saps = []
        for sap in all_saps:
            match = re.search(r'(\d+)$', sap)
            if match:
                numeric_saps.append(int(match.group(1)))
        
        next_sap_num = max(numeric_saps) + 1 if numeric_saps else 1162
        self.stdout.write(f"🔢 Starting SAP number: SSCWN{next_sap_num:04d}\n")
        
        # Unit name mapping
        unit_mappings = {
            'DEMENTIA': {
                'MEADOW': 'MEADOW_RED',
                'HAWTHORN': 'HAWTHORN_AMBER',
                'RIVERSIDE': 'RIVERSIDE_NORTH1'
            },
            'BLUE': {
                'MEADOW': 'MEADOW_BLUE',
                'HAWTHORN': 'HAWTHORN_BIRCH',
                'RIVERSIDE': 'RIVERSIDE_NORTH2'
            },
            'GREEN': {
                'MEADOW': 'MEADOW_GREEN',
                'HAWTHORN': 'HAWTHORN_CEDAR',
                'RIVERSIDE': 'RIVERSIDE_NORTH3'
            },
            'ROSE': {
                'MEADOW': 'MEADOW_YELLOW',
                'HAWTHORN': 'HAWTHORN_ELDER',
                'RIVERSIDE': 'RIVERSIDE_SOUTH1'
            },
            'VIOLET': {
                'MEADOW': 'MEADOW_PURPLE',
                'HAWTHORN': 'HAWTHORN_HOLLY',
                'RIVERSIDE': 'RIVERSIDE_SOUTH2'
            },
            'ORANGE': {
                'MEADOW': 'MEADOW_ORANGE',
                'HAWTHORN': 'HAWTHORN_MAPLE',
                'RIVERSIDE': 'RIVERSIDE_SOUTH3'
            },
            'PEACH': {
                'MEADOW': 'MEADOW_PINK',
                'HAWTHORN': 'HAWTHORN_OAK',
                'RIVERSIDE': 'RIVERSIDE_EAST'
            },
            'GRAPE': {
                'MEADOW': 'MEADOW_WHITE',
                'HAWTHORN': 'HAWTHORN_WILLOW',
                'RIVERSIDE': 'RIVERSIDE_WEST'
            },
            'MGMT': {
                'MEADOW': 'MEADOW_MGMT',
                'HAWTHORN': 'HAWTHORN_MGMT',
                'RIVERSIDE': 'RIVERSIDE_MGMT'
            }
        }
        
        # Fictional name generator
        first_names = [
            'Emma', 'James', 'Olivia', 'William', 'Ava', 'Oliver', 'Isabella', 'George',
            'Sophia', 'Jack', 'Mia', 'Harry', 'Amelia', 'Noah', 'Charlotte', 'Leo',
            'Harper', 'Oscar', 'Evelyn', 'Charlie', 'Abigail', 'Jacob', 'Emily', 'Thomas',
            'Elizabeth', 'Henry', 'Ella', 'Alfie', 'Scarlett', 'Freddie', 'Grace', 'Archie',
            'Lily', 'Joshua', 'Chloe', 'Arthur', 'Ellie', 'Theo', 'Isla', 'Alexander',
            'Sophie', 'Lucas', 'Freya', 'Max', 'Maisie', 'Isaac', 'Hannah', 'Benjamin',
            'Poppy', 'Sebastian', 'Lucy', 'Muhammad', 'Evie', 'Edward', 'Daisy', 'Dylan',
            'Ruby', 'Daniel', 'Phoebe', 'Samuel'
        ]
        
        last_names = [
            'Smith', 'Jones', 'Taylor', 'Brown', 'Williams', 'Wilson', 'Johnson', 'Davies',
            'Patel', 'Robinson', 'Wright', 'Thompson', 'Evans', 'Walker', 'White', 'Roberts',
            'Green', 'Hall', 'Wood', 'Jackson', 'Clarke', 'Harris', 'Lewis', 'Martin',
            'Cooper', 'King', 'Lee', 'Baker', 'Harrison', 'Morgan', 'Hughes', 'Edwards',
            'Hill', 'Moore', 'Clark', 'Watson', 'Scott', 'Young', 'Mitchell', 'Carter',
            'Phillips', 'Turner', 'Campbell', 'Anderson', 'Allen', 'Cook', 'Bailey', 'Murphy',
            'Miller', 'Davis', 'Khan', 'Ahmed', 'Ali', 'Singh', 'Kumar', 'Shah',
            'Rahman', 'Hussain', 'Khan', 'Begum'
        ]
        
        # Create staff for each target home
        total_created = 0
        name_counter = 0
        
        for target_home, home_display_name, home_prefix in target_homes:
            self.stdout.write(f"\n{'='*70}")
            self.stdout.write(f"🏠 {home_display_name}")
            self.stdout.write(f"{'='*70}")
            
            created_count = 0
            unit_counts = {}
            
            try:
                with transaction.atomic():
                    for og_staff_member in og_staff:
                        # Get the corresponding unit in the target home
                        og_unit_name = og_staff_member.unit.name
                    
                        target_unit_name = unit_mappings.get(og_unit_name, {}).get(home_prefix)
                        if not target_unit_name:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"⚠️  No mapping for unit {og_unit_name} to {home_prefix}"
                                )
                            )
                            continue
                        
                        try:
                            target_unit = Unit.objects.get(
                                name=target_unit_name,
                                care_home=target_home
                            )
                        except Unit.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"⚠️  Unit {target_unit_name} not found in {home_display_name}"
                                )
                            )
                            continue
                        
                        # Generate fictional name
                        first_name = first_names[name_counter % len(first_names)]
                        last_name = last_names[name_counter % len(last_names)]
                        name_counter += 1
                        
                        # Generate email (used as username)
                        email = f"{first_name.lower()}.{last_name.lower()}.{next_sap_num}@example.com"
                        
                        # Generate SAP number
                        sap = f"SSCWN{next_sap_num:04d}"
                        next_sap_num += 1
                        
                        if not dry_run:
                            # Create the new user
                            new_user = User.objects.create(
                                first_name=first_name,
                                last_name=last_name,
                                sap=sap,
                                email=email,
                                unit=target_unit,
                                role=og_staff_member.role,
                                team=og_staff_member.team,
                                shift_preference=og_staff_member.shift_preference,
                                annual_leave_allowance=og_staff_member.annual_leave_allowance,
                                annual_leave_used=0,  # Start fresh
                                shifts_per_week_override=og_staff_member.shifts_per_week_override,
                                is_active=True,
                                phone_number=f"07{next_sap_num:09d}"[-11:],  # Fake UK mobile
                            )
                            new_user.set_password('changeme123')
                            new_user.save()
                        
                        created_count += 1
                        unit_counts[target_unit_name] = unit_counts.get(target_unit_name, 0) + 1
                    
                    if dry_run:
                        raise Exception("Dry run - rolling back")
            except Exception as e:
                if str(e) != "Dry run - rolling back":
                    raise
            
            if dry_run:
                self.stdout.write(f"   Would create: {created_count} staff members")
            else:
                self.stdout.write(self.style.SUCCESS(f"   ✅ Created: {created_count} staff members"))
            
            # Show breakdown by unit
            self.stdout.write(f"\n   📋 Staff by unit:")
            for unit_name, count in sorted(unit_counts.items()):
                self.stdout.write(f"      • {unit_name}: {count} staff")
            
            total_created += created_count
        
        # Summary
        self.stdout.write(f"\n{'='*70}")
        self.stdout.write(self.style.SUCCESS("📊 SUMMARY"))
        self.stdout.write(f"{'='*70}")
        self.stdout.write(f"Source home: Orchard Grove ({total_og_staff} staff)")
        self.stdout.write(f"Target homes: 3 (Meadowburn, Hawthorn House, Riverside)")
        if dry_run:
            self.stdout.write(f"Would create: {total_created} new staff members")
            self.stdout.write(f"Next SAP would be: SSCWN{next_sap_num:04d}")
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ Created: {total_created} new staff members"))
            self.stdout.write(f"Final SAP: SSCWN{next_sap_num-1:04d}")
            self.stdout.write(f"Next available SAP: SSCWN{next_sap_num:04d}")
        
        self.stdout.write("\n" + "="*70 + "\n")
