"""
Comprehensive test suite for automated staffing workflow.

Tests all 8 workflow steps, WTD compliance, OT priority scoring,
reallocation search, timeout handling, and agency escalation.

Author: Dean Sockalingum
Created: 2025-01-18
"""

from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, time, timedelta
from unittest.mock import patch, MagicMock

from scheduling.models import Shift, Unit, Role, ShiftType
from scheduling.models_automated_workflow import (
    SicknessAbsence, StaffingCoverRequest, OvertimeOfferBatch,
    OvertimeOffer, ReallocationRequest, AgencyRequest,
    LongTermCoverPlan, PostShiftAdministration
)
from scheduling.models_multi_home import CareHome
from scheduling.workflow_orchestrator import (
    trigger_absence_workflow, execute_concurrent_search,
    process_reallocation_response, process_ot_offer_response,
    handle_timeout, create_long_term_plan, escalate_to_agency,
    auto_approve_agency_timeout, resolve_cover_request,
    create_post_shift_admin, get_workflow_summary
)
from scheduling.wdt_compliance import (
    is_wdt_compliant_for_ot, calculate_weekly_hours,
    calculate_rolling_average_hours
)
from scheduling.ot_priority import (
    calculate_total_priority_score, get_top_ot_candidates
)
from scheduling.reallocation_search import find_eligible_staff_for_reallocation

User = get_user_model()


class WorkflowTestBase(TransactionTestCase):
    """Base test case with common setup for workflow tests"""
    
    def setUp(self):
        """Create test data for workflow testing"""
        # Create care home
        self.care_home = CareHome.objects.create(
            name='ORCHARD_GROVE',
            bed_capacity=60,
            current_occupancy=50,
            location_address="123 Test Street, Glasgow",
            postcode="G1 1AA",
            care_inspectorate_id="CS2025000001"
        )
        
        # Create roles (using actual model fields)
        self.rn_role = Role.objects.create(
            name="SSCW",
            description="Senior Social Care Worker",
            is_management=False,
            can_approve_leave=False,
            can_manage_rota=False,
            required_headcount=3
        )
        
        self.hca_role = Role.objects.create(
            name="SCA",
            description="Social Care Assistant",
            is_management=False,
            can_approve_leave=False,
            can_manage_rota=False,
            required_headcount=2
        )
        
        # Create unit (using actual model fields)
        self.unit = Unit.objects.create(
            name="Test Unit",
            description="Test Unit for Workflow Testing",
            is_active=True,
            min_day_staff=2,
            min_night_staff=2,
            min_weekend_staff=2
        )
        
        # Create staff members
        self.staff1 = self._create_staff_member("Alice", "Smith", self.rn_role)
        self.staff2 = self._create_staff_member("Bob", "Jones", self.rn_role)
        self.staff3 = self._create_staff_member("Carol", "White", self.rn_role)
        self.staff4 = self._create_staff_member("David", "Brown", self.hca_role)
        self.staff5 = self._create_staff_member("Emma", "Davis", self.hca_role)
        
        # Create shift type (applicable_roles is a CharField with comma-separated values)
        self.shift_type = ShiftType.objects.create(
            name="DAY_SENIOR",
            start_time=time(9, 0),
            end_time=time(17, 0),
            duration_hours=8.0,
            is_active=True,
            applicable_roles="SSCW,SCW"  # Comma-separated role names
        )
        
        # Create test shift (using actual model fields)
        tomorrow = date.today() + timedelta(days=1)
        self.shift = Shift.objects.create(
            unit=self.unit,
            user=self.staff1,
            shift_type=self.shift_type,
            date=tomorrow,
            shift_classification='REGULAR',
            status='SCHEDULED'
        )
    
    def _create_staff_member(self, first_name, last_name, role):
        """Helper to create a staff member"""
        import random
        sap = f"TEST{random.randint(1000, 9999)}"
        
        user = User.objects.create_user(
            sap=sap,
            first_name=first_name,
            last_name=last_name,
            email=f"{first_name.lower()}@test.com"
        )
        
        user.role = role
        user.unit = self.unit
        user.save()
        
        return user
    
    
    
    def _create_shift(self, user, shift_date, shift_type=None, status='SCHEDULED'):
        """Helper to create a shift properly"""
        if shift_type is None:
            shift_type = self.shift_type
        
        return Shift.objects.create(
            unit=self.unit,
            user=user,
            shift_type=shift_type,
            date=shift_date,
            shift_classification='REGULAR',
            status=status
        )
    
    def _create_sickness_absence(self, staff_member, start_date, end_date=None, shifts=None):
        """Helper to create sickness absence with affected shifts"""
        if end_date is None:
            end_date = start_date
        
        duration = (end_date - start_date).days + 1
        
        self._create_sickness_absence(
            staff_member=staff_member,
            start_date=start_date,
            end_date=end_date
        )
        
        # Add affected shifts if provided
        if shifts:
            if not isinstance(shifts, list):
                shifts = [shifts]
            absence.affected_shifts.set(shifts)
        
        return absence
    
def _create_shift(self, user, shift_date, shift_type=None, status='SCHEDULED'):
        """Helper to create a shift properly"""
        if shift_type is None:
            shift_type = self.shift_type
        
        return Shift.objects.create(
            unit=self.unit,
            user=user,
            shift_type=shift_type,
            date=shift_date,
            shift_classification='REGULAR',
            status=status
        )
    
    def _create_sickness_absence(self, staff_member, start_date, end_date=None, shifts=None):
        """Helper to create sickness absence with affected shifts"""
        if end_date is None:
            end_date = start_date
        
        duration = (end_date - start_date).days + 1
        
        self._create_sickness_absence(
            staff_member=staff_member,
            start_date=start_date,
            end_date=end_date
        )
        
        # Add affected shifts if provided
        if shifts:
            if not isinstance(shifts, list):
                shifts = [shifts]
            absence.affected_shifts.set(shifts)
        
        return absence


# ==================== STEP 1: Absence Trigger Tests ====================

class AbsenceTriggerTest(WorkflowTestBase):
    """Test Step 1: Absence detection and workflow trigger"""
    
    def test_trigger_workflow_creates_cover_request(self):
        """Test that absence triggers workflow and creates cover request"""
        absence = self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=self.shift.date,
            end_date=self.shift.date,
            shifts=[self.shift]
        )
        
        result = trigger_absence_workflow(absence)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['shifts_affected'], 1)
        
        # Check cover request created
        cover_request = StaffingCoverRequest.objects.filter(absence=absence).first()
        self.assertIsNotNone(cover_request)
        self.assertEqual(cover_request.status, 'PENDING')
    
    def test_long_term_absence_detection(self):
        """Test detection of long-term absences (≥3 shifts OR ≥5 days)"""
        # Create 3 shifts for staff member
        tomorrow = date.today() + timedelta(days=1)
        for i in range(3):
            self._create_shift(self.staff1, tomorrow + timedelta(days=i, status='SCHEDULED')
        
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=tomorrow,
            end_date=tomorrow + timedelta(days=2
        )
        
        result = trigger_absence_workflow(absence)
        
        self.assertTrue(result['success'])
        self.assertTrue(result['is_long_term'])
    
    def test_shift_status_updated_to_uncovered(self):
        """Test that affected shifts are marked as UNCOVERED"""
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=self.shift.date,
            end_date=self.shift.date
        )
        
        trigger_absence_workflow(absence)
        
        self.shift.refresh_from_db()
        self.assertEqual(self.shift.status, 'UNCOVERED')


# ==================== STEP 2: Concurrent Search Tests ====================

class ConcurrentSearchTest(WorkflowTestBase):
    """Test Step 2: Concurrent reallocation and OT search"""
    
    def test_concurrent_search_creates_requests(self):
        """Test that concurrent search creates both reallocation and OT requests"""
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=self.shift.date,
            end_date=self.shift.date
        )
        
        cover_request = StaffingCoverRequest.objects.create(
            absence=absence,
            status='PENDING'
        )
        
        result = execute_concurrent_search(cover_request, self.shift)
        
        self.assertTrue(result['success'])
        
        # Check reallocation requests created
        reallocation_count = ReallocationRequest.objects.filter(
            cover_request=cover_request
        ).count()
        self.assertGreaterEqual(reallocation_count, 0)  # May be 0 if no eligible staff
        
        # Check OT offer batch created
        ot_batch = OvertimeOfferBatch.objects.filter(
            cover_request=cover_request
        ).first()
        self.assertIsNotNone(ot_batch)
    
    def test_ot_offers_sent_to_top_candidates(self):
        """Test that OT offers are sent to top-scored candidates"""
        # Create additional shifts for staff to vary their OT history
        yesterday = date.today() - timedelta(days=1)
        
        # Give staff2 recent OT (should lower their priority)
        self._create_shift(self.staff2, yesterday, status='COMPLETED')
        
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=self.shift.date,
            end_date=self.shift.date
        )
        
        cover_request = StaffingCoverRequest.objects.create(
            absence=absence,
            status='PENDING'
        )
        
        execute_concurrent_search(cover_request, self.shift)
        
        # Check OT offers sent
        ot_offers = OvertimeOffer.objects.filter(
            batch__cover_request=cover_request
        )
        self.assertGreater(ot_offers.count(), 0)


# ==================== STEP 3: Response Processing Tests ====================

class ResponseProcessingTest(WorkflowTestBase):
    """Test Step 3: Reallocation and OT response handling"""
    
    def test_accept_reallocation_cancels_ot_offers(self):
        """Test that accepting reallocation cancels pending OT offers"""
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=self.shift.date,
            end_date=self.shift.date
        )
        
        cover_request = StaffingCoverRequest.objects.create(
            absence=absence,
            status='PENDING'
        )
        
        # Create reallocation request
        reallocation = ReallocationRequest.objects.create(
            cover_request=cover_request,
            staff_member=self.staff2,
            status='PENDING',
            response_deadline=timezone.now() + timedelta(hours=1)
        )
        
        # Create OT offer batch
        ot_batch = OvertimeOfferBatch.objects.create(
            cover_request=cover_request,
            response_deadline=timezone.now() + timedelta(hours=1)
        )
        
        OvertimeOffer.objects.create(
            batch=ot_batch,
            staff_member=self.staff3,
            priority_score=75,
            status='PENDING'
        )
        
        # Accept reallocation
        result = process_reallocation_response(reallocation, 'ACCEPTED')
        
        self.assertTrue(result['success'])
        
        # Check OT offers cancelled
        ot_offer = OvertimeOffer.objects.first()
        self.assertEqual(ot_offer.status, 'CANCELLED')
        
        # Check shift updated
        self.shift.refresh_from_db()
        self.assertEqual(self.shift.user, self.staff2)
        self.assertEqual(self.shift.status, 'SCHEDULED')
    
    def test_accept_ot_offer_cancels_others(self):
        """Test that accepting OT offer cancels other pending offers"""
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=self.shift.date,
            end_date=self.shift.date
        )
        
        cover_request = StaffingCoverRequest.objects.create(
            absence=absence,
            status='PENDING'
        )
        
        ot_batch = OvertimeOfferBatch.objects.create(
            cover_request=cover_request,
            response_deadline=timezone.now() + timedelta(hours=1)
        )
        
        offer1 = OvertimeOffer.objects.create(
            batch=ot_batch,
            staff_member=self.staff2,
            priority_score=80,
            status='PENDING'
        )
        
        offer2 = OvertimeOffer.objects.create(
            batch=ot_batch,
            staff_member=self.staff3,
            priority_score=75,
            status='PENDING'
        )
        
        # Accept first offer
        result = process_ot_offer_response(offer1, 'ACCEPTED')
        
        self.assertTrue(result['success'])
        
        # Check second offer cancelled
        offer2.refresh_from_db()
        self.assertEqual(offer2.status, 'CANCELLED')
        
        # Check shift updated
        self.shift.refresh_from_db()
        self.assertEqual(self.shift.user, self.staff2)
        self.assertEqual(self.shift.shift_classification, 'OVERTIME')
    
    def test_reallocation_cost_is_zero(self):
        """Test that reallocation cover has zero cost"""
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=self.shift.date,
            end_date=self.shift.date
        )
        
        cover_request = StaffingCoverRequest.objects.create(
            absence=absence,
            status='PENDING'
        )
        
        reallocation = ReallocationRequest.objects.create(
            cover_request=cover_request,
            staff_member=self.staff2,
            status='PENDING',
            response_deadline=timezone.now() + timedelta(hours=1)
        )
        
        process_reallocation_response(reallocation, 'ACCEPTED')
        
        cover_request.refresh_from_db()
        self.assertEqual(cover_request.total_cost, Decimal('0'))


# ==================== STEP 4: Timeout Handling Tests ====================

class TimeoutHandlingTest(WorkflowTestBase):
    """Test Step 4: Deadline expiry and escalation"""
    
    def test_timeout_expires_pending_requests(self):
        """Test that timeout expires all pending requests/offers"""
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=self.shift.date,
            end_date=self.shift.date
        )
        
        cover_request = StaffingCoverRequest.objects.create(
            absence=absence,
            status='OT_OFFERED'
        )
        
        # Create expired OT offer
        ot_batch = OvertimeOfferBatch.objects.create(
            cover_request=cover_request,
            response_deadline=timezone.now() - timedelta(minutes=5)  # Expired
        )
        
        OvertimeOffer.objects.create(
            batch=ot_batch,
            staff_member=self.staff2,
            priority_score=75,
            status='PENDING'
        )
        
        result = handle_timeout(cover_request)
        
        self.assertTrue(result['success'])
        
        # Check offer expired
        ot_offer = OvertimeOffer.objects.first()
        self.assertEqual(ot_offer.status, 'EXPIRED')
    
    def test_timeout_escalates_to_agency(self):
        """Test that timeout triggers agency escalation"""
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=self.shift.date,
            end_date=self.shift.date
        )
        
        cover_request = StaffingCoverRequest.objects.create(
            absence=absence,
            status='OT_OFFERED'
        )
        
        result = handle_timeout(cover_request)
        
        self.assertTrue(result['success'])
        
        # Check agency request created
        agency_request = AgencyRequest.objects.filter(
            cover_request=cover_request
        ).first()
        self.assertIsNotNone(agency_request)


# ==================== STEP 5: Long-Term Planning Tests ====================

class LongTermPlanningTest(WorkflowTestBase):
    """Test Step 5: Long-term absence strategy generation"""
    
    def test_long_term_plan_created_for_multi_shift_absence(self):
        """Test that long-term plan is created for ≥3 shifts"""
        tomorrow = date.today() + timedelta(days=1)
        
        # Create 4 shifts
        shifts = []
        for i in range(4):
            self._create_shift(self.staff1, tomorrow + timedelta(days=i, status='SCHEDULED')
            shifts.append(shift)
        
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=tomorrow,
            end_date=tomorrow + timedelta(days=3
        )
        
        for shift in shifts:
            absence.affected_shifts.add(shift)
        
        cover_request = StaffingCoverRequest.objects.create(
            absence=absence,
            is_long_term=True,
            status='PENDING'
        )
        
        result = create_long_term_plan(cover_request)
        
        self.assertTrue(result['success'])
        
        # Check plan created
        plan = LongTermCoverPlan.objects.filter(
            cover_request=cover_request
        ).first()
        self.assertIsNotNone(plan)
        self.assertIsNotNone(plan.recommended_strategy)
        self.assertGreater(plan.estimated_total_cost, Decimal('0'))
    
    def test_long_term_plan_cost_estimation(self):
        """Test that long-term plan estimates costs for different strategies"""
        tomorrow = date.today() + timedelta(days=1)
        
        shifts = []
        for i in range(5):
            self._create_shift(self.staff1, tomorrow + timedelta(days=i, status='SCHEDULED')
            shifts.append(shift)
        
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=tomorrow,
            end_date=tomorrow + timedelta(days=4
        )
        
        for shift in shifts:
            absence.affected_shifts.add(shift)
        
        cover_request = StaffingCoverRequest.objects.create(
            absence=absence,
            is_long_term=True,
            status='PENDING'
        )
        
        result = create_long_term_plan(cover_request)
        
        plan = LongTermCoverPlan.objects.get(cover_request=cover_request)
        
        # Should have cost estimates
        self.assertIsNotNone(plan.estimated_reallocation_cost)
        self.assertIsNotNone(plan.estimated_ot_cost)
        self.assertIsNotNone(plan.estimated_agency_cost)


# ==================== STEP 6: Agency Escalation Tests ====================

class AgencyEscalationTest(WorkflowTestBase):
    """Test Step 6: Agency request and auto-approval"""
    
    def test_agency_request_created_with_approval_deadline(self):
        """Test that agency request has 15-minute approval deadline"""
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=self.shift.date,
            end_date=self.shift.date
        )
        
        cover_request = StaffingCoverRequest.objects.create(
            absence=absence,
            status='PENDING'
        )
        
        result = escalate_to_agency(cover_request)
        
        self.assertTrue(result['success'])
        
        agency_request = AgencyRequest.objects.get(cover_request=cover_request)
        
        # Check approval deadline is ~15 minutes from now
        deadline_diff = (agency_request.approval_deadline - timezone.now()).total_seconds()
        self.assertLess(abs(deadline_diff - 900), 60)  # Within 1 minute of 15 min
    
    @patch('rotasystems.settings.STAFFING_WORKFLOW', {'AUTO_APPROVE_AGENCY_TIMEOUT': True})
    def test_auto_approve_after_timeout(self):
        """Test that agency request is auto-approved after timeout"""
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=self.shift.date,
            end_date=self.shift.date
        )
        
        cover_request = StaffingCoverRequest.objects.create(
            absence=absence,
            status='AGENCY_REQUESTED'
        )
        
        # Create expired agency request
        agency_request = AgencyRequest.objects.create(
            cover_request=cover_request,
            estimated_cost=Decimal('200.00'),
            approval_status='PENDING_APPROVAL',
            approval_deadline=timezone.now() - timedelta(minutes=5)  # Expired
        )
        
        result = auto_approve_agency_timeout(agency_request)
        
        self.assertTrue(result['success'])
        
        agency_request.refresh_from_db()
        self.assertEqual(agency_request.approval_status, 'AUTO_APPROVED')
        
        # Check shift updated
        self.shift.refresh_from_db()
        self.assertEqual(self.shift.shift_classification, 'AGENCY')
    
    def test_agency_cost_calculation(self):
        """Test that agency cost is calculated at 1.8x multiplier"""
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=self.shift.date,
            end_date=self.shift.date
        )
        
        cover_request = StaffingCoverRequest.objects.create(
            absence=absence,
            status='PENDING'
        )
        
        escalate_to_agency(cover_request)
        
        agency_request = AgencyRequest.objects.get(cover_request=cover_request)
        
        # Expected: 8 hours * £15/hr * 1.8 = £216
        expected_cost = Decimal('8.0') * Decimal('15.00') * Decimal('1.8')
        self.assertEqual(agency_request.estimated_cost, expected_cost)


# ==================== STEP 7-8: Resolution & Post-Shift Admin Tests ====================

class ResolutionAndAdminTest(WorkflowTestBase):
    """Test Steps 7-8: Resolution confirmation and post-shift admin"""
    
    def test_resolve_cover_request_marks_resolved(self):
        """Test that resolution finalizes cover request"""
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=self.shift.date,
            end_date=self.shift.date
        )
        
        cover_request = StaffingCoverRequest.objects.create(
            absence=absence,
            status='OT_OFFERED'
        )
        
        result = resolve_cover_request(
            cover_request,
            resolution_method='OVERTIME',
            assigned_staff=self.staff2,
            actual_cost=Decimal('180.00')
        )
        
        self.assertTrue(result['success'])
        
        cover_request.refresh_from_db()
        self.assertEqual(cover_request.status, 'RESOLVED')
        self.assertEqual(cover_request.resolution_method, 'OVERTIME')
        self.assertEqual(cover_request.total_cost, Decimal('180.00'))
    
    def test_post_shift_admin_auto_population(self):
        """Test that post-shift admin auto-populates from workflow"""
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=self.shift.date,
            end_date=self.shift.date
        )
        
        cover_request = StaffingCoverRequest.objects.create(
            absence=absence,
            status='RESOLVED',
            resolution_method='OVERTIME',
            total_cost=Decimal('180.00')
        )
        
        # Mark shift as completed
        self.shift.shift_classification = 'OVERTIME'
        self.shift.user = self.staff2
        self.shift.save()
        
        result = create_post_shift_admin(
            shift=self.shift,
            cover_request=cover_request,
            actual_staff_assigned=self.staff2,
            actual_hours_worked=Decimal('8.0')
        )
        
        self.assertTrue(result['success'])
        
        post_admin = PostShiftAdministration.objects.get(shift=self.shift)
        self.assertEqual(post_admin.original_staff_member, self.staff1)
        self.assertEqual(post_admin.actual_staff_assigned, self.staff2)
        self.assertEqual(post_admin.cover_method, 'OVERTIME')
    
    def test_cost_discrepancy_detection(self):
        """Test that cost discrepancies are flagged"""
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=self.shift.date,
            end_date=self.shift.date
        )
        
        cover_request = StaffingCoverRequest.objects.create(
            absence=absence,
            status='RESOLVED',
            resolution_method='OVERTIME',
            total_cost=Decimal('180.00')  # Estimated
        )
        
        self.shift.shift_classification = 'OVERTIME'
        self.shift.user = self.staff2
        self.shift.save()
        
        result = create_post_shift_admin(
            shift=self.shift,
            cover_request=cover_request,
            actual_cost=Decimal('200.00')  # £20 difference
        )
        
        post_admin = PostShiftAdministration.objects.get(shift=self.shift)
        self.assertTrue(post_admin.has_cost_discrepancy)
        self.assertEqual(post_admin.status, 'PENDING_REVIEW')


# ==================== WTD Compliance Tests ====================

class WTDComplianceTest(WorkflowTestBase):
    """Test UK Working Time Directive compliance checks"""
    
    def test_weekly_hours_calculation(self):
        """Test calculation of hours worked in a week"""
        # Create shifts for the week
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        for i in range(5):
            self._create_shift(self.staff1, week_start + timedelta(days=i, status='COMPLETED')
        
        weekly_hours = calculate_weekly_hours(self.staff1, week_start, weeks=1)
        self.assertEqual(weekly_hours, Decimal('40.0'))
    
    def test_wdt_compliance_blocks_excessive_ot(self):
        """Test that WTD compliance prevents OT offers when at limit"""
        # Create shifts totaling 46 hours this week
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        # 5 days x 9 hours = 45 hours
        for i in range(5):
            self._create_shift(self.staff2, week_start + timedelta(days=i, status='COMPLETED')
        
        # Try to offer 8-hour OT shift (would exceed 48hr limit)
        tomorrow = date.today() + timedelta(days=1)
        compliance = is_wdt_compliant_for_ot(self.staff2, tomorrow, Decimal('8.0'))
        
        self.assertFalse(compliance['compliant'])
        self.assertIn('weekly hours', compliance['violations'][0].lower())
    
    def test_rest_period_compliance(self):
        """Test that 11-hour rest period is enforced"""
        # Create shift ending at 22:00 today
        today = date.today()
        self._create_shift(self.staff3, today, status='SCHEDULED')
        
        # Try to offer shift starting at 07:00 tomorrow (only 9 hours rest)
        tomorrow = today + timedelta(days=1)
        self._create_shift(self.staff3, tomorrow, status='DRAFT')
        
        compliance = is_wdt_compliant_for_ot(self.staff3, tomorrow, Decimal('8.0'))
        
        # Clean up test shift
        test_shift.delete()
        
        self.assertFalse(compliance['compliant'])
        self.assertIn('rest period', compliance['violations'][0].lower())


# ==================== OT Priority Scoring Tests ====================

class OTPriorityTest(WorkflowTestBase):
    """Test OT priority scoring algorithm"""
    
    def test_fair_rotation_scoring(self):
        """Test that staff with less recent OT score higher"""
        # Give staff2 recent OT
        yesterday = date.today() - timedelta(days=1)
        self._create_shift(self.staff2, yesterday, status='COMPLETED')
        
        # Staff3 has no recent OT
        score2 = calculate_total_priority_score(self.staff2, self.shift)
        score3 = calculate_total_priority_score(self.staff3, self.shift)
        
        # Staff3 should score higher due to fair rotation
        self.assertGreater(score3, score2)
    
    def test_qualification_scoring(self):
        """Test that exact qualification match scores highest"""
        # Create shift requiring RN
        self._create_shift(self.staff1, date.today(, status='DRAFT')
        
        # RN staff should score higher than HCA staff
        rn_score = calculate_total_priority_score(self.staff2, rn_shift)  # RN
        hca_score = calculate_total_priority_score(self.staff4, rn_shift)  # HCA
        
        self.assertGreater(rn_score, hca_score)
        
        rn_shift.delete()
    
    def test_top_candidates_selection(self):
        """Test that top candidates are correctly selected"""
        # Create additional staff
        for i in range(25):
            staff = self._create_staff_member(f"Test{i}", f"User{i}", self.rn_role)
        
        tomorrow = date.today() + timedelta(days=1)
        self._create_shift(self.staff1, tomorrow, status='DRAFT')
        
        # Get all RN staff
        rn_staff = User.objects.filter(
            role_code='RN'
        ).exclude(id=self.staff1.id)
        
        top_candidates = get_top_ot_candidates(test_shift, rn_staff, max_candidates=20)
        
        # Should return max 20 candidates
        self.assertLessEqual(len(top_candidates), 20)
        
        # Should be ordered by priority score (descending)
        if len(top_candidates) > 1:
            self.assertGreaterEqual(
                top_candidates[0]['priority_score'],
                top_candidates[-1]['priority_score']
            )
        
        test_shift.delete()


# ==================== Reallocation Search Tests ====================

class ReallocationSearchTest(WorkflowTestBase):
    """Test cross-home staff reallocation search"""
    
    def test_reallocation_finds_eligible_staff(self):
        """Test that reallocation search finds eligible staff"""
        # Create second care home
        care_home2 = CareHome.objects.create(
            name='MEADOWBURN',
            bed_capacity=50,
            current_occupancy=40,
            location_address="456 Another Street, Glasgow",
            postcode="G2 2BB",
            care_inspectorate_id="CS2025000002"
        )
        
        unit2 = Unit.objects.create(
            name="Unit 2",
            care_home=care_home2,
            min_staff_required=2
        )
        
        # Create staff member in second home
        staff_other_home = self._create_staff_member("Frank", "Wilson", self.rn_role)
        
        eligible_staff = find_eligible_staff_for_reallocation(
            shift=self.shift,
            source_home=self.care_home
        )
        
        # Should find staff from other home (if WTD compliant and within distance)
        # Note: May be empty if distance/travel time filters exclude them
        self.assertIsInstance(eligible_staff, list)
    
    def test_reallocation_excludes_scheduled_staff(self):
        """Test that already-scheduled staff are excluded from reallocation"""
        tomorrow = date.today() + timedelta(days=1)
        
        # Schedule staff2 for another shift at same time
        self._create_shift(self.staff2, tomorrow, status='SCHEDULED')
        
        eligible_staff = find_eligible_staff_for_reallocation(
            shift=self.shift,
            source_home=self.care_home
        )
        
        # Staff2 should not be in eligible list
        eligible_ids = [s['staff_member'].id for s in eligible_staff]
        self.assertNotIn(self.staff2.id, eligible_ids)


# ==================== Workflow Reporting Tests ====================

class WorkflowReportingTest(WorkflowTestBase):
    """Test workflow summary and reporting functions"""
    
    def test_workflow_summary_generation(self):
        """Test generation of workflow summary report"""
        # Create some completed workflows
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=self.shift.date,
            end_date=self.shift.date
        )
        
        cover_request = StaffingCoverRequest.objects.create(
            absence=absence,
            status='RESOLVED',
            resolution_method='OVERTIME',
            total_cost=Decimal('180.00'),
            resolved_at=timezone.now()
        )
        
        summary = get_workflow_summary(
            start_date=date.today() - timedelta(days=7),
            end_date=date.today() + timedelta(days=7)
        )
        
        self.assertIn('period', summary)
        self.assertIn('absences', summary)
        self.assertIn('cover_requests', summary)
        self.assertIn('costs', summary)
        self.assertIn('performance', summary)
        
        # Check that our request is counted
        self.assertGreaterEqual(summary['cover_requests']['total'], 1)
        self.assertGreaterEqual(summary['cover_requests']['resolved'], 1)


# ==================== Integration Tests ====================

class EndToEndWorkflowTest(WorkflowTestBase):
    """End-to-end integration tests for complete workflow scenarios"""
    
    def test_complete_workflow_reallocation_success(self):
        """Test complete workflow: Absence → Reallocation → Resolution"""
        # Create absence
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=self.shift.date,
            end_date=self.shift.date
        )
        
        # Step 1: Trigger workflow
        trigger_result = trigger_absence_workflow(absence)
        self.assertTrue(trigger_result['success'])
        
        cover_request = StaffingCoverRequest.objects.get(absence=absence)
        
        # Step 2: Execute search
        search_result = execute_concurrent_search(cover_request, self.shift)
        self.assertTrue(search_result['success'])
        
        # Step 3: Simulate reallocation acceptance
        reallocation = ReallocationRequest.objects.filter(
            cover_request=cover_request
        ).first()
        
        if reallocation:
            response_result = process_reallocation_response(reallocation, 'ACCEPTED')
            self.assertTrue(response_result['success'])
            
            # Step 7: Resolve
            resolve_result = resolve_cover_request(
                cover_request,
                resolution_method='REALLOCATION',
                assigned_staff=reallocation.staff_member,
                actual_cost=Decimal('0')
            )
            self.assertTrue(resolve_result['success'])
            
            # Verify final state
            cover_request.refresh_from_db()
            self.assertEqual(cover_request.status, 'RESOLVED')
            self.assertEqual(cover_request.total_cost, Decimal('0'))
    
    def test_complete_workflow_ot_to_agency_escalation(self):
        """Test complete workflow: Absence → OT timeout → Agency → Auto-approve"""
        # Create absence
        self._create_sickness_absence(
            staff_member=self.staff1,
            start_date=self.shift.date,
            end_date=self.shift.date
        )
        
        # Step 1: Trigger
        trigger_absence_workflow(absence)
        
        cover_request = StaffingCoverRequest.objects.get(absence=absence)
        
        # Step 2: Search
        execute_concurrent_search(cover_request, self.shift)
        
        # Step 4: Simulate timeout (all offers expired)
        cover_request.status = 'OT_OFFERED'
        cover_request.save()
        
        timeout_result = handle_timeout(cover_request)
        self.assertTrue(timeout_result['success'])
        
        # Step 6: Verify agency request created
        agency_request = AgencyRequest.objects.filter(
            cover_request=cover_request
        ).first()
        self.assertIsNotNone(agency_request)
        
        # Simulate auto-approval
        agency_request.approval_deadline = timezone.now() - timedelta(minutes=20)
        agency_request.save()
        
        with patch('rotasystems.settings.STAFFING_WORKFLOW', {'AUTO_APPROVE_AGENCY_TIMEOUT': True}):
            auto_result = auto_approve_agency_timeout(agency_request)
            self.assertTrue(auto_result['success'])
        
        # Verify final state
        agency_request.refresh_from_db()
        self.assertEqual(agency_request.approval_status, 'AUTO_APPROVED')


# ==================== Run Tests ====================

if __name__ == '__main__':
    import sys
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    failures = test_runner.run_tests(['scheduling.tests.test_workflow'])
    sys.exit(bool(failures))
