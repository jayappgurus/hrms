"""
Leave Application Model
Handles leave requests and their lifecycle
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from .employee import Employee
from .leave_type import LeaveType

class LeaveApplication(models.Model):
    """
    Leave application with complete workflow
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    # Core Fields
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_applications'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.PROTECT,
        related_name='applications'
    )

    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    applied_date = models.DateTimeField(auto_now_add=True)

    # Leave Details
    total_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.5'))],
        help_text="Total days to be deducted (can be 0.5 for half-day)"
    )
    actual_working_days = models.IntegerField(
        default=0,
        help_text="Actual working days (excluding weekends/holidays)"
    )

    # Half-Day Fields
    is_half_day = models.BooleanField(default=False)
    scheduled_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Scheduled working hours for half-day leave"
    )
    is_wfh = models.BooleanField(
        default=False,
        help_text="Half-day work from home"
    )
    is_office = models.BooleanField(
        default=False,
        help_text="Half-day in office"
    )

    # Sandwich Leave
    is_sandwich_leave = models.BooleanField(
        default=False,
        help_text="Leave taken before AND after weekend/holiday"
    )

    # Reason & Documents
    reason = models.TextField()
    document = models.FileField(
        upload_to='leave_documents/%Y/%m/',
        null=True,
        blank=True
    )

    # Approval Workflow
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves'
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leave_applications'
        ordering = ['-applied_date']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.start_date} to {self.end_date})"

    @property
    def duration_display(self):
        """Human-readable duration"""
        if self.is_half_day:
            return f"{self.total_days} day (Half-day)"
        return f"{self.total_days} days"

    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def is_approved(self):
        return self.status == 'approved'

    @property
    def is_rejected(self):
        return self.status == 'rejected'
