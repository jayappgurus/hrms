# Leave Management Service
# This module implements the HRMS leave management flow diagram logic
# Refactored to strictly follow the HRMS flow diagram requirements

from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Dict, Tuple, Optional
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
    def count_working_days(start_date: date, end_date: date, country: str = 'IN') -> int:
        """
        FLOW DIAGRAM REQUIREMENT: Count only working days
        Exclude weekends (Saturday & Sunday) and public holidays
        """
        working_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            # Skip weekends and public holidays
            if not LeaveManagementService.is_weekend(current_date) and \
               not LeaveManagementService.is_public_holiday(current_date, country):
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
            current_month = current_date.month
            
            # Accrued casual leaves = number of months worked (1 per month)
            months_worked = current_month - start_month + 1
            accrued_leaves = min(months_worked, 12)  # Maximum 12 per year
            
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
            
            # Calculate balance
            balance = Decimal(str(annual_allocation)) - Decimal(str(approved_leaves))
            
            return balance
    
    @staticmethod
    def get_casual_leave_accrual_info(employee: Employee, year: int = None) -> Dict:
        """
        Get detailed accrual information for casual leave
        Returns: Dictionary with accrued, used, and available casual leaves
        """
        if year is None:
            year = timezone.now().year
        
        current_date = timezone.now().date()
        
        # If employee joined this year, calculate from joining date
        if employee.joining_date and employee.joining_date.year == year:
            start_month = employee.joining_date.month
        else:
            start_month = 1
        
        # Current month
        current_month = current_date.month
        
        # Accrued casual leaves = number of months worked (1 per month)
        months_worked = current_month - start_month + 1
        accrued_leaves = min(months_worked, 12)  # Maximum 12 per year
        
        # Get total approved leaves for this year
        approved_leaves = LeaveApplication.objects.filter(
            employee=employee,
            leave_type__leave_type=LeaveManagementService.CASUAL_LEAVE,
            status='approved',
            start_date__year=year
        ).aggregate(total=Sum('total_days'))['total'] or 0
        
        # Calculate available balance
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
        
        Validation rules:
        - Birthday Leave: Maximum 1 per year only
        - Marriage Anniversary Leave: Maximum 1 per year only
        """
        if year is None:
            year = timezone.now().year
        
        # Birthday Leave: Maximum 1 per year
        if leave_type_code == LeaveManagementService.BIRTHDAY_LEAVE:
            count = LeaveApplication.objects.filter(
                employee=employee,
                leave_type__leave_type=leave_type_code,
                status='approved',
                start_date__year=year
            ).count()
            
            if count >= 1:
                return False, "❌ Birthday Leave: Maximum 1 per year already used. You have already taken your birthday leave for this year."
        
        # Marriage Anniversary Leave: Maximum 1 per year
        elif leave_type_code == LeaveManagementService.MARRIAGE_ANNIVERSARY_LEAVE:
            count = LeaveApplication.objects.filter(
                employee=employee,
                leave_type__leave_type=leave_type_code,
                status='approved',
                start_date__year=year
            ).count()
            
            if count >= 1:
                return False, "❌ Marriage Anniversary Leave: Maximum 1 per year already used. You have already taken your anniversary leave for this year."
        
        return True, ""
    
    @staticmethod
    def check_half_day_wfh_office_same_day(leave_request: Dict) -> Tuple[bool, str]:
        """
        FLOW DIAGRAM STEP 3: Half-Day WFH + Office Check
        
        Rule: Cannot combine "Half-Day WFH + Half-Day Office on SAME day"
        If YES → Reject Request
        If NO → Continue to half-day leave processing
        """
        is_half_day = leave_request.get('is_half_day', False)
        is_wfh = leave_request.get('is_wfh', False)
        is_office = leave_request.get('is_office', False)
        same_day = leave_request.get('start_date') == leave_request.get('end_date')
        
        # Check if trying to combine WFH and Office on same day
        if is_half_day and is_wfh and is_office and same_day:
            return False, "❌ Cannot combine half-day WFH and half-day office on the same day. Please choose either WFH or Office, not both."
        
        return True, ""
    
    @staticmethod
    def calculate_half_day_deduction(scheduled_hours: Decimal) -> Decimal:
        """
        FLOW DIAGRAM STEP 4: Half-Day Leave Processing
        
        Rule: Check scheduled working hours (excluding break)
        - If scheduled hours ≥ 5 hours → Deduct 0.5 day leave
        - If scheduled hours < 5 hours → Deduct 1 full day
        """
        if scheduled_hours >= Decimal('5.0'):
            return Decimal('0.5')
        else:
            return Decimal('1.0')
    
    @staticmethod
    def check_sandwich_rule(start_date: date, end_date: date, country: str = 'IN') -> Tuple[bool, int, int]:
        """
        FLOW DIAGRAM STEP 5: Sandwich Rule (Full Day Leave Processing)
        
        Critical Rule: Check if leave is taken before AND after weekend/holiday
        - If YES (sandwich detected) → Include non-working days in deduction
        - If NO → Deduct only working days
        
        Returns: (is_sandwich, total_days_to_deduct, actual_working_days)
        """
        # Check if there are any non-working days within the leave period
        current_date = start_date
        has_non_working_days_inside = False
        
        while current_date <= end_date:
            if LeaveManagementService.is_weekend(current_date) or \
               LeaveManagementService.is_public_holiday(current_date, country):
                has_non_working_days_inside = True
                break
            current_date += timedelta(days=1)
        
        # Check day before start_date
        day_before = start_date - timedelta(days=1)
        is_before_non_working = LeaveManagementService.is_weekend(day_before) or \
                                LeaveManagementService.is_public_holiday(day_before, country)
        
        # Check day after end_date
        day_after = end_date + timedelta(days=1)
        is_after_non_working = LeaveManagementService.is_weekend(day_after) or \
                               LeaveManagementService.is_public_holiday(day_after, country)
        
        # Count actual working days
        actual_working_days = LeaveManagementService.count_working_days(start_date, end_date, country)
        
        # Sandwich detected if:
        # 1. There are non-working days INSIDE the leave period, AND
        # 2. Leave is taken before AND after these non-working days
        is_sandwich = has_non_working_days_inside and is_before_non_working and is_after_non_working
        
        if is_sandwich:
            # Count all calendar days including non-working days
            total_days = (end_date - start_date).days + 1
            return True, total_days, actual_working_days
        else:
            # Count only working days
            return False, actual_working_days, actual_working_days

    
    @staticmethod
    def process_leave_request(employee: Employee, leave_request: Dict) -> LeaveValidationResult:
        """
        MAIN FUNCTION: Process leave request following the exact flow diagram sequence
        
        Flow Sequence:
        1. Identify Employee Type
        2. Leave Validation Rules (Regular Employees Only)
        3. Half-Day WFH + Office Check
        4. Half-Day Leave Processing (if applicable)
        5. Full Day Leave Processing - Sandwich Rule (if not half-day)
        6. Leave Balance Check
        
        Args:
            employee: Employee object
            leave_request: Dictionary containing:
                - leave_type_code: str
                - start_date: date
                - end_date: date
                - is_half_day: bool
                - scheduled_hours: Decimal (for half-day)
                - is_wfh: bool
                - is_office: bool
                - reason: str
        
        Returns:
            LeaveValidationResult object with validation status and deduction details
        """
        leave_type_code = leave_request.get('leave_type_code')
        start_date = leave_request.get('start_date')
        end_date = leave_request.get('end_date')
        is_half_day = leave_request.get('is_half_day', False)
        
        # ============================================================
        # STEP 1: Identify Employee Type
        # ============================================================
        employee_type = LeaveManagementService.identify_employee_type(employee)
        
        # Check if restricted employee is trying to apply for restricted leave types
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
        # STEP 2: Leave Validation Rules (Regular Employees Only)
        # ============================================================
        if employee_type == 'regular':
            is_valid, message = LeaveManagementService.check_annual_limit(employee, leave_type_code)
            if not is_valid:
                return LeaveValidationResult(is_valid=False, message=message)
        
        # ============================================================
        # STEP 3: Check Half-Day WFH + Office Same Day
        # ============================================================
        is_valid, message = LeaveManagementService.check_half_day_wfh_office_same_day(leave_request)
        if not is_valid:
            return LeaveValidationResult(is_valid=False, message=message)
        
        # ============================================================
        # STEP 4 & 5: Half-Day or Full-Day Leave Processing
        # ============================================================
        is_sandwich = False
        actual_working_days = 0
        
        if is_half_day:
            # STEP 4: Half-Day Leave Processing
            scheduled_hours = leave_request.get('scheduled_hours', Decimal('8.0'))
            deduction_days = LeaveManagementService.calculate_half_day_deduction(scheduled_hours)
            actual_working_days = 0  # Half-day doesn't count working days
        else:
            # STEP 5: Full Day Leave Processing - Sandwich Rule
            is_sandwich, total_days, actual_working_days = LeaveManagementService.check_sandwich_rule(
                start_date, end_date, country='IN'
            )
            deduction_days = Decimal(str(total_days))
        
        # ============================================================
        # STEP 6: Leave Balance Check
        # ============================================================
        current_balance = LeaveManagementService.get_leave_balance(employee, leave_type_code)
        
        if current_balance < deduction_days:
            return LeaveValidationResult(
                is_valid=False,
                message=f"❌ Insufficient leave balance. Available: {current_balance} days, Required: {deduction_days} days. Please check your leave balance and apply accordingly."
            )
        
        # ============================================================
        # ALL CHECKS PASSED - APPROVE
        # ============================================================
        approval_message = "✓ Leave request approved"
        if is_sandwich:
            approval_message += f" (Sandwich leave detected: {deduction_days} days will be deducted including non-working days)"
        
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
    Follows exact sequence: Employee Eligibility Check → Paid Absence Type Processing
    """
    
    # Paid absence type constants
    MARRIAGE_LEAVE = 'absence_marriage'
    PATERNITY_LEAVE = 'paternity'
    MATERNITY_LEAVE = 'maternity'
    
    # Disciplinary issues that disqualify employees - FLOW DIAGRAM STEP 1.4
    DISCIPLINARY_ISSUES = [
        'disciplinary_exit',
        'misconduct_case',
        'inappropriate_work',
        'destructive_issue',
    ]
    
    @staticmethod
    def check_employee_eligibility(employee: Employee) -> Tuple[bool, str]:
        """
        FLOW DIAGRAM STEP 1: Employee Eligibility Check
        Sequential checks for paid absence eligibility
        
        Check Sequence:
        1. Check if Trainee/Intern → Reject
        2. Check if Probation/Notice period → Reject
        3. Check tenure (must have completed 1 year) → Reject if < 1 year
        4. Check disciplinary record → Reject if issues found
        """
        
        # ============================================================
        # CHECK 1: Trainee/Intern
        # ============================================================
        if employee.period_type in ['trainee', 'intern']:
            return False, "❌ Trainees and Interns are not eligible for paid absence. Only confirmed employees with at least 1 year tenure are eligible."
        
        # ============================================================
        # CHECK 2: Probation/Notice period
        # ============================================================
        if employee.period_type in ['probation', 'notice_period']:
            return False, "❌ Employees on Probation or Notice period are not eligible for paid absence. Only confirmed employees with at least 1 year tenure are eligible."
        
        # ============================================================
        # CHECK 3: Tenure (must have completed 1 year)
        # ============================================================
        if employee.joining_date:
            tenure_days = (timezone.now().date() - employee.joining_date).days
            tenure_years = tenure_days / 365.25
            
            if tenure_years < 1:
                remaining_days = int(365.25 - tenure_days)
                return False, f"❌ Employee must complete at least 1 year in company to be eligible for paid absence. You need {remaining_days} more days to complete 1 year."
        
        # ============================================================
        # CHECK 4: Disciplinary Record
        # ============================================================
        # Note: This requires a disciplinary_records field in Employee model
        # For now, we assume clean record if no field exists
        # TODO: Implement when disciplinary tracking is added to Employee model
        # Example implementation:
        # if hasattr(employee, 'disciplinary_records'):
        #     has_issues = employee.disciplinary_records.filter(
        #         issue_type__in=PaidAbsenceService.DISCIPLINARY_ISSUES,
        #         is_resolved=False
        #     ).exists()
        #     if has_issues:
        #         return False, "❌ Employees with active disciplinary issues are not eligible for paid absence. Please contact HR."
        
        # All checks passed
        return True, "Employee is eligible for paid absence"

    
    @staticmethod
    def is_first_child(employee: Employee, leave_application: 'LeaveApplication' = None) -> bool:
        """
        FLOW DIAGRAM STEP 2: Check if this is for the first child
        Required for Paternity and Maternity leave approval
        
        Note: This requires additional data tracking in the system
        TODO: Implement based on child tracking system
        
        Implementation options:
        1. Add 'number_of_children' field to Employee model
        2. Create separate ChildRecord model linked to Employee
        3. Track via previous paternity/maternity leave applications
        
        For now, we check previous paternity/maternity leaves as a proxy
        """
        if leave_application:
            # Check if employee has any previously approved paternity/maternity leaves
            previous_leaves = LeaveApplication.objects.filter(
                employee=employee,
                leave_type__leave_type__in=[
                    PaidAbsenceService.PATERNITY_LEAVE,
                    PaidAbsenceService.MATERNITY_LEAVE
                ],
                status='approved'
            ).exclude(id=leave_application.id if leave_application.id else None).exists()
            
            # If no previous paternity/maternity leaves, assume first child
            return not previous_leaves
        
        # Default: assume first child (should be explicitly confirmed in form)
        return True
    
    @staticmethod
    def process_marriage_leave(employee: Employee) -> LeaveValidationResult:
        """
        FLOW DIAGRAM STEP 2.1: Process Marriage Leave
        
        Rule: Approve 2 days paid leave/absence for marriage
        """
        # Check eligibility
        is_eligible, message = PaidAbsenceService.check_employee_eligibility(employee)
        if not is_eligible:
            return LeaveValidationResult(is_valid=False, message=message)
        
        # Approve 2 days
        return LeaveValidationResult(
            is_valid=True,
            message="✓ Marriage Leave approved: 2 days paid absence",
            deduction_days=Decimal('2.0')
        )
    
    @staticmethod
    def process_paternity_leave(employee: Employee, is_first_child: bool = True) -> LeaveValidationResult:
        """
        FLOW DIAGRAM STEP 2.2: Process Paternity Leave
        
        Rule: Check if it's for birth/adoption of FIRST child
        - If NO → Reject (only first child eligible)
        - If YES → Approve 5 continuous days paid leave
        """
        # Check eligibility
        is_eligible, message = PaidAbsenceService.check_employee_eligibility(employee)
        if not is_eligible:
            return LeaveValidationResult(is_valid=False, message=message)
        
        # Check if first child
        if not is_first_child:
            return LeaveValidationResult(
                is_valid=False,
                message="❌ Paternity Leave is only available for the birth/adoption of FIRST child. This benefit has already been used or is not applicable."
            )
        
        # Approve 5 continuous days
        return LeaveValidationResult(
            is_valid=True,
            message="✓ Paternity Leave approved: 5 continuous days paid leave for first child",
            deduction_days=Decimal('5.0')
        )
    
    @staticmethod
    def process_maternity_leave(employee: Employee, is_first_child: bool = True) -> LeaveValidationResult:
        """
        FLOW DIAGRAM STEP 2.3: Process Maternity Leave
        
        Rule: Check if it's for birth/adoption of FIRST child
        - If NO → Reject (only first child eligible)
        - If YES → Approve 8 weeks paid leave
        """
        # Check eligibility
        is_eligible, message = PaidAbsenceService.check_employee_eligibility(employee)
        if not is_eligible:
            return LeaveValidationResult(is_valid=False, message=message)
        
        # Check if first child
        if not is_first_child:
            return LeaveValidationResult(
                is_valid=False,
                message="❌ Maternity Leave is only available for the birth/adoption of FIRST child. This benefit has already been used or is not applicable."
            )
        
        # Approve 8 weeks (56 days)
        return LeaveValidationResult(
            is_valid=True,
            message="✓ Maternity Leave approved: 8 weeks (56 days) paid leave for first child",
            deduction_days=Decimal('56.0')
        )
    
    @staticmethod
    def process_paid_absence_request(employee: Employee, absence_type: str, is_first_child: bool = True) -> LeaveValidationResult:
        """
        MAIN FUNCTION: Process paid absence request following the flow diagram
        
        Flow Sequence:
        1. Employee Eligibility Check (4 sequential checks)
        2. Paid Absence Type Processing (Marriage/Paternity/Maternity)
        
        Args:
            employee: Employee object
            absence_type: Type of paid absence (marriage, paternity, maternity)
            is_first_child: Boolean indicating if this is for first child (required for paternity/maternity)
        
        Returns:
            LeaveValidationResult object with validation status and deduction details
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
