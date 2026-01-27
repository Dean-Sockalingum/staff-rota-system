"""
Bulk operations service for Task 24
Handles multi-shift editing and batch operations
"""

from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


class BulkOperationError(Exception):
    """Custom exception for bulk operation errors"""
    pass


class BulkOperationHistory:
    """
    Track bulk operations for undo/redo functionality
    Stored in session to avoid database overhead
    """
    def __init__(self, session):
        self.session = session
        if 'bulk_operation_history' not in self.session:
            self.session['bulk_operation_history'] = []
    
    def add_operation(self, operation_type, affected_shifts, rollback_data):
        """Add operation to history"""
        history = self.session.get('bulk_operation_history', [])
        
        # Limit history to last 10 operations
        if len(history) >= 10:
            history.pop(0)
        
        history.append({
            'type': operation_type,
            'timestamp': timezone.now().isoformat(),
            'affected_shifts': affected_shifts,
            'rollback_data': rollback_data,
        })
        
        self.session['bulk_operation_history'] = history
        self.session.modified = True
    
    def get_last_operation(self):
        """Get last operation for undo"""
        history = self.session.get('bulk_operation_history', [])
        return history[-1] if history else None
    
    def clear_history(self):
        """Clear all operation history"""
        self.session['bulk_operation_history'] = []
        self.session.modified = True


def bulk_assign_shifts(staff_list, date_range, shift_type, unit, care_home, created_by):
    """
    Assign shifts to multiple staff members across multiple dates
    
    Args:
        staff_list: List of User objects
        date_range: Tuple of (start_date, end_date)
        shift_type: ShiftType object
        unit: Unit object
        care_home: CareHome object
        created_by: User who initiated the bulk operation
    
    Returns:
        dict: {
            'created': count,
            'skipped': count,
            'shift_ids': [list of created shift IDs],
            'errors': [list of error messages]
        }
    """
    from scheduling.models import Shift
    
    start_date, end_date = date_range
    created_count = 0
    skipped_count = 0
    shift_ids = []
    errors = []
    
    try:
        with transaction.atomic():
            current_date = start_date
            
            while current_date <= end_date:
                for staff in staff_list:
                    # Check if shift already exists
                    existing = Shift.objects.filter(
                        staff=staff,
                        date=current_date,
                        shift_type=shift_type,
                        unit=unit
                    ).exists()
                    
                    if existing:
                        skipped_count += 1
                        logger.info(f"Skipped duplicate shift for {staff.get_full_name()} on {current_date}")
                        continue
                    
                    # Create shift
                    try:
                        shift = Shift.objects.create(
                            staff=staff,
                            date=current_date,
                            shift_type=shift_type,
                            start_time=shift_type.start_time,
                            end_time=shift_type.end_time,
                            unit=unit,
                            care_home=care_home,
                            created_by=created_by
                        )
                        shift_ids.append(shift.id)
                        created_count += 1
                        logger.info(f"Created shift for {staff.get_full_name()} on {current_date}")
                    
                    except Exception as e:
                        error_msg = f"Error creating shift for {staff.get_full_name()} on {current_date}: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)
                
                current_date += timedelta(days=1)
    
    except Exception as e:
        raise BulkOperationError(f"Bulk assign failed: {str(e)}")
    
    return {
        'created': created_count,
        'skipped': skipped_count,
        'shift_ids': shift_ids,
        'errors': errors
    }


def bulk_delete_shifts(shift_queryset, deleted_by):
    """
    Delete multiple shifts at once
    
    Args:
        shift_queryset: QuerySet of Shift objects to delete
        deleted_by: User who initiated the deletion
    
    Returns:
        dict: {
            'deleted': count,
            'rollback_data': [list of deleted shift data for undo],
            'errors': [list of error messages]
        }
    """
    deleted_count = 0
    rollback_data = []
    errors = []
    
    try:
        with transaction.atomic():
            for shift in shift_queryset:
                # Save shift data for potential undo
                rollback_data.append({
                    'staff_id': shift.staff.id,
                    'date': shift.date.isoformat(),
                    'shift_type_id': shift.shift_type.id,
                    'start_time': shift.start_time.isoformat(),
                    'end_time': shift.end_time.isoformat(),
                    'unit_id': shift.unit.id,
                    'care_home_id': shift.care_home.id,
                })
                
                shift.delete()
                deleted_count += 1
                logger.info(f"Deleted shift {shift.id} for {shift.staff.get_full_name()} on {shift.date}")
    
    except Exception as e:
        raise BulkOperationError(f"Bulk delete failed: {str(e)}")
    
    return {
        'deleted': deleted_count,
        'rollback_data': rollback_data,
        'errors': errors
    }


def bulk_copy_week(source_week_start, target_week_start, care_home, units=None, staff_list=None, created_by=None):
    """
    Copy an entire week's schedule to another week
    
    Args:
        source_week_start: Date object for Monday of source week
        target_week_start: Date object for Monday of target week
        care_home: CareHome object
        units: Optional list of Unit objects to filter
        staff_list: Optional list of User objects to filter
        created_by: User who initiated the copy
    
    Returns:
        dict: {
            'copied': count,
            'skipped': count,
            'shift_ids': [list of created shift IDs],
            'errors': [list of error messages]
        }
    """
    from scheduling.models import Shift
    
    copied_count = 0
    skipped_count = 0
    shift_ids = []
    errors = []
    
    # Calculate week end dates
    source_week_end = source_week_start + timedelta(days=6)
    
    try:
        with transaction.atomic():
            # Get all shifts from source week
            source_shifts = Shift.objects.filter(
                care_home=care_home,
                date__range=[source_week_start, source_week_end]
            ).select_related('staff', 'shift_type', 'unit')
            
            # Apply filters
            if units:
                source_shifts = source_shifts.filter(unit__in=units)
            
            if staff_list:
                source_shifts = source_shifts.filter(staff__in=staff_list)
            
            # Copy each shift to target week
            for source_shift in source_shifts:
                # Calculate target date (same day of week)
                days_offset = (source_shift.date - source_week_start).days
                target_date = target_week_start + timedelta(days=days_offset)
                
                # Check if shift already exists
                existing = Shift.objects.filter(
                    staff=source_shift.staff,
                    date=target_date,
                    shift_type=source_shift.shift_type,
                    unit=source_shift.unit
                ).exists()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Create copy
                try:
                    new_shift = Shift.objects.create(
                        staff=source_shift.staff,
                        date=target_date,
                        shift_type=source_shift.shift_type,
                        start_time=source_shift.start_time,
                        end_time=source_shift.end_time,
                        unit=source_shift.unit,
                        care_home=source_shift.care_home,
                        created_by=created_by
                    )
                    shift_ids.append(new_shift.id)
                    copied_count += 1
                    logger.info(f"Copied shift for {new_shift.staff.get_full_name()} to {target_date}")
                
                except Exception as e:
                    error_msg = f"Error copying shift to {target_date}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
    
    except Exception as e:
        raise BulkOperationError(f"Bulk copy failed: {str(e)}")
    
    return {
        'copied': copied_count,
        'skipped': skipped_count,
        'shift_ids': shift_ids,
        'errors': errors
    }


def bulk_swap_staff(staff_a, staff_b, date_range, care_home, units=None):
    """
    Swap all shifts between two staff members in a date range
    
    Args:
        staff_a: First User object
        staff_b: Second User object
        date_range: Tuple of (start_date, end_date)
        care_home: CareHome object
        units: Optional list of Unit objects to filter
    
    Returns:
        dict: {
            'swapped': count,
            'errors': [list of error messages]
        }
    """
    from scheduling.models import Shift
    
    start_date, end_date = date_range
    swapped_count = 0
    errors = []
    
    try:
        with transaction.atomic():
            # Get shifts for both staff members
            shifts_a = Shift.objects.filter(
                staff=staff_a,
                care_home=care_home,
                date__range=[start_date, end_date]
            ).select_related('shift_type', 'unit')
            
            shifts_b = Shift.objects.filter(
                staff=staff_b,
                care_home=care_home,
                date__range=[start_date, end_date]
            ).select_related('shift_type', 'unit')
            
            # Apply unit filter
            if units:
                shifts_a = shifts_a.filter(unit__in=units)
                shifts_b = shifts_b.filter(unit__in=units)
            
            # Swap shifts
            for shift in shifts_a:
                shift.staff = staff_b
                shift.save()
                swapped_count += 1
            
            for shift in shifts_b:
                shift.staff = staff_a
                shift.save()
                swapped_count += 1
            
            logger.info(f"Swapped {swapped_count} shifts between {staff_a.get_full_name()} and {staff_b.get_full_name()}")
    
    except Exception as e:
        raise BulkOperationError(f"Bulk swap failed: {str(e)}")
    
    return {
        'swapped': swapped_count,
        'errors': errors
    }


def bulk_change_shift_type(shift_queryset, new_shift_type):
    """
    Change shift type for multiple shifts
    
    Args:
        shift_queryset: QuerySet of Shift objects
        new_shift_type: ShiftType object to change to
    
    Returns:
        dict: {
            'changed': count,
            'rollback_data': [list of original shift types for undo],
            'errors': [list of error messages]
        }
    """
    changed_count = 0
    rollback_data = []
    errors = []
    
    try:
        with transaction.atomic():
            for shift in shift_queryset:
                # Save original for undo
                rollback_data.append({
                    'shift_id': shift.id,
                    'original_shift_type_id': shift.shift_type.id,
                    'original_start_time': shift.start_time.isoformat(),
                    'original_end_time': shift.end_time.isoformat(),
                })
                
                # Update shift type and times
                shift.shift_type = new_shift_type
                shift.start_time = new_shift_type.start_time
                shift.end_time = new_shift_type.end_time
                shift.save()
                
                changed_count += 1
                logger.info(f"Changed shift {shift.id} to {new_shift_type.name}")
    
    except Exception as e:
        raise BulkOperationError(f"Bulk change shift type failed: {str(e)}")
    
    return {
        'changed': changed_count,
        'rollback_data': rollback_data,
        'errors': errors
    }


def undo_bulk_operation(operation_data):
    """
    Undo a bulk operation using saved rollback data
    
    Args:
        operation_data: Dict from BulkOperationHistory
    
    Returns:
        dict: {'undone': count, 'errors': [list of errors]}
    """
    from scheduling.models import Shift, User, ShiftType, Unit, CareHome
    
    operation_type = operation_data['type']
    rollback_data = operation_data['rollback_data']
    undone_count = 0
    errors = []
    
    try:
        with transaction.atomic():
            
            if operation_type == 'delete':
                # Recreate deleted shifts
                for shift_data in rollback_data:
                    try:
                        Shift.objects.create(
                            staff_id=shift_data['staff_id'],
                            date=shift_data['date'],
                            shift_type_id=shift_data['shift_type_id'],
                            start_time=shift_data['start_time'],
                            end_time=shift_data['end_time'],
                            unit_id=shift_data['unit_id'],
                            care_home_id=shift_data['care_home_id'],
                        )
                        undone_count += 1
                    except Exception as e:
                        errors.append(f"Error recreating shift: {str(e)}")
            
            elif operation_type == 'assign' or operation_type == 'copy':
                # Delete created shifts
                shift_ids = operation_data.get('affected_shifts', [])
                deleted = Shift.objects.filter(id__in=shift_ids).delete()
                undone_count = deleted[0]
            
            elif operation_type == 'change_type':
                # Restore original shift types
                for shift_data in rollback_data:
                    try:
                        shift = Shift.objects.get(id=shift_data['shift_id'])
                        shift.shift_type_id = shift_data['original_shift_type_id']
                        shift.start_time = shift_data['original_start_time']
                        shift.end_time = shift_data['original_end_time']
                        shift.save()
                        undone_count += 1
                    except Shift.DoesNotExist:
                        errors.append(f"Shift {shift_data['shift_id']} not found")
                    except Exception as e:
                        errors.append(f"Error restoring shift: {str(e)}")
            
            logger.info(f"Undo operation: {operation_type}, undone {undone_count} changes")
    
    except Exception as e:
        raise BulkOperationError(f"Undo failed: {str(e)}")
    
    return {
        'undone': undone_count,
        'errors': errors
    }


def validate_bulk_operation(operation_type, **kwargs):
    """
    Validate bulk operation parameters before execution
    
    Args:
        operation_type: Type of operation ('assign', 'delete', 'copy', 'swap', 'change_type')
        **kwargs: Operation-specific parameters
    
    Raises:
        ValidationError: If validation fails
    
    Returns:
        dict: {'valid': True, 'warnings': [list of warnings]}
    """
    warnings = []
    
    if operation_type == 'assign':
        staff_list = kwargs.get('staff_list', [])
        date_range = kwargs.get('date_range')
        
        if not staff_list:
            raise ValidationError("No staff members selected")
        
        if not date_range or not date_range[0] or not date_range[1]:
            raise ValidationError("Invalid date range")
        
        if date_range[1] < date_range[0]:
            raise ValidationError("End date must be after start date")
        
        # Warn if date range is very long
        days_diff = (date_range[1] - date_range[0]).days
        if days_diff > 90:
            warnings.append(f"Date range is {days_diff} days - this will create many shifts")
    
    elif operation_type == 'delete':
        shift_queryset = kwargs.get('shift_queryset')
        
        if not shift_queryset or not shift_queryset.exists():
            raise ValidationError("No shifts selected for deletion")
        
        # Warn if deleting many shifts
        count = shift_queryset.count()
        if count > 100:
            warnings.append(f"You are about to delete {count} shifts")
    
    elif operation_type == 'copy':
        source_week_start = kwargs.get('source_week_start')
        target_week_start = kwargs.get('target_week_start')
        
        if not source_week_start or not target_week_start:
            raise ValidationError("Invalid week dates")
        
        if source_week_start == target_week_start:
            raise ValidationError("Source and target weeks must be different")
    
    elif operation_type == 'swap':
        staff_a = kwargs.get('staff_a')
        staff_b = kwargs.get('staff_b')
        
        if not staff_a or not staff_b:
            raise ValidationError("Two staff members must be selected")
        
        if staff_a == staff_b:
            raise ValidationError("Cannot swap shifts with the same person")
    
    return {
        'valid': True,
        'warnings': warnings
    }


def get_bulk_operation_preview(operation_type, **kwargs):
    """
    Generate preview of what a bulk operation will affect
    
    Args:
        operation_type: Type of operation
        **kwargs: Operation-specific parameters
    
    Returns:
        dict: Preview data including affected shifts count
    """
    from scheduling.models import Shift
    
    preview = {
        'operation_type': operation_type,
        'affected_count': 0,
        'details': {}
    }
    
    if operation_type == 'assign':
        staff_list = kwargs.get('staff_list', [])
        date_range = kwargs.get('date_range')
        
        if staff_list and date_range:
            days = (date_range[1] - date_range[0]).days + 1
            preview['affected_count'] = len(staff_list) * days
            preview['details'] = {
                'staff_count': len(staff_list),
                'days': days,
                'total_shifts': preview['affected_count']
            }
    
    elif operation_type == 'delete':
        shift_queryset = kwargs.get('shift_queryset')
        if shift_queryset:
            preview['affected_count'] = shift_queryset.count()
    
    elif operation_type == 'copy':
        from scheduling.models import Shift
        source_week_start = kwargs.get('source_week_start')
        care_home = kwargs.get('care_home')
        
        if source_week_start and care_home:
            source_week_end = source_week_start + timedelta(days=6)
            source_count = Shift.objects.filter(
                care_home=care_home,
                date__range=[source_week_start, source_week_end]
            ).count()
            preview['affected_count'] = source_count
            preview['details'] = {'source_shifts': source_count}
    
    elif operation_type == 'swap':
        staff_a = kwargs.get('staff_a')
        staff_b = kwargs.get('staff_b')
        date_range = kwargs.get('date_range')
        care_home = kwargs.get('care_home')
        
        if all([staff_a, staff_b, date_range, care_home]):
            count_a = Shift.objects.filter(
                staff=staff_a,
                care_home=care_home,
                date__range=date_range
            ).count()
            count_b = Shift.objects.filter(
                staff=staff_b,
                care_home=care_home,
                date__range=date_range
            ).count()
            preview['affected_count'] = count_a + count_b
            preview['details'] = {
                f'{staff_a.get_full_name()} shifts': count_a,
                f'{staff_b.get_full_name()} shifts': count_b
            }
    
    return preview
