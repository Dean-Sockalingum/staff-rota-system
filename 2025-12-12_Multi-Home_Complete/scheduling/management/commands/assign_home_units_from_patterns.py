from django.core.management.base import BaseCommand
from scheduling.models import User, Unit
from scheduling.management.commands.apply_three_week_scw_sca_pattern import Command as PatternCommand

class Command(BaseCommand):
    help = 'Assign home units to SCW/SCA staff missing them, using rota pattern mapping.'

    def handle(self, *args, **options):
        patterns = getattr(PatternCommand, 'patterns', {})
        staff_to_pattern_sap = {
            # TEAM A SCW 3-shift
            "SCW1001": "SCWD3A01", "SCW1002": "SCWD3A02", "SCW1003": "SCWD3A03",
            # TEAM A SCW 2-shift
            "SCW1004": "SCWD2A01", "SCW1005": "SCWD2A02", "SCW1006": "SCWD2A03", "SCW1007": "SCWD2A04", "SCW1008": "SCWD2A05", "SCW1009": "SCWD2A06",
            # TEAM A SCA 3-shift
            "SCA1010": "SCAD3A03", "SCA1011": "SCAD3A04", "SCA1012": "SCAD3A05", "SCA1013": "SCAD3A06", "SCA1014": "SCAD3A07", "SCA1015": "SCAD3A08", "SCA1016": "SCAD3A09", "SCA1017": "SCAD3A10", "SCA1018": "SCAD3A03",
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
            "SCW1054": "SCWD2C01", "SCW1055": "SCWD2C02", "SCW1056": "SCWD2C03", "SCW1057": "SCWD2C04", "SCW1058": "SCWD2C05", "SCW1059": "SCWD2C06",
            # TEAM C SCA 3-shift
            "SCA1060": "SCAD3A02", "SCA1061": "SCAD3C01", "SCA1062": "SCAD3C02", "SCA1063": "SCAD3C03", "SCA1064": "SCAD3C04", "SCA1065": "SCAD3C05", "SCA1066": "SCAD3C06", "SCA1067": "SCAD3C07", "SCA1068": "SCAD3C08", "SCA1069": "SCAD3C09", "SCA1070": "SCAD3C10", "SCA1071": "SCAD3C11",
            # TEAM C SCA 2-shift
            "SCA1079": "SCAD2C08", "SCA1072": "SCAD2A01", "SCA1073": "SCAD2A08", "SCA1074": "SCAD2C01", "SCA1075": "SCAD2C02", "SCA1076": "SCAD2C03", "SCA1077": "SCAD2C04", "SCA1078": "SCAD2C05",
            # Unmapped SAP codes (log and skip)
            "SCA001": None, "SCA099": None, "SCW001": None
        }
        missing = User.objects.filter(role__name__in=['SCW','SCA'], home_unit__isnull=True)
        updated = 0
        for user in missing:
            pattern_key = staff_to_pattern_sap.get(user.sap)
            pattern = patterns.get(pattern_key)
            unit_name = pattern[1] if pattern else None
            if unit_name:
                unit = Unit.objects.filter(name=unit_name).first()
                if unit:
                    user.home_unit = unit
                    user.save(update_fields=['home_unit'])
                    updated += 1
                    self.stdout.write(self.style.SUCCESS(f"Assigned {unit_name} to {user.sap}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Unit {unit_name} not found for {user.sap}"))
            else:
                self.stdout.write(self.style.WARNING(f"No pattern mapping for {user.sap}"))
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} users."))
