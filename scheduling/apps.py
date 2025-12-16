from django.apps import AppConfig


class SchedulingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduling'
    
    def ready(self):
        """Import signals and initialize workflow helpers when Django starts."""
        import scheduling.signals  # noqa
        
        # Attach workflow helper methods to Shift model
        from scheduling.shift_helpers import attach_workflow_methods
        attach_workflow_methods()
