from django.core.management.base import BaseCommand
from scheduling.models import User, Role, Unit


class Command(BaseCommand):
    help = 'Import night shift SCW and SCA staff'

    def handle(self, *args, **options):
        self.stdout.write('Importing night shift SCW and SCA staff...')
        
        # Night shift staff data
        staff_data = [
            # Team 1 Night Shift
            {'role': 'SCW(N)', 'first': 'Jack', 'last': 'Henderson', 'sap': 'SCW1080', 'hours': 35, 'shifts_per_week': 3, 'unit': 'DEMENTIA', 'team': '1'},
            {'role': 'SCW(N)', 'first': 'Karen', 'last': 'Watson', 'sap': 'SCW1081', 'hours': 35, 'shifts_per_week': 3, 'unit': 'BLUE', 'team': '1'},
            {'role': 'SCW(N)', 'first': 'Liam', 'last': 'Brooks', 'sap': 'SCW1082', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ORANGE', 'team': '1'},
            {'role': 'SCW(N)', 'first': 'Mia', 'last': 'Bryant', 'sap': 'SCW1083', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GREEN', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Olivia', 'last': 'Jones', 'sap': 'SCA1084', 'hours': 35, 'shifts_per_week': 3, 'unit': 'DEMENTIA', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Peter', 'last': 'Johnson', 'sap': 'SCA1085', 'hours': 35, 'shifts_per_week': 3, 'unit': 'BLUE', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Quinn', 'last': 'Oboe', 'sap': 'SCA1086', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ORANGE', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Rachel', 'last': 'Griffin', 'sap': 'SCA1087', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GREEN', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Noah', 'last': 'Coleman', 'sap': 'SCA1088', 'hours': 35, 'shifts_per_week': 3, 'unit': 'VIOLET', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Sam', 'last': 'Foster', 'sap': 'SCA1090', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ROSE', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Tina', 'last': 'Bailey', 'sap': 'SCA1091', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GRAPE', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Uma', 'last': 'Reed', 'sap': 'SCA1092', 'hours': 35, 'shifts_per_week': 3, 'unit': 'PEACH', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Victor', 'last': 'Kelly', 'sap': 'SCA1093', 'hours': 35, 'shifts_per_week': 3, 'unit': 'DEMENTIA', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Nora', 'last': 'Howard', 'sap': 'SCA1094', 'hours': 35, 'shifts_per_week': 3, 'unit': 'BLUE', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Nora', 'last': 'Gotyo', 'sap': 'SCA1095', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ORANGE', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Wendy', 'last': 'Barnes', 'sap': 'SCA1096', 'hours': 24, 'shifts_per_week': 2, 'unit': 'DEMENTIA', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Xander', 'last': 'Ross', 'sap': 'SCA1097', 'hours': 24, 'shifts_per_week': 2, 'unit': 'BLUE', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Yara', 'last': 'Henderson', 'sap': 'SCA1098', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ORANGE', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Zoe', 'last': 'Peterson', 'sap': 'SCA1099', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GREEN', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Aaron', 'last': 'Cook', 'sap': 'SCA1100', 'hours': 24, 'shifts_per_week': 2, 'unit': 'VIOLET', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Bella', 'last': 'Price', 'sap': 'SCA1101', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ROSE', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Ben', 'last': 'Nevis', 'sap': 'SCA1102', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GRAPE', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Chloe', 'last': 'Earlie', 'sap': 'SCA1103', 'hours': 24, 'shifts_per_week': 2, 'unit': 'PEACH', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Daniel', 'last': 'Cohen', 'sap': 'SCA1104', 'hours': 24, 'shifts_per_week': 2, 'unit': 'VIOLET', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Ella', 'last': 'Fitzgerald', 'sap': 'SCA1105', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ROSE', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Finn', 'last': 'Barr', 'sap': 'SCA1106', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GRAPE', 'team': '1'},
            {'role': 'SCA (N)', 'first': 'Gemma', 'last': 'Arthur', 'sap': 'SCA1107', 'hours': 24, 'shifts_per_week': 2, 'unit': 'PEACH', 'team': '1'},
            
            # Team 2 Night Shift
            {'role': 'SCW(N)', 'first': 'Blessing', 'last': 'Oghoa', 'sap': 'SCW1108', 'hours': 35, 'shifts_per_week': 3, 'unit': 'VIOLET', 'team': '2'},
            {'role': 'SCW(N)', 'first': 'Peace', 'last': 'Sibbald', 'sap': 'SCW1109', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ROSE', 'team': '2'},
            {'role': 'SCW(N)', 'first': 'JoJo', 'last': 'McArthur', 'sap': 'SCW1110', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GRAPE', 'team': '2'},
            {'role': 'SCW(N)', 'first': 'Pedro', 'last': 'Wallace', 'sap': 'SCW1111', 'hours': 35, 'shifts_per_week': 2, 'unit': 'PEACH', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Caleb', 'last': 'King', 'sap': 'SCA1112', 'hours': 35, 'shifts_per_week': 3, 'unit': 'VIOLET', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Diana', 'last': 'Doors', 'sap': 'SCA1113', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ROSE', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Ethan', 'last': 'Hawke', 'sap': 'SCA1114', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GRAPE', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Fiona', 'last': 'Bruce', 'sap': 'SCA1115', 'hours': 35, 'shifts_per_week': 3, 'unit': 'PEACH', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'George', 'last': 'Harrison', 'sap': 'SCA1116', 'hours': 35, 'shifts_per_week': 3, 'unit': 'DEMENTIA', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Hannah', 'last': 'Barbera', 'sap': 'SCA1117', 'hours': 35, 'shifts_per_week': 3, 'unit': 'BLUE', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Mark', 'last': 'Lewis', 'sap': 'SCA1118', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ORANGE', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Isaac', 'last': 'Robinson', 'sap': 'SCA1119', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GREEN', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Julia', 'last': 'Walker', 'sap': 'SCA1120', 'hours': 35, 'shifts_per_week': 3, 'unit': 'DEMENTIA', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Kyle', 'last': 'Young', 'sap': 'SCA1121', 'hours': 35, 'shifts_per_week': 3, 'unit': 'BLUE', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Luna', 'last': 'Allen', 'sap': 'SCA1122', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ORANGE', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Oscar', 'last': 'Wright', 'sap': 'SCA1123', 'hours': 24, 'shifts_per_week': 2, 'unit': 'VIOLET', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Piper', 'last': 'Scott', 'sap': 'SCA1124', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ROSE', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Ryan', 'last': 'Torres', 'sap': 'SCA1125', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GRAPE', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Nathan', 'last': 'Nguyen', 'sap': 'SCA1126', 'hours': 24, 'shifts_per_week': 2, 'unit': 'PEACH', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Sophia', 'last': 'Hill', 'sap': 'SCA1127', 'hours': 24, 'shifts_per_week': 2, 'unit': 'DEMENTIA', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Tyler', 'last': 'Green', 'sap': 'SCA1128', 'hours': 24, 'shifts_per_week': 2, 'unit': 'BLUE', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Ursula', 'last': 'Adams', 'sap': 'SCA1129', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ORANGE', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Vincent', 'last': 'Baker', 'sap': 'SCA1130', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GREEN', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Willow', 'last': 'Nelson', 'sap': 'SCA1131', 'hours': 24, 'shifts_per_week': 2, 'unit': 'DEMENTIA', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Wyatt', 'last': 'Earp', 'sap': 'SCA1132', 'hours': 24, 'shifts_per_week': 2, 'unit': 'BLUE', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Xenia', 'last': 'Warrior', 'sap': 'SCA1133', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ORANGE', 'team': '2'},
            {'role': 'SCA (N)', 'first': 'Jacqui', 'last': 'Swan', 'sap': 'SCA1134', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GRAPE', 'team': '2'},
            
            # Team 3 Night Shift
            {'role': 'SCW(N)', 'first': 'Harry', 'last': 'Hall', 'sap': 'SCW1135', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ORANGE', 'team': '3'},
            {'role': 'SCW(N)', 'first': 'Isabel', 'last': 'Rivera', 'sap': 'SCW1136', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GREEN', 'team': '3'},
            {'role': 'SCW(N)', 'first': 'Jacob', 'last': 'Campbell', 'sap': 'SCW1137', 'hours': 24, 'shifts_per_week': 2, 'unit': 'VIOLET', 'team': '3'},
            {'role': 'SCW(N)', 'first': 'Katie', 'last': 'Mitchell', 'sap': 'SCW1138', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ROSE', 'team': '3'},
            {'role': 'SCW(N)', 'first': 'Leo', 'last': 'Carter', 'sap': 'SCW1139', 'hours': 24, 'shifts_per_week': 2, 'unit': 'DEMENTIA', 'team': '3'},
            {'role': 'SCW(N)', 'first': 'Megan', 'last': 'Roberts', 'sap': 'SCW1140', 'hours': 24, 'shifts_per_week': 2, 'unit': 'BLUE', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Poppy', 'last': 'Saeed', 'sap': 'SCA1141', 'hours': 35, 'shifts_per_week': 3, 'unit': 'DEMENTIA', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Quentin', 'last': 'Tarant', 'sap': 'SCA1142', 'hours': 35, 'shifts_per_week': 3, 'unit': 'BLUE', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Ruby', 'last': 'Rubia', 'sap': 'SCA1143', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ORANGE', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Sebastian', 'last': 'Coen', 'sap': 'SCA1144', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GREEN', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Taylor', 'last': 'Swifty', 'sap': 'SCA1145', 'hours': 35, 'shifts_per_week': 3, 'unit': 'VIOLET', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Janice', 'last': 'Evans', 'sap': 'SCA1146', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ROSE', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Victor', 'last': 'Turner', 'sap': 'SCA1147', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GRAPE', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Zoe', 'last': 'Cooper', 'sap': 'SCA1148', 'hours': 35, 'shifts_per_week': 3, 'unit': 'PEACH', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Adam', 'last': 'Phillips', 'sap': 'SCA1149', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GRAPE', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Beth', 'last': 'Aimes', 'sap': 'SCA1150', 'hours': 35, 'shifts_per_week': 3, 'unit': 'PEACH', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Natasha', 'last': 'Kaplinski', 'sap': 'SCA1151', 'hours': 35, 'shifts_per_week': 3, 'unit': 'DEMENTIA', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Abby', 'last': 'Rhodes', 'sap': 'SCA1152', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ROSE', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'David', 'last': 'Morris', 'sap': 'SCA1153', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GREEN', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Emily', 'last': 'Rogers', 'sap': 'SCA1154', 'hours': 24, 'shifts_per_week': 2, 'unit': 'VIOLET', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Frank', 'last': 'Cox', 'sap': 'SCA1155', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ROSE', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Grace', 'last': 'Ward', 'sap': 'SCA1156', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GRAPE', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Henry', 'last': 'Gray', 'sap': 'SCA1157', 'hours': 24, 'shifts_per_week': 2, 'unit': 'PEACH', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Ivy', 'last': 'Bell', 'sap': 'SCA1158', 'hours': 24, 'shifts_per_week': 2, 'unit': 'DEMENTIA', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Angela', 'last': 'Ripton', 'sap': 'SCA1159', 'hours': 24, 'shifts_per_week': 2, 'unit': 'BLUE', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Kyle', 'last': 'Son Ji', 'sap': 'SCA1160', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ORANGE', 'team': '3'},
            {'role': 'SCA (N)', 'first': 'Precious', 'last': 'Richards', 'sap': 'SCA1161', 'hours': 35, 'shifts_per_week': 2, 'unit': 'ROSE', 'team': '3'},
        ]
        
        # Role mapping
        role_map = {
            'SCW(N)': 'SCW',  # Night shift senior care workers use same SCW role
            'SCA (N)': 'SCA',  # Night shift assistants use same SCA role
        }
        
        # Unit mapping - units are stored with uppercase names
        unit_map = {
            'DEMENTIA': 'DEMENTIA',
            'BLUE': 'BLUE',
            'VIOLET': 'VIOLET',
            'ROSE': 'ROSE',
            'GRAPE': 'GRAPE',
            'PEACH': 'PEACH',
            'ORANGE': 'ORANGE',
            'GREEN': 'GREEN',
        }
        
        created_count = 0
        updated_count = 0
        
        for data in staff_data:
            role_name = role_map[data['role']]
            unit_name = unit_map[data['unit']]
            
            role = Role.objects.get(name=role_name)
            unit = Unit.objects.get(name=unit_name)
            
            # Determine shift preference based on role (night shift)
            shift_preference = 'NIGHT_SENIOR' if role.name == 'SCW' else 'NIGHT_ASSISTANT'
            
            user, created = User.objects.update_or_create(
                sap=data['sap'],
                defaults={
                    'first_name': data['first'],
                    'last_name': data['last'],
                    'email': f"{data['first'].lower()}.{data['last'].lower()}@staffrota.com",
                    'role': role,
                    'unit': unit,
                    'home_unit': unit,
                    'team': data['team'],
                    'shift_preference': shift_preference,
                    'shifts_per_week_override': data['shifts_per_week'],
                    'is_active': True,
                    'is_staff': False,  # Regular staff, not supernumerary
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                created_count += 1
            else:
                updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'✅ Night shift import complete! '
            f'Created: {created_count} staff, '
            f'Updated: {updated_count} staff, '
            f'Total: {created_count + updated_count} staff'
        ))
