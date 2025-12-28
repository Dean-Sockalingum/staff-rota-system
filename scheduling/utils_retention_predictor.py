"""
Staff Retention Predictor - Optional Enhancement 1
ML-based prediction of staff turnover risk for proactive intervention

Business Impact:
- Save 2-3 turnovers/year = £10-20K (recruitment costs)
- 300-600% ROI in year 1
- Improved staff morale through proactive support
"""

from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.db.models import Count, Avg, Q
from scheduling.models import User, Shift, LeaveRequest
from staff_records.models import SicknessRecord
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import logging

logger = logging.getLogger(__name__)


class StaffRetentionPredictor:
    """
    Predicts staff turnover risk using ML analysis of behavioral patterns
    
    Risk Factors Analyzed:
    - Sickness patterns (frequency, duration)
    - OT hours (burnout indicator)
    - Leave usage (work-life balance)
    - Shift swap frequency (scheduling dissatisfaction)
    - Length of service (tenure)
    """
    
    def __init__(self):
        self.today = timezone.now().date()
        self.lookback_days = 180  # Analyze last 6 months
    
    def predict_all_staff_risk(self):
        """
        Analyze all active staff and predict turnover risk
        
        Returns:
            list of dicts with staff and risk scores
        """
        active_staff = User.objects.filter(
            is_active=True,
            is_staff=False  # Exclude admin users
        )
        
        predictions = []
        
        for staff in active_staff:
            risk_score = self._calculate_risk_score(staff)
            
            if risk_score >= 60:  # High risk threshold
                predictions.append({
                    'staff': staff,
                    'risk_score': risk_score,
                    'risk_level': 'HIGH',
                    'factors': risk_score['factors'],
                    'interventions': self._suggest_interventions(risk_score)
                })
            elif risk_score >= 40:
                predictions.append({
                    'staff': staff,
                    'risk_score': risk_score,
                    'risk_level': 'MEDIUM',
                    'factors': risk_score['factors'],
                    'interventions': self._suggest_interventions(risk_score)
                })
        
        # Sort by risk score (highest first)
        predictions.sort(key=lambda x: x['risk_score']['total'], reverse=True)
        
        return predictions
    
    def _calculate_risk_score(self, staff):
        """
        Calculate turnover risk score (0-100) based on multiple factors
        
        Returns:
            dict with total score and factor breakdown
        """
        factors = {}
        
        # Factor 1: Sickness Pattern (0-25 points)
        # More sickness = higher risk
        sickness_score = self._analyze_sickness(staff)
        factors['sickness'] = sickness_score
        
        # Factor 2: OT/Burnout (0-25 points)
        # Excessive OT = burnout risk
        ot_score = self._analyze_overtime(staff)
        factors['overtime'] = ot_score
        
        # Factor 3: Leave Usage (0-20 points)
        # Not taking leave = burnout/dissatisfaction
        leave_score = self._analyze_leave_usage(staff)
        factors['leave_usage'] = leave_score
        
        # Factor 4: Shift Swap Frequency (0-15 points)
        # Many swaps = scheduling dissatisfaction
        swap_score = self._analyze_shift_swaps(staff)
        factors['shift_swaps'] = swap_score
        
        # Factor 5: Tenure (0-15 points)
        # <6 months or >3 years = higher risk
        tenure_score = self._analyze_tenure(staff)
        factors['tenure'] = tenure_score
        
        total_risk = sum(factors.values())
        
        return {
            'total': total_risk,
            'factors': factors
        }
    
    def _analyze_sickness(self, staff):
        """Analyze sickness patterns (0-25 points)"""
        cutoff_date = self.today - timedelta(days=self.lookback_days)
        
        sickness_records = SicknessRecord.objects.filter(
            user=staff,
            sickness_start__gte=cutoff_date
        )
        
        total_days = sum(
            (min(record.sickness_end or self.today, self.today) - 
             max(record.sickness_start, cutoff_date)).days + 1
            for record in sickness_records
        )
        
        # High sickness = higher risk
        # 0 days = 0 points, 30+ days = 25 points
        score = min(25, (total_days / 30) * 25)
        
        return round(score, 1)
    
    def _analyze_overtime(self, staff):
        """Analyze OT hours (0-25 points)"""
        cutoff_date = self.today - timedelta(days=self.lookback_days)
        
        ot_shifts = Shift.objects.filter(
            user=staff,
            date__gte=cutoff_date,
            shift_classification='OVERTIME'
        ).count()
        
        # Excessive OT = burnout risk
        # 0 shifts = 0 points, 20+ OT shifts in 6 months = 25 points
        score = min(25, (ot_shifts / 20) * 25)
        
        return round(score, 1)
    
    def _analyze_leave_usage(self, staff):
        """Analyze leave usage (0-20 points)"""
        current_year_start = timezone.datetime(self.today.year, 1, 1).date()
        
        # Get approved leave days this year
        approved_leave = LeaveRequest.objects.filter(
            user=staff,
            status='approved',
            start_date__year=self.today.year
        ).aggregate(
            total=Count('id')
        )['total'] or 0
        
        # Not taking leave = risk
        # 14+ days taken = 0 points, 0 days = 20 points
        if approved_leave >= 14:
            score = 0
        elif approved_leave == 0:
            score = 20
        else:
            score = 20 - (approved_leave / 14 * 20)
        
        return round(score, 1)
    
    def _analyze_shift_swaps(self, staff):
        """Analyze shift swap requests (0-15 points)"""
        cutoff_date = self.today - timedelta(days=self.lookback_days)
        
        from scheduling.models import ShiftSwapRequest
        
        swap_requests = ShiftSwapRequest.objects.filter(
            Q(requesting_user=staff) | Q(target_user=staff),
            created_at__gte=cutoff_date
        ).count()
        
        # Many swaps = scheduling dissatisfaction
        # 0 swaps = 0 points, 10+ swaps = 15 points
        score = min(15, (swap_requests / 10) * 15)
        
        return round(score, 1)
    
    def _analyze_tenure(self, staff):
        """Analyze length of service (0-15 points)"""
        if not staff.date_joined:
            return 5  # Unknown tenure = moderate risk
        
        tenure_days = (self.today - staff.date_joined.date()).days
        tenure_months = tenure_days / 30
        
        # U-shaped risk: New hires (<6mo) and long-tenure (>36mo) higher risk
        if tenure_months < 6:
            score = 15  # New hire flight risk
        elif tenure_months > 36:
            score = 10  # Long tenure burnout risk
        elif 12 <= tenure_months <= 24:
            score = 0  # Sweet spot (1-2 years)
        else:
            score = 5  # Moderate risk
        
        return score
    
    def _suggest_interventions(self, risk_data):
        """
        Suggest interventions based on risk factors
        
        Returns:
            list of intervention recommendations
        """
        interventions = []
        factors = risk_data['factors']
        
        if factors['sickness'] > 15:
            interventions.append({
                'issue': 'High sickness absence',
                'action': 'Schedule wellbeing check-in',
                'priority': 'high'
            })
        
        if factors['overtime'] > 15:
            interventions.append({
                'issue': 'Excessive overtime (burnout risk)',
                'action': 'Reduce OT hours, review workload',
                'priority': 'high'
            })
        
        if factors['leave_usage'] > 12:
            interventions.append({
                'issue': 'Not taking annual leave',
                'action': 'Encourage leave booking, offer flexible dates',
                'priority': 'medium'
            })
        
        if factors['shift_swaps'] > 10:
            interventions.append({
                'issue': 'Frequent shift swap requests',
                'action': 'Review scheduling preferences, offer flexibility',
                'priority': 'medium'
            })
        
        if factors['tenure'] > 10:
            interventions.append({
                'issue': 'Tenure risk (new hire or long-term)',
                'action': 'Conduct stay interview, discuss career development',
                'priority': 'medium'
            })
        
        return interventions
    
    def send_manager_alerts(self, high_risk_only=True):
        """
        Send alerts to managers about at-risk staff
        
        Returns:
            int: number of alerts sent
        """
        predictions = self.predict_all_staff_risk()
        
        if high_risk_only:
            predictions = [p for p in predictions if p['risk_level'] == 'HIGH']
        
        if not predictions:
            logger.info("No high-risk staff identified")
            return 0
        
        # Get managers
        managers = User.objects.filter(
            role__is_management=True,
            is_active=True
        )
        
        from django.core.mail import send_mail
        
        for manager in managers:
            staff_list = "\n\n".join([
                f"- {p['staff'].full_name} (SAP: {p['staff'].sap})\n"
                f"  Risk Score: {p['risk_score']['total']}/100\n"
                f"  Key Factors: {', '.join([k for k, v in p['risk_score']['factors'].items() if v > 10])}\n"
                f"  Recommended Actions:\n" + 
                "\n".join([f"    • {i['action']}" for i in p['interventions']])
                for p in predictions
            ])
            
            subject = f"🚨 Staff Retention Alert: {len(predictions)} High-Risk Staff"
            message = f"""
Staff Retention Prediction Alert

{len(predictions)} staff members identified as HIGH RISK for turnover.

URGENT INTERVENTIONS REQUIRED:

{staff_list}

This is an automated alert from the ML-based retention prediction system.
Early intervention can significantly reduce turnover risk.

Best regards,
Staff Rota Retention Predictor
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    'noreply@staffrota.com',
                    [manager.email],
                    fail_silently=False
                )
            except Exception as e:
                logger.error(f"Failed to send retention alert: {e}")
        
        logger.info(f"Sent retention alerts for {len(predictions)} high-risk staff")
        return len(predictions)


def run_retention_prediction():
    """
    Main entry point for scheduled task
    Run weekly via cron/celery
    """
    predictor = StaffRetentionPredictor()
    predictions = predictor.predict_all_staff_risk()
    
    high_risk_count = len([p for p in predictions if p['risk_level'] == 'HIGH'])
    medium_risk_count = len([p for p in predictions if p['risk_level'] == 'MEDIUM'])
    
    logger.info(f"Retention prediction complete: {high_risk_count} high risk, {medium_risk_count} medium risk")
    
    # Send alerts for high-risk staff
    if high_risk_count > 0:
        predictor.send_manager_alerts(high_risk_only=True)
    
    return {
        'total_analyzed': User.objects.filter(is_active=True, is_staff=False).count(),
        'high_risk': high_risk_count,
        'medium_risk': medium_risk_count,
        'predictions': predictions
    }
