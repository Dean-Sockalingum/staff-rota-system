"""
Intelligent Overtime Distribution System
Automatically ranks and contacts staff for overtime coverage based on multiple factors
"""

from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import math


class OvertimeRanker:
    """
    Smart ranking algorithm for overtime coverage
    
    Scoring Factors:
    - Availability (40%): Willing, shift type matches, home matches
    - Acceptance Rate (25%): Historical response to OT requests
    - Fairness (20%): Recent OT hours distribution
    - Proximity (10%): Geographic distance to care home
    - Reliability (5%): Attendance record, low sickness
    """
    
    WEIGHTS = {
        'availability': 0.40,
        'acceptance_rate': 0.25,
        'fairness': 0.20,
        'proximity': 0.10,
        'reliability': 0.05,
    }
    
    def __init__(self, shift_date, shift_type, care_home, unit=None):
        """
        Initialize ranker for a specific coverage need
        
        Args:
            shift_date: Date of shift needing coverage
            shift_type: 'DAY' or 'NIGHT'
            care_home: CareHome instance
            unit: Optional specific Unit instance
        """
        self.shift_date = shift_date
        self.shift_type = shift_type.upper()
        self.care_home = care_home
        self.unit = unit
        self.is_weekend = shift_date.weekday() >= 5  # Sat=5, Sun=6
        
    def rank_all_available_staff(self):
        """
        Get all OT-willing staff ranked by suitability
        
        Returns:
            List of dicts with staff, score, and breakdown
        """
        from .models_overtime import StaffOvertimePreference
        from .models import User
        
        # Get all staff with OT preferences who are available
        preferences = StaffOvertimePreference.objects.filter(
            available_for_overtime=True
        ).select_related('staff', 'staff__role', 'staff__unit').prefetch_related('willing_to_work_at')
        
        ranked_staff = []
        
        for pref in preferences:
            # Calculate comprehensive score
            score_breakdown = self._calculate_scores(pref)
            total_score = sum(
                score_breakdown[key] * self.WEIGHTS[key]
                for key in self.WEIGHTS.keys()
            )
            
            # Only include if availability score > 0 (basic eligibility)
            if score_breakdown['availability'] > 0:
                ranked_staff.append({
                    'staff': pref.staff,
                    'preference': pref,
                    'total_score': round(total_score, 2),
                    'breakdown': score_breakdown,
                    'phone': pref.phone_number,
                    'contact_method': pref.get_preferred_contact_method_display(),
                    'min_notice_hours': pref.min_notice_hours,
                })
        
        # Sort by total score (descending)
        ranked_staff.sort(key=lambda x: x['total_score'], reverse=True)
        
        return ranked_staff
    
    def get_top_candidates(self, limit=5):
        """
        Get top N candidates for immediate contact
        
        Args:
            limit: Number of top candidates to return
            
        Returns:
            List of top-ranked staff
        """
        all_ranked = self.rank_all_available_staff()
        return all_ranked[:limit]
    
    def _calculate_scores(self, preference):
        """
        Calculate individual component scores for a staff member
        
        Returns:
            Dict with scores for each factor (0-100 scale)
        """
        return {
            'availability': self._score_availability(preference),
            'acceptance_rate': self._score_acceptance_rate(preference),
            'fairness': self._score_fairness(preference),
            'proximity': self._score_proximity(preference),
            'reliability': self._score_reliability(preference),
        }
    
    def _score_availability(self, preference):
        """
        Score based on shift type, day, and home preferences (0-100)
        
        Must match:
        - Shift type (day/night)
        - Day type (weekday/weekend)
        - Willing to work at this home
        """
        score = 0
        
        # Check shift type match (50 points)
        if self.shift_type == 'DAY' and preference.available_early_shifts:
            score += 50
        elif self.shift_type == 'NIGHT' and preference.available_night_shifts:
            score += 50
        else:
            return 0  # Not available for this shift type
        
        # Check day type match (25 points)
        if self.is_weekend and preference.available_weekends:
            score += 25
        elif not self.is_weekend and preference.available_weekdays:
            score += 25
        else:
            return 0  # Not available for this day type
        
        # Check willing to work at this home (25 points)
        willing_units = preference.willing_to_work_at.all()
        if willing_units.filter(care_home=self.care_home).exists():
            score += 25
        else:
            return 0  # Not willing to work at this home
        
        return score
    
    def _score_acceptance_rate(self, preference):
        """
        Score based on historical OT acceptance (0-100)
        
        Uses acceptance_rate field (percentage)
        """
        # Convert percentage to 0-100 score
        return float(preference.acceptance_rate)
    
    def _score_fairness(self, preference):
        """
        Score based on fairness - prioritize staff with less recent OT (0-100)
        
        Logic: Staff who haven't had OT recently get higher scores
        """
        from .models import Shift
        
        # Get OT shifts in last 30 days
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent_ot_shifts = Shift.objects.filter(
            staff=preference.staff,
            date__gte=thirty_days_ago,
            shift_classification='OVERTIME'
        ).count()
        
        # Score inversely proportional to recent OT
        # 0 shifts = 100 points, 10+ shifts = 0 points
        if recent_ot_shifts == 0:
            return 100
        elif recent_ot_shifts >= 10:
            return 0
        else:
            return 100 - (recent_ot_shifts * 10)
    
    def _score_proximity(self, preference):
        """
        Score based on proximity to care home (0-100)
        
        Note: Currently returns neutral score as postcode data not yet in system
        TODO: Implement when postcode/address data available
        """
        # Placeholder: All staff get neutral score for now
        # Future: Calculate distance from staff.postcode to care_home.postcode
        return 50
    
    def _score_reliability(self, preference):
        """
        Score based on attendance reliability (0-100)
        
        Factors:
        - Sickness rate (lower = better)
        - No-show history (none = better)
        """
        from staff_records.models import SicknessRecord
        
        staff = preference.staff
        
        # Get sickness records in last 6 months
        six_months_ago = timezone.now().date() - timedelta(days=180)
        sickness_days = SicknessRecord.objects.filter(
            user=staff,
            sickness_start__gte=six_months_ago
        ).count()
        
        # Score inversely proportional to sickness
        # 0 days = 100 points, 20+ days = 0 points
        if sickness_days == 0:
            return 100
        elif sickness_days >= 20:
            return 0
        else:
            return 100 - (sickness_days * 5)


class OvertimeCoverageOrchestrator:
    """
    Manages the full OT coverage workflow:
    1. Detect coverage need
    2. Rank available staff
    3. Send alerts in priority order
    4. Track responses
    5. Update fairness metrics
    """
    
    def __init__(self, shift_needing_coverage):
        """
        Args:
            shift_needing_coverage: Shift instance that needs coverage
        """
        self.shift = shift_needing_coverage
        self.ranker = OvertimeRanker(
            shift_date=shift_needing_coverage.date,
            shift_type=self._determine_shift_type(),
            care_home=shift_needing_coverage.unit.care_home,
            unit=shift_needing_coverage.unit
        )
    
    def _determine_shift_type(self):
        """Extract day/night from shift type name"""
        shift_name = self.shift.shift_type.name.upper()
        if 'NIGHT' in shift_name:
            return 'NIGHT'
        else:
            return 'DAY'
    
    def get_contact_queue(self, batch_size=5):
        """
        Get prioritized list of staff to contact
        
        Args:
            batch_size: Number of staff to contact in first batch
            
        Returns:
            List of staff ordered by ranking score
        """
        return self.ranker.get_top_candidates(limit=batch_size)
    
    def create_coverage_request(self):
        """
        Create OvertimeCoverageRequest record for tracking
        
        Returns:
            OvertimeCoverageRequest instance
        """
        from .models_overtime import OvertimeCoverageRequest
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Get system user for created_by (or first admin)
        system_user = User.objects.filter(is_superuser=True).first()
        
        request = OvertimeCoverageRequest.objects.create(
            unit=self.shift.unit,
            shift_date=self.shift.date,
            shift_type=self.shift.shift_type.name,
            required_role=self.shift.role.name if self.shift.role else 'ANY',
            created_by=system_user,
            status='PENDING'
        )
        
        return request
    
    def send_alerts_to_ranked_staff(self, coverage_request, top_n=5):
        """
        Send alerts to top N ranked staff
        
        Args:
            coverage_request: OvertimeCoverageRequest instance
            top_n: Number of staff to alert
            
        Returns:
            List of staff contacted
        """
        from .models_overtime import OvertimeCoverageResponse
        
        candidates = self.get_contact_queue(batch_size=top_n)
        contacted = []
        
        for candidate in candidates:
            staff = candidate['staff']
            preference = candidate['preference']
            
            # Create response record
            response = OvertimeCoverageResponse.objects.create(
                request=coverage_request,
                staff=staff,
                contact_method=preference.preferred_contact_method,
                reliability_score_when_sent=Decimal(str(candidate['total_score'])),
                response='NO_RESPONSE'  # Will update when they respond
            )
            
            # Send actual alert (SMS/email/app notification)
            self._send_alert(staff, preference, coverage_request)
            
            # Update preference tracking
            preference.total_requests_sent += 1
            preference.last_contacted = timezone.now()
            preference.save()
            
            contacted.append({
                'staff': staff,
                'score': candidate['total_score'],
                'contact_method': preference.get_preferred_contact_method_display(),
                'response_id': response.id
            })
        
        # Update coverage request
        coverage_request.total_contacted = len(contacted)
        coverage_request.save()
        
        return contacted
    
    def _send_alert(self, staff, preference, coverage_request):
        """
        Send actual alert via preferred method
        
        TODO: Integrate with SMS/email services
        For now: Log the alert
        """
        import logging
        logger = logging.getLogger(__name__)
        
        message = (
            f"OVERTIME OPPORTUNITY: {coverage_request.shift_type} shift "
            f"on {coverage_request.shift_date} at {coverage_request.unit.name}. "
            f"Reply YES to accept or NO to decline."
        )
        
        if preference.preferred_contact_method == 'SMS':
            # TODO: Send SMS to preference.phone_number
            logger.info(f"SMS to {staff.full_name} ({preference.phone_number}): {message}")
        elif preference.preferred_contact_method == 'EMAIL':
            # TODO: Send email
            logger.info(f"Email to {staff.full_name} ({staff.email}): {message}")
        else:
            # App notification
            logger.info(f"App notification to {staff.full_name}: {message}")
    
    def record_response(self, coverage_request, staff, accepted, decline_reason=None):
        """
        Record staff response to OT request
        
        Args:
            coverage_request: OvertimeCoverageRequest instance
            staff: User instance who responded
            accepted: Boolean - did they accept?
            decline_reason: Optional reason for declining
        """
        from .models_overtime import OvertimeCoverageResponse, StaffOvertimePreference
        
        # Find their response record
        response = OvertimeCoverageResponse.objects.filter(
            request=coverage_request,
            staff=staff
        ).first()
        
        if response:
            response.responded_at = timezone.now()
            response.response = 'ACCEPTED' if accepted else 'DECLINED'
            if decline_reason:
                response.decline_reason = decline_reason
            response.save()
            
            # Update coverage request
            coverage_request.total_responses += 1
            if accepted:
                coverage_request.total_acceptances += 1
                coverage_request.status = 'FILLED'
                coverage_request.filled_by = staff
                coverage_request.filled_at = timezone.now()
                
                # Calculate time to fill
                time_diff = coverage_request.filled_at - coverage_request.created_at
                coverage_request.time_to_fill_minutes = int(time_diff.total_seconds() / 60)
            
            coverage_request.save()
            
            # Update staff preference
            try:
                pref = StaffOvertimePreference.objects.get(staff=staff)
                if accepted:
                    pref.total_requests_accepted += 1
                    pref.total_shifts_worked += 1
                    pref.last_worked_overtime = timezone.now()
                pref.update_acceptance_rate()
                pref.save()
            except StaffOvertimePreference.DoesNotExist:
                pass


def rank_staff_for_coverage(shift):
    """
    Convenience function to quickly rank staff for a shift
    
    Args:
        shift: Shift instance needing coverage
        
    Returns:
        List of ranked candidates
    """
    orchestrator = OvertimeCoverageOrchestrator(shift)
    return orchestrator.get_contact_queue()


def auto_request_ot_coverage(shift, top_n=5):
    """
    Fully automated OT coverage request
    
    Args:
        shift: Shift instance needing coverage
        top_n: Number of staff to contact initially
        
    Returns:
        Dict with coverage_request and contacted_staff
    """
    orchestrator = OvertimeCoverageOrchestrator(shift)
    
    # Create request record
    coverage_request = orchestrator.create_coverage_request()
    
    # Send alerts to top N candidates
    contacted = orchestrator.send_alerts_to_ranked_staff(coverage_request, top_n=top_n)
    
    return {
        'coverage_request': coverage_request,
        'contacted_staff': contacted,
        'total_contacted': len(contacted)
    }
