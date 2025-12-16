from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from scheduling.models import Role, StaffingRequirement


class Command(BaseCommand):
    help = "Create or refresh the staffing repository with the agreed baseline counts."

    REQUIREMENTS = [
        {"role": "SSCW", "shift_period": "DAY", "shifts_per_week": 3, "target_staff": 9},
        {"role": "SSCW", "shift_period": "NIGHT", "shifts_per_week": 3, "target_staff": 8},
        {"role": "SCA", "shift_period": "NIGHT", "shifts_per_week": 3, "target_staff": 34},
        {"role": "SCA", "shift_period": "NIGHT", "shifts_per_week": 2, "target_staff": 32},
        {"role": "SCA", "shift_period": "DAY", "shifts_per_week": 3, "target_staff": 28},
        {"role": "SCA", "shift_period": "DAY", "shifts_per_week": 2, "target_staff": 22},
        {"role": "SCW", "shift_period": "NIGHT", "shifts_per_week": 3, "target_staff": 7},
        {"role": "SCW", "shift_period": "NIGHT", "shifts_per_week": 2, "target_staff": 8},
        {"role": "SCW", "shift_period": "DAY", "shifts_per_week": 3, "target_staff": 9},
        {"role": "SCW", "shift_period": "DAY", "shifts_per_week": 2, "target_staff": 18},
    ]

    def handle(self, *args, **options):
        role_names = {item["role"] for item in self.REQUIREMENTS}
        roles = {role.name: role for role in Role.objects.filter(name__in=role_names)}
        missing_roles = sorted(role_names - roles.keys())

        if missing_roles:
            missing_display = ", ".join(missing_roles)
            raise CommandError(f"Missing roles: {missing_display}. Please load core role data first.")

        created = 0
        updated = 0
        requirement_ids = set()

        with transaction.atomic():
            for requirement in self.REQUIREMENTS:
                role = roles[requirement["role"]]
                obj, was_created = StaffingRequirement.objects.update_or_create(
                    role=role,
                    shift_period=requirement["shift_period"],
                    shifts_per_week=requirement["shifts_per_week"],
                    defaults={"target_staff": requirement["target_staff"]},
                )
                requirement_ids.add(obj.id)
                if was_created:
                    created += 1
                else:
                    updated += 1

            removed = 0
            if requirement_ids:
                removed, _ = StaffingRequirement.objects.exclude(id__in=requirement_ids).delete()

        self.stdout.write(self.style.SUCCESS("Staffing repository refreshed."))
        self.stdout.write(f"- Created {created} records")
        self.stdout.write(f"- Updated {updated} records")
        self.stdout.write(f"- Removed {removed} stale records")
