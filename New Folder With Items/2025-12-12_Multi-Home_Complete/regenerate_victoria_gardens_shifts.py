"""
Regenerate Victoria Gardens shifts using patterns from yesterday's setup.
Uses updated 6-digit SAP numbers (001253-001350).
"""

import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift, User, CareHome, ShiftType, Unit

def get_week_number(date, start_date):
    """Calculate which week (1-3) in the 3-week rotation cycle"""
    days_since_start = (date - start_date).days
    week_in_cycle = (days_since_start // 7) % 3
    return week_in_cycle + 1

def should_work_on_day(date, pattern, start_date):
    """Check if staff member should work on this date based on their pattern"""
    week_num = get_week_number(date, start_date)
    week_key = f'week{week_num}'
    
    # Convert Python's Monday=0 to Sunday=0
    day_of_week = (date.weekday() + 1) % 7
    
    return day_of_week in pattern.get(week_key, [])

def main():
    print("\n" + "="*80)
    print("VICTORIA GARDENS SHIFT REGENERATION")
    print("="*80)
    
    # Configuration
    start_date = datetime(2026, 1, 4).date()  # First Sunday in January 2026
    end_date = datetime(2027, 1, 3).date()    # 52 weeks later
    
    print(f"\nShift period: {start_date} to {end_date}")
    print(f"Total days: {(end_date - start_date).days + 1}")
    
    # Get Victoria Gardens
    vg = CareHome.objects.get(name='VICTORIA_GARDENS')
    print(f"\n✓ Victoria Gardens care home loaded")
    
    # Get units
    units = list(Unit.objects.filter(care_home=vg).order_by('name'))
    print(f"✓ {len(units)} units loaded: {', '.join([u.name for u in units])}")
    
    # Get shift types
    day_senior = ShiftType.objects.get(name='DAY_SENIOR')
    day_assistant = ShiftType.objects.get(name='DAY_ASSISTANT')
    night_senior = ShiftType.objects.get(name='NIGHT_SENIOR')
    night_assistant = ShiftType.objects.get(name='NIGHT_ASSISTANT')
    admin_shift = ShiftType.objects.get(name='ADMIN')
    
    print("\n✓ Shift types loaded")
    
    # Delete existing Victoria Gardens shifts
    existing_count = Shift.objects.filter(user__unit__care_home=vg).count()
    if existing_count > 0:
        print(f"\nDeleting {existing_count} existing Victoria Gardens shifts...")
        Shift.objects.filter(user__unit__care_home=vg).delete()
        print("✓ Old shifts deleted")
    
    # Define patterns using Sunday=0 numbering
    # Sun=0, Mon=1, Tue=2, Wed=3, Thu=4, Fri=5, Sat=6
    
    # SM/OM Patterns (Admin - Monday to Friday)
    SM_OM_PATTERN = {'week1': [1,2,3,4,5], 'week2': [1,2,3,4,5], 'week3': [1,2,3,4,5]}
    
    # SSCW Patterns (Day Senior) - 3 teams of 2
    SSCW_PATTERNS = {
        'TEAM_A': {'week1': [0,3,4], 'week2': [1,2,3], 'week3': [2,5,6]},  # Sun/Wed/Thu → Mon/Tue/Wed → Tue/Fri/Sat
        'TEAM_B': {'week1': [1,2,3], 'week2': [2,5,6], 'week3': [0,3,4]},  # Mon/Tue/Wed → Tue/Fri/Sat → Sun/Wed/Thu
        'TEAM_C': {'week1': [2,5,6], 'week2': [0,3,4], 'week3': [1,2,3]},  # Tue/Fri/Sat → Sun/Wed/Thu → Mon/Tue/Wed
    }
    
    # SSCWN Patterns (Night Senior) - 3 teams
    SSCWN_PATTERNS = {
        'TEAM_A': {'week1': [1,2,3], 'week2': [3,4,5], 'week3': [6,0,1]},  # Tue/Wed/Thu → Thu/Fri/Sat → Sun/Mon/Tue
        'TEAM_B': {'week1': [3,4,5], 'week2': [6,0,1], 'week3': [1,2,3]},  # Thu/Fri/Sat → Sun/Mon/Tue → Tue/Wed/Thu
        'TEAM_C': {'week1': [6,0,1], 'week2': [1,2,3], 'week3': [3,4,5]},  # Sun/Mon/Tue → Tue/Wed/Thu → Thu/Fri/Sat
    }
    
    # SCW Patterns (Day Assistant)
    SCW_35HR_PATTERNS = {
        'PATTERN_1': {'week1': [0,3,4], 'week2': [1,2,3], 'week3': [3,5,6]},  # Sun/Wed/Thu → Mon/Tue/Wed → Wed/Fri/Sat
        'PATTERN_2': {'week1': [1,2,3], 'week2': [3,5,6], 'week3': [0,3,4]},  # Mon/Tue/Wed → Wed/Fri/Sat → Sun/Wed/Thu
        'PATTERN_3': {'week1': [3,5,6], 'week2': [0,3,4], 'week3': [1,2,3]},  # Wed/Fri/Sat → Sun/Wed/Thu → Mon/Tue/Wed
        'PATTERN_4': {'week1': [1,2,3], 'week2': [2,5,6], 'week3': [0,3,4]},  # Mon/Tue/Wed → Tue/Fri/Sat → Sun/Wed/Thu (Kevin Wallace)
    }
    
    SCW_24HR_PATTERNS = {
        'PATTERN_1': {'week1': [5,6], 'week2': [0,4], 'week3': [1,2]},      # Fri/Sat → Sun/Thu → Mon/Tue
        'PATTERN_2': {'week1': [1,4], 'week2': [5,6], 'week3': [0,4]},      # Mon/Thu → Fri/Sat → Sun/Thu
        'PATTERN_3': {'week1': [1,2], 'week2': [5,6], 'week3': [0,4]},      # Mon/Tue → Fri/Sat → Sun/Thu
    }
    
    # SCWN Patterns (Night Assistant)
    SCWN_35HR_PATTERNS = {
        'PATTERN_1': {'week1': [2,3,4], 'week2': [4,5,6], 'week3': [0,1,2]},  # Tue/Wed/Thu → Thu/Fri/Sat → Sun/Mon/Tue
        'PATTERN_2': {'week1': [4,5,6], 'week2': [0,1,2], 'week3': [2,3,4]},  # Thu/Fri/Sat → Sun/Mon/Tue → Tue/Wed/Thu
        'PATTERN_3': {'week1': [0,1,2], 'week2': [2,3,4], 'week3': [4,5,6]},  # Sun/Mon/Tue → Tue/Wed/Thu → Thu/Fri/Sat
    }
    
    SCWN_24HR_PATTERNS = {
        'PATTERN_1': {'week1': [2,3], 'week2': [0,1], 'week3': [5,6]},  # Tue/Wed → Sun/Mon → Fri/Sat
        'PATTERN_2': {'week1': [5,6], 'week2': [0,1], 'week3': [2,3]},  # Fri/Sat → Sun/Mon → Tue/Wed
        'PATTERN_3': {'week1': [0,1], 'week2': [5,6], 'week3': [2,3]},  # Sun/Mon → Fri/Sat → Tue/Wed
    }
    
    # SCA Patterns (Day Assistant)
    SCA_35HR_PATTERNS = {
        'PATTERN_1': {'week1': [0,3,4], 'week2': [1,2,3], 'week3': [3,5,6]},  # Sun/Wed/Thu → Mon/Tue/Wed → Wed/Fri/Sat
        'PATTERN_2': {'week1': [1,2,3], 'week2': [4,5,6], 'week3': [0,3,4]},  # Mon/Tue/Wed → Thu/Fri/Sat → Sun/Wed/Thu
        'PATTERN_3': {'week1': [3,5,6], 'week2': [0,3,4], 'week3': [1,2,3]},  # Wed/Fri/Sat → Sun/Wed/Thu → Mon/Tue/Wed
    }
    
    SCA_24HR_PATTERNS = {
        'PATTERN_1': {'week1': [5,6], 'week2': [0,4], 'week3': [1,2]},  # Fri/Sat → Sun/Thu → Mon/Tue
        'PATTERN_2': {'week1': [1,2], 'week2': [5,6], 'week3': [0,4]},  # Mon/Tue → Fri/Sat → Sun/Thu
        'PATTERN_3': {'week1': [0,1], 'week2': [5,6], 'week3': [0,4]},  # Sun/Mon → Fri/Sat → Sun/Thu
    }
    
    # SCAN Patterns (Night Assistant)
    SCAN_35HR_PATTERNS = {
        'PATTERN_1': {'week1': [2,3,4], 'week2': [0,1,2], 'week3': [4,5,6]},  # Tue/Wed/Thu → Sun/Mon/Tue → Thu/Fri/Sat
        'PATTERN_2': {'week1': [0,1,2], 'week2': [4,5,6], 'week3': [2,3,4]},  # Sun/Mon/Tue → Thu/Fri/Sat → Tue/Wed/Thu
    }
    
    SCAN_24HR_PATTERNS = {
        'PATTERN_1': {'week1': [2,3], 'week2': [0,1], 'week3': [5,6]},  # Tue/Wed → Sun/Mon → Fri/Sat
        'PATTERN_2': {'week1': [5,6], 'week2': [0,1], 'week3': [2,3]},  # Fri/Sat → Sun/Mon → Tue/Wed
        'PATTERN_3': {'week1': [0,1], 'week2': [5,6], 'week3': [2,3]},  # Sun/Mon → Fri/Sat → Tue/Wed
    }
    
    # Staff assignments
    staff_patterns = {
        # SM/OM (Admin)
        '001253': ('SM', SM_OM_PATTERN, admin_shift),   # Grace MacDonald
        '001254': ('OM', SM_OM_PATTERN, admin_shift),   # David Stewart
        
        # SSCW (Day Senior) - 6 staff, 3 teams of 2
        '001255': ('SSCW', SSCW_PATTERNS['TEAM_A'], day_senior),  # Rose Campbell
        '001256': ('SSCW', SSCW_PATTERNS['TEAM_A'], day_senior),  # Michael Robertson
        '001257': ('SSCW', SSCW_PATTERNS['TEAM_B'], day_senior),  # Florence Thomson
        '001258': ('SSCW', SSCW_PATTERNS['TEAM_B'], day_senior),  # Christopher Anderson
        '001259': ('SSCW', SSCW_PATTERNS['TEAM_C'], day_senior),  # Ivy Murray
        '001260': ('SSCW', SSCW_PATTERNS['TEAM_C'], day_senior),  # Andrew Reid
        
        # SCW (Day Assistant) - 16 staff (8x35hr, 8x24hr)
        '001261': ('SCW', SCW_35HR_PATTERNS['PATTERN_1'], day_assistant),  # Pearl Ferguson
        '001262': ('SCW', SCW_35HR_PATTERNS['PATTERN_1'], day_assistant),  # Stephen Grant
        '001263': ('SCW', SCW_35HR_PATTERNS['PATTERN_1'], day_assistant),  # Violet Morrison
        '001264': ('SCW', SCW_35HR_PATTERNS['PATTERN_1'], day_assistant),  # Mark Duncan
        '001265': ('SCW', SCW_35HR_PATTERNS['PATTERN_2'], day_assistant),  # Hazel Hamilton
        '001266': ('SCW', SCW_35HR_PATTERNS['PATTERN_2'], day_assistant),  # Paul Graham
        '001267': ('SCW', SCW_35HR_PATTERNS['PATTERN_3'], day_assistant),  # Iris Johnston
        '001268': ('SCW', SCW_35HR_PATTERNS['PATTERN_4'], day_assistant),  # Kevin Wallace (special pattern)
        '001269': ('SCW', SCW_24HR_PATTERNS['PATTERN_1'], day_assistant),  # Marigold Fraser
        '001270': ('SCW', SCW_24HR_PATTERNS['PATTERN_1'], day_assistant),  # Simon Ross
        '001271': ('SCW', SCW_24HR_PATTERNS['PATTERN_1'], day_assistant),  # Poppy Henderson
        '001272': ('SCW', SCW_24HR_PATTERNS['PATTERN_1'], day_assistant),  # Colin Gibson
        '001273': ('SCW', SCW_24HR_PATTERNS['PATTERN_2'], day_assistant),  # Jasmine Burns
        '001274': ('SCW', SCW_24HR_PATTERNS['PATTERN_3'], day_assistant),  # Brian Kennedy
        '001275': ('SCW', SCW_24HR_PATTERNS['PATTERN_3'], day_assistant),  # Heather Russell
        '001276': ('SCW', SCW_24HR_PATTERNS['PATTERN_1'], day_assistant),  # Graham Crawford
        
        # SCA (Day Assistant) - 31 staff
        '001277': ('SCA', SCA_35HR_PATTERNS['PATTERN_1'], day_assistant),  # Lily Mitchell
        '001278': ('SCA', SCA_35HR_PATTERNS['PATTERN_1'], day_assistant),  # Malcolm Hunter (VG)
        '001279': ('SCA', SCA_35HR_PATTERNS['PATTERN_2'], day_assistant),  # Ruby Bell
        '001280': ('SCA', SCA_35HR_PATTERNS['PATTERN_2'], day_assistant),  # Derek Watson
        '001281': ('SCA', SCA_35HR_PATTERNS['PATTERN_3'], day_assistant),  # Amber Gordon
        '001282': ('SCA', SCA_35HR_PATTERNS['PATTERN_3'], day_assistant),  # Keith Simpson
        '001283': ('SCA', SCA_35HR_PATTERNS['PATTERN_2'], day_assistant),  # Crystal Cameron
        '001284': ('SCA', SCA_35HR_PATTERNS['PATTERN_3'], day_assistant),  # Trevor Shaw
        '001285': ('SCA', SCA_35HR_PATTERNS['PATTERN_1'], day_assistant),  # Jade Hughes
        '001286': ('SCA', SCA_35HR_PATTERNS['PATTERN_2'], day_assistant),  # Ian Ellis
        '001287': ('SCA', SCA_35HR_PATTERNS['PATTERN_3'], day_assistant),  # Pearl Bennett
        '001288': ('SCA', SCA_35HR_PATTERNS['PATTERN_1'], day_assistant),  # Adrian Chapman
        '001289': ('SCA', SCA_35HR_PATTERNS['PATTERN_3'], day_assistant),  # Opal Coleman
        '001290': ('SCA', SCA_35HR_PATTERNS['PATTERN_1'], day_assistant),  # Stuart Foster
        '001291': ('SCA', SCA_35HR_PATTERNS['PATTERN_3'], day_assistant),  # Coral Gray
        '001292': ('SCA', SCA_35HR_PATTERNS['PATTERN_2'], day_assistant),  # Neil Holland
        '001293': ('SCA', SCA_24HR_PATTERNS['PATTERN_1'], day_assistant),  # Autumn Howard
        '001294': ('SCA', SCA_24HR_PATTERNS['PATTERN_1'], day_assistant),  # Philip Marshall
        '001295': ('SCA', SCA_24HR_PATTERNS['PATTERN_1'], day_assistant),  # Summer Mason
        '001296': ('SCA', SCA_24HR_PATTERNS['PATTERN_2'], day_assistant),  # Barry Palmer
        '001297': ('SCA', SCA_24HR_PATTERNS['PATTERN_2'], day_assistant),  # April Richards
        '001298': ('SCA', SCA_24HR_PATTERNS['PATTERN_3'], day_assistant),  # Nigel Simpson
        '001299': ('SCA', SCA_24HR_PATTERNS['PATTERN_3'], day_assistant),  # May Stevens
        '001300': ('SCA', SCA_24HR_PATTERNS['PATTERN_3'], day_assistant),  # Robin Webb
        '001301': ('SCA', SCA_24HR_PATTERNS['PATTERN_1'], day_assistant),  # June Wells
        '001302': ('SCA', SCA_24HR_PATTERNS['PATTERN_1'], day_assistant),  # Gerald West
        '001303': ('SCA', SCA_24HR_PATTERNS['PATTERN_1'], day_assistant),  # Dawn Woods
        '001304': ('SCA', SCA_24HR_PATTERNS['PATTERN_2'], day_assistant),  # Roger Barnes
        '001305': ('SCA', SCA_24HR_PATTERNS['PATTERN_2'], day_assistant),  # Faith Fisher
        '001306': ('SCA', SCA_24HR_PATTERNS['PATTERN_3'], day_assistant),  # Clive Harper
        '001307': ('SCA', SCA_24HR_PATTERNS['PATTERN_3'], day_assistant),  # Hope Hayes
        
        # SSCWN (Night Senior) - 4 staff
        '001308': ('SSCWN', SSCWN_PATTERNS['TEAM_A'], night_senior),  # Dennis Hudson
        '001309': ('SSCWN', SSCWN_PATTERNS['TEAM_B'], night_senior),  # Joy Mills
        '001310': ('SSCWN', SSCWN_PATTERNS['TEAM_C'], night_senior),  # Raymond Palmer
        '001311': ('SSCWN', SSCWN_PATTERNS['TEAM_A'], night_senior),  # Mercy Stone
        
        # SCAN (Night Assistant) - 28 staff
        '001312': ('SCAN', SCAN_35HR_PATTERNS['PATTERN_1'], night_assistant),  # Norman Walsh
        '001313': ('SCAN', SCAN_35HR_PATTERNS['PATTERN_1'], night_assistant),  # Patience Boyd
        '001314': ('SCAN', SCAN_35HR_PATTERNS['PATTERN_1'], night_assistant),  # Maurice Craig
        '001315': ('SCAN', SCAN_35HR_PATTERNS['PATTERN_1'], night_assistant),  # Charity Dunn
        '001316': ('SCAN', SCAN_35HR_PATTERNS['PATTERN_1'], night_assistant),  # Leonard Fleming
        '001317': ('SCAN', SCAN_35HR_PATTERNS['PATTERN_1'], night_assistant),  # Honor Hart
        '001318': ('SCAN', SCAN_35HR_PATTERNS['PATTERN_2'], night_assistant),  # Kenneth Kerr
        '001319': ('SCAN', SCAN_35HR_PATTERNS['PATTERN_2'], night_assistant),  # Verity Maxwell
        '001320': ('SCAN', SCAN_35HR_PATTERNS['PATTERN_2'], night_assistant),  # Leslie Morrison
        '001321': ('SCAN', SCAN_35HR_PATTERNS['PATTERN_2'], night_assistant),  # Grace Muir
        '001322': ('SCAN', SCAN_35HR_PATTERNS['PATTERN_2'], night_assistant),  # Gordon Paterson
        '001323': ('SCAN', SCAN_35HR_PATTERNS['PATTERN_1'], night_assistant),  # Ruth Quinn
        '001324': ('SCAN', SCAN_35HR_PATTERNS['PATTERN_2'], night_assistant),  # Douglas Sutherland
        '001325': ('SCAN', SCAN_35HR_PATTERNS['PATTERN_2'], night_assistant),  # Esther MacDonald
        '001326': ('SCAN', SCAN_35HR_PATTERNS['PATTERN_2'], night_assistant),  # Ronald Stewart
        '001327': ('SCAN', SCAN_35HR_PATTERNS['PATTERN_1'], night_assistant),  # Miriam Campbell
        '001328': ('SCAN', SCAN_24HR_PATTERNS['PATTERN_1'], night_assistant),  # Terence Robertson
        '001329': ('SCAN', SCAN_24HR_PATTERNS['PATTERN_2'], night_assistant),  # Rachel Thomson
        '001330': ('SCAN', SCAN_24HR_PATTERNS['PATTERN_2'], night_assistant),  # Geoffrey Anderson
        '001331': ('SCAN', SCAN_24HR_PATTERNS['PATTERN_3'], night_assistant),  # Leah Murray
        '001332': ('SCAN', SCAN_24HR_PATTERNS['PATTERN_3'], night_assistant),  # Peter Reid
        '001333': ('SCAN', SCAN_24HR_PATTERNS['PATTERN_3'], night_assistant),  # Sarah Ferguson
        '001334': ('SCAN', SCAN_24HR_PATTERNS['PATTERN_2'], night_assistant),  # Anthony Grant
        '001335': ('SCAN', SCAN_24HR_PATTERNS['PATTERN_2'], night_assistant),  # Rebecca Morrison
        '001336': ('SCAN', SCAN_24HR_PATTERNS['PATTERN_3'], night_assistant),  # Francis Duncan
        '001337': ('SCAN', SCAN_24HR_PATTERNS['PATTERN_3'], night_assistant),  # Naomi Hamilton
        '001338': ('SCAN', SCAN_24HR_PATTERNS['PATTERN_1'], night_assistant),  # Clifford Graham
        '001339': ('SCAN', SCAN_24HR_PATTERNS['PATTERN_2'], night_assistant),  # Hannah Johnston
        
        # SCWN (Night Assistant) - 11 staff
        '001340': ('SCWN', SCWN_35HR_PATTERNS['PATTERN_1'], night_assistant),  # Albert Wallace
        '001341': ('SCWN', SCWN_35HR_PATTERNS['PATTERN_2'], night_assistant),  # Deborah Fraser
        '001342': ('SCWN', SCWN_35HR_PATTERNS['PATTERN_3'], night_assistant),  # Walter Ross
        '001343': ('SCWN', SCWN_35HR_PATTERNS['PATTERN_1'], night_assistant),  # Judith Henderson
        '001344': ('SCWN', SCWN_35HR_PATTERNS['PATTERN_2'], night_assistant),  # Roy Gibson
        '001345': ('SCWN', SCWN_24HR_PATTERNS['PATTERN_1'], night_assistant),  # Grace Burns
        '001346': ('SCWN', SCWN_24HR_PATTERNS['PATTERN_2'], night_assistant),  # David Kennedy
        '001347': ('SCWN', SCWN_24HR_PATTERNS['PATTERN_3'], night_assistant),  # Rose Russell
        '001348': ('SCWN', SCWN_24HR_PATTERNS['PATTERN_1'], night_assistant),  # Michael Crawford
        '001349': ('SCWN', SCWN_24HR_PATTERNS['PATTERN_2'], night_assistant),  # Florence Mitchell
        '001350': ('SCWN', SCWN_24HR_PATTERNS['PATTERN_3'], night_assistant),  # Christopher Hunter
    }
    
    print(f"\n✓ {len(staff_patterns)} staff patterns configured")
    
    # Generate shifts
    print("\nGenerating shifts...")
    total_shifts = 0
    role_counts = {}
    
    current_date = start_date
    while current_date <= end_date:
        for sap, (role, pattern, shift_type) in staff_patterns.items():
            if should_work_on_day(current_date, pattern, start_date):
                staff = User.objects.get(sap=sap)
                
                # Assign unit (distribute across units)
                unit = units[int(sap) % len(units)]
                
                Shift.objects.create(
                    user=staff,
                    date=current_date,
                    shift_type=shift_type,
                    unit=unit
                )
                
                total_shifts += 1
                role_counts[role] = role_counts.get(role, 0) + 1
        
        current_date += timedelta(days=1)
    
    print(f"\n✅ COMPLETE!")
    print(f"\nTotal shifts created: {total_shifts:,}")
    print(f"\nShifts by role:")
    for role, count in sorted(role_counts.items()):
        print(f"  {role:10s}: {count:,} shifts")
    
    # Verify
    vg_shifts = Shift.objects.filter(user__unit__care_home=vg).count()
    print(f"\nVerification: {vg_shifts:,} Victoria Gardens shifts in database")

if __name__ == '__main__':
    main()
