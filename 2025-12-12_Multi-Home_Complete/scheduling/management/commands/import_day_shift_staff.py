from django.core.management.base import BaseCommand
from scheduling.models import User, Role, Unit

class Command(BaseCommand):
    help = 'Import day shift SCW and SCA staff'

    def handle(self, *args, **options):
        self.stdout.write('Importing day shift SCW and SCA staff...')
        
        # Get or create roles
        scw_role, _ = Role.objects.get_or_create(name='SCW', defaults={'is_management': False})
        sca_role, _ = Role.objects.get_or_create(name='SCA', defaults={'is_management': False})
        
        # Get units
        unit_map = {name: Unit.objects.get_or_create(name=name, defaults={'is_active': True})[0] 
                    for name in ['DEMENTIA', 'BLUE', 'VIOLET', 'ROSE', 'GRAPE', 'PEACH', 'ORANGE', 'GREEN']}
        
        # Day shift SCW and SCA staff data
        staff_data = [
            # Team 2 - SCW Days
            {'role': 'SCW', 'first': 'Alice', 'last': 'Smith', 'sap': 'SCW1001', 'unit': 'DEMENTIA', 'team': '2', 'shifts_per_week': 3},
            {'role': 'SCW', 'first': 'Bob', 'last': 'Johnson', 'sap': 'SCW1002', 'unit': 'BLUE', 'team': '2', 'shifts_per_week': 3},
            {'role': 'SCW', 'first': 'Carol', 'last': 'Williams', 'sap': 'SCW1003', 'unit': 'ORANGE', 'team': '2', 'shifts_per_week': 3},
            {'role': 'SCW', 'first': 'David', 'last': 'Brown', 'sap': 'SCW1004', 'unit': 'GREEN', 'team': '2', 'shifts_per_week': 2},
            {'role': 'SCW', 'first': 'Emily', 'last': 'Jones', 'sap': 'SCW1005', 'unit': 'VIOLET', 'team': '2', 'shifts_per_week': 2},
            {'role': 'SCW', 'first': 'Frank', 'last': 'Garcia', 'sap': 'SCW1006', 'unit': 'ROSE', 'team': '2', 'shifts_per_week': 2},
            {'role': 'SCW', 'first': 'Grace', 'last': 'Miller', 'sap': 'SCW1007', 'unit': 'GRAPE', 'team': '2', 'shifts_per_week': 2},
            {'role': 'SCW', 'first': 'Henry', 'last': 'Davis', 'sap': 'SCW1008', 'unit': 'PEACH', 'team': '2', 'shifts_per_week': 2},
            {'role': 'SCW', 'first': 'Ivy', 'last': 'Rodriguez', 'sap': 'SCW1009', 'unit': 'DEMENTIA', 'team': '2', 'shifts_per_week': 2},
            
            # Team 2 - SCA Days
            {'role': 'SCA', 'first': 'Jack', 'last': 'Martinez', 'sap': 'SCA1010', 'unit': 'DEMENTIA', 'team': '2', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Karen', 'last': 'Hernandez', 'sap': 'SCA1011', 'unit': 'BLUE', 'team': '2', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Liam', 'last': 'Lopez', 'sap': 'SCA1012', 'unit': 'ORANGE', 'team': '2', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Mia', 'last': 'Gonzalez', 'sap': 'SCA1013', 'unit': 'GREEN', 'team': '2', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Noah', 'last': 'Wilson', 'sap': 'SCA1014', 'unit': 'VIOLET', 'team': '2', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Olivia', 'last': 'Anderson', 'sap': 'SCA1015', 'unit': 'ROSE', 'team': '2', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Peter', 'last': 'Thomas', 'sap': 'SCA1016', 'unit': 'GRAPE', 'team': '2', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Quinn', 'last': 'Taylor', 'sap': 'SCA1017', 'unit': 'PEACH', 'team': '2', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Rachel', 'last': 'Moore', 'sap': 'SCA1018', 'unit': 'DEMENTIA', 'team': '2', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Sam', 'last': 'Jackson', 'sap': 'SCA1019', 'unit': 'PEACH', 'team': '2', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Tina', 'last': 'Martin', 'sap': 'SCA1020', 'unit': 'BLUE', 'team': '2', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Uma', 'last': 'Lee', 'sap': 'SCA1021', 'unit': 'ORANGE', 'team': '2', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Victor', 'last': 'Perez', 'sap': 'SCA1022', 'unit': 'GREEN', 'team': '2', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Wendy', 'last': 'Thompson', 'sap': 'SCA1023', 'unit': 'VIOLET', 'team': '2', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Xander', 'last': 'White', 'sap': 'SCA1024', 'unit': 'ROSE', 'team': '2', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Yara', 'last': 'Harris', 'sap': 'SCA1025', 'unit': 'GRAPE', 'team': '2', 'shifts_per_week': 2},
            
            # Team 3 - SCW Days
            {'role': 'SCW', 'first': 'Zoe', 'last': 'Sanchez', 'sap': 'SCW1026', 'unit': 'GREEN', 'team': '3', 'shifts_per_week': 3},
            {'role': 'SCW', 'first': 'Aaron', 'last': 'Clark', 'sap': 'SCW1027', 'unit': 'VIOLET', 'team': '3', 'shifts_per_week': 3},
            {'role': 'SCW', 'first': 'Bella', 'last': 'Ramirezz', 'sap': 'SCW1028', 'unit': 'ROSE', 'team': '3', 'shifts_per_week': 3},
            {'role': 'SCW', 'first': 'Caleb', 'last': 'Lewis', 'sap': 'SCW1029', 'unit': 'GRAPE', 'team': '3', 'shifts_per_week': 2},
            {'role': 'SCW', 'first': 'Diana', 'last': 'Robinson', 'sap': 'SCW1030', 'unit': 'PEACH', 'team': '3', 'shifts_per_week': 2},
            {'role': 'SCW', 'first': 'Ethan', 'last': 'Walker', 'sap': 'SCW1031', 'unit': 'DEMENTIA', 'team': '3', 'shifts_per_week': 2},
            {'role': 'SCW', 'first': 'Fiona', 'last': 'Young', 'sap': 'SCW1032', 'unit': 'BLUE', 'team': '3', 'shifts_per_week': 2},
            {'role': 'SCW', 'first': 'George', 'last': 'Allen', 'sap': 'SCW1033', 'unit': 'ORANGE', 'team': '3', 'shifts_per_week': 2},
            {'role': 'SCW', 'first': 'Hannah', 'last': 'King', 'sap': 'SCW1034', 'unit': 'GREEN', 'team': '3', 'shifts_per_week': 2},
            
            # Team 3 - SCA Days
            {'role': 'SCA', 'first': 'Isaac', 'last': 'Wright', 'sap': 'SCA1035', 'unit': 'VIOLET', 'team': '3', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Julia', 'last': 'Scott', 'sap': 'SCA1036', 'unit': 'ROSE', 'team': '3', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Kyle', 'last': 'Torres', 'sap': 'SCA1037', 'unit': 'GRAPE', 'team': '3', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Luna', 'last': 'Nguyen', 'sap': 'SCA1038', 'unit': 'PEACH', 'team': '3', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Mark', 'last': 'Hill', 'sap': 'SCA1039', 'unit': 'DEMENTIA', 'team': '3', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Nora', 'last': 'Green', 'sap': 'SCA1040', 'unit': 'BLUE', 'team': '3', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Oscar', 'last': 'Adams', 'sap': 'SCA1041', 'unit': 'GRAPE', 'team': '3', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Piper', 'last': 'Baker', 'sap': 'SCA1042', 'unit': 'ORANGE', 'team': '3', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Ryan', 'last': 'Nelson', 'sap': 'SCA1043', 'unit': 'GREEN', 'team': '3', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Sophia', 'last': 'Hall', 'sap': 'SCA1044', 'unit': 'VIOLET', 'team': '3', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Tyler', 'last': 'Rivera', 'sap': 'SCA1045', 'unit': 'ROSE', 'team': '3', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Ursula', 'last': 'Campbell', 'sap': 'SCA1046', 'unit': 'GRAPE', 'team': '3', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Vincent', 'last': 'Mitchell', 'sap': 'SCA1047', 'unit': 'PEACH', 'team': '3', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Willow', 'last': 'Carter', 'sap': 'SCA1048', 'unit': 'DEMENTIA', 'team': '3', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Wyatt', 'last': 'Roberts', 'sap': 'SCA1049', 'unit': 'BLUE', 'team': '3', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Xenia', 'last': 'Phillips', 'sap': 'SCA1050', 'unit': 'ORANGE', 'team': '3', 'shifts_per_week': 2},
            
            # Team 1 - SCW Days
            {'role': 'SCW', 'first': 'Yvonne', 'last': 'Evans', 'sap': 'SCW1051', 'unit': 'GRAPE', 'team': '1', 'shifts_per_week': 3},
            {'role': 'SCW', 'first': 'Zachary', 'last': 'Turner', 'sap': 'SCW1052', 'unit': 'PEACH', 'team': '1', 'shifts_per_week': 3},
            {'role': 'SCW', 'first': 'Abigail', 'last': 'Cooper', 'sap': 'SCW1053', 'unit': 'DEMENTIA', 'team': '1', 'shifts_per_week': 3},
            {'role': 'SCW', 'first': 'Ben', 'last': 'Morris', 'sap': 'SCW1054', 'unit': 'BLUE', 'team': '1', 'shifts_per_week': 2},
            {'role': 'SCW', 'first': 'Chloe', 'last': 'Rogers', 'sap': 'SCW1055', 'unit': 'ORANGE', 'team': '1', 'shifts_per_week': 2},
            {'role': 'SCW', 'first': 'Daniel', 'last': 'Cox', 'sap': 'SCW1056', 'unit': 'GREEN', 'team': '1', 'shifts_per_week': 2},
            {'role': 'SCW', 'first': 'Ella', 'last': 'Ward', 'sap': 'SCW1057', 'unit': 'VIOLET', 'team': '1', 'shifts_per_week': 2},
            {'role': 'SCW', 'first': 'Finn', 'last': 'Gray', 'sap': 'SCW1058', 'unit': 'ROSE', 'team': '1', 'shifts_per_week': 2},
            {'role': 'SCW', 'first': 'Gemma', 'last': 'Bell', 'sap': 'SCW1059', 'unit': 'GRAPE', 'team': '1', 'shifts_per_week': 2},
            
            # Team 1 - SCA Days
            {'role': 'SCA', 'first': 'Harry', 'last': 'Coleman', 'sap': 'SCA1060', 'unit': 'PEACH', 'team': '1', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Isabel', 'last': 'Foster', 'sap': 'SCA1061', 'unit': 'DEMENTIA', 'team': '1', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Jacob', 'last': 'Bailey', 'sap': 'SCA1062', 'unit': 'BLUE', 'team': '1', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Katie', 'last': 'Reed', 'sap': 'SCA1063', 'unit': 'ORANGE', 'team': '1', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Leo', 'last': 'Kelly', 'sap': 'SCA1064', 'unit': 'GREEN', 'team': '1', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Megan', 'last': 'Howard', 'sap': 'SCA1065', 'unit': 'VIOLET', 'team': '1', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Nathan', 'last': 'Peterson', 'sap': 'SCA1066', 'unit': 'ROSE', 'team': '1', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Poppy', 'last': 'Cook', 'sap': 'SCA1067', 'unit': 'GRAPE', 'team': '1', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Quentin', 'last': 'Price', 'sap': 'SCA1068', 'unit': 'PEACH', 'team': '1', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Ruby', 'last': 'Barnes', 'sap': 'SCA1069', 'unit': 'DEMENTIA', 'team': '1', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Sebastian', 'last': 'Ross', 'sap': 'SCA1070', 'unit': 'BLUE', 'team': '1', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Taylor', 'last': 'Henderson', 'sap': 'SCA1071', 'unit': 'ORANGE', 'team': '1', 'shifts_per_week': 3},
            {'role': 'SCA', 'first': 'Janice', 'last': 'Henderson', 'sap': 'SCA1079', 'unit': 'GREEN', 'team': '1', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Victor', 'last': 'Watson', 'sap': 'SCA1072', 'unit': 'VIOLET', 'team': '1', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Zoe', 'last': 'Brooks', 'sap': 'SCA1073', 'unit': 'ROSE', 'team': '1', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Adam', 'last': 'Bryant', 'sap': 'SCA1074', 'unit': 'GRAPE', 'team': '1', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Beth', 'last': 'Griffin', 'sap': 'SCA1075', 'unit': 'PEACH', 'team': '1', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Natasha', 'last': 'Jones', 'sap': 'SCA1076', 'unit': 'DEMENTIA', 'team': '1', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Abby', 'last': 'Johnson', 'sap': 'SCA1077', 'unit': 'BLUE', 'team': '1', 'shifts_per_week': 2},
            {'role': 'SCA', 'first': 'Kyle', 'last': 'Oboe', 'sap': 'SCA1078', 'unit': 'ORANGE', 'team': '1', 'shifts_per_week': 2},
        ]
        
        role_map = {
            'SCW': scw_role,
            'SCA': sca_role,
        }
        
        created_count = 0
        updated_count = 0
        
        for data in staff_data:
            sap = data['sap']
            role = role_map[data['role']]
            unit = unit_map[data['unit']]
            
            user, created = User.objects.update_or_create(
                sap=sap,
                defaults={
                    'first_name': data['first'],
                    'last_name': data['last'],
                    'email': f"{data['first'].lower()}.{data['last'].lower()}@staffrota.com",
                    'role': role,
                    'unit': unit,
                    'home_unit': unit,
                    'team': data['team'],
                    'shift_preference': 'DAY_SENIOR' if role.name == 'SCW' else 'DAY_ASSISTANT',
                    'shifts_per_week_override': data['shifts_per_week'],
                    'is_active': True,
                    'is_staff': False,  # Regular staff, not supernumerary
                }
            )
            
            # Set default password
            user.set_password('password123')
            user.save()
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Day shift import complete!'))
        self.stdout.write(self.style.SUCCESS(f'   Created: {created_count} staff'))
        self.stdout.write(self.style.SUCCESS(f'   Updated: {updated_count} staff'))
        self.stdout.write(self.style.SUCCESS(f'   Total: {created_count + updated_count} staff'))
