from django.core.management.base import BaseCommand
from scheduling.models import Shift, ShiftType
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Verify night shift daily totals for 3-week pattern'

    def handle(self, *args, **options):
        # Get night shift types
        night_types = ShiftType.objects.filter(name__in=['NIGHT_SENIOR', 'NIGHT_ASSISTANT'])
        
        # Check first 3 weeks (21 days) to verify pattern
        start = date(2025, 11, 23)
        days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        
        expected = {
            'Week 1': [26, 26, 40, 27, 27, 28, 28],
            'Week 2': [27, 27, 27, 28, 41, 26, 26],
            'Week 3': [28, 28, 26, 26, 40, 27, 27],
        }
        
        all_match = True
        
        for week_num in range(3):
            week_name = f'Week {week_num + 1}'
            self.stdout.write(f'\n{week_name} Daily Totals:')
            self.stdout.write('=' * 60)
            
            week_start = week_num * 7
            week_match = True
            
            for day_num in range(7):
                i = week_start + day_num
                d = start + timedelta(days=i)
                count = Shift.objects.filter(date=d, shift_type__in=night_types).count()
                exp = expected[week_name][day_num]
                
                status = '✓' if count == exp else '✗'
                style = self.style.SUCCESS if count == exp else self.style.ERROR
                
                self.stdout.write(style(
                    f'{status} {days[day_num]} {d}: {count:2d} (expected {exp})'
                ))
                
                if count != exp:
                    week_match = False
                    all_match = False
            
            if week_match:
                self.stdout.write(self.style.SUCCESS(f'✓ {week_name} matches expected pattern!'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ {week_name} has discrepancies'))
        
        self.stdout.write('\n' + '=' * 60)
        if all_match:
            self.stdout.write(self.style.SUCCESS('✓ ALL 21 DAYS MATCH EXPECTED PATTERN! 100% ACCURACY'))
        else:
            self.stdout.write(self.style.ERROR('✗ Some days do not match expected pattern'))
