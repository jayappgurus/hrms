from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import date

# Import job management models
from .models_job import JobDescription, JobApplication, InterviewSchedule

# Import job management models
from .models_job import JobDescription, JobApplication, InterviewSchedule

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('director', 'Director'),
        ('hr', 'HR'),
        ('accountant', 'Accountant'),
        ('manager', 'Manager'),
        ('it_admin', 'IT Admin'),
        ('employee', 'Employee'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    employee = models.OneToOneField('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='user_profile')
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
    def is_director(self):
        return self.role == 'director'

    @property
    def is_hr(self):
        return self.role == 'hr'

    @property
    def is_accountant(self):
        return self.role == 'accountant'

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
        return self.role in ['admin', 'director', 'hr', 'manager']

    @property
    def can_view_all_employees(self):
        return self.role in ['admin', 'director', 'hr']

    @property
    def can_manage_system(self):
        return self.role in ['admin', 'it_admin']

    @property
    def can_manage_finance(self):
        return self.role in ['admin', 'director', 'accountant']

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    head = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')
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

    PERIOD_TYPE_CHOICES = [
        ('trainee', 'Trainee (6 Months)'),
        ('intern', 'Intern'),
        ('probation', 'Probation (3 Months)'),
        ('notice_period', 'Notice Period'),
        ('confirmed', 'Confirmed'),
    ]

    QUALIFICATION_CHOICES = [
        ('B.Com', 'B.Com'),
        ('B.E (Civil)', 'B.E (Civil)'),
        ('B.E. (CE)', 'B.E. (CE)'),
        ('B.E. (CSE)', 'B.E. (CSE)'),
        ('B.E./B.Tech (IT)', 'B.E./B.Tech (IT)'),
        ('BBA', 'BBA'),
        ('BCA', 'BCA'),
        ('BCA & PGDCA', 'BCA & PGDCA'),
        ('ITI', 'ITI'),
        ('MBA (BA)', 'MBA (BA)'),
        ('MBA (Finance)', 'MBA (Finance)'),
        ('MBA (IT)', 'MBA (IT)'),
        ('MCA', 'MCA'),
        ('M.Sc. IT', 'M.Sc. IT'),
        ('PGDCA', 'PGDCA'),
        ('PGDM', 'PGDM'),
        ('Other', 'Other'),
    ]

    # Core Employee Details
    employee_code = models.CharField(max_length=20, unique=True, help_text="Unique employee code")
    full_name = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='employee_profiles/%Y/%m/', null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees')
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, related_name='employees')
    joining_date = models.DateField()
    probation_end_date = models.DateField(null=True, blank=True, help_text="End of probation period (3 months from joining)")
    relieving_date = models.DateField(null=True, blank=True)
    employment_status = models.CharField(max_length=10, choices=EMPLOYMENT_STATUS_CHOICES, default='active')
    current_ctc = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Current CTC in INR")
    salary_structure = models.TextField(blank=True, null=True, help_text="Copy from salary slip")

    # Contact Information
    mobile_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid mobile number.")]
    )
    official_email = models.EmailField(validators=[EmailValidator()], unique=True)
    personal_email = models.EmailField(validators=[EmailValidator()], blank=True, null=True)
    local_address = models.TextField(blank=True)
    permanent_address = models.TextField(blank=True)

    # Emergency Contact
    emergency_contact = models.ForeignKey(EmergencyContact, on_delete=models.SET_NULL, null=True, blank=True)

    # Direct Emergency Contact Fields
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_mobile = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid mobile number.")]
    )
    emergency_contact_email = models.EmailField(validators=[EmailValidator()], blank=True, null=True)
    emergency_contact_address = models.TextField(blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True)

    # Personal Information
    date_of_birth = models.DateField()
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES)
    anniversary_date = models.DateField(null=True, blank=True)

    # Professional Information
    highest_qualification = models.CharField(max_length=100, choices=QUALIFICATION_CHOICES)
    total_experience_years = models.PositiveIntegerField(default=0)
    total_experience_months = models.PositiveIntegerField(default=0)
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPE_CHOICES, default='confirmed', help_text="Employee period type")

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

    # Document Tracker Extras
    graduates_marksheet_count = models.PositiveIntegerField(default=0, help_text="Number of marksheets for graduation/post-graduation")

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
        # Auto-generate employee code if not provided
        if not self.employee_code:
            # Get the latest employee code
            latest_employee = Employee.objects.order_by('-id').first()
            if latest_employee and latest_employee.employee_code and latest_employee.employee_code.startswith('EM'):
                # Extract numeric part and increment
                try:
                    latest_num = int(latest_employee.employee_code[2:])
                    new_num = latest_num + 1
                except ValueError:
                    new_num = 1
            else:
                new_num = 1

            # Format as EM0001, EM0002, etc.
            self.employee_code = f'EM{new_num:04d}'

        # Auto-calculate probation status
        if self.joining_date:
            # Convert string to date object if needed
            if isinstance(self.joining_date, str):
                from datetime import datetime
                self.joining_date = datetime.strptime(self.joining_date, '%Y-%m-%d').date()

            # Calculate probation end date (3 months from joining date) if not provided
            if not self.probation_end_date:
                probation_months = 3
                year = self.joining_date.year
                month = self.joining_date.month + probation_months
                day = self.joining_date.day

                # Adjust year and month if overflow
                if month > 12:
                    year += 1
                    month -= 12

                # Handle end of month edge cases (e.g. Nov 31 doesn't exist)
                try:
                    self.probation_end_date = date(year, month, day)
                except ValueError:
                    # Fallback to last day of the month
                    if month == 12:
                        self.probation_end_date = date(year, 31, 31) # date(year, 12, 31) -> fixed logic
                        # Simplified:
                        import calendar
                        last_day = calendar.monthrange(year, month)[1]
                        self.probation_end_date = date(year, month, last_day)

            # Note: probation_status field removed - use period_type instead


        super().save(*args, **kwargs)

    @property
    def salary_components(self):
        """Calculate salary components based on standard structure if not explicitly defined"""
        if self.salary_structure:
            try:
                import json
                return json.loads(self.salary_structure)
            except:
                pass

        # Standard Indian Salary Structure Calculation
        # Assumptions:
        # Basic = 50% of CTC
        # HRA = 50% of Basic
        # Special Allowance = Balancing Figure
        # PF = 12% of Basic (Employee Share)
        # PT = 200 (Standard)

        monthly_ctc = float(self.current_ctc) / 12
        basic = monthly_ctc * 0.50
        hra = basic * 0.50

        # Statutory limits
        pf_employee = min(basic * 0.12, 1800) # Capped at 1800 for standard compliance
        pt = 200

        # Allowances must sum up to Gross
        # Gross (Earnings) = CTC / 12 (Simplified)
        # Net Take Home = Gross - Deductions

        special_allowance = monthly_ctc - (basic + hra)

        # Ensure non-negative
        if special_allowance < 0:
            special_allowance = 0
            # Adjust HRA or Basic if needed, but for now strict 50% rule

        gross_salary = basic + hra + special_allowance
        total_deductions = pf_employee + pt
        net_salary = gross_salary - total_deductions

        return {
            'earnings': {
                'Basic_Salary': round(basic, 2),
                'House_Rent_Allowance': round(hra, 2),
                'Special_Allowance': round(special_allowance, 2),
            },
            'deductions': {
                'Provident_Fund': round(pf_employee, 2),
                'Professional_Tax': round(pt, 2),
            },
            'gross_salary': round(gross_salary, 2),
            'total_deductions': round(total_deductions, 2),
            'net_salary': round(net_salary, 2),
            'ctc_monthly': round(monthly_ctc, 2),
            'ctc_annual': round(float(self.current_ctc), 2)
        }
        # Delete the associated UserProfile and User if they exist
        if hasattr(self, 'user_profile'):
            user = self.user_profile.user
            self.user_profile.delete()
            user.delete()
        super().delete(*args, **kwargs)

    @property
    def total_experience_display(self):
        """Return formatted total experience"""
        years = self.total_experience_years
        months = self.total_experience_months
        if years == 0 and months == 0:
            return "Fresher"
        elif years == 0:
            return f"{months} mo"
        elif months == 0:
            return f"{years} y"
        else:
            return f"{years} y {months} mo"

    @property
    def age(self):
        """Calculate age from date of birth"""
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    @property
    def plain_password(self):
        """Return the default generated password for the employee"""
        if hasattr(self, 'user_profile'):
            return f"{self.user_profile.user.username}@123"
        return "—"

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

    @property
    def allocated_to(self):
        """Get current user if device is allocated"""
        current = self.current_allocation
        return current.assigned_to if current else None

class Device(models.Model):
    DEVICE_TYPE_CHOICES = [
        ('laptop', 'Laptop'),
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
        ('accessories', 'Accessories'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('retired', 'Retired'),
    ]

    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICES)
    device_name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    purchase_date = models.DateField()
    warranty_details = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Device"
        verbose_name_plural = "Devices"
        ordering = ['-created_at']

    def __str__(self):
        return self.device_name

    @property
    def allocated_to(self):
        """Get current user if device is allocated"""
        current = self.current_allocation
        return current.assigned_to if current else None

    @property
    def current_allocation(self):
        return self.allocations.filter(returned_date__isnull=True).first()

class DeviceAllocation(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='allocations')
    assigned_to = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='device_allocations')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='device_assignments')
    assigned_date = models.DateTimeField(auto_now_add=True)
    returned_date = models.DateTimeField(null=True, blank=True)
    return_notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Device Allocation"
        verbose_name_plural = "Device Allocations"
        ordering = ['-assigned_date']

    def __str__(self):
        return f"{self.device.device_name} -> {self.assigned_to.full_name}"

    def save(self, *args, **kwargs):
        # Update device status based on allocation
        if self.returned_date:
            self.device.status = 'available'
        else:
            self.device.status = 'in_use'
        self.device.save()
        super().save(*args, **kwargs)

class PublicHoliday(models.Model):
    COUNTRY_CHOICES = [
        ('IN', 'India'),
        ('AU', 'Australia'),
    ]

    name = models.CharField(max_length=100)
    date = models.DateField()
    day = models.CharField(max_length=20)  # Monday, Tuesday, etc.
    year = models.IntegerField()
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, default='IN')
    is_optional = models.BooleanField(default=False, help_text="Optional holiday")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Public Holiday"
        verbose_name_plural = "Public Holidays"
        ordering = ['date']

    def __str__(self):
        return f"{self.name} ({self.date})"

class LeaveType(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('casual', 'Casual Leave (CL)'),
        ('emergency', 'Emergency Leave (EL)'),
        ('public_holiday', 'Public Holidays'),
        ('birthday', 'Birthday Leave'),
        ('marriage_anniversary', 'Marriage Anniversary Leave'),
        ('weekend', 'Weekends'),
        ('absence_marriage', 'Absence for Marriage'),
        ('paternity', 'Paternity'),
        ('maternity', 'Maternity'),
    ]

    name = models.CharField(max_length=100)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES, unique=True)
    max_days_per_year = models.IntegerField(default=12)
    duration_type = models.CharField(max_length=10, choices=[
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years'),
    ], default='days')
    is_paid = models.BooleanField(default=True)
    requires_document = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Leave Type"
        verbose_name_plural = "Leave Types"

    def __str__(self):
        return self.name

class LeaveApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_applications')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='applications')
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Changed to support 0.5 days
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Half-day leave fields
    is_half_day = models.BooleanField(default=False)
    scheduled_hours = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, help_text="Scheduled working hours for half-day calculation")
    is_wfh = models.BooleanField(default=False, help_text="Work from home")
    is_office = models.BooleanField(default=False, help_text="Work from office")

    # Sandwich rule tracking
    is_sandwich_leave = models.BooleanField(default=False, help_text="Leave includes non-working days due to sandwich rule")
    actual_working_days = models.IntegerField(null=True, blank=True, help_text="Actual working days in leave period")

    # Approval/Rejection
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    approved_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    # Paid absence specific fields
    is_first_child = models.BooleanField(default=False, null=True, blank=True, help_text="For paternity/maternity leave")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Leave Application"
        verbose_name_plural = "Leave Applications"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.start_date} to {self.end_date})"

    def save(self, *args, **kwargs):
        # Auto-calculate total days if not provided
        if not self.total_days and self.start_date and self.end_date:
            if self.is_half_day:
                # Will be calculated by the service
                self.total_days = 0.5
            else:
                self.total_days = (self.end_date - self.start_date).days + 1

        # Set approved date when status changes to approved
        if self.status == 'approved' and not self.approved_date:
            self.approved_date = timezone.now()

        super().save(*args, **kwargs)

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('danger', 'Danger'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    icon = models.CharField(max_length=50, default='bi-info-circle')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # For targeting specific users or all
    target_all = models.BooleanField(default=True)
    target_users = models.ManyToManyField(User, related_name='targeted_notifications', blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%Y-%m-%d')}"

class NotificationRead(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='reads')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_reads')
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('notification', 'user')
        verbose_name = "Notification Read"
        verbose_name_plural = "Notification Reads"

    def __str__(self):
        return f"{self.user.username} read {self.notification.title}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # For targeting specific users or all
    target_all = models.BooleanField(default=True)
    target_users = models.ManyToManyField(User, related_name='received_messages', blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"{self.subject} - from {self.sender.username}"

class MessageRead(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reads')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_reads')
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user')
        verbose_name = "Message Read"
        verbose_name_plural = "Message Reads"

    def __str__(self):
        return f"{self.user.username} read {self.message.subject}"

class EmployeeIncrement(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='increments')
    effective_date = models.DateField()
    new_designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, blank=True)
    previous_ctc = models.DecimalField(max_digits=12, decimal_places=2)
    incremented_amount = models.DecimalField(max_digits=12, decimal_places=2)
    increment_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    revised_ctc = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Employee Increment"
        verbose_name_plural = "Employee Increments"
        ordering = ['-effective_date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.effective_date}"

class SalarySlip(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_slips')
    month = models.IntegerField()
    year = models.IntegerField()
    generated_date = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='salary_slips/%Y/%m/', null=True, blank=True)
    is_emailed = models.BooleanField(default=False)
    download_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Salary Slip"
        verbose_name_plural = "Salary Slips"
        unique_together = ['employee', 'month', 'year']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.employee.full_name} - {self.month}/{self.year}"
    
    def get_download_url(self):
        from django.urls import reverse
        return reverse('employees:download_payslip', args=[self.id])
