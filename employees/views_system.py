from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import SystemDetail, MacAddress, SystemRequirement, Employee
from .forms_system import SystemDetailForm, MacAddressForm, SystemRequirementForm
from .decorators import admin_required, it_admin_required
from django.utils.decorators import method_decorator
from django.db.models import Q, Count


# SystemDetail Views

@method_decorator([login_required, it_admin_required], name='dispatch')
class SystemDetailListView(LoginRequiredMixin, ListView):
    model = SystemDetail
    template_name = 'system/system_detail_list.html'
    context_object_name = 'systems'
    paginate_by = 20

    def get_queryset(self):
        queryset = SystemDetail.objects.select_related('employee', 'employee__department', 'department', 'allocated_by').all()
        
        # Search functionality
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(employee__full_name__icontains=search) |
                Q(employee__employee_code__icontains=search) |
                Q(cpu_company_name__icontains=search) |
                Q(cpu_label_no__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'returned':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'System Details'
        context['total_systems'] = SystemDetail.objects.count()
        context['active_systems'] = SystemDetail.objects.filter(is_active=True).count()
        context['search'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', '')
        return context


@method_decorator([login_required, it_admin_required], name='dispatch')
class SystemDetailCreateView(LoginRequiredMixin, CreateView):
    model = SystemDetail
    form_class = SystemDetailForm
    template_name = 'system/system_detail_form.html'
    success_url = reverse_lazy('employees:system_detail_list')

    def form_valid(self, form):
        form.instance.allocated_by = self.request.user
        # Auto-populate department from employee
        if form.instance.employee:
            form.instance.department = form.instance.employee.department
        messages.success(self.request, 'System details added successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add System Details'
        context['button_text'] = 'Add System'
        return context


@method_decorator([login_required, it_admin_required], name='dispatch')
class SystemDetailUpdateView(LoginRequiredMixin, UpdateView):
    model = SystemDetail
    form_class = SystemDetailForm
    template_name = 'system/system_detail_form.html'
    success_url = reverse_lazy('employees:system_detail_list')

    def form_valid(self, form):
        # Auto-populate department from employee
        if form.instance.employee:
            form.instance.department = form.instance.employee.department
        messages.success(self.request, 'System details updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit System Details'
        context['button_text'] = 'Update System'
        return context


@method_decorator([login_required, it_admin_required], name='dispatch')
class SystemDetailDeleteView(LoginRequiredMixin, DeleteView):
    model = SystemDetail
    template_name = 'system/system_detail_confirm_delete.html'
    success_url = reverse_lazy('employees:system_detail_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'System details deleted successfully.')
        return super().delete(request, *args, **kwargs)


# MacAddress Views

@method_decorator([login_required, it_admin_required], name='dispatch')
class MacAddressListView(LoginRequiredMixin, ListView):
    model = MacAddress
    template_name = 'system/mac_address_list.html'
    context_object_name = 'mac_addresses'
    paginate_by = 20

    def get_queryset(self):
        queryset = MacAddress.objects.select_related('employee').all()
        
        # Search functionality
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(mac_address__icontains=search) |
                Q(employee__full_name__icontains=search) |
                Q(employee__employee_code__icontains=search)
            )
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'MAC Address Management'
        context['total_macs'] = MacAddress.objects.count()
        context['active_macs'] = MacAddress.objects.count()  # All are active now
        context['search'] = self.request.GET.get('search', '')
        return context


@method_decorator([login_required, it_admin_required], name='dispatch')
class MacAddressCreateView(LoginRequiredMixin, CreateView):
    model = MacAddress
    form_class = MacAddressForm
    template_name = 'system/mac_address_form.html'
    success_url = reverse_lazy('employees:mac_address_list')

    def form_valid(self, form):
        messages.success(self.request, 'MAC address added successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add MAC Address'
        context['button_text'] = 'Add MAC Address'
        return context


@method_decorator([login_required, it_admin_required], name='dispatch')
class MacAddressUpdateView(LoginRequiredMixin, UpdateView):
    model = MacAddress
    form_class = MacAddressForm
    template_name = 'system/mac_address_form.html'
    success_url = reverse_lazy('employees:mac_address_list')

    def form_valid(self, form):
        messages.success(self.request, 'MAC address updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit MAC Address'
        context['button_text'] = 'Update MAC Address'
        return context


@method_decorator([login_required, it_admin_required], name='dispatch')
class MacAddressDeleteView(LoginRequiredMixin, DeleteView):
    model = MacAddress
    template_name = 'system/mac_address_confirm_delete.html'
    success_url = reverse_lazy('employees:mac_address_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'MAC address deleted successfully.')
        return super().delete(request, *args, **kwargs)


# SystemRequirement Views

@method_decorator([login_required], name='dispatch')
class SystemRequirementListView(LoginRequiredMixin, ListView):
    model = SystemRequirement
    template_name = 'system/system_requirement_list.html'
    context_object_name = 'requirements'
    paginate_by = 20

    def get_queryset(self):
        queryset = SystemRequirement.objects.select_related('requested_by', 'requested_for', 'approved_by').all()
        
        # Search functionality
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(requested_by__full_name__icontains=search) |
                Q(requirement_types__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by priority
        priority = self.request.GET.get('priority', '')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'System Requirements'
        context['total_requirements'] = SystemRequirement.objects.count()
        context['pending_requirements'] = SystemRequirement.objects.filter(status='pending').count()
        context['approved_requirements'] = SystemRequirement.objects.filter(status='approved').count()
        context['search'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', '')
        context['priority'] = self.request.GET.get('priority', '')
        return context


@method_decorator([login_required], name='dispatch')
class SystemRequirementCreateView(LoginRequiredMixin, CreateView):
    model = SystemRequirement
    form_class = SystemRequirementForm
    template_name = 'system/system_requirement_form.html'
    success_url = reverse_lazy('employees:system_requirement_list')

    def form_valid(self, form):
        messages.success(self.request, 'System requirement submitted successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add System Requirement'
        context['button_text'] = 'Submit Requirement'
        return context


@method_decorator([login_required, it_admin_required], name='dispatch')
class SystemRequirementUpdateView(LoginRequiredMixin, UpdateView):
    model = SystemRequirement
    form_class = SystemRequirementForm
    template_name = 'system/system_requirement_form.html'
    success_url = reverse_lazy('employees:system_requirement_list')

    def form_valid(self, form):
        messages.success(self.request, 'System requirement updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit System Requirement'
        context['button_text'] = 'Update Requirement'
        return context


@method_decorator([login_required, it_admin_required], name='dispatch')
class SystemRequirementDeleteView(LoginRequiredMixin, DeleteView):
    model = SystemRequirement
    template_name = 'system/system_requirement_confirm_delete.html'
    success_url = reverse_lazy('employees:system_requirement_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'System requirement deleted successfully.')
        return super().delete(request, *args, **kwargs)


# Additional Actions

@login_required
@it_admin_required
def approve_system_requirement(request, pk):
    """Approve a system requirement"""
    requirement = get_object_or_404(SystemRequirement, pk=pk)
    
    if requirement.status == 'pending':
        requirement.status = 'approved'
        requirement.approved_by = request.user
        from django.utils import timezone
        requirement.approved_date = timezone.now()
        requirement.save()
        messages.success(request, f'Requirement approved successfully.')
    else:
        messages.warning(request, 'Only pending requirements can be approved.')
    
    return redirect('employees:system_requirement_list')


@login_required
@it_admin_required
def reject_system_requirement(request, pk):
    """Reject a system requirement"""
    requirement = get_object_or_404(SystemRequirement, pk=pk)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        if rejection_reason:
            requirement.status = 'rejected'
            requirement.rejection_reason = rejection_reason
            requirement.save()
            messages.success(request, 'Requirement rejected.')
            return redirect('employees:system_requirement_list')
        else:
            messages.error(request, 'Rejection reason is required.')
    
    return render(request, 'system/reject_requirement.html', {'requirement': requirement})
