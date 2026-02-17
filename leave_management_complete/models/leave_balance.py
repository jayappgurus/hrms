"""
Leave Balance Model
Tracks employee leave balances with accrual
"""
from django.db import models
from decimal import Decimal
from .employee import Employee
from .leave_type import LeaveType

class LeaveBalance(models.Model):
    """
    Employee leave balance tracking with monthly accrual
    """

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name='balances'
    )
    year = models.IntegerField()

    # Balance Tracking
    allocated = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Total allocated for the year"
    )
    accrued = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Accrued so far (for accrual-based leaves)"
    )
    used = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Total used"
    )
    carried_forward = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Carried forward from previous year"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leave_balances'
        unique_together = ['employee', 'leave_type', 'year']
        indexes = [
            models.Index(fields=['employee', 'year']),
            models.Index(fields=['leave_type', 'year']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.year})"

    @property
    def available(self):
        """Calculate available balance"""
        if self.leave_type.is_accrual_based:
            # For accrual-based (Casual Leave), use accrued amount
            return self.accrued + self.carried_forward - self.used
        else:
            # For other leaves, use full allocation
            return self.allocated + self.carried_forward - self.used

    @property
    def is_sufficient(self, required_days):
        """Check if balance is sufficient for requested days"""
        return self.available >= Decimal(str(required_days))

    def deduct(self, days):
        """Deduct days from balance"""
        self.used += Decimal(str(days))
        self.save()

    def credit(self, days):
        """Credit days back to balance (for cancelled leaves)"""
        self.used -= Decimal(str(days))
        if self.used < 0:
            self.used = 0
        self.save()

class LeaveAccrualLog(models.Model):
    """
    Log of monthly accruals for audit trail
    """

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='accrual_logs'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE
    )
    year = models.IntegerField()
    month = models.IntegerField()
    accrued_amount = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    balance_before = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    balance_after = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'leave_accrual_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'year', 'month']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} - {self.year}/{self.month}"
