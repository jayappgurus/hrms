"""
Leave Service - Core Business Logic
Handles all leave-related operations following clean architecture
"""
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Dict, Tuple, Optional
from django.db.models import Sum
from django.utils import timezone
from django.db import transaction

from ..models.employee import Employee
from ..models.leave_type import LeaveType, PublicHoliday
from ..models.leave_application import LeaveApplication
from ..models.leave_balance import LeaveBalance


class LeaveValidationResult:
    """Result object for leave validation"""
    def __init__(
        self,
        is_valid: bool,
        message: str = "",
        deduction_days: Decimal = Decimal('0'),
        is_sandwich: bool = False,
        actual_working_days: int = 0
    ):
        self.is_valid = is_valid
        self.message = message
        self.deduction_days = deduction_days
        self.is_sandwich = is_sandwich
        self.actual_working_days = actual_working_days


class LeaveService:
    """
    Core leave management service
    Implements all business rules and validations
    """
    
    @staticmethod
    def is_weekend(check_date: date) -> bool:
        """Check if date is weekend (Saturday=5, Sunday=6)"""
        return check_date.weekday() in [5, 6]
    
    @staticmethod
    def is_public_holiday(check_date: date, country: str = 'IN') -> bool:
        """Check if date is a public holiday"""
        return PublicHoliday.objects.filter(
            date=check_date,
            country=country,
            is_active=True
        ).exists()
    
    @staticmethod
    def count_working_days(start_date: date, end_date: date, country: str = 'IN') -> int:
        """
        Count only working days (exclude weekends and public holidays)
        """
        working_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            if not LeaveService.is_weekend(current_date) and \
               not LeaveService.is_public_holiday(current_date, country):
                working_days += 1
            current_date += timedelta(days=1)
        
        return working_days

    
    @staticmethod
    def check_sandwich_rule(
        start_date: date,
        end_date: date,
        country: str = 'IN'
    ) -> Tuple[bool, int, int]:
        """
        Sandwich Rule: Check if leave is taken before AND after weekend/holiday
        
        Returns:
            (is_sandwich, total_days_to_deduct, actual_working_days)
        """
        # Check if there are non-working days within the period
        current_date = start_date
        has_non_working_inside = False
        
        while current_date <= end_date:
            if LeaveService.is_weekend(current_date) or \
               LeaveService.is_public_holiday(current_date, country):
                has_non_working_inside = True
                break
            current_date += timedelta(days=1)
        
        # Check day before and after
        day_before = start_date - timedelta(days=1)
        day_after = end_date + timedelta(days=1)
        
        is_before_non_working = (
            LeaveService.is_weekend(day_before) or
            LeaveService.is_public_holiday(day_before, country)
        )
        is_after_non_working = (
            LeaveService.is_weekend(day_after) or
            LeaveService.is_public_holiday(day_after, country)
        )
        
        # Count actual working days
        actual_working_days = LeaveService.count_working_days(start_date, end_date, country)
        
        # Sandwich detected if non-working days inside AND leave before AND after
        is_sandwich = has_non_working_inside and is_before_non_working and is_after_non_working
        
        if is_sandwich:
            # Include all calendar days
            total_days = (end_date - start_date).days + 1
            return True, total_days, actual_working_days
        else:
            # Only working days
            return False, actual_working_days, actual_working_days
    
    @staticmethod
    def calculate_half_day_deduction(scheduled_hours: Decimal) -> Decimal:
        """
        Half-day leave calculation
        - If scheduled hours >= 5 → Deduct 0.5 day
        - If scheduled hours < 5 → Deduct 1 full day
        """
        return Decimal('0.5') if scheduled_hours >= Decimal('5.0') else Decimal('1.0')
    
    @staticmethod
    def validate_employee_eligibility(
        employee: Employee,
        leave_type: LeaveType
    ) -> Tuple[bool, str]:
        """
        Validate if employee is eligible for the leave type
        """
        # Check if employee is restricted and leave type is restricted
        if employee.is_restricted_employee and leave_type.is_restricted_leave:
            return False, (
                f"❌ {employee.get_employee_type_display()} employees are not eligible "
                f"for {leave_type.name}. Only regular employees can apply."
            )
        
        return True, ""
