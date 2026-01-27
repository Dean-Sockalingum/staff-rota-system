from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from quality_audits.models import (
    PDSAProject, PDSACycle, PDSADataPoint, PDSATeamMember
)
from scheduling.models import CareHome, Unit

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with sample PDSA project data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample PDSA data...')
        
        # Get existing user
        try:
            user = User.objects.get(sap='000541')
            self.stdout.write(f'Using existing user: {user.sap} - {user.get_full_name()}')
        except User.DoesNotExist:
            # If no user with this SAP, get the first staff user
            user = User.objects.filter(is_staff=True).first()
            if not user:
                self.stdout.write(self.style.ERROR('No staff users found. Please create a user first.'))
                return
            self.stdout.write(f'Using user: {user.sap} - {user.get_full_name()}')
        
        # Get first care home and unit
        care_home = CareHome.objects.first()
        unit = Unit.objects.first()
        
        if not care_home:
            self.stdout.write(self.style.ERROR('No care homes found. Please create care homes first.'))
            return
        
        # Sample projects data
        projects_data = [
            {
                'title': 'Reduce Medication Errors',
                'aim_statement': 'Reduce medication administration errors by 50% within 12 weeks through implementation of a double-check system',
                'problem_description': 'Current medication error rate is 12 per 100 administrations, causing potential harm to residents',
                'target_population': 'All residents receiving regular medications (n=45)',
                'category': 'clinical_outcomes',
                'priority': 'high',
                'baseline_value': 12.0,
                'target_value': 6.0,
                'measurement_unit': 'errors per 100 administrations',
                'status': 'active',
            },
            {
                'title': 'Improve Hand Hygiene Compliance',
                'aim_statement': 'Increase hand hygiene compliance from 65% to 95% among all staff within 8 weeks',
                'problem_description': 'Observations show only 65% of staff follow proper hand hygiene protocols',
                'target_population': 'All care staff (n=28)',
                'category': 'infection_control',
                'priority': 'high',
                'baseline_value': 65.0,
                'target_value': 95.0,
                'measurement_unit': '% compliance',
                'status': 'active',
            },
            {
                'title': 'Reduce Falls in Dementia Unit',
                'aim_statement': 'Reduce falls by 40% in dementia unit through environmental modifications and staff training',
                'problem_description': 'Average 8 falls per month in dementia unit, well above benchmark of 5',
                'target_population': 'Dementia unit residents (n=18)',
                'category': 'safety',
                'priority': 'critical',
                'baseline_value': 8.0,
                'target_value': 4.8,
                'measurement_unit': 'falls per month',
                'status': 'active',
            },
            {
                'title': 'Increase Family Satisfaction',
                'aim_statement': 'Improve family satisfaction scores from 7.2 to 8.5 out of 10 through enhanced communication',
                'problem_description': 'Family feedback indicates communication gaps and delayed responses to concerns',
                'target_population': 'Families of all residents (n=50 families)',
                'category': 'person_centered_care',
                'priority': 'medium',
                'baseline_value': 7.2,
                'target_value': 8.5,
                'measurement_unit': 'satisfaction score (0-10)',
                'status': 'planning',
            },
            {
                'title': 'Reduce Pressure Ulcers',
                'aim_statement': 'Achieve zero hospital-acquired pressure ulcers through enhanced skin assessment and repositioning protocol',
                'problem_description': 'Currently 3 pressure ulcers per quarter, all preventable with proper care',
                'target_population': 'High-risk residents (n=12)',
                'category': 'clinical_outcomes',
                'priority': 'critical',
                'baseline_value': 3.0,
                'target_value': 0.0,
                'measurement_unit': 'pressure ulcers per quarter',
                'status': 'completed',
            }
        ]
        
        created_projects = []
        
        for proj_data in projects_data:
            project, created = PDSAProject.objects.get_or_create(
                title=proj_data['title'],
                defaults={
                    **proj_data,
                    'lead_user': user,
                    'care_home': care_home,
                    'unit': unit,
                    'start_date': timezone.now().date() - timedelta(days=random.randint(30, 90)),
                    'target_completion_date': timezone.now().date() + timedelta(days=random.randint(30, 120)),
                }
            )
            
            if created:
                created_projects.append(project)
                self.stdout.write(self.style.SUCCESS(f'Created project: {project.title}'))
                
                # Add team member
                PDSATeamMember.objects.get_or_create(
                    project=project,
                    user=user,
                    defaults={'role': 'lead'}
                )
                
                # Create cycles for active and completed projects
                if project.status in ['active', 'completed']:
                    num_cycles = 3 if project.status == 'active' else 4
                    
                    for cycle_num in range(1, num_cycles + 1):
                        cycle = self._create_cycle(project, cycle_num, user)
                        self._create_data_points(cycle, project)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(created_projects)} projects with cycles and data points'))
    
    def _create_cycle(self, project, cycle_number, user):
        """Create a PDSA cycle"""
        cycle, created = PDSACycle.objects.get_or_create(
            project=project,
            cycle_number=cycle_number,
            defaults={
                'hypothesis': f'If we implement intervention {cycle_number}, then we will see improvement in {project.measurement_unit}',
                'prediction': f'We predict a {10 * cycle_number}% improvement in the first 2 weeks',
                'change_idea': f'Cycle {cycle_number}: Test specific intervention targeting root cause #{cycle_number}',
                'data_collection_plan': 'Daily measurements recorded by shift supervisor',
                'plan_start_date': timezone.now().date() - timedelta(days=30 - (cycle_number * 7)),
                'plan_end_date': timezone.now().date() - timedelta(days=16 - (cycle_number * 7)),
                'do_start_date': timezone.now().date() - timedelta(days=30 - (cycle_number * 7)),
                'do_end_date': timezone.now().date() - timedelta(days=16 - (cycle_number * 7)),
                'execution_log': f'Implemented change on schedule. Staff training completed. {random.randint(80, 95)}% adherence observed.',
                'observations': f'Initial resistance from some staff. Improvement noted by day {random.randint(3, 7)}.',
                'deviations': 'Minor deviations during weekend shifts due to staffing changes.',
                'staff_feedback': 'Mostly positive. Staff appreciate the structured approach and clear protocols.',
                'data_analysis': f'Statistical analysis shows {"significant" if cycle_number > 1 else "moderate"} improvement trend.',
                'findings': f'{"Achieved" if cycle_number > 1 else "Approaching"} target improvement. Data shows consistent trend.',
                'comparison_to_prediction': f'Results {"exceeded" if cycle_number > 1 else "met"} our predictions.',
                'lessons_learned': f'Key learning: Early engagement with night staff critical. Consider {random.choice(["visual cues", "reminders", "champions"])} for next cycle.',
                'unexpected_outcomes': 'Unexpected positive impact on staff morale and teamwork.',
                'act_decision': 'adopt' if cycle_number == 1 else 'adapt',
                'next_steps': f'Scale to additional units' if cycle_number > 2 else f'Refine approach and test cycle {cycle_number + 1}',
                'new_cycle_planned': cycle_number < 4,
                'spread_plan': f'Plan to spread to all units if final cycle successful' if cycle_number > 2 else f'Not planning spread yet for cycle {cycle_number}',
            }
        )
        
        if created:
            self.stdout.write(f'  Created Cycle #{cycle_number} for {project.title}')
        
        return cycle
    
    def _create_data_points(self, cycle, project):
        """Create data points for a cycle"""
        # Create 10-15 data points over the cycle period
        num_points = random.randint(10, 15)
        
        # Calculate improvement trajectory
        baseline = project.baseline_value
        target = project.target_value
        improving = target < baseline  # True if lower is better
        
        for i in range(num_points):
            # Create gradual improvement with some variation
            progress = i / num_points
            if improving:
                # Moving from high (baseline) to low (target)
                trend_value = baseline - (baseline - target) * progress * 0.7
            else:
                # Moving from low (baseline) to high (target)
                trend_value = baseline + (target - baseline) * progress * 0.7
            
            # Add random variation (±10%)
            variation = random.uniform(-0.1, 0.1) * abs(baseline - target)
            value = trend_value + variation
            
            # Ensure value stays in reasonable range
            if improving:
                value = max(target * 0.9, min(baseline * 1.1, value))
            else:
                value = min(target * 1.1, max(baseline * 0.9, value))
            
            measurement_date = cycle.do_start_date + timedelta(days=i)
            
            PDSADataPoint.objects.get_or_create(
                cycle=cycle,
                measurement_date=measurement_date,
                defaults={
                    'value': round(value, 2),
                    'notes': random.choice([
                        'Normal conditions',
                        'Weekend measurement',
                        'Post-training session',
                        'Staff feedback positive',
                        'Some resistance noted',
                        'Protocol followed correctly',
                    ]) if i % 3 == 0 else ''
                }
            )
        
        self.stdout.write(f'    Created {num_points} data points for Cycle #{cycle.cycle_number}')
