from django.db import models
from django.core.validators import MinValueValidator
from employees.models import Employee
from decimal import Decimal


class SalaryStructure(models.Model):
    """
    Salary Structure Template - defines how salary components are calculated
    """
    name = models.CharField(max_length=200, help_text="Structure name (e.g., 'Standard Structure 2024')")
    description = models.TextField(blank=True, null=True)
    
    # Percentage configurations
    basic_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=40.00,
        help_text="Basic as % of CTC (default 40%)"
    )
    hra_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=40.00,
        help_text="HRA as % of Basic (default 40%)"
    )
    
    # Fixed allowances
    medical_allowance = models.DecimalField(
        max_digits=10, decimal_places=2, default=1250.00,
        help_text="Fixed medical allowance"
    )
    conveyance_allowance = models.DecimalField(
        max_digits=10, decimal_places=2, default=1600.00,
        help_text="Fixed conveyance allowance"
    )
    
    # Deduction configurations
    pf_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=12.00,
        help_text="PF as % of Basic (default 12%)"
    )
    esic_threshold = models.DecimalField(
        max_digits=10, decimal_places=2, default=21000.00,
        help_text="ESIC applicable if gross <= this amount"
    )
    esic_employee_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.75,
        help_text="Employee ESIC % (default 0.75%)"
    )
    esic_employer_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=3.25,
        help_text="Employer ESIC % (default 3.25%)"
    )
    professional_tax = models.DecimalField(
        max_digits=10, decimal_places=2, default=200.00,
        help_text="Fixed professional tax"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Salary Structure"
        verbose_name_plural = "Salary Structures"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def calculate_components(self, ctc):
        """
        Calculate all salary components based on CTC
        Returns a dictionary with all components
        """
        ctc = Decimal(str(ctc))
        
        # Calculate Basic
        basic = (ctc * self.basic_percentage / 100).quantize(Decimal('0.01'))
        
        # Calculate HRA
        hra = (basic * self.hra_percentage / 100).quantize(Decimal('0.01'))
        
        # Fixed allowances
        medical = self.medical_allowance
        conveyance = self.conveyance_allowance
        
        # Calculate Special Allowance (balancing figure)
        special = (ctc - basic - hra - medical - conveyance).quantize(Decimal('0.01'))
        
        # Gross Salary
        gross = basic + hra + medical + conveyance + special
        
        # Employee Deductions
        employee_pf = (basic * self.pf_percentage / 100).quantize(Decimal('0.01'))
        
        # ESIC only if gross <= threshold
        employee_esic = Decimal('0.00')
        if gross <= self.esic_threshold:
            employee_esic = (gross * self.esic_employee_percentage / 100).quantize(Decimal('0.01'))
        
        pt = self.professional_tax
        
        # Total Employee Deductions
        total_deductions = employee_pf + employee_esic + pt
        
        # Net Salary
        net_salary = gross - total_deductions
        
        # Employer Contributions
        employer_pf = (basic * self.pf_percentage / 100).quantize(Decimal('0.01'))
        employer_esic = Decimal('0.00')
        if gross <= self.esic_threshold:
            employer_esic = (gross * self.esic_employer_percentage / 100).quantize(Decimal('0.01'))
        
        total_employer_contribution = employer_pf + employer_esic
        
        # Total CTC (verification)
        total_ctc = gross + total_employer_contribution
        
        return {
            'earnings': {
                'basic': basic,
                'hra': hra,
                'medical_allowance': medical,
                'conveyance_allowance': conveyance,
                'special_allowance': special,
            },
            'gross_salary': gross,
            'employee_deductions': {
                'pf': employee_pf,
                'esic': employee_esic,
                'professional_tax': pt,
            },
            'total_deductions': total_deductions,
            'net_salary': net_salary,
            'employer_contributions': {
                'pf': employer_pf,
                'esic': employer_esic,
            },
            'total_employer_contribution': total_employer_contribution,
            'total_ctc': total_ctc,
        }


class EmployeeSalaryStructure(models.Model):
    """
    Links an employee to a salary structure with specific CTC
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_assignments')
    salary_structure = models.ForeignKey(SalaryStructure, on_delete=models.PROTECT)
    
    ctc = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Cost to Company (monthly)"
    )
    
    effective_from = models.DateField(help_text="Date from which this structure is effective")
    effective_to = models.DateField(null=True, blank=True, help_text="Date until which this structure is effective")
    
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='salary_structures_created')
    
    class Meta:
        verbose_name = "Employee Salary Structure"
        verbose_name_plural = "Employee Salary Structures"
        ordering = ['-effective_from']
        unique_together = ['employee', 'effective_from']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.salary_structure.name} - ₹{self.ctc}"
    
    def get_calculated_components(self):
        """Get calculated salary components"""
        return self.salary_structure.calculate_components(self.ctc)


class SalarySlip(models.Model):
    """
    Monthly salary slip for an employee
    """
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='new_salary_slips')
    employee_salary_structure = models.ForeignKey(EmployeeSalaryStructure, on_delete=models.SET_NULL, null=True)
    
    month = models.IntegerField(help_text="Month (1-12)")
    year = models.IntegerField(help_text="Year")
    
    # Working days
    total_working_days = models.IntegerField(default=26)
    days_present = models.IntegerField(default=26)
    days_absent = models.IntegerField(default=0)
    lop_days = models.IntegerField(default=0, help_text="Loss of Pay days")
    
    # Earnings
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    hra = models.DecimalField(max_digits=12, decimal_places=2)
    medical_allowance = models.DecimalField(max_digits=12, decimal_places=2)
    conveyance_allowance = models.DecimalField(max_digits=12, decimal_places=2)
    special_allowance = models.DecimalField(max_digits=12, decimal_places=2)
    overtime_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Deductions
    employee_pf = models.DecimalField(max_digits=12, decimal_places=2)
    employee_esic = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    professional_tax = models.DecimalField(max_digits=12, decimal_places=2)
    lop_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Net
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Employer contributions
    employer_pf = models.DecimalField(max_digits=12, decimal_places=2)
    employer_esic = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('sent', 'Sent to Employee'),
        ('paid', 'Paid'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    payment_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    generated_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = "Salary Slip"
        verbose_name_plural = "Salary Slips"
        ordering = ['-year', '-month']
        unique_together = ['employee', 'month', 'year']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.month}/{self.year}"
    
    @property
    def month_name(self):
        from datetime import date
        return date(2000, self.month, 1).strftime('%B')
    
    def calculate_lop_deduction(self):
        """Calculate LOP deduction based on absent days"""
        if self.lop_days > 0 and self.total_working_days > 0:
            per_day_salary = self.gross_salary / Decimal(str(self.total_working_days))
            return (per_day_salary * Decimal(str(self.lop_days))).quantize(Decimal('0.01'))
        return Decimal('0.00')
    
    def save(self, *args, **kwargs):
        # Auto-calculate LOP deduction
        if self.lop_days > 0:
            self.lop_deduction = self.calculate_lop_deduction()
        
        # Recalculate totals
        self.total_deductions = (
            self.employee_pf + self.employee_esic + self.professional_tax +
            self.lop_deduction + self.other_deductions
        )
        self.net_salary = self.gross_salary + self.overtime_amount - self.total_deductions
        
        super().save(*args, **kwargs)


class SalaryHistory(models.Model):
    """
    Track salary changes over time
    """
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='new_salary_history')
    
    previous_ctc = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    new_ctc = models.DecimalField(max_digits=12, decimal_places=2)
    
    increment_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    increment_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    reason = models.CharField(max_length=200, help_text="Reason for change (e.g., Annual Increment, Promotion)")
    effective_date = models.DateField()
    
    remarks = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = "Salary History"
        verbose_name_plural = "Salary Histories"
        ordering = ['-effective_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.effective_date} - ₹{self.new_ctc}"
    
    def save(self, *args, **kwargs):
        # Calculate increment if previous CTC exists
        if self.previous_ctc and self.new_ctc:
            self.increment_amount = self.new_ctc - self.previous_ctc
            if self.previous_ctc > 0:
                self.increment_percentage = ((self.increment_amount / self.previous_ctc) * 100).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)
