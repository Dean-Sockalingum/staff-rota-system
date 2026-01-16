"""
Auto-Send Overtime Offers Service
Automatically sends OT offers to top-ranked staff with escalation to agency
Part of Task 1: Smart Staff Availability Matching System
"""

from django.utils import timezone
from django.db import transaction
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from typing import List, Dict, Optional
import logging

from scheduling.models import Shift, User
from scheduling.models_automated_workflow import (
    OvertimeOfferBatch, 
    OvertimeOffer
)
from scheduling.models_overtime import StaffOvertimePreference
from scheduling.utils_overtime_intelligence import OvertimeRanker

logger = logging.getLogger(__name__)


class OvertimeOfferService:
    """
    Service for automatically sending OT offers to best-matched staff
    with intelligent escalation to agency if no response.
    """
    
    DEFAULT_NUM_OFFERS = 3
    DEFAULT_ESCALATION_TIMEOUT = 30  # minutes
    
    @classmethod
    @transaction.atomic
    def create_and_send_offers(
        cls,
        shift: Shift,
        num_offers: int = DEFAULT_NUM_OFFERS,
        escalation_timeout: int = DEFAULT_ESCALATION_TIMEOUT,
        created_by: Optional[User] = None
    ) -> OvertimeOfferBatch:
        """
        Find best matches, create batch, and send offers automatically.
        
        Args:
            shift: Shift needing coverage
            num_offers: Number of offers to send (default 3)
            escalation_timeout: Minutes before escalating to agency (default 30)
            created_by: User who initiated the batch (optional)
            
        Returns:
            OvertimeOfferBatch instance
        """
        # Step 1: Rank available staff
        ranker = OvertimeRanker(
            shift_date=shift.date,
            shift_type=shift.shift_type.shift_type,
            care_home=shift.care_home,
            unit=shift.unit
        )
        
        top_candidates = ranker.get_top_candidates(limit=num_offers)
        
        if not top_candidates:
            logger.warning(f"No available staff found for shift {shift.id}")
            # TODO: Trigger immediate agency escalation
            return None
        
        # Step 2: Create batch
        batch = OvertimeOfferBatch.objects.create(
            shift=shift,
            created_by=created_by,
            num_offers_sent=len(top_candidates),
            escalation_timeout_minutes=escalation_timeout,
            status='PENDING'
        )
        
        # Step 3: Create individual offers and send
        for rank, candidate in enumerate(top_candidates, start=1):
            offer = cls._create_offer(batch, candidate, rank)
            cls._send_offer_notification(offer)
        
        logger.info(
            f"Created OT batch {batch.id} with {len(top_candidates)} offers "
            f"for shift {shift.id}"
        )
        
        return batch
    
    @classmethod
    def _create_offer(
        cls,
        batch: OvertimeOfferBatch,
        candidate: Dict,
        rank: int
    ) -> OvertimeOffer:
        """
        Create individual offer record.
        
        Args:
            batch: Parent batch
            candidate: Dict from OvertimeRanker with staff and scores
            rank: Position in ranking (1-based)
            
        Returns:
            OvertimeOffer instance
        """
        # Extract matching details
        staff = candidate['staff']
        total_score = candidate['total_score']
        breakdown = candidate['breakdown']
        
        # Generate recommendation text
        recommendation = cls._generate_recommendation(breakdown, total_score)
        
        # Determine contact method
        contact_method = 'SMS'  # Default
        if hasattr(staff, 'overtime_preference'):
            pref = staff.overtime_preference
            if pref.preferred_contact_method:
                contact_method = pref.preferred_contact_method
        
        offer = OvertimeOffer.objects.create(
            batch=batch,
            staff=staff,
            rank_position=rank,
            match_score=total_score,
            match_breakdown=breakdown,
            recommendation=recommendation,
            contact_method=contact_method,
            response='PENDING'
        )
        
        return offer
    
    @classmethod
    def _generate_recommendation(cls, breakdown: Dict, total_score: float) -> str:
        """Generate human-readable recommendation text."""
        if total_score >= 90:
            return "Excellent match - highly recommended"
        elif total_score >= 80:
            strengths = []
            if breakdown.get('availability', 0) >= 90:
                strengths.append("high availability")
            if breakdown.get('acceptance_rate', 0) >= 90:
                strengths.append("reliable responder")
            if breakdown.get('fairness', 0) >= 90:
                strengths.append("low recent OT")
            return f"Strong match - {', '.join(strengths) if strengths else 'recommended'}"
        elif total_score >= 70:
            return "Good match - suitable for coverage"
        else:
            return "Acceptable match - backup option"
    
    @classmethod
    def _send_offer_notification(cls, offer: OvertimeOffer):
        """
        Send notification to staff member about OT offer.
        
        Supports multiple channels:
        - SMS (default)
        - Email
        - Mobile App Push (if configured)
        """
        shift = offer.batch.shift
        staff = offer.staff
        
        # Build message content
        message = cls._build_offer_message(offer)
        offer.message_sent = message
        offer.save()
        
        # Send via appropriate channel
        try:
            if offer.contact_method == 'SMS':
                cls._send_sms(staff, message)
            elif offer.contact_method == 'EMAIL':
                cls._send_email(staff, offer, message)
            elif offer.contact_method == 'APP':
                cls._send_push_notification(staff, message)
            
            logger.info(f"Sent OT offer to {staff.full_name} via {offer.contact_method}")
            
        except Exception as e:
            logger.error(f"Failed to send offer to {staff.full_name}: {str(e)}")
    
    @classmethod
    def _build_offer_message(cls, offer: OvertimeOffer) -> str:
        """Build SMS/notification message text."""
        shift = offer.batch.shift
        
        # Format shift details
        shift_date = shift.date.strftime('%A, %d %B')
        shift_time = f"{shift.shift_type.start_time} - {shift.shift_type.end_time}"
        location = f"{shift.unit.name}, {shift.care_home.name}"
        
        # Calculate hourly rate (with OT premium)
        base_rate = shift.hourly_rate or 12.50
        ot_rate = base_rate * 1.5  # Time and a half
        
        message = (
            f"🔔 OVERTIME OPPORTUNITY\n\n"
            f"Date: {shift_date}\n"
            f"Time: {shift_time}\n"
            f"Location: {location}\n"
            f"Rate: £{ot_rate:.2f}/hour\n\n"
            f"You've been selected as a top match!\n"
            f"Reply YES to accept or NO to decline.\n\n"
            f"Offer expires in {offer.batch.escalation_timeout_minutes} minutes."
        )
        
        return message
    
    @classmethod
    def _send_sms(cls, staff: User, message: str):
        """Send SMS via configured SMS provider."""
        # TODO: Integrate with SMS provider (Twilio, AWS SNS, etc.)
        phone = getattr(staff, 'phone', None) or getattr(
            staff.overtime_preference, 'phone_number', None
        )
        
        if not phone:
            logger.warning(f"No phone number for {staff.full_name}")
            return
        
        # Placeholder - implement actual SMS sending
        logger.info(f"SMS to {phone}: {message}")
    
    @classmethod
    def _send_email(cls, staff: User, offer: OvertimeOffer, message: str):
        """Send email notification."""
        shift = offer.batch.shift
        
        subject = f"Overtime Opportunity - {shift.date.strftime('%d/%m/%Y')}"
        
        # Render HTML email template
        html_message = render_to_string('scheduling/emails/ot_offer.html', {
            'staff': staff,
            'offer': offer,
            'shift': shift,
            'message': message,
        })
        
        send_mail(
            subject=subject,
            message=message,  # Plain text fallback
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[staff.email],
            html_message=html_message,
            fail_silently=False
        )
    
    @classmethod
    def _send_push_notification(cls, staff: User, message: str):
        """Send mobile app push notification."""
        # TODO: Integrate with Firebase Cloud Messaging or similar
        logger.info(f"Push notification to {staff.full_name}: {message}")
    
    @classmethod
    def process_response(
        cls,
        offer_id: int,
        response: str,
        decline_reason: str = ''
    ) -> bool:
        """
        Process staff response to OT offer.
        
        Args:
            offer_id: OvertimeOffer ID
            response: 'ACCEPTED' or 'DECLINED'
            decline_reason: Optional reason if declined
            
        Returns:
            True if processed successfully
        """
        try:
            offer = OvertimeOffer.objects.get(id=offer_id)
            
            if response == 'ACCEPTED':
                offer.mark_accepted()
                # Assign staff to shift
                offer.batch.shift.assigned_users.add(offer.staff)
                logger.info(f"OT offer {offer_id} accepted by {offer.staff.full_name}")
                return True
                
            elif response == 'DECLINED':
                offer.mark_declined(decline_reason)
                logger.info(f"OT offer {offer_id} declined by {offer.staff.full_name}")
                return True
                
        except OvertimeOffer.DoesNotExist:
            logger.error(f"OT offer {offer_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error processing OT response: {str(e)}")
            return False
    
    @classmethod
    def check_escalation(cls, batch_id: int) -> bool:
        """
        Check if batch should be escalated to agency.
        Called by scheduled task every minute.
        
        Args:
            batch_id: OvertimeOfferBatch ID
            
        Returns:
            True if escalated
        """
        try:
            batch = OvertimeOfferBatch.objects.get(id=batch_id)
            
            # Skip if not pending
            if batch.status != 'PENDING':
                return False
            
            # Check if accepted
            if batch.has_acceptance():
                return False
            
            # Check if all declined
            if batch.all_declined():
                cls._escalate_to_agency(batch, 'ALL_DECLINED')
                return True
            
            # Check if timeout expired
            if batch.is_expired():
                cls._escalate_to_agency(batch, 'TIMEOUT')
                return True
            
            return False
            
        except OvertimeOfferBatch.DoesNotExist:
            logger.error(f"Batch {batch_id} not found")
            return False
    
    @classmethod
    @transaction.atomic
    def _escalate_to_agency(cls, batch: OvertimeOfferBatch, reason: str):
        """
        Escalate to agency after no staff response.
        
        Args:
            batch: OvertimeOfferBatch to escalate
            reason: 'TIMEOUT' or 'ALL_DECLINED'
        """
        # Update batch status
        batch.status = 'ESCALATED'
        batch.escalation_triggered_by = reason
        batch.escalated_at = timezone.now()
        
        # Create agency request
        from scheduling.models import AgencyRequest
        
        shift = batch.shift
        agency_request = AgencyRequest.objects.create(
            shift=shift,
            requested_at=timezone.now(),
            requested_by=batch.created_by,
            urgency='HIGH',
            reason=f"Auto-escalated after {reason}: No staff accepted OT offer",
            status='PENDING'
        )
        
        batch.agency_request = agency_request
        batch.save()
        
        # Mark all pending offers as expired
        batch.offers.filter(response='PENDING').update(response='EXPIRED')
        
        logger.warning(
            f"Escalated batch {batch.id} to agency (reason: {reason}). "
            f"Created agency request {agency_request.id}"
        )
        
        # TODO: Send agency request email/notification


def auto_send_ot_offers(shift_id: int, num_offers: int = 3) -> Optional[OvertimeOfferBatch]:
    """
    Convenience function to auto-send OT offers for a shift.
    
    Args:
        shift_id: Shift ID needing coverage
        num_offers: Number of offers to send
        
    Returns:
        OvertimeOfferBatch or None if no staff available
    """
    try:
        shift = Shift.objects.get(id=shift_id)
        return OvertimeOfferService.create_and_send_offers(shift, num_offers=num_offers)
    except Shift.DoesNotExist:
        logger.error(f"Shift {shift_id} not found")
        return None
