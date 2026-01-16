"""
ITIL Change Management Handlers for NHS Highland HSCP Rota System
Implements change request creation, approval workflow, risk assessment, and PIR tracking

Handler Classes:
1. ChangeRequestHandler - Create/manage change requests in ServiceNow
2. RiskAssessmentHandler - Calculate risk scores, mitigation strategies
3. CABScheduler - Schedule CAB meetings, manage agendas
4. ChangeCalendarHandler - Track change windows, blackout periods
5. PIRHandler - Post-implementation review tracking and metrics
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


# ==============================================================================
# 1. CHANGE REQUEST HANDLER
# ==============================================================================

class ChangeRequestHandler:
    """
    Creates and manages change requests in ServiceNow.
    Integrates with rotasystems.itil_change_settings configuration.
    """
    
    def __init__(self):
        from rotasystems.itil_change_settings import SERVICENOW_INTEGRATION
        self.config = SERVICENOW_INTEGRATION
        self.base_url = self.config['instance_url']
        self.access_token = None
    
    def authenticate(self) -> bool:
        """
        Authenticate with ServiceNow using OAuth 2.0.
        Returns True if authentication successful.
        """
        auth_config = self.config['authentication']
        
        try:
            response = requests.post(
                auth_config['token_url'],
                data={
                    'grant_type': 'client_credentials',
                    'client_id': auth_config['client_id'],
                    'client_secret': auth_config['client_secret'],
                    'scope': auth_config['scope'],
                },
                timeout=10,
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            
            logger.info("ServiceNow authentication successful")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"ServiceNow authentication failed: {e}")
            return False
    
    def create_change_request(
        self,
        change_type: str,
        short_description: str,
        description: str,
        category: str,
        risk_score: int,
        impact_score: int,
        start_date: datetime,
        end_date: datetime,
        backout_plan: str,
        test_plan: str,
        requested_by: str,
        cmdb_ci: str = 'NHS Highland HSCP Rota System',
    ) -> Dict:
        """
        Create a change request in ServiceNow.
        
        Args:
            change_type: 'standard', 'normal', or 'emergency'
            short_description: Summary (max 160 chars)
            description: Detailed description with impact analysis
            category: 'Software', 'Hardware', 'Network', 'Database'
            risk_score: 1-5 from risk matrix
            impact_score: 1-5 from risk matrix
            start_date: Change window start
            end_date: Change window end
            backout_plan: Rollback procedure
            test_plan: Testing procedure
            requested_by: User who requested change
            cmdb_ci: Configuration Item from CMDB
        
        Returns:
            Dict with change request details {'sys_id', 'number', 'state'}
        """
        if not self.access_token:
            if not self.authenticate():
                raise Exception("Failed to authenticate with ServiceNow")
        
        endpoint = self.config['api_endpoints']['create_change']
        priority = risk_score * impact_score  # Auto-calculate priority
        
        payload = {
            'short_description': short_description[:160],  # Enforce max length
            'description': description,
            'category': category,
            'type': change_type,
            'risk': risk_score,
            'impact': impact_score,
            'priority': min(priority, 5),  # Cap at 5
            'assignment_group': 'CGI Application Support',
            'requested_by': requested_by,
            'cmdb_ci': cmdb_ci,
            'start_date': start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'end_date': end_date.strftime('%Y-%m-%d %H:%M:%S'),
            'backout_plan': backout_plan,
            'test_plan': test_plan,
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{endpoint['url']}",
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json',
                },
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            
            result = response.json().get('result', {})
            change_number = result.get('number')
            
            logger.info(f"Change request created: {change_number}")
            return {
                'sys_id': result.get('sys_id'),
                'number': change_number,
                'state': result.get('state'),
                'approval': result.get('approval'),
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create change request: {e}")
            raise
    
    def get_change_status(self, sys_id: str) -> Dict:
        """
        Retrieve change request status from ServiceNow.
        
        Returns:
            Dict with {'state', 'approval', 'work_notes', 'close_notes'}
        """
        endpoint = self.config['api_endpoints']['get_change_status']
        url = f"{self.base_url}{endpoint['url']}".format(sys_id=sys_id)
        
        try:
            response = requests.get(
                url,
                headers={'Authorization': f'Bearer {self.access_token}'},
                timeout=10,
            )
            response.raise_for_status()
            
            result = response.json().get('result', {})
            return {
                'state': result.get('state'),
                'approval': result.get('approval'),
                'work_notes': result.get('work_notes'),
                'close_notes': result.get('close_notes'),
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get change status: {e}")
            raise
    
    def add_work_note(self, sys_id: str, note: str) -> bool:
        """
        Add timestamped work note to change request.
        Used for documenting implementation progress.
        """
        endpoint = self.config['api_endpoints']['add_work_note']
        url = f"{self.base_url}{endpoint['url']}".format(sys_id=sys_id)
        
        timestamped_note = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {note}"
        
        try:
            response = requests.patch(
                url,
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json',
                },
                json={'work_notes': timestamped_note},
                timeout=10,
            )
            response.raise_for_status()
            
            logger.info(f"Work note added to change {sys_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to add work note: {e}")
            return False


# ==============================================================================
# 2. RISK ASSESSMENT HANDLER
# ==============================================================================

class RiskAssessmentHandler:
    """
    Calculates risk scores using probability × impact matrix.
    Recommends mitigation strategies based on risk level.
    """
    
    def __init__(self):
        from rotasystems.itil_change_settings import RISK_ASSESSMENT
        self.config = RISK_ASSESSMENT
        self.risk_matrix = self.config['risk_matrix']
    
    def calculate_risk_score(
        self,
        probability: str,  # 'very_low', 'low', 'medium', 'high', 'very_high'
        impact: str,  # 'minimal', 'minor', 'moderate', 'major', 'critical'
    ) -> Dict:
        """
        Calculate risk score using probability × impact matrix.
        
        Returns:
            Dict with {
                'probability_score': int,
                'impact_score': int,
                'risk_score': int,
                'risk_level': str,  # 'low', 'medium', 'high', 'critical'
                'recommended_action': str,
            }
        """
        prob_score = self.risk_matrix['probability'][probability]['score']
        impact_score = self.risk_matrix['impact'][impact]['score']
        risk_score = prob_score * impact_score
        
        # Determine risk level
        risk_level = None
        recommended_action = None
        
        for level, config in self.risk_matrix['risk_score_interpretation'].items():
            if config['range'][0] <= risk_score <= config['range'][1]:
                risk_level = level
                recommended_action = config['action']
                break
        
        return {
            'probability_score': prob_score,
            'impact_score': impact_score,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'recommended_action': recommended_action,
            'probability_description': self.risk_matrix['probability'][probability]['description'],
            'impact_description': self.risk_matrix['impact'][impact]['description'],
        }
    
    def recommend_mitigation(self, risk_score: int, change_type: str) -> List[str]:
        """
        Recommend mitigation strategies based on risk score and change type.
        
        Returns:
            List of recommended mitigation strategies
        """
        mitigations = []
        strategies = self.config['mitigation_strategies']
        
        if risk_score >= 13:  # High/Critical risk
            mitigations.extend([
                strategies['phased_rollout'],
                strategies['database_backups'],
                strategies['rollback_plan'],
                strategies['monitoring'],
                strategies['communication'],
            ])
            
            if change_type == 'application':
                mitigations.append(strategies['blue_green_deployment'])
                mitigations.append(strategies['feature_flags'])
        
        elif risk_score >= 7:  # Medium risk
            mitigations.extend([
                strategies['database_backups'],
                strategies['rollback_plan'],
                strategies['monitoring'],
            ])
        
        else:  # Low risk
            mitigations.append(strategies['rollback_plan'])
        
        return mitigations
    
    def assess_risk_factors(
        self,
        complexity: str,
        reversibility: str,
        timing: str,
        dependencies: str,
        testing: str,
    ) -> Dict:
        """
        Assess additional risk factors beyond probability × impact.
        
        Returns:
            Dict with risk factor analysis and recommendations
        """
        risk_factors = self.config['risk_factors']
        
        # High-risk combinations
        high_risk_flags = []
        
        if complexity == 'Cross-system integration':
            high_risk_flags.append('Complex cross-system change increases coordination risk')
        
        if reversibility == 'Irreversible':
            high_risk_flags.append('Irreversible change requires exceptional testing and backup')
        
        if timing == 'Peak usage time':
            high_risk_flags.append('Peak timing increases user impact, recommend off-hours window')
        
        if dependencies == 'Critical path':
            high_risk_flags.append('Critical path dependency requires stakeholder coordination')
        
        if testing == 'No testing (emergency)':
            high_risk_flags.append('Untested emergency change requires enhanced post-change monitoring')
        
        return {
            'complexity': complexity,
            'reversibility': reversibility,
            'timing': timing,
            'dependencies': dependencies,
            'testing': testing,
            'high_risk_flags': high_risk_flags,
            'overall_assessment': 'High Risk' if len(high_risk_flags) >= 2 else 'Moderate Risk',
        }


# ==============================================================================
# 3. CAB SCHEDULER
# ==============================================================================

class CABScheduler:
    """
    Manages CAB meeting schedule, agendas, and change submissions.
    """
    
    def __init__(self):
        from rotasystems.itil_change_settings import CAB_CONFIGURATION
        self.config = CAB_CONFIGURATION
        self.standard_cab = self.config['standard_cab']
    
    def get_next_cab_date(self) -> datetime:
        """
        Calculate next CAB meeting date (every Thursday 14:00 GMT).
        """
        today = datetime.now()
        days_until_thursday = (3 - today.weekday()) % 7  # Thursday = 3
        
        if days_until_thursday == 0 and today.hour >= 14:
            # Today is Thursday after 14:00, next CAB is next week
            days_until_thursday = 7
        
        next_cab = today + timedelta(days=days_until_thursday)
        next_cab = next_cab.replace(hour=14, minute=0, second=0, microsecond=0)
        
        return next_cab
    
    def is_submission_on_time(self, submission_date: datetime) -> bool:
        """
        Check if change submission meets 14-day lead time for next CAB.
        """
        from rotasystems.itil_change_settings import CHANGE_TYPES
        lead_time_days = CHANGE_TYPES['normal']['lead_time_days']
        
        next_cab = self.get_next_cab_date()
        required_submission = next_cab - timedelta(days=lead_time_days)
        
        return submission_date <= required_submission
    
    def generate_cab_agenda(self, changes: List[Dict]) -> Dict:
        """
        Generate CAB meeting agenda with submitted changes.
        
        Args:
            changes: List of change requests with {
                'number': str,
                'short_description': str,
                'risk_score': int,
                'requested_by': str,
            }
        
        Returns:
            Dict with agenda items organized by priority
        """
        agenda_items = self.standard_cab['agenda']
        
        # Sort changes by risk score (highest risk first)
        sorted_changes = sorted(changes, key=lambda x: x.get('risk_score', 0), reverse=True)
        
        return {
            'meeting_date': self.get_next_cab_date().strftime('%Y-%m-%d %H:%M GMT'),
            'duration_minutes': self.standard_cab['meeting_schedule']['duration_minutes'],
            'location': self.standard_cab['meeting_schedule']['location'],
            'standard_agenda': agenda_items,
            'changes_for_review': sorted_changes,
            'total_changes': len(sorted_changes),
            'high_risk_changes': len([c for c in sorted_changes if c.get('risk_score', 0) >= 13]),
        }


# ==============================================================================
# 4. CHANGE CALENDAR HANDLER
# ==============================================================================

class ChangeCalendarHandler:
    """
    Manages change windows and blackout periods.
    Validates change timing against allowed windows.
    """
    
    def __init__(self):
        from rotasystems.itil_change_settings import CHANGE_WINDOWS
        self.config = CHANGE_WINDOWS
    
    def is_in_change_window(
        self,
        proposed_date: datetime,
        change_type: str,
        risk_level: str,
    ) -> Dict:
        """
        Check if proposed date falls within allowed change window.
        
        Returns:
            Dict with {
                'allowed': bool,
                'window_name': str,
                'reason': str,
            }
        """
        # Check blackout periods first
        blackout_check = self.is_blackout_period(proposed_date)
        if blackout_check['is_blackout']:
            if change_type != 'emergency':
                return {
                    'allowed': False,
                    'window_name': None,
                    'reason': f"Blackout period: {blackout_check['blackout_name']}",
                }
        
        # Check against standard windows
        for window in self.config['standard_windows']:
            if change_type not in window['allowed_change_types']:
                continue
            
            if risk_level not in window['risk_levels']:
                continue
            
            # Check day and time
            if window['day'] == 'Any':
                # Emergency window - always allowed
                return {
                    'allowed': True,
                    'window_name': window['name'],
                    'reason': 'Emergency window allows 24/7 changes',
                }
            
            elif window['day'] == 'Saturday':
                if proposed_date.weekday() == 5:  # Saturday = 5
                    # Check time (22:00-06:00)
                    if proposed_date.hour >= 22 or proposed_date.hour < 6:
                        return {
                            'allowed': True,
                            'window_name': window['name'],
                            'reason': 'Within weekly maintenance window (Sat 22:00-06:00)',
                        }
            
            elif window['day'] == 'Monday-Friday':
                if proposed_date.weekday() < 5:  # Mon-Fri = 0-4
                    # Check time (09:00-17:00)
                    if 9 <= proposed_date.hour < 17:
                        return {
                            'allowed': True,
                            'window_name': window['name'],
                            'reason': 'Within low-risk business hours window',
                        }
        
        return {
            'allowed': False,
            'window_name': None,
            'reason': f'No change window available for {change_type} change with {risk_level} risk on {proposed_date.strftime("%A %H:%M")}',
        }
    
    def is_blackout_period(self, proposed_date: datetime) -> Dict:
        """
        Check if date falls within blackout period.
        
        Returns:
            Dict with {
                'is_blackout': bool,
                'blackout_name': str,
                'reason': str,
                'allowed_changes': List[str],
            }
        """
        for blackout in self.config['blackout_periods']:
            # Handle TBD dates (payroll, inspections)
            if 'TBD' in blackout['start_date']:
                # For payroll: 25th-28th of each month
                if blackout['name'] == 'Monthly Payroll Processing':
                    if 25 <= proposed_date.day <= 28:
                        return {
                            'is_blackout': True,
                            'blackout_name': blackout['name'],
                            'reason': blackout['reason'],
                            'allowed_changes': blackout['allowed_changes'],
                        }
                continue
            
            # Parse fixed dates
            start = datetime.strptime(blackout['start_date'], '%Y-%m-%d')
            end = datetime.strptime(blackout['end_date'], '%Y-%m-%d')
            
            if start <= proposed_date <= end:
                return {
                    'is_blackout': True,
                    'blackout_name': blackout['name'],
                    'reason': blackout['reason'],
                    'allowed_changes': blackout['allowed_changes'],
                }
        
        return {
            'is_blackout': False,
            'blackout_name': None,
            'reason': 'Not in blackout period',
            'allowed_changes': ['standard', 'normal', 'emergency'],
        }
    
    def get_next_available_window(self, change_type: str, risk_level: str) -> datetime:
        """
        Find next available change window for given change type and risk.
        """
        current_date = datetime.now()
        
        # For emergency changes, return immediately
        if change_type == 'emergency':
            return current_date
        
        # For normal/standard changes, find next Saturday 22:00
        days_until_saturday = (5 - current_date.weekday()) % 7
        if days_until_saturday == 0 and current_date.hour >= 22:
            days_until_saturday = 7
        
        next_window = current_date + timedelta(days=days_until_saturday)
        next_window = next_window.replace(hour=22, minute=0, second=0, microsecond=0)
        
        # Check if in blackout period
        blackout_check = self.is_blackout_period(next_window)
        if blackout_check['is_blackout'] and change_type not in blackout_check['allowed_changes']:
            # Skip to next week
            next_window = next_window + timedelta(days=7)
        
        return next_window


# ==============================================================================
# 5. POST-IMPLEMENTATION REVIEW (PIR) HANDLER
# ==============================================================================

class PIRHandler:
    """
    Manages Post-Implementation Reviews.
    Tracks change success metrics and lessons learned.
    """
    
    def __init__(self):
        from rotasystems.itil_change_settings import POST_IMPLEMENTATION_REVIEW
        self.config = POST_IMPLEMENTATION_REVIEW
    
    def evaluate_change_success(
        self,
        change_number: str,
        implemented_on_time: bool,
        downtime_actual_minutes: int,
        downtime_planned_minutes: int,
        rollback_required: bool,
        user_issues_count: int,
        performance_acceptable: bool,
    ) -> Dict:
        """
        Evaluate change success based on PIR criteria.
        
        Returns:
            Dict with {
                'rating': str,  # 'successful', 'successful_with_issues', etc.
                'success_metrics': Dict,
                'recommendations': List[str],
            }
        """
        success_criteria = self.config['review_criteria']['success_metrics']
        
        # Evaluate each criterion
        on_time = implemented_on_time
        within_downtime = downtime_actual_minutes <= downtime_planned_minutes
        no_rollback = not rollback_required
        minimal_issues = user_issues_count < 5
        performance_ok = performance_acceptable
        
        # Determine rating
        if all([on_time, within_downtime, no_rollback, minimal_issues, performance_ok]):
            rating = 'successful'
        elif no_rollback and performance_ok:
            rating = 'successful_with_issues'
        elif no_rollback:
            rating = 'partially_successful'
        else:
            rating = 'failed'
        
        # Generate recommendations
        recommendations = []
        
        if not on_time:
            recommendations.append('Improve change planning - actual time exceeded window')
        
        if not within_downtime:
            recommendations.append(f'Downtime exceeded estimate by {downtime_actual_minutes - downtime_planned_minutes} minutes - review estimation process')
        
        if rollback_required:
            recommendations.append('Rollback was required - enhance testing in staging environment')
        
        if user_issues_count >= 5:
            recommendations.append(f'{user_issues_count} user issues reported - improve UAT and communication')
        
        if not performance_ok:
            recommendations.append('Performance degraded post-change - add performance testing to change checklist')
        
        return {
            'change_number': change_number,
            'rating': rating,
            'rating_description': self.config['review_criteria']['rating_scale'][rating],
            'success_metrics': {
                'implemented_on_time': on_time,
                'downtime_within_estimate': within_downtime,
                'downtime_actual_minutes': downtime_actual_minutes,
                'downtime_planned_minutes': downtime_planned_minutes,
                'rollback_required': rollback_required,
                'user_issues_count': user_issues_count,
                'performance_acceptable': performance_ok,
            },
            'recommendations': recommendations,
        }
    
    def create_pir_document(
        self,
        change_number: str,
        success_evaluation: Dict,
        what_went_well: str,
        what_went_wrong: str,
        what_to_improve: str,
        runbook_updates: Optional[str] = None,
    ) -> Dict:
        """
        Create Post-Implementation Review document.
        
        Returns:
            PIR document dict for ServiceNow attachment
        """
        pir_doc = {
            'change_number': change_number,
            'pir_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'reviewer': 'CGI Change Manager',  # TBD - actual user
            'success_evaluation': success_evaluation,
            'lessons_learned': {
                'what_went_well': what_went_well,
                'what_went_wrong': what_went_wrong,
                'what_to_improve': what_to_improve,
            },
            'knowledge_management': {
                'runbook_updates': runbook_updates or 'No updates required',
                'standard_change_candidate': success_evaluation['rating'] == 'successful' and 'Yes - consider creating Standard Change SOP',
            },
        }
        
        logger.info(f"PIR document created for change {change_number}: {success_evaluation['rating']}")
        return pir_doc


# ==============================================================================
# ORCHESTRATOR
# ==============================================================================

class ChangeManagementOrchestrator:
    """
    Orchestrates full change management lifecycle.
    Entry point for creating and managing changes.
    """
    
    def __init__(self):
        self.change_handler = ChangeRequestHandler()
        self.risk_handler = RiskAssessmentHandler()
        self.cab_scheduler = CABScheduler()
        self.calendar_handler = ChangeCalendarHandler()
        self.pir_handler = PIRHandler()
    
    def submit_normal_change(
        self,
        short_description: str,
        description: str,
        category: str,
        probability: str,
        impact: str,
        proposed_date: datetime,
        duration_hours: int,
        backout_plan: str,
        test_plan: str,
        requested_by: str,
    ) -> Dict:
        """
        Submit normal change with full workflow validation.
        
        Returns:
            Dict with change request details and validation results
        """
        # Step 1: Risk assessment
        risk_assessment = self.risk_handler.calculate_risk_score(probability, impact)
        
        # Step 2: Check CAB submission timing
        if not self.cab_scheduler.is_submission_on_time(datetime.now()):
            return {
                'success': False,
                'reason': f'Late submission - must be 14 days before next CAB ({self.cab_scheduler.get_next_cab_date().strftime("%Y-%m-%d")})',
            }
        
        # Step 3: Validate change window
        window_check = self.calendar_handler.is_in_change_window(
            proposed_date,
            'normal',
            risk_assessment['risk_level'],
        )
        
        if not window_check['allowed']:
            # Suggest next available window
            next_window = self.calendar_handler.get_next_available_window('normal', risk_assessment['risk_level'])
            return {
                'success': False,
                'reason': window_check['reason'],
                'suggested_window': next_window.strftime('%Y-%m-%d %H:%M'),
            }
        
        # Step 4: Create change request in ServiceNow
        end_date = proposed_date + timedelta(hours=duration_hours)
        
        change_request = self.change_handler.create_change_request(
            change_type='normal',
            short_description=short_description,
            description=description,
            category=category,
            risk_score=risk_assessment['risk_score'],
            impact_score=risk_assessment['impact_score'],
            start_date=proposed_date,
            end_date=end_date,
            backout_plan=backout_plan,
            test_plan=test_plan,
            requested_by=requested_by,
        )
        
        return {
            'success': True,
            'change_number': change_request['number'],
            'sys_id': change_request['sys_id'],
            'risk_assessment': risk_assessment,
            'change_window': window_check['window_name'],
            'next_cab_date': self.cab_scheduler.get_next_cab_date().strftime('%Y-%m-%d %H:%M'),
            'recommended_mitigations': self.risk_handler.recommend_mitigation(risk_assessment['risk_score'], category),
        }
