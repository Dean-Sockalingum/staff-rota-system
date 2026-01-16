"""
Shift Optimization Algorithm using Linear Programming (PuLP)

Task 12: ML Phase 4 - Shift Optimization
Scottish Design: Evidence-based, transparent, user-centered

Business Problem:
- Minimize staffing costs while meeting forecasted demand
- Prefer permanent staff over agency workers
- Respect constraints: availability, skills, WTD limits
- Fair workload distribution across staff
"""

from pulp import *
from decimal import Decimal
from datetime import date, timedelta
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class ShiftOptimizationResult:
    """Container for optimization results with transparency metrics"""
    
    def __init__(self, success: bool, status: str, assignments: List[Dict], 
                 cost: float, metrics: Dict):
        self.success = success
        self.status = status  # "Optimal", "Feasible", "Infeasible", "Unbounded"
        self.assignments = assignments  # List of {staff, unit, shift_type, date}
        self.total_cost = cost
        self.metrics = metrics  # Cost breakdown, demand met, etc.
    
    def __str__(self):
        if self.success:
            cost_str = f"£{self.total_cost:.2f}" if self.total_cost is not None else "N/A"
            return (f"Optimization: {self.status} | "
                   f"Cost: {cost_str} | "
                   f"Assignments: {len(self.assignments)}")
        else:
            return f"Optimization Failed: {self.status}"


class ShiftOptimizer:
    """
    Linear Programming-based shift scheduling optimizer
    
    Minimizes: Total staffing cost (prefer permanent > overtime > agency)
    
    Constraints:
    1. Meet forecasted demand (min/max bounds from Prophet CI)
    2. Each staff works ≤1 shift per day
    3. Respect staff availability (off-duty, leave, existing shifts)
    4. Working Time Directive: ≤48 hours/week, 11-hour rest between shifts
    5. Skill matching: Qualified staff for each shift type
    6. Fair distribution: Balance workload across staff
    """
    
    # Cost multipliers (permanent = 1.0 baseline)
    COST_PERMANENT = 1.0      # £12-15/hour (baseline)
    COST_OVERTIME = 1.5       # Time-and-a-half
    COST_AGENCY = 2.0         # Typical agency premium
    
    # WTD Limits
    MAX_HOURS_PER_WEEK = 48
    MIN_REST_HOURS = 11
    
    # Shift duration hours (typical)
    SHIFT_HOURS = {
        'DAY_SENIOR': 12,
        'DAY_ASSISTANT': 12,
        'NIGHT_SENIOR': 12,
        'NIGHT_ASSISTANT': 12,
        'ADMIN': 8,
    }
    
    def __init__(self, care_home, optimization_date: date, forecast_demand: Dict, 
                 available_staff: List, existing_shifts: List):
        """
        Initialize optimizer
        
        Args:
            care_home: CareHome instance to optimize for
            optimization_date: Date to optimize (single day)
            forecast_demand: Dict[unit_name][shift_type] = (min, max) demand
            available_staff: List of User instances available to work
            existing_shifts: List of existing Shift instances (constraints)
        """
        self.care_home = care_home
        self.date = optimization_date
        self.forecast_demand = forecast_demand  # {unit: {shift_type: (min, max)}}
        self.staff = available_staff
        self.existing_shifts = existing_shifts
        
        self.model = None
        self.variables = {}
        self.result = None
    
    def optimize(self) -> ShiftOptimizationResult:
        """
        Run optimization algorithm
        
        Returns:
            ShiftOptimizationResult with assignments and cost breakdown
        """
        logger.info(f"Starting optimization for {self.care_home} on {self.date}")
        logger.info(f"Available staff: {len(self.staff)}")
        logger.info(f"Forecast demand: {self.forecast_demand}")
        
        # Build LP model
        self._build_model()
        
        # Solve
        status = self.model.solve(PULP_CBC_CMD(msg=0))  # CBC solver, silent
        
        # Extract results
        if status == LpStatusOptimal:
            assignments = self._extract_assignments()
            cost = value(self.model.objective)
            metrics = self._calculate_metrics(assignments, cost)
            
            self.result = ShiftOptimizationResult(
                success=True,
                status="Optimal",
                assignments=assignments,
                cost=cost,
                metrics=metrics
            )
            logger.info(f"Optimization successful: {self.result}")
            
        elif status == LpStatusInfeasible:
            logger.error("Optimization infeasible - cannot meet demand with constraints")
            self.result = ShiftOptimizationResult(
                success=False,
                status="Infeasible",
                assignments=[],
                cost=0,
                metrics={'error': 'No feasible solution - insufficient staff or too many constraints'}
            )
        
        else:
            logger.warning(f"Optimization status: {LpStatus[status]}")
            self.result = ShiftOptimizationResult(
                success=False,
                status=LpStatus[status],
                assignments=[],
                cost=0,
                metrics={'error': f'Solver status: {LpStatus[status]}'}
            )
        
        return self.result
    
    def _build_model(self):
        """Build Linear Programming model with objective and constraints"""
        
        self.model = LpProblem("Shift_Assignment_Optimization", LpMinimize)
        
        # Get all units and shift types for this care home
        units = self.care_home.units.filter(is_active=True)
        shift_types = list(self.SHIFT_HOURS.keys())
        
        # Decision variables: x[staff_id, unit_name, shift_type] ∈ {0, 1}
        self.variables = LpVariable.dicts(
            "assign",
            (
                (s.sap, u.name, st)
                for s in self.staff
                for u in units
                for st in shift_types
            ),
            cat='Binary'
        )
        
        # === OBJECTIVE FUNCTION: Minimize Total Cost ===
        # Cost = Σ (staff_cost × shift_hours × assignment_variable)
        
        staff_costs = self._calculate_staff_costs()
        
        self.model += lpSum([
            staff_costs[s.sap] * self.SHIFT_HOURS.get(st, 12) * 
            self.variables[(s.sap, u.name, st)]
            for s in self.staff
            for u in units
            for st in shift_types
        ]), "Total_Cost"
        
        # === CONSTRAINTS ===
        
        # 1. Meet forecasted demand for each unit/shift type
        self._add_demand_constraints(units, shift_types)
        
        # 2. Each staff member works at most 1 shift per day
        self._add_one_shift_per_day_constraint(units, shift_types)
        
        # 3. Respect staff availability (existing shifts, leave, off-duty)
        self._add_availability_constraints(units, shift_types)
        
        # 4. Skill matching (role → shift type compatibility)
        self._add_skill_constraints(units, shift_types)
        
        # 5. Working Time Directive compliance (48h/week, 11h rest)
        self._add_wtd_constraints(units, shift_types)
        
        logger.info(f"Model built: {len(self.variables)} variables, "
                   f"{len(self.model.constraints)} constraints")
        
        return self.model
    
    def _calculate_staff_costs(self) -> Dict[str, float]:
        """
        Calculate hourly cost for each staff member
        
        Permanent staff: £12-15/hour (role-based)
        Overtime: 1.5× permanent rate
        Agency: 2.0× permanent rate
        
        Returns:
            Dict[sap_number] = hourly_cost
        """
        costs = {}
        
        for staff in self.staff:
            # Base hourly rate by role
            if staff.role:
                if staff.role.name == 'OPERATIONS_MANAGER':
                    base_rate = 18.0
                elif staff.role.name == 'SSCW':
                    base_rate = 15.0
                elif staff.role.name == 'SCW':
                    base_rate = 13.0
                elif staff.role.name == 'SCA':
                    base_rate = 12.0
                else:
                    base_rate = 12.0
            else:
                base_rate = 12.0
            
            # Check if this would be overtime (already worked shifts this week)
            weekly_hours = self._get_weekly_hours(staff)
            
            if weekly_hours >= 40:  # Overtime threshold
                costs[staff.sap] = base_rate * self.COST_OVERTIME
            else:
                costs[staff.sap] = base_rate * self.COST_PERMANENT
        
        return costs
    
    def _get_weekly_hours(self, staff) -> float:
        """
        Get hours already worked this week (for WTD compliance)
        
        Args:
            staff: User instance
        
        Returns:
            Total hours worked Mon-Sun of current week
        """
        # Calculate week start (Monday)
        days_since_monday = self.date.weekday()
        week_start = self.date - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)
        
        # Sum hours from existing shifts
        from scheduling.models import Shift
        
        weekly_shifts = Shift.objects.filter(
            user=staff,
            date__gte=week_start,
            date__lte=week_end,
            status__in=['SCHEDULED', 'CONFIRMED']
        )
        
        total_hours = sum(shift.duration_hours for shift in weekly_shifts)
        return float(total_hours)
    
    def _add_demand_constraints(self, units, shift_types):
        """
        Constraint 1: Meet forecasted demand (with CI bounds)
        
        For each unit/shift_type:
            min_demand ≤ Σ assignments ≤ max_demand
        """
        for unit in units:
            for shift_type in shift_types:
                # Support both formats:
                # 1. {(unit, shift_type): {'min': x, 'max': y}}
                # 2. {unit: {shift_type: (min, max)}}
                demand_key = (unit.name, shift_type)
                if demand_key in self.forecast_demand:
                    demand = self.forecast_demand[demand_key]
                    if isinstance(demand, dict):
                        min_demand = demand.get('min', 0)
                        max_demand = demand.get('max', 0)
                    else:
                        min_demand, max_demand = demand, demand
                else:
                    unit_demand = self.forecast_demand.get(unit.name, {})
                    demand = unit_demand.get(shift_type, (0, 0))
                    if isinstance(demand, tuple):
                        min_demand, max_demand = demand
                    else:
                        min_demand = max_demand = demand
                
                # Minimum demand constraint
                self.model += (
                    lpSum([
                        self.variables[(s.sap, unit.name, shift_type)]
                        for s in self.staff
                    ]) >= min_demand,
                    f"MinDemand_{unit.name}_{shift_type}"
                )
                
                # Maximum demand constraint (don't over-staff)
                self.model += (
                    lpSum([
                        self.variables[(s.sap, unit.name, shift_type)]
                        for s in self.staff
                    ]) <= max_demand + 1,  # Allow 1 extra for flexibility
                    f"MaxDemand_{unit.name}_{shift_type}"
                )
    
    def _add_one_shift_per_day_constraint(self, units, shift_types):
        """
        Constraint 2: Each staff member assigned to ≤1 shift per day
        
        Σ (all units, all shift types) assignments[staff] ≤ 1
        """
        for staff in self.staff:
            self.model += (
                lpSum([
                    self.variables[(staff.sap, u.name, st)]
                    for u in units
                    for st in shift_types
                ]) <= 1,
                f"OneShiftPerDay_{staff.sap}"
            )
    
    def _add_availability_constraints(self, units, shift_types):
        """
        Constraint 3: Respect staff availability
        
        Staff cannot be assigned if:
        - Already has a shift on this date
        - On approved annual leave
        - Marked as unavailable
        """
        from scheduling.models import Shift, LeaveRequest
        
        for staff in self.staff:
            unavailable = False
            
            # Check existing shifts
            existing = Shift.objects.filter(
                user=staff,
                date=self.date,
                status__in=['SCHEDULED', 'CONFIRMED']
            ).exists()
            
            if existing:
                unavailable = True
            
            # Check approved leave
            on_leave = LeaveRequest.objects.filter(
                user=staff,
                start_date__lte=self.date,
                end_date__gte=self.date,
                status='APPROVED'
            ).exists()
            
            if on_leave:
                unavailable = True
            
            # If unavailable, set all assignments to 0
            if unavailable:
                for unit in units:
                    for shift_type in shift_types:
                        self.model += (
                            self.variables[(staff.sap, unit.name, shift_type)] == 0,
                            f"Unavailable_{staff.sap}_{unit.name}_{shift_type}"
                        )
    
    def _add_skill_constraints(self, units, shift_types):
        """
        Constraint 4: Skill/role matching
        
        Staff can only work shifts compatible with their role:
        - SSCW/SCW: DAY_SENIOR, NIGHT_SENIOR
        - SCA: DAY_ASSISTANT, NIGHT_ASSISTANT
        - OM: ADMIN (supernumerary)
        """
        role_shift_compatibility = {
            'OPERATIONS_MANAGER': ['ADMIN'],
            'SSCW': ['DAY_SENIOR', 'NIGHT_SENIOR'],
            'SCW': ['DAY_SENIOR', 'NIGHT_SENIOR'],
            'SCA': ['DAY_ASSISTANT', 'NIGHT_ASSISTANT'],
        }
        
        for staff in self.staff:
            if not staff.role:
                continue
            
            allowed_shifts = role_shift_compatibility.get(staff.role.name, [])
            
            # Block incompatible shift types
            for unit in units:
                for shift_type in shift_types:
                    if shift_type not in allowed_shifts:
                        self.model += (
                            self.variables[(staff.sap, unit.name, shift_type)] == 0,
                            f"SkillMatch_{staff.sap}_{unit.name}_{shift_type}"
                        )
    
    def _add_wtd_constraints(self, units, shift_types):
        """
        Constraint 5: Working Time Directive compliance
        
        - Total weekly hours ≤ 48
        - Minimum 11 hours rest between shifts (checked for yesterday's shift)
        """
        from scheduling.models import Shift
        
        for staff in self.staff:
            # Weekly hours constraint
            weekly_hours = self._get_weekly_hours(staff)
            
            # Hours available this week
            hours_available = self.MAX_HOURS_PER_WEEK - weekly_hours
            
            if hours_available < 8:  # Can't fit even 1 more shift
                # Block all assignments
                for unit in units:
                    for shift_type in shift_types:
                        self.model += (
                            self.variables[(staff.sap, unit.name, shift_type)] == 0,
                            f"WTD_MaxHours_{staff.sap}_{unit.name}_{shift_type}"
                        )
            
            # Rest period constraint (11 hours between shifts)
            # Check if staff worked yesterday
            yesterday = self.date - timedelta(days=1)
            yesterday_shift = Shift.objects.filter(
                user=staff,
                date=yesterday,
                status__in=['SCHEDULED', 'CONFIRMED']
            ).first()
            
            if yesterday_shift:
                # If yesterday was night shift (ends 08:00), can't work early day shift today
                if 'NIGHT' in yesterday_shift.shift_type.name:
                    # Block DAY shifts (start 08:00 - not enough rest)
                    for unit in units:
                        for shift_type in ['DAY_SENIOR', 'DAY_ASSISTANT']:
                            self.model += (
                                self.variables[(staff.sap, unit.name, shift_type)] == 0,
                                f"RestPeriod_{staff.sap}_{unit.name}_{shift_type}"
                            )
    
    def _extract_assignments(self) -> List[Dict]:
        """
        Extract optimal assignments from solved model
        
        Returns:
            List of assignment dicts:
            [
                {
                    'staff_sap': '12345',
                    'staff_name': 'John Doe',
                    'unit': 'HH_ROSE',
                    'shift_type': 'DAY_SENIOR',
                    'date': date(2025, 12, 21),
                    'cost': 180.0,
                    'hours': 12.0
                },
                ...
            ]
        """
        assignments = []
        
        for (staff_sap, unit_name, shift_type), var in self.variables.items():
            if value(var) == 1:  # Assignment made
                # Find staff object
                staff = next((s for s in self.staff if s.sap == staff_sap), None)
                
                if staff:
                    shift_hours = self.SHIFT_HOURS.get(shift_type, 12)
                    staff_costs = self._calculate_staff_costs()
                    cost = staff_costs[staff_sap] * shift_hours
                    
                    assignments.append({
                        'staff_sap': staff_sap,
                        'staff_name': staff.full_name,
                        'unit': unit_name,
                        'shift_type': shift_type,
                        'date': self.date,
                        'cost': cost,
                        'hours': shift_hours,
                        'staff_obj': staff,  # For creating Shift instances
                    })
        
        return assignments
    
    def _calculate_metrics(self, assignments: List[Dict], total_cost: float) -> Dict:
        """
        Calculate transparency metrics for optimization result
        
        Scottish Design: Evidence-based, transparent
        
        Returns:
            Dict with cost breakdown, demand met, staff utilization
        """
        metrics = {
            'total_cost': total_cost,
            'total_assignments': len(assignments),
            'total_hours': sum(a['hours'] for a in assignments),
            'cost_breakdown': {
                'permanent': 0,
                'overtime': 0,
                'agency': 0,
            },
            'demand_met': {},
            'staff_utilization': len(assignments) / len(self.staff) if self.staff else 0,
            'avg_cost_per_shift': total_cost / len(assignments) if assignments else 0,
        }
        
        # Cost breakdown by classification
        for assignment in assignments:
            staff_sap = assignment['staff_sap']
            weekly_hours = self._get_weekly_hours(
                next(s for s in self.staff if s.sap == staff_sap)
            )
            
            if weekly_hours >= 40:
                metrics['cost_breakdown']['overtime'] += assignment['cost']
            else:
                metrics['cost_breakdown']['permanent'] += assignment['cost']
        
        # Demand met analysis
        for unit_name, shift_demand in self.forecast_demand.items():
            metrics['demand_met'][unit_name] = {}
            
            for shift_type, demand in shift_demand.items():
                assigned = sum(
                    1 for a in assignments 
                    if a['unit'] == unit_name and a['shift_type'] == shift_type
                )
                
                if isinstance(demand, tuple):
                    min_demand, max_demand = demand
                else:
                    min_demand = max_demand = demand
                
                metrics['demand_met'][unit_name][shift_type] = {
                    'assigned': assigned,
                    'min_demand': min_demand,
                    'max_demand': max_demand,
                    'met': assigned >= min_demand,
                }
        
        return metrics
    
    def create_shifts(self) -> List:
        """
        Create Shift instances from optimization results
        
        Returns:
            List of created Shift instances
        """
        from scheduling.models import Shift, ShiftType, Unit
        
        if not self.result or not self.result.success:
            raise ValueError("Cannot create shifts - optimization not successful")
        
        created_shifts = []
        
        for assignment in self.result.assignments:
            # Get unit
            unit = Unit.objects.get(name=assignment['unit'])
            
            # Get shift type
            shift_type = ShiftType.objects.get(name=assignment['shift_type'])
            
            # Create shift
            shift = Shift.objects.create(
                user=assignment['staff_obj'],
                unit=unit,
                shift_type=shift_type,
                date=assignment['date'],
                status='SCHEDULED',
                shift_classification='REGULAR',
                notes=f"Auto-generated by optimizer (cost: £{assignment['cost']:.2f})"
            )
            
            created_shifts.append(shift)
            logger.info(f"Created shift: {shift}")
        
        return created_shifts


def optimize_shifts_for_forecast(care_home, forecast_date: date, 
                                 days_ahead: int = 1) -> List[ShiftOptimizationResult]:
    """
    Convenience function to optimize shifts for forecasted demand
    
    Args:
        care_home: CareHome instance
        forecast_date: Starting date for optimization
        days_ahead: Number of days to optimize (default 1)
    
    Returns:
        List of ShiftOptimizationResult objects (one per day)
    """
    from scheduling.models import StaffingForecast, User, Shift
    from scheduling.models_multi_home import CareHome
    
    results = []
    
    for day_offset in range(days_ahead):
        optimization_date = forecast_date + timedelta(days=day_offset)
        
        # Get forecasts for this date
        forecasts = StaffingForecast.objects.filter(
            care_home=care_home,
            forecast_date=optimization_date
        ).select_related('unit')
        
        if not forecasts.exists():
            logger.warning(f"No forecasts found for {care_home} on {optimization_date}")
            continue
        
        # Build demand dictionary
        forecast_demand = {}
        for forecast in forecasts:
            unit_name = forecast.unit.name
            
            if unit_name not in forecast_demand:
                forecast_demand[unit_name] = {}
            
            # Use confidence interval bounds as min/max demand
            # Predicted value ± uncertainty gives staffing range
            min_demand = max(0, int(forecast.confidence_lower))
            max_demand = int(forecast.confidence_upper) + 1
            
            # Assume DAY_SENIOR as primary shift type (can be enhanced)
            shift_type = 'DAY_SENIOR'
            forecast_demand[unit_name][shift_type] = (min_demand, max_demand)
        
        # Get available staff (active, assigned to this care home's units)
        available_staff = User.objects.filter(
            is_active=True,
            unit__care_home=care_home,
            role__isnull=False
        ).distinct()
        
        # Get existing shifts (constraints)
        existing_shifts = Shift.objects.filter(
            date=optimization_date,
            unit__care_home=care_home,
            status__in=['SCHEDULED', 'CONFIRMED']
        )
        
        # Run optimization
        optimizer = ShiftOptimizer(
            care_home=care_home,
            optimization_date=optimization_date,
            forecast_demand=forecast_demand,
            available_staff=list(available_staff),
            existing_shifts=list(existing_shifts)
        )
        
        result = optimizer.optimize()
        results.append(result)
        
        logger.info(f"Optimization complete for {optimization_date}: {result}")
    
    return results
