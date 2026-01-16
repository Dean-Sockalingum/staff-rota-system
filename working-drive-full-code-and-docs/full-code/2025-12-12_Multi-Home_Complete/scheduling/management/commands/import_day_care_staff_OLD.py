from django.core.management.base import BaseCommand
from scheduling.models import User, Role, Unit
from django.db import transaction


class Command(BaseCommand):
    help = 'Import day shift care staff (SCW and SCA) with shift patterns'

    def handle(self, *args, **options):
        # Day shift care staff data
        day_care_staff = [
            # Team 2 (B) - SCW Day
            {'role': 'SCW', 'first': 'Alice', 'surname': 'Smith', 'sap': 'SCW1001', 'hours': 35, 'shifts_per_week': 3, 'unit': 'DEMENTIA', 'team': 'B'},
            {'role': 'SCW', 'first': 'Bob', 'surname': 'Johnson', 'sap': 'SCW1002', 'hours': 35, 'shifts_per_week': 3, 'unit': 'BLUE', 'team': 'B'},
            {'role': 'SCW', 'first': 'Carol', 'surname': 'Williams', 'sap': 'SCW1003', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ORANGE', 'team': 'B'},
            {'role': 'SCW', 'first': 'David', 'surname': 'Brown', 'sap': 'SCW1004', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GREEN', 'team': 'B'},
            {'role': 'SCW', 'first': 'Emily', 'surname': 'Jones', 'sap': 'SCW1005', 'hours': 24, 'shifts_per_week': 2, 'unit': 'VIOLET', 'team': 'B'},
            {'role': 'SCW', 'first': 'Frank', 'surname': 'Garcia', 'sap': 'SCW1006', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ROSE', 'team': 'B'},
            {'role': 'SCW', 'first': 'Grace', 'surname': 'Miller', 'sap': 'SCW1007', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GRAPE', 'team': 'B'},
            {'role': 'SCW', 'first': 'Henry', 'surname': 'Davis', 'sap': 'SCW1008', 'hours': 24, 'shifts_per_week': 2, 'unit': 'PEACH', 'team': 'B'},
            {'role': 'SCW', 'first': 'Ivy', 'surname': 'Rodriguez', 'sap': 'SCW1009', 'hours': 24, 'shifts_per_week': 2, 'unit': 'DEMENTIA', 'team': 'B'},
            
            # Team 2 (B) - SCA Day
            {'role': 'SCA', 'first': 'Jack', 'surname': 'Martinez', 'sap': 'SCA1010', 'hours': 35, 'shifts_per_week': 3, 'unit': 'DEMENTIA', 'team': 'B'},
            {'role': 'SCA', 'first': 'Karen', 'surname': 'Hernandez', 'sap': 'SCA1011', 'hours': 35, 'shifts_per_week': 3, 'unit': 'BLUE', 'team': 'B'},
            {'role': 'SCA', 'first': 'Liam', 'surname': 'Lopez', 'sap': 'SCA1012', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ORANGE', 'team': 'B'},
            {'role': 'SCA', 'first': 'Mia', 'surname': 'Gonzalez', 'sap': 'SCA1013', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GREEN', 'team': 'B'},
            {'role': 'SCA', 'first': 'Noah', 'surname': 'Wilson', 'sap': 'SCA1014', 'hours': 35, 'shifts_per_week': 3, 'unit': 'VIOLET', 'team': 'B'},
            {'role': 'SCA', 'first': 'Olivia', 'surname': 'Anderson', 'sap': 'SCA1015', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ROSE', 'team': 'B'},
            {'role': 'SCA', 'first': 'Peter', 'surname': 'Thomas', 'sap': 'SCA1016', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GRAPE', 'team': 'B'},
            {'role': 'SCA', 'first': 'Quinn', 'surname': 'Taylor', 'sap': 'SCA1017', 'hours': 35, 'shifts_per_week': 3, 'unit': 'PEACH', 'team': 'B'},
            {'role': 'SCA', 'first': 'Rachel', 'surname': 'Moore', 'sap': 'SCA1018', 'hours': 35, 'shifts_per_week': 3, 'unit': 'DEMENTIA', 'team': 'B'},
            {'role': 'SCA', 'first': 'Sam', 'surname': 'Jackson', 'sap': 'SCA1019', 'hours': 24, 'shifts_per_week': 2, 'unit': 'PEACH', 'team': 'B'},
            {'role': 'SCA', 'first': 'Tina', 'surname': 'Martin', 'sap': 'SCA1020', 'hours': 24, 'shifts_per_week': 2, 'unit': 'BLUE', 'team': 'B'},
            {'role': 'SCA', 'first': 'Uma', 'surname': 'Lee', 'sap': 'SCA1021', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ORANGE', 'team': 'B'},
            {'role': 'SCA', 'first': 'Victor', 'surname': 'Perez', 'sap': 'SCA1022', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GREEN', 'team': 'B'},
            {'role': 'SCA', 'first': 'Wendy', 'surname': 'Thompson', 'sap': 'SCA1023', 'hours': 24, 'shifts_per_week': 2, 'unit': 'VIOLET', 'team': 'B'},
            {'role': 'SCA', 'first': 'Xander', 'surname': 'White', 'sap': 'SCA1024', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ROSE', 'team': 'B'},
            {'role': 'SCA', 'first': 'Yara', 'surname': 'Harris', 'sap': 'SCA1025', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GRAPE', 'team': 'B'},
            
            # Team 3 (C) - SCW Day
            {'role': 'SCW', 'first': 'Zoe', 'surname': 'Sanchez', 'sap': 'SCW1026', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GREEN', 'team': 'C'},
            {'role': 'SCW', 'first': 'Aaron', 'surname': 'Clark', 'sap': 'SCW1027', 'hours': 35, 'shifts_per_week': 3, 'unit': 'VIOLET', 'team': 'C'},
            {'role': 'SCW', 'first': 'Bella', 'surname': 'Ramirezz', 'sap': 'SCW1028', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ROSE', 'team': 'C'},
            {'role': 'SCW', 'first': 'Caleb', 'surname': 'Lewis', 'sap': 'SCW1029', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GRAPE', 'team': 'C'},
            {'role': 'SCW', 'first': 'Diana', 'surname': 'Robinson', 'sap': 'SCW1030', 'hours': 24, 'shifts_per_week': 2, 'unit': 'PEACH', 'team': 'C'},
            {'role': 'SCW', 'first': 'Ethan', 'surname': 'Walker', 'sap': 'SCW1031', 'hours': 24, 'shifts_per_week': 2, 'unit': 'DEMENTIA', 'team': 'C'},
            {'role': 'SCW', 'first': 'Fiona', 'surname': 'Young', 'sap': 'SCW1032', 'hours': 24, 'shifts_per_week': 2, 'unit': 'BLUE', 'team': 'C'},
            {'role': 'SCW', 'first': 'George', 'surname': 'Allen', 'sap': 'SCW1033', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ORANGE', 'team': 'C'},
            {'role': 'SCW', 'first': 'Hannah', 'surname': 'King', 'sap': 'SCW1034', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GREEN', 'team': 'C'},
            
            # Team 3 (C) - SCA Day
            {'role': 'SCA', 'first': 'Isaac', 'surname': 'Wright', 'sap': 'SCA1035', 'hours': 35, 'shifts_per_week': 3, 'unit': 'VIOLET', 'team': 'C'},
            {'role': 'SCA', 'first': 'Julia', 'surname': 'Scott', 'sap': 'SCA1036', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ROSE', 'team': 'C'},
            {'role': 'SCA', 'first': 'Kyle', 'surname': 'Torres', 'sap': 'SCA1037', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GRAPE', 'team': 'C'},
            {'role': 'SCA', 'first': 'Luna', 'surname': 'Nguyen', 'sap': 'SCA1038', 'hours': 35, 'shifts_per_week': 3, 'unit': 'PEACH', 'team': 'C'},
            {'role': 'SCA', 'first': 'Mark', 'surname': 'Hill', 'sap': 'SCA1039', 'hours': 35, 'shifts_per_week': 3, 'unit': 'DEMENTIA', 'team': 'C'},
            {'role': 'SCA', 'first': 'Nora', 'surname': 'Green', 'sap': 'SCA1040', 'hours': 35, 'shifts_per_week': 3, 'unit': 'BLUE', 'team': 'C'},
            {'role': 'SCA', 'first': 'Oscar', 'surname': 'Adams', 'sap': 'SCA1041', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GRAPE', 'team': 'C'},
            {'role': 'SCA', 'first': 'Piper', 'surname': 'Baker', 'sap': 'SCA1042', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ORANGE', 'team': 'C'},
            {'role': 'SCA', 'first': 'Ryan', 'surname': 'Nelson', 'sap': 'SCA1043', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GREEN', 'team': 'C'},
            {'role': 'SCA', 'first': 'Sophia', 'surname': 'Hall', 'sap': 'SCA1044', 'hours': 24, 'shifts_per_week': 2, 'unit': 'VIOLET', 'team': 'C'},
            {'role': 'SCA', 'first': 'Tyler', 'surname': 'Rivera', 'sap': 'SCA1045', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ROSE', 'team': 'C'},
            {'role': 'SCA', 'first': 'Ursula', 'surname': 'Campbell', 'sap': 'SCA1046', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GRAPE', 'team': 'C'},
            {'role': 'SCA', 'first': 'Vincent', 'surname': 'Mitchell', 'sap': 'SCA1047', 'hours': 24, 'shifts_per_week': 2, 'unit': 'PEACH', 'team': 'C'},
            {'role': 'SCA', 'first': 'Willow', 'surname': 'Carter', 'sap': 'SCA1048', 'hours': 24, 'shifts_per_week': 2, 'unit': 'DEMENTIA', 'team': 'C'},
            {'role': 'SCA', 'first': 'Wyatt', 'surname': 'Roberts', 'sap': 'SCA1049', 'hours': 24, 'shifts_per_week': 2, 'unit': 'BLUE', 'team': 'C'},
            {'role': 'SCA', 'first': 'Xenia', 'surname': 'Phillips', 'sap': 'SCA1050', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ORANGE', 'team': 'C'},
            
            # Team 1 (A) - SCW Day
            {'role': 'SCW', 'first': 'Yvonne', 'surname': 'Evans', 'sap': 'SCW1051', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GRAPE', 'team': 'A'},
            {'role': 'SCW', 'first': 'Zachary', 'surname': 'Turner', 'sap': 'SCW1052', 'hours': 35, 'shifts_per_week': 3, 'unit': 'PEACH', 'team': 'A'},
            {'role': 'SCW', 'first': 'Abigail', 'surname': 'Cooper', 'sap': 'SCW1053', 'hours': 35, 'shifts_per_week': 3, 'unit': 'DEMENTIA', 'team': 'A'},
            {'role': 'SCW', 'first': 'Ben', 'surname': 'Morris', 'sap': 'SCW1054', 'hours': 24, 'shifts_per_week': 2, 'unit': 'BLUE', 'team': 'A'},
            {'role': 'SCW', 'first': 'Chloe', 'surname': 'Rogers', 'sap': 'SCW1055', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ORANGE', 'team': 'A'},
            {'role': 'SCW', 'first': 'Daniel', 'surname': 'Cox', 'sap': 'SCW1056', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GREEN', 'team': 'A'},
            {'role': 'SCW', 'first': 'Ella', 'surname': 'Ward', 'sap': 'SCW1057', 'hours': 24, 'shifts_per_week': 2, 'unit': 'VIOLET', 'team': 'A'},
            {'role': 'SCW', 'first': 'Finn', 'surname': 'Gray', 'sap': 'SCW1058', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ROSE', 'team': 'A'},
            {'role': 'SCW', 'first': 'Gemma', 'surname': 'Bell', 'sap': 'SCW1059', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GRAPE', 'team': 'A'},
            
            # Team 1 (A) - SCA Day
            {'role': 'SCA', 'first': 'Harry', 'surname': 'Coleman', 'sap': 'SCA1060', 'hours': 35, 'shifts_per_week': 3, 'unit': 'PEACH', 'team': 'A'},
            {'role': 'SCA', 'first': 'Isabel', 'surname': 'Foster', 'sap': 'SCA1061', 'hours': 35, 'shifts_per_week': 3, 'unit': 'DEMENTIA', 'team': 'A'},
            {'role': 'SCA', 'first': 'Jacob', 'surname': 'Bailey', 'sap': 'SCA1062', 'hours': 35, 'shifts_per_week': 3, 'unit': 'BLUE', 'team': 'A'},
            {'role': 'SCA', 'first': 'Katie', 'surname': 'Reed', 'sap': 'SCA1063', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ORANGE', 'team': 'A'},
            {'role': 'SCA', 'first': 'Leo', 'surname': 'Kelly', 'sap': 'SCA1064', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GREEN', 'team': 'A'},
            {'role': 'SCA', 'first': 'Megan', 'surname': 'Howard', 'sap': 'SCA1065', 'hours': 35, 'shifts_per_week': 3, 'unit': 'VIOLET', 'team': 'A'},
            {'role': 'SCA', 'first': 'Nathan', 'surname': 'Peterson', 'sap': 'SCA1066', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ROSE', 'team': 'A'},
            {'role': 'SCA', 'first': 'Poppy', 'surname': 'Cook', 'sap': 'SCA1067', 'hours': 35, 'shifts_per_week': 3, 'unit': 'GRAPE', 'team': 'A'},
            {'role': 'SCA', 'first': 'Quentin', 'surname': 'Price', 'sap': 'SCA1068', 'hours': 35, 'shifts_per_week': 3, 'unit': 'PEACH', 'team': 'A'},
            {'role': 'SCA', 'first': 'Ruby', 'surname': 'Barnes', 'sap': 'SCA1069', 'hours': 35, 'shifts_per_week': 3, 'unit': 'DEMENTIA', 'team': 'A'},
            {'role': 'SCA', 'first': 'Sebastian', 'surname': 'Ross', 'sap': 'SCA1070', 'hours': 35, 'shifts_per_week': 3, 'unit': 'BLUE', 'team': 'A'},
            {'role': 'SCA', 'first': 'Taylor', 'surname': 'Henderson', 'sap': 'SCA1071', 'hours': 35, 'shifts_per_week': 3, 'unit': 'ORANGE', 'team': 'A'},
            {'role': 'SCA', 'first': 'Janice', 'surname': 'Henderson', 'sap': 'SCA1079', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GREEN', 'team': 'A'},
            {'role': 'SCA', 'first': 'Victor', 'surname': 'Watson', 'sap': 'SCA1072', 'hours': 24, 'shifts_per_week': 2, 'unit': 'VIOLET', 'team': 'A'},
            {'role': 'SCA', 'first': 'Zoe', 'surname': 'Brooks', 'sap': 'SCA1073', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ROSE', 'team': 'A'},
            {'role': 'SCA', 'first': 'Adam', 'surname': 'Bryant', 'sap': 'SCA1074', 'hours': 24, 'shifts_per_week': 2, 'unit': 'GRAPE', 'team': 'A'},
            {'role': 'SCA', 'first': 'Beth', 'surname': 'Griffin', 'sap': 'SCA1075', 'hours': 24, 'shifts_per_week': 2, 'unit': 'PEACH', 'team': 'A'},
            {'role': 'SCA', 'first': 'Natasha', 'surname': 'Jones', 'sap': 'SCA1076', 'hours': 24, 'shifts_per_week': 2, 'unit': 'DEMENTIA', 'team': 'A'},
            {'role': 'SCA', 'first': 'Abby', 'surname': 'Johnson', 'sap': 'SCA1077', 'hours': 24, 'shifts_per_week': 2, 'unit': 'BLUE', 'team': 'A'},
            {'role': 'SCA', 'first': 'Kyle', 'surname': 'Oboe', 'sap': 'SCA1078', 'hours': 24, 'shifts_per_week': 2, 'unit': 'ORANGE', 'team': 'A'},
        ]

        with transaction.atomic():
            # Ensure SCW and SCA roles exist
            scw_role, _ = Role.objects.get_or_create(
                name='SCW',
                defaults={
                    'color_code': '#90EE90',  # Light green
                    'is_management': False
                }
            )
            sca_role, _ = Role.objects.get_or_create(
                name='SCA',
                defaults={
                    'color_code': '#DDA0DD',  # Light purple
                    'is_management': False
                }
            )

            created_count = 0
            updated_count = 0

            for staff in day_care_staff:
                role = Role.objects.get(name=staff['role'])
                unit = Unit.objects.get(name=staff['unit'])
                
                # Generate unique email
                email = f"{staff['sap'].lower()}@staffrota.com"
                
                user, created = User.objects.update_or_create(
                    sap=staff['sap'],
                    defaults={
                        'first_name': staff['first'],
                        'last_name': staff['surname'],
                        'email': email,
                        'role': role,
                        'unit': unit,
                        'home_unit': unit,
                        'team': staff['team'],
                        'is_staff': False,
                        'is_active': True,
                        'shifts_per_week_override': staff['shifts_per_week']
                    }
                )
                
                if created:
                    user.set_password('password123')
                    user.save()
                    created_count += 1
                else:
                    updated_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Day Care Staff Import Complete!\n'
                    f'Created: {created_count} staff\n'
                    f'Updated: {updated_count} staff\n'
                    f'Total: {created_count + updated_count} day care staff\n'
                )
            )
            
            # Summary by team and role
            self.stdout.write('\n--- Summary by Team and Role ---')
            for team in ['A', 'B', 'C']:
                scw_count = User.objects.filter(team=team, role__name='SCW', is_staff=False).count()
                sca_count = User.objects.filter(team=team, role__name='SCA', is_staff=False).count()
                self.stdout.write(f'Team {team}: {scw_count} SCW + {sca_count} SCA = {scw_count + sca_count} total')
