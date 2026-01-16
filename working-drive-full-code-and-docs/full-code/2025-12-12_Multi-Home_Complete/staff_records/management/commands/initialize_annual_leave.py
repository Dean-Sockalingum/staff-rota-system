"""
Management command to initialize annual leave entitlements for all staff members.

This command creates AnnualLeaveEntitlement records for staff who don't have one
for the current leave year, and creates the initial transaction record.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from scheduling.models import User
from staff_records.models import (
    AnnualLeaveEntitlement,
    AnnualLeaveTransaction,
    StaffProfile,
)


class Command(BaseCommand):
    help = "Initialize annual leave entitlements for all active staff"

    def add_arguments(self, parser):
        parser.add_argument(
            '--year-start',
            type=str,
            help='Leave year start date (YYYY-MM-DD), defaults to current year January 1st'
        )
        parser.add_argument(
            '--entitlement-hours',
            type=float,
            default=196.0,  # 28 days × 7 hours for 35hr/week staff
            help='Default entitlement in hours (default: 196 = 28 days)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of entitlements even if they exist'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # Determine leave year start
        if options['year_start']:
            year_start = date.fromisoformat(options['year_start'])
        else:
            today = date.today()
            # Calendar year: January 1st - December 31st
            year_start = date(today.year, 1, 1)
        
        year_end = date(year_start.year, 12, 31)
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"Initializing Annual Leave Entitlements")
        self.stdout.write(f"{'='*60}\n")
        self.stdout.write(f"Leave Year: {year_start} to {year_end}\n")
        
        # Get all active staff with profiles
        active_users = User.objects.filter(
            is_active=True,
            is_staff=False  # Exclude admin/management
        ).select_related('staff_profile')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for user in active_users:
            # Ensure staff profile exists
            profile, _ = StaffProfile.objects.get_or_create(
                user=user,
                defaults={
                    'employment_status': 'ACTIVE',
                    'job_title': user.role.name if user.role else 'Care Staff',
                }
            )
            
            # Check if entitlement exists
            entitlement_exists = AnnualLeaveEntitlement.objects.filter(
                profile=profile,
                leave_year_start=year_start
            ).exists()
            
            if entitlement_exists and not options['force']:
                skipped_count += 1
                continue
            
            # Calculate contracted hours (based on shifts per week)
            shifts_per_week = user.shifts_per_week_override or 3
            hours_per_shift = Decimal('11.5')  # Day: 7am-7pm, Night: 7pm-7am
            contracted_hours_per_week = Decimal(shifts_per_week) * hours_per_shift
            
            # Calculate pro-rata entitlement
            # Full-time (35hrs) = 196 hours (28 days × 7hrs)
            # Part-time is pro-rated
            full_time_hours = Decimal('35.0')
            full_time_entitlement = Decimal(str(options['entitlement_hours']))
            
            if contracted_hours_per_week > 0:
                entitlement_hours = (contracted_hours_per_week / full_time_hours) * full_time_entitlement
            else:
                entitlement_hours = full_time_entitlement
            
            entitlement_hours = entitlement_hours.quantize(Decimal('0.01'))
            
            if options['force'] and entitlement_exists:
                # Update existing
                entitlement = AnnualLeaveEntitlement.objects.get(
                    profile=profile,
                    leave_year_start=year_start
                )
                entitlement.total_entitlement_hours = entitlement_hours
                entitlement.contracted_hours_per_week = contracted_hours_per_week
                entitlement.save()
                updated_count += 1
                action = "Updated"
            else:
                # Create new entitlement
                entitlement = AnnualLeaveEntitlement.objects.create(
                    profile=profile,
                    leave_year_start=year_start,
                    leave_year_end=year_end,
                    total_entitlement_hours=entitlement_hours,
                    contracted_hours_per_week=contracted_hours_per_week,
                    hours_remaining=entitlement_hours,
                )
                
                # Create initial transaction
                AnnualLeaveTransaction.objects.create(
                    entitlement=entitlement,
                    transaction_type='INITIAL',
                    hours=entitlement_hours,
                    balance_after=entitlement_hours,
                    description=f"Initial entitlement for leave year {year_start.year}",
                    created_by=None,
                )
                created_count += 1
                action = "Created"
            
            # Calculate days equivalent
            hours_per_day = contracted_hours_per_week / Decimal('5.0') if contracted_hours_per_week > 0 else Decimal('7.0')
            days_entitlement = (entitlement_hours / hours_per_day).quantize(Decimal('0.1'))
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓ {action}: {user.full_name:30s} | "
                    f"{entitlement_hours:6.1f}hrs ({days_entitlement:4.1f} days) | "
                    f"{contracted_hours_per_week:.1f}hrs/week"
                )
            )
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS(f"Summary:"))
        self.stdout.write(f"  Created:  {created_count} entitlements")
        self.stdout.write(f"  Updated:  {updated_count} entitlements")
        self.stdout.write(f"  Skipped:  {skipped_count} (already exist)")
        self.stdout.write(f"  Total:    {active_users.count()} active staff")
        self.stdout.write(f"{'='*60}\n")
        
        self.stdout.write(self.style.SUCCESS("✅ Annual leave initialization complete!"))
