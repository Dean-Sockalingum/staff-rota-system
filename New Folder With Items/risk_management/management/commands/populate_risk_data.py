"""
Populate Risk Management Sample Data

Django management command to populate comprehensive sample data for Scottish care home
risk management system.

Usage:
    python manage.py populate_risk_data [--clear]

Options:
    --clear: Delete existing risk data before populating
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from risk_management.models import (
    RiskCategory,
    RiskRegister,
    RiskMitigation,
    RiskReview,
    RiskTreatmentPlan
)
from scheduling.models import CareHome

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate risk management system with sample Scottish care home data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing risk data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing risk data...')
            RiskReview.objects.all().delete()
            RiskMitigation.objects.all().delete()
            RiskTreatmentPlan.objects.all().delete()
            RiskRegister.objects.all().delete()
            RiskCategory.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared'))

        self.stdout.write('Creating risk categories...')
        categories = self.create_categories()
        
        self.stdout.write('Creating sample risks...')
        risks = self.create_risks(categories)
        
        self.stdout.write('Creating mitigations...')
        self.create_mitigations(risks)
        
        self.stdout.write('Creating reviews...')
        self.create_reviews(risks)
        
        self.stdout.write('Creating treatment plans...')
        self.create_treatment_plans(risks)
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully populated risk management data:\n'
            f'  - {len(categories)} risk categories\n'
            f'  - {len(risks)} risks\n'
            f'  - Sample mitigations, reviews, and treatment plans'
        ))

    def create_categories(self):
        """Create hierarchical risk categories for Scottish care homes"""
        categories = []
        
        # Level 1: Top-level categories
        clinical = RiskCategory.objects.create(
            name='Clinical & Care Quality',
            description='Risks related to resident care and clinical practice',
            color='#dc3545',
            is_active=True,
            his_domain='Person-Centred Care',
            care_inspectorate_theme='Health and Wellbeing'
        )
        categories.append(clinical)
        
        operational = RiskCategory.objects.create(
            name='Operational',
            description='Day-to-day operational risks',
            color='#fd7e14',
            is_active=True
        )
        categories.append(operational)
        
        regulatory = RiskCategory.objects.create(
            name='Regulatory & Compliance',
            description='Compliance with Scottish care regulations',
            color='#ffc107',
            is_active=True,
            his_domain='Safe Care',
            care_inspectorate_theme='Leadership and Management'
        )
        categories.append(regulatory)
        
        financial = RiskCategory.objects.create(
            name='Financial',
            description='Financial and resource management risks',
            color='#28a745',
            is_active=True
        )
        categories.append(financial)
        
        reputational = RiskCategory.objects.create(
            name='Reputational',
            description='Risks affecting organization reputation',
            color='#6c757d',
            is_active=True
        )
        categories.append(reputational)
        
        # Level 2: Subcategories for Clinical
        medication = RiskCategory.objects.create(
            name='Medication Management',
            description='Medication administration and storage',
            parent=clinical,
            color='#dc3545',
            his_domain='Safe Care',
            care_inspectorate_theme='Health and Wellbeing'
        )
        categories.append(medication)
        
        infection = RiskCategory.objects.create(
            name='Infection Prevention & Control',
            description='IPC practices and procedures',
            parent=clinical,
            color='#dc3545',
            his_domain='Safe Care',
            care_inspectorate_theme='Health and Wellbeing'
        )
        categories.append(infection)
        
        falls = RiskCategory.objects.create(
            name='Falls Prevention',
            description='Resident falls and mobility',
            parent=clinical,
            color='#dc3545',
            his_domain='Safe Care'
        )
        categories.append(falls)
        
        nutrition = RiskCategory.objects.create(
            name='Nutrition & Hydration',
            description='Nutritional care and hydration',
            parent=clinical,
            color='#dc3545',
            his_domain='Person-Centred Care'
        )
        categories.append(nutrition)
        
        # Level 2: Subcategories for Operational
        staffing = RiskCategory.objects.create(
            name='Staffing & Workforce',
            description='Staff recruitment, retention, and competency',
            parent=operational,
            color='#fd7e14',
            care_inspectorate_theme='Staff and Volunteers'
        )
        categories.append(staffing)
        
        building = RiskCategory.objects.create(
            name='Building & Environment',
            description='Premises safety and maintenance',
            parent=operational,
            color='#fd7e14',
            care_inspectorate_theme='Setting'
        )
        categories.append(building)
        
        return categories

    def create_risks(self, categories):
        """Create sample risks across all categories"""
        risks = []
        
        # Get first care home and user
        care_home = CareHome.objects.first()
        user = User.objects.filter(is_staff=True).first()
        
        if not care_home or not user:
            self.stdout.write(self.style.WARNING(
                'No care homes or users found. Creating minimal sample data.'
            ))
            return risks
        
        # Medication risks
        medication_cat = RiskCategory.objects.get(name='Medication Management')
        
        risk1 = RiskRegister.objects.create(
            title='Medication Administration Errors',
            description='Risk of incorrect medication being administered to residents, '
                       'including wrong dose, wrong resident, or wrong time.',
            category=medication_cat,
            care_home=care_home,
            affected_area='All units - medication rounds',
            inherent_likelihood=4,
            inherent_impact=5,
            current_controls='Double-checking procedures, MAR charts, e-MAR system, '
                           'trained staff, regular audits',
            control_effectiveness=4,
            residual_likelihood=2,
            residual_impact=4,
            risk_owner=user,
            assigned_to=user,
            identified_by=user,
            identified_date=timezone.now().date() - timedelta(days=90),
            status='CONTROLLED',
            priority='HIGH',
            review_frequency='MONTHLY',
            next_review_date=timezone.now().date() + timedelta(days=15),
            last_reviewed=timezone.now().date() - timedelta(days=15),
            regulatory_requirement='The Care Inspectorate - Health and Wellbeing outcome. '
                                  'HIS medication safety standards.',
            notes='Regular medication audits show 98% compliance. Continue monthly monitoring.'
        )
        risks.append(risk1)
        
        # Infection control
        infection_cat = RiskCategory.objects.get(name='Infection Prevention & Control')
        
        risk2 = RiskRegister.objects.create(
            title='COVID-19 Outbreak',
            description='Risk of COVID-19 outbreak affecting residents and staff, '
                       'leading to serious illness and potential deaths.',
            category=infection_cat,
            care_home=care_home,
            affected_area='All areas',
            inherent_likelihood=4,
            inherent_impact=5,
            current_controls='Vaccination program, PPE supplies, IPC training, '
                           'visitor restrictions, testing protocols, isolation procedures',
            control_effectiveness=4,
            residual_likelihood=2,
            residual_impact=4,
            risk_owner=user,
            assigned_to=user,
            identified_by=user,
            identified_date=timezone.now().date() - timedelta(days=180),
            status='CONTROLLED',
            priority='CRITICAL',
            review_frequency='MONTHLY',
            next_review_date=timezone.now().date() + timedelta(days=10),
            last_reviewed=timezone.now().date() - timedelta(days=20),
            regulatory_requirement='HIS IPC standards, Scottish Government COVID-19 guidance',
            target_likelihood=1,
            target_impact=3
        )
        risks.append(risk2)
        
        # Falls prevention
        falls_cat = RiskCategory.objects.get(name='Falls Prevention')
        
        risk3 = RiskRegister.objects.create(
            title='Resident Falls',
            description='Risk of residents falling, resulting in injury (fractures, head trauma), '
                       'reduced mobility, and loss of confidence.',
            category=falls_cat,
            care_home=care_home,
            affected_area='All resident areas',
            inherent_likelihood=5,
            inherent_impact=4,
            current_controls='Falls risk assessments, walking aids, call bells, '
                           'bed/chair sensors, physiotherapy, staff training',
            control_effectiveness=3,
            residual_likelihood=3,
            residual_impact=3,
            risk_owner=user,
            assigned_to=user,
            identified_by=user,
            identified_date=timezone.now().date() - timedelta(days=120),
            status='MITIGATED',
            priority='MEDIUM',
            review_frequency='QUARTERLY',
            next_review_date=timezone.now().date() + timedelta(days=30),
            regulatory_requirement='Care Inspectorate - Health and Wellbeing',
            notes='Falls rate reduced by 15% over last quarter'
        )
        risks.append(risk3)
        
        # Staffing
        staffing_cat = RiskCategory.objects.get(name='Staffing & Workforce')
        
        risk4 = RiskRegister.objects.create(
            title='Staff Shortage - Qualified Nurses',
            description='Insufficient qualified nursing staff to meet resident needs, '
                       'leading to care quality issues and staff burnout.',
            category=staffing_cat,
            care_home=care_home,
            affected_area='Nursing units',
            inherent_likelihood=4,
            inherent_impact=4,
            current_controls='Agency staff contracts, recruitment campaigns, '
                           'retention bonuses, flexible working, training programs',
            control_effectiveness=3,
            residual_likelihood=3,
            residual_impact=4,
            risk_owner=user,
            assigned_to=user,
            identified_by=user,
            identified_date=timezone.now().date() - timedelta(days=60),
            status='TREATMENT',
            priority='HIGH',
            review_frequency='MONTHLY',
            next_review_date=timezone.now().date() + timedelta(days=20),
            regulatory_requirement='SSSC registration requirements, Care Inspectorate staffing standards',
            is_escalated=True
        )
        risks.append(risk4)
        
        # Regulatory compliance
        regulatory_cat = RiskCategory.objects.get(name='Regulatory & Compliance')
        
        risk5 = RiskRegister.objects.create(
            title='Care Inspectorate Grade Reduction',
            description='Risk of receiving lower grades in Care Inspectorate inspection, '
                       'affecting reputation and regulatory status.',
            category=regulatory_cat,
            care_home=care_home,
            affected_area='All services',
            inherent_likelihood=3,
            inherent_impact=5,
            current_controls='Quality assurance framework, regular audits, '
                           'staff supervision, policy reviews, mock inspections',
            control_effectiveness=4,
            residual_likelihood=2,
            residual_impact=4,
            risk_owner=user,
            assigned_to=user,
            identified_by=user,
            identified_date=timezone.now().date() - timedelta(days=150),
            status='ASSESSED',
            priority='HIGH',
            review_frequency='QUARTERLY',
            next_review_date=timezone.now().date() + timedelta(days=45),
            regulatory_requirement='Care Inspectorate - All Health and Social Care Standards'
        )
        risks.append(risk5)
        
        # Building safety
        building_cat = RiskCategory.objects.get(name='Building & Environment')
        
        risk6 = RiskRegister.objects.create(
            title='Fire Safety - Inadequate Evacuation Procedures',
            description='Risk of residents/staff unable to evacuate safely in event of fire '
                       'due to mobility issues and building layout.',
            category=building_cat,
            care_home=care_home,
            affected_area='All units, especially upper floors',
            inherent_likelihood=2,
            inherent_impact=5,
            current_controls='Fire detection system, sprinklers, PEEP (Personal Emergency '
                           'Evacuation Plans), fire drills, staff training, fire doors',
            control_effectiveness=5,
            residual_likelihood=1,
            residual_impact=4,
            risk_owner=user,
            assigned_to=user,
            identified_by=user,
            identified_date=timezone.now().date() - timedelta(days=200),
            status='CONTROLLED',
            priority='MEDIUM',
            review_frequency='BIANNUALLY',
            next_review_date=timezone.now().date() + timedelta(days=90),
            regulatory_requirement='Fire Safety (Scotland) Regulations, Care Inspectorate premises standards'
        )
        risks.append(risk6)
        
        # Nutrition
        nutrition_cat = RiskCategory.objects.get(name='Nutrition & Hydration')
        
        risk7 = RiskRegister.objects.create(
            title='Malnutrition and Dehydration',
            description='Risk of residents becoming malnourished or dehydrated due to '
                       'swallowing difficulties, cognitive impairment, or inadequate monitoring.',
            category=nutrition_cat,
            care_home=care_home,
            affected_area='Dining areas, all units',
            inherent_likelihood=3,
            inherent_impact=4,
            current_controls='MUST screening, food/fluid charts, dietitian input, '
                           'modified diets, assistance at mealtimes, fortified foods',
            control_effectiveness=4,
            residual_likelihood=2,
            residual_impact=3,
            risk_owner=user,
            assigned_to=user,
            identified_by=user,
            identified_date=timezone.now().date() - timedelta(days=100),
            status='MITIGATED',
            priority='MEDIUM',
            review_frequency='QUARTERLY',
            next_review_date=timezone.now().date() + timedelta(days=60),
            regulatory_requirement='Care Inspectorate - Health and Wellbeing'
        )
        risks.append(risk7)
        
        # Financial
        financial_cat = RiskCategory.objects.get(name='Financial')
        
        risk8 = RiskRegister.objects.create(
            title='Budget Overspend - Agency Staff Costs',
            description='Risk of significant budget overspend due to reliance on expensive '
                       'agency staff to cover vacancies and sickness.',
            category=financial_cat,
            care_home=care_home,
            affected_area='All departments',
            inherent_likelihood=4,
            inherent_impact=3,
            current_controls='Budget monitoring, agency cost tracking, recruitment drive, '
                           'retention initiatives, flexible contracts',
            control_effectiveness=3,
            residual_likelihood=3,
            residual_impact=3,
            risk_owner=user,
            assigned_to=user,
            identified_by=user,
            identified_date=timezone.now().date() - timedelta(days=75),
            status='TREATMENT',
            priority='MEDIUM',
            review_frequency='MONTHLY',
            next_review_date=timezone.now().date() + timedelta(days=25)
        )
        risks.append(risk8)
        
        return risks

    def create_mitigations(self, risks):
        """Create sample mitigation actions"""
        if not risks:
            return
        
        user = User.objects.filter(is_staff=True).first()
        
        # Medication error mitigations
        RiskMitigation.objects.create(
            risk=risks[0],
            action='Implement barcode scanning for medication',
            description='Install barcode scanning system to verify resident identity '
                       'and medication before administration',
            mitigation_type='REDUCE',
            expected_likelihood_reduction=1,
            expected_impact_reduction=1,
            status='IN_PROGRESS',
            priority='HIGH',
            assigned_to=user,
            created_by=user,
            start_date=timezone.now().date() - timedelta(days=30),
            target_completion_date=timezone.now().date() + timedelta(days=60),
            estimated_cost=15000.00,
            resources_required='Barcode scanners (x5), software license, staff training',
            regulatory_requirement=True
        )
        
        RiskMitigation.objects.create(
            risk=risks[0],
            action='Enhanced medication audit program',
            description='Increase medication audits from monthly to weekly, with immediate '
                       'feedback to staff',
            mitigation_type='REDUCE',
            expected_likelihood_reduction=1,
            expected_impact_reduction=0,
            status='COMPLETED',
            priority='MEDIUM',
            assigned_to=user,
            created_by=user,
            start_date=timezone.now().date() - timedelta(days=60),
            target_completion_date=timezone.now().date() - timedelta(days=10),
            completion_date=timezone.now().date() - timedelta(days=10),
            estimated_cost=500.00,
            actual_cost=450.00,
            effectiveness_rating=4,
            resources_required='Senior nurse time for audits'
        )
        
        # COVID-19 mitigations
        RiskMitigation.objects.create(
            risk=risks[1],
            action='Booster vaccination campaign',
            description='Organize booster vaccination program for all residents and staff',
            mitigation_type='REDUCE',
            expected_likelihood_reduction=2,
            expected_impact_reduction=2,
            status='COMPLETED',
            priority='CRITICAL',
            assigned_to=user,
            created_by=user,
            start_date=timezone.now().date() - timedelta(days=90),
            target_completion_date=timezone.now().date() - timedelta(days=30),
            completion_date=timezone.now().date() - timedelta(days=30),
            estimated_cost=0.00,
            actual_cost=0.00,
            effectiveness_rating=5,
            resources_required='NHS vaccination team, consent forms',
            regulatory_requirement=True
        )
        
        # Falls mitigations
        RiskMitigation.objects.create(
            risk=risks[2],
            action='Enhanced physiotherapy program',
            description='Increase physiotherapy sessions to improve resident strength and balance',
            mitigation_type='REDUCE',
            expected_likelihood_reduction=1,
            expected_impact_reduction=1,
            status='IN_PROGRESS',
            priority='MEDIUM',
            assigned_to=user,
            created_by=user,
            start_date=timezone.now().date() - timedelta(days=20),
            target_completion_date=timezone.now().date() + timedelta(days=150),
            estimated_cost=12000.00,
            resources_required='Part-time physiotherapist (20 hours/week), equipment'
        )
        
        # Staffing mitigations
        RiskMitigation.objects.create(
            risk=risks[3],
            action='Nursing recruitment campaign',
            description='Launch targeted recruitment campaign for registered nurses, '
                       'including social media, job fairs, and university partnerships',
            mitigation_type='REDUCE',
            expected_likelihood_reduction=2,
            expected_impact_reduction=1,
            status='IN_PROGRESS',
            priority='HIGH',
            assigned_to=user,
            created_by=user,
            start_date=timezone.now().date() - timedelta(days=15),
            target_completion_date=timezone.now().date() + timedelta(days=90),
            estimated_cost=8000.00,
            resources_required='Marketing materials, recruitment agency fees',
            regulatory_requirement=True
        )
        
        RiskMitigation.objects.create(
            risk=risks[3],
            action='Student nurse partnership program',
            description='Establish partnership with local university to offer student placements '
                       'and graduate positions',
            mitigation_type='REDUCE',
            expected_likelihood_reduction=1,
            expected_impact_reduction=1,
            status='PLANNED',
            priority='MEDIUM',
            assigned_to=user,
            created_by=user,
            start_date=timezone.now().date() + timedelta(days=30),
            target_completion_date=timezone.now().date() + timedelta(days=180),
            estimated_cost=5000.00,
            resources_required='Practice educator time, training materials'
        )

    def create_reviews(self, risks):
        """Create sample risk reviews"""
        if not risks:
            return
        
        user = User.objects.filter(is_staff=True).first()
        
        # Review for medication risk
        RiskReview.objects.create(
            risk=risks[0],
            review_date=timezone.now().date() - timedelta(days=15),
            reviewed_by=user,
            reassessed_likelihood=2,
            reassessed_impact=4,
            controls_effective=True,
            control_gaps='None identified. Barcode scanning project on track.',
            new_mitigations_required=False,
            recommended_actions='Continue with current controls and complete barcode '
                              'scanning implementation.',
            decision='CONTINUE',
            decision_rationale='Current controls working well. Medication audit shows 98% compliance. '
                             'Barcode scanning will further reduce risk.',
            next_review_date=timezone.now().date() + timedelta(days=15),
            follow_up_actions='Monitor barcode scanning implementation progress.',
            changes_in_environment='No significant changes.',
            notes='Positive audit results. Staff engagement with new procedures excellent.'
        )
        
        # Review for COVID-19 risk
        RiskReview.objects.create(
            risk=risks[1],
            review_date=timezone.now().date() - timedelta(days=20),
            reviewed_by=user,
            reassessed_likelihood=2,
            reassessed_impact=4,
            controls_effective=True,
            control_gaps='Booster uptake at 92% - target 95%.',
            new_mitigations_required=True,
            recommended_actions='Continue monitoring. Promote booster uptake among staff.',
            decision='CONTINUE',
            decision_rationale='Vaccination program effective. No recent cases. Controls appropriate.',
            next_review_date=timezone.now().date() + timedelta(days=10),
            follow_up_actions='Encourage remaining staff to receive booster.',
            changes_in_environment='New COVID variant identified - monitoring situation.',
            notes='Zero cases in last 60 days. Excellent IPC compliance.'
        )
        
        # Review for falls risk
        RiskReview.objects.create(
            risk=risks[2],
            review_date=timezone.now().date() - timedelta(days=45),
            reviewed_by=user,
            reassessed_likelihood=3,
            reassessed_impact=3,
            controls_effective=True,
            control_gaps='Some residents not using walking aids consistently.',
            new_mitigations_required=False,
            recommended_actions='Reinforce importance of walking aids. Continue physiotherapy program.',
            decision='CONTINUE',
            decision_rationale='Falls rate decreasing. Physiotherapy showing positive results.',
            next_review_date=timezone.now().date() + timedelta(days=30),
            follow_up_actions='Review walking aid compliance with care staff.',
            changes_in_environment='Two new high-risk residents admitted.',
            notes='Falls reduced by 15% this quarter.'
        )

    def create_treatment_plans(self, risks):
        """Create sample treatment plans for high-priority risks"""
        if not risks:
            return
        
        user = User.objects.filter(is_staff=True).first()
        
        # Treatment plan for staffing risk
        RiskTreatmentPlan.objects.create(
            risk=risks[3],  # Staffing shortage
            treatment_strategy='REDUCE',
            plan_owner=user,
            created_by=user,
            start_date=timezone.now().date() - timedelta(days=15),
            target_completion_date=timezone.now().date() + timedelta(days=180),
            estimated_budget=25000.00,
            actual_spend=8500.00,
            required_resources='HR time, recruitment budget, training facilities',
            success_criteria='Achieve 95% nursing vacancy fill rate within 6 months. '
                           'Reduce agency spend by 40%.',
            implementation_steps='1. Launch recruitment campaign\n'
                                '2. Establish university partnership\n'
                                '3. Implement retention bonuses\n'
                                '4. Review flexible working policies\n'
                                '5. Enhance training and development program',
            barriers='Competitive job market, national nurse shortage, salary constraints',
            plan_status='IN_PROGRESS',
            approval_status='APPROVED',
            approved_by=user,
            approval_date=timezone.now().date() - timedelta(days=20),
            progress_notes='Recruitment campaign launched. 3 interviews scheduled. '
                          'University partnership meeting next week.'
        )
        
        # Treatment plan for medication risk
        RiskTreatmentPlan.objects.create(
            risk=risks[0],  # Medication errors
            treatment_strategy='REDUCE',
            plan_owner=user,
            created_by=user,
            start_date=timezone.now().date() - timedelta(days=30),
            target_completion_date=timezone.now().date() + timedelta(days=60),
            estimated_budget=18000.00,
            actual_spend=15200.00,
            required_resources='Barcode scanners, IT support, training time',
            success_criteria='Zero medication errors for 3 consecutive months. '
                           '100% barcode scanning compliance.',
            implementation_steps='1. Install barcode scanning system\n'
                                '2. Train all nursing staff\n'
                                '3. Pilot in one unit\n'
                                '4. Roll out to all units\n'
                                '5. Monitor and audit',
            barriers='Staff resistance to technology, initial time investment, IT issues',
            plan_status='IN_PROGRESS',
            approval_status='APPROVED',
            approved_by=user,
            approval_date=timezone.now().date() - timedelta(days=40),
            progress_notes='System installed. Pilot phase successful in Unit A. '
                          'Rolling out to Units B and C next week.'
        )
