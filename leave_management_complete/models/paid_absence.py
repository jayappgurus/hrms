"""
Paid Absence Model
Handles special paid leaves (Marriage, Paternity, Maternity)
"""
from django.db import models
from decimal import Decimal
from .employee import Employee

class PaidAbsence(models.Model):
    """
    Paid absence tracking for special leaves
    """

    ABSENCE_TYPE_CHOICES = [
        ('marriage', 'Marriage Leave'),
        ('paternity', 'Paternity Leave'),
        ('maternity', 'Maternity Leave'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # Core Fields
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='paid_absences'
    )
    absence_type = models.CharField(
        max_length=20,
        choices=ABSENCE_TYPE_CHOICES
    )

    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    applied_date = models.DateTimeField(auto_now_add=True)

    # Details
    total_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Total paid absence days"
    )
    reason = models.TextField()

    # For Paternity/Maternity
    is_first_child = models.BooleanField(
        default=False,
        help_text="Required for paternity/maternity leave"
    )
    expected_delivery_date = models.DateField(
        null=True,
        blank=True,
        help_text="For maternity leave"
    )

    # Documents
    marriage_certificate = models.FileField(
        upload_to='paid_absence/marriage/%Y/%m/',
        null=True,
        blank=True
    )
    birth_certificate = models.FileField(
        upload_to='paid_absence/birth/%Y/%m/',
        null=True,
        blank=True
    )

    # Approval
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
        related_name='approved_paid_absences'
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'paid_absences'
        ordering = ['-applied_date']
        indexes = [
            models.Index(fields=['employee', 'absence_type']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_absence_type_display()}"

    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def is_approved(self):
        return self.status == 'approved'

    @classmethod
    def get_days_for_type(cls, absence_type):
        """Get standard days for each absence type"""
        days_mapping = {
            'marriage': Decimal('2.0'),
            'paternity': Decimal('5.0'),
            'maternity': Decimal('56.0'),  # 8 weeks
        }
        return days_mapping.get(absence_type, Decimal('0'))
