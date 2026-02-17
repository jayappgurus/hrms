from django import forms
from datetime import date
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.auth.models import User
from .models import Employee, Department, Designation, EmergencyContact, EmployeeDocument, LeaveType, LeaveApplication, PublicHoliday

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
    # Emergency Contact Fields
    emergency_contact_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter emergency contact name'}))
    emergency_contact_mobile = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mobile number'}))
    emergency_contact_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}))
    emergency_contact_address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter emergency contact address'}))
    emergency_contact_relationship = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Spouse, Parent, Sibling'}))

    class Meta:
        model = Employee
        fields = [
            'employee_code', 'full_name', 'profile_picture', 'department', 'designation', 'joining_date', 'probation_end_date', 'relieving_date',
            'employment_status', 'current_ctc', 'salary_structure', 'mobile_number', 'official_email', 'personal_email', 'local_address',
            'permanent_address', 'date_of_birth', 'marital_status', 'anniversary_date',
            'highest_qualification', 'total_experience_years', 'total_experience_months',
            'period_type', 'aadhar_card_number', 'pan_card_number', 'graduates_marksheet_count',
            'emergency_contact_name', 'emergency_contact_mobile', 'emergency_contact_email', 'emergency_contact_address', 'emergency_contact_relationship'
        ]
        widgets = {
            'employee_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated if left blank'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'joining_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'YYYY-MM-DD'
            }),
            'probation_end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'YYYY-MM-DD'
            }),
            'relieving_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'YYYY-MM-DD'
            }),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'current_ctc': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Current CTC'
            }),
            'salary_structure': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter salary structure details...'
            }),
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
                'type': 'date',
                'placeholder': 'YYYY-MM-DD'
            }),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'anniversary_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'YYYY-MM-DD'
            }),
            'highest_qualification': forms.Select(attrs={
                'class': 'form-select'
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
            'period_type': forms.Select(attrs={'class': 'form-select'}),
            'graduates_marksheet_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'No. of marksheets'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.all()
        self.fields['employee_code'].required = False
        self.fields['graduates_marksheet_count'].required = False

        if self.instance and self.instance.pk and self.instance.emergency_contact:
            ec = self.instance.emergency_contact
            self.fields['emergency_contact_name'].initial = ec.name
            self.fields['emergency_contact_mobile'].initial = ec.mobile_number
            self.fields['emergency_contact_email'].initial = ec.email
            self.fields['emergency_contact_address'].initial = ec.address
            self.fields['emergency_contact_relationship'].initial = ec.relationship

        # Always show all designations for now
        self.fields['designation'].queryset = Designation.objects.all()

        # Add dynamic designation filtering based on department (for future use)
        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['designation'].queryset = Designation.objects.filter(department_id=department_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.department:
            self.fields['designation'].queryset = Designation.objects.filter(department=self.instance.department)

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

class EmployeeRegistrationForm(forms.ModelForm):
    """Form for employee self-registration"""
    # User fields
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username', 'id': 'id_username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create a password', 'id': 'id_password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password', 'id': 'id_confirm_password'}))
    full_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name', 'id': 'id_full_name'}))

    class Meta:
        model = Employee
        fields = [
            'full_name', 'department', 'designation', 'mobile_number', 'personal_email',
            'date_of_birth', 'marital_status',
            'highest_qualification', 'total_experience_years', 'total_experience_months',
            'aadhar_card_number', 'pan_card_number', 'local_address', 'permanent_address'
        ]
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mobile number'}),
            'personal_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'personal@email.com'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'highest_qualification': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Highest Qualification'}),
            'total_experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'total_experience_months': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 11}),
            'aadhar_card_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12-digit Aadhar number', 'maxlength': 12}),
            'pan_card_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PAN number', 'style': 'text-transform: uppercase'}),
            'local_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter local address'}),
            'permanent_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter permanent address'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.all()
        self.fields['designation'].queryset = Designation.objects.all()

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

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        marital_status = cleaned_data.get('marital_status')
        # Since we don't have anniversary_date in registration form,
        # we might want to handle it or just allow it to be empty for now.
        # But the model might require it if we add it later.

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Save emergency contact fields directly to the employee model
        instance.emergency_contact_name = self.cleaned_data.get('emergency_contact_name', '')
        instance.emergency_contact_mobile = self.cleaned_data.get('emergency_contact_mobile', '')
        instance.emergency_contact_email = self.cleaned_data.get('emergency_contact_email', '')
        instance.emergency_contact_address = self.cleaned_data.get('emergency_contact_address', '')

        if commit:
            instance.save()
        return instance

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

class LeaveTypeForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        fields = ['name', 'leave_type', 'max_days_per_year', 'duration_type', 'is_paid', 'requires_document', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter leave type name'
            }),
            'leave_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'max_days_per_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '365',
                'placeholder': 'Maximum days per year'
            }),
            'is_paid': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'requires_document': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Leave Type Name'
        self.fields['leave_type'].label = 'Leave Type Category'
        self.fields['max_days_per_year'].label = 'Maximum Days Per Year'
        self.fields['is_paid'].label = 'Paid Leave'
        self.fields['requires_document'].label = 'Document Required'
        self.fields['description'].label = 'Description'
        self.fields['is_active'].label = 'Active Status'

        # Add Bootstrap classes to checkboxes
        self.fields['is_paid'].widget.attrs['class'] = 'form-check-input'
        self.fields['requires_document'].widget.attrs['class'] = 'form-check-input'
        self.fields['is_active'].widget.attrs['class'] = 'form-check-input'

class LeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = LeaveApplication
        fields = [
            'leave_type', 'start_date', 'end_date', 'reason',
            'is_half_day', 'scheduled_hours', 'is_wfh', 'is_office',
            'is_first_child'
        ]
        widgets = {
            'leave_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_leave_type'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'id_start_date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'id_end_date'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter reason for leave application',
                'id': 'id_reason'
            }),
            'is_half_day': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_is_half_day'
            }),
            'scheduled_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '24',
                'step': '0.5',
                'placeholder': 'e.g., 8.0',
                'id': 'id_scheduled_hours'
            }),
            'is_wfh': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_is_wfh'
            }),
            'is_office': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_is_office'
            }),
            'is_first_child': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_is_first_child'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)
        self.fields['leave_type'].label = 'Leave Type'
        self.fields['start_date'].label = 'Start Date'
        self.fields['end_date'].label = 'End Date'
        self.fields['reason'].label = 'Reason'
        self.fields['is_half_day'].label = 'Half Day Leave'
        self.fields['scheduled_hours'].label = 'Scheduled Working Hours'
        self.fields['is_wfh'].label = 'Work From Home'
        self.fields['is_office'].label = 'Work From Office'
        self.fields['is_first_child'].label = 'Is this for your first child?'

        # Make fields optional initially
        self.fields['scheduled_hours'].required = False
        self.fields['is_first_child'].required = False

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        is_half_day = cleaned_data.get('is_half_day')
        scheduled_hours = cleaned_data.get('scheduled_hours')
        leave_type = cleaned_data.get('leave_type')

        # Validate dates
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after or equal to start date")

        # Validate half-day requirements
        if is_half_day and not scheduled_hours:
            raise forms.ValidationError("Scheduled hours are required for half-day leave")

        # Validate first child requirement for paternity/maternity
        if leave_type and leave_type.leave_type in ['paternity', 'maternity']:
            if 'is_first_child' not in cleaned_data or cleaned_data.get('is_first_child') is None:
                self.fields['is_first_child'].required = True

        return cleaned_data

class PublicHolidayForm(forms.ModelForm):
    class Meta:
        model = PublicHoliday
        fields = ['name', 'date', 'year', 'country', 'is_optional', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'modern-form-control',
                'placeholder': 'Enter holiday name'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'YYYY-MM-DD'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'modern-form-control',
                'min': 2020,
                'max': 2030
            }),
            'country': forms.Select(attrs={
                'class': 'modern-form-control'
            }),
            'is_optional': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'description': forms.Textarea(attrs={
                'class': 'modern-form-control',
                'rows': 3,
                'placeholder': 'Optional description'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Holiday Name'
        self.fields['date'].label = 'Date'
        self.fields['year'].label = 'Year'
        self.fields['country'].label = 'Country'
        self.fields['is_optional'].label = 'Optional Holiday'
        self.fields['description'].label = 'Description'
        self.fields['is_active'].label = 'Active'

        # Auto-populate day field based on date
        if self.instance and self.instance.pk:
            self.fields['day'] = forms.CharField(
                initial=self.instance.date.strftime('%A'),
                disabled=True,
                widget=forms.TextInput(attrs={
                    'class': 'modern-form-control',
                    'readonly': True
                })
            )
        else:
            self.fields['day'] = forms.CharField(
                required=False,
                disabled=True,
                widget=forms.TextInput(attrs={
                    'class': 'modern-form-control',
                    'readonly': True,
                    'placeholder': 'Will be auto-calculated'
                })
            )


    def save(self, commit=True):
        instance = super().save(commit=False)
        # Auto-calculate day from date
        if instance.date:
            instance.day = instance.date.strftime('%A')
        if commit:
            instance.save()
        return instance

class PaySlipGenerationForm(forms.Form):
    month = forms.ChoiceField(choices=[(i,  date(2000, i, 1).strftime('%B')) for i in range(1, 13)], widget=forms.Select(attrs={'class': 'form-select'}))
    year = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, **kwargs):
        employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)

        current_year = date.today().year
        start_year = current_year

        if employee and employee.joining_date:
            start_year = employee.joining_date.year

        year_choices = [(y, y) for y in range(start_year, current_year + 1)]
        # Sort in reverse to show latest year first
        year_choices.sort(key=lambda x: x[0], reverse=True)
        self.fields['year'].choices = year_choices
