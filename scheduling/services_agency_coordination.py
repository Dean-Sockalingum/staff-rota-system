"""
Enhanced Agency Coordination Service - Task 2
Multi-agency blast emails with auto-booking capability

Timeline: 2 hours manual phone tag → 10 minutes automated
"""

from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from decimal import Decimal
import logging

from scheduling.models_automated_workflow import AgencyRequest, AgencyResponse, AgencyBlastBatch
from scheduling.models import AgencyCompany, Shift
from scheduling.notifications import send_email


logger = logging.getLogger(__name__)


class AgencyCoordinationService:
    """
    Orchestrates multi-agency communication and auto-booking
    
    Workflow:
    1. Create blast batch → Email 3 agencies simultaneously
    2. Track responses in real-time
    3. Auto-book first responder if within budget
    4. Escalate to OM if over budget or no responses
    """
    
    # Configuration
    DEFAULT_RESPONSE_TIMEOUT = 30  # minutes
    MAX_AGENCIES_PER_BLAST = 3
    AUTO_BOOK_THRESHOLD = Decimal('200.00')  # Auto-book if quote ≤ £200
    
    
    @classmethod
    def create_agency_blast(cls, agency_request_id, max_agencies=MAX_AGENCIES_PER_BLAST, 
                           timeout_minutes=DEFAULT_RESPONSE_TIMEOUT):
        """
        Create multi-agency blast for a shift
        
        Args:
            agency_request_id: AgencyRequest to process
            max_agencies: How many agencies to contact (default 3)
            timeout_minutes: Response deadline (default 30 min)
            
        Returns:
            AgencyBlastBatch object with tracking info
        """
        
        try:
            agency_request = AgencyRequest.objects.select_related(
                'shift', 'shift__unit__home'
            ).get(id=agency_request_id)
            
        except AgencyRequest.DoesNotExist:
            logger.error(f"AgencyRequest {agency_request_id} not found")
            raise ValueError(f"Invalid agency_request_id: {agency_request_id}")
        
        # Check if already has active blast
        existing_blast = AgencyBlastBatch.objects.filter(
            agency_request=agency_request,
            status__in=['PENDING', 'PARTIAL']
        ).first()
        
        if existing_blast:
            logger.warning(f"AgencyRequest {agency_request_id} already has active blast")
            return existing_blast
        
        # Find top agencies based on:
        # 1. Historical reliability
        # 2. Proximity to care home
        # 3. Rates
        top_agencies = cls._find_top_agencies(
            agency_request.shift,
            limit=max_agencies
        )
        
        if not top_agencies:
            logger.error(f"No agencies available for shift {agency_request.shift.id}")
            raise ValueError("No agencies available for this shift")
        
        # Create blast batch
        with transaction.atomic():
            blast_batch = AgencyBlastBatch.objects.create(
                agency_request=agency_request,
                response_deadline=timezone.now() + timedelta(minutes=timeout_minutes),
                status='PENDING',
                budget_limit=agency_request.estimated_cost
            )
            
            # Create individual responses for each agency
            responses_created = []
            for rank, agency in enumerate(top_agencies, start=1):
                response = AgencyResponse.objects.create(
                    blast_batch=blast_batch,
                    agency=agency,
                    rank=rank,
                    status='SENT'
                )
                responses_created.append(response)
                
                # Send email to agency
                cls._send_agency_email(response, agency_request.shift)
            
            logger.info(
                f"Created blast batch {blast_batch.id} with {len(responses_created)} agencies "
                f"for shift {agency_request.shift.id}"
            )
            
            return blast_batch
    
    
    @classmethod
    def _find_top_agencies(cls, shift, limit=3):
        """
        Find best agencies for this shift based on multiple factors
        
        Ranking criteria:
        - Historical acceptance rate
        - Average response time
        - Quote competitiveness
        - Proximity to care home
        - Availability for this role/grade
        """
        
        from django.db.models import Avg, Count, Q
        
        # Get agencies that can fulfill this role
        qualified_agencies = AgencyCompany.objects.filter(
            is_active=True,
            roles_provided__icontains=shift.role  # Simple contains check
        )
        
        # Annotate with performance metrics
        ranked_agencies = qualified_agencies.annotate(
            acceptance_rate=Count(
                'agency_responses',
                filter=Q(agency_responses__status='ACCEPTED')
            ) * 100.0 / Count('agency_responses'),
            avg_quote=Avg('agency_responses__quoted_rate'),
            total_bookings=Count(
                'agency_responses',
                filter=Q(agency_responses__status='BOOKED')
            )
        ).order_by(
            '-acceptance_rate',  # Highest acceptance first
            'avg_quote',          # Lowest rates second
            '-total_bookings'     # Most experienced third
        )[:limit]
        
        return list(ranked_agencies)
    
    
    @classmethod
    def _send_agency_email(cls, agency_response, shift):
        """
        Send email to agency with shift details and response links
        
        Template includes:
        - Shift date, time, location
        - Role and grade requirements
        - Budget indication
        - Accept/Quote links (webhook URLs)
        """
        
        agency = agency_response.agency
        blast_batch = agency_response.blast_batch
        
        # Build email content
        subject = f"URGENT: {shift.role} Needed - {shift.date.strftime('%A %d %B')}"
        
        response_url_base = f"https://rota.example.com/api/agency-coordination/response/{agency_response.id}"
        accept_url = f"{response_url_base}/accept/"
        quote_url = f"{response_url_base}/quote/"
        
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px;">
            <h2 style="color: #d9534f;">🚨 Urgent Staff Request</h2>
            
            <div style="background: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3>Shift Details</h3>
                <p><strong>Date:</strong> {shift.date.strftime('%A, %d %B %Y')}</p>
                <p><strong>Time:</strong> {shift.start_time.strftime('%H:%M')} - {shift.end_time.strftime('%H:%M')}</p>
                <p><strong>Role:</strong> {shift.role}</p>
                <p><strong>Location:</strong> {shift.unit.home.name if hasattr(shift.unit, 'home') else 'Care Home'}</p>
                <p><strong>Budget Indication:</strong> £{blast_batch.budget_limit} (negotiable)</p>
            </div>
            
            <div style="background: #fffacd; padding: 15px; border-left: 4px solid #f0ad4e; margin: 20px 0;">
                <p><strong>⏰ Response Deadline:</strong> {blast_batch.response_deadline.strftime('%H:%M today')}</p>
                <p style="font-size: 12px; color: #666;">First to respond has priority</p>
            </div>
            
            <div style="margin: 30px 0;">
                <a href="{accept_url}" 
                   style="display: inline-block; background: #5cb85c; color: white; 
                          padding: 12px 30px; text-decoration: none; border-radius: 5px; 
                          font-weight: bold; margin-right: 10px;">
                    ✅ Accept at Budget Rate
                </a>
                
                <a href="{quote_url}" 
                   style="display: inline-block; background: #0275d8; color: white; 
                          padding: 12px 30px; text-decoration: none; border-radius: 5px; 
                          font-weight: bold;">
                    💷 Send Quote
                </a>
            </div>
            
            <p style="font-size: 12px; color: #999; margin-top: 30px;">
                This request was sent to {blast_batch.agency_responses.count()} agencies. 
                First qualified response will be prioritized.
            </p>
        </div>
        """
        
        try:
            send_email(
                to_email=agency.contact_email,
                subject=subject,
                html_body=html_body,
                priority='high'
            )
            
            logger.info(f"Sent blast email to {agency.name} for shift {shift.id}")
            
        except Exception as e:
            logger.error(f"Failed to send email to {agency.name}: {str(e)}")
            agency_response.status = 'EMAIL_FAILED'
            agency_response.save()
    
    
    @classmethod
    def process_agency_response(cls, response_id, response_type, quoted_rate=None):
        """
        Handle agency response (accept or quote)
        
        Args:
            response_id: AgencyResponse ID
            response_type: 'ACCEPT' or 'QUOTE'
            quoted_rate: Decimal rate if QUOTE (required for quotes)
            
        Returns:
            dict with booking status and next actions
        """
        
        try:
            agency_response = AgencyResponse.objects.select_related(
                'blast_batch__agency_request__shift',
                'agency'
            ).get(id=response_id)
            
        except AgencyResponse.DoesNotExist:
            logger.error(f"AgencyResponse {response_id} not found")
            raise ValueError(f"Invalid response_id: {response_id}")
        
        blast_batch = agency_response.blast_batch
        
        # Check if batch already filled
        if blast_batch.status in ['BOOKED', 'CANCELLED']:
            return {
                'status': 'TOO_LATE',
                'message': 'This shift has already been filled by another agency'
            }
        
        # Update response
        agency_response.responded_at = timezone.now()
        
        if response_type == 'ACCEPT':
            # Agency accepts at budget rate
            agency_response.status = 'ACCEPTED'
            agency_response.quoted_rate = blast_batch.budget_limit
            agency_response.save()
            
            # Auto-book if first to respond
            return cls._auto_book_agency(agency_response)
        
        elif response_type == 'QUOTE':
            # Agency provides custom quote
            if quoted_rate is None:
                raise ValueError("quoted_rate required for QUOTE response")
            
            agency_response.status = 'QUOTED'
            agency_response.quoted_rate = Decimal(str(quoted_rate))
            agency_response.save()
            
            # Check if within auto-book threshold
            if agency_response.quoted_rate <= cls.AUTO_BOOK_THRESHOLD:
                return cls._auto_book_agency(agency_response)
            else:
                return cls._escalate_to_manager(agency_response)
        
        else:
            raise ValueError(f"Invalid response_type: {response_type}")
    
    
    @classmethod
    def _auto_book_agency(cls, agency_response):
        """
        Auto-book agency if within budget and first to respond
        
        Updates:
        - Shift assignment
        - Blast batch status
        - Agency request status
        - Sends confirmations
        """
        
        blast_batch = agency_response.blast_batch
        shift = blast_batch.agency_request.shift
        
        with transaction.atomic():
            # Mark as booked
            agency_response.status = 'BOOKED'
            agency_response.save()
            
            # Update blast batch
            blast_batch.status = 'BOOKED'
            blast_batch.booked_agency = agency_response.agency
            blast_batch.final_rate = agency_response.quoted_rate
            blast_batch.save()
            
            # Update agency request
            blast_batch.agency_request.status = 'FILLED'
            blast_batch.agency_request.save()
            
            # Assign shift to agency
            shift.agency_staff_name = f"{agency_response.agency.name} Staff"
            shift.is_agency_filled = True
            shift.agency_cost = agency_response.quoted_rate
            shift.save()
            
            # Cancel other pending responses
            blast_batch.agency_responses.exclude(
                id=agency_response.id
            ).update(status='CANCELLED')
            
            # Send confirmations
            cls._send_booking_confirmation(agency_response)
            cls._send_manager_notification(agency_response, 'BOOKED')
            
            logger.info(
                f"Auto-booked {agency_response.agency.name} for shift {shift.id} "
                f"at £{agency_response.quoted_rate}"
            )
        
        return {
            'status': 'BOOKED',
            'message': f'Booking confirmed with {agency_response.agency.name}',
            'shift_id': shift.id,
            'rate': float(agency_response.quoted_rate),
            'agency': agency_response.agency.name
        }
    
    
    @classmethod
    def _escalate_to_manager(cls, agency_response):
        """
        Quote exceeds auto-book threshold - requires manager approval
        """
        
        blast_batch = agency_response.blast_batch
        
        # Update batch status
        if blast_batch.status == 'PENDING':
            blast_batch.status = 'PARTIAL'
            blast_batch.save()
        
        # Notify manager
        cls._send_manager_notification(agency_response, 'QUOTE_REVIEW')
        
        logger.info(
            f"Escalated quote from {agency_response.agency.name} "
            f"(£{agency_response.quoted_rate}) to manager approval"
        )
        
        return {
            'status': 'PENDING_APPROVAL',
            'message': 'Quote submitted - awaiting manager approval',
            'quoted_rate': float(agency_response.quoted_rate),
            'budget': float(blast_batch.budget_limit)
        }
    
    
    @classmethod
    def _send_booking_confirmation(cls, agency_response):
        """Send booking confirmation to agency"""
        
        shift = agency_response.blast_batch.agency_request.shift
        
        subject = f"CONFIRMED: Booking for {shift.date.strftime('%A %d %B')}"
        html_body = f"""
        <h2 style="color: #5cb85c;">✅ Booking Confirmed</h2>
        <p>Your booking has been confirmed for:</p>
        <ul>
            <li><strong>Date:</strong> {shift.date.strftime('%A, %d %B %Y')}</li>
            <li><strong>Time:</strong> {shift.start_time.strftime('%H:%M')} - {shift.end_time.strftime('%H:%M')}</li>
            <li><strong>Role:</strong> {shift.role}</li>
            <li><strong>Rate:</strong> £{agency_response.quoted_rate}</li>
        </ul>
        <p>Please confirm staff name by replying to this email.</p>
        """
        
        send_email(
            to_email=agency_response.agency.contact_email,
            subject=subject,
            html_body=html_body
        )
    
    
    @classmethod
    def _send_manager_notification(cls, agency_response, notification_type):
        """Send notification to manager about agency response"""
        
        blast_batch = agency_response.blast_batch
        shift = blast_batch.agency_request.shift
        
        if notification_type == 'BOOKED':
            subject = f"✅ Agency Booked: {shift.date.strftime('%A %d %B')}"
            message = f"""
            Shift automatically filled by {agency_response.agency.name}
            Rate: £{agency_response.quoted_rate}
            Total savings vs manual: 110 minutes
            """
        
        elif notification_type == 'QUOTE_REVIEW':
            subject = f"⚠️ Agency Quote Needs Approval: £{agency_response.quoted_rate}"
            message = f"""
            {agency_response.agency.name} quoted £{agency_response.quoted_rate}
            Budget was: £{blast_batch.budget_limit}
            Overage: £{agency_response.quoted_rate - blast_batch.budget_limit}
            
            Review at: https://rota.example.com/agency/batch/{blast_batch.id}/
            """
        
        # Send to operational manager
        send_email(
            to_email='operational.manager@example.com',
            subject=subject,
            html_body=f"<pre>{message}</pre>"
        )
    
    
    @classmethod
    def check_blast_timeout(cls, blast_batch_id):
        """
        Check if blast batch has timed out (no responses within deadline)
        Called by cron job every 5 minutes
        """
        
        try:
            blast_batch = AgencyBlastBatch.objects.get(id=blast_batch_id)
        except AgencyBlastBatch.DoesNotExist:
            return None
        
        # Skip if already resolved
        if blast_batch.status in ['BOOKED', 'CANCELLED', 'TIMEOUT']:
            return None
        
        # Check if deadline passed
        if timezone.now() > blast_batch.response_deadline:
            
            # Check if any quotes pending review
            pending_quotes = blast_batch.agency_responses.filter(
                status='QUOTED'
            ).order_by('quoted_rate')
            
            if pending_quotes.exists():
                # Auto-escalate best quote to manager
                best_quote = pending_quotes.first()
                cls._escalate_to_manager(best_quote)
                
                blast_batch.status = 'TIMEOUT'
                blast_batch.save()
                
                logger.info(
                    f"Blast batch {blast_batch_id} timed out - "
                    f"escalated best quote (£{best_quote.quoted_rate})"
                )
            else:
                # No responses at all - escalate to senior management
                blast_batch.status = 'TIMEOUT'
                blast_batch.save()
                
                send_email(
                    to_email='head.of.service@example.com',
                    subject='🚨 URGENT: No Agency Responses',
                    html_body=f"""
                    <h2 style="color: #d9534f;">No agencies responded</h2>
                    <p>Shift: {blast_batch.agency_request.shift}</p>
                    <p>Contacted: {blast_batch.agency_responses.count()} agencies</p>
                    <p>Action: Manual intervention required</p>
                    """
                )
                
                logger.warning(
                    f"Blast batch {blast_batch_id} timed out with NO responses - "
                    f"escalated to senior management"
                )
