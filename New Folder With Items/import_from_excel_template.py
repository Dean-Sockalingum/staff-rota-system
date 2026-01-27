#!/usr/bin/env python
"""
Bulk Import Staff from Excel Template (Template off duty 2026 v3.xlsx)
This script imports all staff and their shift patterns exactly as defined in the Excel file.
"""

import os
import django
import pandas as pd
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from scheduling.models import CareHome, Unit, User, Shift, Role, ShiftType

# Password for all imported staff
DEFAULT_PASSWORD = "Demo123##"
HASHED_PASSWORD = make_password(DEFAULT_PASSWORD)

# Excel file path
EXCEL_FILE = "Template off duty 2026 v3.xlsx"

# Care home to import into
CARE_HOME_NAME = "ORCHARD_GROVE"

# Define the base date for shift generation (start of 3-week cycle)
BASE_DATE = datetime(2026, 1, 27)  # Monday, 27 Jan 2026

# Team patterns for 3-week rotation
TEAM_PATTERNS_35HR = {
    'A': {
        'Week 1': ['Wed', 'Fri', 'Sat'],
        'Week 2': ['Sun', 'Wed', 'Thu'],
        'Week 3': ['Mon', 'Tue', 'Wed']
    },
    'B': {
        'Week 1': ['Sun', 'Mon', 'Tue'],
        'Week 2': ['Wed', 'Fri', 'Sat'],
        'Week 3': ['Sun', 'Wed', 'Thu']
    },
    'C': {
        'Week 1': ['Mon', 'Tue', 'Wed'],
        'Week 2': ['Wed', 'Fri', 'Sat'],
        'Week 3': ['Sun', 'Tue', 'Wed']
    }
}

TEAM_PATTERNS_24HR = {
    'A': {
        'Week 1': ['Fri', 'Sat'],
        'Week 2': ['Sun', 'Thu'],
        'Week 3': ['Mon', 'Tue']
    },
    'B': {
        'Week 1': ['Sun', 'Mon'],
        'Week 2': ['Fri', 'Sat'],
        'Week 3': ['Sun', 'Thu']
    },
    'C': {
        'Week 1': ['Mon', 'Tue'],
        'Week 2': ['Fri', 'Sat'],
        'Week 3': ['Sun', 'Thu']
    }
}

TEAM_PATTERNS_MGMT = {
    'A': {
        'Week 1': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
        'Week 2': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
        'Week 3': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    }
}

# Day name to weekday mapping
DAY_TO_WEEKDAY = {
    'Sun': 6, 'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5
}


def get_shift_dates_for_team(team, hours_per_week, role_code):
    """Generate shift dates for a specific team based on their pattern"""
    # Management roles use Mon-Fri pattern regardless of team
    if role_code in ['SM', 'OM']:
        pattern = TEAM_PATTERNS_MGMT['A']
    elif hours_per_week == 35:
        if team in TEAM_PATTERNS_35HR:
            pattern = TEAM_PATTERNS_35HR[team]
        else:
            return []
    elif hours_per_week == 24:
        if team in TEAM_PATTERNS_24HR:
            pattern = TEAM_PATTERNS_24HR[team]
        else:
            return []
    else:
        return []
    
    shift_dates = []
    
    for week_num in range(1, 4):
        week_key = f'Week {week_num}'
        days_in_week = pattern.get(week_key, [])
        week_offset = (week_num - 1) * 7
        
        for day_name in days_in_week:
            target_weekday = DAY_TO_WEEKDAY[day_name]
            days_from_base = week_offset + (target_weekday - BASE_DATE.weekday()) % 7
            shift_date = BASE_DATE + timedelta(days=days_from_base)
            shift_dates.append(shift_date)
    
    return sorted(shift_dates)


def determine_team_from_pattern(row_data, sheet_name):
    """Determine team assignment based on shift pattern in Excel"""
    # For managers (Mon-Fri pattern) - default to Team A
    if 'SM' in str(row_data.get('Role', '')) or 'OM' in str(row_data.get('Role', '')):
        return 'A'  # Management staff default to Team A
    
    # Check Week 1 pattern to determine team
    week1_days = []
    for day in ['SUN', 'Mon', 'TUE', 'WED', 'THU', 'FRI', 'SAT']:
        if pd.notna(row_data.get(day, 0)) and row_data.get(day, 0) == 1:
            week1_days.append(day)
    
    hours = row_data.get('Hours Worked per week', 35)
    if pd.isna(hours):
        hours = row_data.get('Hrs per week', 35)
    
    # Pattern matching for 35-hour contracts
    if hours == 35:
        if 'WED' in week1_days and 'FRI' in week1_days and 'SAT' in week1_days:
            return 'A'
        elif 'SUN' in week1_days and 'Mon' in week1_days and 'TUE' in week1_days:
            return 'B'
        elif 'Mon' in week1_days and 'TUE' in week1_days and 'WED' in week1_days:
            return 'C'
    
    # Pattern matching for 24-hour contracts
    elif hours == 24:
        if 'FRI' in week1_days and 'SAT' in week1_days:
            return 'A'
        elif 'SUN' in week1_days and 'Mon' in week1_days:
            return 'B'
        elif 'Mon' in week1_days and 'TUE' in week1_days:
            return 'C'
    
    # Default to A if pattern unclear
    return 'A'


def map_role_code(role_str):
    """Map Excel role names to database role codes"""
    role_str = str(role_str).strip().upper()
    
    if 'SM' in role_str:
        return 'SM'  # Service Manager
    elif 'OM' in role_str:
        return 'OM'  # Operations Manager
    elif 'SSCW(N)' in role_str:
        return 'SSCWN'  # Senior Social Care Worker (Night)
    elif 'SSCW' in role_str:
        return 'SSCW'  # Senior Social Care Worker (Day)
    elif 'SCW(N)' in role_str or 'SCW (N)' in role_str:
        return 'SCWN'  # Social Care Worker (Night)
    elif 'SCW' in role_str:
        return 'SCW'  # Social Care Worker (Day)
    elif 'SCA(N)' in role_str or 'SCA (N)' in role_str:
        return 'SCAN'  # Social Care Assistant (Night)
    elif 'SCA' in role_str:
        return 'SCA'  # Social Care Assistant (Day)
    else:
        return 'SCA'  # Default to SCA


def map_unit_name(unit_str, care_home_name):
    """Map Excel unit names to database unit names (with care home prefix if needed)"""
    unit_str = str(unit_str).strip().upper()
    
    # Base mapping (for TEMPLATE_DEMO which uses simple names)
    base_mapping = {
        'PEAR(SRD)': 'Jasmine',
        'PLUM': 'Lavender',
        'PEACH': 'Magnolia',
        'GRAPE': 'Orchid',
        'STRAWBERRY': 'Poppy',
        'BRAMLEY': 'Jasmine',
        'ORANGE': 'Lavender',
        'CHERRY': 'Magnolia',
        'MGMT': 'Management'
    }
    
    # Orchard Grove specific mapping (Excel units map to prefixed unit names)
    orchard_grove_mapping = {
        'PEAR(SRD)': 'ORCHARD_GROVE_Pear',
        'PLUM': 'ORCHARD_GROVE_Plum',
        'PEACH': 'ORCHARD_GROVE_Peach',
        'GRAPE': 'ORCHARD_GROVE_Grape',
        'STRAWBERRY': 'ORCHARD_GROVE_Strawberry',
        'BRAMLEY': 'ORCHARD_GROVE_Bramley',
        'ORANGE': 'ORCHARD_GROVE_Orange',
        'CHERRY': 'ORCHARD_GROVE_Cherry',
        'MGMT': 'ORCHARD_GROVE_Mgmt'
    }
    
    # Use appropriate mapping based on care home
    if care_home_name == 'ORCHARD_GROVE':
        return orchard_grove_mapping.get(unit_str, 'ORCHARD_GROVE_Pear')
    else:
        return base_mapping.get(unit_str, 'Jasmine')


def determine_shift_pattern(role_code, hours, is_night):
    """Determine shift pattern code based on role, hours, and shift type"""
    if role_code in ['SM', 'OM']:
        return 'Pattern_3'  # Management pattern
    elif hours == 24:
        return 'Pattern_1'  # 24-hour pattern (2 shifts/week)
    else:  # 35 hours
        return 'Pattern_2'  # 35-hour pattern (3 shifts/week)


def import_staff_from_sheet(sheet_name, care_home, is_night=False):
    """Import staff from a specific Excel sheet"""
    print(f"\n{'='*80}")
    print(f"Importing from sheet: {sheet_name}")
    print(f"{'='*80}\n")
    
    # Get existing shift types
    try:
        day_shift = ShiftType.objects.get(name='DAY_0800_2000')
        night_shift = ShiftType.objects.get(name='NIGHT_2000_0800')
        mgmt_shift = ShiftType.objects.get(name='MGMT_DAY')
    except ShiftType.DoesNotExist as e:
        print(f"⚠️  ShiftType not found: {e}")
        return 0, 0
    
    # Read Excel - Nights sheet has blank row 0, header in row 1
    if sheet_name == 'Nights':
        # Row 0 is blank, Row 1 has headers, data starts at Row 2
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name, header=1)
    else:
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
    
    staff_imported = 0
    shifts_created = 0
    
    for idx, row in df.iterrows():
        # Skip rows without SAP number or with invalid SAP
        sap = row.get('SAP')
        if pd.isna(sap) or sap == 'SAP':  # Skip header rows and empty rows
            continue
        
        try:
            sap = int(sap)
        except (ValueError, TypeError):
            continue  # Skip rows with invalid SAP numbers
        
        first_name = str(row.get('First', '')).strip()
        surname = str(row.get('Surname', '')).strip()
        
        if not first_name or not surname or first_name == 'nan' or surname == 'nan':
            continue
        
        role_str = row.get('Role', 'SCA')
        hours = row.get('Hours Worked per week', 35)
        if pd.isna(hours):
            hours = row.get('Hrs per week', 35)
        hours = int(hours)
        
        unit_str = row.get('Unit', 'PEAR(SRD)')
        
        # Map to database values
        role_code = map_role_code(role_str)
        unit_name = map_unit_name(unit_str, care_home.name)
        team = determine_team_from_pattern(row, sheet_name)
        shift_pattern = determine_shift_pattern(role_code, hours, is_night)
        
        # Get or create role
        role, _ = Role.objects.get_or_create(name=role_code)
        
        # Get unit (don't create - should already exist)
        try:
            unit = Unit.objects.get(care_home=care_home, name=unit_name)
        except Unit.DoesNotExist:
            print(f"⚠ Warning: Unit {unit_name} not found in {care_home.name}, skipping staff member")
            continue
        
        # Create or update user
        user, created = User.objects.update_or_create(
            sap=str(sap).zfill(6),
            defaults={
                'first_name': first_name,
                'last_name': surname,
                'role': role,
                'unit': unit,
                'team': team,
                'password': HASHED_PASSWORD,
                'is_active': True,
                'email': f"{sap}@template.demo",
            }
        )
        
        if created:
            print(f"✓ Created: {first_name} {surname} (SAP: {sap}, Role: {role_code}, Team: {team}, Unit: {unit_name})")
        else:
            print(f"↻ Updated: {first_name} {surname} (SAP: {sap}, Role: {role_code}, Team: {team}, Unit: {unit_name})")
        
        staff_imported += 1
        
        # Delete existing shifts for this user
        Shift.objects.filter(user=user).delete()
        
        # Create shifts based on team pattern
        shift_dates = get_shift_dates_for_team(team, hours, role_code)
        
        # Determine shift type
        if role_code in ['SM', 'OM']:
            shift_type_obj = mgmt_shift
        elif is_night or 'N' in role_code:
            shift_type_obj = night_shift
        else:
            shift_type_obj = day_shift
        
        for shift_date in shift_dates:
            Shift.objects.create(
                user=user,
                unit=unit,
                shift_type=shift_type_obj,
                date=shift_date,
                status='SCHEDULED'
            )
            shifts_created += 1
    
    print(f"\n{'='*40}")
    print(f"Sheet Summary: {sheet_name}")
    print(f"  Staff imported: {staff_imported}")
    print(f"  Shifts created: {shifts_created}")
    print(f"{'='*40}\n")
    
    return staff_imported, shifts_created


def main():
    """Main import function"""
    print("\n" + "="*80)
    print("BULK IMPORT FROM EXCEL TEMPLATE")
    print("="*80)
    print(f"Excel file: {EXCEL_FILE}")
    print(f"Target care home: {CARE_HOME_NAME}")
    print(f"Base date for shifts: {BASE_DATE.strftime('%A, %d %B %Y')}")
    print(f"Default password: {DEFAULT_PASSWORD}")
    print("="*80 + "\n")
    
    # Get care home
    try:
        care_home = CareHome.objects.get(name=CARE_HOME_NAME)
        print(f"✓ Found care home: {care_home.name}\n")
    except CareHome.DoesNotExist:
        print(f"✗ Care home '{CARE_HOME_NAME}' not found!")
        return
    
    # Confirm deletion
    existing_staff = User.objects.filter(unit__care_home=care_home).count()
    existing_shifts = Shift.objects.filter(user__unit__care_home=care_home).count()
    
    print(f"⚠️  WARNING: This will replace existing data:")
    print(f"   - {existing_staff} existing staff members")
    print(f"   - {existing_shifts} existing shifts")
    print()
    
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    if response != 'yes':
        print("\n✗ Import cancelled.")
        return
    
    # Delete existing data
    print("\n🗑️  Deleting existing shifts...")
    Shift.objects.filter(user__unit__care_home=care_home).delete()
    
    print("🗑️  Deleting existing staff...")
    User.objects.filter(unit__care_home=care_home).delete()
    
    print("✓ Existing data cleared.\n")
    
    total_staff = 0
    total_shifts = 0
    
    # Import from each sheet
    sheets_to_import = [
        ('Managers', False),  # Day managers and SSCWs
        ('Days', False),      # Day shift staff (SCA, SCW)
        ('Nights', True),     # Night shift staff (SCA(N), SCW(N))
    ]
    
    for sheet_name, is_night in sheets_to_import:
        staff_count, shift_count = import_staff_from_sheet(sheet_name, care_home, is_night)
        total_staff += staff_count
        total_shifts += shift_count
    
    # Final summary
    print("\n" + "="*80)
    print("IMPORT COMPLETE")
    print("="*80)
    print(f"Total staff imported: {total_staff}")
    print(f"Total shifts created: {total_shifts}")
    print(f"Care home: {care_home.name}")
    print(f"3-week rotation: {BASE_DATE.strftime('%d %b')} - {(BASE_DATE + timedelta(days=20)).strftime('%d %b %Y')}")
    print("="*80)
    print(f"\n✓ All staff can login with password: {DEFAULT_PASSWORD}")
    print(f"✓ Staff SAP numbers range from 10082 to 100141 (Days) and 100001 to 100049 (Nights)")
    print(f"✓ Managers: SAP 999996-999981 (SSCW Day/Night), 999999-999997 (SM/OM)")
    print("\n" + "="*80 + "\n")


if __name__ == '__main__':
    main()
