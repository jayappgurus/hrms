from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, ListView, FormView
from django.http import HttpResponse, HttpResponseForbidden, FileResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import Employee, EmployeeIncrement, SalarySlip
from .forms import PaySlipGenerationForm
import os
from datetime import date
from xhtml2pdf import pisa
from io import BytesIO

class SalaryDetailsView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'employees/salary_details.html'
    context_object_name = 'employee'

    def get_object(self, queryset=None):
        # Regular employees can only see their own salary details
        if not self.request.user.is_staff and not self.request.user.is_superuser:
            return get_object_or_404(Employee, user_profile__user=self.request.user)
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.get_object()
        context['salary_components'] = employee.salary_components

        # Check if eligible for payslip
        # PaySlip generation option will be shown to only confirmed employees who are not in training or internship.
        is_eligible = employee.period_type == 'confirmed' and employee.employment_status == 'active'
        context['payslip_eligible'] = is_eligible

        if is_eligible:
            context['payslip_form'] = PaySlipGenerationForm(employee=employee)

        return context

class IncrementDetailsView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'employees/increment_details.html'
    context_object_name = 'employee'

    def get_object(self, queryset=None):
        if not self.request.user.is_staff and not self.request.user.is_superuser:
            return get_object_or_404(Employee, user_profile__user=self.request.user)
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.get_object()
        # Show all the previous increments in descending order.
        context['increments'] = employee.increments.all().order_by('-effective_date')
        return context

class GeneratePaySlipView(LoginRequiredMixin, FormView):
    form_class = PaySlipGenerationForm
    template_name = 'employees/salary_details.html'

    def post(self, request, *args, **kwargs):
        employee_id = kwargs.get('pk')
        employee = get_object_or_404(Employee, pk=employee_id)

        # Permission check
        if not request.user.is_staff and not request.user.is_superuser:
            if employee.user_profile.user != request.user:
                return HttpResponseForbidden("You cannot generate payslips for others.")

        # Eligibility check
        if employee.period_type != 'confirmed' or employee.employment_status != 'active':
            messages.error(request, "Only confirmed employees are eligible for payslips.")
            return redirect('employees:salary_details', pk=employee.id)

        form = PaySlipGenerationForm(request.POST, employee=employee)
        if form.is_valid():
            month = int(form.cleaned_data.get('month'))
            year = int(form.cleaned_data.get('year'))

            # Additional validation: Cannot generate for future dates
            today = date.today()
            if year > today.year or (year == today.year and month > today.month):
                messages.error(request, "Cannot generate payslips for future months.")
                return redirect('employees:salary_details', pk=employee.id)

            joining_date = employee.joining_date
            if joining_date and (year < joining_date.year or (year == joining_date.year and month < joining_date.month)):
                messages.error(request, f"Payslip can only be generated for months starting from your joining date ({joining_date.strftime('%B %Y')}).")
                return redirect('employees:salary_details', pk=employee.id)

            # Get context for PDF rendering
            month_name = dict(form.fields['month'].choices).get(int(month))

            context = {
                'employee': employee,
                'salary': employee.salary_components,
                'month_name': month_name,
                'year': year,
                'current_date': date.today(),
            }

            html = render_to_string('employees/payslip_pdf.html', context)
            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

            if not pdf.err:
                pdf_content = result.getvalue()

                action = request.POST.get('action', 'email')

                if action == 'download':
                    response = HttpResponse(pdf_content, content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="payslip_{month_name}_{year}.pdf"'
                    return response

                try:
                    # Generate email with HTML and plain text versions
                    subject = f"Payslip for {month_name} {year} - {employee.full_name}"
                    
                    # Email context
                    email_context = {
                        'employee_name': employee.full_name,
                        'employee_code': employee.employee_code,
                        'department': employee.department.name,
                        'designation': employee.designation.name,
                        'month_name': month_name,
                        'year': year,
                    }
                    
                    # Save PDF to database and get download URL
                    from django.core.files.base import ContentFile
                    slip, created = SalarySlip.objects.update_or_create(
                        employee=employee,
                        month=month,
                        year=year,
                        defaults={'is_emailed': True}
                    )
                    
                    # Save PDF file
                    pdf_filename = f'payslip_{employee.employee_code}_{month_name}_{year}.pdf'
                    slip.pdf_file.save(pdf_filename, ContentFile(pdf_content), save=True)
                    
                    # Add download URL to email context
                    download_url = request.build_absolute_uri(slip.get_download_url())
                    email_context['download_url'] = download_url
                    
                    # Render both HTML and plain text versions
                    html_body = render_to_string('emails/payslip_email.html', email_context)
                    plain_body = render_to_string('emails/payslip_email.txt', email_context)

                    # Create email with both versions
                    email = EmailMultiAlternatives(
                        subject,
                        plain_body,
                        settings.DEFAULT_FROM_EMAIL,
                        [employee.official_email]
                    )
                    email.attach_alternative(html_body, "text/html")
                    email.attach(f'payslip_{month_name}_{year}.pdf', pdf_content, 'application/pdf')
                    email.send()

                    messages.success(request, f"Payslip for {month_name} {year} has been sent to your email.")
                except Exception as e:
                    messages.error(request, f"Error sending email: {str(e)}")
            else:
                messages.error(request, "Error generating PDF payslip.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")

        return redirect('employees:salary_details', pk=employee.id)


@login_required
def download_payslip(request, slip_id):
    """Download payslip PDF from portal"""
    slip = get_object_or_404(SalarySlip, id=slip_id)
    
    # Permission check - employees can only download their own payslips
    if not request.user.is_staff and not request.user.is_superuser:
        if not hasattr(slip.employee, 'user_profile') or slip.employee.user_profile.user != request.user:
            return HttpResponseForbidden("You don't have permission to download this payslip.")
    
    # Check if PDF file exists
    if not slip.pdf_file:
        messages.error(request, "PDF file not found. Please regenerate the payslip.")
        return redirect('employees:salary_details', pk=slip.employee.id)
    
    # Increment download count
    slip.download_count += 1
    slip.save()
    
    # Serve the file
    try:
        response = FileResponse(
            slip.pdf_file.open('rb'),
            content_type='application/pdf'
        )
        filename = f'payslip_{slip.employee.employee_code}_{slip.month}_{slip.year}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        messages.error(request, f"Error downloading file: {str(e)}")
        return redirect('employees:salary_details', pk=slip.employee.id)
