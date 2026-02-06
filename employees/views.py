from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.utils import timezone
from .models import Employee, Department, Designation, EmergencyContact, EmployeeDocument
from .forms import EmployeeForm, EmergencyContactForm, EmployeeSearchForm, EmployeeDocumentForm


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
        })
        
        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Employee'
        context['emergency_contact_form'] = EmergencyContactForm()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Employee added successfully!')
        return response


class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:employee_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Employee'
        context['emergency_contact_form'] = EmergencyContactForm()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Employee updated successfully!')
        return response


@require_POST
def toggle_employee_status(request, pk):
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
