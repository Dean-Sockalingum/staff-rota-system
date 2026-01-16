from django.core.management.base import BaseCommand
from django.db import transaction

from scheduling.models import (
    ActivityLog,
    BlackoutPeriod,
    LeaveRequest,
    Shift,
    ShiftSwapRequest,
    StaffReallocation,
    User,
)
from staff_records.models import (
    ContactLogEntry,
    MedicalCertificate,
    SicknessRecord,
    StaffProfile,
)


class Command(BaseCommand):
    help = "Remove all rota data and staff records so the system can be rebuilt from scratch."

    def add_arguments(self, parser):
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Do not prompt for confirmation.",
        )
        parser.add_argument(
            "--include-admin",
            action="store_true",
            help="Also delete admin and superuser accounts.",
        )

    def handle(self, *args, **options):
        noinput = options["noinput"]
        include_admin = options["include_admin"]

        if not noinput:
            confirmation = input(
                "This will permanently delete all staff and rota records. Type 'yes' to continue: "
            )
            if confirmation.strip().lower() != "yes":
                self.stdout.write(self.style.WARNING("Operation cancelled."))
                return

        with transaction.atomic():
            counts = {}

            counts["medical_certificates"] = MedicalCertificate.objects.count()
            MedicalCertificate.objects.all().delete()

            counts["contact_log_entries"] = ContactLogEntry.objects.count()
            ContactLogEntry.objects.all().delete()

            counts["sickness_records"] = SicknessRecord.objects.count()
            SicknessRecord.objects.all().delete()

            counts["staff_profiles"] = StaffProfile.objects.count()
            StaffProfile.objects.all().delete()

            counts["shift_swaps"] = ShiftSwapRequest.objects.count()
            ShiftSwapRequest.objects.all().delete()

            counts["staff_reallocations"] = StaffReallocation.objects.count()
            StaffReallocation.objects.all().delete()

            counts["leave_requests"] = LeaveRequest.objects.count()
            LeaveRequest.objects.all().delete()

            counts["activity_logs"] = ActivityLog.objects.count()
            ActivityLog.objects.all().delete()

            counts["blackout_periods"] = BlackoutPeriod.objects.count()
            BlackoutPeriod.objects.all().delete()

            counts["shifts"] = Shift.objects.count()
            Shift.objects.all().delete()

            user_queryset = User.objects.all()
            if include_admin:
                preserved_users = 0
            else:
                user_queryset = user_queryset.filter(is_superuser=False).exclude(role__name="ADMIN")
                preserved_users = User.objects.count() - user_queryset.count()

            counts["users"] = user_queryset.count()
            user_queryset.delete()

        self.stdout.write(self.style.SUCCESS("Roster data reset completed."))
        for label, amount in counts.items():
            self.stdout.write(f"- Deleted {amount} {label.replace('_', ' ')}")

        if not include_admin:
            self.stdout.write(
                self.style.WARNING(
                    "Admin and superuser accounts were preserved. Use --include-admin to remove them as well."
                )
            )
            self.stdout.write(f"- Preserved {preserved_users} admin/superuser accounts")
        else:
            self.stdout.write(self.style.WARNING("All user accounts were deleted."))
