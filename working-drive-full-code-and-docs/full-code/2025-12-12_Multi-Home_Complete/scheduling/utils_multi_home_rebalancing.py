"""
Multi-Home Staff Rebalancing AI
================================

Intelligent cross-home staff allocation system for optimal resource utilization.

Purpose:
- Identify surplus staff at one home who could cover shortages at another
- Suggest travel bonuses and temporary assignments
- Reduce agency costs by maximizing existing workforce
- Maintain fairness and staff preferences

Key Features:
1. Real-time surplus/shortage detection across all homes
2. Travel distance calculation and willingness matching
3. Auto-suggest rebalancing with financial incentives
4. Fair rotation (don't overuse same staff for travel)
5. Skills matching (SSCW surplus → SSCW shortage only)

Rebalancing Logic:
- Identify homes with predicted surpluses (>10% overstaffed)
- Identify homes with predicted shortages (<95% coverage)
- Match by role, distance (<15 miles preferred), and staff willingness
- Suggest travel bonus (£30-50 depending on distance)
- Prefer permanent solutions over repeated temporary moves

ROI Target: £35,000/year
- Reduce agency usage by 20%
- Better resource utilization across portfolio
- Cost: £50 travel bonus vs £280 agency shift

Author: AI Assistant Enhancement Sprint
Date: December 2025
"""

from django.db.models import Count, Q, F, Avg
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import logging
import math

# Import models
from .models import Unit, Shift, User, ShiftType
from .shortage_predictor import ShortagePredictor

logger = logging.getLogger(__name__)


class MultiHomeRebalancingAI:
    """
    Cross-home staff allocation optimizer.
    
    Identifies opportunities to move surplus staff from one home
    to cover shortages at another, with financial incentives.
    """
    
    # Configuration
    MAX_TRAVEL_DISTANCE_MILES = 15  # Maximum reasonable travel distance
    TRAVEL_BONUS_NEAR = Decimal('30.00')    # <5 miles
    TRAVEL_BONUS_MEDIUM = Decimal('40.00')  # 5-10 miles
    TRAVEL_BONUS_FAR = Decimal('50.00')     # 10-15 miles
    
    SURPLUS_THRESHOLD = 1.10  # 10% overstaffed
    SHORTAGE_THRESHOLD = 0.95 # 5% understaffed
    
    MAX_TRAVEL_SHIFTS_PER_MONTH = 4  # Don't overuse same staff
    
    def __init__(self, organization_name: str = "Glasgow HSCP"):
        """
        Initialize rebalancing AI for organization.
        
        Args:
            organization_name: Name of care home group
        """
        self.organization_name = organization_name
    
    
    def analyze_all_homes(self, forecast_days: int = 14) -> Dict:
        """
        Analyze all homes to find rebalancing opportunities.
        
        Args:
            forecast_days: Days ahead to forecast
        
        Returns:
            dict: {
                'surplus_homes': list,
                'shortage_homes': list,
                'rebalancing_opportunities': list,
                'potential_savings': Decimal
            }
        """
        logger.info(f"Analyzing rebalancing opportunities for next {forecast_days} days")
        
        # Get all active care homes
        homes = Unit.objects.filter(is_active=True)
        
        surplus_homes = []
        shortage_homes = []
        
        # Analyze each home
        for home in homes:
            analysis = self._analyze_single_home(home, forecast_days)
            
            if analysis['status'] == 'surplus':
                surplus_homes.append(analysis)
            elif analysis['status'] == 'shortage':
                shortage_homes.append(analysis)
        
        # Find rebalancing opportunities
        opportunities = self._find_rebalancing_matches(surplus_homes, shortage_homes)
        
        # Calculate potential savings
        total_savings = sum(opp['savings'] for opp in opportunities)
        
        return {
            'surplus_homes': surplus_homes,
            'shortage_homes': shortage_homes,
            'rebalancing_opportunities': opportunities,
            'potential_savings': total_savings,
            'analysis_period_days': forecast_days,
            'timestamp': timezone.now()
        }
    
    
    def _analyze_single_home(self, home: Unit, forecast_days: int) -> Dict:
        """
        Analyze staffing levels for a single home.
        
        Args:
            home: Unit instance
            forecast_days: Days to analyze
        
        Returns:
            dict: Home analysis with surplus/shortage/balanced status
        """
        from datetime import date
        
        # Get forecast using existing predictor
        predictor = ShortagePredictor(home)
        
        # Analyze next forecast_days
        total_required = 0
        total_scheduled = 0
        shortages_by_role = {}
        surpluses_by_role = {}
        
        for day_offset in range(forecast_days):
            check_date = date.today() + timedelta(days=day_offset)
            
            # Get required shifts for this day
            shift_types = ShiftType.objects.all()
            for shift_type in shift_types:
                required = self._get_required_staff(home, check_date, shift_type)
                scheduled = self._get_scheduled_staff(home, check_date, shift_type)
                
                total_required += required
                total_scheduled += scheduled
                
                diff = scheduled - required
                
                if diff < 0:
                    # Shortage
                    role = shift_type.role.code
                    shortages_by_role[role] = shortages_by_role.get(role, 0) + abs(diff)
                elif diff > 0:
                    # Surplus
                    role = shift_type.role.code
                    surpluses_by_role[role] = surpluses_by_role.get(role, 0) + diff
        
        # Determine status
        if total_required == 0:
            coverage_ratio = 1.0
        else:
            coverage_ratio = total_scheduled / total_required
        
        if coverage_ratio >= self.SURPLUS_THRESHOLD:
            status = 'surplus'
        elif coverage_ratio <= self.SHORTAGE_THRESHOLD:
            status = 'shortage'
        else:
            status = 'balanced'
        
        return {
            'home': home,
            'home_name': home.name,
            'status': status,
            'coverage_ratio': coverage_ratio,
            'total_required': total_required,
            'total_scheduled': total_scheduled,
            'surpluses_by_role': surpluses_by_role,
            'shortages_by_role': shortages_by_role,
            'location': getattr(home, 'address', 'Unknown')
        }
    
    
    def _get_required_staff(self, home: Unit, date: date, shift_type: ShiftType) -> int:
        """
        Get required staff count (simplified - use business rules or forecast).
        
        Args:
            home: Unit
            date: Date to check
            shift_type: Shift type
        
        Returns:
            int: Required staff count
        """
        # Simplified: Use standard staffing levels
        # In production, this would use forecast demand
        
        role_code = shift_type.role.code
        is_day = shift_type.shift_type == 'DAY'
        
        # Standard staffing matrix (example)
        standards = {
            'RN': 2 if is_day else 1,
            'SSW': 3 if is_day else 0,
            'SCW': 4 if is_day else 0,
            'SCWN': 0 if is_day else 2,
            'SCA': 2 if is_day else 0,
            'SCAN': 0 if is_day else 1
        }
        
        return standards.get(role_code, 1)
    
    
    def _get_scheduled_staff(self, home: Unit, date: date, shift_type: ShiftType) -> int:
        """
        Get currently scheduled staff count.
        
        Args:
            home: Unit
            date: Date to check
            shift_type: Shift type
        
        Returns:
            int: Scheduled staff count
        """
        return Shift.objects.filter(
            unit=home,
            date=date,
            shift_type=shift_type,
            assigned_to__isnull=False
        ).count()
    
    
    def _find_rebalancing_matches(
        self, 
        surplus_homes: List[Dict], 
        shortage_homes: List[Dict]
    ) -> List[Dict]:
        """
        Match surplus staff with shortage opportunities.
        
        Args:
            surplus_homes: List of homes with surplus
            shortage_homes: List of homes with shortages
        
        Returns:
            list: Rebalancing opportunities
        """
        opportunities = []
        
        # For each shortage...
        for shortage_home in shortage_homes:
            for role, shortage_count in shortage_home['shortages_by_role'].items():
                
                # Find surplus homes with this role
                for surplus_home in surplus_homes:
                    if role not in surplus_home['surpluses_by_role']:
                        continue
                    
                    surplus_count = surplus_home['surpluses_by_role'][role]
                    
                    # Calculate distance
                    distance = self._calculate_distance(
                        surplus_home['home'],
                        shortage_home['home']
                    )
                    
                    # Skip if too far
                    if distance > self.MAX_TRAVEL_DISTANCE_MILES:
                        continue
                    
                    # Find available staff
                    available_staff = self._get_available_staff_for_travel(
                        surplus_home['home'],
                        role,
                        min(surplus_count, shortage_count)
                    )
                    
                    if not available_staff:
                        continue
                    
                    # Calculate incentive
                    travel_bonus = self._calculate_travel_bonus(distance)
                    
                    # Calculate savings (travel bonus vs agency)
                    agency_cost = Decimal('280.00')  # Per shift
                    cost_with_travel = Decimal('120.00') + travel_bonus  # Regular + bonus
                    savings_per_shift = agency_cost - cost_with_travel
                    
                    shifts_to_cover = min(len(available_staff), shortage_count)
                    total_savings = savings_per_shift * shifts_to_cover
                    
                    # Create opportunity
                    opportunity = {
                        'from_home': surplus_home['home_name'],
                        'to_home': shortage_home['home_name'],
                        'role': role,
                        'staff_available': len(available_staff),
                        'shifts_to_cover': shifts_to_cover,
                        'distance_miles': distance,
                        'travel_bonus': travel_bonus,
                        'savings_per_shift': savings_per_shift,
                        'savings': total_savings,
                        'available_staff_names': [s.get_full_name() for s in available_staff[:5]],
                        'recommendation': self._generate_recommendation(
                            surplus_home['home_name'],
                            shortage_home['home_name'],
                            role,
                            shifts_to_cover,
                            distance,
                            travel_bonus
                        )
                    }
                    
                    opportunities.append(opportunity)
        
        # Sort by savings (highest first)
        opportunities.sort(key=lambda x: x['savings'], reverse=True)
        
        return opportunities
    
    
    def _calculate_distance(self, home1: Unit, home2: Unit) -> float:
        """
        Calculate distance between two homes.
        
        In production, this would use real addresses and geocoding.
        For now, returns simplified estimate.
        
        Args:
            home1: First home
            home2: Second home
        
        Returns:
            float: Distance in miles
        """
        # Simplified: Random distance for demo
        # In production, use Google Maps API or similar
        
        # For demo, use hash of home names to get consistent "distance"
        hash_value = hash(f"{home1.name}{home2.name}") % 150
        distance = float(hash_value) / 10  # 0-15 miles
        
        return round(distance, 1)
    
    
    def _calculate_travel_bonus(self, distance: float) -> Decimal:
        """
        Calculate travel bonus based on distance.
        
        Args:
            distance: Distance in miles
        
        Returns:
            Decimal: Bonus amount
        """
        if distance < 5:
            return self.TRAVEL_BONUS_NEAR
        elif distance < 10:
            return self.TRAVEL_BONUS_MEDIUM
        else:
            return self.TRAVEL_BONUS_FAR
    
    
    def _get_available_staff_for_travel(
        self, 
        home: Unit, 
        role: str, 
        max_count: int
    ) -> List[User]:
        """
        Get staff willing and able to travel.
        
        Args:
            home: Home with surplus
            role: Role code
            max_count: Maximum staff needed
        
        Returns:
            list: Available User instances
        """
        # Get staff from this home with this role
        staff = User.objects.filter(
            profile__units=home,
            profile__role__code=role,
            is_active=True
        )
        
        # Filter by willingness to travel (if tracked)
        # For now, exclude staff who've traveled too much this month
        
        cutoff_date = timezone.now() - timedelta(days=30)
        
        available = []
        for person in staff:
            # Count travel shifts this month
            travel_shifts = Shift.objects.filter(
                assigned_to=person,
                date__gte=cutoff_date,
                shift_classification='TRAVEL'
            ).count()
            
            if travel_shifts < self.MAX_TRAVEL_SHIFTS_PER_MONTH:
                available.append(person)
            
            if len(available) >= max_count:
                break
        
        return available
    
    
    def _generate_recommendation(
        self,
        from_home: str,
        to_home: str,
        role: str,
        shift_count: int,
        distance: float,
        bonus: Decimal
    ) -> str:
        """
        Generate human-readable recommendation.
        
        Args:
            from_home: Source home name
            to_home: Destination home name
            role: Role code
            shift_count: Number of shifts
            distance: Distance in miles
            bonus: Travel bonus amount
        
        Returns:
            str: Recommendation text
        """
        role_names = {
            'RN': 'Registered Nurse',
            'SSW': 'Senior Support Worker',
            'SCW': 'Support Care Worker',
            'SCWN': 'Night Support Care Worker',
            'SCA': 'Care Assistant',
            'SCAN': 'Night Care Assistant'
        }
        
        role_name = role_names.get(role, role)
        
        return (
            f"💡 Move {shift_count} {role_name} shifts from {from_home} to {to_home}. "
            f"Distance: {distance} miles. Offer £{bonus} travel bonus. "
            f"Savings: £{(Decimal('280') - Decimal('120') - bonus) * shift_count:.0f} vs agency."
        )
    
    
    def send_rebalancing_suggestions(self, analysis: Dict) -> bool:
        """
        Email rebalancing suggestions to managers.
        
        Args:
            analysis: Dict from analyze_all_homes()
        
        Returns:
            bool: True if sent successfully
        """
        from django.core.mail import send_mail
        from django.conf import settings
        
        opportunities = analysis['rebalancing_opportunities']
        
        if not opportunities:
            logger.info("No rebalancing opportunities found")
            return False
        
        # Get Head of Service / Operations Manager
        managers = User.objects.filter(
            profile__role__code__in=['HEAD_OF_SERVICE', 'OPERATIONS_MANAGER'],
            is_active=True
        )
        
        if not managers.exists():
            logger.warning("No managers found for rebalancing suggestions")
            return False
        
        # Build email
        subject = f"🔄 Multi-Home Rebalancing Opportunities - Potential Savings: £{analysis['potential_savings']:.0f}"
        
        opportunities_text = "\n\n".join(
            f"{i+1}. {opp['recommendation']}\n"
            f"   Staff Available: {', '.join(opp['available_staff_names'][:3])}"
            f"{' + more' if len(opp['available_staff_names']) > 3 else ''}\n"
            f"   Total Savings: £{opp['savings']:.0f}"
            for i, opp in enumerate(opportunities[:10])  # Top 10
        )
        
        message = f"""
Multi-Home Staff Rebalancing Analysis
=====================================

Analysis Period: Next {analysis['analysis_period_days']} days
Total Potential Savings: £{analysis['potential_savings']:.0f}

Homes with Surplus:
{chr(10).join(f"  • {h['home_name']}: {h['coverage_ratio']*100:.0f}% staffed" for h in analysis['surplus_homes'])}

Homes with Shortages:
{chr(10).join(f"  • {h['home_name']}: {h['coverage_ratio']*100:.0f}% staffed" for h in analysis['shortage_homes'])}

TOP REBALANCING OPPORTUNITIES:
==============================

{opportunities_text}

ACTION REQUIRED:
1. Review opportunities above
2. Contact suggested staff to confirm willingness
3. Arrange travel logistics and bonus payments
4. Update rotas to reflect cross-home assignments

Cost Comparison:
• Agency shift: £280
• Staff travel (regular £120 + bonus £30-50): £150-170
• Savings per shift: £110-130

This automated analysis was generated by the Multi-Home Rebalancing AI.

---
Staff Rota System - Cross-Home Optimization
        """
        
        # Send email
        recipient_emails = [m.email for m in managers if m.email]
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_emails,
                fail_silently=False
            )
            logger.info(f"Sent rebalancing suggestions to {len(recipient_emails)} managers")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send rebalancing suggestions: {str(e)}")
            return False
    
    
    def execute_rebalancing(
        self, 
        opportunity: Dict,
        staff_ids: List[int],
        shift_dates: List[date]
    ) -> Dict:
        """
        Execute a rebalancing opportunity by creating travel shifts.
        
        Args:
            opportunity: Opportunity dict from analyze_all_homes()
            staff_ids: List of staff User IDs to assign
            shift_dates: List of dates for travel shifts
        
        Returns:
            dict: Execution results
        """
        logger.info(f"Executing rebalancing: {opportunity['recommendation']}")
        
        created_shifts = []
        errors = []
        
        for staff_id in staff_ids:
            try:
                staff = User.objects.get(id=staff_id)
                
                for shift_date in shift_dates:
                    # Get destination home
                    to_home = Unit.objects.get(name=opportunity['to_home'])
                    
                    # Get shift type for role
                    shift_type = ShiftType.objects.filter(
                        role__code=opportunity['role']
                    ).first()
                    
                    if not shift_type:
                        errors.append(f"No shift type found for role {opportunity['role']}")
                        continue
                    
                    # Create shift
                    shift = Shift.objects.create(
                        unit=to_home,
                        date=shift_date,
                        shift_type=shift_type,
                        assigned_to=staff,
                        shift_classification='TRAVEL',  # Mark as travel shift
                        notes=f"Cross-home rebalancing from {opportunity['from_home']}. "
                              f"Travel bonus: £{opportunity['travel_bonus']}"
                    )
                    
                    created_shifts.append(shift)
                    logger.info(f"Created travel shift for {staff.get_full_name()} on {shift_date}")
            
            except Exception as e:
                errors.append(f"Error creating shift for staff {staff_id}: {str(e)}")
                logger.error(f"Rebalancing error: {str(e)}")
        
        return {
            'success': len(created_shifts) > 0,
            'created_shifts': len(created_shifts),
            'errors': errors,
            'shifts': created_shifts
        }


def run_weekly_rebalancing_analysis():
    """
    Convenience function for weekly automated analysis.
    
    Returns:
        dict: Analysis results
    """
    ai = MultiHomeRebalancingAI()
    analysis = ai.analyze_all_homes(forecast_days=14)
    
    # Send suggestions if opportunities found
    if analysis['rebalancing_opportunities']:
        ai.send_rebalancing_suggestions(analysis)
    
    return analysis
