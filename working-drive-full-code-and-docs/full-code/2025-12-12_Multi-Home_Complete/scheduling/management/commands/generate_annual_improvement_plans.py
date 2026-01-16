"""
Management command to generate annual service improvement plans using ML

Scheduled to run every April 1st via cron:
    0 2 1 4 * cd /path/to/project && python manage.py generate_annual_improvement_plans

Usage:
    python manage.py generate_annual_improvement_plans --all
    python manage.py generate_annual_improvement_plans --home "Orchard Grove"
    python manage.py generate_annual_improvement_plans --dry-run
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.db.models import Avg, Count, Q, Sum
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import json
import logging

from scheduling.models import Unit, Shift
from scheduling.models_audit import ComplianceCheck, ComplianceViolation, AuditReport
from scheduling.models_improvement import (
    CareInspectorateReport, ServiceImprovementPlan, ImprovementAction,
    ServiceImprovementAnalyzer
)
from staff_records.models import SicknessRecord

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate annual service improvement plans using ML and historical data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Generate plans for all homes',
        )
        parser.add_argument(
            '--home',
            type=str,
            help='Generate plan for specific home',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be generated without creating records',
        )
        parser.add_argument(
            '--period-months',
            type=int,
            default=12,
            help='Number of months of historical data to analyze (default: 12)',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('Annual Service Improvement Plan Generation'))
        self.stdout.write(self.style.SUCCESS(f"Date: {timezone.now().strftime('%d %B %Y')}"))
        self.stdout.write(self.style.SUCCESS('='*70))
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('\n🔍 DRY RUN MODE - No data will be saved\n'))
        
        # Determine which homes to process
        if options['all']:
            homes = Unit.objects.filter(is_care_home=True)
        elif options['home']:
            homes = Unit.objects.filter(name=options['home'], is_care_home=True)
            if not homes.exists():
                self.stdout.write(self.style.ERROR(f"Home '{options['home']}' not found"))
                return
        else:
            self.stdout.write(self.style.ERROR('Must specify --all or --home'))
            return
        
        period_months = options['period_months']
        
        # Process each home
        plans_created = 0
        actions_created = 0
        
        for home in homes:
            self.stdout.write(f"\n{'='*70}")
            self.stdout.write(self.style.SUCCESS(f"Processing: {home.name}"))
            self.stdout.write(f"{'='*70}\n")
            
            try:
                plan, num_actions = self.generate_plan_for_home(
                    home, 
                    period_months, 
                    dry_run=options['dry_run']
                )
                
                if plan:
                    plans_created += 1
                    actions_created += num_actions
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {home.name}: {str(e)}"))
                logger.exception(f"Error generating plan for {home.name}")
        
        # Create organizational plan
        if plans_created > 0 and not options['dry_run']:
            self.stdout.write(f"\n{'='*70}")
            self.stdout.write(self.style.SUCCESS("Generating Organizational Improvement Plan..."))
            org_plan = self.generate_organizational_plan()
            if org_plan:
                self.stdout.write(self.style.SUCCESS(f"✓ Created organizational plan: {org_plan.plan_title}"))
        
        # Summary
        self.stdout.write(f"\n{'='*70}")
        self.stdout.write(self.style.SUCCESS('GENERATION COMPLETE'))
        self.stdout.write(self.style.SUCCESS(f"Plans created: {plans_created}"))
        self.stdout.write(self.style.SUCCESS(f"Actions created: {actions_created}"))
        self.stdout.write(self.style.SUCCESS('='*70))
    
    def generate_plan_for_home(self, home, period_months, dry_run=False):
        """Generate improvement plan for a single home using ML analysis"""
        
        self.stdout.write(f"📊 Analyzing {period_months} months of historical data...\n")
        
        # Initialize ML analyzer
        analyzer = ServiceImprovementAnalyzer()
        
        # Perform analysis
        analysis = analyzer.analyze_home(home.id, period_months=period_months)
        
        # Display analysis results
        self.display_analysis_summary(analysis)
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\n⚠️  Dry run mode - skipping plan creation"))
            return None, len(analysis.get('actions', []))
        
        # Create improvement plan
        today = date.today()
        plan_start = date(today.year, 4, 1)  # April 1st
        plan_end = date(today.year + 1, 3, 31)  # March 31st next year
        
        # Get latest CI report
        latest_inspection = CareInspectorateReport.objects.filter(
            home=home
        ).order_by('-inspection_date').first()
        
        with transaction.atomic():
            # Create plan
            plan = ServiceImprovementPlan.objects.create(
                home=home,
                plan_title=f"{home.name} Annual Service Improvement Plan {today.year}/{today.year + 1}",
                plan_period_start=plan_start,
                plan_period_end=plan_end,
                auto_generated=True,
                status='ACTIVE',
                baseline_metrics=analysis['baseline_metrics'],
                current_metrics=analysis['current_metrics'],
                executive_summary=self.generate_executive_summary(home, analysis),
                inspection_report=latest_inspection,
            )
            
            self.stdout.write(self.style.SUCCESS(f"\n✓ Created plan: {plan.plan_title}"))
            
            # Create actions
            actions = analysis.get('actions', [])
            action_count = 0
            
            for idx, action_data in enumerate(actions, 1):
                action = ImprovementAction.objects.create(
                    improvement_plan=plan,
                    action_number=f"{home.name[:3].upper()}-{today.year}-{idx:03d}",
                    title=action_data['title'],
                    description=action_data['description'],
                    priority=action_data['priority'],
                    source=action_data['source'],
                    category=action_data['category'],
                    quality_theme=action_data.get('quality_theme'),
                    target_start_date=action_data.get('target_start_date', plan_start),
                    target_completion_date=action_data['target_completion_date'],
                    expected_outcome=action_data['expected_outcome'],
                    success_metrics=action_data.get('success_metrics', []),
                    status='NOT_STARTED',
                )
                
                action_count += 1
                
                priority_icon = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠',
                    'MEDIUM': '🟡',
                    'LOW': '🟢',
                }.get(action_data['priority'], '⚪')
                
                self.stdout.write(
                    f"  {priority_icon} {action.action_number}: {action.title[:60]}..."
                )
            
            self.stdout.write(self.style.SUCCESS(f"\n✓ Created {action_count} improvement actions"))
        
        return plan, action_count
    
    def display_analysis_summary(self, analysis):
        """Display analysis results in a readable format"""
        
        # Overall score
        score = analysis.get('overall_score', 0)
        score_color = self.style.SUCCESS if score >= 80 else (
            self.style.WARNING if score >= 60 else self.style.ERROR
        )
        
        self.stdout.write(score_color(f"Overall Quality Score: {score}/100"))
        
        # Metrics comparison
        baseline = analysis.get('baseline_metrics', {})
        current = analysis.get('current_metrics', {})
        
        self.stdout.write("\n📈 Key Metrics:")
        
        metrics_to_show = [
            ('staffing.agency_usage_rate', 'Agency Usage', '%', 'lower'),
            ('staffing.turnover_rate', 'Staff Turnover', '%', 'lower'),
            ('compliance.training_compliance', 'Training Compliance', '%', 'higher'),
            ('compliance.wtd_violations', 'WTD Violations', '', 'lower'),
        ]
        
        for metric_path, label, unit, direction in metrics_to_show:
            baseline_val = self._get_nested_value(baseline, metric_path)
            current_val = self._get_nested_value(current, metric_path)
            
            if baseline_val is not None and current_val is not None:
                diff = current_val - baseline_val
                trend = '↑' if diff > 0 else ('↓' if diff < 0 else '→')
                
                # Determine if change is good
                is_good = (diff > 0 and direction == 'higher') or (diff < 0 and direction == 'lower')
                style_fn = self.style.SUCCESS if is_good else (
                    self.style.ERROR if not is_good and abs(diff) > 0 else self.style.WARNING
                )
                
                self.stdout.write(
                    f"  • {label}: {current_val:.1f}{unit} {trend} "
                    f"(was {baseline_val:.1f}{unit})"
                )
        
        # Action summary
        actions = analysis.get('actions', [])
        if actions:
            self.stdout.write(f"\n🎯 Recommended Actions: {len(actions)}")
            
            by_priority = {}
            for action in actions:
                priority = action['priority']
                by_priority[priority] = by_priority.get(priority, 0) + 1
            
            priority_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
            for priority in priority_order:
                if priority in by_priority:
                    icon = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}[priority]
                    self.stdout.write(f"  {icon} {priority}: {by_priority[priority]}")
        
        # Strengths
        strengths = analysis.get('strengths', [])
        if strengths:
            self.stdout.write("\n✅ Strengths:")
            for strength in strengths[:3]:
                self.stdout.write(f"  • {strength}")
        
        # Critical issues
        critical = analysis.get('critical_issues', [])
        if critical:
            self.stdout.write(self.style.ERROR("\n⚠️  Critical Issues:"))
            for issue in critical:
                self.stdout.write(self.style.ERROR(f"  • {issue}"))
    
    def _get_nested_value(self, data, path):
        """Get value from nested dict using dot notation"""
        keys = path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
    
    def generate_executive_summary(self, home, analysis):
        """Generate executive summary text"""
        
        score = analysis.get('overall_score', 0)
        
        summary = f"""
# {home.name} Service Improvement Plan - Executive Summary

## Overall Performance
Quality Score: {score}/100

## Analysis Period
{analysis.get('period_description', 'Past 12 months')}

## Key Findings

### Strengths
"""
        for strength in analysis.get('strengths', [])[:5]:
            summary += f"- {strength}\n"
        
        summary += "\n### Areas for Improvement\n"
        
        for issue in analysis.get('critical_issues', []):
            summary += f"- {issue}\n"
        
        summary += f"""
## Improvement Actions
Total Actions: {len(analysis.get('actions', []))}
- Critical Priority: {len([a for a in analysis.get('actions', []) if a['priority'] == 'CRITICAL'])}
- High Priority: {len([a for a in analysis.get('actions', []) if a['priority'] == 'HIGH'])}
- Medium Priority: {len([a for a in analysis.get('actions', []) if a['priority'] == 'MEDIUM'])}
- Low Priority: {len([a for a in analysis.get('actions', []) if a['priority'] == 'LOW'])}

## Expected Outcomes
Implementation of this plan is expected to:
"""
        
        # Add outcome predictions based on ML
        outcomes = analysis.get('predicted_outcomes', [])
        for outcome in outcomes:
            summary += f"- {outcome}\n"
        
        return summary.strip()
    
    def generate_organizational_plan(self):
        """Generate aggregated organizational improvement plan"""
        
        from scheduling.models_improvement import OrganizationalImprovementPlan
        
        today = date.today()
        plan_start = date(today.year, 4, 1)
        plan_end = date(today.year + 1, 3, 31)
        
        # Get all active home plans
        home_plans = ServiceImprovementPlan.objects.filter(
            status='ACTIVE',
            plan_period_start=plan_start
        )
        
        if not home_plans.exists():
            return None
        
        # Aggregate data
        all_actions = ImprovementAction.objects.filter(
            improvement_plan__in=home_plans
        )
        
        # Identify cross-cutting themes
        priority_counts = all_actions.values('category').annotate(count=Count('id')).order_by('-count')
        organizational_priorities = [
            {'category': p['category'], 'action_count': p['count']}
            for p in priority_counts[:5]
        ]
        
        # Create organizational plan
        org_plan = OrganizationalImprovementPlan.objects.create(
            plan_title=f"Organizational Service Improvement Plan {today.year}/{today.year + 1}",
            plan_period_start=plan_start,
            plan_period_end=plan_end,
            status='ACTIVE',
            organizational_priorities=organizational_priorities,
            executive_summary=self.generate_org_summary(home_plans, all_actions),
        )
        
        # Link home plans
        org_plan.home_plans.set(home_plans)
        
        return org_plan
    
    def generate_org_summary(self, home_plans, actions):
        """Generate organizational summary"""
        
        total_actions = actions.count()
        critical_actions = actions.filter(priority='CRITICAL').count()
        
        summary = f"""
# Organizational Service Improvement Plan - Executive Summary

## Scope
- Number of Care Homes: {home_plans.count()}
- Total Improvement Actions: {total_actions}
- Critical Priority Actions: {critical_actions}

## Cross-Cutting Priorities
"""
        
        # Add priority categories
        priority_counts = actions.values('category').annotate(count=Count('id')).order_by('-count')[:5]
        for idx, priority in enumerate(priority_counts, 1):
            summary += f"{idx}. {priority['category']}: {priority['count']} actions\n"
        
        return summary.strip()
