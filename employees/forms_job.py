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
            'job_description', 'responsibilities', 'requirements', 'experience_criteria',
            'min_salary', 'max_salary', 'currency', 'location', 'work_mode',
            'travel_required', 'number_of_vacancies', 'application_deadline',
            'company_description', 'interview_process', 'status', 'is_featured', 'is_urgent', 'jd_document'
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
            'job_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Detailed job description...'
            }),
            'responsibilities': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Key responsibilities and duties...'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Required skills and qualifications...'
            }),
            'experience_criteria': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Specific experience requirements...'
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
            'company_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Company description for this role...'
            }),
            'interview_process': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Interview process details...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
            }),
            'jd_document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Job Title'
        self.fields['designation'].label = 'Designation'
        self.fields['department'].label = 'Department'
        self.fields['employment_type'].label = 'Employment Type'
        self.fields['experience_level'].label = 'Experience Level'
        self.fields['job_description'].label = 'Job Description'
        self.fields['responsibilities'].label = 'Key Responsibilities'
        self.fields['requirements'].label = 'Requirements'
        self.fields['experience_criteria'].label = 'Experience Criteria'
        self.fields['min_salary'].label = 'Minimum Salary'
        self.fields['max_salary'].label = 'Maximum Salary'
        self.fields['currency'].label = 'Currency'
        self.fields['location'].label = 'Location'
        self.fields['work_mode'].label = 'Work Mode'
        self.fields['travel_required'].label = 'Travel Required'
        self.fields['number_of_vacancies'].label = 'Number of Vacancies'
        self.fields['application_deadline'].label = 'Application Deadline'
        self.fields['company_description'].label = 'Company Description'
        self.fields['interview_process'].label = 'Interview Process'
        self.fields['status'].label = 'Status'
        self.fields['is_featured'].label = 'Featured Job'
        self.fields['is_urgent'].label = 'Urgent Opening'
        self.fields['jd_document'].label = 'Job Description Document'
        
        # Add Bootstrap classes to checkboxes
        self.fields['travel_required'].widget.attrs['class'] = 'form-check-input'
        self.fields['is_featured'].widget.attrs['class'] = 'form-check-input'
        self.fields['is_urgent'].widget.attrs['class'] = 'form-check-input'

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
            'job', 'candidate_name', 'email', 'phone_number', 'source',
            'current_organization', 'current_ctc', 'expected_ctc', 'is_negotiable',
            'total_experience', 'relevant_experience', 'degree_name', 'passing_year',
            'training_included', 'official_notice_period', 'preferred_location',
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
        self.fields['current_organization'].label = 'Current Organization'
        self.fields['current_ctc'].label = 'Current CTC'
        self.fields['expected_ctc'].label = 'Expected CTC (ECTC)'
        self.fields['is_negotiable'].label = 'Negotiable'
        self.fields['total_experience'].label = 'Total Experience'
        self.fields['relevant_experience'].label = 'Relevant Experience'
        self.fields['degree_name'].label = 'Degree Name'
        self.fields['passing_year'].label = 'Passing Year'
        self.fields['training_included'].label = 'Training Included'
        self.fields['official_notice_period'].label = 'Official Notice Period'
        self.fields['preferred_location'].label = 'Preferred Location'
        self.fields['available_for_interview'].label = 'Available for Interview'
        self.fields['resume'].label = 'Resume/CV'
        self.fields['cover_letter'].label = 'Cover Letter'
        
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
            'duration_minutes', 'interview_mode', 'meeting_link', 'location',
            'interviewer', 'status'
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
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '15',
                'max': '480',
                'placeholder': 'Duration in minutes'
            }),
            'interview_mode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone, Video, In-person'
            }),
            'meeting_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://meet.google.com/...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Interview location'
            }),
            'interviewer': forms.Select(attrs={
                'class': 'form-control',
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['application'].label = 'Candidate'
        self.fields['interview_type'].label = 'Interview Type'
        self.fields['scheduled_date'].label = 'Interview Date'
        self.fields['scheduled_time'].label = 'Interview Time'
        self.fields['duration_minutes'].label = 'Duration (Minutes)'
        self.fields['interview_mode'].label = 'Interview Mode'
        self.fields['meeting_link'].label = 'Meeting Link'
        self.fields['location'].label = 'Location'
        self.fields['interviewer'].label = 'Interviewer'
        self.fields['status'].label = 'Status'


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
