"""
ESB Message Handlers
NHS Staff Rota Management System

Event handlers for processing inbound/outbound ESB messages.

Author: NHS HSCP Development Team
Date: January 7, 2026
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import User, Shift, LeaveRequest, ComplianceViolation
from .models_multi_home import CareHome

logger = logging.getLogger(__name__)
User = get_user_model()


class ESBMessageHandler:
    """Base class for ESB message handlers"""
    
    @staticmethod
    def validate_schema(message: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate message against JSON schema"""
        from jsonschema import validate, ValidationError
        try:
            validate(instance=message, schema=schema)
            return True
        except ValidationError as e:
            logger.error(f"Schema validation failed: {e}")
            return False
    
    @staticmethod
    def publish_event(exchange: str, routing_key: str, message: Dict[str, Any]):
        """Publish event to ESB"""
        from .esb_publisher import ESBPublisher
        publisher = ESBPublisher()
        publisher.publish(exchange, routing_key, message)


# ============================================================================
# LDAP SYNC HANDLERS
# ============================================================================

def handle_ldap_user_created(message: Dict[str, Any]):
    """
    Handle LDAP user creation event
    Creates corresponding Django user account
    """
    try:
        with transaction.atomic():
            user = User.objects.create(
                username=message['username'],
                email=message['email'],
                first_name=message['first_name'],
                last_name=message['last_name'],
                sap=message.get('sap_number'),
                is_active=True,
            )
            logger.info(f"Created user from LDAP: {user.username}")
            
            # Publish confirmation event
            ESBMessageHandler.publish_event(
                'nhs.rota.integration',
                'ldap.user_synced',
                {
                    'user_id': user.id,
                    'username': user.username,
                    'timestamp': datetime.now().isoformat(),
                }
            )
    except Exception as e:
        logger.error(f"Failed to create user from LDAP: {e}")
        raise


def handle_ldap_user_updated(message: Dict[str, Any]):
    """Handle LDAP user update event"""
    try:
        user = User.objects.get(username=message['username'])
        user.email = message.get('email', user.email)
        user.first_name = message.get('first_name', user.first_name)
        user.last_name = message.get('last_name', user.last_name)
        user.save()
        logger.info(f"Updated user from LDAP: {user.username}")
    except User.DoesNotExist:
        logger.warning(f"User not found for LDAP update: {message['username']}")
    except Exception as e:
        logger.error(f"Failed to update user from LDAP: {e}")
        raise


def handle_ldap_user_deleted(message: Dict[str, Any]):
    """Handle LDAP user deletion event"""
    try:
        user = User.objects.get(username=message['username'])
        user.is_active = False
        user.save()
        logger.info(f"Deactivated user from LDAP: {user.username}")
    except User.DoesNotExist:
        logger.warning(f"User not found for LDAP deletion: {message['username']}")
    except Exception as e:
        logger.error(f"Failed to deactivate user from LDAP: {e}")
        raise


# ============================================================================
# PAYROLL HANDLERS
# ============================================================================

def handle_payroll_export(message: Dict[str, Any]):
    """
    Handle payroll export request
    Generate and send payroll data
    """
    try:
        from .utils_payroll import generate_payroll_export
        
        start_date = datetime.fromisoformat(message['start_date'])
        end_date = datetime.fromisoformat(message['end_date'])
        
        payroll_data = generate_payroll_export(start_date, end_date)
        
        # Publish payroll data
        ESBMessageHandler.publish_event(
            'nhs.rota.integration',
            'payroll.export_completed',
            {
                'request_id': message.get('request_id'),
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'record_count': len(payroll_data),
                'data': payroll_data,
                'timestamp': datetime.now().isoformat(),
            }
        )
        logger.info(f"Payroll export completed: {len(payroll_data)} records")
    except Exception as e:
        logger.error(f"Payroll export failed: {e}")
        raise


# ============================================================================
# ITSM HANDLERS
# ============================================================================

def handle_itsm_incident(message: Dict[str, Any]):
    """Handle ITSM incident creation notification"""
    try:
        # Log incident for audit
        logger.info(f"ITSM Incident: {message.get('incident_number')} - {message.get('description')}")
        
        # If critical incident, notify managers
        if message.get('priority') == 'P1':
            from .tasks import notify_managers_critical_incident
            notify_managers_critical_incident.delay(message)
    except Exception as e:
        logger.error(f"Failed to handle ITSM incident: {e}")


# ============================================================================
# EMAIL HANDLERS
# ============================================================================

def handle_email_delivery(message: Dict[str, Any]):
    """Handle email delivery confirmation"""
    try:
        logger.info(f"Email delivered: {message.get('message_id')} to {message.get('recipient')}")
    except Exception as e:
        logger.error(f"Failed to handle email delivery: {e}")


def handle_email_failure(message: Dict[str, Any]):
    """Handle email delivery failure"""
    try:
        logger.error(f"Email failed: {message.get('message_id')} - {message.get('error')}")
        
        # Retry or escalate
        if message.get('retry_count', 0) < 3:
            from .tasks import retry_email_delivery
            retry_email_delivery.delay(message)
    except Exception as e:
        logger.error(f"Failed to handle email failure: {e}")


# ============================================================================
# SIEM HANDLERS
# ============================================================================

def handle_siem_event(message: Dict[str, Any]):
    """Handle SIEM security event"""
    try:
        event_type = message.get('event_type')
        severity = message.get('severity')
        
        logger.info(f"SIEM Event: {event_type} (severity: {severity})")
        
        # If critical security event, escalate
        if severity == 'CRITICAL':
            from .tasks import escalate_security_event
            escalate_security_event.delay(message)
    except Exception as e:
        logger.error(f"Failed to handle SIEM event: {e}")
