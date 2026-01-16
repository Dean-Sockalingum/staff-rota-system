from collections import defaultdict
from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from scheduling.models import Shift, ShiftType, User


class Command(BaseCommand):
    help = "Generate the repeating three-week rota for SSCWN (night senior) shifts starting from a given Sunday."

    DEFAULT_START = "2025-11-23"
    PATTERN_LENGTH = 3
    NOTES_DEFAULT = "ON DUTY (supernumerary night senior)"

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
            help="Number of consecutive weeks to generate (defaults to 12 weeks).",
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

        # Get all SSCWN staff (night senior supervisors)
        users = list(
            User.objects.filter(role__name="SSCWN", is_active=True)
            .select_related("home_unit")
            .order_by("team", "sap")
        )
        if len(users) != 8:
            raise CommandError(f"Expected 8 active SSCWN records, found {len(users)}.")

        users_by_team = defaultdict(list)
        for user in users:
            if not user.team:
                raise CommandError(f"User {user.sap} is missing a team assignment.")
            users_by_team[user.team].append(user)

        # Team distribution: A=3, B=3, C=2
        expected_team_sizes = {"A": 3, "B": 3, "C": 2}
        for team, expected in expected_team_sizes.items():
            actual = len(users_by_team.get(team, []))
            if actual != expected:
                raise CommandError(f"Team {team} should have {expected} SSCWN staff, found {actual}.")

        try:
            night_shift_type = ShiftType.objects.get(name="NIGHT_SENIOR")
        except ShiftType.DoesNotExist as exc:
            raise CommandError("Required shift type NIGHT_SENIOR does not exist.") from exc

        # 3-week rotation pattern (same as night care teams)
        # Team A: Sun/Mon/Tue → Thu/Fri/Sat → Tue/Wed/Thu
        # Team B: Thu/Fri/Sat → Tue/Wed/Thu → Sun/Mon/Tue
        # Team C: Tue/Wed/Thu → Sun/Mon/Tue → Thu/Fri/Sat
        pattern = self._build_pattern()
        total_created = 0
        total_updated = 0

        end_date = start_date + timedelta(weeks=weeks) - timedelta(days=1)
        
        # Delete existing SSCWN night shifts in the date range
        existing_shifts = Shift.objects.filter(
            user__in=users,
            shift_type=night_shift_type,
            date__gte=start_date,
            date__lte=end_date,
        )
        existing_count = existing_shifts.count()

        if dry_run:
            self.stdout.write("Dry run: skips deletions and creations.")
        else:
            if existing_count:
                existing_shifts.delete()
                self.stdout.write(f"Deleted {existing_count} existing SSCWN night shifts in range.")

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

                        note = self.NOTES_DEFAULT
                        for day_offset in assignments[pattern_index]["duty"]:
                            shift_date = week_start + timedelta(days=day_offset)
                            total_created, total_updated = self._create_shift(
                                user=user,
                                unit=home_unit,
                                shift_type=night_shift_type,
                                shift_date=shift_date,
                                notes=note,
                                dry_run=dry_run,
                                totals=(total_created, total_updated),
                            )

        self.stdout.write(self.style.SUCCESS("SSCWN night rota generation complete."))
        self.stdout.write(f"- Weeks covered: {weeks}")
        self.stdout.write(f"- Start date: {start_date.isoformat()}")
        self.stdout.write(f"- On-duty shifts created: {total_created}")
        if total_updated:
            self.stdout.write(f"- Existing shifts updated: {total_updated}")
        self.stdout.write(f"- End date: {end_date.isoformat()}")

    def _build_pattern(self):
        """
        3-week rotation pattern matching night care teams:
        - Team A (like Night Team 1): Sun/Mon/Tue → Thu/Fri/Sat → Tue/Wed/Thu
        - Team B (like Night Team 2): Thu/Fri/Sat → Tue/Wed/Thu → Sun/Mon/Tue
        - Team C (like Night Team 3): Tue/Wed/Thu → Sun/Mon/Tue → Thu/Fri/Sat
        
        Days: 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
        """
        return {
            "A": [
                {"duty": {0, 1, 2}},  # Week 1: Sun/Mon/Tue
                {"duty": {4, 5, 6}},  # Week 2: Thu/Fri/Sat
                {"duty": {2, 3, 4}},  # Week 3: Tue/Wed/Thu
            ],
            "B": [
                {"duty": {4, 5, 6}},  # Week 1: Thu/Fri/Sat
                {"duty": {2, 3, 4}},  # Week 2: Tue/Wed/Thu
                {"duty": {0, 1, 2}},  # Week 3: Sun/Mon/Tue
            ],
            "C": [
                {"duty": {2, 3, 4}},  # Week 1: Tue/Wed/Thu
                {"duty": {0, 1, 2}},  # Week 2: Sun/Mon/Tue
                {"duty": {4, 5, 6}},  # Week 3: Thu/Fri/Sat
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
