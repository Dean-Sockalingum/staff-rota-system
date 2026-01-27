"""
ITSM Integration for Automated Incident Ticket Creation
=======================================================

Integrates with CGI ServiceNow/Remedy for automated incident management.

Features:
- Automatic ticket creation for P1-P4 incidents
- Ticket status tracking and updates
- Escalation workflow automation
- SLA compliance monitoring
- Incident correlation and deduplication

Author: Staff Rota Development Team
Date: January 2026
"""

import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from functools import lru_cache

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("requests library not installed. ITSM integration disabled.")

from django.core.cache import cache
from rotasystems import siem_settings


logger = logging.getLogger(__name__)


class ITSMClient:
    """
    Client for CGI ServiceNow/Remedy ITSM platform.
    
    Handles ticket creation, updates, and escalation workflows.
    """
    
    def __init__(self):
        self.config = siem_settings.ITSM_CONFIG
        self.platform = self.config['platform']
        self.api_url = self.config['api_url']
        self.api_key = self.config['api_key']
        self.username = self.config['username']
        self.password = self.config['password']
        
        # Deduplication cache (prevent duplicate tickets for same incident)
        self.dedup_window = 300  # 5 minutes
        
        if not REQUESTS_AVAILABLE:
            logger.error("ITSM integration disabled: requests library not available")
    
    def create_incident(self, incident_type: str, severity: str, 
                       description: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Create incident ticket in ServiceNow/Remedy.
        
        Args:
            incident_type: Type of incident (e.g., 'sql_injection_attempt')
            severity: P1-P4 severity level
            description: Detailed incident description
            context: Additional context dictionary
            
        Returns:
            Ticket ID (e.g., 'INC0012345') or None if creation failed
        """
        if not REQUESTS_AVAILABLE:
            logger.error("Cannot create incident: requests library not available")
            return None
        
        # Check for duplicate incidents (deduplication)
        dedup_key = self._generate_dedup_key(incident_type, severity, context)
        if self._is_duplicate_incident(dedup_key):
            logger.info(f"Skipping duplicate incident: {incident_type} ({severity})")
            return cache.get(dedup_key)  # Return existing ticket ID
        
        # Build ticket payload
        payload = self._build_ticket_payload(incident_type, severity, description, context)
        
        try:
            # Send API request
            if self.platform == 'servicenow':
                ticket_id = self._create_servicenow_ticket(payload)
            elif self.platform == 'remedy':
                ticket_id = self._create_remedy_ticket(payload)
            else:
                logger.error(f"Unsupported ITSM platform: {self.platform}")
                return None
            
            # Cache ticket ID for deduplication
            if ticket_id:
                cache.set(dedup_key, ticket_id, self.dedup_window)
                logger.info(f"Created {severity} incident ticket: {ticket_id} for {incident_type}")
            
            return ticket_id
        
        except Exception as e:
            logger.error(f"Failed to create ITSM ticket: {e}", exc_info=True)
            return None
    
    def update_incident(self, ticket_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update existing incident ticket.
        
        Args:
            ticket_id: Ticket ID (e.g., 'INC0012345')
            updates: Dictionary of fields to update
            
        Returns:
            True if update succeeded, False otherwise
        """
        if not REQUESTS_AVAILABLE:
            return False
        
        try:
            if self.platform == 'servicenow':
                return self._update_servicenow_ticket(ticket_id, updates)
            elif self.platform == 'remedy':
                return self._update_remedy_ticket(ticket_id, updates)
            else:
                logger.error(f"Unsupported ITSM platform: {self.platform}")
                return False
        
        except Exception as e:
            logger.error(f"Failed to update ticket {ticket_id}: {e}", exc_info=True)
            return False
    
    def get_incident_status(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve incident ticket status.
        
        Args:
            ticket_id: Ticket ID (e.g., 'INC0012345')
            
        Returns:
            Ticket status dictionary or None if retrieval failed
        """
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            if self.platform == 'servicenow':
                return self._get_servicenow_ticket(ticket_id)
            elif self.platform == 'remedy':
                return self._get_remedy_ticket(ticket_id)
            else:
                logger.error(f"Unsupported ITSM platform: {self.platform}")
                return None
        
        except Exception as e:
            logger.error(f"Failed to retrieve ticket {ticket_id}: {e}", exc_info=True)
            return None
    
    def escalate_incident(self, ticket_id: str, escalation_level: int, reason: str) -> bool:
        """
        Escalate incident to higher support tier.
        
        Args:
            ticket_id: Ticket ID to escalate
            escalation_level: 1-3 (Team Lead → Manager → Director)
            reason: Escalation reason
            
        Returns:
            True if escalation succeeded, False otherwise
        """
        escalation_groups = {
            1: 'CGI Team Lead',
            2: 'CGI Service Delivery Manager',
            3: 'CGI Incident Manager',
        }
        
        updates = {
            'assignment_group': escalation_groups.get(escalation_level, 'CGI Team Lead'),
            'work_notes': f"ESCALATION LEVEL {escalation_level}: {reason}",
            'urgency': '1',  # Increase urgency
        }
        
        success = self.update_incident(ticket_id, updates)
        
        if success:
            logger.warning(f"Escalated ticket {ticket_id} to level {escalation_level}: {reason}")
        
        return success
    
    def _build_ticket_payload(self, incident_type: str, severity: str,
                            description: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build ticket payload for ITSM API."""
        template = self.config['templates'][severity]
        context = context or {}
        
        # Build short description (subject line)
        short_description = f"{template['short_description_prefix']} {incident_type}"
        if 'user_id' in context:
            short_description += f" (User: {context['user_id']})"
        
        # Build detailed description
        detailed_description = f"""
INCIDENT TYPE: {incident_type}
SEVERITY: {severity}
TIMESTAMP: {datetime.utcnow().isoformat()}Z

DESCRIPTION:
{description}

CONTEXT:
"""
        for key, value in context.items():
            detailed_description += f"- {key}: {value}\n"
        
        # Build payload
        payload = {
            'short_description': short_description[:160],  # Max length
            'description': detailed_description,
            'priority': template['priority'],
            'impact': template['impact'],
            'urgency': template['urgency'],
            'assignment_group': self.config['assignment_group'],
            'category': self.config['category'],
            'subcategory': self.config['subcategory'],
        }
        
        # Add custom fields
        payload.update(self.config['custom_fields'])
        
        # Add severity-specific fields
        if severity == 'P1':
            payload['caller_id'] = context.get('user_id', 'SYSTEM')
            payload['contact_type'] = 'Alert'
            payload['notify'] = '1'  # Send notifications
        
        return payload
    
    def _create_servicenow_ticket(self, payload: Dict[str, Any]) -> Optional[str]:
        """Create ticket in ServiceNow."""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        # Authentication
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            auth = None
        else:
            auth = (self.username, self.password)
        
        response = requests.post(
            self.api_url,
            headers=headers,
            auth=auth,
            json=payload,
            timeout=10,
        )
        
        if response.status_code in (200, 201):
            result = response.json()
            ticket_id = result.get('result', {}).get('number')
            return ticket_id
        else:
            logger.error(f"ServiceNow API error {response.status_code}: {response.text}")
            return None
    
    def _create_remedy_ticket(self, payload: Dict[str, Any]) -> Optional[str]:
        """Create ticket in Remedy (BMC Helix)."""
        # Remedy uses different API endpoint structure
        remedy_url = self.api_url.replace('/api/now/', '/api/arsys/v1/entry/')
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'AR-JWT {self.api_key}',
        }
        
        # Map ServiceNow fields to Remedy fields
        remedy_payload = {
            'values': {
                'z1D_Action': 'CREATE',
                'Description': payload['description'],
                'Impact': payload['impact'],
                'Urgency': payload['urgency'],
                'Assigned_Group': payload['assignment_group'],
                'Categorization_Tier_1': payload['category'],
                'Categorization_Tier_2': payload['subcategory'],
            }
        }
        
        response = requests.post(
            remedy_url,
            headers=headers,
            json=remedy_payload,
            timeout=10,
        )
        
        if response.status_code in (200, 201):
            result = response.json()
            ticket_id = result.get('values', {}).get('Incident Number')
            return ticket_id
        else:
            logger.error(f"Remedy API error {response.status_code}: {response.text}")
            return None
    
    def _update_servicenow_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> bool:
        """Update ServiceNow ticket."""
        # Get ticket sys_id first
        sys_id = self._get_servicenow_sys_id(ticket_id)
        if not sys_id:
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            auth = None
        else:
            auth = (self.username, self.password)
        
        url = f"{self.api_url}/{sys_id}"
        
        response = requests.patch(
            url,
            headers=headers,
            auth=auth,
            json=updates,
            timeout=10,
        )
        
        return response.status_code == 200
    
    def _update_remedy_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> bool:
        """Update Remedy ticket."""
        remedy_url = f"{self.api_url}/{ticket_id}"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'AR-JWT {self.api_key}',
        }
        
        remedy_updates = {'values': updates}
        
        response = requests.put(
            remedy_url,
            headers=headers,
            json=remedy_updates,
            timeout=10,
        )
        
        return response.status_code == 200
    
    def _get_servicenow_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get ServiceNow ticket details."""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            auth = None
        else:
            auth = (self.username, self.password)
        
        params = {'sysparm_query': f'number={ticket_id}'}
        
        response = requests.get(
            self.api_url,
            headers=headers,
            auth=auth,
            params=params,
            timeout=10,
        )
        
        if response.status_code == 200:
            result = response.json()
            tickets = result.get('result', [])
            return tickets[0] if tickets else None
        
        return None
    
    def _get_remedy_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get Remedy ticket details."""
        remedy_url = f"{self.api_url}/{ticket_id}"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'AR-JWT {self.api_key}',
        }
        
        response = requests.get(
            remedy_url,
            headers=headers,
            timeout=10,
        )
        
        if response.status_code == 200:
            return response.json()
        
        return None
    
    def _get_servicenow_sys_id(self, ticket_id: str) -> Optional[str]:
        """Get ServiceNow sys_id for ticket number."""
        ticket = self._get_servicenow_ticket(ticket_id)
        return ticket.get('sys_id') if ticket else None
    
    def _generate_dedup_key(self, incident_type: str, severity: str, 
                           context: Optional[Dict[str, Any]]) -> str:
        """Generate deduplication key for incident."""
        # Use incident type, severity, and relevant context for dedup
        dedup_data = f"{incident_type}:{severity}"
        
        if context:
            # Add user/IP/resource for more specific dedup
            dedup_data += f":{context.get('user_id', '')}"
            dedup_data += f":{context.get('ip_address', '')}"
            dedup_data += f":{context.get('resource', '')}"
        
        # Hash to fixed-length key
        dedup_hash = hashlib.md5(dedup_data.encode()).hexdigest()
        return f"itsm_dedup:{dedup_hash}"
    
    def _is_duplicate_incident(self, dedup_key: str) -> bool:
        """Check if incident is duplicate within dedup window."""
        return cache.get(dedup_key) is not None


# Global ITSM client instance
itsm_client = ITSMClient()


def create_incident_ticket(incident_type: str, severity: str, 
                          context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Create incident ticket in CGI ITSM system.
    
    High-level wrapper for SIEM integration.
    
    Args:
        incident_type: Type of incident (e.g., 'database_failure')
        severity: P1-P4 severity level
        context: Additional context dictionary
        
    Returns:
        Ticket ID or None if creation failed
    """
    # Build description from incident type and severity
    severity_info = siem_settings.INCIDENT_SEVERITY_LEVELS.get(severity, {})
    description = f"{severity_info.get('name', severity)} severity incident: {incident_type}"
    
    if context and 'error_message' in context:
        description += f"\n\nError: {context['error_message']}"
    
    # Create ticket
    ticket_id = itsm_client.create_incident(
        incident_type=incident_type,
        severity=severity,
        description=description,
        context=context,
    )
    
    # Send notifications based on severity
    if ticket_id and severity in ('P1', 'P2'):
        _send_incident_notifications(ticket_id, incident_type, severity, context)
    
    return ticket_id


def _send_incident_notifications(ticket_id: str, incident_type: str, 
                                severity: str, context: Optional[Dict[str, Any]]):
    """
    Send notifications for high-severity incidents.
    
    Args:
        ticket_id: Created ticket ID
        incident_type: Type of incident
        severity: P1 or P2
        context: Incident context
    """
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        # Get escalation procedures
        escalation = siem_settings.ESCALATION_PROCEDURES.get(f'{severity}_{"CRITICAL" if severity == "P1" else "HIGH"}', {})
        
        # Build notification message
        subject = f"[{severity}] Staff Rota Incident: {incident_type} - Ticket {ticket_id}"
        
        message = f"""
{severity} Incident Alert
==================

Ticket ID: {ticket_id}
Incident Type: {incident_type}
Severity: {severity}
Timestamp: {datetime.utcnow().isoformat()}Z

Context:
"""
        if context:
            for key, value in context.items():
                message += f"- {key}: {value}\n"
        
        message += f"\n\nEscalation Procedure:\n"
        for action in escalation.get('immediate', []):
            message += f"- {action}\n"
        
        message += f"\n\nServiceNow Ticket: {itsm_client.api_url.replace('/api/now/table/incident', '')}/nav_to.do?uri=incident.do?sysparm_query=number={ticket_id}"
        
        # Send email to SOC team
        soc_config = siem_settings.CGI_SOC_CONFIG['primary_soc']
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[soc_config['email']],
            fail_silently=True,
        )
        
        logger.info(f"Sent {severity} incident notification for ticket {ticket_id}")
    
    except Exception as e:
        logger.error(f"Failed to send incident notifications: {e}", exc_info=True)
