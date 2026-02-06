from django import forms
from django.core.validators import RegexValidator, EmailValidator
from .models import Employee, Department, Designation, EmergencyContact, EmployeeDocument


class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'mobile_number', 'email', 'address', 'relationship']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter emergency contact name'
            }),
            'mobile_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter mobile number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter address'
            }),
            'relationship': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Spouse, Parent, Sibling'
            }),
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'employee_code', 'full_name', 'department', 'designation', 'joining_date', 'relieving_date',
            'employment_status', 'mobile_number', 'official_email', 'personal_email', 'local_address',
            'permanent_address', 'date_of_birth', 'marital_status', 'anniversary_date',
            'highest_qualification', 'total_experience_years', 'total_experience_months',
            'aadhar_card_number', 'pan_card_number'
        ]
        widgets = {
            'employee_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter unique employee code'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name'
            }),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'joining_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'relieving_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'mobile_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter mobile number'
            }),
            'official_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'official@company.com'
            }),
            'personal_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'personal@email.com'
            }),
            'local_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter local address'
            }),
            'permanent_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter permanent address'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'anniversary_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'highest_qualification': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., B.Tech, MBA, etc.'
            }),
            'total_experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Years'
            }),
            'total_experience_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 11,
                'placeholder': 'Months'
            }),
            'aadhar_card_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12-digit Aadhar number',
                'maxlength': 12
            }),
            'pan_card_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'PAN number (e.g., ABCDE1234F)',
                'style': 'text-transform: uppercase'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.all()
        self.fields['designation'].queryset = Designation.objects.all()
        
        # Add dynamic designation filtering based on department
        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['designation'].queryset = Designation.objects.filter(department_id=department_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.department:
            self.fields['designation'].queryset = Designation.objects.filter(department=self.instance.department)

    def clean_employee_code(self):
        employee_code = self.cleaned_data.get('employee_code')
        if not employee_code:
            raise forms.ValidationError("Employee code is required.")
        return employee_code.upper()

    def clean_aadhar_card_number(self):
        aadhar = self.cleaned_data.get('aadhar_card_number')
        if aadhar and len(aadhar) != 12:
            raise forms.ValidationError("Aadhar card number must be exactly 12 digits.")
        return aadhar

    def clean_pan_card_number(self):
        pan = self.cleaned_data.get('pan_card_number')
        if pan:
            pan = pan.upper()
            if len(pan) != 10:
                raise forms.ValidationError("PAN card number must be exactly 10 characters.")
        return pan

    def clean(self):
        cleaned_data = super().clean()
        joining_date = cleaned_data.get('joining_date')
        relieving_date = cleaned_data.get('relieving_date')
        anniversary_date = cleaned_data.get('anniversary_date')
        marital_status = cleaned_data.get('marital_status')

        # Validation: Relieving date should be after joining date
        if joining_date and relieving_date and relieving_date < joining_date:
            raise forms.ValidationError("Relieving date cannot be before joining date.")

        # Validation: Anniversary date required if married
        if marital_status == 'married' and not anniversary_date:
            raise forms.ValidationError("Anniversary date is required when marital status is Married.")

        return cleaned_data


class EmployeeSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by employee name...',
            'autocomplete': 'off'
        })
    )


class EmployeeDocumentForm(forms.ModelForm):
    class Meta:
        model = EmployeeDocument
        fields = ['document_type', 'document_file', 'is_submitted', 'remarks']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'document_file': forms.FileInput(attrs={'class': 'form-control'}),
            'is_submitted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any remarks about the document'
            }),
        }


from django.contrib.auth.models import User


class UserProfileForm(forms.ModelForm):
    """Form for user profile management"""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
        }
