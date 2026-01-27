from django.apps import AppConfig


class StaffRecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'staff_records'
    verbose_name = 'Staff Records'

    def ready(self):
        # Import signals to ensure staff profiles are created automatically.
        from . import signals  # noqa: F401
