"""
Demo: Bulk Setup New Care Home Using Staffing Template
========================================================

This script demonstrates how to use the STAFFING_SETUP_TEMPLATE.md to 
create a new care home with full staffing in minutes.

Choose your demo:
1. Template A: Large Home (120 beds, 8 care units, ~179 staff)
2. Template B: Medium Home (70 beds, 5 care units, ~98 staff)
3. Clone Existing Home (fastest - duplicate Orchard Grove)
"""

import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import CareHome, Unit, Role, User, Shift, ShiftType
from django.contrib.auth.hashers import make_password

# ============================================================================
# DEMO CONFIGURATION
# ============================================================================

DEMO_CHOICE = 2  # Change to 1, 2, or 3
NEW_HOME_NAME = "DEMO_HOME"
START_SAP = 900000  # Starting SAP number for demo staff

# ============================================================================
# TEMPLATE A: LARGE HOME (120 BEDS, 8 UNITS)
# ============================================================================

TEMPLATE_A_CONFIG = {
    "name": NEW_HOME_NAME,
    "beds": 120,
    "units": [
        {"name": "Acorn", "beds": 15},
        {"name": "Birch", "beds": 15},
        {"name": "Cedar", "beds": 15},
        {"name": "Elm", "beds": 15},
        {"name": "Fir", "beds": 15},
        {"name": "Grove", "beds": 15},
        {"name": "Hazel", "beds": 15},
        {"name": "Ivy", "beds": 15},
    ],
    "management": {
        "OM": 1,
        "SM": 1,
    },
    "per_unit_staff": {
        "SSCW": 1,    # Day supervisor (supernumerary)
        "SSCWN": 1,   # Night supervisor (supernumerary)
        "SCW": 4,     # Day workers
        "SCWN": 3,    # Night workers
        "SCA": 6,     # Day assistants
        "SCAN": 7,    # Night assistants
    }
}

# ============================================================================
# TEMPLATE B: MEDIUM HOME (70 BEDS, 5 UNITS)
# ============================================================================

TEMPLATE_B_CONFIG = {
    "name": NEW_HOME_NAME,
    "beds": 70,
    "units": [
        {"name": "Jasmine", "beds": 15},
        {"name": "Lavender", "beds": 15},
        {"name": "Magnolia", "beds": 15},
        {"name": "Orchid", "beds": 15},
        {"name": "Poppy", "beds": 10},  # Smaller unit
    ],
    "management": {
        "OM": 1,
        "SM": 1,
    },
    "per_unit_staff": {
        "SSCW": 1,    # Day supervisor (supernumerary)
        "SSCWN": 1,   # Night supervisor (supernumerary)
        "SCW": 3,     # Day workers
        "SCWN": 2,    # Night workers
        "SCA": 6,     # Day assistants
        "SCAN": 6,    # Night assistants
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(text):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_step(step_num, text):
    """Print formatted step"""
    print(f"\n[STEP {step_num}] {text}")
    print("-" * 70)

def create_home_and_units(config):
    """Create care home and all units"""
    print_step(1, f"Creating {config['name']} with {config['beds']} beds")
    
    # Create care home
    home = CareHome.objects.create(
        name=config["name"],
        address="123 Demo Street",
        city="Demo City",
        postcode="D3M0 1AB",
        phone="01234567890",
        email=f"{config['name'].lower()}@demo.care",
        capacity=config["beds"]
    )
    print(f"✅ Created care home: {home.name} ({home.capacity} beds)")
    
    # Create management unit
    mgmt_unit = Unit.objects.create(
        care_home=home,
        name=f"{config['name']}_Mgmt"
    )
    print(f"✅ Created management unit: {mgmt_unit.name}")
    
    # Create care units
    units = []
    for unit_config in config["units"]:
        unit = Unit.objects.create(
            care_home=home,
            name=f"{config['name']}_{unit_config['name']}"
        )
        units.append(unit)
        print(f"✅ Created care unit: {unit.name} ({unit_config['beds']} beds)")
    
    return home, mgmt_unit, units

def create_staff(home, mgmt_unit, units, config):
    """Create all staff based on template"""
    print_step(2, "Creating staff from template")
    
    # Get roles
    roles = {
        'OM': Role.objects.get(name='OM'),
        'SM': Role.objects.get(name='SM'),
        'SSCW': Role.objects.get(name='SSCW'),
        'SSCWN': Role.objects.get(name='SSCWN'),
        'SCW': Role.objects.get(name='SCW'),
        'SCWN': Role.objects.get(name='SCWN'),
        'SCA': Role.objects.get(name='SCA'),
        'SCAN': Role.objects.get(name='SCAN'),
    }
    
    staff_list = []
    sap_counter = START_SAP
    
    # Create management staff
    print(f"\n📋 Management Staff:")
    for role_name, count in config["management"].items():
        for i in range(count):
            sap = f"{sap_counter:06d}"
            user = User.objects.create(
                sap=sap,
                email=f"{sap}@{home.name.lower()}.care",
                first_name=f"Demo_{role_name}",
                last_name=f"{i+1}",
                role=roles[role_name],
                unit=mgmt_unit,
                password=make_password('Demo123##'),
                is_active=True,
                shifts_per_week_override=5,  # Management works Mon-Fri
                team='A'
            )
            staff_list.append(user)
            print(f"  ✅ {sap}: {user.get_full_name()} - {role_name} (5 shifts/week)")
            sap_counter += 1
    
    # Create staff for each unit
    teams = ['A', 'B', 'C']
    for unit_idx, unit in enumerate(units):
        print(f"\n📋 {unit.name} Staff:")
        
        for role_name, count in config["per_unit_staff"].items():
            role = roles[role_name]
            is_night = role_name.endswith('N')
            
            # Determine shifts per week based on contract type
            # Mix of 24-hour (2 shifts) and 35-hour (3 shifts) contracts
            for i in range(count):
                # Alternate between 24hr and 35hr contracts
                shifts_per_week = 2 if i % 2 == 0 else 3
                team = teams[i % 3]  # Distribute across teams A, B, C
                
                sap = f"{sap_counter:06d}"
                user = User.objects.create(
                    sap=sap,
                    email=f"{sap}@{home.name.lower()}.care",
                    first_name=f"Demo_{role_name}",
                    last_name=f"U{unit_idx+1}_{i+1}",
                    role=role,
                    unit=unit,
                    password=make_password('Demo123##'),
                    is_active=True,
                    shifts_per_week_override=shifts_per_week,
                    team=team
                )
                staff_list.append(user)
                contract = "24hr" if shifts_per_week == 2 else "35hr"
                print(f"  ✅ {sap}: {user.get_full_name()} - {role_name} (Team {team}, {contract})")
                sap_counter += 1
    
    return staff_list

def generate_shifts(staff_list, home, months=6):
    """Generate shift schedules for all staff"""
    print_step(3, f"Generating {months}-month shift schedules")
    
    # Get shift types
    day_shift = ShiftType.objects.get(name='DAY_0800_2000')
    night_shift = ShiftType.objects.get(name='NIGHT_2000_0800')
    mgmt_shift = ShiftType.objects.get(name='MGMT_DAY')
    
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=30 * months)
    
    shifts_created = 0
    
    for user in staff_list:
        # Determine shift type
        if user.role.name in ['OM', 'SM']:
            shift_type = mgmt_shift
            is_night = False
        elif user.role.name.endswith('N'):
            shift_type = night_shift
            is_night = True
        else:
            shift_type = day_shift
            is_night = False
        
        # Generate shift dates using 3-week rotation
        shift_dates = generate_shift_dates_6_months(
            user.shifts_per_week_override,
            user.team,
            is_night=is_night
        )
        
        # Filter to date range
        shift_dates = [d for d in shift_dates if start_date <= d <= end_date]
        
        # Create shifts
        for date in shift_dates:
            Shift.objects.create(
                user=user,
                unit=user.unit,
                shift_type=shift_type,
                date=date,
                status='SCHEDULED'
            )
            shifts_created += 1
    
    print(f"✅ Created {shifts_created:,} shifts for {len(staff_list)} staff")
    return shifts_created

def generate_shift_dates_6_months(shifts_per_week, team, is_night=False):
    """Generate shift dates using 3-week rotation pattern"""
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=182)  # 6 months
    
    dates = []
    current_date = start_date
    week_counter = 0
    
    # 3-week pattern for different shift counts
    if shifts_per_week == 5:
        # Management: Mon-Fri every week
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Mon-Fri
                dates.append(current_date)
            current_date += timedelta(days=1)
    
    elif shifts_per_week == 2:
        # 2 shifts/week pattern: 2-1-1 across 3 weeks
        patterns = {
            'A': [[0, 3], [0], [3]],      # Mon, Thu | Mon | Thu
            'B': [[1, 4], [4], [1]],      # Tue, Fri | Fri | Tue
            'C': [[2, 5], [2, 5], [5]],   # Wed, Sat | Wed, Sat | Sat
        }
        pattern = patterns.get(team, patterns['A'])
        
        while current_date <= end_date:
            week_in_cycle = week_counter % 3
            weekdays = pattern[week_in_cycle]
            
            for day in weekdays:
                shift_date = current_date + timedelta(days=day)
                if shift_date <= end_date:
                    dates.append(shift_date)
            
            current_date += timedelta(days=7)
            week_counter += 1
    
    elif shifts_per_week == 3:
        # 3 shifts/week pattern: 3-2-2 across 3 weeks
        patterns = {
            'A': [[0, 2, 4], [0, 4], [2, 4]],           # Mon, Wed, Fri | Mon, Fri | Wed, Fri
            'B': [[1, 3, 5], [3, 5], [1, 3]],           # Tue, Thu, Sat | Thu, Sat | Tue, Thu
            'C': [[0, 3, 6], [0, 3, 6], [3, 6]],        # Mon, Thu, Sun | Mon, Thu, Sun | Thu, Sun
        }
        pattern = patterns.get(team, patterns['A'])
        
        while current_date <= end_date:
            week_in_cycle = week_counter % 3
            weekdays = pattern[week_in_cycle]
            
            for day in weekdays:
                shift_date = current_date + timedelta(days=day)
                if shift_date <= end_date:
                    dates.append(shift_date)
            
            current_date += timedelta(days=7)
            week_counter += 1
    
    return sorted(dates)

def verify_setup(home, staff_list, shifts_created):
    """Verify the home setup is complete and compliant"""
    print_step(4, "Verifying setup and compliance")
    
    from django.db.models import Q
    from collections import defaultdict
    
    # Get a sample date to check coverage
    sample_date = datetime.now().date() + timedelta(days=30)
    
    # Check day shift coverage
    day_shifts = Shift.objects.filter(
        unit__care_home=home,
        date=sample_date,
        shift_type__name__in=['DAY_0800_2000', 'MGMT_DAY']
    ).select_related('user__role')
    
    day_count = day_shifts.exclude(user__role__name__in=['SSCW']).count()
    day_sscw = day_shifts.filter(user__role__name='SSCW').count()
    
    # Check night shift coverage
    night_shifts = Shift.objects.filter(
        unit__care_home=home,
        date=sample_date,
        shift_type__name='NIGHT_2000_0800'
    ).select_related('user__role')
    
    night_count = night_shifts.exclude(user__role__name='SSCWN').count()
    night_sscw = night_shifts.filter(user__role__name='SSCWN').count()
    
    # Check per-unit coverage
    units = Unit.objects.filter(care_home=home).exclude(name__contains='Mgmt')
    unit_coverage = defaultdict(lambda: {'day': 0, 'night': 0})
    
    for shift in day_shifts:
        if not shift.unit.name.endswith('Mgmt'):
            unit_coverage[shift.unit.name]['day'] += 1
    
    for shift in night_shifts:
        if not shift.unit.name.endswith('Mgmt'):
            unit_coverage[shift.unit.name]['night'] += 1
    
    # Print results
    print(f"\n📊 {home.name} Summary:")
    print(f"  Total Staff: {len(staff_list)}")
    print(f"  Total Shifts (6 months): {shifts_created:,}")
    print(f"  Care Units: {units.count()}")
    print(f"  Bed Capacity: {home.capacity}")
    
    print(f"\n📅 Sample Date Coverage ({sample_date}):")
    print(f"  Day Shift: {day_count} staff + {day_sscw} SSCW supervisors")
    print(f"  Night Shift: {night_count} staff + {night_sscw} SSCWN supervisors")
    
    print(f"\n📍 Per-Unit Coverage on {sample_date}:")
    for unit_name, coverage in sorted(unit_coverage.items()):
        day_status = "✅" if coverage['day'] >= 2 else "⚠️"
        night_status = "✅" if coverage['night'] >= 2 else "⚠️"
        print(f"  {unit_name}: {day_status} {coverage['day']} day, {night_status} {coverage['night']} night")
    
    # Compliance checks
    print(f"\n✅ COMPLIANCE CHECKS:")
    
    if home.capacity == 120:
        min_day = 18
        min_night = 18
    else:  # 70 beds
        min_day = 10
        min_night = 10
    
    day_ok = "✅" if day_count >= min_day else "❌"
    night_ok = "✅" if night_count >= min_night else "❌"
    sscw_day_ok = "✅" if day_sscw >= 1 else "❌"
    sscw_night_ok = "✅" if night_sscw >= 1 else "❌"
    
    print(f"  {day_ok} Day shift minimum ({day_count}/{min_day} staff)")
    print(f"  {night_ok} Night shift minimum ({night_count}/{min_night} staff)")
    print(f"  {sscw_day_ok} Day SSCW supervisors ({day_sscw}+)")
    print(f"  {sscw_night_ok} Night SSCWN supervisors ({night_sscw}+)")
    
    all_units_ok = all(c['day'] >= 2 and c['night'] >= 2 for c in unit_coverage.values())
    units_ok = "✅" if all_units_ok else "⚠️"
    print(f"  {units_ok} All units have 2+ staff on days and nights")

def clone_existing_home(source_name="ORCHARD_GROVE", new_name="CLONED_HOME"):
    """Clone an existing home (fastest method)"""
    print_step(1, f"Cloning {source_name} to {new_name}")
    
    # Get source home
    source_home = CareHome.objects.get(name=source_name)
    source_units = Unit.objects.filter(care_home=source_home)
    source_staff = User.objects.filter(unit__care_home=source_home)
    
    print(f"📋 Source: {source_home.name}")
    print(f"  Units: {source_units.count()}")
    print(f"  Staff: {source_staff.count()}")
    
    # Create new home
    new_home = CareHome.objects.create(
        name=new_name,
        address=source_home.address,
        city=source_home.city,
        postcode=source_home.postcode,
        phone=source_home.phone,
        email=f"{new_name.lower()}@demo.care",
        capacity=source_home.capacity
    )
    print(f"\n✅ Created new home: {new_home.name}")
    
    # Clone units
    unit_mapping = {}
    for source_unit in source_units:
        new_unit = Unit.objects.create(
            care_home=new_home,
            name=source_unit.name.replace(source_name, new_name)
        )
        unit_mapping[source_unit.id] = new_unit
        print(f"✅ Cloned unit: {new_unit.name}")
    
    # Clone staff
    sap_counter = START_SAP
    staff_list = []
    
    for source_user in source_staff:
        new_unit = unit_mapping[source_user.unit.id]
        sap = f"{sap_counter:06d}"
        
        new_user = User.objects.create(
            sap=sap,
            email=f"{sap}@{new_name.lower()}.care",
            first_name=source_user.first_name,
            last_name=source_user.last_name,
            role=source_user.role,
            unit=new_unit,
            password=make_password('Demo123##'),
            is_active=True,
            shifts_per_week_override=source_user.shifts_per_week_override,
            team=source_user.team
        )
        staff_list.append(new_user)
        sap_counter += 1
    
    print(f"✅ Cloned {len(staff_list)} staff members")
    
    # Generate shifts
    shifts_created = generate_shifts(staff_list, new_home, months=6)
    
    return new_home, staff_list, shifts_created

# ============================================================================
# MAIN DEMO
# ============================================================================

def run_demo():
    """Run the selected demo"""
    print_header("CARE HOME BULK SETUP DEMO")
    print(f"Demo Type: {DEMO_CHOICE}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if DEMO_CHOICE == 1:
        print_header("TEMPLATE A: LARGE HOME (120 beds, 8 care units)")
        config = TEMPLATE_A_CONFIG
        home, mgmt_unit, units = create_home_and_units(config)
        staff_list = create_staff(home, mgmt_unit, units, config)
        shifts_created = generate_shifts(staff_list, home)
        verify_setup(home, staff_list, shifts_created)
        
    elif DEMO_CHOICE == 2:
        print_header("TEMPLATE B: MEDIUM HOME (70 beds, 5 care units)")
        config = TEMPLATE_B_CONFIG
        home, mgmt_unit, units = create_home_and_units(config)
        staff_list = create_staff(home, mgmt_unit, units, config)
        shifts_created = generate_shifts(staff_list, home)
        verify_setup(home, staff_list, shifts_created)
        
    elif DEMO_CHOICE == 3:
        print_header("OPTION 3: CLONE EXISTING HOME (Fastest)")
        home, staff_list, shifts_created = clone_existing_home(
            source_name="ORCHARD_GROVE",
            new_name=NEW_HOME_NAME
        )
        verify_setup(home, staff_list, shifts_created)
    
    else:
        print("❌ Invalid DEMO_CHOICE. Please set to 1, 2, or 3.")
        return
    
    print_header("DEMO COMPLETE!")
    print(f"\n🎉 Successfully created {home.name}!")
    print(f"\n📝 Login credentials for all demo staff:")
    print(f"   Username: Any SAP number (e.g., {staff_list[0].sap})")
    print(f"   Password: Demo123##")
    print(f"\n🌐 View in system: http://127.0.0.1:8000/")
    print(f"\n⚠️  This is demo data. To delete:")
    print(f"   CareHome.objects.filter(name='{home.name}').delete()")
    
if __name__ == "__main__":
    run_demo()
