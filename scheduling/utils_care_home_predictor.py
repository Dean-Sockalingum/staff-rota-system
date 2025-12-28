"""
Care Home Performance Predictor
================================

Predictive ML model for estimating Care Inspectorate rating based on operational metrics.

Purpose:
- Predict CI rating (Excellent/Good/Adequate/Weak/Unsatisfactory)
- Identify early warning signs of potential downgrades
- Provide actionable recommendations for improvement
- Support proactive compliance management

Prediction Factors (100-point scale):
1. Training Compliance (0-20 points): Current vs required qualifications
2. Supervision Completion (0-20 points): Staff supervision meeting frequency
3. Incident Frequency (0-20 points): Falls, medication errors, complaints
4. Staff Turnover Rate (0-20 points): Leavers in last 12 months
5. Skill Mix Quality (0-10 points): RN/HCA ratio vs recommended
6. Overtime Usage (0-10 points): % shifts covered by OT vs standard

Rating Prediction Logic:
- 90-100 points: Excellent (Grade 6)
- 75-89 points: Very Good (Grade 5)
- 60-74 points: Good (Grade 4)
- 45-59 points: Adequate (Grade 3)
- 30-44 points: Weak (Grade 2)
- 0-29 points: Unsatisfactory (Grade 1)

ROI Target: £30,000/year
- Avoid CI downgrades (lost resident placements)
- Proactive remediation (cheaper than reactive)
- Reputation management

Author: AI Assistant Enhancement Sprint
Date: December 2025
"""

from django.db.models import Count, Q, F, Avg
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from typing import Dict, List, Optional
import logging

# Import models
from .models import (
    Unit, Shift, User, TrainingRecord, TrainingCourse,
    ComplianceViolation, Incident
)

logger = logging.getLogger(__name__)


class CareHomePerformancePredictor:
    """
    Predictive model for Care Inspectorate rating estimation.
    
    Uses 6-factor scoring system to predict likely CI rating and
    provide early warning of potential compliance issues.
    """
    
    # Scoring weights
    WEIGHTS = {
        'training_compliance': 20,    # Max 20 points
        'supervision_completion': 20, # Max 20 points
        'incident_frequency': 20,     # Max 20 points
        'turnover_rate': 20,          # Max 20 points
        'skill_mix': 10,              # Max 10 points
        'overtime_usage': 10          # Max 10 points
    }
    
    # Rating thresholds
    RATING_THRESHOLDS = {
        'Excellent': 90,
        'Very Good': 75,
        'Good': 60,
        'Adequate': 45,
        'Weak': 30,
        'Unsatisfactory': 0
    }
    
    # Target metrics
    TARGET_TRAINING_COMPLIANCE = 95.0  # %
    TARGET_SUPERVISION_FREQUENCY = 8   # Weeks
    TARGET_INCIDENTS_PER_100_RESIDENTS = 2.0
    TARGET_TURNOVER_RATE = 15.0        # % annual
    TARGET_RN_RATIO = 0.35             # 35% RNs in team
    TARGET_OT_USAGE = 15.0             # % of total shifts
    
    def __init__(self, care_home: Unit):
        """
        Initialize predictor for specific care home.
        
        Args:
            care_home: Unit instance representing the care home
        """
        self.care_home = care_home
        self.analysis_period_days = 90  # Default to 90-day analysis
    
    
    def predict_rating(self) -> Dict:
        """
        Generate comprehensive performance prediction.
        
        Returns:
            dict: {
                'predicted_rating': str,      # E.g., "Good"
                'total_score': int,           # 0-100
                'confidence': float,          # 0.0-1.0
                'factor_scores': dict,        # Breakdown by factor
                'recommendations': list,      # Improvement actions
                'risk_level': str,            # High/Medium/Low
                'next_review_date': date
            }
        """
        logger.info(f"Predicting CI rating for {self.care_home.name}")
        
        # Calculate individual factor scores
        factor_scores = {
            'training_compliance': self._score_training_compliance(),
            'supervision_completion': self._score_supervision_completion(),
            'incident_frequency': self._score_incident_frequency(),
            'turnover_rate': self._score_turnover_rate(),
            'skill_mix': self._score_skill_mix(),
            'overtime_usage': self._score_overtime_usage()
        }
        
        # Calculate total score
        total_score = sum(factor_scores.values())
        
        # Determine predicted rating
        predicted_rating = self._get_rating_from_score(total_score)
        
        # Calculate confidence (based on data completeness)
        confidence = self._calculate_confidence(factor_scores)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(factor_scores)
        
        # Determine risk level
        risk_level = self._determine_risk_level(total_score, factor_scores)
        
        return {
            'predicted_rating': predicted_rating,
            'total_score': total_score,
            'confidence': confidence,
            'factor_scores': factor_scores,
            'recommendations': recommendations,
            'risk_level': risk_level,
            'next_review_date': timezone.now().date() + timedelta(days=30),
            'analysis_period_days': self.analysis_period_days,
            'care_home': self.care_home.name
        }
    
    
    def _score_training_compliance(self) -> int:
        """
        Score training compliance (0-20 points).
        
        Logic:
        - Count staff with current mandatory training
        - Compare to total active staff
        - 100% compliance = 20 points, 0% = 0 points
        
        Returns:
            int: 0-20 score
        """
        from datetime import date
        
        # Get all active staff
        active_staff = User.objects.filter(
            profile__units=self.care_home,
            is_active=True
        ).count()
        
        if active_staff == 0:
            return 0
        
        # Get mandatory courses
        mandatory_courses = TrainingCourse.objects.filter(
            is_mandatory=True
        )
        
        if not mandatory_courses.exists():
            return 20  # No mandatory training = assume compliant
        
        # Count staff with ALL mandatory training current
        compliant_staff = 0
        for staff in User.objects.filter(profile__units=self.care_home, is_active=True):
            staff_compliant = True
            for course in mandatory_courses:
                # Check if staff has current training for this course
                has_current = TrainingRecord.objects.filter(
                    staff=staff,
                    course=course,
                    expiry_date__gte=date.today()
                ).exists()
                
                if not has_current:
                    staff_compliant = False
                    break
            
            if staff_compliant:
                compliant_staff += 1
        
        # Calculate compliance percentage
        compliance_rate = (compliant_staff / active_staff) * 100
        
        # Convert to 0-20 score
        score = int((compliance_rate / 100) * self.WEIGHTS['training_compliance'])
        
        logger.info(f"Training compliance: {compliance_rate:.1f}% = {score}/20 points")
        return score
    
    
    def _score_supervision_completion(self) -> int:
        """
        Score supervision completion (0-20 points).
        
        Logic:
        - Check if staff have had supervision in last 8 weeks
        - Target: All staff supervised every 8 weeks
        - 100% = 20 points, 0% = 0 points
        
        Returns:
            int: 0-20 score
        """
        # Get active staff
        active_staff = User.objects.filter(
            profile__units=self.care_home,
            is_active=True
        ).count()
        
        if active_staff == 0:
            return 0
        
        # Check staff with supervision in last 8 weeks
        cutoff_date = timezone.now() - timedelta(weeks=8)
        
        supervised_staff = User.objects.filter(
            profile__units=self.care_home,
            is_active=True,
            supervision_records__supervision_date__gte=cutoff_date
        ).distinct().count()
        
        # Calculate supervision rate
        supervision_rate = (supervised_staff / active_staff) * 100
        
        # Convert to 0-20 score
        score = int((supervision_rate / 100) * self.WEIGHTS['supervision_completion'])
        
        logger.info(f"Supervision completion: {supervision_rate:.1f}% = {score}/20 points")
        return score
    
    
    def _score_incident_frequency(self) -> int:
        """
        Score incident frequency (0-20 points).
        
        Logic:
        - Count incidents in last 90 days
        - Normalize by resident count
        - Target: <2 incidents per 100 residents
        - Low incidents = high score
        
        Returns:
            int: 0-20 score (inverted - fewer incidents = higher score)
        """
        # Get incidents in analysis period
        cutoff_date = timezone.now() - timedelta(days=self.analysis_period_days)
        
        incident_count = Incident.objects.filter(
            unit=self.care_home,
            incident_date__gte=cutoff_date
        ).count()
        
        # Get resident count (assume capacity if not tracked)
        resident_count = getattr(self.care_home, 'resident_count', 40)
        
        # Calculate incidents per 100 residents
        incidents_per_100 = (incident_count / resident_count) * 100 if resident_count > 0 else 0
        
        # Score: Target is <2 per 100 residents
        # 0 incidents = 20 points
        # 2 incidents = 15 points
        # 5+ incidents = 0 points
        if incidents_per_100 <= self.TARGET_INCIDENTS_PER_100_RESIDENTS:
            score = self.WEIGHTS['incident_frequency']
        elif incidents_per_100 <= 3:
            score = 15
        elif incidents_per_100 <= 4:
            score = 10
        elif incidents_per_100 <= 5:
            score = 5
        else:
            score = 0
        
        logger.info(f"Incidents: {incidents_per_100:.1f} per 100 residents = {score}/20 points")
        return score
    
    
    def _score_turnover_rate(self) -> int:
        """
        Score staff turnover (0-20 points).
        
        Logic:
        - Count staff who left in last 12 months
        - Compare to average headcount
        - Target: <15% annual turnover
        - Low turnover = high score
        
        Returns:
            int: 0-20 score (inverted)
        """
        # Get current active staff
        current_staff = User.objects.filter(
            profile__units=self.care_home,
            is_active=True
        ).count()
        
        # Get staff who left in last 12 months
        cutoff_date = timezone.now() - timedelta(days=365)
        
        leavers = User.objects.filter(
            profile__units=self.care_home,
            profile__leaving_date__gte=cutoff_date,
            profile__leaving_date__isnull=False
        ).count()
        
        if current_staff == 0:
            return 0
        
        # Calculate annual turnover rate
        turnover_rate = (leavers / current_staff) * 100
        
        # Score: Target <15% turnover
        # 0-10% = 20 points
        # 10-15% = 15 points
        # 15-20% = 10 points
        # 20-30% = 5 points
        # 30%+ = 0 points
        if turnover_rate <= 10:
            score = 20
        elif turnover_rate <= 15:
            score = 15
        elif turnover_rate <= 20:
            score = 10
        elif turnover_rate <= 30:
            score = 5
        else:
            score = 0
        
        logger.info(f"Turnover: {turnover_rate:.1f}% annually = {score}/20 points")
        return score
    
    
    def _score_skill_mix(self) -> int:
        """
        Score skill mix quality (0-10 points).
        
        Logic:
        - Calculate % of RNs in active workforce
        - Target: 35% RNs (CI recommended)
        - Close to target = high score
        
        Returns:
            int: 0-10 score
        """
        # Get active staff by role
        total_staff = User.objects.filter(
            profile__units=self.care_home,
            is_active=True
        ).count()
        
        if total_staff == 0:
            return 0
        
        rn_staff = User.objects.filter(
            profile__units=self.care_home,
            is_active=True,
            profile__role__code='RN'
        ).count()
        
        # Calculate RN ratio
        rn_ratio = (rn_staff / total_staff) * 100 if total_staff > 0 else 0
        
        # Score based on proximity to 35% target
        # 30-40% = 10 points
        # 25-30% or 40-45% = 7 points
        # 20-25% or 45-50% = 5 points
        # <20% or >50% = 0 points
        target = self.TARGET_RN_RATIO * 100
        
        if 30 <= rn_ratio <= 40:
            score = 10
        elif 25 <= rn_ratio <= 45:
            score = 7
        elif 20 <= rn_ratio <= 50:
            score = 5
        else:
            score = 0
        
        logger.info(f"Skill mix: {rn_ratio:.1f}% RNs (target {target}%) = {score}/10 points")
        return score
    
    
    def _score_overtime_usage(self) -> int:
        """
        Score overtime usage (0-10 points).
        
        Logic:
        - Calculate % of shifts covered by OT
        - Target: <15% OT usage
        - Low OT = high score (indicates stable staffing)
        
        Returns:
            int: 0-10 score (inverted)
        """
        # Get shifts in analysis period
        cutoff_date = timezone.now() - timedelta(days=self.analysis_period_days)
        
        total_shifts = Shift.objects.filter(
            unit=self.care_home,
            date__gte=cutoff_date
        ).count()
        
        if total_shifts == 0:
            return 0
        
        # Count OT shifts
        ot_shifts = Shift.objects.filter(
            unit=self.care_home,
            date__gte=cutoff_date,
            shift_classification='OT'
        ).count()
        
        # Calculate OT percentage
        ot_percentage = (ot_shifts / total_shifts) * 100
        
        # Score: Target <15% OT
        # 0-10% = 10 points
        # 10-15% = 7 points
        # 15-20% = 5 points
        # 20-30% = 3 points
        # 30%+ = 0 points
        if ot_percentage <= 10:
            score = 10
        elif ot_percentage <= 15:
            score = 7
        elif ot_percentage <= 20:
            score = 5
        elif ot_percentage <= 30:
            score = 3
        else:
            score = 0
        
        logger.info(f"OT usage: {ot_percentage:.1f}% = {score}/10 points")
        return score
    
    
    def _get_rating_from_score(self, total_score: int) -> str:
        """
        Convert total score to CI rating.
        
        Args:
            total_score: 0-100 score
        
        Returns:
            str: Rating name
        """
        for rating, threshold in self.RATING_THRESHOLDS.items():
            if total_score >= threshold:
                return rating
        
        return 'Unsatisfactory'
    
    
    def _calculate_confidence(self, factor_scores: Dict) -> float:
        """
        Calculate confidence level based on data completeness.
        
        Args:
            factor_scores: Dict of factor scores
        
        Returns:
            float: Confidence 0.0-1.0
        """
        # Simple heuristic: High confidence if all factors have data
        # Low confidence if many factors are 0 (indicating missing data)
        
        non_zero_factors = sum(1 for score in factor_scores.values() if score > 0)
        total_factors = len(factor_scores)
        
        confidence = non_zero_factors / total_factors
        
        return round(confidence, 2)
    
    
    def _generate_recommendations(self, factor_scores: Dict) -> List[str]:
        """
        Generate actionable recommendations for improvement.
        
        Args:
            factor_scores: Dict of factor scores
        
        Returns:
            list: Recommendation strings
        """
        recommendations = []
        
        # Training compliance
        if factor_scores['training_compliance'] < 15:
            recommendations.append(
                "❗ URGENT: Schedule mandatory training for non-compliant staff. "
                "Use Proactive Training Scheduler to auto-book courses."
            )
        elif factor_scores['training_compliance'] < 18:
            recommendations.append(
                "⚠️ Training compliance below target. Review expiring certifications."
            )
        
        # Supervision
        if factor_scores['supervision_completion'] < 15:
            recommendations.append(
                "❗ URGENT: Schedule supervision meetings for overdue staff. "
                "CI expects all staff supervised every 8 weeks."
            )
        elif factor_scores['supervision_completion'] < 18:
            recommendations.append(
                "⚠️ Supervision frequency needs improvement. Book remaining meetings."
            )
        
        # Incidents
        if factor_scores['incident_frequency'] < 10:
            recommendations.append(
                "❗ URGENT: High incident rate detected. Review safety protocols and "
                "consider additional staff training."
            )
        elif factor_scores['incident_frequency'] < 15:
            recommendations.append(
                "⚠️ Incident rate above target. Investigate root causes."
            )
        
        # Turnover
        if factor_scores['turnover_rate'] < 10:
            recommendations.append(
                "❗ URGENT: High staff turnover detected. Use Retention Predictor to "
                "identify at-risk staff and implement interventions."
            )
        elif factor_scores['turnover_rate'] < 15:
            recommendations.append(
                "⚠️ Turnover rate above target. Review staff satisfaction and benefits."
            )
        
        # Skill mix
        if factor_scores['skill_mix'] < 5:
            recommendations.append(
                "❗ Skill mix imbalance. Review RN ratio (CI recommends 35%)."
            )
        
        # Overtime
        if factor_scores['overtime_usage'] < 5:
            recommendations.append(
                "❗ High OT usage indicates staffing instability. Consider additional "
                "permanent hires to reduce agency dependency."
            )
        elif factor_scores['overtime_usage'] < 7:
            recommendations.append(
                "⚠️ OT usage above target. Monitor staffing levels."
            )
        
        # If all good
        if not recommendations:
            recommendations.append(
                "✅ All metrics within acceptable ranges. Maintain current standards."
            )
        
        return recommendations
    
    
    def _determine_risk_level(self, total_score: int, factor_scores: Dict) -> str:
        """
        Determine overall risk level for CI downgrade.
        
        Args:
            total_score: 0-100 score
            factor_scores: Dict of factor scores
        
        Returns:
            str: 'High', 'Medium', or 'Low'
        """
        # High risk: Score <60 OR any single factor critically low
        if total_score < 60:
            return 'High'
        
        # Check for any critically low factors
        critical_low = any(
            factor_scores['training_compliance'] < 12,
            factor_scores['supervision_completion'] < 12,
            factor_scores['incident_frequency'] < 10,
            factor_scores['turnover_rate'] < 10
        )
        
        if critical_low:
            return 'High'
        
        # Medium risk: Score 60-74
        if total_score < 75:
            return 'Medium'
        
        # Low risk: Score 75+
        return 'Low'
    
    
    def send_manager_alert(self, prediction: Dict) -> bool:
        """
        Send email alert to managers if risk is High or Medium.
        
        Args:
            prediction: Dict from predict_rating()
        
        Returns:
            bool: True if alert sent successfully
        """
        from django.core.mail import send_mail
        from django.conf import settings
        
        # Only alert on High/Medium risk
        if prediction['risk_level'] == 'Low':
            logger.info(f"No alert needed - {self.care_home.name} is Low risk")
            return False
        
        # Get managers
        managers = User.objects.filter(
            profile__role__code__in=['MANAGER', 'HEAD_OF_SERVICE'],
            is_active=True
        )
        
        if not managers.exists():
            logger.warning(f"No managers found to alert for {self.care_home.name}")
            return False
        
        # Build email content
        subject = f"🚨 Care Home Performance Alert: {self.care_home.name} - {prediction['risk_level']} Risk"
        
        recommendations_text = "\n".join(f"  • {rec}" for rec in prediction['recommendations'])
        
        factor_breakdown = "\n".join(
            f"  • {factor.replace('_', ' ').title()}: {score}/{self.WEIGHTS[factor]}"
            for factor, score in prediction['factor_scores'].items()
        )
        
        message = f"""
Performance Prediction Alert
===========================

Care Home: {self.care_home.name}
Predicted CI Rating: {prediction['predicted_rating']}
Total Score: {prediction['total_score']}/100
Risk Level: {prediction['risk_level']}
Confidence: {prediction['confidence']*100:.0f}%

Factor Breakdown:
{factor_breakdown}

Recommendations:
{recommendations_text}

Next Review: {prediction['next_review_date']}

This automated alert was generated by the Care Home Performance Predictor.
Please review and take action on urgent items as soon as possible.

---
Staff Rota System - AI Performance Monitoring
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
            logger.info(f"Sent performance alert to {len(recipient_emails)} managers")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send performance alert: {str(e)}")
            return False


def run_prediction_for_all_homes():
    """
    Convenience function to run predictions for all care homes.
    
    Returns:
        dict: Results by care home
    """
    results = {}
    
    for home in Unit.objects.filter(is_active=True):
        predictor = CareHomePerformancePredictor(home)
        prediction = predictor.predict_rating()
        
        # Send alert if needed
        predictor.send_manager_alert(prediction)
        
        results[home.name] = prediction
    
    return results
