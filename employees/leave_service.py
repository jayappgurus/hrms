# Leave Management Service
# This module implements the HRMS leave management flow diagram logic
# Refactored to strictly follow the HRMS flow diagram requirements
# 
# FLOW DIAGRAM SEQUENCE:
# Leave Management: Employee Type → Validation → Half-Day Check → Half-Day Processing → Full-Day Processing → Balance Check
# Paid Absence: Eligibility Check → Type Processing (Marriage/Paternity/Maternity)

from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Dict, Tuple, Optional, List
from django.db.models import Sum, Q
from django.utils import timezone
from .models import Employee, LeaveApplication, LeaveType, PublicHoliday


class LeaveValidationResult:
    """
    Result object for leave validation
    Contains validation status, messages, and calculated deduction days
    """
    def __init__(self, is_valid: bool, message: str = "", deduction_days: Decimal = Decimal('0'), 
                 is_sandwich: bool = False, actual_working_days: int = 0):
        self.is_valid = is_valid
        self.message = message
        self.deduction_days = deduction_days
        self.is_sandwich = is_sandwich
        self.actual_working_days = actual_working_days


class LeaveManagementService:
    """
    Service class implementing the HRMS Leave Management flow diagram
    
    FLOW DIAGRAM SEQUENCE:
    1. Employee Type Classification (Restricted vs Regular)
    2. Leave Validation Rules (Annual limits, working days only)
    3. Half-Day WFH + Office Check (reject if both on same day)
    4. Half-Day Leave Processing (5-hour threshold)
    5. Full-Day Leave Processing (Sandwich rule)
    6. Leave Balance Check (final approval gate)
    """

    # ========================================================================
    # LEAVE TYPE CONSTANTS
    # ========================================================================
    # Short codes used internally
    CASUAL_LEAVE = 'casual'
    EMERGENCY_LEAVE = 'emergency'
    BIRTHDAY_LEAVE = 'birthday'
    MARRIAGE_ANNIVERSARY_LEAVE = 'marriage_anniversary'
    CARRY_FORWARD_CL = 'carry_forward_cl'
    PUBLIC_HOLIDAY = 'public_holiday'
    WEEKEND = 'weekend'

    # Mapping from short codes to database names (LeaveType.name field)
    # This mapping is required because the database stores full display names
    LEAVE_TYPE_NAMES = {
        'casual': 'Casual Leave (CL)',
        'emergency': 'Emergency Leave (EL)',
        'birthday': 'Birthday Leave',
        'marriage_anniversary': 'Marriage Anniversary Leave',
        'public_holiday': 'Public Holidays',
        'weekend': 'Weekends',
        'absence_marriage': 'Absence for Marriage',
        'paternity': 'Paternity',
        'maternity': 'Maternity',
    }

    # ========================================================================
    # FLOW DIAGRAM STEP 1: RESTRICTED LEAVE TYPES
    # ========================================================================
    # These leave types are REJECTED for Trainee/Intern/Probation/Notice period employees
    RESTRICTED_LEAVE_TYPES = [
        CASUAL_LEAVE,
        EMERGENCY_LEAVE,
        BIRTHDAY_LEAVE,
        MARRIAGE_ANNIVERSARY_LEAVE,
        CARRY_FORWARD_CL,
    ]

    # ========================================================================
    # FLOW DIAGRAM STEP 2: ANNUAL LEAVE ALLOCATIONS
    # ========================================================================
    ANNUAL_ALLOCATIONS = {
        CASUAL_LEAVE: 12,  # 1 per month accrual (not all 12 at once)
        EMERGENCY_LEAVE: 4,
        BIRTHDAY_LEAVE: 1,
        MARRIAGE_ANNIVERSARY_LEAVE: 1,
        PUBLIC_HOLIDAY: 15,  # 15 public holidays per year
    }

    # ========================================================================
    # EMPLOYEE TYPE CLASSIFICATIONS
    # ========================================================================
    RESTRICTED_EMPLOYEE_TYPES = ['trainee', 'intern', 'probation', 'notice_period']
    REGULAR_EMPLOYEE_TYPE = 'confirmed'

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    @staticmethod
    def get_leave_type_name(leave_type_code: str) -> str:
        """
        Convert leave type code to database name.
        Falls back to the code itself if not found in mapping.
        
        Args:
            leave_type_code: Short code like 'casual', 'emergency'
            
        Returns:
            Database name like 'Casual Leave (CL)', 'Emergency Leave (EL)'
        """
        return LeaveManagementService.LEAVE_TYPE_NAMES.get(leave_type_code, leave_type_code)

    @staticmethod
    def is_weekend(check_date: date) -> bool:
        """
        Check if date is weekend (Saturday=5, Sunday=6)
        Weekends are non-working days and excluded from leave calculations
        
        FLOW DIAGRAM: Weekends are counted as non-working days
        """
        return check_date.weekday() in [5, 6]

    @staticmethod
    def is_public_holiday(check_date: date, country: str = 'IN') -> bool:
        """
        Check if date is a public holiday
        Public holidays are non-working days and excluded from leave calculations
        
        FLOW DIAGRAM: Public holidays are counted as non-working days
        """
        return PublicHoliday.objects.filter(
            date=check_date,
            country=country,
            is_active=True
        ).exists()

    @staticmethod
    def is_working_day(check_date: date, country: str = 'IN') -> bool:
        """
        Helper to determine if a day is a working day
        Working day = NOT (weekend OR public holiday)
        """
        return not (LeaveManagementService.is_weekend(check_date) or
                    LeaveManagementService.is_public_holiday(check_date, country))

    @staticmethod
    def count_working_days(start_date: date, end_date: date, country: str = 'IN') -> int:
        """
        FLOW DIAGRAM REQUIREMENT: Count only working days
        Exclude weekends (Saturday & Sunday) and public holidays
        
        This is used in leave calculations to ensure only actual working days are counted
        """
        working_days = 0
        current_date = start_date

        while current_date <= end_date:
            if LeaveManagementService.is_working_day(current_date, country):
                working_days += 1
            current_date += timedelta(days=1)

        return working_days

    # ========================================================================
    # FLOW DIAGRAM STEP 1: EMPLOYEE TYPE CLASSIFICATION
    # ========================================================================

    @staticmethod
    def identify_employee_type(employee: Employee) -> str:
        """
        FLOW DIAGRAM STEP 1: Identify Employee Type
        First decision point in the leave management flow
        
        Decision Logic:
        - If employee.period_type in [trainee, intern, probation, notice_period] → 'restricted'
        - If employee.period_type = confirmed → 'regular'
        
        Returns:
            'restricted' - for Trainee/Intern/Probation/Notice period
            'regular' - for Confirmed employees
        """
        if employee.period_type in LeaveManagementService.RESTRICTED_EMPLOYEE_TYPES:
            return 'restricted'
        return 'regular'

    # ========================================================================
    # FLOW DIAGRAM STEP 2: LEAVE VALIDATION RULES
    # ========================================================================

    @staticmethod
    def validate_request_dates(start_date: date, end_date: date, country: str = 'IN') -> Tuple[bool, str]:
        """
        FLOW DIAGRAM STEP 2: Strict Date Validation
        
        CRITICAL RULE: Reject leave if it falls on a Weekend or Public Holiday
        Employees must apply for working days only
        
        Returns:
            (True, "") if all dates are working days
            (False, error_message) if any weekend or holiday found
        """
        # Check for Public Holidays in the range
        holidays_in_range = PublicHoliday.objects.filter(
            date__range=[start_date, end_date],
            country=country,
            is_active=True
        )
        if holidays_in_range.exists():
            holiday_names = ", ".join([f"{h.name} ({h.date.strftime('%d-%m-%Y')})" for h in holidays_in_range])
            return False, f"❌ Leave request rejected. The selected range includes Public Holiday(s): {holiday_names}. Please apply for working days only."

        # Check for Weekends in the range
        current_date = start_date
        while current_date <= end_date:
            if LeaveManagementService.is_weekend(current_date):
                return False, f"❌ Leave request rejected. The selected range includes a Weekend ({current_date.strftime('%A, %d-%m-%Y')}). Please apply for working days only."
            current_date += timedelta(days=1)

        return True, ""

    @staticmethod
    def check_annual_limit(employee: Employee, leave_type_code: str, year: int = None) -> Tuple[bool, str]:
        """
        FLOW DIAGRAM STEP 2: Leave Validation Rules (Regular Employees Only)
        
        Validation Rules:
        - Birthday Leave: Maximum 1 per year only
        - Marriage Anniversary Leave: Maximum 1 per year only
        
        Returns:
            (True, "") if within limits
            (False, error_message) if limit exceeded
        """
        if year is None:
            year = timezone.now().year

        if leave_type_code == LeaveManagementService.BIRTHDAY_LEAVE:
            leave_type_name = LeaveManagementService.get_leave_type_name(leave_type_code)
            count = LeaveApplication.objects.filter(
                employee=employee,
                leave_type__name=leave_type_name,
                status='approved',
                start_date__year=year
            ).count()

            if count >= 1:
                return False, "❌ Birthday Leave: Maximum 1 per year already used."

        elif leave_type_code == LeaveManagementService.MARRIAGE_ANNIVERSARY_LEAVE:
            leave_type_name = LeaveManagementService.get_leave_type_name(leave_type_code)
            count = LeaveApplication.objects.filter(
                employee=employee,
                leave_type__name=leave_type_name,
                status='approved',
                start_date__year=year
            ).count()

            if count >= 1:
                return False, "❌ Marriage Anniversary Leave: Maximum 1 per year already used."

        return True, ""

    # ========================================================================
    # FLOW DIAGRAM STEP 3: HALF-DAY WFH + OFFICE CHECK
    # ========================================================================

    @staticmethod
    def check_half_day_wfh_office_same_day(leave_request: Dict) -> Tuple[bool, str]:
        """
        FLOW DIAGRAM STEP 3: Half-Day WFH + Office Check
        
        CRITICAL RULE: Check if request is "Half-Day WFH + Half-Day Office on SAME day"
        - If YES → Reject Request
        - If NO → Continue to half-day leave processing
        
        Returns:
            (True, "") if valid (not both WFH and Office)
            (False, error_message) if both WFH and Office on same day
        """
        is_half_day = leave_request.get('is_half_day', False)
        is_wfh = leave_request.get('is_wfh', False)
        is_office = leave_request.get('is_office', False)

        if is_half_day and is_wfh and is_office:
            return False, "❌ Cannot combine half-day WFH and half-day office on the same day in a single request."

        return True, ""

    # ========================================================================
    # FLOW DIAGRAM STEP 4: HALF-DAY LEAVE PROCESSING
    # ========================================================================

    @staticmethod
    def calculate_half_day_deduction(scheduled_hours: Decimal) -> Decimal:
        """
        FLOW DIAGRAM STEP 4: Half-Day Leave Processing
        
        Check scheduled working hours (excluding break):
        - If scheduled hours ≥ 5 hours → Deduct 0.5 day leave
        - If scheduled hours < 5 hours → Deduct 1 full day
        
        Args:
            scheduled_hours: Working hours scheduled (excluding break time)
            
        Returns:
            Decimal: 0.5 or 1.0 days to deduct
        """
        if scheduled_hours >= Decimal('5.0'):
            return Decimal('0.5')
        else:
            return Decimal('1.0')

    # ========================================================================
    # FLOW DIAGRAM STEP 5: FULL-DAY LEAVE PROCESSING (SANDWICH RULE)
    # ========================================================================

    @staticmethod
    def has_approved_leave_on_date(employee: Employee, check_date: date) -> bool:
        """
        Check if employee has an approved leave on the specific date
        Used for sandwich rule detection
        """
        return LeaveApplication.objects.filter(
            employee=employee,
            status='approved',
            start_date__lte=check_date,
            end_date__gte=check_date
        ).exists()

    @staticmethod
    def check_sandwich_rule(employee: Employee, start_date: date, end_date: date, country: str = 'IN') -> Tuple[bool, int, int]:
        """
        FLOW DIAGRAM STEP 5: Full Day Leave Processing - Sandwich Rule
        
        CRITICAL RULE: Check if leave is taken before AND after weekend/holiday
        - If YES (sandwich detected) → Include non-working days in deduction
        - If NO → Deduct only working days
        
        Sandwich Detection Logic:
        1. Count actual working days in the leave period
        2. Check for non-working days BEFORE start_date
        3. Check for non-working days AFTER end_date
        4. If employee has approved leave on the other side of non-working days,
           then those non-working days are "sandwiched" and must be included
        
        Returns:
            (is_sandwich, total_deduction_days, actual_working_days)
        """
        # Count actual working days in the requested period
        actual_working_days = LeaveManagementService.count_working_days(start_date, end_date, country)
        sandwiched_days_count = 0

        # --- Check for Non-working days ADJACENT to the request ---

        # Check BEFORE start_date
        check_date = start_date - timedelta(days=1)
        adjacent_sandwich_before = 0

        # Count consecutive non-working days before start_date
        while not LeaveManagementService.is_working_day(check_date, country):
            adjacent_sandwich_before += 1
            check_date -= timedelta(days=1)

        # If there are non-working days before, check if employee has leave on the other side
        if adjacent_sandwich_before > 0:
            if LeaveManagementService.has_approved_leave_on_date(employee, check_date):
                sandwiched_days_count += adjacent_sandwich_before

        # Check AFTER end_date
        check_date = end_date + timedelta(days=1)
        adjacent_sandwich_after = 0

        # Count consecutive non-working days after end_date
        while not LeaveManagementService.is_working_day(check_date, country):
            adjacent_sandwich_after += 1
            check_date += timedelta(days=1)

        # If there are non-working days after, check if employee has leave on the other side
        if adjacent_sandwich_after > 0:
            if LeaveManagementService.has_approved_leave_on_date(employee, check_date):
                sandwiched_days_count += adjacent_sandwich_after

        is_sandwich = sandwiched_days_count > 0
        total_deduction = actual_working_days + sandwiched_days_count

        return is_sandwich, total_deduction, actual_working_days

    # ========================================================================
    # FLOW DIAGRAM STEP 6: LEAVE BALANCE CHECK
    # ========================================================================

    @staticmethod
    def get_leave_balance(employee: Employee, leave_type_code: str, year: int = None) -> Decimal:
        """
        FLOW DIAGRAM STEP 6: Calculate remaining leave balance for an employee
        Used in final balance check before approval
        
        Leave Allocation Rules:
        - Casual Leave (CL): Accrues at 1 per month (not all 12 at once)
        - Emergency Leave (EL): Full 4 days available at year start
        - Birthday Leave: 1 per year
        - Marriage Anniversary: 1 per year
        
        Formula: Balance = Allocated - Used
        
        Returns:
            Decimal: Available leave balance
        """
        if year is None:
            year = timezone.now().year

        # Get annual allocation
        annual_allocation = LeaveManagementService.ANNUAL_ALLOCATIONS.get(leave_type_code, 0)

        # For Casual Leave, calculate accrued balance based on months worked
        if leave_type_code == LeaveManagementService.CASUAL_LEAVE:
            # Calculate months worked in current year
            current_date = timezone.now().date()

            # If employee joined this year, calculate from joining date
            if employee.joining_date and employee.joining_date.year == year:
                start_month = employee.joining_date.month
            else:
                start_month = 1

            # Current month calculation
            if year > current_date.year:  # Future year, 0 accrual
                months_worked = 0
            elif year < current_date.year:  # Past year, full accrual
                months_worked = 12
            else:  # Current year
                months_worked = current_date.month - start_month + 1

            # Accrued leaves = months worked (max 12)
            accrued_leaves = max(0, min(months_worked, 12))

            # Get total approved leaves for this year
            leave_type_name = LeaveManagementService.get_leave_type_name(leave_type_code)
            approved_leaves = LeaveApplication.objects.filter(
                employee=employee,
                leave_type__name=leave_type_name,
                status='approved',
                start_date__year=year
            ).aggregate(total=Sum('total_days'))['total']

            # Handle None case
            if approved_leaves is None:
                approved_leaves = 0

            # Calculate balance (accrued - used)
            balance = Decimal(str(accrued_leaves)) - Decimal(str(approved_leaves))

            return balance
        else:
            # For other leave types, full annual allocation is available
            leave_type_name = LeaveManagementService.get_leave_type_name(leave_type_code)
            approved_leaves = LeaveApplication.objects.filter(
                employee=employee,
                leave_type__name=leave_type_name,
                status='approved',
                start_date__year=year
            ).aggregate(total=Sum('total_days'))['total']

            # Handle None case
            if approved_leaves is None:
                approved_leaves = 0

            # Calculate balance
            balance = Decimal(str(annual_allocation)) - Decimal(str(approved_leaves))

            return balance

    @staticmethod
    def get_casual_leave_accrual_info(employee: Employee, year: int = None) -> Dict:
        """
        Get detailed accrual information for casual leave
        Useful for displaying to users why they have certain balance
        
        Returns:
            Dict with keys: accrued, used, available, months_worked
        """
        if year is None:
            year = timezone.now().year

        current_date = timezone.now().date()

        if employee.joining_date and employee.joining_date.year == year:
            start_month = employee.joining_date.month
        else:
            start_month = 1

        if year > current_date.year:
            months_worked = 0
        elif year < current_date.year:
            months_worked = 12
        else:
            months_worked = current_date.month - start_month + 1

        accrued_leaves = max(0, min(months_worked, 12))

        leave_type_name = LeaveManagementService.get_leave_type_name(LeaveManagementService.CASUAL_LEAVE)
        approved_leaves = LeaveApplication.objects.filter(
            employee=employee,
            leave_type__name=leave_type_name,
            status='approved',
            start_date__year=year
        ).aggregate(total=Sum('total_days'))['total'] or 0

        available = accrued_leaves - approved_leaves

        return {
            'accrued': accrued_leaves,
            'used': approved_leaves,
            'available': available,
            'months_worked': months_worked
        }

    # ========================================================================
    # MAIN PROCESSING FUNCTION
    # ========================================================================

    @staticmethod
    def process_leave_request(employee: Employee, leave_request: Dict) -> LeaveValidationResult:
        """
        MAIN FUNCTION: Process leave request following the exact flow diagram sequence
        
        FLOW DIAGRAM SEQUENCE:
        1. Employee Type Classification → Reject restricted employees for certain leave types
        2. Date Validation → Reject if weekends/holidays included
        3. Leave Validation Rules → Check annual limits (Birthday, Anniversary)
        4. Half-Day WFH + Office Check → Reject if both on same day
        5. Half-Day or Full-Day Processing → Calculate deduction
        6. Leave Balance Check → Final approval gate
        
        Args:
            employee: Employee object
            leave_request: Dict with keys:
                - leave_type_code: str (e.g., 'casual', 'emergency')
                - start_date: date
                - end_date: date
                - is_half_day: bool
                - scheduled_hours: Decimal (for half-day)
                - is_wfh: bool
                - is_office: bool
                
        Returns:
            LeaveValidationResult with validation status and details
        """
        leave_type_code = leave_request.get('leave_type_code')
        start_date = leave_request.get('start_date')
        end_date = leave_request.get('end_date')
        is_half_day = leave_request.get('is_half_day', False)

        # ====================================================================
        # STEP 1: IDENTIFY EMPLOYEE TYPE
        # ====================================================================
        # First decision point: Regular Employee OR Trainee/Intern/Probation/Notice period
        employee_type = LeaveManagementService.identify_employee_type(employee)

        # If restricted employee, reject for restricted leave types
        if employee_type == 'restricted' and leave_type_code in LeaveManagementService.RESTRICTED_LEAVE_TYPES:
            leave_type_display = {
                'casual': 'Casual Leave (CL)',
                'emergency': 'Emergency Leave (EL)',
                'birthday': 'Birthday Leave',
                'marriage_anniversary': 'Marriage Anniversary Leave',
                'carry_forward_cl': 'Carry Forward CL'
            }.get(leave_type_code, leave_type_code)

            return LeaveValidationResult(
                is_valid=False,
                message=f"❌ Trainees/Interns/Probation/Notice period employees are not eligible for {leave_type_display}. Only confirmed employees can apply for this leave type."
            )

        # ====================================================================
        # STEP 2: STRICT DATE VALIDATION (WEEKENDS & HOLIDAYS)
        # ====================================================================
        # Reject leave if it falls on a Weekend or Public Holiday
        is_valid, message = LeaveManagementService.validate_request_dates(start_date, end_date, country='IN')
        if not is_valid:
            return LeaveValidationResult(is_valid=False, message=message)

        # ====================================================================
        # STEP 3: LEAVE VALIDATION RULES (REGULAR EMPLOYEES ONLY)
        # ====================================================================
        # Check annual limits for Birthday and Marriage Anniversary leaves
        if employee_type == 'regular':
            is_valid, message = LeaveManagementService.check_annual_limit(employee, leave_type_code, start_date.year)
            if not is_valid:
                return LeaveValidationResult(is_valid=False, message=message)

        # ====================================================================
        # STEP 4: CHECK HALF-DAY WFH + OFFICE SAME DAY
        # ====================================================================
        # Reject if request is "Half-Day WFH + Half-Day Office on SAME day"
        is_valid, message = LeaveManagementService.check_half_day_wfh_office_same_day(leave_request)
        if not is_valid:
            return LeaveValidationResult(is_valid=False, message=message)

        # ====================================================================
        # STEP 5 & 6: HALF-DAY OR FULL-DAY LEAVE PROCESSING
        # ====================================================================
        is_sandwich = False
        actual_working_days = 0

        if is_half_day:
            # STEP 5: Half-Day Leave Processing
            # Check scheduled hours: ≥5 hours → 0.5 day, <5 hours → 1 day
            scheduled_hours = leave_request.get('scheduled_hours', Decimal('8.0'))
            deduction_days = LeaveManagementService.calculate_half_day_deduction(scheduled_hours)
            actual_working_days = 0
        else:
            # STEP 6: Full-Day Leave Processing - Sandwich Rule
            # Check if leave is taken before AND after weekend/holiday
            is_sandwich, total_days, actual_working_days = LeaveManagementService.check_sandwich_rule(
                employee, start_date, end_date, country='IN'
            )
            deduction_days = Decimal(str(total_days))

        # ====================================================================
        # STEP 7: LEAVE BALANCE CHECK
        # ====================================================================
        # Verify sufficient leave balance available
        current_balance = LeaveManagementService.get_leave_balance(employee, leave_type_code, year=start_date.year)

        if current_balance < deduction_days:
            # Insufficient balance - Reject request
            error_msg = f"❌ Insufficient leave balance. Available: {current_balance} days, Required: {deduction_days} days."

            # For Casual Leave, provide detailed accrual information
            if leave_type_code == LeaveManagementService.CASUAL_LEAVE:
                casual_info = LeaveManagementService.get_casual_leave_accrual_info(employee, year=start_date.year)
                error_msg = (
                    f"❌ Insufficient Casual Leave Balance. "
                    f"Accrual Rule: 1 day per month. "
                    f"Months Worked: {casual_info['months_worked']}, "
                    f"Accrued: {casual_info['accrued']} days, "
                    f"Used: {casual_info['used']} days, "
                    f"Available: {casual_info['available']} days. "
                    f"Required: {deduction_days} days. "
                    f"Please apply for Loss of Pay for excess days."
                )

            return LeaveValidationResult(
                is_valid=False,
                message=error_msg
            )

        # ====================================================================
        # ALL CHECKS PASSED - APPROVE
        # ====================================================================
        approval_message = "✓ Leave request approved"
        if is_sandwich:
            approval_message += f" (Sandwich leave detected: {deduction_days} days will be deducted including bridged non-working days)"

        return LeaveValidationResult(
            is_valid=True,
            message=approval_message,
            deduction_days=deduction_days,
            is_sandwich=is_sandwich,
            actual_working_days=actual_working_days
        )


# ============================================================================
# PAID ABSENCE MODULE
# ============================================================================

class PaidAbsenceService:
    """
    Service class implementing the HRMS Paid Absence flow diagram
    
    FLOW DIAGRAM SEQUENCE:
    1. Employee Eligibility Check (Sequential checks)
       1.1 Identify employee type (Trainee/Intern → Reject)
       1.2 Check employment phase (Probation/Notice → Reject)
       1.3 Check tenure (< 1 year → Reject)
       1.4 Check disciplinary record (Issues → Reject)
    2. Paid Absence Type Processing
       - Marriage Leave: 2 days paid
       - Paternity Leave: 5 days paid (first child only)
       - Maternity Leave: 8 weeks paid (first child only)
    """

    # ========================================================================
    # PAID ABSENCE TYPE CONSTANTS
    # ========================================================================
    MARRIAGE_LEAVE = 'absence_marriage'
    PATERNITY_LEAVE = 'paternity'
    MATERNITY_LEAVE = 'maternity'

    # ========================================================================
    # FLOW DIAGRAM STEP 1.4: DISCIPLINARY ISSUES
    # ========================================================================
    # These disciplinary issues disqualify employees from paid absence
    DISCIPLINARY_ISSUES = [
        'disciplinary_exit',
        'misconduct_case',
        'inappropriate_work',
        'destructive_issue',
    ]

    # ========================================================================
    # FLOW DIAGRAM STEP 1: EMPLOYEE ELIGIBILITY CHECK
    # ========================================================================

    @staticmethod
    def check_employee_eligibility(employee: Employee) -> Tuple[bool, str]:
        """
        FLOW DIAGRAM STEP 1: Employee Eligibility Check
        Sequential checks that must ALL pass for eligibility
        
        Check Sequence:
        1. Identify employee type
           - If Trainee/Intern → Reject (not eligible for paid leave)
        2. Check employment phase
           - If Probation/Notice period → Reject (not eligible)
           - If Regular → Continue
        3. Check tenure
           - If completed < 1 year in company → Reject (not eligible)
           - If ≥ 1 year → Continue
        4. Check disciplinary record
           - If ANY disciplinary issues exist → Reject (not eligible)
           - If clean record → Eligible
        
        Returns:
            (True, success_message) if eligible
            (False, rejection_reason) if not eligible
        """
        # ====================================================================
        # CHECK 1.1: IDENTIFY EMPLOYEE TYPE
        # ====================================================================
        if employee.period_type in ['trainee', 'intern']:
            return False, (
                "❌ Trainees and Interns are not eligible for paid absence. "
                "Only confirmed employees with at least 1 year tenure are eligible."
            )

        # ====================================================================
        # CHECK 1.2: CHECK EMPLOYMENT PHASE
        # ====================================================================
        if employee.period_type in ['probation', 'notice_period']:
            return False, (
                "❌ Employees on Probation or Notice period are not eligible for paid absence. "
                "Only confirmed employees with at least 1 year tenure are eligible."
            )

        # ====================================================================
        # CHECK 1.3: CHECK TENURE (MINIMUM 1 YEAR)
        # ====================================================================
        if employee.joining_date:
            tenure_days = (timezone.now().date() - employee.joining_date).days
            tenure_years = tenure_days / 365.25

            if tenure_years < 1:
                remaining_days = int(365.25 - tenure_days)
                return False, (
                    f"❌ Employee must complete at least 1 year in company to be eligible for paid absence. "
                    f"You need {remaining_days} more days to complete 1 year."
                )

        # ====================================================================
        # CHECK 1.4: CHECK DISCIPLINARY RECORD
        # ====================================================================
        # Note: This check would require a disciplinary record model
        # For now, we assume clean record if employee reached this point
        # In production, you would check:
        # if employee.disciplinary_records.filter(issue_type__in=DISCIPLINARY_ISSUES).exists():
        #     return False, "❌ Employees with disciplinary issues are not eligible for paid absence."

        # ====================================================================
        # ALL CHECKS PASSED - EMPLOYEE IS ELIGIBLE
        # ====================================================================
        return True, "✓ Employee is eligible for paid absence"

    # ========================================================================
    # HELPER METHOD: CHECK FIRST CHILD
    # ========================================================================

    @staticmethod
    def is_first_child(employee: Employee, leave_application: 'LeaveApplication' = None) -> bool:
        """
        Check if this is for the first child
        Used for Paternity and Maternity leave validation
        
        Logic:
        - Check if employee has any previous approved Paternity or Maternity leaves
        - If yes → Not first child
        - If no → First child
        
        Args:
            employee: Employee object
            leave_application: Current leave application (to exclude from check)
            
        Returns:
            True if first child, False otherwise
        """
        if leave_application:
            paternity_name = LeaveManagementService.get_leave_type_name(PaidAbsenceService.PATERNITY_LEAVE)
            maternity_name = LeaveManagementService.get_leave_type_name(PaidAbsenceService.MATERNITY_LEAVE)
            
            previous_leaves = LeaveApplication.objects.filter(
                employee=employee,
                leave_type__name__in=[paternity_name, maternity_name],
                status='approved'
            ).exclude(id=leave_application.id if leave_application.id else None).exists()
            
            return not previous_leaves
        return True

    # ========================================================================
    # FLOW DIAGRAM STEP 2: PAID ABSENCE TYPE PROCESSING
    # ========================================================================

    @staticmethod
    def process_marriage_leave(employee: Employee) -> LeaveValidationResult:
        """
        FLOW DIAGRAM STEP 2: Marriage Leave Processing
        
        Rules:
        - Approve 2 days paid leave/absence for marriage
        - Must pass eligibility check first
        
        Returns:
            LeaveValidationResult with approval or rejection
        """
        # Check eligibility first
        is_eligible, message = PaidAbsenceService.check_employee_eligibility(employee)
        if not is_eligible:
            return LeaveValidationResult(is_valid=False, message=message)

        # Approve 2 days paid leave
        return LeaveValidationResult(
            is_valid=True,
            message="✓ Marriage Leave approved: 2 days paid absence",
            deduction_days=Decimal('2.0')
        )

    @staticmethod
    def process_paternity_leave(employee: Employee, is_first_child: bool = True) -> LeaveValidationResult:
        """
        FLOW DIAGRAM STEP 2: Paternity Leave Processing
        
        Rules:
        - Check: Is it for birth/adoption of FIRST child?
        - If NO → Reject (only first child eligible)
        - If YES → Approve 5 continuous days paid leave
        
        Returns:
            LeaveValidationResult with approval or rejection
        """
        # Check eligibility first
        is_eligible, message = PaidAbsenceService.check_employee_eligibility(employee)
        if not is_eligible:
            return LeaveValidationResult(is_valid=False, message=message)

        # Check if first child
        if not is_first_child:
            return LeaveValidationResult(
                is_valid=False,
                message=(
                    "❌ Paternity Leave is only available for the birth/adoption of FIRST child. "
                    "This benefit has already been used or is not applicable."
                )
            )

        # Approve 5 days paid leave
        return LeaveValidationResult(
            is_valid=True,
            message="✓ Paternity Leave approved: 5 continuous days paid leave for first child",
            deduction_days=Decimal('5.0')
        )

    @staticmethod
    def process_maternity_leave(employee: Employee, is_first_child: bool = True) -> LeaveValidationResult:
        """
        FLOW DIAGRAM STEP 2: Maternity Leave Processing
        
        Rules:
        - Check: Is it for birth/adoption of FIRST child?
        - If NO → Reject (only first child eligible)
        - If YES → Approve 8 weeks paid leave
        
        Returns:
            LeaveValidationResult with approval or rejection
        """
        # Check eligibility first
        is_eligible, message = PaidAbsenceService.check_employee_eligibility(employee)
        if not is_eligible:
            return LeaveValidationResult(is_valid=False, message=message)

        # Check if first child
        if not is_first_child:
            return LeaveValidationResult(
                is_valid=False,
                message=(
                    "❌ Maternity Leave is only available for the birth/adoption of FIRST child. "
                    "This benefit has already been used or is not applicable."
                )
            )

        # Approve 8 weeks (56 days) paid leave
        return LeaveValidationResult(
            is_valid=True,
            message="✓ Maternity Leave approved: 8 weeks (56 days) paid leave for first child",
            deduction_days=Decimal('56.0')
        )

    # ========================================================================
    # MAIN PROCESSING FUNCTION
    # ========================================================================

    @staticmethod
    def process_paid_absence_request(employee: Employee, absence_type: str, is_first_child: bool = True) -> LeaveValidationResult:
        """
        MAIN FUNCTION: Process paid absence request
        
        Routes to appropriate handler based on absence type:
        - Marriage Leave → 2 days
        - Paternity Leave → 5 days (first child only)
        - Maternity Leave → 8 weeks (first child only)
        
        Args:
            employee: Employee object
            absence_type: Type of paid absence ('absence_marriage', 'paternity', 'maternity')
            is_first_child: Boolean flag for paternity/maternity (default True)
            
        Returns:
            LeaveValidationResult with approval or rejection
        """
        if absence_type == PaidAbsenceService.MARRIAGE_LEAVE:
            return PaidAbsenceService.process_marriage_leave(employee)
        elif absence_type == PaidAbsenceService.PATERNITY_LEAVE:
            return PaidAbsenceService.process_paternity_leave(employee, is_first_child)
        elif absence_type == PaidAbsenceService.MATERNITY_LEAVE:
            return PaidAbsenceService.process_maternity_leave(employee, is_first_child)
        else:
            return LeaveValidationResult(
                is_valid=False,
                message=f"❌ Unknown paid absence type: {absence_type}. Valid types are: Marriage, Paternity, Maternity."
            )
