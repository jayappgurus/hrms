from django import forms
from django.core.validators import RegexValidator, EmailValidator
from .models_job import JobDescription, JobApplication, InterviewSchedule
from .models import Department, Designation


class JobDescriptionForm(forms.ModelForm):
    """Form for creating and editing job descriptions"""
    class Meta:
        model = JobDescription
        fields = [
            'title', 'designation', 'department', 'employment_type', 'experience_level',
            'required_qualifications', 'skills_requirements',
            'min_salary', 'max_salary', 'currency', 'location', 'work_mode',
            'number_of_vacancies', 'application_deadline',
            'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter job title'
            }),
            'designation': forms.Select(attrs={
                'class': 'form-control',
            }),
            'department': forms.Select(attrs={
                'class': 'form-control',
            }),
            'employment_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'experience_level': forms.Select(attrs={
                'class': 'form-control',
            }),
            'required_qualifications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Required qualifications for the role...'
            }),
            'skills_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Required skills and competencies...'
            }),
            'min_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Minimum salary'
            }),
            'max_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Maximum salary'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-control',
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job location'
            }),
            'work_mode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Remote, Hybrid, Office'
            }),
            'number_of_vacancies': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Number of positions'
            }),
            'application_deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Job Title'
        self.fields['designation'].label = 'Designation'
        self.fields['department'].label = 'Department'
        self.fields['employment_type'].label = 'Employment Type'
        self.fields['experience_level'].label = 'Experience Level'
        self.fields['required_qualifications'].label = 'Required Qualifications'
        self.fields['skills_requirements'].label = 'Skills & Requirements'
        self.fields['min_salary'].label = 'Minimum Salary'
        self.fields['max_salary'].label = 'Maximum Salary'
        self.fields['currency'].label = 'Currency'
        self.fields['location'].label = 'Location'
        self.fields['work_mode'].label = 'Work Mode'
        self.fields['number_of_vacancies'].label = 'Number of Vacancies'
        self.fields['application_deadline'].label = 'Application Deadline'
        self.fields['status'].label = 'Status'

        # Set currency choices
        self.fields['currency'].widget.choices = [
            ('INR', 'INR - Indian Rupee'),
            ('USD', 'USD - US Dollar'),
            ('EUR', 'EUR - Euro'),
            ('GBP', 'GBP - British Pound'),
            ('AUD', 'AUD - Australian Dollar'),
            ('CAD', 'CAD - Canadian Dollar'),
            ('SGD', 'SGD - Singapore Dollar'),
            ('AED', 'AED - UAE Dirham'),
        ]


class JobApplicationForm(forms.ModelForm):
    """Form for job applications"""
    class Meta:
        model = JobApplication
        fields = [
            'job', 'candidate_name', 'email', 'phone_number', 'source', 'referred_by', 'referral_notes',
            'current_organization', 'current_ctc', 'expected_ctc', 'is_negotiable',
            'total_experience', 'relevant_experience', 'degree_name', 'passing_year',
            'training_included', 'official_notice_period', 'current_location', 'preferred_location',
            'available_for_interview', 'resume', 'cover_letter'
        ]
        widgets = {
            'job': forms.Select(attrs={
                'class': 'form-control',
            }),
            'candidate_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact number'
            }),
            'source': forms.Select(attrs={
                'class': 'form-control',
            }),
            'referred_by': forms.Select(attrs={
                'class': 'form-control',
            }),
            'referral_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Referral details...'
            }),
            'current_organization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Current company'
            }),
            'current_ctc': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Current CTC'
            }),
            'expected_ctc': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Expected CTC'
            }),
            'total_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Total years'
            }),
            'relevant_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Relevant years'
            }),
            'degree_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Degree name'
            }),
            'passing_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1950',
                'max': '2030',
                'placeholder': 'Year of passing'
            }),
            'official_notice_period': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 30 days, 3 months'
            }),
            'current_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Current location'
            }),
            'preferred_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Preferred work location'
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            'cover_letter': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['job'].label = 'Applied Position'
        self.fields['candidate_name'].label = 'Candidate Name'
        self.fields['email'].label = 'Email Address'
        self.fields['phone_number'].label = 'Contact Number'
        self.fields['source'].label = 'Source'
        self.fields['referred_by'].label = 'Referred By (Employee)'
        self.fields['referral_notes'].label = 'Referral Notes'
        self.fields['current_organization'].label = 'Current Organization'
        self.fields['current_ctc'].label = 'Current CTC'
        self.fields['expected_ctc'].label = 'Expected CTC (ECTC)'
        self.fields['is_negotiable'].label = 'Negotiable'
        self.fields['total_experience'].label = 'Total Experience (Years)'
        self.fields['relevant_experience'].label = 'Relevant Experience (Years)'
        self.fields['degree_name'].label = 'Degree Name'
        self.fields['passing_year'].label = 'Passing Year'
        self.fields['training_included'].label = 'Training Included'
        self.fields['official_notice_period'].label = 'Official Notice Period'
        self.fields['current_location'].label = 'Current Location'
        self.fields['preferred_location'].label = 'Preferred Location'
        self.fields['available_for_interview'].label = 'Available for Interview'
        self.fields['resume'].label = 'Resume/CV'
        self.fields['cover_letter'].label = 'Cover Letter'
        
        # Make referred_by optional and add empty label
        self.fields['referred_by'].required = False
        self.fields['referred_by'].empty_label = "No Referral"
        
        # Add Bootstrap classes to checkboxes
        self.fields['is_negotiable'].widget.attrs['class'] = 'form-check-input'
        self.fields['training_included'].widget.attrs['class'] = 'form-check-input'
        self.fields['available_for_interview'].widget.attrs['class'] = 'form-check-input'


class InterviewScheduleForm(forms.ModelForm):
    """Form for scheduling interviews"""
    class Meta:
        model = InterviewSchedule
        fields = [
            'application', 'interview_type', 'scheduled_date', 'scheduled_time',
            'platform', 'meeting_link', 'location', 'taken_by', 'status', 'remarks'
        ]
        widgets = {
            'application': forms.Select(attrs={
                'class': 'form-control',
            }),
            'interview_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'scheduled_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'scheduled_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'platform': forms.Select(attrs={
                'class': 'form-control',
            }),
            'meeting_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://meet.google.com/...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Office address or location'
            }),
            'taken_by': forms.Select(attrs={
                'class': 'form-control',
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter interview remarks (no character limit)...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['application'].label = 'Candidate'
        self.fields['interview_type'].label = 'Type of Round'
        self.fields['scheduled_date'].label = 'Date'
        self.fields['scheduled_time'].label = 'Time'
        self.fields['platform'].label = 'Platform'
        self.fields['meeting_link'].label = 'Meeting Link'
        self.fields['location'].label = 'Location'
        self.fields['taken_by'].label = 'Taken By (Employee)'
        self.fields['status'].label = 'Status'
        self.fields['remarks'].label = 'Remarks'
        
        # Make fields optional as needed
        self.fields['meeting_link'].required = False
        self.fields['location'].required = False
        self.fields['remarks'].required = False
        self.fields['taken_by'].required = False
        
        # Add empty label for taken_by
        self.fields['taken_by'].empty_label = "Select Employee"


class JobSearchForm(forms.Form):
    """Form for searching job descriptions"""
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title, department, or skills...'
        })
    )
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="All Departments",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    employment_type = forms.ChoiceField(
        choices=[('', 'All Types')] + JobDescription.EMPLOYMENT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    experience_level = forms.ChoiceField(
        choices=[('', 'All Levels')] + JobDescription.EXPERIENCE_LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + JobDescription.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class CandidateSearchForm(forms.Form):
    """Form for searching candidates"""
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, email, or skills...'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + JobApplication.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    source = forms.ChoiceField(
        choices=[('', 'All Sources')] + JobApplication.SOURCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
