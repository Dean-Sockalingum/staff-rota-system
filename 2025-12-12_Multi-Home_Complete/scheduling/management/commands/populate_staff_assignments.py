"""
Management command to populate staff unit and home_unit assignments based on their existing shifts.
This ensures all staff have proper care home associations for performance tracking.
"""
from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from scheduling.models import User, Shift, Unit, CareHome
from datetime import datetime


class Command(BaseCommand):
    help = 'Populate staff unit and home_unit assignments based on their shift history'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even for staff who already have assignments',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('Populating Staff Unit Assignments from Shift Data'))
        self.stdout.write(self.style.SUCCESS('=' * 80))

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Get all active staff
        staff_queryset = User.objects.filter(is_active=True)
        total_staff = staff_queryset.count()
        
        self.stdout.write(f'\nTotal active staff: {total_staff}')
        
        # Stats tracking
        stats = {
            'already_assigned': 0,
            'updated': 0,
            'no_shifts': 0,
            'errors': 0,
        }
        
        for staff in staff_queryset:
            try:
                # Check if staff already has unit assignment
                if staff.unit and staff.home_unit and not force:
                    stats['already_assigned'] += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ {staff.sap} - {staff.get_full_name()}: '
                            f'Already assigned to {staff.unit} (home: {staff.home_unit})'
                        )
                    )
                    continue
                
                # Get shift data for this staff member
                shift_data = (
                    Shift.objects
                    .filter(user=staff)
                    .values('unit', 'unit__care_home')
                    .annotate(shift_count=Count('id'))
                    .order_by('-shift_count')
                )
                
                if not shift_data:
                    stats['no_shifts'] += 0
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠ {staff.sap} - {staff.get_full_name()}: '
                            f'No shifts found'
                        )
                    )
                    continue
                
                # Get the unit where they work most frequently
                primary_unit_data = shift_data[0]
                primary_unit = Unit.objects.get(id=primary_unit_data['unit'])
                
                # Get care home through unit
                care_home = primary_unit.care_home
                
                if not care_home:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  ✗ {staff.sap} - {staff.get_full_name()}: '
                            f'Unit {primary_unit} has no care home assigned'
                        )
                    )
                    stats['errors'] += 1
                    continue
                
                # Show what we found
                total_shifts = sum(s['shift_count'] for s in shift_data)
                primary_shifts = primary_unit_data['shift_count']
                percentage = (primary_shifts / total_shifts * 100) if total_shifts > 0 else 0
                
                self.stdout.write(
                    f'\n  {staff.sap} - {staff.get_full_name()}:'
                )
                self.stdout.write(
                    f'    Primary Unit: {primary_unit} ({primary_shifts}/{total_shifts} shifts - {percentage:.1f}%)'
                )
                self.stdout.write(
                    f'    Care Home: {care_home}'
                )
                
                # Show all units they work in
                if len(shift_data) > 1:
                    self.stdout.write(f'    Also works in:')
                    for data in shift_data[1:4]:  # Show top 3 other units
                        unit = Unit.objects.get(id=data['unit'])
                        count = data['shift_count']
                        pct = (count / total_shifts * 100)
                        self.stdout.write(f'      - {unit} ({count} shifts - {pct:.1f}%)')
                
                # Update the staff record
                if not dry_run:
                    old_unit = staff.unit
                    old_home = staff.home_unit
                    
                    staff.unit = primary_unit
                    staff.home_unit = primary_unit
                    
                    try:
                        staff.save(update_fields=['unit', 'home_unit'])
                        
                        change_msg = []
                        if old_unit != primary_unit:
                            change_msg.append(f'unit: {old_unit} → {primary_unit}')
                        if old_home != primary_unit:
                            change_msg.append(f'home_unit: {old_home} → {primary_unit}')
                        
                        if change_msg:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'    ✓ Updated: {", ".join(change_msg)}'
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'    ✓ Confirmed existing assignment'
                                )
                            )
                        
                        stats['updated'] += 1
                    except Exception as save_error:
                        self.stdout.write(
                            self.style.ERROR(
                                f'    ✗ Failed to save: {str(save_error)}'
                            )
                        )
                        stats['errors'] += 1
                        continue
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'    [DRY RUN] Would update unit={primary_unit}, home_unit={primary_unit}'
                        )
                    )
                    stats['updated'] += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'  ✗ {staff.sap} - {staff.get_full_name()}: Error - {str(e)}'
                    )
                )
                stats['errors'] += 1
        
        # Print summary
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write('=' * 80)
        self.stdout.write(f'Total staff processed: {total_staff}')
        self.stdout.write(f'Already correctly assigned: {stats["already_assigned"]}')
        self.stdout.write(f'Updated: {stats["updated"]}')
        self.stdout.write(f'No shifts found: {stats["no_shifts"]}')
        self.stdout.write(f'Errors: {stats["errors"]}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    '\nThis was a DRY RUN. Run without --dry-run to apply changes.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Successfully updated {stats["updated"]} staff assignments!'
                )
            )
