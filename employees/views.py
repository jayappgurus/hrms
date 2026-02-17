from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
from .models import Employee, Department, Designation, EmergencyContact, EmployeeDocument, Device, DeviceAllocation, PublicHoliday, LeaveType, LeaveApplication, UserProfile
from .models_job import InterviewSchedule
from .forms import EmployeeForm, EmergencyContactForm, EmployeeSearchForm, EmployeeDocumentForm, LeaveTypeForm, LeaveApplicationForm, PublicHolidayForm, EmployeeRegistrationForm

class DashboardView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'employees/dashboard_new.html'
    context_object_name = 'employees'
    paginate_by = 20

    def get_queryset(self):
        queryset = Employee.objects.select_related('department', 'designation').all()
        return queryset.order_by('-created_at')[:5]  # Get recent 5 employees

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Statistics
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(employment_status='active').count()
        inactive_count = total_employees - active_employees

        context.update({
            'total_employees': total_employees,
            'active_employees': active_employees,
            'inactive_count': inactive_count,
            'recent_employees': self.get_queryset(),
            'departments': Department.objects.all(),
            'total_departments': Department.objects.count(),
            'interviews_today': InterviewSchedule.objects.filter(scheduled_date=timezone.now().date()).count(),
            'upcoming_holidays': PublicHoliday.objects.filter(date__gte=timezone.now().date(), is_active=True).order_by('date')[:5],
        })

        return context

class CalendarEventsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        start_str = request.GET.get('start')
        end_str = request.GET.get('end')

        if not start_str or not end_str:
            return JsonResponse({'error': 'Missing start or end date'}, status=400)

        from datetime import datetime
        try:
            # FullCalendar sends ISO strings like 2024-05-26T00:00:00Z or just 2024-05-26
            start_date = datetime.fromisoformat(start_str.replace('Z', '')).date()
            end_date = datetime.fromisoformat(end_str.replace('Z', '')).date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'}, status=400)

        events = []

        # 1. Birthdays
        employees = Employee.objects.filter(employment_status='active').exclude(date_of_birth__isnull=True)
        for emp in employees:
            # Create a birthday date for the range years
            current_year = start_date.year
            try:
                # Handle Feb 29
                if emp.date_of_birth.month == 2 and emp.date_of_birth.day == 29:
                    # check if current year is leap, else use Feb 28
                    if current_year % 4 == 0 and (current_year % 100 != 0 or current_year % 400 == 0):
                        bday = emp.date_of_birth.replace(year=current_year)
                    else:
                        bday = emp.date_of_birth.replace(year=current_year, day=28)
                else:
                    bday = emp.date_of_birth.replace(year=current_year)

                if start_date <= bday <= end_date:
                    events.append({
                        'id': f'bday-{emp.id}',
                        'title': f'🎂 {emp.full_name}',
                        'start': bday.isoformat(),
                        'allDay': True,
                        'className': 'bg-primary-subtle text-primary border-primary',
                        'extendedProps': {
                            'type': 'birthday',
                            'employee_id': emp.id
                        }
                    })

                # Also check next year if the range spans across years
                if end_date.year > start_date.year:
                    next_year = end_date.year
                    if emp.date_of_birth.month == 2 and emp.date_of_birth.day == 29:
                        if next_year % 4 == 0 and (next_year % 100 != 0 or next_year % 400 == 0):
                            bday_next = emp.date_of_birth.replace(year=next_year)
                        else:
                            bday_next = emp.date_of_birth.replace(year=next_year, day=28)
                    else:
                        bday_next = emp.date_of_birth.replace(year=next_year)

                    if start_date <= bday_next <= end_date:
                        events.append({
                            'id': f'bday-next-{emp.id}',
                            'title': f'🎂  {emp.full_name}',
                            'start': bday_next.isoformat(),
                            'allDay': True,
                            'className': 'bg-primary-subtle text-primary border-primary',
                        })
            except Exception:
                continue

        # 2. Interviews
        interviews = InterviewSchedule.objects.filter(
            scheduled_date__gte=start_date,
            scheduled_date__lte=end_date
        ).select_related('application')

        for interview in interviews:
            from django.urls import reverse
            url = reverse('employees:candidate_detail', args=[interview.application.id])
            events.append({
                'id': f'interview-{interview.id}',
                'title': f'🤝 {interview.application.candidate_name}',
                'start': f"{interview.scheduled_date.isoformat()}T{interview.scheduled_time.isoformat()}",
                'className': 'bg-info-subtle text-info border-info',
                'url': url,
                'extendedProps': {
                    'type': 'interview',
                    'time': interview.scheduled_time.strftime('%I:%M %p'),
                    'candidate': interview.application.candidate_name
                }
            })

        # 2. Anniversaries (Work Anniversaries)
        employees = Employee.objects.filter(employment_status='active').exclude(joining_date__isnull=True)
        for emp in employees:
            # Create anniversary date for current year
            current_year = start_date.year
            try:
                # Calculate years of service for current year
                years = current_year - emp.anniversary_date.year

                # Only show anniversary if it's a meaningful anniversary (at least 1 year)
                if years >= 1:
                    anniversary = emp.anniversary_date.replace(year=current_year)

                    if start_date <= anniversary <= end_date:
                        events.append({
                            'id': f'anniversary-{emp.id}',
                            'title': f'🎉 {emp.full_name} ({years} years)',
                            'start': anniversary.isoformat(),
                            'allDay': True,
                            'className': 'bg-info-subtle text-info border-info',
                            'extendedProps': {
                                'type': 'anniversary',
                                'employee_id': emp.id,
                                'years': years
                            }
                        })

                    # Also check next year if range spans across years
                    if end_date.year > start_date.year:
                        next_year = end_date.year
                        years_next = next_year - emp.anniversary_date.year

                        if years_next >= 1:
                            anniversary_next = emp.anniversary_date.replace(year=next_year)

                            if start_date <= anniversary_next <= end_date:
                                events.append({
                                    'id': f'anniversary-next-{emp.id}',
                                    'title': f'🎉 {emp.full_name} ({years_next} years)',
                                    'start': anniversary_next.isoformat(),
                                    'allDay': True,
                                    'className': 'bg-info-subtle text-info border-info',
                                    'extendedProps': {
                                        'type': 'anniversary',
                                        'employee_id': emp.id,
                                        'years': years_next
                                    }
                                })
            except Exception:
                continue

        # 3. Leave Applications
        leaves = LeaveApplication.objects.filter(
            start_date__lte=end_date,
            end_date__gte=start_date,
            status='approved'
        ).select_related('employee', 'leave_type')

        for leave in leaves:
            events.append({
                'id': f'leave-{leave.id}',
                'title': f'🌴 {leave.employee.full_name} ({leave.leave_type.name})',
                'start': leave.start_date.isoformat(),
                'end': (leave.end_date + timezone.timedelta(days=1)).isoformat(), # Inclusive end for FullCalendar
                'className': 'bg-warning-subtle text-warning border-warning',
                'extendedProps': {
                    'type': 'leave',
                    'employee': leave.employee.full_name
                }
            })

        # 4. Public Holidays
        holidays = PublicHoliday.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            is_active=True
        )

        for holiday in holidays:
            events.append({
                'id': f'holiday-{holiday.id}',
                'title': f'🚩 {holiday.name}',
                'start': holiday.date.isoformat(),
                'allDay': True,
                'className': 'bg-danger-subtle text-danger border-danger',
                'extendedProps': {
                    'type': 'holiday'
                }
            })

        print(f"Generated {len(events)} events")
        print("Anniversary events:", [e for e in events if 'anniversary' in e.get('id', '')])
        return JsonResponse(events, safe=False)

class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20

    def get_queryset(self):
        queryset = Employee.objects.select_related('department', 'designation').all()

        # Search functionality
        search_term = self.request.GET.get('search', '')
        if search_term:
            queryset = queryset.filter(
                Q(full_name__icontains=search_term) |
                Q(employee_code__icontains=search_term)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = EmployeeSearchForm(self.request.GET)
        context['active_employees_count'] = self.get_queryset().filter(employment_status='active').count()
        context['is_paginated'] = self.get_queryset().count() > self.paginate_by
        return context

class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'employees/employee_detail.html'
    context_object_name = 'employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['emergency_contact'] = self.object.emergency_contact
        context['documents'] = self.object.documents.all()

        # Define document categories for the tracker
        document_categories = {
            'Photographs': [
                {'type': 'passport_photo', 'display': 'Passport Size Photos – 4 Copies'},
            ],
            'Identity Proofs': [
                {'type': 'aadhar_card', 'display': 'Aadhar Card'},
                {'type': 'pan_card', 'display': 'PAN Card'},
                {'type': 'driving_license', 'display': 'Driving License'},
                {'type': 'voter_id', 'display': 'Voter ID'},
                {'type': 'passport', 'display': 'Passport'},
            ],
            'Address Proofs': [
                {'type': 'electricity_bill', 'display': 'Electricity Bill'},
                {'type': 'tax_bill', 'display': 'Tax Bill'},
                {'type': 'rent_agreement', 'display': 'Rent Agreement'},
            ],
            'Education Proofs': [
                {'type': 'ssc_marksheet', 'display': 'SSC Marksheet'},
                {'type': 'hsc_marksheet', 'display': 'HSC Marksheet'},
                {'type': 'graduation_certificate', 'display': 'Graduation Certificate'},
                {'type': 'pg_certificate', 'display': 'Post-Graduation Certificate'},
                {'type': 'graduation_marksheet', 'display': 'Graduation Marksheet'},
                {'type': 'pg_marksheet', 'display': 'Post-Graduation Marksheet'},
            ]
        }

        # Add document status to each category
        documents_dict = {doc.document_type: doc for doc in context['documents']}

        for category, docs in document_categories.items():
            for doc in docs:
                if doc['type'] in documents_dict:
                    existing_doc = documents_dict[doc['type']]
                    doc.update({
                        'id': existing_doc.id,
                        'is_submitted': existing_doc.is_submitted,
                        'submitted_date': existing_doc.submitted_date,
                        'remarks': existing_doc.remarks,
                    })
                else:
                    # Document doesn't exist yet - will be created on first toggle
                    doc.update({
                        'id': None,
                        'is_submitted': False,
                        'submitted_date': None,
                        'remarks': None,
                    })

        context['document_categories'] = document_categories
        return context

class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:employee_list')

    def dispatch(self, request, *args, **kwargs):
        # Only allow superusers and staff to create employees
        if not request.user.is_superuser and not request.user.is_staff:
            messages.error(request, 'You do not have permission to add employees.')
            return redirect('employees:employee_list')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Employee'
        context['emergency_contact_form'] = EmergencyContactForm()
        # Serialize designations to JSON for JavaScript use
        # Serialize designations to JSON for JavaScript use
        all_designations = list(Designation.objects.values('id', 'name', 'department_id'))
        context['all_designations'] = json.dumps(all_designations)

        # Serialize departments to JSON for JavaScript use (Department Head feature)
        all_departments = list(Department.objects.values('id', 'name', 'head__full_name'))
        context['all_departments'] = json.dumps(all_departments)
        return context

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
            employee = self.object

            # Handle emergency contact
            ec_name = form.cleaned_data.get('emergency_contact_name')
            if ec_name:
                ec = EmergencyContact.objects.create(
                    name=ec_name,
                    mobile_number=form.cleaned_data.get('emergency_contact_mobile'),
                    email=form.cleaned_data.get('emergency_contact_email'),
                    address=form.cleaned_data.get('emergency_contact_address') or '',
                    relationship=form.cleaned_data.get('emergency_contact_relationship')
                )
                employee.emergency_contact = ec
                employee.save()

            # Create User for the employee
            username = employee.official_email
            email = employee.official_email
            # Default password
            password = f"Welcome@{timezone.now().year}"

            try:
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(username=username, email=email, password=password)
                    name_parts = employee.full_name.split()
                    user.first_name = name_parts[0]
                    if len(name_parts) > 1:
                        user.last_name = " ".join(name_parts[1:])
                    user.save()

                    # Create UserProfile
                    UserProfile.objects.create(
                        user=user,
                        employee=employee,
                        role='employee',
                        department=employee.department,
                        phone=employee.mobile_number
                    )

                    messages.success(self.request, f'Employee added successfully! ID: {employee.employee_code}. User account created (Pass: {password})')
                else:
                    messages.warning(self.request, f'Employee added (ID: {employee.employee_code}), but user account for {email} already exists.')
            except Exception as e:
                messages.error(self.request, f'Employee added, but error creating user account: {str(e)}')

        return response

class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:employee_list')

    def dispatch(self, request, *args, **kwargs):
        # Only allow superusers and staff to edit employees
        if not request.user.is_superuser and not request.user.is_staff:
            messages.error(request, 'You do not have permission to edit employees.')
            return redirect('employees:employee_list')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Employee'
        context['emergency_contact_form'] = EmergencyContactForm()
        # Serialize designations to JSON for JavaScript use
        # Serialize designations to JSON for JavaScript use
        all_designations = list(Designation.objects.values('id', 'name', 'department_id'))
        context['all_designations'] = json.dumps(all_designations)

        # Serialize departments to JSON for JavaScript use (Department Head feature)
        all_departments = list(Department.objects.values('id', 'name', 'head__full_name'))
        context['all_departments'] = json.dumps(all_departments)
        return context

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
            employee = self.object

            # Handle emergency contact
            ec_name = form.cleaned_data.get('emergency_contact_name')
            if ec_name:
                ec_data = {
                    'name': ec_name,
                    'mobile_number': form.cleaned_data.get('emergency_contact_mobile'),
                    'email': form.cleaned_data.get('emergency_contact_email'),
                    'address': form.cleaned_data.get('emergency_contact_address') or '',
                    'relationship': form.cleaned_data.get('emergency_contact_relationship')
                }
                if employee.emergency_contact:
                    for key, value in ec_data.items():
                        setattr(employee.emergency_contact, key, value)
                    employee.emergency_contact.save()
                else:
                    ec = EmergencyContact.objects.create(**ec_data)
                    employee.emergency_contact = ec
                    employee.save()

            messages.success(self.request, 'Employee updated successfully!')
            return response

class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    model = Employee
    template_name = 'employees/employee_confirm_delete.html'
    success_url = reverse_lazy('employees:employee_list')

    def dispatch(self, request, *args, **kwargs):
        # Only allow superusers and staff to delete employees
        if not request.user.is_superuser and not request.user.is_staff:
            messages.error(request, 'You do not have permission to delete employees.')
            return redirect('employees:employee_list')
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Employee deleted successfully!')
        return super().delete(request, *args, **kwargs)

@require_POST
def toggle_employee_status(request, pk):
    # Only allow superusers and staff to toggle employee status
    if not request.user.is_superuser and not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'You do not have permission to change employee status.'
        }, status=403)

    employee = get_object_or_404(Employee, pk=pk)

    if employee.employment_status == 'active':
        employee.employment_status = 'inactive'
    else:
        employee.employment_status = 'active'

    employee.save()

    return JsonResponse({
        'success': True,
        'message': 'Employee status updated successfully!'
    })

@require_POST
def update_document_status(request, employee_pk, document_type):
    # Only allow superusers and staff to update document status
    if not request.user.is_superuser and not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'You do not have permission to update document status.'
        }, status=403)

    employee = get_object_or_404(Employee, pk=employee_pk)

    # Get or create the document record
    document, created = EmployeeDocument.objects.get_or_create(
        employee=employee,
        document_type=document_type,
        defaults={'is_submitted': False}
    )

    # Update the submission status
    is_submitted = request.POST.get('is_submitted') == 'on'
    document.is_submitted = is_submitted

    if is_submitted and not document.submitted_date:
        document.submitted_date = timezone.now()
    elif not is_submitted:
        document.submitted_date = None

    document.save()

    return JsonResponse({
        'success': True,
        'message': 'Document status updated successfully!'
    })

def get_designations_by_department(request):
    department_id = request.GET.get('department_id')

    if department_id:
        designations = Designation.objects.filter(department_id=department_id).values('id', 'name')
        return JsonResponse(list(designations), safe=False)

    return JsonResponse([], safe=False)

@require_POST
@login_required
def update_document_status_by_id(request, document_id):
    """
    AJAX view to update document submission status by document ID
    """
    try:
        # Parse the request body
        data = json.loads(request.body)
        is_submitted = data.get('is_submitted', False)

        # Get the document
        document = EmployeeDocument.objects.get(id=document_id)

        # Update the document status
        document.is_submitted = is_submitted
        if is_submitted:
            document.submitted_date = timezone.now()
        else:
            document.submitted_date = None

        document.save()

        return JsonResponse({
            'success': True,
            'submitted_date': document.submitted_date.strftime('%b %d, %Y') if document.submitted_date else None
        })

    except EmployeeDocument.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Document not found'
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Device Management Views

class DeviceListView(LoginRequiredMixin, ListView):
    model = Device
    template_name = 'devices/device_list.html'
    context_object_name = 'devices'
    paginate_by = 20

    def get_queryset(self):
        queryset = Device.objects.all()
        search = self.request.GET.get('search')
        device_type = self.request.GET.get('device_type')
        status = self.request.GET.get('status')

        if search:
            queryset = queryset.filter(
                Q(device_name__icontains=search) |
                Q(serial_number__icontains=search)
            )

        if device_type:
            queryset = queryset.filter(device_type=device_type)

        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'device_types': Device.DEVICE_TYPE_CHOICES,
            'status_choices': Device.STATUS_CHOICES,
            'search': self.request.GET.get('search', ''),
            'selected_device_type': self.request.GET.get('device_type', ''),
            'selected_status': self.request.GET.get('status', ''),
        })
        return context

class DeviceCreateView(LoginRequiredMixin, CreateView):
    model = Device
    template_name = 'devices/device_form.html'
    fields = ['device_type', 'device_name', 'serial_number', 'purchase_date', 'warranty_details']
    success_url = reverse_lazy('employees:device_list')

    def dispatch(self, request, *args, **kwargs):
        # Only allow superusers and staff to create devices
        if not request.user.is_superuser and not request.user.is_staff:
            messages.error(request, 'You do not have permission to add devices.')
            return redirect('employees:device_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Device added successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Device'
        context['device_types'] = Device.DEVICE_TYPE_CHOICES
        return context

class DeviceUpdateView(LoginRequiredMixin, UpdateView):
    model = Device
    template_name = 'devices/device_form.html'
    fields = ['device_type', 'device_name', 'serial_number', 'purchase_date', 'warranty_details', 'status']
    success_url = reverse_lazy('employees:device_list')

    def dispatch(self, request, *args, **kwargs):
        # Only allow superusers and staff to edit devices
        if not request.user.is_superuser and not request.user.is_staff:
            messages.error(request, 'You do not have permission to edit devices.')
            return redirect('employees:device_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Device updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Device'
        context['device_types'] = Device.DEVICE_TYPE_CHOICES
        context['status_choices'] = Device.STATUS_CHOICES
        return context

class DeviceDeleteView(LoginRequiredMixin, DeleteView):
    model = Device
    template_name = 'devices/device_confirm_delete.html'
    success_url = reverse_lazy('employees:device_list')

    def dispatch(self, request, *args, **kwargs):
        # Only allow superusers and staff to delete devices
        if not request.user.is_superuser and not request.user.is_staff:
            messages.error(request, 'You do not have permission to delete devices.')
            return redirect('employees:device_list')
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Device deleted successfully!')
        return super().delete(request, *args, **kwargs)

class DeviceVisibilityView(LoginRequiredMixin, ListView):
    model = Device
    template_name = 'devices/device_visibility.html'
    context_object_name = 'devices'

    def get_queryset(self):
        return Device.objects.all().order_by('device_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Statistics
        total_devices = Device.objects.count()
        available_devices = Device.objects.filter(status='available').count()
        in_use_devices = Device.objects.filter(status='in_use').count()

        context.update({
            'total_devices': total_devices,
            'available_devices': available_devices,
            'in_use_devices': in_use_devices,
        })

        return context

def allocate_device(request, pk):
    # Only allow superusers and staff to allocate devices
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'You do not have permission to allocate devices.')
        return redirect('employees:device_visibility')

    device = get_object_or_404(Device, pk=pk)

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        employee = get_object_or_404(Employee, pk=employee_id)

        # Create allocation
        DeviceAllocation.objects.create(
            device=device,
            assigned_to=employee,
            assigned_by=request.user
        )

        messages.success(request, f'Device {device.device_name} allocated to {employee.full_name}')
        return redirect('employees:device_visibility')

    employees = Employee.objects.filter(employment_status='active')
    return render(request, 'devices/allocate_device.html', {
        'device': device,
        'employees': employees,
    })

def return_device(request, pk):
    # Only allow superusers and staff to return devices
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'You do not have permission to return devices.')
        return redirect('employees:device_visibility')

    device = get_object_or_404(Device, pk=pk)
    allocation = device.current_allocation

    if not allocation:
        messages.error(request, 'This device is not currently allocated.')
        return redirect('employees:device_visibility')

    if request.method == 'POST':
        allocation.returned_date = timezone.now()
        allocation.return_notes = request.POST.get('return_notes', '')
        allocation.save()

        messages.success(request, f'Device {device.device_name} returned successfully.')
        return redirect('employees:device_visibility')

    return render(request, 'devices/return_device.html', {
        'device': device,
        'allocation': allocation,
    })

# Leave Management Views

class PublicHolidayListView(LoginRequiredMixin, ListView):
    model = PublicHoliday
    template_name = 'leave/public_holidays.html'
    context_object_name = 'holidays'

    def get_queryset(self):
        queryset = PublicHoliday.objects.filter(is_active=True)
        # Show holidays for previous, current and next years
        queryset = queryset.filter(year__in=[2024, 2025, 2026]).order_by('date')

        # Filter by country if provided in URL
        country = self.kwargs.get('country')
        if country:
            country_code = 'IN' if country.lower() == 'indian' else 'AU' if country.lower() == 'australian' else None
            if country_code:
                queryset = queryset.filter(country=country_code)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all unique years from the queryset for filtering
        context['available_years'] = PublicHoliday.objects.filter(is_active=True).values_list('year', flat=True).distinct().order_by('year')
        context['current_year'] = timezone.now().year

        # Get country filter from URL
        country = self.kwargs.get('country')
        context['selected_country'] = country

        # Separate holidays by country
        context['indian_holidays'] = PublicHoliday.objects.filter(is_active=True, country='IN', year__in=[2024, 2025, 2026]).order_by('date')
        context['australian_holidays'] = PublicHoliday.objects.filter(is_active=True, country='AU', year__in=[2024, 2025, 2026]).order_by('date')

        # Get list of countries that have holidays (for export modal) - ensure unique
        available_countries = PublicHoliday.objects.values('country').distinct().order_by('country')
        context['available_countries'] = [item['country'] for item in available_countries if item['country']]

        return context

class PublicHolidayCreateView(LoginRequiredMixin, CreateView):
    model = PublicHoliday
    form_class = PublicHolidayForm
    template_name = 'leave/public_holiday_form.html'
    success_url = reverse_lazy('employees:public_holidays')

    def dispatch(self, request, *args, **kwargs):
        # Only allow superusers and staff to create holidays
        if not request.user.is_superuser and not request.user.is_staff:
            messages.error(request, 'You do not have permission to add holidays.')
            return redirect('employees:public_holidays')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Holiday added successfully!')
        return super().form_valid(form)

class PublicHolidayUpdateView(LoginRequiredMixin, UpdateView):
    model = PublicHoliday
    form_class = PublicHolidayForm
    template_name = 'leave/public_holiday_form.html'
    success_url = reverse_lazy('employees:public_holidays')

    def dispatch(self, request, *args, **kwargs):
        # Only allow superusers and staff to edit holidays
        if not request.user.is_superuser and not request.user.is_staff:
            messages.error(request, 'You do not have permission to edit holidays.')
            return redirect('employees:public_holidays')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Holiday updated successfully!')
        return super().form_valid(form)

class PublicHolidayDeleteView(LoginRequiredMixin, DeleteView):
    model = PublicHoliday
    template_name = 'leave/public_holiday_confirm_delete.html'
    success_url = reverse_lazy('employees:public_holidays')

    def dispatch(self, request, *args, **kwargs):
        # Only allow superusers and staff to delete holidays
        if not request.user.is_superuser and not request.user.is_staff:
            messages.error(request, 'You do not have permission to delete holidays.')
            return redirect('employees:public_holidays')
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Holiday deleted successfully!')
        return super().delete(request, *args, **kwargs)

@require_POST
@login_required
def bulk_delete_public_holidays(request):
    """
    Bulk delete public holidays
    """
    # Only allow superusers and staff to delete holidays
    if not request.user.is_superuser and not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'You do not have permission to delete holidays.'
        }, status=403)

    try:
        # Parse JSON data
        data = json.loads(request.body)
        holiday_ids = data.get('holiday_ids', [])

        if not holiday_ids:
            return JsonResponse({
                'success': False,
                'error': 'No holidays selected for deletion.'
            }, status=400)

        # Convert to integers and validate
        try:
            holiday_ids = [int(id) for id in holiday_ids]
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'Invalid holiday IDs provided.'
            }, status=400)

        if not holiday_ids:
            return JsonResponse({
                'success': False,
                'error': 'Invalid holiday IDs provided.'
            }, status=400)

        # Perform bulk delete
        deleted_count, _ = PublicHoliday.objects.filter(id__in=holiday_ids).delete()

        if deleted_count > 0:
            return JsonResponse({
                'success': True,
                'message': f'Successfully deleted {deleted_count} holiday(s).'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No holidays were deleted. They may have already been deleted.'
            }, status=404)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid request format.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }, status=500)

class LeaveTypeListView(LoginRequiredMixin, ListView):
    model = LeaveType
    template_name = 'leave/leave_types.html'
    context_object_name = 'leave_types'
    paginate_by = 20

    def get_queryset(self):
        return LeaveType.objects.filter(is_active=True)

class LeaveApplicationListView(LoginRequiredMixin, ListView):
    model = LeaveApplication
    template_name = 'leave/leave_applications.html'
    context_object_name = 'leave_applications'
    paginate_by = 20

    def get_queryset(self):
        if self.request.user.is_superuser:
            return LeaveApplication.objects.all()
        else:
            # Check if user has an employee profile
            try:
                user_profile = self.request.user.profile
                if user_profile.employee:
                    return LeaveApplication.objects.filter(employee=user_profile.employee)
                else:
                    # Try to find employee by matching email
                    from employees.models import Employee
                    employee = Employee.objects.filter(official_email=self.request.user.email).first()
                    if employee:
                        # Link the employee to the user profile
                        user_profile.employee = employee
                        user_profile.save()
                        return LeaveApplication.objects.filter(employee=employee)
                    else:
                        return LeaveApplication.objects.none()
            except AttributeError:
                # User doesn't have employee profile, return empty queryset
                return LeaveApplication.objects.none()

class LeaveApplicationDetailView(LoginRequiredMixin, DetailView):
    model = LeaveApplication
    template_name = 'leave/leave_application_detail.html'
    context_object_name = 'leave'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return LeaveApplication.objects.all()
        else:
            # Check if user has an employee profile
            try:
                user_profile = self.request.user.profile
                if user_profile.employee:
                    return LeaveApplication.objects.filter(employee=user_profile.employee)
                else:
                    return LeaveApplication.objects.none()
            except AttributeError:
                return LeaveApplication.objects.none()

class LeaveApplicationCreateView(LoginRequiredMixin, CreateView):
    model = LeaveApplication
    form_class = LeaveApplicationForm
    template_name = 'leave/leave_application_form.html'
    success_url = reverse_lazy('employees:leave_application_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass employee to form
        try:
            user_profile = self.request.user.profile
            if user_profile.employee:
                kwargs['employee'] = user_profile.employee
        except AttributeError:
            pass
        return kwargs

    def form_valid(self, form):
        from .leave_service import LeaveManagementService, PaidAbsenceService
        from decimal import Decimal
        from datetime import timedelta

        # Check if user has an employee profile and employee record
        try:
            user_profile = self.request.user.profile
            if not user_profile.employee:
                # Try to find employee by matching email
                from employees.models import Employee
                employee = Employee.objects.filter(official_email=self.request.user.email).first()
                if employee:
                    user_profile.employee = employee
                    user_profile.save()
                    form.instance.employee = employee
                else:
                    raise AttributeError("No employee found for this user")
            else:
                form.instance.employee = user_profile.employee
        except AttributeError:
            # User doesn't have employee profile or employee record, show error message
            messages.error(self.request, 'You need to have an employee profile to apply for leave.')
            return self.form_invalid(form)

        employee = form.instance.employee
        leave_type = form.cleaned_data['leave_type']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']




        # Check if there's already a rejected leave application for overlapping dates
        rejected_leaves = LeaveApplication.objects.filter(
            employee=employee,
            status='rejected',
            start_date__lte=end_date,
            end_date__gte=start_date
        )

        if rejected_leaves.exists():
            # Found rejected leave(s) for overlapping dates
            rejected_leave = rejected_leaves.first()
            messages.error(
                self.request,
                f'❌ Cannot apply leave for these dates. You have a rejected leave application from {rejected_leave.start_date.strftime("%d %b %Y")} to {rejected_leave.end_date.strftime("%d %b %Y")}. Please contact HR or select different dates.'
            )
            return self.form_invalid(form)

        # Prepare leave request data
        leave_request = {
            'leave_type_code': leave_type.leave_type,
            'start_date': start_date,
            'end_date': end_date,
            'is_half_day': form.cleaned_data.get('is_half_day', False),
            'scheduled_hours': form.cleaned_data.get('scheduled_hours', Decimal('8.0')),
            'is_wfh': form.cleaned_data.get('is_wfh', False),
            'is_office': form.cleaned_data.get('is_office', False),
            'reason': form.cleaned_data['reason'],
        }

        # Check if this is a paid absence type
        paid_absence_types = [
            PaidAbsenceService.MARRIAGE_LEAVE,
            PaidAbsenceService.PATERNITY_LEAVE,
            PaidAbsenceService.MATERNITY_LEAVE
        ]

        if leave_type.leave_type in paid_absence_types:
            # Process as paid absence - get is_first_child from form
            is_first_child = form.cleaned_data.get('is_first_child', True)
            result = PaidAbsenceService.process_paid_absence_request(
                employee, leave_type.leave_type, is_first_child
            )
        else:
            # Process as regular leave
            result = LeaveManagementService.process_leave_request(employee, leave_request)

        if not result.is_valid:
            # Validation failed
            messages.error(self.request, result.message)
            return self.form_invalid(form)

        # Validation passed - save the leave application
        form.instance.total_days = result.deduction_days

        # Set sandwich leave flag and actual working days from result
        if hasattr(result, 'is_sandwich'):
            form.instance.is_sandwich_leave = result.is_sandwich
        if hasattr(result, 'actual_working_days') and result.actual_working_days > 0:
            form.instance.actual_working_days = result.actual_working_days

        messages.success(
            self.request,
            f'✓ Leave application submitted successfully! {result.message} Days to be deducted: {result.deduction_days}'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['leave_types'] = LeaveType.objects.filter(is_active=True)

        # Get employee leave balances
        try:
            user_profile = self.request.user.profile
            if user_profile.employee:
                from .leave_service import LeaveManagementService
                employee = user_profile.employee

                context['leave_balances'] = {
                    'casual': LeaveManagementService.get_leave_balance(employee, 'casual'),
                    'emergency': LeaveManagementService.get_leave_balance(employee, 'emergency'),
                    'birthday': LeaveManagementService.get_leave_balance(employee, 'birthday'),
                    'marriage_anniversary': LeaveManagementService.get_leave_balance(employee, 'marriage_anniversary'),
                }

                # Get casual leave accrual details
                context['casual_leave_info'] = LeaveManagementService.get_casual_leave_accrual_info(employee)

                context['employee_type'] = LeaveManagementService.identify_employee_type(employee)
            else:
                # Try to find employee by matching email
                from employees.models import Employee
                employee = Employee.objects.filter(official_email=self.request.user.email).first()
                if employee:
                    # Link the employee to the user profile
                    user_profile.employee = employee
                    user_profile.save()

                    from .leave_service import LeaveManagementService
                    context['leave_balances'] = {
                        'casual': LeaveManagementService.get_leave_balance(employee, 'casual'),
                        'emergency': LeaveManagementService.get_leave_balance(employee, 'emergency'),
                        'birthday': LeaveManagementService.get_leave_balance(employee, 'birthday'),
                        'marriage_anniversary': LeaveManagementService.get_leave_balance(employee, 'marriage_anniversary'),
                    }

                    # Get casual leave accrual details
                    context['casual_leave_info'] = LeaveManagementService.get_casual_leave_accrual_info(employee)

                    context['employee_type'] = LeaveManagementService.identify_employee_type(employee)
        except AttributeError as e:
            # User doesn't have employee profile
            context['leave_balances'] = None
            context['casual_leave_info'] = None
            context['employee_type'] = None

        return context

def approve_leave(request, pk):
    leave = get_object_or_404(LeaveApplication, pk=pk)

    if request.method == 'POST':
        leave.status = 'approved'
        leave.approved_by = request.user
        leave.approved_date = timezone.now()
        leave.save()

        # Show success message
        messages.success(
            request,
            f'✓ Leave application for {leave.employee.full_name} has been approved! '
            f'({leave.start_date.strftime("%d %b %Y")} to {leave.end_date.strftime("%d %b %Y")})'
        )

        # Create notification for the employee
        try:
            from .models import Notification
            employee_user = leave.employee.user_profile.user
            notification = Notification.objects.create(
                title='Leave Approved ✓',
                message=f'Your leave application from {leave.start_date.strftime("%d %b %Y")} to {leave.end_date.strftime("%d %b %Y")} has been approved by {request.user.get_full_name() or request.user.username}.',
                notification_type='success',
                icon='bi-check-circle',
                created_by=request.user,
                target_all=False
            )
            notification.target_users.add(employee_user)
        except Exception as e:
            pass  # If notification fails, don't break the approval

        return redirect('employees:leave_application_list')

    return render(request, 'leave/approve_leave.html', {'leave': leave})

def reject_leave(request, pk):
    leave = get_object_or_404(LeaveApplication, pk=pk)

    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', 'No reason provided')
        leave.status = 'rejected'
        leave.rejection_reason = rejection_reason
        leave.save()

        # Show warning/error message for rejection
        messages.warning(
            request,
            f'✗ Leave application for {leave.employee.full_name} has been rejected. '
            f'({leave.start_date.strftime("%d %b %Y")} to {leave.end_date.strftime("%d %b %Y")})'
        )

        # Create notification for the employee
        try:
            from .models import Notification
            employee_user = leave.employee.user_profile.user
            notification = Notification.objects.create(
                title='Leave Rejected ✗',
                message=f'Your leave application from {leave.start_date.strftime("%d %b %Y")} to {leave.end_date.strftime("%d %b %Y")} has been rejected. Reason: {rejection_reason}',
                notification_type='danger',
                icon='bi-x-circle',
                created_by=request.user,
                target_all=False
            )
            notification.target_users.add(employee_user)
        except Exception as e:
            pass  # If notification fails, don't break the rejection

        return redirect('employees:leave_application_list')

    return render(request, 'leave/reject_leave.html', {'leave': leave})

# Leave Type Management Views

class LeaveTypeCreateView(LoginRequiredMixin, CreateView):
    model = LeaveType
    form_class = LeaveTypeForm
    template_name = 'leave/leave_type_form.html'
    success_url = reverse_lazy('employees:leave_types')

    def dispatch(self, request, *args, **kwargs):
        # Only allow superusers and staff to create leave types
        if not request.user.is_superuser and not request.user.is_staff:
            messages.error(request, 'You do not have permission to add leave types.')
            return redirect('employees:leave_types')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Leave type added successfully!')
        return super().form_valid(form)

class LeaveTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = LeaveType
    form_class = LeaveTypeForm
    template_name = 'leave/leave_type_form.html'
    success_url = reverse_lazy('employees:leave_types')

    def dispatch(self, request, *args, **kwargs):
        # Only allow superusers and staff to edit leave types
        if not request.user.is_superuser and not request.user.is_staff:
            messages.error(request, 'You do not have permission to edit leave types.')
            return redirect('employees:leave_types')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Leave type updated successfully!')
        return super().form_valid(form)

class LeaveTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = LeaveType
    template_name = 'leave/leave_type_confirm_delete.html'
    success_url = reverse_lazy('employees:leave_types')

    def dispatch(self, request, *args, **kwargs):
        # Only allow superusers and staff to delete leave types
        if not request.user.is_superuser and not request.user.is_staff:
            messages.error(request, 'You do not have permission to delete leave types.')
            return redirect('employees:leave_types')
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Leave type deleted successfully!')
        return super().delete(request, *args, **kwargs)

class LeaveTypeDetailView(LoginRequiredMixin, DetailView):
    model = LeaveType
    template_name = 'leave/leave_type_detail.html'
    context_object_name = 'leave_type'

@method_decorator(csrf_exempt, name='dispatch')
class DesignationAPIView(LoginRequiredMixin, View):
    def get(self, request):
        department_id = request.GET.get('department_id')

        try:
            if department_id:
                # Filter by department
                designations = Designation.objects.filter(department_id=department_id)
            else:
                # Return all designations
                designations = Designation.objects.all()

            data = [
                {
                    'id': desig.id,
                    'name': desig.name,
                    'description': desig.description
                }
                for desig in designations
            ]
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
