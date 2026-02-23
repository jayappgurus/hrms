"""
Complete User CRUD Operations Example
This file demonstrates how to use the abstracted views for user management
"""

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.db import transaction

# Import abstracted views
from .base_views import (
    BaseListView, BaseCreateView, BaseUpdateView, 
    BaseDeleteView, BaseBulkOperationView, BaseToggleStatusView
)
from .mixins import StaffRequiredMixin, AdminRequiredMixin
from .models import UserProfile, Department
from .decorators import admin_required
from django import forms


# Forms
class UserCreateForm(UserCreationForm):
    """Enhanced user creation form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=True)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-select'})
        self.fields['department'].widget.attrs.update({'class': 'form-select'})
        self.fields['phone'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                department=self.cleaned_data['department'],
                phone=self.cleaned_data['phone']
            )
        return user


class UserUpdateForm(forms.ModelForm):
    """Enhanced user update form"""
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=True)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get user profile if exists
        if hasattr(self.instance, 'profile'):
            profile = self.instance.profile
            self.fields['role'].initial = profile.role
            self.fields['department'].initial = profile.department
            self.fields['phone'].initial = profile.phone

        # Add CSS classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['role'].widget.attrs.update({'class': 'form-select'})
        self.fields['department'].widget.attrs.update({'class': 'form-select'})

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Update user profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data['role']
            profile.department = self.cleaned_data['department']
            profile.phone = self.cleaned_data['phone']
            profile.save()
        return user


# Views for User CRUD Operations

class UserListView(BaseListView):
    """List all users with search and filtering"""
    model = User
    template_name = 'employees/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '').strip()
        role_filter = self.request.GET.get('role', '')
        department_filter = self.request.GET.get('department', '')
        status_filter = self.request.GET.get('status', '')

        # Apply search
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )

        # Apply role filter
        if role_filter:
            queryset = queryset.filter(profile__role=role_filter)

        # Apply department filter
        if department_filter:
            queryset = queryset.filter(profile__department__id=department_filter)

        # Apply status filter
        if status_filter:
            queryset = queryset.filter(is_active=(status_filter == 'active'))

        return queryset.select_related('profile', 'profile__department').order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'total_users': self.get_queryset().count(),
            'active_users': self.get_queryset().filter(is_active=True).count(),
            'inactive_users': self.get_queryset().filter(is_active=False).count(),
            'role_choices': UserProfile.ROLE_CHOICES,
            'departments': Department.objects.all(),
        })
        return context


class UserCreateView(StaffRequiredMixin, BaseCreateView):
    """Create new user with profile"""
    model = User
    form_class = UserCreateForm
    template_name = 'employees/user_form.html'
    success_url = reverse_lazy('employees:user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New User'
        context['action'] = 'Create'
        context['role_choices'] = UserProfile.ROLE_CHOICES
        context['departments'] = Department.objects.all()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'User "{self.object.username}" created successfully!')
        return response


class UserUpdateView(StaffRequiredMixin, BaseUpdateView):
    """Update existing user and profile"""
    model = User
    form_class = UserUpdateForm
    template_name = 'employees/user_form.html'
    success_url = reverse_lazy('employees:user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit User: {self.object.username}'
        context['action'] = 'Update'
        context['role_choices'] = UserProfile.ROLE_CHOICES
        context['departments'] = Department.objects.all()
        context['is_edit'] = True
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'User "{self.object.username}" updated successfully!')
        return response


class UserDeleteView(AdminRequiredMixin, BaseDeleteView):
    """Delete user (soft delete by deactivating)"""
    model = User
    template_name = 'employees/user_confirm_delete.html'
    success_url = reverse_lazy('employees:user_list')

    def delete(self, request, *args, **kwargs):
        """Soft delete by deactivating user"""
        user = self.get_object()
        user.is_active = False
        user.save()
        messages.success(request, f'User "{user.username}" has been deactivated!')
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete User: {self.object.username}'
        context['object_name'] = self.object.username
        return context


class UserBulkOperationView(AdminRequiredMixin, BaseBulkOperationView):
    """Bulk operations on users"""
    model = User
    success_url = reverse_lazy('employees:user_list')

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        selected_ids = request.POST.getlist('selected_ids')
        
        if not selected_ids:
            messages.error(request, 'No users selected.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        queryset = User.objects.filter(id__in=selected_ids)
        
        if action == 'delete':
            count = queryset.count()
            queryset.update(is_active=False)
            messages.success(request, f'Successfully deactivated {count} users.')
            
        elif action == 'activate':
            count = queryset.count()
            queryset.update(is_active=True)
            messages.success(request, f'Successfully activated {count} users.')
            
        elif action == 'delete_permanent':
            count = queryset.count()
            usernames = ', '.join([u.username for u in queryset])
            queryset.delete()
            messages.success(request, f'Permanently deleted {count} users: {usernames}')
            
        else:
            messages.error(request, 'Invalid action.')
        
        return redirect(request.META.get('HTTP_REFERER', '/'))


class UserToggleStatusView(StaffRequiredMixin, BaseToggleStatusView):
    """Toggle user active/inactive status"""
    model = User
    success_url = reverse_lazy('employees:user_list')

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs['pk'])
        
        # Don't allow deactivating superusers unless current user is superuser
        if user.is_superuser and not request.user.is_superuser:
            messages.error(request, 'You cannot deactivate a superuser.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        user.is_active = not user.is_active
        user.save()
        
        status_text = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User "{user.username}" {status_text} successfully!')
        
        return redirect(request.META.get('HTTP_REFERER', '/'))


# Function-based views for additional operations

@admin_required
def user_dashboard(request):
    """User management dashboard with statistics"""
    from django.shortcuts import render
    
    context = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'inactive_users': User.objects.filter(is_active=False).count(),
        'staff_users': User.objects.filter(is_staff=True).count(),
        'superusers': User.objects.filter(is_superuser=True).count(),
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'users_by_role': {},
        'users_by_department': {},
    }
    
    # Get users by role
    for role, _ in UserProfile.ROLE_CHOICES:
        context['users_by_role'][role] = UserProfile.objects.filter(role=role).count()
    
    # Get users by department
    for dept in Department.objects.all():
        context['users_by_department'][dept.name] = User.objects.filter(
            profile__department=dept
        ).count()
    
    return render(request, 'employees/user_dashboard.html', context)


@transaction.atomic
def create_multiple_users(request):
    """Create multiple users at once"""
    if request.method == 'POST':
        users_data = request.POST.getlist('users_data')
        created_users = []
        errors = []
        
        for user_data in users_data:
            try:
                # Parse user data (assuming JSON format)
                import json
                data = json.loads(user_data)
                
                # Create user
                user = User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    password=data['password'],
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', '')
                )
                
                # Create profile
                UserProfile.objects.create(
                    user=user,
                    role=data.get('role', 'employee'),
                    department_id=data.get('department'),
                    phone=data.get('phone', '')
                )
                
                created_users.append(user)
                
            except Exception as e:
                errors.append(f"Error creating user {data.get('username', 'unknown')}: {str(e)}")
        
        if created_users:
            messages.success(request, f'Successfully created {len(created_users)} users.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        
        return redirect('employees:user_list')
    
    return render(request, 'employees/create_multiple_users.html', {
        'role_choices': UserProfile.ROLE_CHOICES,
        'departments': Department.objects.all()
    })


# URL patterns to add to urls.py:
"""
urlpatterns = [
    # User CRUD URLs
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/add/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('users/<int:pk>/toggle-status/', UserToggleStatusView.as_view(), name='user_toggle_status'),
    path('users/bulk-operation/', UserBulkOperationView.as_view(), name='user_bulk_operation'),
    
    # Additional user management URLs
    path('users/dashboard/', user_dashboard, name='user_dashboard'),
    path('users/create-multiple/', create_multiple_users, name='create_multiple_users'),
]
"""
