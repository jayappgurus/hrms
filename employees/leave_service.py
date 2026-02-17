# Leave Management Service
# This module implements the HRMS leave management flow diagram logic
# Refactored to strictly follow the HRMS flow diagram requirements

from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Dict, Tuple, Optional, List
from django.db.models import Sum, Q
from django.utils import timezone
from .models import Employee, LeaveApplication, LeaveType, PublicHoliday

class LeaveValidationResult:
    """Result object for leave validation"""
    def __init__(self, is_valid: bool, message: str = "", deduction_days: Decimal = Decimal('0'), is_sandwich: bool = False, actual_working_days: int = 0):
        self.is_valid = is_valid
        self.message = message
        self.deduction_days = deduction_days
        self.is_sandwich = is_sandwich
        self.actual_working_days = actual_working_days

class LeaveManagementService:
    """
    Service class implementing the HRMS Leave Management flow diagram
    Follows exact sequence: Employee Type → Validation → Half-Day Check → Half-Day Processing → Full-Day Processing → Balance Check
    """

    # Leave type constants
    CASUAL_LEAVE = 'casual'
    EMERGENCY_LEAVE = 'emergency'
    BIRTHDAY_LEAVE = 'birthday'
    MARRIAGE_ANNIVERSARY_LEAVE = 'marriage_anniversary'
    CARRY_FORWARD_CL = 'carry_forward_cl'
    PUBLIC_HOLIDAY = 'public_holiday'
    WEEKEND = 'weekend'

    # Restricted leave types for trainees/interns/probation/notice period
    # FLOW DIAGRAM STEP 1: These leave types are REJECTED for restricted employees
    RESTRICTED_LEAVE_TYPES = [
        CASUAL_LEAVE,
        EMERGENCY_LEAVE,
        BIRTHDAY_LEAVE,
        MARRIAGE_ANNIVERSARY_LEAVE,
        CARRY_FORWARD_CL,
    ]

    # Annual leave allocations - FLOW DIAGRAM STEP 2
    ANNUAL_ALLOCATIONS = {
        CASUAL_LEAVE: 12,  # 1 per month accrual
        EMERGENCY_LEAVE: 4,
        BIRTHDAY_LEAVE: 1,
        MARRIAGE_ANNIVERSARY_LEAVE: 1,
        PUBLIC_HOLIDAY: 15,  # 15 public holidays per year
    }

    # Employee type classifications - FLOW DIAGRAM STEP 1
    RESTRICTED_EMPLOYEE_TYPES = ['trainee', 'intern', 'probation', 'notice_period']
    REGULAR_EMPLOYEE_TYPE = 'confirmed'

    @staticmethod
    def identify_employee_type(employee: Employee) -> str:
        """
        FLOW DIAGRAM STEP 1: Identify Employee Type
        First decision point in the flow

        Returns:
            'restricted' - for Trainee/Intern/Probation/Notice period
            'regular' - for Confirmed employees
        """
        if employee.period_type in LeaveManagementService.RESTRICTED_EMPLOYEE_TYPES:
            return 'restricted'
        return 'regular'

    @staticmethod
    def is_weekend(check_date: date) -> bool:
        """
        Check if date is weekend (Saturday=5, Sunday=6)
        Weekends are non-working days and excluded from leave calculations
        """
        return check_date.weekday() in [5, 6]

    @staticmethod
    def is_public_holiday(check_date: date, country: str = 'IN') -> bool:
        """
        Check if date is a public holiday
        Public holidays are non-working days and excluded from leave calculations
        """
        return PublicHoliday.objects.filter(
            date=check_date,
            country=country,
            is_active=True
        ).exists()

    @staticmethod
    def is_working_day(check_date: date, country: str = 'IN') -> bool:
        """Helper to determine if a day is a working day"""
        return not (LeaveManagementService.is_weekend(check_date) or
                    LeaveManagementService.is_public_holiday(check_date, country))

    @staticmethod
    def validate_request_dates(start_date: date, end_date: date, country: str = 'IN') -> Tuple[bool, str]:
        """
        Strict Rule: Reject leave if it falls on a Weekend or Public Holiday
        """
        # 1. Check for Public Holidays in the range
        holidays_in_range = PublicHoliday.objects.filter(
            date__range=[start_date, end_date],
            country=country,
            is_active=True
        )
        if holidays_in_range.exists():
            holiday_names = ", ".join([f"{h.name} ({h.date.strftime('%d-%m-%Y')})" for h in holidays_in_range])
            return False, f"❌ Leave request rejected. The selected range includes Public Holiday(s): {holiday_names}. Please apply for working days only."

        # 2. Check for Weekends in the range
        current_date = start_date
        while current_date <= end_date:
            if LeaveManagementService.is_weekend(current_date):
                 return False, f"❌ Leave request rejected. The selected range includes a Weekend ({current_date.strftime('%A, %d-%m-%Y')}). Please apply for working days only."
            current_date += timedelta(days=1)

        return True, ""

    @staticmethod
    def count_working_days(start_date: date, end_date: date, country: str = 'IN') -> int:
        """
        FLOW DIAGRAM REQUIREMENT: Count only working days
        Exclude weekends (Saturday & Sunday) and public holidays
        """
        working_days = 0
        current_date = start_date

        while current_date <= end_date:
            if LeaveManagementService.is_working_day(current_date, country):
                working_days += 1
            current_date += timedelta(days=1)

        return working_days


    @staticmethod
    def get_leave_balance(employee: Employee, leave_type_code: str, year: int = None) -> Decimal:
        """
        FLOW DIAGRAM STEP 6: Calculate remaining leave balance for an employee
        Used in final balance check before approval

        For Casual Leave: Accrues at 1 per month (not all 12 at once)
        For other leaves: Full annual allocation available
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

            # Current month
            if year > current_date.year: # Future year, 0 accrual
                months_worked = 0
            elif year < current_date.year: # Past year, full accrual logic
                months_worked = 12 # Simplified
            else:
                months_worked = current_date.month - start_month + 1

            accrued_leaves = max(0, min(months_worked, 12))

            # Get total approved leaves for this year
            approved_leaves = LeaveApplication.objects.filter(
                employee=employee,
                leave_type__leave_type=leave_type_code,
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
            approved_leaves = LeaveApplication.objects.filter(
                employee=employee,
                leave_type__leave_type=leave_type_code,
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

        approved_leaves = LeaveApplication.objects.filter(
            employee=employee,
            leave_type__leave_type=LeaveManagementService.CASUAL_LEAVE,
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

    @staticmethod
    def check_annual_limit(employee: Employee, leave_type_code: str, year: int = None) -> Tuple[bool, str]:
        """
        FLOW DIAGRAM STEP 2: Leave Validation Rules (Regular Employees Only)
        """
        if year is None:
            year = timezone.now().year

        if leave_type_code == LeaveManagementService.BIRTHDAY_LEAVE:
            count = LeaveApplication.objects.filter(
                employee=employee,
                leave_type__leave_type=leave_type_code,
                status='approved',
                start_date__year=year
            ).count()

            if count >= 1:
                return False, "❌ Birthday Leave: Maximum 1 per year already used."

        elif leave_type_code == LeaveManagementService.MARRIAGE_ANNIVERSARY_LEAVE:
            count = LeaveApplication.objects.filter(
                employee=employee,
                leave_type__leave_type=leave_type_code,
                status='approved',
                start_date__year=year
            ).count()

            if count >= 1:
                return False, "❌ Marriage Anniversary Leave: Maximum 1 per year already used."

        return True, ""

    @staticmethod
    def check_half_day_wfh_office_same_day(leave_request: Dict) -> Tuple[bool, str]:
        """
        FLOW DIAGRAM STEP 3: Half-Day WFH + Office Check
        """
        is_half_day = leave_request.get('is_half_day', False)
        is_wfh = leave_request.get('is_wfh', False)
        is_office = leave_request.get('is_office', False)

        if is_half_day and is_wfh and is_office:
             return False, "❌ Cannot combine half-day WFH and half-day office on the same day in a single request."

        return True, ""

    @staticmethod
    def calculate_half_day_deduction(scheduled_hours: Decimal) -> Decimal:
        """
        FLOW DIAGRAM STEP 4: Half-Day Leave Processing
        """
        if scheduled_hours >= Decimal('5.0'):
            return Decimal('0.5')
        else:
            return Decimal('1.0')

    @staticmethod
    def has_approved_leave_on_date(employee: Employee, check_date: date) -> bool:
        """Check if employee has an approved leave on the specific date"""
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
        """

        actual_working_days = LeaveManagementService.count_working_days(start_date, end_date, country)
        sandwiched_days_count = 0

        # --- Check for Non-working days ADJACENT to the request ---

        # Check BEFORE start_date
        check_date = start_date - timedelta(days=1)
        adjacent_sandwich_before = 0

        while not LeaveManagementService.is_working_day(check_date, country):
            adjacent_sandwich_before += 1
            check_date -= timedelta(days=1)

        if adjacent_sandwich_before > 0:
            if LeaveManagementService.has_approved_leave_on_date(employee, check_date):
                sandwiched_days_count += adjacent_sandwich_before

        # Check AFTER end_date
        check_date = end_date + timedelta(days=1)
        adjacent_sandwich_after = 0

        while not LeaveManagementService.is_working_day(check_date, country):
            adjacent_sandwich_after += 1
            check_date += timedelta(days=1)

        if adjacent_sandwich_after > 0:
            if LeaveManagementService.has_approved_leave_on_date(employee, check_date):
                sandwiched_days_count += adjacent_sandwich_after

        is_sandwich = sandwiched_days_count > 0
        total_deduction = actual_working_days + sandwiched_days_count

        return is_sandwich, total_deduction, actual_working_days


    @staticmethod
    def process_leave_request(employee: Employee, leave_request: Dict) -> LeaveValidationResult:
        """
        MAIN FUNCTION: Process leave request following the exact flow diagram sequence
        """
        leave_type_code = leave_request.get('leave_type_code')
        start_date = leave_request.get('start_date')
        end_date = leave_request.get('end_date')
        is_half_day = leave_request.get('is_half_day', False)

        # ============================================================
        # STEP 1: Identify Employee Type
        # ============================================================
        employee_type = LeaveManagementService.identify_employee_type(employee)

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

        # ============================================================
        # STEP 2: Strict Date Validation (Weekends & Holidays)
        # ============================================================
        is_valid, message = LeaveManagementService.validate_request_dates(start_date, end_date, country='IN')
        if not is_valid:
            return LeaveValidationResult(is_valid=False, message=message)

        # ============================================================
        # STEP 3: Leave Validation Rules (Regular Employees Only)
        # ============================================================
        if employee_type == 'regular':
            is_valid, message = LeaveManagementService.check_annual_limit(employee, leave_type_code, start_date.year)
            if not is_valid:
                return LeaveValidationResult(is_valid=False, message=message)

        # ============================================================
        # STEP 4: Check Half-Day WFH + Office Same Day
        # ============================================================
        is_valid, message = LeaveManagementService.check_half_day_wfh_office_same_day(leave_request)
        if not is_valid:
            return LeaveValidationResult(is_valid=False, message=message)

        # ============================================================
        # STEP 5 & 6: Half-Day or Full-Day Leave Processing
        # ============================================================
        is_sandwich = False
        actual_working_days = 0

        if is_half_day:
            scheduled_hours = leave_request.get('scheduled_hours', Decimal('8.0'))
            deduction_days = LeaveManagementService.calculate_half_day_deduction(scheduled_hours)
            actual_working_days = 0
        else:
            is_sandwich, total_days, actual_working_days = LeaveManagementService.check_sandwich_rule(
                employee, start_date, end_date, country='IN'
            )
            deduction_days = Decimal(str(total_days))

        # ============================================================
        # STEP 7: Leave Balance Check
        # ============================================================
        current_balance = LeaveManagementService.get_leave_balance(employee, leave_type_code, year=start_date.year)

        if current_balance < deduction_days:
            # Detailed breakdown for CL balance failure
            error_msg = f"❌ Insufficient leave balance. Available: {current_balance} days, Required: {deduction_days} days. Excess leaves will be deducted from salary."

            if leave_type_code == LeaveManagementService.CASUAL_LEAVE:
                casual_info = LeaveManagementService.get_casual_leave_accrual_info(employee, year=start_date.year)
                error_msg = (
                    f"❌ Insufficient Casual Leave Balance. "
                    f"Accrual Rule: 1 day per month. "
                    f"Accrued: {casual_info['accrued']} "
                    f"Used: {casual_info['used']} "
                    f"Available: {casual_info['available']}. "
                    f"Required: {deduction_days}. "
                    f"Please apply for Loss of Pay for excess days."
                )

            return LeaveValidationResult(
                is_valid=False,
                message=error_msg
            )

        # ============================================================
        # ALL CHECKS PASSED - APPROVE
        # ============================================================
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

class PaidAbsenceService:
    """
    Service class implementing the HRMS Paid Absence flow diagram
    """

    # Paid absence type constants
    MARRIAGE_LEAVE = 'absence_marriage'
    PATERNITY_LEAVE = 'paternity'
    MATERNITY_LEAVE = 'maternity'
    # ... (same as before)

    # Disciplinary issues that disqualify employees - FLOW DIAGRAM STEP 1.4
    DISCIPLINARY_ISSUES = [
        'disciplinary_exit',
        'misconduct_case',
        'inappropriate_work',
        'destructive_issue',
    ]

    @staticmethod
    def check_employee_eligibility(employee: Employee) -> Tuple[bool, str]:
        if employee.period_type in ['trainee', 'intern']:
            return False, "❌ Trainees and Interns are not eligible for paid absence. Only confirmed employees with at least 1 year tenure are eligible."

        if employee.period_type in ['probation', 'notice_period']:
            return False, "❌ Employees on Probation or Notice period are not eligible for paid absence. Only confirmed employees with at least 1 year tenure are eligible."

        if employee.joining_date:
            tenure_days = (timezone.now().date() - employee.joining_date).days
            tenure_years = tenure_days / 365.25

            if tenure_years < 1:
                remaining_days = int(365.25 - tenure_days)
                return False, f"❌ Employee must complete at least 1 year in company to be eligible for paid absence. You need {remaining_days} more days to complete 1 year."

        pass
        return True, "Employee is eligible for paid absence"


    @staticmethod
    def is_first_child(employee: Employee, leave_application: 'LeaveApplication' = None) -> bool:
        if leave_application:
            previous_leaves = LeaveApplication.objects.filter(
                employee=employee,
                leave_type__leave_type__in=[
                    PaidAbsenceService.PATERNITY_LEAVE,
                    PaidAbsenceService.MATERNITY_LEAVE
                ],
                status='approved'
            ).exclude(id=leave_application.id if leave_application.id else None).exists()
            return not previous_leaves
        return True

    @staticmethod
    def process_marriage_leave(employee: Employee) -> LeaveValidationResult:
        is_eligible, message = PaidAbsenceService.check_employee_eligibility(employee)
        if not is_eligible:
            return LeaveValidationResult(is_valid=False, message=message)

        return LeaveValidationResult(
            is_valid=True,
            message="✓ Marriage Leave approved: 2 days paid absence",
            deduction_days=Decimal('2.0')
        )

    @staticmethod
    def process_paternity_leave(employee: Employee, is_first_child: bool = True) -> LeaveValidationResult:
        is_eligible, message = PaidAbsenceService.check_employee_eligibility(employee)
        if not is_eligible:
            return LeaveValidationResult(is_valid=False, message=message)

        if not is_first_child:
            return LeaveValidationResult(
                is_valid=False,
                message="❌ Paternity Leave is only available for the birth/adoption of FIRST child. This benefit has already been used or is not applicable."
            )

        return LeaveValidationResult(
            is_valid=True,
            message="✓ Paternity Leave approved: 5 continuous days paid leave for first child",
            deduction_days=Decimal('5.0')
        )

    @staticmethod
    def process_maternity_leave(employee: Employee, is_first_child: bool = True) -> LeaveValidationResult:
        is_eligible, message = PaidAbsenceService.check_employee_eligibility(employee)
        if not is_eligible:
            return LeaveValidationResult(is_valid=False, message=message)

        if not is_first_child:
            return LeaveValidationResult(
                is_valid=False,
                message="❌ Maternity Leave is only available for the birth/adoption of FIRST child. This benefit has already been used or is not applicable."
            )

        return LeaveValidationResult(
            is_valid=True,
            message="✓ Maternity Leave approved: 8 weeks (56 days) paid leave for first child",
            deduction_days=Decimal('56.0')
        )

    @staticmethod
    def process_paid_absence_request(employee: Employee, absence_type: str, is_first_child: bool = True) -> LeaveValidationResult:
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
