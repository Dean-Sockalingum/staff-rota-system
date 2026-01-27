from django.core.management.base import BaseCommand
from scheduling.models import User, Shift, Role, Unit
from django.db import transaction

# Embedded staff data: (team, role, first, last, sap, shifts_per_week, unit, pattern)
staff_data = [
    # TEAM A
    ("A", "SCW", "Alice", "Smith", "SCW1001", 3, "DEMENTIA", [[0,0,0,1,0,1,1],[1,0,0,1,1,0,0],[0,1,1,1,0,0,0]]),
    ("A", "SCW", "Bob", "Johnson", "SCW1002", 3, "BLUE", [[0,0,0,1,0,1,1],[1,0,0,1,1,0,0],[0,1,1,1,0,0,0]]),
    ("A", "SCW", "Carol", "Williams", "SCW1003", 3, "ORANGE", [[0,0,0,1,0,1,1],[1,0,0,1,1,0,0],[0,1,1,1,0,0,0]]),
    ("A", "SCW", "David", "Brown", "SCW1004", 2, "GREEN", [[0,0,0,0,0,1,1],[1,0,0,0,1,0,0],[0,1,1,0,0,0,0]]),
    ("A", "SCW", "Emily", "Jones", "SCW1005", 2, "VIOLET", [[0,0,0,0,0,1,1],[1,0,0,0,1,0,0],[0,1,1,0,0,0,0]]),
    ("A", "SCW", "Frank", "Garcia", "SCW1006", 2, "ROSE", [[0,0,0,0,0,1,1],[1,0,0,0,1,0,0],[0,1,1,0,0,0,0]]),
    ("A", "SCW", "Grace", "Miller", "SCW1007", 2, "GRAPE", [[0,0,0,0,0,1,1],[1,0,0,0,1,0,0],[0,1,1,0,0,0,0]]),
    ("A", "SCW", "Henry", "Davis", "SCW1008", 2, "PEACH", [[0,0,0,0,0,1,1],[1,0,0,0,1,0,0],[0,1,1,0,0,0,0]]),
    ("A", "SCW", "Ivy", "Rodriguez", "SCW1009", 2, "DEMENTIA", [[0,0,0,0,0,1,1],[1,0,0,0,1,0,0],[0,1,1,0,0,0,0]]),
    ("A", "SCA", "Jack", "Martinez", "SCA1010", 3, "DEMENTIA", [[0,0,0,1,0,1,1],[1,0,0,1,1,0,0],[0,1,1,1,0,0,0]]),
    ("A", "SCA", "Karen", "Hernandez", "SCA1011", 3, "BLUE", [[0,0,0,1,0,1,1],[1,0,0,1,1,0,0],[0,1,1,1,0,0,0]]),
    ("A", "SCA", "Liam", "Lopez", "SCA1012", 3, "ORANGE", [[0,0,0,1,0,1,1],[1,0,0,1,1,0,0],[0,1,1,1,0,0,0]]),
    ("A", "SCA", "Mia", "Gonzalez", "SCA1013", 3, "GREEN", [[0,0,0,1,0,1,1],[1,0,0,1,1,0,0],[0,1,1,1,0,0,0]]),
    ("A", "SCA", "Noah", "Wilson", "SCA1014", 3, "VIOLET", [[0,0,0,1,0,1,1],[1,0,0,1,1,0,0],[0,1,1,1,0,0,0]]),
    ("A", "SCA", "Olivia", "Anderson", "SCA1015", 3, "ROSE", [[0,0,0,1,0,1,1],[1,0,0,1,1,0,0],[0,1,1,1,0,0,0]]),
    ("A", "SCA", "Peter", "Thomas", "SCA1016", 3, "GRAPE", [[0,0,0,1,0,1,1],[1,0,0,1,1,0,0],[0,1,1,1,0,0,0]]),
    ("A", "SCA", "Quinn", "Taylor", "SCA1017", 3, "PEACH", [[0,0,0,1,0,1,1],[1,0,0,1,1,0,0],[0,1,1,1,0,0,0]]),
    ("A", "SCA", "Rachel", "Moore", "SCA1018", 3, "DEMENTIA", [[0,0,0,1,0,1,1],[1,0,0,1,1,0,0],[0,1,1,1,0,0,0]]),
    ("A", "SCA", "Sam", "Jackson", "SCA1019", 2, "PEACH", [[0,0,0,0,0,1,1],[1,0,0,0,1,0,0],[0,1,1,0,0,0,0]]),
    ("A", "SCA", "Tina", "Martin", "SCA1020", 2, "BLUE", [[0,0,0,0,0,1,1],[1,0,0,0,1,0,0],[0,1,1,0,0,0,0]]),
    ("A", "SCA", "Uma", "Lee", "SCA1021", 2, "ORANGE", [[0,0,0,0,0,1,1],[1,0,0,0,1,0,0],[0,1,1,0,0,0,0]]),
    ("A", "SCA", "Victor", "Perez", "SCA1022", 2, "GREEN", [[0,0,0,0,0,1,1],[1,0,0,0,1,0,0],[0,1,1,0,0,0,0]]),
    ("A", "SCA", "Wendy", "Thompson", "SCA1023", 2, "VIOLET", [[0,0,0,0,0,1,1],[1,0,0,0,1,0,0],[0,1,1,0,0,0,0]]),
    ("A", "SCA", "Xander", "White", "SCA1024", 2, "ROSE", [[0,0,0,0,0,1,1],[1,0,0,0,1,0,0],[0,1,1,0,0,0,0]]),
    ("A", "SCA", "Yara", "Harris", "SCA1025", 2, "GRAPE", [[0,0,0,0,0,1,1],[1,0,0,0,1,0,0],[0,1,1,0,0,0,0]]),
    # TEAM B
    ("B", "SCW", "Zoe", "Sanchez", "SCW1026", 3, "GREEN", [[1,0,0,1,1,0,0],[0,1,1,1,0,0,0],[0,0,1,0,1,1,0]]),
    ("B", "SCW", "Aaron", "Clark", "SCW1027", 3, "VIOLET", [[1,0,0,1,1,0,0],[0,1,1,1,0,0,0],[0,0,1,0,1,1,0]]),
    ("B", "SCW", "Bella", "Ramirezz", "SCW1028", 3, "ROSE", [[1,0,0,1,1,0,0],[0,1,1,1,0,0,0],[0,0,1,0,1,1,0]]),
    ("B", "SCW", "Caleb", "Lewis", "SCW1029", 2, "GRAPE", [[1,0,0,0,1,0,0],[0,1,1,0,0,0,0],[0,0,0,0,0,1,1]]),
    ("B", "SCW", "Diana", "Robinson", "SCW1030", 2, "PEACH", [[1,0,0,0,1,0,0],[0,1,1,0,0,0,0],[0,0,0,0,0,1,1]]),
    ("B", "SCW", "Ethan", "Walker", "SCW1031", 2, "DEMENTIA", [[1,0,0,0,1,0,0],[0,1,1,0,0,0,0],[0,0,0,0,0,1,1]]),
    ("B", "SCW", "Fiona", "Young", "SCW1032", 2, "BLUE", [[1,0,0,0,1,0,0],[0,1,1,0,0,0,0],[0,0,0,0,0,1,1]]),
    ("B", "SCW", "George", "Allen", "SCW1033", 2, "ORANGE", [[1,0,0,0,1,0,0],[0,1,1,0,0,0,0],[0,0,0,0,0,1,1]]),
    ("B", "SCW", "Hannah", "King", "SCW1034", 2, "GREEN", [[1,0,0,0,1,0,0],[0,1,1,0,0,0,0],[0,0,0,0,0,1,1]]),
    ("B", "SCA", "Isaac", "Wright", "SCA1035", 3, "VIOLET", [[1,0,0,1,1,0,0],[0,1,1,1,0,0,0],[0,0,1,0,1,1,0]]),
    ("B", "SCA", "Julia", "Scott", "SCA1036", 3, "ROSE", [[1,0,0,1,1,0,0],[0,1,1,1,0,0,0],[0,0,1,0,1,1,0]]),
    ("B", "SCA", "Kyle", "Torres", "SCA1037", 3, "GRAPE", [[1,0,0,1,1,0,0],[0,1,1,1,0,0,0],[0,0,1,0,1,1,0]]),
    ("B", "SCA", "Luna", "Nguyen", "SCA1038", 3, "PEACH", [[1,0,0,1,1,0,0],[0,1,1,1,0,0,0],[0,0,1,0,1,1,0]]),
    ("B", "SCA", "Mark", "Hill", "SCA1039", 3, "DEMENTIA", [[1,0,0,1,1,0,0],[0,1,1,1,0,0,0],[0,0,1,0,1,1,0]]),
    ("B", "SCA", "Nora", "Green", "SCA1040", 3, "BLUE", [[1,0,0,1,1,0,0],[0,1,1,1,0,0,0],[0,0,1,0,1,1,0]]),
    ("B", "SCA", "Oscar", "Adams", "SCA1041", 3, "GRAPE", [[1,0,0,1,1,0,0],[0,1,1,1,0,0,0],[0,0,1,0,1,1,0]]),
    ("B", "SCA", "Piper", "Baker", "SCA1042", 3, "ORANGE", [[1,0,0,1,1,0,0],[0,1,1,1,0,0,0],[0,0,1,0,1,1,0]]),
    ("B", "SCA", "Ryan", "Nelson", "SCA1043", 3, "GREEN", [[1,0,0,1,1,0,0],[0,1,1,1,0,0,0],[0,0,1,0,1,1,0]]),
    ("B", "SCA", "Sophia", "Hall", "SCA1044", 2, "VIOLET", [[1,0,0,0,1,0,0],[0,1,1,0,0,0,0],[0,0,0,0,0,1,1]]),
    ("B", "SCA", "Tyler", "Rivera", "SCA1045", 2, "ROSE", [[1,0,0,0,1,0,0],[0,1,1,0,0,0,0],[0,0,0,0,0,1,1]]),
    ("B", "SCA", "Ursula", "Campbell", "SCA1046", 2, "GRAPE", [[1,0,0,0,1,0,0],[0,1,1,0,0,0,0],[0,0,0,0,0,1,1]]),
    ("B", "SCA", "Vincent", "Mitchell", "SCA1047", 2, "PEACH", [[1,0,0,0,1,0,0],[0,1,1,0,0,0,0],[0,0,0,0,0,1,1]]),
    ("B", "SCA", "Willow", "Carter", "SCA1048", 2, "DEMENTIA", [[1,0,0,0,1,0,0],[0,1,1,0,0,0,0],[0,0,0,0,0,1,1]]),
    ("B", "SCA", "Wyatt", "Roberts", "SCA1049", 2, "BLUE", [[1,0,0,0,1,0,0],[0,1,1,0,0,0,0],[0,0,0,0,0,1,1]]),
    ("B", "SCA", "Xenia", "Phillips", "SCA1050", 2, "ORANGE", [[1,0,0,0,1,0,0],[0,1,1,0,0,0,0],[0,0,0,0,0,1,1]]),
    # TEAM C
    ("C", "SCW", "Yvonne", "Evans", "SCW1051", 3, "GRAPE", [[0,1,1,1,0,0,0],[0,0,0,1,0,1,1],[1,0,0,0,1,1,0]]),
    ("C", "SCW", "Zachary", "Turner", "SCW1052", 3, "PEACH", [[0,1,1,1,0,0,0],[0,0,0,1,0,1,1],[1,0,0,0,1,1,0]]),
    ("C", "SCW", "Abigail", "Cooper", "SCW1053", 3, "DEMENTIA", [[0,1,1,1,0,0,0],[0,0,0,1,0,1,1],[1,0,0,0,1,1,0]]),
    ("C", "SCW", "Ben", "Morris", "SCW1054", 2, "BLUE", [[0,1,1,0,0,0,0],[0,0,0,0,0,1,1],[1,0,0,0,0,0,1]]),
    ("C", "SCW", "Chloe", "Rogers", "SCW1055", 2, "ORANGE", [[0,1,1,0,0,0,0],[0,0,0,0,0,1,1],[1,0,0,0,0,0,1]]),
    ("C", "SCW", "Daniel", "Cox", "SCW1056", 2, "GREEN", [[0,1,1,0,0,0,0],[0,0,0,0,0,1,1],[1,0,0,0,0,0,1]]),
    ("C", "SCW", "Ella", "Ward", "SCW1057", 2, "VIOLET", [[0,1,1,0,0,0,0],[0,0,0,0,0,1,1],[1,0,0,0,0,0,1]]),
    ("C", "SCW", "Finn", "Gray", "SCW1058", 2, "ROSE", [[0,1,1,0,0,0,0],[0,0,0,0,0,1,1],[1,0,0,0,0,0,1]]),
    ("C", "SCW", "Gemma", "Bell", "SCW1059", 2, "GRAPE", [[0,1,1,0,0,0,0],[0,0,0,0,0,1,1],[1,0,0,0,0,0,1]]),
    ("C", "SCA", "Harry", "Coleman", "SCA1060", 3, "PEACH", [[0,1,1,1,0,0,0],[0,0,0,1,0,1,1],[1,0,0,0,1,1,0]]),
    ("C", "SCA", "Isabel", "Foster", "SCA1061", 3, "DEMENTIA", [[0,1,1,1,0,0,0],[0,0,0,1,0,1,1],[1,0,0,0,1,1,0]]),
    ("C", "SCA", "Jacob", "Bailey", "SCA1062", 3, "BLUE", [[0,1,1,1,0,0,0],[0,0,0,1,0,1,1],[1,0,0,0,1,1,0]]),
    ("C", "SCA", "Katie", "Reed", "SCA1063", 3, "ORANGE", [[0,1,1,1,0,0,0],[0,0,0,1,0,1,1],[1,0,0,0,1,1,0]]),
    ("C", "SCA", "Leo", "Kelly", "SCA1064", 3, "GREEN", [[0,1,1,1,0,0,0],[0,0,0,1,0,1,1],[1,0,0,0,1,1,0]]),
    ("C", "SCA", "Megan", "Howard", "SCA1065", 3, "VIOLET", [[0,1,1,1,0,0,0],[0,0,0,1,0,1,1],[1,0,0,0,1,1,0]]),
    ("C", "SCA", "Nathan", "Peterson", "SCA1066", 3, "ROSE", [[0,1,1,1,0,0,0],[0,0,0,1,0,1,1],[1,0,0,0,1,1,0]]),
    ("C", "SCA", "Poppy", "Cook", "SCA1067", 3, "GRAPE", [[0,1,1,1,0,0,0],[0,0,0,1,0,1,1],[1,0,0,0,1,1,0]]),
    ("C", "SCA", "Quentin", "Price", "SCA1068", 3, "PEACH", [[0,1,1,1,0,0,0],[0,0,0,1,0,1,1],[1,0,0,0,1,1,0]]),
    ("C", "SCA", "Ruby", "Barnes", "SCA1069", 3, "DEMENTIA", [[0,1,1,1,0,0,0],[0,0,0,1,0,1,1],[1,0,0,0,1,1,0]]),
    ("C", "SCA", "Sebastian", "Ross", "SCA1070", 3, "BLUE", [[0,1,1,1,0,0,0],[0,0,0,1,0,1,1],[1,0,0,0,1,1,0]]),
    ("C", "SCA", "Taylor", "Henderson", "SCA1071", 3, "ORANGE", [[0,1,1,1,0,0,0],[0,0,0,1,0,1,1],[1,0,0,0,1,1,0]]),
    ("C", "SCA", "Janice", "Henderson", "SCA1079", 2, "GREEN", [[0,1,1,0,0,0,0],[0,0,0,0,0,1,1],[1,0,0,0,0,0,1]]),
    ("C", "SCA", "Victor", "Watson", "SCA1072", 2, "VIOLET", [[0,1,1,0,0,0,0],[0,0,0,0,0,1,1],[1,0,0,0,0,0,1]]),
    ("C", "SCA", "Zoe", "Brooks", "SCA1073", 2, "ROSE", [[0,1,1,0,0,0,0],[0,0,0,0,0,1,1],[1,0,0,0,0,0,1]]),
    ("C", "SCA", "Adam", "Bryant", "SCA1074", 2, "GRAPE", [[0,1,1,0,0,0,0],[0,0,0,0,0,1,1],[1,0,0,0,0,0,1]]),
    ("C", "SCA", "Beth", "Griffin", "SCA1075", 2, "PEACH", [[0,1,1,0,0,0,0],[0,0,0,0,0,1,1],[1,0,0,0,0,0,1]]),
    ("C", "SCA", "Natasha", "Jones", "SCA1076", 2, "DEMENTIA", [[0,1,1,0,0,0,0],[0,0,0,0,0,1,1],[1,0,0,0,0,0,1]]),
    ("C", "SCA", "Abby", "Johnson", "SCA1077", 2, "BLUE", [[0,1,1,0,0,0,0],[0,0,0,0,0,1,1],[1,0,0,0,0,0,1]]),
    ("C", "SCA", "Kyle", "Oboe", "SCA1078", 2, "ORANGE", [[0,1,1,0,0,0,0],[0,0,0,0,0,1,1],[1,0,0,0,0,0,1]]),
]

class Command(BaseCommand):
    help = 'Import and align SCW/SCA day staff with roles, SAP, and shift patterns.'

    def handle(self, *args, **options):
        with transaction.atomic():
            class Command(BaseCommand):
                help = 'Import and align SCW/SCA day staff with roles, SAP, and shift patterns.'

                def handle(self, *args, **options):
                    with transaction.atomic():
                        # Remove all existing SCW/SCA day staff and their shifts
                        users = User.objects.filter(role__name__in=["SCW", "SCA"], shift_preference__contains="DAY")
                        Shift.objects.filter(user__in=users).delete()
                        users.delete()

                        # Import new staff
                        from datetime import date, timedelta
                        start_date = date(2026, 1, 4)  # Sunday
                        from scheduling.models import ShiftType
                        from datetime import time
                        day_shift_type, _ = ShiftType.objects.get_or_create(
                            name="DAY",
                            defaults={
                                "start_time": time(8, 0),
                                "end_time": time(20, 0),
                                "duration_hours": 12,
                            }
                        )

                        for team, role_name, first, last, sap, shifts_per_week, unit_name, pattern in staff_data:
                            role = Role.objects.get(name=role_name)
                            unit = Unit.objects.get_or_create(name=unit_name)[0]
                            email = f"{sap.lower()}@example.com"
                            user = User.objects.create(
                                first_name=first,
                                last_name=last,
                                sap=sap,
                                email=email,
                                role=role,
                                team=team,
                                unit=unit,
                                shift_preference="DAY",
                                shifts_per_week_override=shifts_per_week
                            )
                            # Assign shifts according to pattern (3 weeks, repeated 4 times)
                            for cycle in range(4):
                                for week in range(3):
                                    for day in range(7):
                                        shift_flag = pattern[week][day]
                                        if shift_flag:
                                            shift_date = start_date + timedelta(weeks=cycle*3 + week, days=day)
                                            Shift.objects.create(
                                                user=user,
                                                date=shift_date,
                                                unit=unit,
                                                shift_type=day_shift_type
                                            )

                        # Assign home units to SCW/SCA staff missing them, using base mapping from rota pattern file
                        try:
                            from scheduling.management.commands.apply_three_week_scw_sca_pattern import Command as RotaCommand
                            rota_patterns = getattr(RotaCommand, 'patterns', {})
                            staff_to_pattern_sap = {
                                # TEAM A SCW 3-shift
                                "SCW1001": "SCWD3A01", "SCW1002": "SCWD3A02", "SCW1003": "SCWD3A03",
                                # TEAM A SCW 2-shift
                                "SCW1004": "SCWD2A01", "SCW1005": "SCWD2A02", "SCW1006": "SCWD2A03", "SCW1007": "SCWD2A04", "SCW1008": "SCWD2A05", "SCW1009": "SCWD2A06",
                                # TEAM A SCA 3-shift
                                "SCA1010": "SCAD3A03", "SCA1011": "SCAD3A04", "SCA1012": "SCAD3A05", "SCA1013": "SCAD3A06", "SCA1014": "SCAD3A07", "SCA1015": "SCAD3A08", "SCA1016": "SCAD3A09", "SCA1017": "SCAD3A10",
                                # TEAM A SCA 2-shift
                                "SCA1019": "SCAD2A02", "SCA1020": "SCAD2A03", "SCA1021": "SCAD2A04", "SCA1022": "SCAD2A05", "SCA1023": "SCAD2A06", "SCA1024": "SCAD2A07", "SCA1025": "SCAD2B02",
                                # TEAM B SCW 3-shift
                                "SCW1026": "SCWD3B01", "SCW1027": "SCWD3B02", "SCW1028": "SCWD3B03",
                                # TEAM B SCW 2-shift
                                "SCW1029": "SCWD2B01", "SCW1030": "SCWD2B02", "SCW1031": "SCWD2B03", "SCW1032": "SCWD2B04", "SCW1033": "SCWD2B05", "SCW1034": "SCWD2B06",
                                # TEAM B SCA 3-shift
                                "SCA1035": "SCAD3A01", "SCA1036": "SCAD3B01", "SCA1037": "SCAD3B02", "SCA1038": "SCAD3B03", "SCA1039": "SCAD3B04", "SCA1040": "SCAD3B05", "SCA1041": "SCAD3B06", "SCA1042": "SCAD3B07", "SCA1043": "SCAD3B08",
                                # TEAM B SCA 2-shift
                                "SCA1044": "SCAD2B01", "SCA1045": "SCAD2B03", "SCA1046": "SCAD2B04", "SCA1047": "SCAD2B05", "SCA1048": "SCAD2B06", "SCA1049": "SCAD2B07", "SCA1050": "SCAD2B08",
                                # TEAM C SCW 3-shift
                                "SCW1051": "SCWD3C01", "SCW1052": "SCWD3C02", "SCW1053": "SCWD3C03",
                                # TEAM C SCW 2-shift
                                "SCW1054": "SCWD2C01", "SCW1055": "SCWD2C02", "SCW1056": "SCWD2C03", "SCW1057": "SCWD2C04", "SCW1058": "SCWD2B05", "SCW1059": "SCWD2C06",
                                # TEAM C SCA 3-shift
                                "SCA1060": "SCAD3A02", "SCA1061": "SCAD3C01", "SCA1062": "SCAD3C02", "SCA1063": "SCAD3C03", "SCA1064": "SCAD3C04", "SCA1065": "SCAD3C05", "SCA1066": "SCAD3C06", "SCA1067": "SCAD3C07", "SCA1068": "SCAD3C08", "SCA1069": "SCAD3C09", "SCA1070": "SCAD3C10", "SCA1071": "SCAD3C11",
                                # TEAM C SCA 2-shift
                                "SCA1079": "SCAD2C08", "SCA1072": "SCAD2A01", "SCA1073": "SCAD2A08", "SCA1074": "SCAD2C01", "SCA1075": "SCAD2C02", "SCA1076": "SCAD2C03", "SCA1077": "SCAD2C04", "SCA1078": "SCAD2C05",
                            }
                            missing_users = User.objects.filter(role__name__in=['SCW','SCA'], home_unit__isnull=True)
                            for user in missing_users:
                                pattern_sap = staff_to_pattern_sap.get(user.sap)
                                if pattern_sap and pattern_sap in rota_patterns:
                                    team, unit_name, *_ = rota_patterns[pattern_sap]
                                    try:
                                        unit = Unit.objects.get(name=unit_name)
                                        user.home_unit = unit
                                        user.save(update_fields=['home_unit'])
                                        self.stdout.write(self.style.SUCCESS(f"Assigned home unit {unit_name} to {user.sap}"))
                                    except Exception as e:
                                            self.stdout.write(self.style.WARNING(f"Could not assign home unit for {user.sap}: {e}"))
                                else:
                                    self.stdout.write(self.style.WARNING(f"No base unit mapping found for {user.sap}"))
                        except Exception as e:
                                self.stdout.write(self.style.WARNING(f"Could not import rota patterns for missing home unit assignment: {e}"))
                        self.stdout.write(self.style.SUCCESS('Staff import and alignment complete.'))
                        # (stray/duplicate lines removed)
    help = 'Import and align SCW/SCA day staff with roles, SAP, and shift patterns.'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Remove all existing SCW/SCA day staff and their shifts
            users = User.objects.filter(role__name__in=["SCW", "SCA"], shift_preference__contains="DAY")
            Shift.objects.filter(user__in=users).delete()
            users.delete()

            # Import new staff
            from datetime import date, timedelta
            start_date = date(2026, 1, 4)  # Sunday
            weeks = 12
            days_of_week = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]

            from scheduling.models import ShiftType
            from datetime import time
            day_shift_type, _ = ShiftType.objects.get_or_create(
                name="DAY",
                defaults={
                    "start_time": time(8, 0),
                    "end_time": time(20, 0),
                    "duration_hours": 12,
                }
            )

            for team, role_name, first, last, sap, shifts_per_week, unit_name, pattern in staff_data:
                role = Role.objects.get(name=role_name)
                unit = Unit.objects.get_or_create(name=unit_name)[0]
                email = f"{sap.lower()}@example.com"
                user = User.objects.create(
                    first_name=first,
                    last_name=last,
                    sap=sap,
                    email=email,
                    role=role,
                    team=team,
                    unit=unit,
                    shift_preference="DAY",
                    shifts_per_week_override=shifts_per_week
                )
                # Assign shifts according to pattern (3 weeks, repeated 4 times)
                for cycle in range(4):
                    for week in range(3):
                        for day in range(7):
                            shift_flag = pattern[week][day]
                            if shift_flag:
                                shift_date = start_date + timedelta(weeks=cycle*3 + week, days=day)
                                Shift.objects.create(
                                    user=user,
                                    date=shift_date,
                                    unit=unit,
                                    shift_type=day_shift_type
                                )

        self.stdout.write(self.style.SUCCESS('Staff import and alignment complete.'))
