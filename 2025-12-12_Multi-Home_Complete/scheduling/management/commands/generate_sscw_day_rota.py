from collections import defaultdict
from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from scheduling.models import Shift, ShiftType, User


class Command(BaseCommand):
    help = "Generate the repeating three-week rota for SSCW day shifts starting from a given Sunday."

    DEFAULT_START = "2026-01-04"
    PATTERN_LENGTH = 3

    NOTES_DEFAULT = "ON DUTY (supernumerary)"
    NOTES_OVERRIDES = {
        # pattern_index -> note overrides for specific SAP identifiers
        "SSCWD3C03": {2: "LEAVE COVER – ON DUTY (supernumerary)"},
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--start-date",
            default=self.DEFAULT_START,
            help="Sunday date (YYYY-MM-DD) that marks the beginning of week 1.",
        )
        parser.add_argument(
            "--weeks",
            type=int,
            default=12,
            help="Number of consecutive weeks to generate (defaults to four full rotations / 12 weeks).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show actions without creating or deleting shifts.",
        )

    def handle(self, *args, **options):
        start_date = self._parse_start(options["start_date"])
        weeks = options["weeks"]
        dry_run = options["dry_run"]

        if weeks <= 0:
            raise CommandError("Weeks must be a positive integer.")

        users = list(
            User.objects.filter(role__name="SSCW", shift_preference="DAY_SENIOR", is_active=True)
            .select_related("home_unit")
            .order_by("team", "sap")
        )
        if len(users) != 9:
            raise CommandError(f"Expected 9 active day SSCW records, found {len(users)}.")

        users_by_team = defaultdict(list)
        for user in users:
            if not user.team:
                raise CommandError(f"User {user.sap} is missing a team assignment.")
            users_by_team[user.team].append(user)

        missing_team = {"A", "B", "C"} - set(users_by_team)
        if missing_team:
            raise CommandError(f"Missing SSCW day staff for teams: {', '.join(sorted(missing_team))}.")

        try:
            day_shift_type = ShiftType.objects.get(name="DAY_SENIOR")
        except ShiftType.DoesNotExist as exc:
            raise CommandError("Required shift type DAY_SENIOR does not exist.") from exc

        pattern = self._build_pattern()
        total_created = 0
        total_updated = 0

        end_date = start_date + timedelta(weeks=weeks) - timedelta(days=1)
        existing_shifts = Shift.objects.filter(
            user__in=users,
            shift_type=day_shift_type,
            date__gte=start_date,
            date__lte=end_date,
        )
        existing_count = existing_shifts.count()

        if dry_run:
            self.stdout.write("Dry run: skips deletions and creations.")
        else:
            if existing_count:
                existing_shifts.delete()
                self.stdout.write(f"Deleted {existing_count} existing shifts for SSCW day staff in range.")

        with transaction.atomic():
            for week_index in range(weeks):
                week_start = start_date + timedelta(weeks=week_index)
                pattern_index = week_index % self.PATTERN_LENGTH

                for team, assignments in pattern.items():
                    for user in users_by_team[team]:
                        home_unit = user.home_unit or user.unit
                        if home_unit is None:
                            raise CommandError(
                                f"User {user.sap} does not have a home unit set; required for rota assignment."
                            )

                        for day_offset in assignments[pattern_index]["duty"]:
                            shift_date = week_start + timedelta(days=day_offset)
                            note = self.NOTES_OVERRIDES.get(user.sap, {}).get(
                                pattern_index, self.NOTES_DEFAULT
                            )
                            total_created, total_updated = self._create_shift(
                                user=user,
                                unit=home_unit,
                                shift_type=day_shift_type,
                                shift_date=shift_date,
                                notes=note,
                                dry_run=dry_run,
                                totals=(total_created, total_updated),
                            )

        self.stdout.write(self.style.SUCCESS("SSCW day rota generation complete."))
        self.stdout.write(f"- Weeks covered: {weeks}")
        self.stdout.write(f"- Start date: {start_date.isoformat()}")
        self.stdout.write(f"- On-duty shifts created: {total_created}")
        if total_updated:
            self.stdout.write(f"- Existing shifts updated: {total_updated}")
        self.stdout.write(f"- End date: {end_date.isoformat()}")

    def _build_pattern(self):
        return {
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
                {"duty": {3, 4, 5}},
            ],
        }

    def _create_shift(self, user, unit, shift_type, shift_date, notes, dry_run, totals):
        created, updated = totals
        if dry_run:
            self.stdout.write(
                f"Would assign {user.sap} ({user.team}) -> {shift_type.name} on {shift_date} at {unit.name} ({notes})"
            )
            return created, updated

        shift, was_created = Shift.objects.update_or_create(
            user=user,
            date=shift_date,
            shift_type=shift_type,
            defaults={
                "unit": unit,
                "status": "SCHEDULED",
                "notes": notes,
            },
        )
        if was_created:
            created += 1
        else:
            updated += 1
        return created, updated

    def _parse_start(self, value):
        try:
            parsed = date.fromisoformat(value)
        except ValueError as exc:
            raise CommandError(f"Invalid date '{value}'. Use YYYY-MM-DD.") from exc

        if parsed.weekday() != 6:
            raise CommandError("Start date must be a Sunday (weekday == 6).")
        return parsed
