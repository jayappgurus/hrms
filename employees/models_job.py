from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone
from datetime import date


class JobDescription(models.Model):
    """Job Description model for managing job postings and descriptions"""
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    ]
    
    EXPERIENCE_LEVEL_CHOICES = [
        ('fresher', 'Fresher'),
        ('junior', 'Junior (0-2 years)'),
        ('mid_level', 'Mid Level (2-5 years)'),
        ('senior', 'Senior (5-10 years)'),
        ('lead', 'Lead (10+ years)'),
        ('manager', 'Manager'),
    ]
    
    NOTICE_PERIOD_CHOICES = [
        ('immediate', 'Immediate'),
        ('15_days', '15 Days'),
        ('30_days', '30 Days'),
        ('45_days', '45 Days'),
        ('60_days', '60 Days'),
        ('90_days', '90 Days'),
        ('3_months', '3 Months'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('on_hold', 'On Hold'),
    ]
    
    WORK_MODE_CHOICES = [
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
        ('office', 'Office'),
    ]
    
    # Basic Job Information
    title = models.CharField(max_length=200, help_text="Job title")
    designation = models.ForeignKey('Designation', on_delete=models.CASCADE, related_name='job_descriptions')
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name='job_descriptions')
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default='fresher')
    
    # Job Details
    job_description = models.TextField(help_text="Detailed job description")
    responsibilities = models.TextField(help_text="Key responsibilities and duties")
    requirements = models.TextField(help_text="Required skills and qualifications")
    experience_criteria = models.TextField(help_text="Specific experience requirements")
    
    # Compensation and Benefits
    min_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Minimum salary")
    max_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Maximum salary")
    currency = models.CharField(max_length=3, default='INR', help_text="Currency code")
    
    # Location and Work Details
    location = models.CharField(max_length=200, help_text="Job location")
    work_mode = models.CharField(max_length=50, help_text="Work mode (Remote, Hybrid, Office)")
    travel_required = models.BooleanField(default=False, help_text="Travel required for this role")
    
    # Application Details
    number_of_vacancies = models.PositiveIntegerField(default=1, help_text="Number of positions available")
    application_deadline = models.DateField(null=True, blank=True, help_text="Last date to apply")
    
    # Company and Process Details
    company_description = models.TextField(blank=True, null=True, help_text="Company description for this role")
    interview_process = models.TextField(blank=True, null=True, help_text="Interview process details")
    
    # Status and Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False, help_text="Feature this job on homepage")
    is_urgent = models.BooleanField(default=False, help_text="Mark as urgent opening")
    
    # JD Document
    jd_document = models.FileField(upload_to='job_descriptions/%Y/%m/', null=True, blank=True, help_text="Job description document")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    posted_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='posted_jobs')
    
    class Meta:
        verbose_name = "Job Description"
        verbose_name_plural = "Job Descriptions"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.designation.name}"
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def days_until_deadline(self):
        if self.application_deadline:
            delta = self.application_deadline - date.today()
            return delta.days if delta.days > 0 else 0
        return None


class JobApplication(models.Model):
    """Job application model for tracking candidates"""
    
    SOURCE_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('website', 'Company Website'),
        ('referral', 'Employee Referral'),
        ('campus', 'Campus Drive'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('interviewed', 'Interviewed'),
        ('offer_extended', 'Offer Extended'),
        ('offer_accepted', 'Offer Accepted'),
        ('offer_rejected', 'Offer Rejected'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    # Basic Information
    job = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='applications')
    candidate_name = models.CharField(max_length=100, help_text="Full name of candidate")
    
    # Contact Information
    email = models.EmailField(help_text="Candidate email address")
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Contact number")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='other')
    
    # Referral Information
    referred_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='referred_candidates', help_text="Employee who referred this candidate")
    referral_notes = models.TextField(blank=True, null=True, help_text="Referral details")
    
    # Current Information
    current_organization = models.CharField(max_length=200, blank=True, null=True, help_text="Current company")
    current_ctc = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Current CTC")
    expected_ctc = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Expected CTC")
    is_negotiable = models.BooleanField(default=True, help_text="Salary is negotiable")
    
    # Experience and Education
    total_experience = models.PositiveIntegerField(default=0, help_text="Total years of experience")
    relevant_experience = models.PositiveIntegerField(null=True, blank=True, help_text="Relevant years of experience")
    
    # Education Details
    degree_name = models.CharField(max_length=200, blank=True, null=True, help_text="Degree name")
    passing_year = models.PositiveIntegerField(null=True, blank=True, help_text="Year of passing")
    
    # Additional Information
    training_included = models.BooleanField(default=False, help_text="Training included in package")
    official_notice_period = models.CharField(max_length=50, blank=True, null=True, help_text="Official notice period")
    current_location = models.CharField(max_length=200, blank=True, null=True, help_text="Current location")
    preferred_location = models.CharField(max_length=200, blank=True, null=True, help_text="Preferred work location")
    available_for_interview = models.BooleanField(default=True, help_text="Available for interview")
    
    # Documents
    resume = models.FileField(upload_to='resumes/%Y/%m/', null=True, blank=True, help_text="Candidate resume")
    cover_letter = models.FileField(upload_to='cover_letters/%Y/%m/', null=True, blank=True, help_text="Cover letter")
    
    # Status and Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    interview_notes = models.TextField(blank=True, null=True, help_text="Interview feedback and notes")
    rejection_reason = models.TextField(blank=True, null=True, help_text="Reason for rejection")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.candidate_name} - {self.job.title}"
    
    @property
    def is_active_candidate(self):
        return self.status in ['received', 'under_review', 'shortlisted', 'interview_scheduled', 'interviewed']


class JobApplicationUser(models.Model):
    """User model for job applications"""
    username = models.CharField(max_length=150, unique=True, help_text="Username for application tracking")
    email = models.EmailField(unique=True, help_text="User email address")
    full_name = models.CharField(max_length=200, help_text="Full name of user")
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Contact number")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, help_text="Whether this user account is active")
    
    class Meta:
        verbose_name = "Job Application User"
        verbose_name_plural = "Job Application Users"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.full_name


class InterviewSchedule(models.Model):
    """Interview scheduling model"""
    
    INTERVIEW_TYPE_CHOICES = [
        ('technical', 'Technical Round'),
        ('practical', 'Practical Round'),
        ('managerial', 'Managerial Round'),
        ('hr', 'HR Round'),
    ]
    
    PLATFORM_CHOICES = [
        ('google_meet', 'Google Meet'),
        ('physical', 'Physical'),
        ('zoom', 'Zoom'),
        ('teams', 'Microsoft Teams'),
        ('phone', 'Phone'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='interviews')
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPE_CHOICES)
    scheduled_date = models.DateField(help_text="Interview date")
    scheduled_time = models.TimeField(help_text="Interview time")
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, default='google_meet', help_text="Interview platform")
    meeting_link = models.URLField(blank=True, null=True, help_text="Meeting link for virtual interviews")
    location = models.CharField(max_length=200, blank=True, null=True, help_text="Interview location for physical interviews")
    
    taken_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='interviews_conducted', help_text="Employee conducting the interview")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    remarks = models.TextField(blank=True, null=True, help_text="Interview remarks (no character limit)")
    
    # Legacy fields (keeping for backward compatibility)
    duration_minutes = models.PositiveIntegerField(default=60, help_text="Expected duration in minutes")
    interview_mode = models.CharField(max_length=50, blank=True, null=True, help_text="Interview mode (deprecated, use platform)")
    interviewer = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='interviews_conducted_legacy')
    notes = models.TextField(blank=True, null=True, help_text="Interview notes")
    feedback = models.TextField(blank=True, null=True, help_text="Interview feedback")
    rating = models.PositiveIntegerField(null=True, blank=True, help_text="Candidate rating (1-10)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Interview Schedule"
        verbose_name_plural = "Interview Schedules"
        ordering = ['scheduled_date', 'scheduled_time']
    
    def __str__(self):
        return f"{self.application.candidate_name} - {self.get_interview_type_display()} - {self.scheduled_date}"
