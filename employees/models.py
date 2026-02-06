from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import date


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('hr', 'HR'),
        ('manager', 'Manager'),
        ('it_admin', 'IT-Admin'),
        ('employee', 'Employee'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_hr(self):
        return self.role == 'hr'
    
    @property
    def is_manager(self):
        return self.role == 'manager'
    
    @property
    def is_it_admin(self):
        return self.role == 'it_admin'
    
    @property
    def is_employee(self):
        return self.role == 'employee'
    
    @property
    def can_manage_employees(self):
        return self.role in ['admin', 'hr', 'manager']
    
    @property
    def can_view_all_employees(self):
        return self.role in ['admin', 'hr']
    
    @property
    def can_manage_system(self):
        return self.role in ['admin', 'it_admin']


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ['name']

    def __str__(self):
        return self.name


class Designation(models.Model):
    name = models.CharField(max_length=100, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='designations')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Designation"
        verbose_name_plural = "Designations"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.department.name}"


class EmergencyContact(models.Model):
    name = models.CharField(max_length=100)
    mobile_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid mobile number.")]
    )
    email = models.EmailField(validators=[EmailValidator()])
    address = models.TextField()
    relationship = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Emergency Contact"
        verbose_name_plural = "Emergency Contacts"

    def __str__(self):
        return f"{self.name} ({self.relationship})"


class Employee(models.Model):
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
    ]

    # Core Employee Details
    employee_code = models.CharField(max_length=20, unique=True, help_text="Unique employee code")
    full_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees')
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, related_name='employees')
    joining_date = models.DateField()
    relieving_date = models.DateField(null=True, blank=True)
    employment_status = models.CharField(max_length=10, choices=EMPLOYMENT_STATUS_CHOICES, default='active')

    # Contact Information
    mobile_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid mobile number.")]
    )
    official_email = models.EmailField(validators=[EmailValidator()], unique=True)
    personal_email = models.EmailField(validators=[EmailValidator()], blank=True, null=True)
    local_address = models.TextField()
    permanent_address = models.TextField()

    # Emergency Contact
    emergency_contact = models.OneToOneField(EmergencyContact, on_delete=models.SET_NULL, null=True, blank=True)

    # Personal Information
    date_of_birth = models.DateField()
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES)
    anniversary_date = models.DateField(null=True, blank=True)

    # Professional Information
    highest_qualification = models.CharField(max_length=100)
    total_experience_years = models.PositiveIntegerField(default=0)
    total_experience_months = models.PositiveIntegerField(default=0)
    probation_status = models.CharField(max_length=20, editable=False)

    # Identity & Compliance
    aadhar_card_number = models.CharField(
        max_length=12,
        validators=[RegexValidator(regex=r'^\d{12}$', message="Enter a valid 12-digit Aadhar number.")],
        unique=True
    )
    pan_card_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', message="Enter a valid PAN number.")],
        unique=True
    )

    # Additional fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.employee_code})"

    def save(self, *args, **kwargs):
        # Auto-calculate probation status
        if self.joining_date:
            # Calculate probation end date (3 months from joining date)
            probation_months = 3
            year = self.joining_date.year
            month = self.joining_date.month + probation_months
            day = self.joining_date.day
            
            # Adjust year and month if overflow
            if month > 12:
                year += 1
                month -= 12
            
            probation_end_date = date(year, month, day)
            
            if timezone.now().date() <= probation_end_date:
                self.probation_status = "On Probation"
            else:
                self.probation_status = "Confirmed"
        
        super().save(*args, **kwargs)

    @property
    def total_experience_display(self):
        """Return formatted total experience"""
        years = self.total_experience_years
        months = self.total_experience_months
        if years == 0 and months == 0:
            return "Fresher"
        elif years == 0:
            return f"{months} month{'s' if months > 1 else ''}"
        elif months == 0:
            return f"{years} year{'s' if years > 1 else ''}"
        else:
            return f"{years} year{'s' if years > 1 else ''} {months} month{'s' if months > 1 else ''}"

    @property
    def age(self):
        """Calculate age from date of birth"""
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))


class EmployeeDocument(models.Model):
    DOCUMENT_TYPES = [
        ('passport_photo', 'Passport Photo'),
        ('aadhar_card', 'Aadhar Card'),
        ('pan_card', 'PAN Card'),
        ('driving_license', 'Driving License'),
        ('voter_id', 'Voter ID'),
        ('passport', 'Passport'),
        ('electricity_bill', 'Electricity Bill'),
        ('tax_bill', 'Tax Bill'),
        ('rent_agreement', 'Rent Agreement'),
        ('ssc_marksheet', 'SSC Marksheet'),
        ('hsc_marksheet', 'HSC Marksheet'),
        ('graduation_certificate', 'Graduation Certificate'),
        ('pg_certificate', 'Post-Graduation Certificate'),
        ('graduation_marksheet', 'Graduation Marksheet'),
        ('pg_marksheet', 'Post-Graduation Marksheet'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='employee_documents/%Y/%m/', null=True, blank=True)
    is_submitted = models.BooleanField(default=False)
    submitted_date = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Employee Document"
        verbose_name_plural = "Employee Documents"
        unique_together = ['employee', 'document_type']

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_document_type_display()}"
