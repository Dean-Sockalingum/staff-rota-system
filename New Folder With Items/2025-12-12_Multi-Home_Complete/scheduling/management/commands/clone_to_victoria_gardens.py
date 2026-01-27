"""
Clone Orchard Grove's rota pattern to Victoria Gardens
Scales the pattern based on Victoria Gardens' staffing levels
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import Shift, Unit, CareHome, User, ShiftType
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Clone Orchard Grove rota pattern to Victoria Gardens'

    def add_arguments(self, parser):
        parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)', default='2025-12-15')
        parser.add_argument('--days', type=int, help='Number of days to clone', default=7)
        parser.add_argument('--clear', action='store_true', help='Clear existing Victoria Gardens shifts first')

    @transaction.atomic
    def handle(self, *args, **options):
        start_date = datetime.strptime(options['start_date'], '%Y-%m-%d').date()
        days = options['days']
        clear = options['clear']
        
        # Get care homes
        orchard_grove = CareHome.objects.get(name='ORCHARD_GROVE')
        victoria_gardens = CareHome.objects.get(name='VICTORIA_GARDENS')
        
        # Get units
        og_units = Unit.objects.filter(care_home=orchard_grove, is_active=True).exclude(name__icontains='MGMT')
        vg_units = Unit.objects.filter(care_home=victoria_gardens, is_active=True).exclude(name__icontains='MGMT')
        
        self.stdout.write(f"Orchard Grove units: {og_units.count()}")
        self.stdout.write(f"Victoria Gardens units: {vg_units.count()}")
        
        # Get staff by role for both homes
        og_staff = {
            'SSCW': list(User.objects.filter(unit__in=og_units, role__name='SSCW', is_active=True)),
            'SCW': list(User.objects.filter(unit__in=og_units, role__name='SCW', is_active=True)),
            'SCA': list(User.objects.filter(unit__in=og_units, role__name='SCA', is_active=True)),
            'SSCWN': list(User.objects.filter(unit__in=og_units, role__name='SSCWN', is_active=True)),
            'SCWN': list(User.objects.filter(unit__in=og_units, role__name='SCWN', is_active=True)),
            'SCAN': list(User.objects.filter(unit__in=og_units, role__name='SCAN', is_active=True)),
        }
        
        vg_staff = {
            'SSCW': list(User.objects.filter(unit__in=vg_units, role__name='SSCW', is_active=True)),
            'SCW': list(User.objects.filter(unit__in=vg_units, role__name='SCW', is_active=True)),
            'SCA': list(User.objects.filter(unit__in=vg_units, role__name='SCA', is_active=True)),
            'SSCWN': list(User.objects.filter(unit__in=vg_units, role__name='SSCWN', is_active=True)),
            'SCWN': list(User.objects.filter(unit__in=vg_units, role__name='SCWN', is_active=True)),
            'SCAN': list(User.objects.filter(unit__in=vg_units, role__name='SCAN', is_active=True)),
            'SM': list(User.objects.filter(unit__in=vg_units, role__name='SM', is_active=True)),
            'OM': list(User.objects.filter(unit__in=vg_units, role__name='OM', is_active=True)),
        }
        
        self.stdout.write("\nStaff counts:")
        for role, staff_list in vg_staff.items():
            self.stdout.write(f"  VG {role}: {len(staff_list)}")
        
        # Clear existing shifts if requested
        if clear:
            deleted = Shift.objects.filter(unit__in=vg_units, date__gte=start_date).delete()
            self.stdout.write(self.style.WARNING(f"Cleared {deleted[0]} existing shifts"))
        
        # Get shift types
        shift_types = {st.name: st for st in ShiftType.objects.all()}
        
        # Clone shifts for each day
        shifts_created = 0
        vg_unit_list = list(vg_units)
        
        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)
            
            # Get Orchard Grove shifts for this date
            og_shifts = Shift.objects.filter(
                unit__in=og_units,
                date=current_date,
                status__in=['SCHEDULED', 'CONFIRMED']
            ).select_related('shift_type', 'user', 'user__role')
            
            # Count shifts by role and type
            shift_pattern = {}
            for shift in og_shifts:
                role = shift.user.role.name
                shift_type = shift.shift_type.name
                key = f"{shift_type}_{role}"
                shift_pattern[key] = shift_pattern.get(key, 0) + 1
            
            self.stdout.write(f"\n{current_date} - Orchard Grove pattern:")
            for key, count in sorted(shift_pattern.items()):
                self.stdout.write(f"  {key}: {count}")
            
            # Create Victoria Gardens shifts using the pattern
            # Scale down proportionally based on staff availability
            staff_counters = {role: 0 for role in vg_staff.keys()}
            
            for key, og_count in shift_pattern.items():
                parts = key.rsplit('_', 1)
                if len(parts) == 2:
                    shift_type_name, role = parts
                else:
                    continue
                
                # Calculate scaled count for Victoria Gardens
                # VG has ~56% of OG staff (98 vs 177), so scale proportionally
                vg_count = max(1, round(og_count * 0.6))  # Use 60% scaling
                
                # Get available staff for this role
                available_staff = vg_staff.get(role, [])
                if not available_staff:
                    self.stdout.write(self.style.WARNING(f"  No {role} staff available for {shift_type_name}"))
                    continue
                
                # Create shifts
                shift_type = shift_types.get(shift_type_name)
                if not shift_type:
                    self.stdout.write(self.style.WARNING(f"  Shift type {shift_type_name} not found"))
                    continue
                
                for i in range(min(vg_count, len(available_staff))):
                    staff_idx = staff_counters[role] % len(available_staff)
                    staff_member = available_staff[staff_idx]
                    unit_idx = shifts_created % len(vg_unit_list)
                    
                    Shift.objects.create(
                        user=staff_member,
                        unit=vg_unit_list[unit_idx],
                        shift_type=shift_type,
                        date=current_date,
                        status='SCHEDULED'
                    )
                    
                    shifts_created += 1
                    staff_counters[role] += 1
            
            self.stdout.write(f"  Created {shifts_created} shifts so far")
        
        self.stdout.write(self.style.SUCCESS(f"\nTotal shifts created: {shifts_created}"))
        
        # Verify coverage
        vg_shifts = Shift.objects.filter(
            unit__in=vg_units,
            date__gte=start_date,
            date__lt=start_date + timedelta(days=days)
        )
        self.stdout.write(f"Victoria Gardens now has {vg_shifts.count()} shifts")
