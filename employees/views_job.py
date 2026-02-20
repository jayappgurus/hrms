from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils import timezone
from django.contrib import messages
from .models_job import JobDescription, JobApplication, InterviewSchedule
from .models import Department, Designation, Employee
from .forms_job import JobDescriptionForm, JobApplicationForm, InterviewScheduleForm, JobSearchForm, CandidateSearchForm

class JobDescriptionListView(LoginRequiredMixin, ListView):
    model = JobDescription
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 9

    def get_queryset(self):
        queryset = JobDescription.objects.select_related('designation', 'department', 'posted_by').all()

        # Search functionality
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(required_qualifications__icontains=search) |
                Q(skills_requirements__icontains=search)
            )

        # Filter by department
        department_id = self.request.GET.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)

        # Filter by employment type
        employment_type = self.request.GET.get('employment_type')
        if employment_type:
            queryset = queryset.filter(employment_type=employment_type)

        # Filter by experience level
        experience_level = self.request.GET.get('experience_level')
        if experience_level:
            queryset = queryset.filter(experience_level=experience_level)

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = JobSearchForm(self.request.GET)
        context['departments'] = Department.objects.all()
        context['total_jobs'] = self.get_queryset().count()
        context['active_jobs'] = self.get_queryset().filter(status='active').count()
        context['job_form'] = JobDescriptionForm()
        return context

class JobDescriptionDetailView(LoginRequiredMixin, DetailView):
    model = JobDescription
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_jobs'] = JobDescription.objects.filter(
            designation=self.object.designation,
            department=self.object.department,
            status='active'
        ).exclude(pk=self.object.pk)[:3]
        return context

class JobDescriptionCreateView(LoginRequiredMixin, CreateView):
    model = JobDescription
    form_class = JobDescriptionForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('employees:job_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Serialize designations to JSON for JavaScript use
        all_designations = list(Designation.objects.values('id', 'name', 'department_id'))
        import json
        context['all_designations'] = json.dumps(all_designations)
        return context

    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        messages.success(self.request, 'Job description created successfully!')
        return super().form_valid(form)

class JobDescriptionUpdateView(LoginRequiredMixin, UpdateView):
    model = JobDescription
    form_class = JobDescriptionForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('employees:job_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Serialize designations to JSON for JavaScript use
        all_designations = list(Designation.objects.values('id', 'name', 'department_id'))
        import json
        context['all_designations'] = json.dumps(all_designations)
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Job description updated successfully!')
        return super().form_valid(form)

class JobDescriptionDeleteView(LoginRequiredMixin, DeleteView):
    model = JobDescription
    template_name = 'jobs/job_confirm_delete.html'
    success_url = reverse_lazy('employees:job_list')

    def dispatch(self, request, *args, **kwargs):
        # Only allow superusers and staff to delete jobs
        if not request.user.is_superuser and not request.user.is_staff:
            messages.error(request, 'You do not have permission to delete jobs.')
            return redirect('employees:job_list')
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Job description deleted successfully!')
        return super().delete(request, *args, **kwargs)

class JobApplicationListView(LoginRequiredMixin, ListView):
    model = JobApplication
    template_name = 'jobs/candidate_list.html'
    context_object_name = 'applications'
    paginate_by = 15

    def get_queryset(self):
        queryset = JobApplication.objects.select_related('job', 'job__designation', 'job__department', 'referred_by').all()

        # Search functionality
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(candidate_name__icontains=search) |
                Q(email__icontains=search) |
                Q(current_organization__icontains=search)
            )

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by source
        source = self.request.GET.get('source')
        if source:
            queryset = queryset.filter(source=source)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = CandidateSearchForm(self.request.GET)
        context['total_applications'] = self.get_queryset().count()
        context['active_applications'] = self.get_queryset().filter(
            status__in=['received', 'under_review', 'shortlisted', 'interview_scheduled']
        ).count()
        return context

class JobApplicationDetailView(LoginRequiredMixin, DetailView):
    model = JobApplication
    template_name = 'jobs/candidate_detail.html'
    context_object_name = 'application'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['interviews'] = InterviewSchedule.objects.filter(
            application=self.object
        ).order_by('scheduled_date')
        return context

class InterviewScheduleView(LoginRequiredMixin, CreateView):
    model = InterviewSchedule
    form_class = InterviewScheduleForm
    template_name = 'jobs/interview_schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application_id = self.request.GET.get('application_id')
        if application_id:
            context['application'] = get_object_or_404(JobApplication, pk=application_id)
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Interview scheduled successfully!')
        return super().form_valid(form)

def update_application_status(request, pk):
    """Update application status via AJAX"""
    application = get_object_or_404(JobApplication, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')

        if new_status in [choice[0] for choice in JobApplication.STATUS_CHOICES]:
            application.status = new_status
            if notes:
                application.interview_notes = notes
            application.save()

            return JsonResponse({
                'success': True,
                'message': f'Application status updated to {application.get_status_display()}'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid status'
            })

    return JsonResponse({'success': False, 'message': 'Method not allowed'})

def download_resume(request, pk):
    """Download candidate resume"""
    application = get_object_or_404(JobApplication, pk=pk)

    if application.resume:
        response = HttpResponse(application.resume.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{application.candidate_name}_resume.pdf"'
        return response

    return JsonResponse({'success': False, 'message': 'Resume not found'})

def download_jd_document(request, pk):
    """Download job description document"""
    job = get_object_or_404(JobDescription, pk=pk)

    if job.jd_document:
        response = HttpResponse(job.jd_document.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{job.title}_JD.pdf"'
        return response

    return JsonResponse({'success': False, 'message': 'JD document not found'})

class CandidateTrackerView(LoginRequiredMixin, ListView):
    """Designation-wise candidate tracking"""
    model = JobApplication
    template_name = 'jobs/candidate_tracker.html'
    context_object_name = 'applications'
    paginate_by = 50

    def get_queryset(self):
        queryset = JobApplication.objects.select_related(
            'job',
            'job__designation',
            'job__department',
            'referred_by'
        ).filter(
            status__in=['received', 'under_review', 'shortlisted', 'interview_scheduled', 'interviewed', 'offer_extended']
        )

        # Filter by designation
        designation_id = self.request.GET.get('designation')
        if designation_id:
            queryset = queryset.filter(job__designation_id=designation_id)

        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(candidate_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone_number__icontains=search) |
                Q(current_organization__icontains=search)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all designations with active job applications count
        designations = Designation.objects.annotate(
            active_applications_count=Count(
                'job_descriptions__applications',
                filter=Q(
                    job_descriptions__applications__status__in=[
                        'received', 'under_review', 'shortlisted',
                        'interview_scheduled', 'interviewed', 'offer_extended'
                    ]
                )
            )
        ).filter(active_applications_count__gt=0).order_by('name')

        context['designations'] = designations
        context['selected_designation_id'] = self.request.GET.get('designation', '')

        # Get selected designation details
        if context['selected_designation_id']:
            try:
                context['selected_designation'] = Designation.objects.get(id=context['selected_designation_id'])
            except Designation.DoesNotExist:
                context['selected_designation'] = None

        # Statistics
        context['total_candidates'] = JobApplication.objects.filter(
            status__in=['received', 'under_review', 'shortlisted', 'interview_scheduled', 'interviewed', 'offer_extended']
        ).count()

        context['received_count'] = JobApplication.objects.filter(status='received').count()
        context['under_review_count'] = JobApplication.objects.filter(status='under_review').count()
        context['shortlisted_count'] = JobApplication.objects.filter(status='shortlisted').count()
        context['interview_count'] = JobApplication.objects.filter(
            status__in=['interview_scheduled', 'interviewed']
        ).count()
        context['offered_count'] = JobApplication.objects.filter(status='offer_extended').count()

        return context

class CurrentOpeningsView(LoginRequiredMixin, ListView):
    """Active job openings listing"""
    model = JobDescription
    template_name = 'jobs/current_openings.html'
    context_object_name = 'jobs'
    paginate_by = 9

    def get_queryset(self):
        queryset = JobDescription.objects.filter(
            status='active'
        ).select_related('designation', 'department')
        
        # Apply filters
        department = self.request.GET.get('department')
        if department:
            queryset = queryset.filter(department_id=department)
        
        employment_type = self.request.GET.get('employment_type')
        if employment_type:
            queryset = queryset.filter(employment_type=employment_type)
        
        experience_level = self.request.GET.get('experience_level')
        if experience_level:
            queryset = queryset.filter(experience_level=experience_level)
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_openings'] = JobDescription.objects.filter(status='active').count()
        context['departments'] = Department.objects.all().order_by('name')
        context['job_form'] = JobDescriptionForm()
        return context

#     ====== INTERVIEW MANAGEMENT VIEWS     ======

@login_required
def add_interview(request, application_id):
    """Add interview round for a candidate"""
    # Only allow superusers and staff
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'You do not have permission to add interviews.')
        return redirect('employees:candidate_tracker')

    application = get_object_or_404(JobApplication, pk=application_id)

    if request.method == 'POST':
        form = InterviewScheduleForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.save()
            messages.success(request, f'Interview round added successfully for {application.candidate_name}.')
            return redirect('employees:candidate_detail', pk=application_id)
    else:
        form = InterviewScheduleForm(initial={'application': application})

    context = {
        'form': form,
        'application': application,
        'page_title': 'Add Interview Round'
    }
    return render(request, 'jobs/interview_form.html', context)

@login_required
def edit_interview(request, interview_id):
    """Edit interview round details"""
    # Only allow superusers and staff
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit interviews.')
        return redirect('employees:candidate_tracker')

    interview = get_object_or_404(InterviewSchedule, pk=interview_id)

    if request.method == 'POST':
        form = InterviewScheduleForm(request.POST, instance=interview)
        if form.is_valid():
            form.save()
            messages.success(request, 'Interview round updated successfully.')
            return redirect('employees:candidate_detail', pk=interview.application.pk)
    else:
        form = InterviewScheduleForm(instance=interview)

    context = {
        'form': form,
        'interview': interview,
        'application': interview.application,
        'page_title': 'Edit Interview Round'
    }
    return render(request, 'jobs/interview_form.html', context)

@login_required
def delete_interview(request, interview_id):
    """Delete interview round"""
    # Only allow superusers and staff
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete interviews.')
        return redirect('employees:candidate_tracker')

    interview = get_object_or_404(InterviewSchedule, pk=interview_id)
    application_id = interview.application.pk

    if request.method == 'POST':
        interview.delete()
        messages.success(request, 'Interview round deleted successfully.')
        return redirect('employees:candidate_detail', pk=application_id)

    context = {
        'interview': interview,
        'application': interview.application
    }
    return render(request, 'jobs/interview_confirm_delete.html', context)
