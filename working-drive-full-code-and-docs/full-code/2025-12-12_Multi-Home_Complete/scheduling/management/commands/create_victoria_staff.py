"""
Management command to create Victoria Gardens staff.

Creates specific staffing complement:
- Management: 1 SM + 1 OM (day shift, 35 hours)
- Day shift: 6 SSCW (35hr), 8 SCW (35hr), 8 SCW (24hr), 15 SCA (35hr), 16 SCA (24hr)
- Night shift: 4 SSCWN (35hr), 9 SCAN (35hr), 19 SCAN (24hr), 4 SCWN (35hr), 7 SCWN (24hr)

Total: 92 staff members
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import User, Unit, Role
from scheduling.models_multi_home import CareHome
import re


class Command(BaseCommand):
    help = 'Create Victoria Gardens staff with specified complement'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("🏥 VICTORIA GARDENS STAFFING"))
        self.stdout.write("="*70 + "\n")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("🔍 DRY RUN MODE - No data will be created\n"))
        
        # Get Victoria Gardens
        try:
            victoria = CareHome.objects.get(name='VICTORIA_GARDENS')
        except CareHome.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Victoria Gardens not found"))
            return
        
        # Get management unit
        try:
            mgmt_unit = Unit.objects.get(name='VICTORIA_MGMT', care_home=victoria)
        except Unit.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ VICTORIA_MGMT unit not found"))
            return
        
        # Get care units (excluding MGMT)
        care_units = list(Unit.objects.filter(
            care_home=victoria,
            is_active=True
        ).exclude(name='VICTORIA_MGMT'))
        
        if len(care_units) != 5:
            self.stdout.write(self.style.WARNING(
                f"⚠️  Expected 5 care units, found {len(care_units)}"
            ))
        
        self.stdout.write(f"📊 Victoria Gardens: {victoria.bed_capacity} beds")
        self.stdout.write(f"   Units: {len(care_units)} care units + 1 management\n")
        
        # Get roles (using actual role codes from database)
        roles = {}
        role_codes = ['SM', 'OM', 'SSCW', 'SCW', 'SCA', 'SSCWN', 'SCWN', 'SCAN']
        
        for code in role_codes:
            try:
                roles[code] = Role.objects.get(name=code)
            except Role.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"⚠️  Role {code} not found, will skip staff with this role"
                ))
        
        # Find highest current SAP number
        all_saps = User.objects.filter(sap__isnull=False).values_list('sap', flat=True)
        numeric_saps = []
        for sap in all_saps:
            match = re.search(r'(\d+)$', sap)
            if match:
                numeric_saps.append(int(match.group(1)))
        
        next_sap_num = max(numeric_saps) + 1 if numeric_saps else 1693
        self.stdout.write(f"🔢 Starting SAP: SSCWN{next_sap_num:04d}\n")
        
        # Name lists
        first_names = [
            'Grace', 'David', 'Rose', 'Michael', 'Florence', 'Christopher', 'Ivy', 'Andrew',
            'Pearl', 'Stephen', 'Violet', 'Mark', 'Hazel', 'Paul', 'Iris', 'Kevin',
            'Marigold', 'Simon', 'Poppy', 'Colin', 'Jasmine', 'Brian', 'Heather', 'Graham',
            'Lily', 'Malcolm', 'Ruby', 'Derek', 'Amber', 'Keith', 'Crystal', 'Trevor',
            'Jade', 'Ian', 'Pearl', 'Adrian', 'Opal', 'Stuart', 'Coral', 'Neil',
            'Autumn', 'Philip', 'Summer', 'Barry', 'April', 'Nigel', 'May', 'Robin',
            'June', 'Gerald', 'Dawn', 'Roger', 'Faith', 'Clive', 'Hope', 'Dennis',
            'Joy', 'Raymond', 'Mercy', 'Norman', 'Patience', 'Maurice', 'Charity', 'Leonard',
            'Honor', 'Kenneth', 'Verity', 'Leslie', 'Grace', 'Gordon', 'Ruth', 'Douglas',
            'Esther', 'Ronald', 'Miriam', 'Terence', 'Rachel', 'Geoffrey', 'Leah', 'Peter',
            'Sarah', 'Anthony', 'Rebecca', 'Francis', 'Naomi', 'Clifford', 'Hannah', 'Albert',
            'Deborah', 'Walter', 'Judith', 'Roy'
        ]
        
        last_names = [
            'MacDonald', 'Stewart', 'Campbell', 'Robertson', 'Thomson', 'Anderson', 'Murray', 'Reid',
            'Ferguson', 'Grant', 'Morrison', 'Duncan', 'Hamilton', 'Graham', 'Johnston', 'Wallace',
            'Fraser', 'Ross', 'Henderson', 'Gibson', 'Burns', 'Kennedy', 'Russell', 'Crawford',
            'Mitchell', 'Hunter', 'Bell', 'Watson', 'Gordon', 'Simpson', 'Cameron', 'Shaw',
            'Hughes', 'Ellis', 'Bennett', 'Chapman', 'Coleman', 'Foster', 'Gray', 'Holland',
            'Howard', 'Marshall', 'Mason', 'Palmer', 'Richards', 'Simpson', 'Stevens', 'Webb',
            'Wells', 'West', 'Woods', 'Barnes', 'Fisher', 'Harper', 'Hayes', 'Hudson',
            'Mills', 'Palmer', 'Stone', 'Walsh', 'Boyd', 'Craig', 'Dunn', 'Fleming',
            'Hart', 'Kerr', 'Maxwell', 'Morrison', 'Muir', 'Paterson', 'Quinn', 'Sutherland'
        ]
        
        # Staffing structure
        staffing = [
            # Management (day shift)
            {'role': 'SM', 'count': 1, 'shift': 'DAY', 'hours': 35, 'unit_type': 'mgmt'},
            {'role': 'OM', 'count': 1, 'shift': 'DAY', 'hours': 35, 'unit_type': 'mgmt'},
            
            # Day shift
            {'role': 'SSCW', 'count': 6, 'shift': 'DAY', 'hours': 35, 'unit_type': 'care'},
            {'role': 'SCW', 'count': 8, 'shift': 'DAY', 'hours': 35, 'unit_type': 'care'},
            {'role': 'SCW', 'count': 8, 'shift': 'DAY', 'hours': 24, 'unit_type': 'care'},
            {'role': 'SCA', 'count': 15, 'shift': 'DAY', 'hours': 35, 'unit_type': 'care'},
            {'role': 'SCA', 'count': 16, 'shift': 'DAY', 'hours': 24, 'unit_type': 'care'},
            
            # Night shift
            {'role': 'SSCWN', 'count': 4, 'shift': 'NIGHT', 'hours': 35, 'unit_type': 'care'},
            {'role': 'SCAN', 'count': 9, 'shift': 'NIGHT', 'hours': 35, 'unit_type': 'care'},
            {'role': 'SCAN', 'count': 19, 'shift': 'NIGHT', 'hours': 24, 'unit_type': 'care'},
            {'role': 'SCWN', 'count': 4, 'shift': 'NIGHT', 'hours': 35, 'unit_type': 'care'},
            {'role': 'SCWN', 'count': 7, 'shift': 'NIGHT', 'hours': 24, 'unit_type': 'care'},
        ]
        
        name_counter = 0
        created_count = 0
        staff_breakdown = {}
        
        try:
            with transaction.atomic():
                for staff_group in staffing:
                    role_code = staff_group['role']
                    count = staff_group['count']
                    shift = staff_group['shift']
                    hours = staff_group['hours']
                    unit_type = staff_group['unit_type']
                    
                    if role_code not in roles:
                        self.stdout.write(self.style.WARNING(
                            f"⚠️  Skipping {count} {role_code} staff (role not found)"
                        ))
                        continue
                    
                    role = roles[role_code]
                    
                    # Determine shift preference
                    if shift == 'DAY':
                        if role_code in ['SM', 'OM']:
                            shift_pref = 'DAY_SENIOR'
                        else:
                            shift_pref = 'DAY'
                    else:
                        shift_pref = 'NIGHT'
                    
                    # Determine unit assignment
                    if unit_type == 'mgmt':
                        target_unit = mgmt_unit
                    else:
                        # Distribute across care units
                        target_unit = care_units[created_count % len(care_units)]
                    
                    # Annual leave based on hours
                    if hours == 35:
                        annual_leave = 35  # Full time: 35 days
                    else:
                        annual_leave = 24  # Part time: 24 days
                    
                    # Create staff members
                    for i in range(count):
                        first_name = first_names[name_counter % len(first_names)]
                        last_name = last_names[name_counter % len(last_names)]
                        name_counter += 1
                        
                        email = f"{first_name.lower()}.{last_name.lower()}.{next_sap_num}@example.com"
                        sap = f"SSCWN{next_sap_num:04d}"
                        next_sap_num += 1
                        
                        if not dry_run:
                            new_user = User.objects.create(
                                first_name=first_name,
                                last_name=last_name,
                                sap=sap,
                                email=email,
                                unit=target_unit,
                                role=role,
                                team='A',  # Default to Team A
                                shift_preference=shift_pref,
                                annual_leave_allowance=annual_leave,
                                annual_leave_used=0,
                                shifts_per_week_override=None,
                                is_active=True,
                                phone_number=f"07{next_sap_num:09d}"[-11:],
                            )
                            new_user.set_password('changeme123')
                            new_user.save()
                        
                        created_count += 1
                        
                        # Track breakdown
                        key = f"{role_code} ({hours}hr) - {shift}"
                        staff_breakdown[key] = staff_breakdown.get(key, 0) + 1
                        
                        # Rotate to next care unit for next staff member
                        if unit_type == 'care' and len(care_units) > 0:
                            target_unit = care_units[created_count % len(care_units)]
                
                if dry_run:
                    raise Exception("Dry run - rolling back")
        
        except Exception as e:
            if str(e) != "Dry run - rolling back":
                raise
        
        # Display results
        self.stdout.write(f"\n{'='*70}")
        if dry_run:
            self.stdout.write("Would create:")
        else:
            self.stdout.write(self.style.SUCCESS("✅ Created:"))
        self.stdout.write(f"{'='*70}\n")
        
        # Group by shift
        day_staff = {k: v for k, v in staff_breakdown.items() if 'DAY' in k}
        night_staff = {k: v for k, v in staff_breakdown.items() if 'NIGHT' in k}
        
        self.stdout.write("☀️  DAY SHIFT:")
        for role_desc, count in sorted(day_staff.items()):
            self.stdout.write(f"   • {role_desc:30} {count:3} staff")
        
        day_total = sum(day_staff.values())
        self.stdout.write(f"   {'─'*50}")
        self.stdout.write(f"   {'Day shift total':30} {day_total:3} staff\n")
        
        self.stdout.write("🌙 NIGHT SHIFT:")
        for role_desc, count in sorted(night_staff.items()):
            self.stdout.write(f"   • {role_desc:30} {count:3} staff")
        
        night_total = sum(night_staff.values())
        self.stdout.write(f"   {'─'*50}")
        self.stdout.write(f"   {'Night shift total':30} {night_total:3} staff\n")
        
        # Summary
        self.stdout.write(f"{'='*70}")
        self.stdout.write(self.style.SUCCESS("📊 SUMMARY"))
        self.stdout.write(f"{'='*70}")
        if dry_run:
            self.stdout.write(f"Would create: {created_count} staff members")
            self.stdout.write(f"Next SAP: SSCWN{next_sap_num:04d}")
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ Created: {created_count} staff members"))
            self.stdout.write(f"SAP range: SSCWN{next_sap_num-created_count:04d} - SSCWN{next_sap_num-1:04d}")
            self.stdout.write(f"Next available SAP: SSCWN{next_sap_num:04d}")
        
        self.stdout.write(f"Day staff: {day_total}")
        self.stdout.write(f"Night staff: {night_total}")
        self.stdout.write(f"Total: {created_count}")
        self.stdout.write(f"\n{'='*70}\n")
