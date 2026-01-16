from collections import defaultdict
from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from scheduling.models import Shift, ShiftType, User


class Command(BaseCommand):
    help = "Generate rota shifts for SCW and SCA cohorts based on the agreed three-week patterns."

    TEAM_ORDER = ("A", "B", "C")
    DEFAULT_START = "2026-01-04"
    PATTERN_LENGTH = 3

    SHIFT_TYPE_MAP = {
        ("SCW", "DAY"): "DAY_SENIOR",
        ("SCW", "NIGHT"): "NIGHT_SENIOR",
        ("SCA", "DAY"): "DAY_ASSISTANT",
        ("SCA", "NIGHT"): "NIGHT_ASSISTANT",
    }

    SHIFT_PREFERENCE_MAP = {
        ("SCW", "DAY"): "DAY_SENIOR",
        ("SCW", "NIGHT"): "NIGHT_SENIOR",
        ("SCA", "DAY"): "DAY_ASSISTANT",
        ("SCA", "NIGHT"): "NIGHT_ASSISTANT",
    }

    PATTERNS = {
        ("DAY", 3): {
            "A": [
                {"duty": {0, 1, 2}},
                {"duty": {4, 5, 6}},
                {"duty": {2, 3, 4}},
            ],
            "B": [
                {"duty": {4, 5, 6}},
                {"duty": {2, 3, 4}},
                {"duty": {0, 1, 2}},
            ],
            "C": [
                {"duty": {2, 3, 4}},
                {"duty": {0, 1, 2}},
                {"duty": {4, 5, 6}},
            ],
        },
        ("DAY", 2): {
            "A": [
                {"duty": {0, 4}},
                {"duty": {1, 2}},
                {"duty": {5, 6}},
            ],
            "B": [
                {"duty": {1, 2}},
                {"duty": {5, 6}},
                {"duty": {0, 4}},
            ],
            "C": [
                {"duty": {5, 6}},
                {"duty": {0, 4}},
                {"duty": {1, 2}},
            ],
        },
        ("NIGHT", 3): {
            "A": [
                {"duty": {0, 1, 2}},
                {"duty": {4, 5, 6}},
                {"duty": {2, 3, 4}},
            ],
            "B": [
                {"duty": {4, 5, 6}},
                {"duty": {2, 3, 4}},
                {"duty": {0, 1, 2}},
            ],
            "C": [
                {"duty": {2, 3, 4}},
                {"duty": {0, 1, 2}},
                {"duty": {4, 5, 6}},
            ],
        },
        ("NIGHT", 2): {
            "A": [
                {"duty": {5, 6}},
                {"duty": {2, 3}},
                {"duty": {0, 1}},
            ],
            "B": [
                {"duty": {2, 3}},
                {"duty": {0, 1}},
                {"duty": {5, 6}},
            ],
            "C": [
                {"duty": {0, 1}},
                {"duty": {5, 6}},
                {"duty": {2, 3}},
            ],
        },
    }

    def add_arguments(self, parser):
        parser.add_argument("--role", required=True, choices=["SCW", "SCA"], help="Target role")
        parser.add_argument("--period", required=True, choices=["DAY", "NIGHT"], help="Shift period")
        parser.add_argument("--shifts", required=True, type=int, choices=[2, 3], help="Shifts per week override")
        parser.add_argument(
            "--start-date",
            default=self.DEFAULT_START,
            help="Sunday date (YYYY-MM-DD) marking the beginning of week 1.",
        )
        parser.add_argument(
            "--weeks",
            type=int,
            default=3,
            help="Number of consecutive weeks to generate (defaults to three).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show changes without touching the database.",
        )

    def handle(self, *args, **options):
        role = options["role"].upper()
        period = options["period"].upper()
        shifts_per_week = options["shifts"]
        start_date = self._parse_start(options["start_date"])
        weeks = options["weeks"]
        dry_run = options["dry_run"]

        if weeks <= 0:
            raise CommandError("Weeks must be a positive integer.")

        pattern_key = (period, shifts_per_week)
        if pattern_key not in self.PATTERNS:
            raise CommandError("No pattern defined for the supplied period and shifts per week.")

        shift_type_name = self.SHIFT_TYPE_MAP.get((role, period))
        shift_preference = self.SHIFT_PREFERENCE_MAP.get((role, period))
        if not shift_type_name or not shift_preference:
            raise CommandError("Unable to resolve shift type or preference for supplied role/period.")

        try:
            shift_type = ShiftType.objects.get(name=shift_type_name)
        except ShiftType.DoesNotExist as exc:
            raise CommandError(f"Shift type '{shift_type_name}' does not exist. Run setup_shift_patterns first.") from exc

        users = list(
            User.objects.filter(
                role__name=role,
                shift_preference=shift_preference,
                shifts_per_week_override=shifts_per_week,
                is_active=True,
            )
            .select_related("unit", "home_unit")
            .order_by("team", "sap")
        )

        if not users:
            raise CommandError("No staff match the provided filters; check role, period, and shifts per week.")

        users_by_team = defaultdict(list)
        for user in users:
            if user.team not in self.TEAM_ORDER:
                raise CommandError(f"User {user.sap} is missing a valid team assignment.")
            if user.unit is None:
                raise CommandError(f"User {user.sap} does not have a unit assigned.")
            users_by_team[user.team].append(user)

        missing_teams = [team for team in self.TEAM_ORDER if team not in users_by_team]
        if missing_teams:
            raise CommandError(f"Missing staff for teams: {', '.join(missing_teams)}.")

        pattern = self.PATTERNS[pattern_key]
        for team in self.TEAM_ORDER:
            if team not in pattern:
                raise CommandError(f"Pattern does not include team {team}.")

        end_date = start_date + timedelta(weeks=weeks) - timedelta(days=1)
        existing_qs = Shift.objects.filter(
            user__in=users,
            date__gte=start_date,
            date__lte=end_date,
            shift_type=shift_type,
        )
        existing_count = existing_qs.count()

        if dry_run:
            self.stdout.write("Dry run: no deletions performed.")
        else:
            if existing_count:
                existing_qs.delete()
                self.stdout.write(f"Deleted {existing_count} existing {shift_type_name} shifts in range.")

        created = 0
        updated = 0

        with transaction.atomic():
            for week_index in range(weeks):
                week_start = start_date + timedelta(weeks=week_index)
                pattern_index = week_index % self.PATTERN_LENGTH

                for team in self.TEAM_ORDER:
                    assignments = pattern[team][pattern_index]
                    duty_days = assignments["duty"]

                    for user in users_by_team[team]:
                        for day_offset in duty_days:
                            shift_date = week_start + timedelta(days=day_offset)
                            if dry_run:
                                self.stdout.write(
                                    f"Would schedule {user.sap} ({team}) for {shift_type_name} on {shift_date}"
                                    f" at {user.unit.name}"
                                )
                                continue

                            shift, was_created = Shift.objects.update_or_create(
                                user=user,
                                date=shift_date,
                                shift_type=shift_type,
                                defaults={
                                    "unit": user.unit,
                                    "status": "SCHEDULED",
                                },
                            )
                            if was_created:
                                created += 1
                            else:
                                updated += 1

        self.stdout.write(self.style.SUCCESS("Shift pattern generation complete."))
        self.stdout.write(f"- Role: {role}")
        self.stdout.write(f"- Period: {period}")
        self.stdout.write(f"- Shifts per week: {shifts_per_week}")
        self.stdout.write(f"- Weeks covered: {weeks}")
        self.stdout.write(f"- Start date: {start_date.isoformat()}")
        self.stdout.write(f"- End date: {end_date.isoformat()}")
        if dry_run:
            self.stdout.write("- No database changes (dry run)")
        else:
            self.stdout.write(f"- Shifts created: {created}")
            self.stdout.write(f"- Existing shifts updated: {updated}")

    def _parse_start(self, value: str) -> date:
        try:
            parsed = date.fromisoformat(value)
        except ValueError as exc:
            raise CommandError(f"Invalid date '{value}'. Use YYYY-MM-DD format.") from exc

        if parsed.weekday() != 6:
            raise CommandError("Start date must be a Sunday (weekday == 6).")
        return parsed
