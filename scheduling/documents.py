"""
Task 49: Elasticsearch Document Definitions
Defines how Django models are indexed in Elasticsearch for full-text search
"""
from django.db import models
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import User, Shift, LeaveRequest, CareHome, Role
from staff_records.models import StaffProfile


@registry.register_document
class UserDocument(Document):
    """
    Elasticsearch document for User/Staff search
    Indexes: name, SAP number, email, role, care home
    """
    # Related fields
    role_name = fields.TextField(attr='staffprofile.role.name')
    care_home_name = fields.TextField(attr='staffprofile.current_care_home.name')
    
    # Computed fields
    full_name = fields.TextField()
    
    class Index:
        name = 'staff'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'max_result_window': 10000,
        }
    
    class Django:
        model = User
        fields = [
            'sap',
            'first_name',
            'last_name',
            'email',
            'is_active',
        ]
        related_models = [StaffProfile, Role, CareHome]
    
    def get_instances_from_related(self, related_instance):
        """
        Update document when related models change
        """
        if isinstance(related_instance, StaffProfile):
            return related_instance.user
        elif isinstance(related_instance, (Role, CareHome)):
            # Update all users with this role/care home
            return User.objects.filter(
                staffprofile__role=related_instance
            ) if isinstance(related_instance, Role) else User.objects.filter(
                staffprofile__current_care_home=related_instance
            )
    
    def prepare_full_name(self, instance):
        """Generate full name for search"""
        return instance.get_full_name()


@registry.register_document
class ShiftDocument(Document):
    """
    Elasticsearch document for Shift search
    Indexes: date, time, care home, assigned staff, shift type
    """
    # Related fields
    care_home_name = fields.TextField(attr='care_home.name')
    assigned_to_name = fields.TextField(attr='assigned_to.get_full_name')
    assigned_to_sap = fields.KeywordField(attr='assigned_to.sap')
    
    # Date fields for range filtering
    date = fields.DateField()
    start_time = fields.TextField()
    end_time = fields.TextField()
    
    # Shift details
    shift_type = fields.KeywordField()
    shift_type_display = fields.TextField()
    notes = fields.TextField()
    
    class Index:
        name = 'shifts'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'max_result_window': 10000,
        }
    
    class Django:
        model = Shift
        fields = [
            'id',
        ]
        related_models = [User, CareHome]
    
    def get_instances_from_related(self, related_instance):
        """Update when User or CareHome changes"""
        if isinstance(related_instance, User):
            return related_instance.assigned_shifts.all()
        elif isinstance(related_instance, CareHome):
            return related_instance.shift_set.all()
    
    def prepare_shift_type_display(self, instance):
        """Get human-readable shift type"""
        return instance.get_shift_type_display()


@registry.register_document
class LeaveRequestDocument(Document):
    """
    Elasticsearch document for Leave Request search
    Indexes: staff name, dates, reason, approval status
    """
    # Related fields
    staff_name = fields.TextField(attr='staff.get_full_name')
    staff_sap = fields.KeywordField(attr='staff.sap')
    approved_by_name = fields.TextField(attr='approved_by.get_full_name')
    
    # Date fields for range filtering
    start_date = fields.DateField()
    end_date = fields.DateField()
    requested_at = fields.DateField()
    
    # Fields
    reason = fields.TextField()
    notes = fields.TextField()
    approved = fields.BooleanField()
    
    # Status field
    approval_status = fields.TextField()
    
    class Index:
        name = 'leave_requests'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'max_result_window': 10000,
        }
    
    class Django:
        model = LeaveRequest
        fields = [
            'id',
        ]
        related_models = [User]
    
    def get_instances_from_related(self, related_instance):
        """Update when User changes"""
        if isinstance(related_instance, User):
            # Update leave requests for this user (both as staff and approver)
            return LeaveRequest.objects.filter(
                models.Q(staff=related_instance) | models.Q(approved_by=related_instance)
            )
    
    def prepare_approval_status(self, instance):
        """Generate approval status text"""
        if instance.approved is None:
            return "Pending"
        elif instance.approved:
            return "Approved"
        else:
            return "Rejected"


@registry.register_document
class CareHomeDocument(Document):
    """
    Elasticsearch document for Care Home search
    Indexes: name, address, contact details
    """
    # Fields
    name = fields.KeywordField()
    location_address = fields.TextField()
    postcode = fields.KeywordField()
    main_phone = fields.KeywordField()
    main_email = fields.KeywordField()
    
    # Nested address field
    full_address = fields.TextField()
    
    class Index:
        name = 'care_homes'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'max_result_window': 10000,
        }
    
    class Django:
        model = CareHome
        fields = [
            'id',
            'bed_capacity',
            'current_occupancy',
            'is_active',
        ]
    
    def prepare_full_address(self, instance):
        """Generate full address for search"""
        parts = [instance.location_address, instance.postcode]
        return ", ".join([p for p in parts if p])
