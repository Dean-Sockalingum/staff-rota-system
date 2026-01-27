"""
Management command to populate sample risks for Module 6 testing

Creates:
- Risk categories aligned with Care Inspectorate themes
- Sample risks across all priority levels
- Mitigation plans
- Risk reviews
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from risk_management.models import (
    RiskCategory, RiskRegister, RiskMitigation, RiskReview
)
from scheduling.models import Home
from datetime import date, timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Populate sample risk data for Module 6 testing'

    def handle(self, *args, **options):
        self.stdout.write('Populating Module 6: Risk Management...')
        
        # Get admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('No admin user found.'))
            return
        
        # Get first care home
        care_home = Home.objects.first()
        if not care_home:
            self.stdout.write(self.style.ERROR('No care homes found.'))
            return
        
        # Create Risk Categories
        categories_data = [
            {
                'name': 'Clinical & Care Quality',
                'description': 'Risks related to quality of clinical care and resident outcomes',
                'color': '#dc3545',
                'care_inspectorate_theme': 'Care & Support',
                'his_domain': 'Person-centred Care',
                'risks': [
                    {
                        'title': 'Medication Errors',
                        'description': 'Risk of medication administration errors leading to resident harm',
                        'likelihood': 3,
                        'impact': 4,
                        'priority': 'HIGH'
                    },
                    {
                        'title': 'Falls Management',
                        'description': 'Inadequate falls prevention and management protocols',
                        'likelihood': 4,
                        'impact': 3,
                        'priority': 'HIGH'
                    },
                ]
            },
            {
                'name': 'Health & Safety',
                'description': 'Environmental and workplace safety risks',
                'color': '#fd7e14',
                'care_inspectorate_theme': 'Setting',
                'his_domain': 'Safe Care',
                'risks': [
                    {
                        'title': 'Fire Safety Compliance',
                        'description': 'Non-compliance with fire safety regulations',
                        'likelihood': 2,
                        'impact': 5,
                        'priority': 'CRITICAL'
                    },
                    {
                        'title': 'Manual Handling Injuries',
                        'description': 'Staff injuries from improper manual handling techniques',
                        'likelihood': 3,
                        'impact': 3,
                        'priority': 'MEDIUM'
                    },
                ]
            },
            {
                'name': 'Safeguarding',
                'description': 'Risks related to adult protection and safeguarding',
                'color': '#6f42c1',
                'care_inspectorate_theme': 'Wellbeing',
                'his_domain': 'Person-centred Care',
                'risks': [
                    {
                        'title': 'Adult Protection Concerns',
                        'description': 'Potential safeguarding incidents not being identified or reported',
                        'likelihood': 2,
                        'impact': 5,
                        'priority': 'CRITICAL'
                    },
                ]
            },
            {
                'name': 'Infection Prevention & Control',
                'description': 'Infection control and outbreak management risks',
                'color': '#20c997',
                'care_inspectorate_theme': 'Care & Support',
                'his_domain': 'Safe Care',
                'risks': [
                    {
                        'title': 'Healthcare Associated Infections',
                        'description': 'Risk of HAI outbreaks due to inadequate IPC practices',
                        'likelihood': 3,
                        'impact': 4,
                        'priority': 'HIGH'
                    },
                ]
            },
            {
                'name': 'Staffing & Workforce',
                'description': 'Staffing levels and workforce management risks',
                'color': '#0dcaf0',
                'care_inspectorate_theme': 'Staff',
                'his_domain': 'Effective Care',
                'risks': [
                    {
                        'title': 'Insufficient Staffing Levels',
                        'description': 'Inability to maintain safe staffing ratios during peak periods',
                        'likelihood': 4,
                        'impact': 4,
                        'priority': 'HIGH'
                    },
                    {
                        'title': 'Staff Turnover',
                        'description': 'High staff turnover impacting continuity of care',
                        'likelihood': 3,
                        'impact': 3,
                        'priority': 'MEDIUM'
                    },
                ]
            },
            {
                'name': 'Regulatory & Compliance',
                'description': 'Regulatory compliance and inspection risks',
                'color': '#6610f2',
                'care_inspectorate_theme': 'Leadership',
                'his_domain': 'Well Led',
                'risks': [
                    {
                        'title': 'Care Inspectorate Requirements',
                        'description': 'Non-compliance with Care Inspectorate requirements',
                        'likelihood': 2,
                        'impact': 4,
                        'priority': 'HIGH'
                    },
                ]
            },
        ]
        
        risk_count = 0
        
        for cat_data in categories_data:
            # Create category
            category, created = RiskCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'color': cat_data['color'],
                    'care_inspectorate_theme': cat_data.get('care_inspectorate_theme', ''),
                    'his_domain': cat_data.get('his_domain', ''),
                }
            )
            
            # Create risks in this category
            for risk_data in cat_data.get('risks', []):
                risk_score = risk_data['likelihood'] * risk_data['impact']
                
                risk, created = RiskRegister.objects.get_or_create(
                    title=risk_data['title'],
                    care_home=care_home,
                    defaults={
                        'description': risk_data['description'],
                        'category': category,
                        'identified_by': admin_user,
                        'identified_date': date.today() - timedelta(days=30),
                        'status': 'ASSESSED',
                        
                        # Inherent risk (before controls)
                        'inherent_likelihood': risk_data['likelihood'],
                        'inherent_impact': risk_data['impact'],
                        'inherent_score': risk_score,
                        
                        # Residual risk (current)
                        'residual_likelihood': max(1, risk_data['likelihood'] - 1),
                        'residual_impact': risk_data['impact'],
                        'residual_score': max(1, risk_data['likelihood'] - 1) * risk_data['impact'],
                        
                        # Target risk
                        'target_likelihood': 1,
                        'target_impact': risk_data['impact'],
                        'target_score': risk_data['impact'],
                        
                        'priority': risk_data['priority'],
                        'risk_owner': admin_user,
                        'next_review_date': date.today() + timedelta(days=90),
                    }
                )
                
                if created:
                    risk_count += 1
                    
                    # Create a mitigation action
                    RiskMitigation.objects.create(
                        risk=risk,
                        action_description=f'Implement enhanced controls for {risk.title.lower()}',
                        responsible_person=admin_user,
                        target_completion_date=date.today() + timedelta(days=60),
                        status='IN_PROGRESS',
                        created_by=admin_user
                    )
                    
                    self.stdout.write(self.style.SUCCESS(f'Created risk: {risk.title}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nCreated {risk_count} risks across {len(categories_data)} categories'))
        self.stdout.write(self.style.SUCCESS('Module 6 sample data populated successfully!'))
