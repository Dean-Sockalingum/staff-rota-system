from django.core.management.base import BaseCommand
from scheduling.models import User, Role, Unit
from django.db import transaction


class Command(BaseCommand):
    help = 'Import night care staff (SCWN and SCAN) with their details'

    def handle(self, *args, **options):
        # Get roles
        scwn_role = Role.objects.get(name='SCWN')
        scan_role = Role.objects.get(name='SCAN')
        
        # Get units
        units = {name: Unit.objects.get(name=name) for name in [
            'DEMENTIA', 'BLUE', 'ORANGE', 'GREEN', 'VIOLET', 'ROSE', 'GRAPE', 'PEACH'
        ]}
        
        # Night care staff data from spreadsheet: 82 total
        staff_data = [
            # Team 1 - SCWN 35hr (3 shifts/week)
            {'sap': 'SCW1080', 'first_name': 'Jack', 'last_name': 'Henderson', 'role': scwn_role, 'team': '1', 'unit': units['DEMENTIA'], 'shifts': 3},
            {'sap': 'SCW1081', 'first_name': 'Karen', 'last_name': 'Watson', 'role': scwn_role, 'team': '1', 'unit': units['BLUE'], 'shifts': 3},
            # Team 1 - SCWN 24hr (2 shifts/week)
            {'sap': 'SCW1082', 'first_name': 'Liam', 'last_name': 'Brooks', 'role': scwn_role, 'team': '1', 'unit': units['ORANGE'], 'shifts': 2},
            {'sap': 'SCW1083', 'first_name': 'Mia', 'last_name': 'Bryant', 'role': scwn_role, 'team': '1', 'unit': units['GREEN'], 'shifts': 2},
            # Team 1 - SCAN 35hr (3 shifts/week)
            {'sap': 'SCA1084', 'first_name': 'Olivia', 'last_name': 'Jones', 'role': scan_role, 'team': '1', 'unit': units['DEMENTIA'], 'shifts': 3},
            {'sap': 'SCA1085', 'first_name': 'Peter', 'last_name': 'Johnson', 'role': scan_role, 'team': '1', 'unit': units['BLUE'], 'shifts': 3},
            {'sap': 'SCA1086', 'first_name': 'Quinn', 'last_name': 'Oboe', 'role': scan_role, 'team': '1', 'unit': units['ORANGE'], 'shifts': 3},
            {'sap': 'SCA1087', 'first_name': 'Rachel', 'last_name': 'Griffin', 'role': scan_role, 'team': '1', 'unit': units['GREEN'], 'shifts': 3},
            {'sap': 'SCA1088', 'first_name': 'Noah', 'last_name': 'Coleman', 'role': scan_role, 'team': '1', 'unit': units['VIOLET'], 'shifts': 3},
            {'sap': 'SCA1090', 'first_name': 'Sam', 'last_name': 'Foster', 'role': scan_role, 'team': '1', 'unit': units['ROSE'], 'shifts': 3},
            {'sap': 'SCA1091', 'first_name': 'Tina', 'last_name': 'Bailey', 'role': scan_role, 'team': '1', 'unit': units['GRAPE'], 'shifts': 3},
            {'sap': 'SCA1092', 'first_name': 'Uma', 'last_name': 'Reed', 'role': scan_role, 'team': '1', 'unit': units['PEACH'], 'shifts': 3},
            {'sap': 'SCA1093', 'first_name': 'Victor', 'last_name': 'Kelly', 'role': scan_role, 'team': '1', 'unit': units['DEMENTIA'], 'shifts': 3},
            {'sap': 'SCA1094', 'first_name': 'Nora', 'last_name': 'Howard', 'role': scan_role, 'team': '1', 'unit': units['BLUE'], 'shifts': 3},
            {'sap': 'SCA1095', 'first_name': 'Nora', 'last_name': 'Gotyo', 'role': scan_role, 'team': '1', 'unit': units['ORANGE'], 'shifts': 3},
            # Team 1 - SCAN 24hr (2 shifts/week)
            {'sap': 'SCA1096', 'first_name': 'Wendy', 'last_name': 'Barnes', 'role': scan_role, 'team': '1', 'unit': units['DEMENTIA'], 'shifts': 2},
            {'sap': 'SCA1097', 'first_name': 'Xander', 'last_name': 'Ross', 'role': scan_role, 'team': '1', 'unit': units['BLUE'], 'shifts': 2},
            {'sap': 'SCA1098', 'first_name': 'Yara', 'last_name': 'Henderson', 'role': scan_role, 'team': '1', 'unit': units['ORANGE'], 'shifts': 2},
            {'sap': 'SCA1099', 'first_name': 'Zoe', 'last_name': 'Peterson', 'role': scan_role, 'team': '1', 'unit': units['GREEN'], 'shifts': 2},
            {'sap': 'SCA1100', 'first_name': 'Aaron', 'last_name': 'Cook', 'role': scan_role, 'team': '1', 'unit': units['VIOLET'], 'shifts': 2},
            {'sap': 'SCA1101', 'first_name': 'Bella', 'last_name': 'Price', 'role': scan_role, 'team': '1', 'unit': units['ROSE'], 'shifts': 2},
            {'sap': 'SCA1102', 'first_name': 'Ben', 'last_name': 'Nevis', 'role': scan_role, 'team': '1', 'unit': units['GRAPE'], 'shifts': 2},
            {'sap': 'SCA1103', 'first_name': 'Chloe', 'last_name': 'Earlie', 'role': scan_role, 'team': '1', 'unit': units['PEACH'], 'shifts': 2},
            {'sap': 'SCA1104', 'first_name': 'Daniel', 'last_name': 'Cohen', 'role': scan_role, 'team': '1', 'unit': units['VIOLET'], 'shifts': 2},
            {'sap': 'SCA1105', 'first_name': 'Ella', 'last_name': 'Fitzgerald', 'role': scan_role, 'team': '1', 'unit': units['ROSE'], 'shifts': 2},
            {'sap': 'SCA1106', 'first_name': 'Finn', 'last_name': 'Barr', 'role': scan_role, 'team': '1', 'unit': units['GRAPE'], 'shifts': 2},
            
            # Team 2 - SCWN 35hr (3 shifts/week)
            {'sap': 'SCW1108', 'first_name': 'Blessing', 'last_name': 'Oghoa', 'role': scwn_role, 'team': '2', 'unit': units['VIOLET'], 'shifts': 3},
            {'sap': 'SCW1109', 'first_name': 'Peace', 'last_name': 'Sibbald', 'role': scwn_role, 'team': '2', 'unit': units['ROSE'], 'shifts': 3},
            # Team 2 - SCWN 24hr (2 shifts/week)
            {'sap': 'SCW1110', 'first_name': 'JoJo', 'last_name': 'McArthur', 'role': scwn_role, 'team': '2', 'unit': units['GRAPE'], 'shifts': 2},
            {'sap': 'SCW1111', 'first_name': 'Pedro', 'last_name': 'Wallace', 'role': scwn_role, 'team': '2', 'unit': units['PEACH'], 'shifts': 2},
            # Team 2 - SCAN 35hr (3 shifts/week)
            {'sap': 'SCA1112', 'first_name': 'Caleb', 'last_name': 'King', 'role': scan_role, 'team': '2', 'unit': units['VIOLET'], 'shifts': 3},
            {'sap': 'SCA1113', 'first_name': 'Diana', 'last_name': 'Doors', 'role': scan_role, 'team': '2', 'unit': units['ROSE'], 'shifts': 3},
            {'sap': 'SCA1114', 'first_name': 'Ethan', 'last_name': 'Hawke', 'role': scan_role, 'team': '2', 'unit': units['GRAPE'], 'shifts': 3},
            {'sap': 'SCA1115', 'first_name': 'Fiona', 'last_name': 'Bruce', 'role': scan_role, 'team': '2', 'unit': units['PEACH'], 'shifts': 3},
            {'sap': 'SCA1116', 'first_name': 'George', 'last_name': 'Harrison', 'role': scan_role, 'team': '2', 'unit': units['DEMENTIA'], 'shifts': 3},
            {'sap': 'SCA1117', 'first_name': 'Hannah', 'last_name': 'Barbera', 'role': scan_role, 'team': '2', 'unit': units['BLUE'], 'shifts': 3},
            {'sap': 'SCA1118', 'first_name': 'Mark', 'last_name': 'Lewis', 'role': scan_role, 'team': '2', 'unit': units['ORANGE'], 'shifts': 3},
            {'sap': 'SCA1119', 'first_name': 'Isaac', 'last_name': 'Robinson', 'role': scan_role, 'team': '2', 'unit': units['GREEN'], 'shifts': 3},
            {'sap': 'SCA1120', 'first_name': 'Julia', 'last_name': 'Walker', 'role': scan_role, 'team': '2', 'unit': units['DEMENTIA'], 'shifts': 3},
            {'sap': 'SCA1121', 'first_name': 'Kyle', 'last_name': 'Young', 'role': scan_role, 'team': '2', 'unit': units['BLUE'], 'shifts': 3},
            {'sap': 'SCA1122', 'first_name': 'Luna', 'last_name': 'Allen', 'role': scan_role, 'team': '2', 'unit': units['ORANGE'], 'shifts': 3},
            # Team 2 - SCAN 24hr (2 shifts/week)
            {'sap': 'SCA1123', 'first_name': 'Oscar', 'last_name': 'Wright', 'role': scan_role, 'team': '2', 'unit': units['VIOLET'], 'shifts': 2},
            {'sap': 'SCA1124', 'first_name': 'Piper', 'last_name': 'Scott', 'role': scan_role, 'team': '2', 'unit': units['ROSE'], 'shifts': 2},
            {'sap': 'SCA1125', 'first_name': 'Ryan', 'last_name': 'Torres', 'role': scan_role, 'team': '2', 'unit': units['GRAPE'], 'shifts': 2},
            {'sap': 'SCA1126', 'first_name': 'Nathan', 'last_name': 'Nguyen', 'role': scan_role, 'team': '2', 'unit': units['PEACH'], 'shifts': 2},
            {'sap': 'SCA1127', 'first_name': 'Sophia', 'last_name': 'Hill', 'role': scan_role, 'team': '2', 'unit': units['DEMENTIA'], 'shifts': 2},
            {'sap': 'SCA1128', 'first_name': 'Tyler', 'last_name': 'Green', 'role': scan_role, 'team': '2', 'unit': units['BLUE'], 'shifts': 2},
            {'sap': 'SCA1129', 'first_name': 'Ursula', 'last_name': 'Adams', 'role': scan_role, 'team': '2', 'unit': units['ORANGE'], 'shifts': 2},
            {'sap': 'SCA1130', 'first_name': 'Vincent', 'last_name': 'Baker', 'role': scan_role, 'team': '2', 'unit': units['GREEN'], 'shifts': 2},
            {'sap': 'SCA1131', 'first_name': 'Willow', 'last_name': 'Nelson', 'role': scan_role, 'team': '2', 'unit': units['DEMENTIA'], 'shifts': 2},
            {'sap': 'SCA1132', 'first_name': 'Wyatt', 'last_name': 'Earp', 'role': scan_role, 'team': '2', 'unit': units['BLUE'], 'shifts': 2},
            {'sap': 'SCA1133', 'first_name': 'Xenia', 'last_name': 'Warrior', 'role': scan_role, 'team': '2', 'unit': units['ORANGE'], 'shifts': 2},
            {'sap': 'SCA1134', 'first_name': 'Jacqui', 'last_name': 'Swan', 'role': scan_role, 'team': '2', 'unit': units['GRAPE'], 'shifts': 2},
            
            # Team 3 - SCWN 35hr (3 shifts/week)
            {'sap': 'SCW1135', 'first_name': 'Harry', 'last_name': 'Hall', 'role': scwn_role, 'team': '3', 'unit': units['ORANGE'], 'shifts': 3},
            {'sap': 'SCW1136', 'first_name': 'Isabel', 'last_name': 'Rivera', 'role': scwn_role, 'team': '3', 'unit': units['GREEN'], 'shifts': 3},
            # Team 3 - SCWN 24hr (2 shifts/week)
            {'sap': 'SCW1137', 'first_name': 'Jacob', 'last_name': 'Campbell', 'role': scwn_role, 'team': '3', 'unit': units['VIOLET'], 'shifts': 2},
            {'sap': 'SCW1138', 'first_name': 'Katie', 'last_name': 'Mitchell', 'role': scwn_role, 'team': '3', 'unit': units['ROSE'], 'shifts': 2},
            {'sap': 'SCW1139', 'first_name': 'Leo', 'last_name': 'Carter', 'role': scwn_role, 'team': '3', 'unit': units['DEMENTIA'], 'shifts': 2},
            {'sap': 'SCW1140', 'first_name': 'Megan', 'last_name': 'Roberts', 'role': scwn_role, 'team': '3', 'unit': units['BLUE'], 'shifts': 2},
            # Team 3 - SCAN 35hr (3 shifts/week)
            {'sap': 'SCA1141', 'first_name': 'Poppy', 'last_name': 'Saeed', 'role': scan_role, 'team': '3', 'unit': units['DEMENTIA'], 'shifts': 3},
            {'sap': 'SCA1142', 'first_name': 'Quentin', 'last_name': 'Tarant', 'role': scan_role, 'team': '3', 'unit': units['BLUE'], 'shifts': 3},
            {'sap': 'SCA1143', 'first_name': 'Ruby', 'last_name': 'Rubia', 'role': scan_role, 'team': '3', 'unit': units['ORANGE'], 'shifts': 3},
            {'sap': 'SCA1144', 'first_name': 'Sebastian', 'last_name': 'Coen', 'role': scan_role, 'team': '3', 'unit': units['GREEN'], 'shifts': 3},
            {'sap': 'SCA1145', 'first_name': 'Taylor', 'last_name': 'Swifty', 'role': scan_role, 'team': '3', 'unit': units['VIOLET'], 'shifts': 3},
            {'sap': 'SCA1146', 'first_name': 'Janice', 'last_name': 'Evans', 'role': scan_role, 'team': '3', 'unit': units['ROSE'], 'shifts': 3},
            {'sap': 'SCA1147', 'first_name': 'Victor', 'last_name': 'Turner', 'role': scan_role, 'team': '3', 'unit': units['GRAPE'], 'shifts': 3},
            {'sap': 'SCA1148', 'first_name': 'Zoe', 'last_name': 'Cooper', 'role': scan_role, 'team': '3', 'unit': units['PEACH'], 'shifts': 3},
            {'sap': 'SCA1149', 'first_name': 'Adam', 'last_name': 'Phillips', 'role': scan_role, 'team': '3', 'unit': units['GRAPE'], 'shifts': 3},
            {'sap': 'SCA1150', 'first_name': 'Beth', 'last_name': 'Aimes', 'role': scan_role, 'team': '3', 'unit': units['PEACH'], 'shifts': 3},
            {'sap': 'SCA1151', 'first_name': 'Natasha', 'last_name': 'Kaplinski', 'role': scan_role, 'team': '3', 'unit': units['DEMENTIA'], 'shifts': 3},
            {'sap': 'SCA1152', 'first_name': 'Abby', 'last_name': 'Rhodes', 'role': scan_role, 'team': '3', 'unit': units['ROSE'], 'shifts': 3},
            # Team 3 - SCAN 24hr (2 shifts/week)
            {'sap': 'SCA1107', 'first_name': 'Gemma', 'last_name': 'Arthur', 'role': scan_role, 'team': '3', 'unit': units['PEACH'], 'shifts': 2},
            {'sap': 'SCA1153', 'first_name': 'David', 'last_name': 'Morris', 'role': scan_role, 'team': '3', 'unit': units['GREEN'], 'shifts': 2},
            {'sap': 'SCA1154', 'first_name': 'Emily', 'last_name': 'Rogers', 'role': scan_role, 'team': '3', 'unit': units['VIOLET'], 'shifts': 2},
            {'sap': 'SCA1155', 'first_name': 'Frank', 'last_name': 'Cox', 'role': scan_role, 'team': '3', 'unit': units['ROSE'], 'shifts': 2},
            {'sap': 'SCA1156', 'first_name': 'Grace', 'last_name': 'Ward', 'role': scan_role, 'team': '3', 'unit': units['GRAPE'], 'shifts': 2},
            {'sap': 'SCA1157', 'first_name': 'Henry', 'last_name': 'Gray', 'role': scan_role, 'team': '3', 'unit': units['PEACH'], 'shifts': 2},
            {'sap': 'SCA1158', 'first_name': 'Ivy', 'last_name': 'Bell', 'role': scan_role, 'team': '3', 'unit': units['DEMENTIA'], 'shifts': 2},
            {'sap': 'SCA1159', 'first_name': 'Angela', 'last_name': 'Ripton', 'role': scan_role, 'team': '3', 'unit': units['BLUE'], 'shifts': 2},
            {'sap': 'SCA1160', 'first_name': 'Kyle', 'last_name': 'Son Ji', 'role': scan_role, 'team': '3', 'unit': units['ORANGE'], 'shifts': 2},
            {'sap': 'SCA1161', 'first_name': 'Precious', 'last_name': 'Richards', 'role': scan_role, 'team': '3', 'unit': units['ROSE'], 'shifts': 2},
        ]
        
        created_count = 0
        with transaction.atomic():
            for staff in staff_data:
                user, created = User.objects.get_or_create(
                    sap=staff['sap'],
                    defaults={
                        'first_name': staff['first_name'],
                        'last_name': staff['last_name'],
                        'email': f"{staff['sap'].lower()}@facility.com",
                        'role': staff['role'],
                        'team': staff['team'],
                        'unit': staff['unit'],
                        'home_unit': staff['unit'],
                        'shifts_per_week_override': staff['shifts'],
                        'is_staff': False,
                        'is_active': True,
                    }
                )
                if created:
                    created_count += 1
        
        # Summary
        scwn_count = User.objects.filter(role=scwn_role, is_staff=False).count()
        scan_count = User.objects.filter(role=scan_role, is_staff=False).count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Imported {created_count} night care staff\n'
                f'   SCWN: {scwn_count}\n'
                f'   SCAN: {scan_count}\n'
                f'   Total: {scwn_count + scan_count}'
            )
        )
