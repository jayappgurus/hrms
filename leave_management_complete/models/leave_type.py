"""
Leave Type Model
Defines different types of leaves and their configurations
"""
from django.db import models
from decimal import Decimal


class LeaveType(models.Model):
    """
    Leave type configuration with rules and allocations
    """
    
    LEAVE_TYPE_CHOICES = [
        ('casual', 'Casual Leave (CL)'),
        ('emergency', 'Emergency Leave (EL)'),
        ('birthday', 'Birthday Leave'),
        ('marriage_anniversary', 'Marriage Anniversary Leave'),
        ('public_holiday', 'Public Holiday'),
        ('weekend', 'Weekend'),
        ('carry_forward_cl', 'Carry Forward CL'),
    ]
    
    DURATION_TYPE_CHOICES = [
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=100)
    code = models.CharField(
        max_length=50,
        choices=LEAVE_TYPE_CHOICES,
        unique=True,
        help_text="Unique code for leave type"
    )
    description = models.TextField(blank=True)
    
    # Allocation
    annual_allocation = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Total leaves allocated per year"
    )
    
    # Accrual Settings (for Casual Leave)
    is_accrual_based = models.BooleanField(
        default=False,
        help_text="If True, leaves accrue monthly (1 per month)"
    )
    accrual_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1,
        help_text="Leaves accrued per month (for accrual-based leaves)"
    )
    
    # Rules
    is_paid = models.BooleanField(default=True)
    requires_document = models.BooleanField(default=False)
    max_consecutive_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum consecutive days allowed"
    )
    
    # Restrictions
    restricted_for_trainees = models.BooleanField(
        default=False,
        help_text="If True, trainees/interns cannot apply"
    )
    max_applications_per_year = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum times this leave can be applied per year (e.g., 1 for birthday)"
    )
    
    # Carry Forward
    can_carry_forward = models.BooleanField(
        default=False,
        help_text="Can unused leaves be carried forward to next year"
    )
    max_carry_forward = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Maximum leaves that can be carried forward"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leave_types'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def is_restricted_leave(self):
        """Check if this leave type is restricted for trainees"""
        return self.code in ['casual', 'emergency', 'birthday', 'marriage_anniversary', 'carry_forward_cl']


class PublicHoliday(models.Model):
    """
    Public holidays for leave calculation
    """
    name = models.CharField(max_length=100)
    date = models.DateField()
    country = models.CharField(max_length=2, default='IN')
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'public_holidays'
        ordering = ['date']
        unique_together = ['date', 'country']
    
    def __str__(self):
        return f"{self.name} - {self.date}"
