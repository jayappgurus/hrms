from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .models_job import JobDescription, JobApplication, JobApplicationUser
from .forms_job import JobApplicationForm
from .models import Department, Designation

@require_http_methods(["GET", "POST"])
def add_job_application_view(request):
    """Handle job application creation with candidate linking"""

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)

            # Link to the selected job
            job_id = request.POST.get('job')
            if job_id:
                try:
                    job = JobDescription.objects.get(pk=job_id, status='active')
                    application.job = job
                except JobDescription.DoesNotExist:
                    messages.error(request, 'Selected job not found or is not active.')
                    return redirect('employees:add_job_application')

            application.status = 'received'
            application.save()

            messages.success(request, f'Application submitted successfully for {job.title if job else "position"}!')
            return redirect('employees:job_application_success')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'jobs/add_job_application.html', {'form': form})
    else:
        form = JobApplicationForm()
        # Get available active jobs for selection
        available_jobs = JobDescription.objects.filter(status='active').select_related('designation', 'department')

        return render(request, 'jobs/add_job_application.html', {
            'form': form,
            'available_jobs': available_jobs
        })

def job_application_success_view(request):
    """Success page after application submission"""
    return render(request, 'jobs/job_application_success.html')
