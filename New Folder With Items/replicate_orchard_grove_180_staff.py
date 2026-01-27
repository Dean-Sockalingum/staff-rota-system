#!/usr/bin/env python
"""
Replicate ORCHARD_GROVE's 180-staff structure to RIVERSIDE, HAWTHORN, and MEADOWBURN.
Each home gets:
- 180 staff total (20 managers, 79 day staff, 81 night staff)
- Same roles, grades, hours, teams, shift patterns
- Unique names and SAP numbers per home
- Same 3-week rota (Jan 27 - Feb 16, 2026)
"""

import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Shift, CareHome, Unit, Role, ShiftType
from django.contrib.auth.hashers import make_password

# Configuration
SOURCE_HOME = 'ORCHARD_GROVE'
TARGET_HOMES = ['RIVERSIDE', 'HAWTHORN_HOUSE', 'MEADOWBURN']
PASSWORD = 'Demo123##'
HASHED_PASSWORD = make_password(PASSWORD)

# SAP number ranges per home (avoid Victoria Gardens 400000-400097)
SAP_RANGES = {
    'RIVERSIDE': 200001,
    'HAWTHORN_HOUSE': 300001,
    'MEADOWBURN': 500001
}

# Unit name mappings (ORCHARD_GROVE → Target home)
UNIT_MAP = {
    'ORCHARD_GROVE_Bramley': 'Bramley',
    'ORCHARD_GROVE_Cherry': 'Cherry',
    'ORCHARD_GROVE_Grape': 'Grape',
    'ORCHARD_GROVE_Mgmt': 'Mgmt',
    'ORCHARD_GROVE_Orange': 'Orange',
    'ORCHARD_GROVE_Peach': 'Peach',
    'ORCHARD_GROVE_Pear': 'Pear',
    'ORCHARD_GROVE_Plum': 'Plum',
    'ORCHARD_GROVE_Strawberry': 'Strawberry'
}

# Name generation (simple incremental approach)
FIRST_NAMES = [
    'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
    'William', 'Barbara', 'David', 'Elizabeth', 'Richard', 'Susan', 'Joseph', 'Jessica',
    'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa',
    'Matthew', 'Betty', 'Anthony', 'Margaret', 'Mark', 'Sandra', 'Donald', 'Ashley',
    'Steven', 'Kimberly', 'Paul', 'Emily', 'Andrew', 'Donna', 'Joshua', 'Michelle',
    'Kenneth', 'Dorothy', 'Kevin', 'Carol', 'Brian', 'Amanda', 'George', 'Melissa',
    'Edward', 'Deborah', 'Ronald', 'Stephanie', 'Timothy', 'Rebecca', 'Jason', 'Sharon',
    'Jeffrey', 'Laura', 'Ryan', 'Cynthia', 'Jacob', 'Kathleen', 'Gary', 'Amy',
    'Nicholas', 'Shirley', 'Eric', 'Angela', 'Jonathan', 'Helen', 'Stephen', 'Anna',
    'Larry', 'Brenda', 'Justin', 'Pamela', 'Scott', 'Nicole', 'Brandon', 'Emma',
    'Benjamin', 'Samantha', 'Samuel', 'Katherine', 'Raymond', 'Christine', 'Gregory', 'Debra',
    'Alexander', 'Rachel', 'Patrick', 'Catherine', 'Frank', 'Carolyn', 'Jack', 'Janet',
    'Dennis', 'Ruth', 'Jerry', 'Maria', 'Tyler', 'Heather', 'Aaron', 'Diane',
    'Jose', 'Virginia', 'Adam', 'Julie', 'Henry', 'Joyce', 'Nathan', 'Victoria',
    'Douglas', 'Olivia', 'Zachary', 'Kelly', 'Peter', 'Christina', 'Kyle', 'Lauren',
    'Walter', 'Joan', 'Ethan', 'Evelyn', 'Jeremy', 'Judith', 'Harold', 'Megan',
    'Keith', 'Cheryl', 'Christian', 'Andrea', 'Roger', 'Hannah', 'Noah', 'Jacqueline',
    'Gerald', 'Martha', 'Carl', 'Gloria', 'Terry', 'Teresa', 'Sean', 'Ann',
    'Austin', 'Sara', 'Arthur', 'Madison', 'Lawrence', 'Frances', 'Jesse', 'Kathryn',
    'Dylan', 'Janice', 'Bryan', 'Jean', 'Joe', 'Abigail', 'Jordan', 'Alice',
    'Billy', 'Judy', 'Bruce', 'Sophia', 'Albert', 'Grace', 'Willie', 'Denise',
    'Gabriel', 'Amber', 'Logan', 'Doris', 'Alan', 'Marilyn', 'Juan', 'Danielle'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas',
    'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White',
    'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young',
    'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
    'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell',
    'Carter', 'Roberts', 'Gomez', 'Phillips', 'Evans', 'Turner', 'Diaz', 'Parker',
    'Cruz', 'Edwards', 'Collins', 'Reyes', 'Stewart', 'Morris', 'Morales', 'Murphy',
    'Cook', 'Rogers', 'Gutierrez', 'Ortiz', 'Morgan', 'Cooper', 'Peterson', 'Bailey',
    'Reed', 'Kelly', 'Howard', 'Ramos', 'Kim', 'Cox', 'Ward', 'Richardson',
    'Watson', 'Brooks', 'Chavez', 'Wood', 'James', 'Bennett', 'Gray', 'Mendoza',
    'Ruiz', 'Hughes', 'Price', 'Alvarez', 'Castillo', 'Sanders', 'Patel', 'Myers',
    'Long', 'Ross', 'Foster', 'Jimenez', 'Powell', 'Jenkins', 'Perry', 'Russell',
    'Sullivan', 'Bell', 'Coleman', 'Butler', 'Henderson', 'Barnes', 'Gonzales', 'Fisher',
    'Vasquez', 'Simmons', 'Romero', 'Jordan', 'Patterson', 'Alexander', 'Hamilton', 'Graham',
    'Reynolds', 'Griffin', 'Wallace', 'Moreno', 'West', 'Cole', 'Hayes', 'Bryant',
    'Herrera', 'Gibson', 'Ellis', 'Tran', 'Medina', 'Aguilar', 'Stevens', 'Murray',
    'Ford', 'Castro', 'Marshall', 'Owens', 'Harrison', 'Fernandez', 'McDonald', 'Woods',
    'Washington', 'Kennedy', 'Wells', 'Vargas', 'Henry', 'Chen', 'Freeman', 'Webb',
    'Tucker', 'Guzman', 'Burns', 'Crawford', 'Olson', 'Simpson', 'Porter', 'Hunter',
    'Gordon', 'Mendez', 'Silva', 'Shaw', 'Snyder', 'Mason', 'Dixon', 'Munoz',
    'Hunt', 'Hicks', 'Holmes', 'Palmer', 'Wagner', 'Black', 'Robertson', 'Boyd'
]

def generate_name(index, home_name):
    """Generate unique name based on index and home"""
    first = FIRST_NAMES[index % len(FIRST_NAMES)]
    last = LAST_NAMES[(index + len(FIRST_NAMES)) % len(LAST_NAMES)]
    
    # Add home initial to ensure uniqueness
    home_initial = home_name[0]
    return f"{first} {last}-{home_initial}"

def replicate_staff_to_home(source_home_name, target_home_name):
    """Replicate all staff and shifts from source to target home"""
    
    print(f"\n{'='*60}")
    print(f"Replicating {source_home_name} → {target_home_name}")
    print(f"{'='*60}")
    
    # Get care homes
    source_home = CareHome.objects.get(name=source_home_name)
    target_home = CareHome.objects.get(name=target_home_name)
    
    # Get all source staff ordered by SAP number for consistency
    source_staff = User.objects.filter(
        unit__care_home=source_home
    ).select_related('unit', 'role').order_by('sap')
    
    print(f"\n📋 Source: {source_staff.count()} staff from {source_home_name}")
    
    # Delete existing staff in target home
    existing_count = User.objects.filter(unit__care_home=target_home).count()
    if existing_count > 0:
        print(f"🗑️  Deleting {existing_count} existing staff from {target_home_name}")
        User.objects.filter(unit__care_home=target_home).delete()
    
    # SAP number counter
    sap_counter = SAP_RANGES[target_home_name]
    
    # Track statistics
    stats = {
        'managers': 0,
        'day_staff': 0,
        'night_staff': 0,
        'total_shifts': 0
    }
    
    # Replicate each staff member
    for index, source_user in enumerate(source_staff):
        # Generate unique name and SAP
        new_name = generate_name(index, target_home_name)
        first_name = new_name.split()[0]
        last_name = ' '.join(new_name.split()[1:])
        new_sap = str(sap_counter).zfill(6)
        sap_counter += 1
        
        # Map unit to target home
        source_unit_name = source_user.unit.name
        target_unit_name = UNIT_MAP.get(source_unit_name, source_unit_name.split('_')[-1])
        
        # Get target unit
        target_unit = Unit.objects.get(
            care_home=target_home,
            name=f"{target_home_name}_{target_unit_name}"
        )
        
        # Create new user
        new_user = User.objects.create(
            sap=new_sap,
            first_name=first_name,
            last_name=last_name,
            email=f"{new_sap}@example.com",
            role=source_user.role,
            unit=target_unit,
            team=source_user.team,
            password=HASHED_PASSWORD,
            is_active=True
        )
        
        # Track statistics
        if source_user.role.name in ['SM', 'OM']:
            stats['managers'] += 1
        elif source_user.role.name in ['SSCWN', 'SCWN', 'SCAN']:
            stats['night_staff'] += 1
        else:
            stats['day_staff'] += 1
        
        # Replicate shifts
        source_shifts = Shift.objects.filter(user=source_user)
        for shift in source_shifts:
            Shift.objects.create(
                user=new_user,
                unit=target_unit,
                shift_type=shift.shift_type,
                date=shift.date
            )
            stats['total_shifts'] += 1
    
    # Print statistics
    print(f"\n✅ Created {source_staff.count()} staff in {target_home_name}:")
    print(f"   • Managers: {stats['managers']}")
    print(f"   • Day staff: {stats['day_staff']}")
    print(f"   • Night staff: {stats['night_staff']}")
    print(f"   • Total shifts: {stats['total_shifts']}")
    print(f"   • SAP range: {SAP_RANGES[target_home_name]:06d} - {sap_counter-1:06d}")
    print(f"   • Password: {PASSWORD}")

def main():
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║  ORCHARD_GROVE 180-Staff Replication Script              ║")
    print("║  Replicating to: RIVERSIDE, HAWTHORN_HOUSE, MEADOWBURN   ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    # Verify source home has 180 staff
    source_home = CareHome.objects.get(name=SOURCE_HOME)
    source_count = User.objects.filter(unit__care_home=source_home).count()
    
    if source_count != 180:
        print(f"\n⚠️  WARNING: {SOURCE_HOME} has {source_count} staff (expected 180)")
        response = input("Continue anyway? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return
    
    # Replicate to each target home
    for target_home_name in TARGET_HOMES:
        try:
            replicate_staff_to_home(SOURCE_HOME, target_home_name)
        except Exception as e:
            print(f"\n❌ ERROR replicating to {target_home_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("✅ REPLICATION COMPLETE")
    print(f"{'='*60}")
    
    # Final summary
    print("\n📊 FINAL SUMMARY:")
    for home_name in [SOURCE_HOME] + TARGET_HOMES:
        home = CareHome.objects.get(name=home_name)
        staff_count = User.objects.filter(unit__care_home=home).count()
        shift_count = Shift.objects.filter(user__unit__care_home=home).count()
        print(f"   {home_name}: {staff_count} staff, {shift_count} shifts")

if __name__ == '__main__':
    main()
