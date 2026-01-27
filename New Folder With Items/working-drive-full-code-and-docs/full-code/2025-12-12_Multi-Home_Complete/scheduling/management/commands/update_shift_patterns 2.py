from django.core.management.base import BaseCommand
from scheduling.models import User
import random

class Command(BaseCommand):
    help = 'Update staff shift patterns to match new establishment'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔄 UPDATING SHIFT PATTERNS TO MATCH NEW ESTABLISHMENT'))
        
        # Target distribution based on user's data
        target_distribution = {
            'SSCW': {3: 17},  # All SSCW have 3 shifts
            'SCW': {3: 9, 2: 26},  # 9 with 3 shifts, 26 with 2 shifts  
            'SCA': {3: 42, 2: 85}  # 42 with 3 shifts, 85 with 2 shifts
        }
        
        changes_made = 0
        
        for role_name, distribution in target_distribution.items():
            # Get all active staff for this role
            staff = list(User.objects.filter(role__name=role_name, is_active=True))
            
            self.stdout.write(f'\n📋 {role_name} Staff ({len(staff)} total):')
            
            # Track positions to assign
            assignments = []
            for shifts, count in distribution.items():
                assignments.extend([shifts] * count)
            
            # Shuffle to randomize assignment
            random.shuffle(assignments)
            
            # Assign shift patterns
            for i, user in enumerate(staff):
                if i < len(assignments):
                    new_shifts = assignments[i]
                    old_shifts = user.shifts_per_week
                    
                    # Set the override field
                    user.shifts_per_week_override = new_shifts
                    user.save()
                    
                    if old_shifts != new_shifts:
                        self.stdout.write(f'   {user.sap}: {old_shifts} → {new_shifts} shifts/week')
                        changes_made += 1
                    else:
                        self.stdout.write(f'   {user.sap}: {new_shifts} shifts/week (no change)')
        
        # Verify final distribution
        self.stdout.write(f'\n✅ UPDATED SHIFT PATTERNS')
        self.stdout.write(f'Changes made: {changes_made}')
        
        # Show final distribution
        for role_name in ['SSCW', 'SCW', 'SCA']:
            staff = User.objects.filter(role__name=role_name, is_active=True)
            
            patterns = {}
            for user in staff:
                shifts = user.shifts_per_week
                patterns[shifts] = patterns.get(shifts, 0) + 1
            
            self.stdout.write(f'\n{role_name} Final Distribution:')
            for shifts, count in sorted(patterns.items()):
                self.stdout.write(f'   {shifts} shifts/week: {count} staff')
                
        self.stdout.write(self.style.SUCCESS('\n🎯 SHIFT PATTERNS UPDATED TO MATCH ESTABLISHMENT DATA'))