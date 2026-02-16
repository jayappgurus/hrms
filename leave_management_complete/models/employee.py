"""
Employee Model
Handles employee information and classification
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Employee(models.Model):
    """
    Employee model with type classification for leave eligibility
    """
    
    # Employee Type Choices
    EMPLOYEE_TYPE_CHOICES = [
        ('regular', 'Regular Employee'),
        ('trainee', 'Trainee'),
        ('intern', 'Intern'),
        ('probation', 'Probation'),
        ('notice_period', 'Notice Period'),
    ]
    
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    # Core Fields
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_code = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    
    # Employment Details
    employee_type = models.CharField(
        max_length=20, 
        choices=EMPLOYEE_TYPE_CHOICES, 
        default='regular',
        help_text="Employee classification for leave eligibility"
    )
    employment_status = models.CharField(
        max_length=10,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default='active'
    )
    
    # Dates
    joining_date = models.DateField()
    relieving_date = models.DateField(null=True, blank=True)
    date_of_birth = models.DateField()
    anniversary_date = models.DateField(null=True, blank=True)
    
    # Department & Designation
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    
    # Manager for approval workflow
    reporting_manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_members'
    )
    
    # Disciplinary tracking
    has_disciplinary_issues = models.BooleanField(
        default=False,
        help_text="Employees with disciplinary issues cannot apply for paid absence"
    )
    
    # Child tracking for paternity/maternity
    number_of_children = models.PositiveIntegerField(
        default=0,
        help_text="Number of children for paternity/maternity leave eligibility"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employees'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee_code']),
            models.Index(fields=['email']),
            models.Index(fields=['employee_type']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.employee_code})"
    
    @property
    def is_regular_employee(self):
        """Check if employee is regular (eligible for all leaves)"""
        return self.employee_type == 'regular'
    
    @property
    def is_restricted_employee(self):
        """Check if employee has restricted leave access"""
        return self.employee_type in ['trainee', 'intern', 'probation', 'notice_period']
    
    @property
    def tenure_in_days(self):
        """Calculate tenure in days"""
        from django.utils import timezone
        if self.relieving_date:
            return (self.relieving_date - self.joining_date).days
        return (timezone.now().date() - self.joining_date).days
    
    @property
    def tenure_in_years(self):
        """Calculate tenure in years"""
        return self.tenure_in_days / 365.25
    
    @property
    def is_eligible_for_paid_absence(self):
        """
        Check eligibility for paid absence
        - Must be regular employee
        - Must have completed 1 year
        - No disciplinary issues
        """
        return (
            self.is_regular_employee and
            self.tenure_in_years >= 1 and
            not self.has_disciplinary_issues
        )
