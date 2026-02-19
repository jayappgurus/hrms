from django.db import models

from django.contrib.auth.models import User

from django.utils import timezone

from datetime import date



class PerformanceEvaluation(models.Model):

    CATEGORY_CHOICES = [

        ('trainee_intern', 'Trainee/Intern'),

        ('probation', 'Probation'),

    ]

    

    STATUS_CHOICES = [

        ('pending', 'Pending'),

        ('submitted_manager', 'Submitted (Manager)'),

        ('submitted_hr', 'Submitted (HR)'),

        ('approved', 'Approved (Admin)'),

        ('rejected', 'Rejected (Admin)'),

    ]



    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='evaluations')

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    cycle_number = models.PositiveIntegerField() # 1, 2, 3

    period_start = models.DateField()

    period_end = models.DateField()

    due_date = models.DateField()

    training_start_date = models.DateField(null=True, blank=True, help_text="Training start date for trainees/interns")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    

    assigned_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_evaluations')

    

    # Form data (placeholder until user provides details)

    # We'll use a JSONField for the actual evaluation answers if supported, else TextField

    form_data = models.JSONField(default=dict, blank=True)

    

    # Audit fields tracked in logs but also summarized here for convenience

    submitted_at = models.DateTimeField(null=True, blank=True)

    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_evals')

    

    approved_at = models.DateTimeField(null=True, blank=True)

    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_evals')

    

    rejection_reason = models.TextField(blank=True, null=True)

    

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        verbose_name = "Performance Evaluation"

        verbose_name_plural = "Performance Evaluations"

        ordering = ['-due_date', 'employee']

        unique_together = ['employee', 'category', 'cycle_number']



    def __str__(self):

        return f"{self.employee.full_name} - Cycle {self.cycle_number} ({self.get_category_display()})"



    @property

    def is_overdue(self):

        return self.status == 'pending' and self.due_date < date.today()



class EvaluationAuditLog(models.Model):

    evaluation = models.ForeignKey(PerformanceEvaluation, on_delete=models.CASCADE, related_name='audit_logs')

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    action = models.CharField(max_length=100) # e.g., 'Created', 'Submitted', 'Approved', 'Rejected'

    details = models.TextField(blank=True, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)



    class Meta:

        ordering = ['-timestamp']

