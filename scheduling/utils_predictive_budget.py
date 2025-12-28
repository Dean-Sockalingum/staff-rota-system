"""
Predictive Budget Management & ROI Calculator
==============================================

Strategic financial planning tools for care home operations.

Purpose:
- ROI calculator for hiring decisions
- Scenario planning ("What if sickness doubles?")
- Auto-budget allocation recommendations
- Predictive spend forecasting

Key Features:
1. Hiring ROI Analysis: Calculate payback period for new hires
2. Scenario Modeling: Test impact of various changes
3. Budget Allocation: Auto-recommend spend distribution
4. Cost-Benefit Analysis: Compare options (hire vs agency vs OT)
5. Trend Forecasting: Predict next quarter spend

ROI Target: £25,000/year
- Better strategic decisions
- Optimal resource allocation
- Avoid costly mistakes (e.g., over-hiring)
- Maximize cost-efficiency

Author: AI Assistant Enhancement Sprint
Date: December 2025
"""

from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import logging
import math

# Import models
from .models import Unit, Shift, User
from .budget_optimizer import BudgetOptimizer

logger = logging.getLogger(__name__)


class PredictiveBudgetManager:
    """
    Strategic budget planning and ROI analysis.
    
    Provides decision-support tools for financial planning
    and scenario modeling.
    """
    
    # Cost constants (per shift)
    COST_REGULAR_SHIFT = Decimal('120.00')
    COST_OT_SHIFT = Decimal('180.00')
    COST_AGENCY_SHIFT = Decimal('280.00')
    
    # Cost constants (annual per staff)
    COST_ANNUAL_SALARY_RN = Decimal('35000.00')
    COST_ANNUAL_SALARY_HCA = Decimal('22000.00')
    COST_RECRUITMENT = Decimal('3000.00')
    COST_TRAINING_INDUCTION = Decimal('1500.00')
    COST_TURNOVER = Decimal('5000.00')  # Total cost to replace one staff
    
    # Revenue constants
    REVENUE_PER_RESIDENT_WEEK = Decimal('800.00')
    
    def __init__(self, care_home: Unit):
        """
        Initialize budget manager.
        
        Args:
            care_home: Care home unit
        """
        self.care_home = care_home
    
    
    def calculate_hiring_roi(
        self,
        role_code: str,
        annual_salary: Decimal,
        expected_reduction_agency_shifts: int,
        expected_reduction_ot_shifts: int
    ) -> Dict:
        """
        Calculate ROI for hiring a new staff member.
        
        Args:
            role_code: Role to hire (RN, HCA, etc.)
            annual_salary: Annual salary cost
            expected_reduction_agency_shifts: Annual agency shifts saved
            expected_reduction_ot_shifts: Annual OT shifts saved
        
        Returns:
            dict: ROI analysis with payback period
        """
        logger.info(f"Calculating hiring ROI for {role_code} at {self.care_home.name}")
        
        # Total cost of hiring
        recruitment_cost = self.COST_RECRUITMENT
        training_cost = self.COST_TRAINING_INDUCTION
        first_year_salary = annual_salary
        
        total_cost_year_1 = recruitment_cost + training_cost + first_year_salary
        
        # Annual savings
        agency_savings = expected_reduction_agency_shifts * self.COST_AGENCY_SHIFT
        ot_savings = expected_reduction_ot_shifts * (self.COST_OT_SHIFT - self.COST_REGULAR_SHIFT)
        
        total_annual_savings = agency_savings + ot_savings
        
        # Calculate payback period
        if total_annual_savings > 0:
            payback_months = float(total_cost_year_1 / (total_annual_savings / 12))
        else:
            payback_months = 999  # Never pays back
        
        # ROI percentage
        roi_year_1 = ((total_annual_savings - total_cost_year_1) / total_cost_year_1) * 100
        
        # 3-year projection
        net_savings_3_years = (total_annual_savings * 3) - total_cost_year_1 - (annual_salary * 2)
        
        # Recommendation
        if payback_months <= 6:
            recommendation = "✅ HIGHLY RECOMMENDED - Payback in 6 months or less"
        elif payback_months <= 12:
            recommendation = "✅ RECOMMENDED - Payback within 1 year"
        elif payback_months <= 24:
            recommendation = "⚠️ CONSIDER - Payback 1-2 years"
        else:
            recommendation = "❌ NOT RECOMMENDED - Long payback period"
        
        return {
            'role': role_code,
            'annual_salary': annual_salary,
            'costs': {
                'recruitment': recruitment_cost,
                'training': training_cost,
                'year_1_total': total_cost_year_1
            },
            'savings': {
                'agency_shifts_saved': expected_reduction_agency_shifts,
                'agency_savings': agency_savings,
                'ot_shifts_saved': expected_reduction_ot_shifts,
                'ot_savings': ot_savings,
                'total_annual_savings': total_annual_savings
            },
            'roi': {
                'payback_months': round(payback_months, 1),
                'roi_year_1_pct': round(roi_year_1, 1),
                'net_savings_3_years': net_savings_3_years
            },
            'recommendation': recommendation
        }
    
    
    def scenario_analysis(
        self,
        scenario_name: str,
        changes: Dict
    ) -> Dict:
        """
        Model impact of hypothetical changes.
        
        Args:
            scenario_name: Description of scenario
            changes: Dict of changes to model:
                {
                    'sickness_multiplier': 2.0,  # Double sickness
                    'turnover_increase': 5,      # +5 leavers
                    'agency_rate_increase': 1.15 # +15% agency costs
                }
        
        Returns:
            dict: Scenario impact analysis
        """
        logger.info(f"Running scenario analysis: {scenario_name}")
        
        # Get baseline metrics (last 90 days)
        baseline = self._get_baseline_metrics()
        
        # Apply changes
        scenario_metrics = baseline.copy()
        
        # Sickness multiplier
        if 'sickness_multiplier' in changes:
            mult = changes['sickness_multiplier']
            scenario_metrics['sickness_shifts'] = int(baseline['sickness_shifts'] * mult)
            scenario_metrics['agency_shifts'] += int(baseline['sickness_shifts'] * (mult - 1))
        
        # Turnover increase
        if 'turnover_increase' in changes:
            additional_leavers = changes['turnover_increase']
            scenario_metrics['turnover_cost'] = baseline['turnover_cost'] + (
                self.COST_TURNOVER * additional_leavers
            )
        
        # Agency rate increase
        if 'agency_rate_increase' in changes:
            mult = changes['agency_rate_increase']
            scenario_metrics['agency_cost'] = baseline['agency_cost'] * mult
        
        # Overtime increase
        if 'overtime_multiplier' in changes:
            mult = changes['overtime_multiplier']
            scenario_metrics['ot_shifts'] = int(baseline['ot_shifts'] * mult)
            scenario_metrics['ot_cost'] = baseline['ot_cost'] * mult
        
        # Calculate impact
        baseline_total_cost = (
            baseline['regular_cost'] +
            baseline['ot_cost'] +
            baseline['agency_cost'] +
            baseline['turnover_cost']
        )
        
        scenario_total_cost = (
            scenario_metrics['regular_cost'] +
            scenario_metrics['ot_cost'] +
            scenario_metrics['agency_cost'] +
            scenario_metrics['turnover_cost']
        )
        
        cost_impact = scenario_total_cost - baseline_total_cost
        pct_impact = ((cost_impact / baseline_total_cost) * 100) if baseline_total_cost > 0 else 0
        
        # Annual projection
        annual_cost_impact = cost_impact * 4  # 90 days → 365 days
        
        return {
            'scenario_name': scenario_name,
            'changes': changes,
            'baseline': baseline,
            'scenario': scenario_metrics,
            'impact': {
                'cost_increase_90_days': cost_impact,
                'cost_increase_annual': annual_cost_impact,
                'percentage_increase': round(pct_impact, 1)
            },
            'recommendations': self._generate_scenario_recommendations(
                scenario_name, cost_impact, annual_cost_impact
            )
        }
    
    
    def _get_baseline_metrics(self) -> Dict:
        """
        Get baseline operational metrics (last 90 days).
        
        Returns:
            dict: Baseline metrics
        """
        cutoff = timezone.now() - timedelta(days=90)
        
        # Count shifts by type
        regular_shifts = Shift.objects.filter(
            unit=self.care_home,
            date__gte=cutoff,
            shift_classification='REGULAR'
        ).count()
        
        ot_shifts = Shift.objects.filter(
            unit=self.care_home,
            date__gte=cutoff,
            shift_classification='OT'
        ).count()
        
        agency_shifts = Shift.objects.filter(
            unit=self.care_home,
            date__gte=cutoff,
            shift_classification='AGENCY'
        ).count()
        
        # Calculate costs
        regular_cost = regular_shifts * self.COST_REGULAR_SHIFT
        ot_cost = ot_shifts * self.COST_OT_SHIFT
        agency_cost = agency_shifts * self.COST_AGENCY_SHIFT
        
        # Turnover (last 90 days)
        leavers = User.objects.filter(
            profile__units=self.care_home,
            profile__leaving_date__gte=cutoff,
            profile__leaving_date__isnull=False
        ).count()
        
        turnover_cost = leavers * self.COST_TURNOVER
        
        # Sickness (estimate from agency usage)
        sickness_shifts = int(agency_shifts * 0.4)  # Assume 40% agency is sickness
        
        return {
            'regular_shifts': regular_shifts,
            'regular_cost': regular_cost,
            'ot_shifts': ot_shifts,
            'ot_cost': ot_cost,
            'agency_shifts': agency_shifts,
            'agency_cost': agency_cost,
            'sickness_shifts': sickness_shifts,
            'turnover_leavers': leavers,
            'turnover_cost': turnover_cost
        }
    
    
    def _generate_scenario_recommendations(
        self,
        scenario_name: str,
        cost_impact: Decimal,
        annual_impact: Decimal
    ) -> List[str]:
        """
        Generate recommendations for scenario.
        
        Args:
            scenario_name: Scenario name
            cost_impact: 90-day cost impact
            annual_impact: Annual cost impact
        
        Returns:
            list: Recommendations
        """
        recommendations = []
        
        if annual_impact > 50000:
            recommendations.append(
                f"❗ CRITICAL: {scenario_name} would cost an additional £{annual_impact:,.0f}/year. "
                "Immediate mitigation required."
            )
        elif annual_impact > 20000:
            recommendations.append(
                f"⚠️ HIGH IMPACT: {scenario_name} would cost £{annual_impact:,.0f}/year. "
                "Develop contingency plan."
            )
        elif annual_impact > 5000:
            recommendations.append(
                f"⚠️ MODERATE IMPACT: {scenario_name} would cost £{annual_impact:,.0f}/year. "
                "Monitor closely."
            )
        else:
            recommendations.append(
                f"✅ LOW IMPACT: {scenario_name} would cost £{annual_impact:,.0f}/year. "
                "Within acceptable range."
            )
        
        # Specific mitigations
        if 'sickness' in scenario_name.lower():
            recommendations.append(
                "Mitigations: (1) Enhance retention to build resilience, "
                "(2) Proactive OT outreach, (3) Consider additional permanent hires."
            )
        
        if 'turnover' in scenario_name.lower():
            recommendations.append(
                "Mitigations: (1) Use Retention Predictor to identify at-risk staff, "
                "(2) Improve working conditions, (3) Review compensation."
            )
        
        if 'agency' in scenario_name.lower():
            recommendations.append(
                "Mitigations: (1) Negotiate better agency rates, "
                "(2) Increase OT pool, (3) Hire permanent staff to reduce dependency."
            )
        
        return recommendations
    
    
    def recommend_budget_allocation(
        self,
        total_monthly_budget: Decimal
    ) -> Dict:
        """
        Recommend optimal budget allocation.
        
        Args:
            total_monthly_budget: Total monthly staffing budget
        
        Returns:
            dict: Recommended allocation
        """
        logger.info(f"Calculating budget allocation for £{total_monthly_budget:,.0f}")
        
        # Get historical data
        baseline = self._get_baseline_metrics()
        
        # Calculate current monthly burn rate (90 days → 30 days)
        current_monthly_spend = (
            baseline['regular_cost'] +
            baseline['ot_cost'] +
            baseline['agency_cost']
        ) / 3
        
        # Recommended allocation strategy:
        # 1. Permanent staff: 70-75%
        # 2. OT buffer: 15-20%
        # 3. Agency emergency: 5-10%
        
        permanent_allocation = total_monthly_budget * Decimal('0.72')
        ot_allocation = total_monthly_budget * Decimal('0.18')
        agency_allocation = total_monthly_budget * Decimal('0.10')
        
        # Calculate capacity
        permanent_shifts = int(permanent_allocation / self.COST_REGULAR_SHIFT)
        ot_shifts = int(ot_allocation / self.COST_OT_SHIFT)
        agency_shifts = int(agency_allocation / self.COST_AGENCY_SHIFT)
        
        return {
            'total_budget': total_monthly_budget,
            'current_monthly_spend': current_monthly_spend,
            'variance': total_monthly_budget - current_monthly_spend,
            'allocation': {
                'permanent': {
                    'budget': permanent_allocation,
                    'percentage': 72,
                    'shifts_capacity': permanent_shifts
                },
                'overtime': {
                    'budget': ot_allocation,
                    'percentage': 18,
                    'shifts_capacity': ot_shifts
                },
                'agency': {
                    'budget': agency_allocation,
                    'percentage': 10,
                    'shifts_capacity': agency_shifts
                }
            },
            'recommendations': [
                "✅ Maintain 72% permanent staff for stability",
                "✅ Keep 18% OT buffer for flexibility",
                "⚠️ Limit agency to 10% for emergencies only",
                "💡 If consistently exceeding agency allocation, consider hiring"
            ]
        }
    
    
    def compare_options(
        self,
        option_a: Dict,
        option_b: Dict
    ) -> Dict:
        """
        Compare two operational options.
        
        Args:
            option_a: First option dict with costs/benefits
            option_b: Second option dict with costs/benefits
        
        Returns:
            dict: Comparison analysis
        """
        # Calculate total cost and benefit for each
        cost_a = option_a.get('upfront_cost', Decimal('0')) + option_a.get('annual_cost', Decimal('0'))
        benefit_a = option_a.get('annual_benefit', Decimal('0'))
        net_a = benefit_a - cost_a
        
        cost_b = option_b.get('upfront_cost', Decimal('0')) + option_b.get('annual_cost', Decimal('0'))
        benefit_b = option_b.get('annual_benefit', Decimal('0'))
        net_b = benefit_b - cost_b
        
        # Determine winner
        if net_a > net_b:
            winner = 'Option A'
            advantage = net_a - net_b
        elif net_b > net_a:
            winner = 'Option B'
            advantage = net_b - net_a
        else:
            winner = 'Equal'
            advantage = Decimal('0')
        
        return {
            'option_a': {
                'name': option_a.get('name', 'Option A'),
                'total_cost': cost_a,
                'total_benefit': benefit_a,
                'net_value': net_a
            },
            'option_b': {
                'name': option_b.get('name', 'Option B'),
                'total_cost': cost_b,
                'total_benefit': benefit_b,
                'net_value': net_b
            },
            'winner': winner,
            'advantage': advantage,
            'recommendation': f"✅ Choose {winner} - £{advantage:,.0f} better value"
        }
    
    
    def forecast_next_quarter(self) -> Dict:
        """
        Forecast spend for next quarter based on trends.
        
        Returns:
            dict: Quarterly forecast
        """
        logger.info(f"Forecasting Q{(date.today().month-1)//3 + 2} spend for {self.care_home.name}")
        
        # Get last 3 months data
        baseline = self._get_baseline_metrics()
        
        # Simple linear projection (in production, use more sophisticated model)
        monthly_avg_spend = (
            baseline['regular_cost'] +
            baseline['ot_cost'] +
            baseline['agency_cost']
        ) / 3
        
        # Apply trend adjustment (assume 2% month-over-month growth)
        growth_rate = Decimal('1.02')
        
        month_1_forecast = monthly_avg_spend * growth_rate
        month_2_forecast = month_1_forecast * growth_rate
        month_3_forecast = month_2_forecast * growth_rate
        
        quarter_total = month_1_forecast + month_2_forecast + month_3_forecast
        
        return {
            'quarter': f"Q{(date.today().month-1)//3 + 2} {date.today().year}",
            'current_monthly_avg': monthly_avg_spend,
            'forecast': {
                'month_1': month_1_forecast,
                'month_2': month_2_forecast,
                'month_3': month_3_forecast,
                'quarter_total': quarter_total
            },
            'assumptions': [
                "Based on last 90 days historical data",
                "Assumes 2% month-over-month growth",
                "Does not account for extraordinary events"
            ],
            'confidence': 'Medium'
        }


def run_quarterly_budget_review(care_home: Unit):
    """
    Comprehensive quarterly budget review.
    
    Args:
        care_home: Care home to review
    
    Returns:
        dict: Full review
    """
    manager = PredictiveBudgetManager(care_home)
    
    # Forecast next quarter
    forecast = manager.forecast_next_quarter()
    
    # Scenario analysis
    worst_case = manager.scenario_analysis(
        "Worst Case: Double sickness + 5 more leavers",
        {
            'sickness_multiplier': 2.0,
            'turnover_increase': 5
        }
    )
    
    # Budget allocation recommendation
    allocation = manager.recommend_budget_allocation(
        total_monthly_budget=Decimal('85000.00')  # Example budget
    )
    
    return {
        'care_home': care_home.name,
        'forecast': forecast,
        'worst_case_scenario': worst_case,
        'budget_allocation': allocation,
        'review_date': date.today()
    }
