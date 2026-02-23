"""
Abstracted CRUD views using the new base classes and mixins
This demonstrates how to use the abstractions for easy CRUD operations
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .base_views import (
    BaseListView, BaseCreateView, BaseUpdateView, 
    BaseDetailView, BaseDeleteView, BaseBulkOperationView,
    BaseExportView, BaseToggleStatusView
)
from .models import Department, Designation, UserProfile, Employee
from .mixins import StaffRequiredMixin, AdminRequiredMixin
from django.contrib.auth.models import User


# Department Views
class DepartmentListView(BaseListView):
    """List view for departments"""
    model = Department
    template_name = 'employees/department_list.html'
    context_object_name = 'departments'
    paginate_by = 15
    
    def get_queryset(self):
        return Department.objects.select_related('head').all()


class DepartmentCreateView(StaffRequiredMixin, BaseCreateView):
    """Create view for departments"""
    model = Department
    template_name = 'employees/department_form.html'
    fields = ['name', 'description', 'head']
    success_url = reverse_lazy('employees:department_list')


class DepartmentUpdateView(StaffRequiredMixin, BaseUpdateView):
    """Update view for departments"""
    model = Department
    template_name = 'employees/department_form.html'
    fields = ['name', 'description', 'head']
    success_url = reverse_lazy('employees:department_list')


class DepartmentDeleteView(StaffRequiredMixin, BaseDeleteView):
    """Delete view for departments"""
    model = Department
    success_url = reverse_lazy('employees:department_list')


class DepartmentBulkOperationView(StaffRequiredMixin, BaseBulkOperationView):
    """Bulk operations for departments"""
    model = Department
    success_url = reverse_lazy('employees:department_list')


class DepartmentExportView(BaseExportView):
    """Export view for departments"""
    model = Department
    
    def get_export_headers(self):
        return ['Name', 'Description', 'Head', 'Created At', 'Updated At']
    
    def get_export_row(self, obj, headers):
        return [
            obj.name,
            obj.description or "",
            obj.head.get_full_name() if obj.head else "",
            obj.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            obj.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        ]


# Designation Views
class DesignationListView(BaseListView):
    """List view for designations"""
    model = Designation
    template_name = 'employees/designation_list.html'
    context_object_name = 'designations'
    paginate_by = 15
    
    def get_queryset(self):
        return Designation.objects.select_related('department', 'department__head').all()


class DesignationCreateView(StaffRequiredMixin, BaseCreateView):
    """Create view for designations"""
    model = Designation
    template_name = 'employees/designation_form.html'
    fields = ['name', 'description', 'department']
    success_url = reverse_lazy('employees:designation_list')


class DesignationUpdateView(StaffRequiredMixin, BaseUpdateView):
    """Update view for designations"""
    model = Designation
    template_name = 'employees/designation_form.html'
    fields = ['name', 'description', 'department']
    success_url = reverse_lazy('employees:designation_list')


class DesignationDeleteView(StaffRequiredMixin, BaseDeleteView):
    """Delete view for designations"""
    model = Designation
    success_url = reverse_lazy('employees:designation_list')


# User Views (Enhanced)
class AbstractedUserListView(BaseListView):
    """Enhanced list view for users using abstractions"""
    model = User
    template_name = 'employees/user_list_abstracted.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '').strip()
        role_filter = self.request.GET.get('role', '')
        department_filter = self.request.GET.get('department', '')

        if search_query:
            queryset = queryset.filter(
                username__icontains=search_query |
                email__icontains=search_query |
                first_name__icontains=search_query |
                last_name__icontains=search_query
            )

        if role_filter:
            queryset = queryset.filter(profile__role=role_filter)

        if department_filter:
            queryset = queryset.filter(profile__department__id=department_filter)

        return queryset.select_related('profile', 'profile__department').order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = self.get_queryset().count()
        context['active_users'] = self.get_queryset().filter(is_active=True).count()
        context['role_choices'] = UserProfile.ROLE_CHOICES
        context['departments'] = Department.objects.all()
        return context


class AbstractedUserCreateView(StaffRequiredMixin, BaseCreateView):
    """Enhanced create view for users using abstractions"""
    model = User
    template_name = 'employees/user_form_abstracted.html'
    fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    success_url = reverse_lazy('employees:user_list_abstracted')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role_choices'] = UserProfile.ROLE_CHOICES
        context['departments'] = Department.objects.all()
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Create user profile
        UserProfile.objects.create(
            user=self.object,
            role=self.request.POST.get('role', 'employee'),
            department_id=self.request.POST.get('department')
        )
        return response


class AbstractedUserUpdateView(StaffRequiredMixin, BaseUpdateView):
    """Enhanced update view for users using abstractions"""
    model = User
    template_name = 'employees/user_form_abstracted.html'
    fields = ['username', 'email', 'first_name', 'last_name']
    success_url = reverse_lazy('employees:user_list_abstracted')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role_choices'] = UserProfile.ROLE_CHOICES
        context['departments'] = Department.objects.all()
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Update user profile
        profile, created = UserProfile.objects.get_or_create(user=self.object)
        profile.role = self.request.POST.get('role', 'employee')
        profile.department_id = self.request.POST.get('department')
        profile.save()
        return response


class AbstractedUserDeleteView(BaseDeleteView):
    """Enhanced delete view for users using abstractions"""
    model = User
    success_url = reverse_lazy('employees:user_list_abstracted')


class AbstractedUserToggleStatusView(BaseToggleStatusView):
    """Toggle user status using abstractions"""
    model = User
    success_url = reverse_lazy('employees:user_list_abstracted')


class UserBulkOperationView(BaseBulkOperationView):
    """Bulk operations for users"""
    model = User
    success_url = reverse_lazy('employees:user_list_abstracted')


class UserExportView(BaseExportView):
    """Export view for users"""
    model = User
    
    def get_export_queryset(self):
        queryset = super().get_export_queryset()
        role_filter = self.request.GET.get('role', '')
        department_filter = self.request.GET.get('department', '')
        
        if role_filter:
            queryset = queryset.filter(profile__role=role_filter)
        if department_filter:
            queryset = queryset.filter(profile__department__id=department_filter)
            
        return queryset.select_related('profile', 'profile__department')
    
    def get_export_headers(self):
        return [
            'Username', 'Email', 'First Name', 'Last Name', 
            'Role', 'Department', 'Phone', 'Is Active', 
            'Date Joined', 'Last Login'
        ]
    
    def get_export_row(self, obj, headers):
        return [
            obj.username,
            obj.email,
            obj.first_name,
            obj.last_name,
            obj.profile.get_role_display() if obj.profile else "",
            obj.profile.department.name if obj.profile and obj.profile.department else "",
            obj.profile.phone if obj.profile else "",
            "Yes" if obj.is_active else "No",
            obj.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
            obj.last_login.strftime("%Y-%m-%d %H:%M:%S") if obj.last_login else "Never"
        ]


# Employee Views (Enhanced)
class EmployeeListView(BaseListView):
    """Enhanced list view for employees"""
    model = Employee
    template_name = 'employees/employee_list_enhanced.html'
    context_object_name = 'employees'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Employee.objects.select_related(
            'user', 'department', 'designation'
        ).all()
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                employee_code__icontains=search_query |
                first_name__icontains=search_query |
                last_name__icontains=search_query |
                email__icontains=search_query |
                phone__icontains=search_query |
                department__name__icontains=search_query |
                designation__name__icontains=search_query
            )
        
        return queryset.order_by('-created_at')


class EmployeeCreateView(StaffRequiredMixin, BaseCreateView):
    """Enhanced create view for employees"""
    model = Employee
    template_name = 'employees/employee_form_enhanced.html'
    fields = [
        'employee_code', 'first_name', 'last_name', 'email', 'phone',
        'date_of_birth', 'gender', 'address', 'department', 'designation'
    ]
    success_url = reverse_lazy('employees:employee_list_enhanced')


class EmployeeUpdateView(StaffRequiredMixin, BaseUpdateView):
    """Enhanced update view for employees"""
    model = Employee
    template_name = 'employees/employee_form_enhanced.html'
    fields = [
        'employee_code', 'first_name', 'last_name', 'email', 'phone',
        'date_of_birth', 'gender', 'address', 'department', 'designation'
    ]
    success_url = reverse_lazy('employees:employee_list_enhanced')


# Utility Views
class DashboardView(LoginRequiredMixin):
    """Enhanced dashboard view with statistics"""
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            return self.staff_dashboard(request)
        else:
            return self.employee_dashboard(request)
    
    def staff_dashboard(self, request):
        """Dashboard for staff users"""
        from django.shortcuts import render
        
        context = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'total_departments': Department.objects.count(),
            'total_designations': Designation.objects.count(),
            'total_employees': Employee.objects.count(),
            'recent_users': User.objects.order_by('-date_joined')[:5],
            'users_by_role': self.get_users_by_role_stats(),
            'employees_by_department': self.get_employees_by_department_stats(),
        }
        return render(request, 'employees/dashboard_staff.html', context)
    
    def employee_dashboard(self, request):
        """Dashboard for regular employees"""
        from django.shortcuts import render
        
        context = {
            'user_profile': request.user.profile,
            'department': request.user.profile.department,
            'recent_activities': [],  # TODO: Add activity logging
        }
        return render(request, 'employees/dashboard_employee.html', context)
    
    def get_users_by_role_stats(self):
        """Get user statistics by role"""
        stats = {}
        for role, _ in UserProfile.ROLE_CHOICES:
            count = UserProfile.objects.filter(role=role).count()
            stats[role] = count
        return stats
    
    def get_employees_by_department_stats(self):
        """Get employee statistics by department"""
        stats = {}
        for dept in Department.objects.all():
            count = Employee.objects.filter(department=dept).count()
            stats[dept.name] = count
        return stats
