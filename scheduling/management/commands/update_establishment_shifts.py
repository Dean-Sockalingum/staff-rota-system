from django.core.management.base import BaseCommand
from scheduling.models import User
import random

class Command(BaseCommand):
    help = 'Update staff shift patterns to match new establishment requirements'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔧 UPDATING SHIFT PATTERNS TO MATCH ESTABLISHMENT'))
        self.stdout.write('=' * 70)
        
        # Target distributions from user's table
        targets = {
            ('SCA', 'night', 3): 34,
            ('SCA', 'night', 2): 32,
            ('SCA', 'day', 3): 28,
            ('SCA', 'day', 2): 22,
            ('SCW', 'night', 3): 7,
            ('SCW', 'night', 2): 8,
            ('SCW', 'day', 3): 9,
            ('SCW', 'day', 2): 18,
        }
        
        total_changes = 0
        
        for (role, shift_time, shifts), target_count in targets.items():
            shift_preferences = ['DAY_SENIOR', 'DAY_ASSISTANT'] if shift_time == 'day' else ['NIGHT_SENIOR', 'NIGHT_ASSISTANT']
            
            # Get current staff in this category
            current_staff = list(User.objects.filter(
                role__name=role,
                shift_preference__in=shift_preferences,
                is_active=True
            ).order_by('sap'))
            
            # Count current distribution
            current_3_shifts = [s for s in current_staff if s.shifts_per_week == 3]
            current_2_shifts = [s for s in current_staff if s.shifts_per_week == 2]
            
            current_count = len(current_3_shifts) if shifts == 3 else len(current_2_shifts)
            
            self.stdout.write(f'\n📋 {role} {shift_time.upper()} - {shifts} shifts/week:')
            self.stdout.write(f'   Current: {current_count} | Target: {target_count}')
            
            if current_count == target_count:
                self.stdout.write(f'   ✅ Already correct')
                continue
                
            difference = target_count - current_count
            
            if difference > 0:
                # Need to convert staff TO this shift pattern
                source_staff = current_2_shifts if shifts == 3 else current_3_shifts
                if len(source_staff) >= difference:
                    # Randomly select staff to convert
                    to_convert = random.sample(source_staff, difference)
                    for staff in to_convert:
                        staff.shifts_per_week_override = shifts
                        staff.save()
                        total_changes += 1
                        self.stdout.write(f'   ✅ {staff.sap}: {staff.shifts_per_week} → {shifts} shifts/week')
                else:
                    self.stdout.write(f'   ⚠️ Warning: Only {len(source_staff)} staff available to convert, need {difference}')
                    
            else:
                # Need to convert staff FROM this shift pattern  
                staff_to_convert = current_3_shifts if shifts == 3 else current_2_shifts
                target_shifts = 2 if shifts == 3 else 3
                
                to_convert = random.sample(staff_to_convert, min(abs(difference), len(staff_to_convert)))
                for staff in to_convert:
                    staff.shifts_per_week_override = target_shifts
                    staff.save()
                    total_changes += 1
                    self.stdout.write(f'   ✅ {staff.sap}: {staff.shifts_per_week} → {target_shifts} shifts/week')
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS(f'✅ ESTABLISHMENT UPDATE COMPLETE'))
        self.stdout.write(f'📊 Total staff shift changes: {total_changes}')
        
        # Verify final distribution
        self.stdout.write('\n🔍 FINAL VERIFICATION:')
        for (role, shift_time, shifts), target_count in targets.items():
            shift_preferences = ['DAY_SENIOR', 'DAY_ASSISTANT'] if shift_time == 'day' else ['NIGHT_SENIOR', 'NIGHT_ASSISTANT']
            
            final_count = User.objects.filter(
                role__name=role,
                shift_preference__in=shift_preferences,
                shifts_per_week_override=shifts,
                is_active=True
            ).count()
            
            # Also count those without override but with default shifts
            if shifts == 3:  # Default for SCW/SSCW
                no_override_count = User.objects.filter(
                    role__name=role,
                    shift_preference__in=shift_preferences,
                    shifts_per_week_override__isnull=True,
                    role__shifts_per_week=3,
                    is_active=True
                ).count()
                final_count += no_override_count
            
            status = '✅' if final_count == target_count else '⚠️'
            self.stdout.write(f'   {role} {shift_time} {shifts} shifts: {final_count}/{target_count} {status}')
        
        self.stdout.write('\n✅ Run generate_six_week_roster to apply changes to the rota!')