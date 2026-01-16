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
        
        # Phase 6: Register models for audit logging
        # Scottish Design Principle: Transparency for CQC compliance
        self.register_audit_logging()
    
    def register_audit_logging(self):
        """Register critical models with django-auditlog for change tracking."""
        try:
            from auditlog.registry import auditlog
            from .models import (
                User, Role, Unit, CareHome, Shift, ShiftType,
                StaffingRequirement, LeaveRequest, Team, Resident,
                ComplianceCheck, ComplianceViolation
            )
            
            # User Management - Track all staff record changes
            auditlog.register(User, exclude_fields=['password', 'last_login'])
            auditlog.register(Role)
            
            # Organizational Structure - Track facility changes
            auditlog.register(CareHome)
            auditlog.register(Unit)
            auditlog.register(Team)
            
            # Scheduling - Track all shift assignments and changes
            auditlog.register(Shift)
            auditlog.register(ShiftType)
            auditlog.register(StaffingRequirement)
            
            # Leave Management - Track approval workflow
            auditlog.register(LeaveRequest)
            
            # Compliance - CQC requirement
            auditlog.register(ComplianceCheck)
            auditlog.register(ComplianceViolation)
            
            # Resident Records - Data protection compliance
            auditlog.register(Resident, exclude_fields=['emergency_contact_details'])
            
        except ImportError:
            # Auditlog not installed yet during initial migrations
            pass
