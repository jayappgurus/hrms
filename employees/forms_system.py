from django import forms
from .models import SystemDetail, MacAddress, SystemRequirement, Employee
from django.contrib.auth.models import User


class SystemDetailForm(forms.ModelForm):
    class Meta:
        model = SystemDetail
        fields = [
            'employee', 'department', 'cpu_ram', 'cpu_storage', 'cpu_company_name', 'cpu_processor', 'cpu_label_no',
            'screen_company_name', 'screen_label_no', 'screen_size',
            'keyboard_company_name', 'keyboard_label_no',
            'mouse_company_name', 'mouse_label_no',
            'has_headphone', 'headphone_company_name', 'headphone_label_no',
            'has_extender', 'extender_label', 'extender_name',
            'is_active'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select', 'id': 'id_employee'}),
            'department': forms.Select(attrs={'class': 'form-select', 'id': 'id_department'}),
            'cpu_ram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 16GB DDR4'}),
            'cpu_storage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 512GB SSD'}),
            'cpu_company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Dell, HP'}),
            'cpu_processor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Intel i7'}),
            'cpu_label_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unique asset number'}),
            
            'screen_company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Dell, LG'}),
            'screen_label_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unique asset number'}),
            'screen_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 24 inch'}),
            
            'keyboard_company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Logitech'}),
            'keyboard_label_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unique asset number'}),
            
            'mouse_company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Logitech'}),
            'mouse_label_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unique asset number'}),
            
            'has_headphone': forms.Select(choices=[(False, 'No'), (True, 'Yes')], attrs={'class': 'form-select', 'id': 'id_has_headphone'}),
            'headphone_company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'}),
            'headphone_label_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Label number'}),
            
            'has_extender': forms.Select(choices=[(False, 'No'), (True, 'Yes')], attrs={'class': 'form-select', 'id': 'id_has_extender'}),
            'extender_label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Label'}),
            'extender_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(employment_status='active')
        self.fields['department'].required = False
        # Remove readonly to allow submission, but keep it visually readonly with JavaScript
        self.fields['department'].widget.attrs['style'] = 'background-color: #e9ecef;'
        
        # Make headphone fields not required initially
        self.fields['headphone_company_name'].required = False
        self.fields['headphone_label_no'].required = False
        
        # Make extender fields not required initially
        self.fields['extender_label'].required = False
        self.fields['extender_name'].required = False

    def clean(self):
        cleaned_data = super().clean()
        has_headphone = cleaned_data.get('has_headphone')
        has_extender = cleaned_data.get('has_extender')
        
        # Validate headphone fields if has_headphone is True
        if has_headphone:
            if not cleaned_data.get('headphone_company_name'):
                self.add_error('headphone_company_name', 'This field is required when headphone is selected.')
            if not cleaned_data.get('headphone_label_no'):
                self.add_error('headphone_label_no', 'This field is required when headphone is selected.')
        
        # Validate extender fields if has_extender is True
        if has_extender:
            if not cleaned_data.get('extender_label'):
                self.add_error('extender_label', 'This field is required when extender is selected.')
            if not cleaned_data.get('extender_name'):
                self.add_error('extender_name', 'This field is required when extender is selected.')
        
        return cleaned_data


class MacAddressForm(forms.ModelForm):
    class Meta:
        model = MacAddress
        fields = ['employee', 'mac_address']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'mac_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00:1B:44:11:3A:B7',
                'pattern': '([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(employment_status='active')
        self.fields['employee'].required = True


class SystemRequirementForm(forms.ModelForm):
    REQUIREMENT_TYPE_CHOICES = [
        ('cpu', 'CPU/Computer'),
        ('screen', 'Monitor/Screen'),
        ('keyboard', 'Keyboard'),
        ('mouse', 'Mouse'),
        ('headphone', 'Headphone'),
        ('other', 'Other'),
    ]
    
    requirement_types = forms.MultipleChoiceField(
        choices=REQUIREMENT_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
        label='Requirement Types'
    )
    
    class Meta:
        model = SystemRequirement
        fields = [
            'requested_by', 'requested_for', 'requirement_types',
            'cpu_ram', 'cpu_storage', 'cpu_company_name', 'cpu_processor',
            'screen_company_name', 'screen_size',
            'keyboard_company_name',
            'mouse_company_name',
            'headphone_company_name',
            'other_device_name', 'other_specification',
            'estimated_cost', 'priority', 'status',
            'order_date', 'expected_delivery_date', 'vendor_name'
        ]
        widgets = {
            'requested_by': forms.Select(attrs={'class': 'form-select'}),
            'requested_for': forms.Select(attrs={'class': 'form-select'}),
            
            # CPU Fields
            'cpu_ram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 16GB DDR4'}),
            'cpu_storage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 512GB SSD'}),
            'cpu_company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Dell, HP'}),
            'cpu_processor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Intel i7'}),
            
            # Screen Fields
            'screen_company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Dell, LG'}),
            'screen_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 24 inch'}),
            
            # Keyboard Fields
            'keyboard_company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Logitech'}),
            
            # Mouse Fields
            'mouse_company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Logitech'}),
            
            # Headphone Fields
            'headphone_company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Logitech'}),
            
            'estimated_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'order_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'vendor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vendor/supplier name'}),
            
            # Other Device Fields
            'other_device_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Printer, Scanner, etc.'}),
            'other_specification': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detailed specifications...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['requested_by'].queryset = Employee.objects.filter(employment_status='active')
        self.fields['requested_for'].queryset = Employee.objects.filter(employment_status='active')
        
        # Make optional fields
        self.fields['requested_for'].required = False
        self.fields['estimated_cost'].required = False
        self.fields['order_date'].required = False
        self.fields['expected_delivery_date'].required = False
        self.fields['vendor_name'].required = False
        
        # All specification fields are optional initially
        spec_fields = [
            'cpu_ram', 'cpu_storage', 'cpu_company_name', 'cpu_processor',
            'screen_company_name', 'screen_size',
            'keyboard_company_name',
            'mouse_company_name',
            'headphone_company_name',
            'other_device_name', 'other_specification',
        ]
        for field in spec_fields:
            self.fields[field].required = False
        
        # If editing existing requirement, populate requirement_types from model
        if self.instance and self.instance.pk:
            self.initial['requirement_types'] = self.instance.get_requirement_types_list()
    
    def clean(self):
        cleaned_data = super().clean()
        requirement_types = cleaned_data.get('requirement_types', [])
        
        # Validate that required fields for each selected type are filled
        if 'cpu' in requirement_types:
            if not cleaned_data.get('cpu_ram') or not cleaned_data.get('cpu_storage') or not cleaned_data.get('cpu_company_name'):
                raise forms.ValidationError('CPU specifications (RAM, Storage, Company Name) are required when CPU is selected.')
        
        if 'screen' in requirement_types:
            if not cleaned_data.get('screen_company_name') or not cleaned_data.get('screen_size'):
                raise forms.ValidationError('Screen specifications (Company Name, Size) are required when Monitor is selected.')
        
        if 'keyboard' in requirement_types:
            if not cleaned_data.get('keyboard_company_name'):
                raise forms.ValidationError('Keyboard company name is required when Keyboard is selected.')
        
        if 'mouse' in requirement_types:
            if not cleaned_data.get('mouse_company_name'):
                raise forms.ValidationError('Mouse company name is required when Mouse is selected.')
        
        if 'headphone' in requirement_types:
            if not cleaned_data.get('headphone_company_name'):
                raise forms.ValidationError('Headphone company name is required when Headphone is selected.')
        
        if 'other' in requirement_types:
            if not cleaned_data.get('other_device_name'):
                raise forms.ValidationError('Device name is required when Other is selected.')
            if not cleaned_data.get('other_specification'):
                raise forms.ValidationError('Specification is required when Other is selected.')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Convert list to comma-separated string
        requirement_types = self.cleaned_data.get('requirement_types', [])
        instance.requirement_types = ','.join(requirement_types)
        if commit:
            instance.save()
        return instance
