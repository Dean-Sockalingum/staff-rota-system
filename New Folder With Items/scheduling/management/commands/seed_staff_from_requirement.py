from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from scheduling.models import Role, StaffingRequirement, User


class Command(BaseCommand):
    help = "Generate staff members for a staffing requirement, optionally splitting evenly across teams."

    def add_arguments(self, parser):
        parser.add_argument("--role", required=True, help="Role code, e.g. SCW or SCA")
        parser.add_argument("--period", required=True, choices=["DAY", "NIGHT"], help="Shift period")
        parser.add_argument("--shifts", required=True, type=int, help="Shifts per week override")
        parser.add_argument(
            "--team-split",
            action="store_true",
            help="Assign staff evenly across Teams A, B, C",
        )
        parser.add_argument(
            "--remove-surplus",
            action="store_true",
            help="Delete existing staff for this requirement beyond the target headcount",
        )

    def handle(self, *args, **options):
        role_name = options["role"].upper()
        period = options["period"].upper()
        shifts = options["shifts"]
        split_teams = options["team_split"]
        remove_surplus = options["remove_surplus"]

        try:
            role = Role.objects.get(name=role_name)
        except Role.DoesNotExist as exc:
            raise CommandError(f"Role '{role_name}' does not exist") from exc

        try:
            requirement = StaffingRequirement.objects.get(
                role=role,
                shift_period=period,
                shifts_per_week=shifts,
            )
        except StaffingRequirement.DoesNotExist as exc:
            raise CommandError(
                f"No staffing requirement for role {role_name}, period {period}, {shifts} shifts"
            ) from exc

        target_count = requirement.target_staff
        if target_count <= 0:
            self.stdout.write(self.style.WARNING("Target count is zero; nothing to do."))
            return

        team_sequence = ["A", "B", "C"] if split_teams else [None]
        team_counts = defaultdict(int)

        created = 0
        updated = 0

        prefix = f"{role_name}{period[0]}{shifts}"

        with transaction.atomic():
            for index in range(1, target_count + 1):
                team = team_sequence[(index - 1) % len(team_sequence)]
                team_counts[team] += 1
                team_counter = team_counts[team]

                if team:
                    sap = f"{prefix}{team}{team_counter:02d}"
                    last_name = f"Team {team}{team_counter:02d}"
                    team_value = team
                else:
                    sap = f"{prefix}{index:03d}"
                    last_name = f"Staff {index:03d}"
                    team_value = None

                email = f"{sap.lower()}@staffrota.local"
                first_name = f"{role.get_name_display()} {period.title()}"

                defaults = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "role": role,
                    "team": team_value,
                    "shift_preference": self._resolve_shift_preference(role_name, period),
                    "shifts_per_week_override": shifts,
                    "is_active": True,
                }

                user, was_created = User.objects.update_or_create(sap=sap, defaults=defaults)
                if was_created:
                    user.set_password("changeme123")
                    user.save(update_fields=["password"])
                    created += 1
                else:
                    updated += 1

            if remove_surplus:
                surplus_qs = User.objects.filter(
                    role=role,
                    shifts_per_week_override=shifts,
                    shift_preference=self._resolve_shift_preference(role_name, period),
                ).exclude(sap__startswith=prefix)
                removed, _ = surplus_qs.delete()
            else:
                removed = 0

        self.stdout.write(self.style.SUCCESS("Staff generation completed."))
        self.stdout.write(f"- Target records: {target_count}")
        self.stdout.write(f"- Created {created}")
        self.stdout.write(f"- Updated {updated}")
        self.stdout.write(f"- Removed {removed} surplus records")

    def _resolve_shift_preference(self, role_name: str, period: str) -> str:
        if role_name in {"SCW", "SSCW"}:
            return "DAY_SENIOR" if period == "DAY" else "NIGHT_SENIOR"
        if role_name == "SCA":
            return "DAY_ASSISTANT" if period == "DAY" else "NIGHT_ASSISTANT"
        return None
