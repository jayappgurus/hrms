from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
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
from .forms import EmployeeForm, EmergencyContactForm, EmployeeSearchForm, EmployeeDocumentForm, LeaveTypeForm, LeaveApplicationForm, PublicHolidayForm


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
                        'title': f'🎂 Birthday: {emp.full_name}',
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
                            'title': f'🎂 Birthday: {emp.full_name}',
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


class EmployeeGridView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'employees/employee_grid.html'
    context_object_name = 'employees'
    paginate_by = 12

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
        context['total_employees'] = Employee.objects.count()
        context['departments'] = Department.objects.all()
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
            'photographs': [
                {'type': 'passport_photo', 'display': 'Passport Size Photos – 4 Copies'},
            ],
            'identity_proofs': [
                {'type': 'aadhar_card', 'display': 'Aadhar Card'},
                {'type': 'pan_card', 'display': 'PAN Card'},
                {'type': 'driving_license', 'display': 'Driving License'},
                {'type': 'voter_id', 'display': 'Voter ID'},
                {'type': 'passport', 'display': 'Passport'},
            ],
            'address_proofs': [
                {'type': 'electricity_bill', 'display': 'Electricity Bill'},
                {'type': 'tax_bill', 'display': 'Tax Bill'},
                {'type': 'rent_agreement', 'display': 'Rent Agreement'},
            ],
            'education_proofs': [
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
                    doc.update({
                        'is_submitted': documents_dict[doc['type']].is_submitted,
                        'submitted_date': documents_dict[doc['type']].submitted_date,
                        'remarks': documents_dict[doc['type']].remarks,
                    })
                else:
                    doc.update({
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
        all_designations = list(Designation.objects.values('id', 'name', 'department_id'))
        context['all_designations'] = json.dumps(all_designations)
        return context

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
            employee = self.object
            
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
        all_designations = list(Designation.objects.values('id', 'name', 'department_id'))
        context['all_designations'] = json.dumps(all_designations)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
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
        maintenance_devices = Device.objects.filter(status='maintenance').count()
        
        context.update({
            'total_devices': total_devices,
            'available_devices': available_devices,
            'in_use_devices': in_use_devices,
            'maintenance_devices': maintenance_devices,
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
    paginate_by = 20

    def get_queryset(self):
        queryset = PublicHoliday.objects.filter(is_active=True)
        year = timezone.now().year
        return queryset.filter(year=year)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_year'] = timezone.now().year
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


class LeaveApplicationCreateView(LoginRequiredMixin, CreateView):
    model = LeaveApplication
    template_name = 'leave/leave_application_form.html'
    fields = ['leave_type', 'start_date', 'end_date', 'total_days', 'reason']
    success_url = reverse_lazy('employees:leave_application_list')

    def form_valid(self, form):
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
        else:
            messages.success(self.request, 'Leave application submitted successfully!')
            return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['leave_types'] = LeaveType.objects.filter(is_active=True)
        return context


def approve_leave(request, pk):
    leave = get_object_or_404(LeaveApplication, pk=pk)
    
    if request.method == 'POST':
        leave.status = 'approved'
        leave.approved_by = request.user
        leave.approved_date = timezone.now()
        leave.save()
        
        messages.success(request, f'Leave application for {leave.employee.full_name} approved successfully!')
        return redirect('employees:leave_application_list')
    
    return render(request, 'leave/approve_leave.html', {'leave': leave})


def reject_leave(request, pk):
    leave = get_object_or_404(LeaveApplication, pk=pk)
    
    if request.method == 'POST':
        leave.status = 'rejected'
        leave.rejection_reason = request.POST.get('rejection_reason', '')
        leave.save()
        
        messages.success(request, f'Leave application for {leave.employee.full_name} rejected!')
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
