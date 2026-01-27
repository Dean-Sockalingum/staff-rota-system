from collections import Counter, deque
from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError

from scheduling.models import Role, Unit, User


class Command(BaseCommand):
    help = "Assign staff to units in a round-robin fashion, balancing teams as evenly as possible."

    TEAM_ORDER = ["A", "B", "C"]

    def add_arguments(self, parser):
        parser.add_argument("--role", required=True, help="Role code, e.g. SCW")
        parser.add_argument("--period", required=True, choices=["DAY", "NIGHT"], help="Shift period")
        parser.add_argument(
            "--shifts",
            required=True,
            type=int,
            nargs="+",
            help="Shifts per week overrides to include (provide one or more values)",
        )
        parser.add_argument(
            "--units",
            nargs="+",
            help="Explicit list of unit names to assign in order (defaults to all active non-admin units)",
        )
        parser.add_argument(
            "--set-home-unit",
            action="store_true",
            help="Also update each user's home_unit to match the assigned unit",
        )
        parser.add_argument(
            "--per-unit",
            nargs="+",
            help="Specify per-unit allocations as shift=count (e.g. 3=1 2=2)",
        )
        parser.add_argument(
            "--excess-unit",
            help="Unit name that should receive any remaining staff after per-unit allocation",
        )

    def handle(self, *args, **options):
        role_name = options["role"].upper()
        period = options["period"].upper()
        shift_values = sorted(set(options["shifts"]))
        unit_names = options.get("units")
        update_home = options["set_home_unit"]
        per_unit_counts = self._parse_per_unit(options.get("per_unit"))
        excess_unit_name = options.get("excess_unit")
        excess_unit = self._get_unit_by_name(excess_unit_name) if excess_unit_name else None

        role = self._get_role(role_name)
        shift_pref = self._resolve_shift_preference(role_name, period)
        if shift_pref is None:
            raise CommandError(
                f"Unable to resolve shift preference for role {role_name} with period {period}."
            )

        if per_unit_counts:
            missing_shifts = set(per_unit_counts.keys()) - set(shift_values)
            if missing_shifts:
                missing_fmt = ", ".join(str(val) for val in sorted(missing_shifts))
                raise CommandError(
                    f"Per-unit mapping references shift overrides not supplied via --shifts: {missing_fmt}"
                )

        units = self._get_units(unit_names)
        staff = list(
            User.objects.filter(
                role=role,
                shift_preference=shift_pref,
                shifts_per_week_override__in=shift_values,
                team__in=self.TEAM_ORDER,
            )
            .order_by("team", "-shifts_per_week_override", "sap")
        )

        if not staff:
            self.stdout.write(self.style.WARNING("No staff found matching the specified criteria."))
            return

        staff_by_shift = defaultdict(list)
        for user in staff:
            staff_by_shift[user.shifts_per_week_override].append(user)

        if per_unit_counts:
            self._assign_with_distribution(
                units=units,
                staff_by_shift=staff_by_shift,
                per_unit_counts=per_unit_counts,
                excess_unit=excess_unit,
                update_home=update_home,
            )
            return

        allocation_order = self._build_round_robin_order(staff)

        if not allocation_order:
            self.stdout.write(self.style.WARNING("No staff queued for allocation."))
            return

        updates = []
        summary_counter = Counter()
        team_counter = Counter()
        unit_count = len(units)

        for index, user in enumerate(allocation_order):
            unit = units[index % unit_count]
            self._apply_assignment(user, unit, update_home)
            updates.append(user)
            summary_counter[(unit.name, user.team)] += 1
            team_counter[user.team] += 1

        self._bulk_update_users(updates, update_home)

        self.stdout.write(self.style.SUCCESS("Unit assignment completed."))
        self.stdout.write(f"- Processed {len(allocation_order)} staff")
        for team in self.TEAM_ORDER:
            self.stdout.write(f"- Team {team}: {team_counter[team]} assigned")

        self.stdout.write("Unit breakdown (unit -> team counts):")
        for unit in units:
            counts = {team: summary_counter[(unit.name, team)] for team in self.TEAM_ORDER}
            formatted = ", ".join(f"{team}:{counts[team]}" for team in self.TEAM_ORDER)
            self.stdout.write(f"  {unit.get_name_display()}: {formatted}")

    def _get_units(self, unit_names):
        qs = Unit.objects.filter(is_active=True)
        if unit_names:
            units = list(qs.filter(name__in=unit_names))
            missing = sorted(set(unit_names) - {unit.name for unit in units})
            if missing:
                raise CommandError(f"Unknown units specified: {', '.join(missing)}")
            units.sort(key=lambda unit: unit_names.index(unit.name))
            return units
        return list(qs.exclude(name="ADMIN").order_by("name"))

    def _get_role(self, role_name):
        try:
            return Role.objects.get(name=role_name)
        except Role.DoesNotExist as exc:
            raise CommandError(f"Role '{role_name}' does not exist") from exc

    def _resolve_shift_preference(self, role_name: str, period: str):
        if role_name in {"SCW", "SSCW"}:
            return "DAY_SENIOR" if period == "DAY" else "NIGHT_SENIOR"
        if role_name == "SCA":
            return "DAY_ASSISTANT" if period == "DAY" else "NIGHT_ASSISTANT"
        return None

    def _parse_per_unit(self, values):
        if not values:
            return None
        result = {}
        for token in values:
            if "=" not in token:
                raise CommandError("Per-unit arguments must use the format shift=count, e.g. 3=1")
            shift_str, count_str = token.split("=", 1)
            try:
                shift_val = int(shift_str)
                count_val = int(count_str)
            except ValueError as exc:
                raise CommandError(f"Invalid per-unit mapping '{token}'. Both shift and count must be integers.") from exc
            if shift_val <= 0:
                raise CommandError("Shift overrides in per-unit mapping must be positive integers.")
            if count_val < 0:
                raise CommandError("Per-unit counts cannot be negative.")
            result[shift_val] = count_val
        return result

    def _assign_with_distribution(self, units, staff_by_shift, per_unit_counts, excess_unit, update_home):
        orders = {}
        indices = {}
        for shift_value, users in staff_by_shift.items():
            orders[shift_value] = self._build_round_robin_order(users)
            indices[shift_value] = 0

        required_shifts = set(per_unit_counts.keys())
        if missing := required_shifts - set(orders.keys()):
            missing_fmt = ", ".join(str(val) for val in sorted(missing))
            raise CommandError(f"No staff found for required shift overrides: {missing_fmt}")

        unit_count = len(units)
        updates = []
        summary_counter = Counter()
        processed = 0

        for shift_value in required_shifts:
            available = len(orders[shift_value])
            needed = per_unit_counts[shift_value] * unit_count
            if available < needed:
                raise CommandError(
                    f"Not enough staff with {shift_value} shifts per week (needed {needed}, available {available})."
                )

        for unit in units:
            for shift_value, count in per_unit_counts.items():
                for _ in range(count):
                    user = self._next_user(orders, indices, shift_value, required=True)
                    self._apply_assignment(user, unit, update_home)
                    updates.append(user)
                    processed += 1
                    summary_counter[(unit.name, shift_value, user.team)] += 1

        for shift_value in required_shifts:
            while True:
                user = self._next_user(orders, indices, shift_value)
                if user is None:
                    break
                if excess_unit is None:
                    raise CommandError(
                        "Staff remain after fulfilling per-unit targets. Specify --excess-unit to allocate the surplus."
                    )
                self._apply_assignment(user, excess_unit, update_home)
                updates.append(user)
                processed += 1
                summary_counter[(excess_unit.name, shift_value, user.team)] += 1

        self._bulk_update_users(updates, update_home)

        self.stdout.write(self.style.SUCCESS("Unit assignment completed."))
        self.stdout.write(f"- Processed {processed} staff")

        for shift_value in sorted(orders.keys()):
            team_totals = {team: 0 for team in self.TEAM_ORDER}
            for (unit_name, shift_val, team), amount in summary_counter.items():
                if shift_val == shift_value:
                    team_totals[team] += amount
            totals_str = ", ".join(f"Team {team}:{team_totals[team]}" for team in self.TEAM_ORDER)
            self.stdout.write(f"- {shift_value} shifts -> {totals_str}")

        units_for_report = list(units)
        if excess_unit and excess_unit.name not in {unit.name for unit in units_for_report}:
            units_for_report.append(excess_unit)

        self.stdout.write("Unit breakdown (unit -> shift/team counts):")
        for unit in units_for_report:
            shift_details = []
            for shift_value in sorted(orders.keys()):
                team_counts = [
                    f"{team}:{summary_counter[(unit.name, shift_value, team)]}"
                    for team in self.TEAM_ORDER
                ]
                shift_details.append(f"{shift_value}=>({' '.join(team_counts)})")
            self.stdout.write(f"  {unit.get_name_display()}: {'; '.join(shift_details)}")

    def _build_round_robin_order(self, users):
        team_queues = {team: deque() for team in self.TEAM_ORDER}
        for user in users:
            if user.team in team_queues:
                team_queues[user.team].append(user)

        order = []
        while any(team_queues[team] for team in self.TEAM_ORDER):
            for team in self.TEAM_ORDER:
                if team_queues[team]:
                    order.append(team_queues[team].popleft())
        return order

    def _next_user(self, orders, indices, shift_value, required=False):
        order = orders.get(shift_value, [])
        index = indices.get(shift_value, 0)
        if index >= len(order):
            if required:
                raise CommandError(
                    f"Not enough staff remain to satisfy allocation for shift override {shift_value}."
                )
            return None
        user = order[index]
        indices[shift_value] = index + 1
        return user

    def _apply_assignment(self, user, unit, update_home):
        user.unit = unit
        if update_home:
            user.home_unit = unit

    def _bulk_update_users(self, users, update_home):
        if not users:
            return
        unique_updates = list({user.pk: user for user in users}.values())
        fields = ["unit"]
        if update_home:
            fields.append("home_unit")
        User.objects.bulk_update(unique_updates, fields)

    def _get_unit_by_name(self, unit_name):
        try:
            return Unit.objects.get(name=unit_name)
        except Unit.DoesNotExist as exc:
            raise CommandError(f"Unit '{unit_name}' does not exist") from exc
