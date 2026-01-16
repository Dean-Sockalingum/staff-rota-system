from django.core.management.base import BaseCommand
from scheduling.models import User, Unit
import random

class Command(BaseCommand):
    help = 'Redistribute SCW and SCA staff across care units as home assignments'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Redistributing SCW and SCA staff to care units...'))
        
        # Get all care units (excluding ADMIN)
        care_units = list(Unit.objects.filter(is_active=True).exclude(name='ADMIN'))
        
        if not care_units:
            self.stdout.write(self.style.ERROR('No care units found!'))
            return
        
        # Get all SCW and SCA staff (exclude management roles)
        scw_staff = list(User.objects.filter(
            role__name='SCW',
            is_active=True
        ).order_by('team', 'sap'))
        
        sca_staff = list(User.objects.filter(
            role__name='SCA', 
            is_active=True
        ).order_by('team', 'sap'))
        
        self.stdout.write(f'Found {len(scw_staff)} SCW staff and {len(sca_staff)} SCA staff')
        self.stdout.write(f'Distributing across {len(care_units)} care units')
        
        # Clear existing home unit assignments for care staff
        User.objects.filter(role__name__in=['SCW', 'SCA']).update(home_unit=None)
        
        # Distribute SCW staff evenly across units
        unit_assignments = {unit.name: {'SCW': [], 'SCA': []} for unit in care_units}
        
        # Assign SCW staff (distribute evenly, trying to balance teams)
        random.shuffle(scw_staff)  # Add some randomness
        for i, staff in enumerate(scw_staff):
            unit = care_units[i % len(care_units)]
            staff.home_unit = unit
            staff.unit = unit  # Also set current unit
            staff.save()
            unit_assignments[unit.name]['SCW'].append(staff)
            self.stdout.write(f'  Assigned SCW {staff.sap} ({staff.first_name} {staff.last_name}) - Team {staff.team or "None"} to {unit.get_name_display()}')
        
        # Assign SCA staff (distribute evenly, trying to balance teams)
        random.shuffle(sca_staff)  # Add some randomness
        for i, staff in enumerate(sca_staff):
            unit = care_units[i % len(care_units)]
            staff.home_unit = unit
            staff.unit = unit  # Also set current unit
            staff.save()
            unit_assignments[unit.name]['SCA'].append(staff)
            self.stdout.write(f'  Assigned SCA {staff.sap} ({staff.first_name} {staff.last_name}) - Team {staff.team or "None"} to {unit.get_name_display()}')
        
        # Show summary
        self.stdout.write(self.style.SUCCESS('\n📊 HOME UNIT ASSIGNMENT SUMMARY:'))
        self.stdout.write('=' * 60)
        
        total_assigned = 0
        for unit in care_units:
            scw_count = len(unit_assignments[unit.name]['SCW'])
            sca_count = len(unit_assignments[unit.name]['SCA'])
            total = scw_count + sca_count
            total_assigned += total
            
            self.stdout.write(f'\\n🏢 {unit.get_name_display()}:')
            self.stdout.write(f'  👥 SCW: {scw_count} staff')
            self.stdout.write(f'  👥 SCA: {sca_count} staff')
            self.stdout.write(f'  📋 Total: {total} staff')
            
            # Show team distribution
            teams = {'A': 0, 'B': 0, 'C': 0, None: 0}
            for staff in unit_assignments[unit.name]['SCW'] + unit_assignments[unit.name]['SCA']:
                teams[staff.team] += 1
            
            self.stdout.write(f'  🎯 Team A: {teams["A"]}, Team B: {teams["B"]}, Team C: {teams["C"]}, Unassigned: {teams[None]}')
        
        self.stdout.write(self.style.SUCCESS(f'\\n✅ Successfully assigned {total_assigned} care staff to home units!'))
        self.stdout.write('💡 Staff can still be temporarily deployed to other units for cover')