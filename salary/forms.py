from django import forms
from .models import SalaryStructure, EmployeeSalaryStructure, SalarySlip, SalaryHistory
from employees.models import Employee
from decimal import Decimal


class SalaryStructureForm(forms.ModelForm):
    """Form for creating/editing salary structures"""
    
    class Meta:
        model = SalaryStructure
        fields = [
            'name', 'description', 'basic_percentage', 'hra_percentage',
            'medical_allowance', 'conveyance_allowance', 'pf_percentage',
            'esic_threshold', 'esic_employee_percentage', 'esic_employer_percentage',
            'professional_tax', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Standard Structure 2024'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'basic_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'hra_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'medical_allowance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'conveyance_allowance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'pf_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'esic_threshold': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'esic_employee_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'esic_employer_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'professional_tax': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_basic_percentage(self):
        basic = self.cleaned_data.get('basic_percentage')
        if basic and basic > 50:
            raise forms.ValidationError("Basic salary should not exceed 50% of CTC as per best practices")
        return basic


class EmployeeSalaryStructureForm(forms.ModelForm):
    """Form for assigning salary structure to employee"""
    
    class Meta:
        model = EmployeeSalaryStructure
        fields = ['employee', 'salary_structure', 'ctc', 'effective_from', 'effective_to', 'remarks']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'salary_structure': forms.Select(attrs={'class': 'form-control'}),
            'ctc': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Enter monthly CTC',
                'id': 'id_ctc'
            }),
            'effective_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'effective_to': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(employment_status__in=['probation', 'confirmed'])
        self.fields['salary_structure'].queryset = SalaryStructure.objects.filter(is_active=True)
        self.fields['effective_to'].required = False
        self.fields['remarks'].required = False
    
    def clean_ctc(self):
        ctc = self.cleaned_data.get('ctc')
        if ctc and ctc <= 0:
            raise forms.ValidationError("CTC must be a positive value")
        return ctc
    
    def clean(self):
        cleaned_data = super().clean()
        effective_from = cleaned_data.get('effective_from')
        effective_to = cleaned_data.get('effective_to')
        
        if effective_from and effective_to and effective_to < effective_from:
            raise forms.ValidationError("Effective To date must be after Effective From date")
        
        return cleaned_data


class SalarySlipForm(forms.ModelForm):
    """Form for generating salary slips"""
    
    class Meta:
        model = SalarySlip
        fields = [
            'employee', 'month', 'year', 'total_working_days', 'days_present',
            'days_absent', 'lop_days', 'overtime_amount', 'other_deductions', 'remarks'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'month': forms.Select(attrs={'class': 'form-control'}, choices=[
                (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
                (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
                (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
            ]),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': '2020', 'max': '2030'}),
            'total_working_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '31'}),
            'days_present': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '31'}),
            'days_absent': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '31'}),
            'lop_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '31'}),
            'overtime_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'other_deductions': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(employment_status__in=['probation', 'confirmed'])
        self.fields['overtime_amount'].required = False
        self.fields['other_deductions'].required = False
        self.fields['remarks'].required = False


class SalaryHistoryForm(forms.ModelForm):
    """Form for recording salary history"""
    
    class Meta:
        model = SalaryHistory
        fields = ['employee', 'previous_ctc', 'new_ctc', 'reason', 'effective_date', 'remarks']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'previous_ctc': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': True}),
            'new_ctc': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'reason': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Annual Increment, Promotion'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(employment_status__in=['probation', 'confirmed'])
        self.fields['previous_ctc'].required = False
        self.fields['remarks'].required = False


class CTCCalculatorForm(forms.Form):
    """Simple form for CTC calculation preview"""
    
    ctc = forms.DecimalField(
        max_value=9999999.99,
        min_value=0.01,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter monthly CTC (e.g., 45000)',
            'step': '0.01',
            'id': 'calculator_ctc'
        }),
        label='Monthly CTC (₹)'
    )
    
    salary_structure = forms.ModelChoiceField(
        queryset=SalaryStructure.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'calculator_structure'}),
        label='Salary Structure'
    )
