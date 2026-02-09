from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import UserProfile, Department
from .forms import UserProfileForm
from .decorators import admin_required, hr_required
from django.contrib.auth.forms import UserCreationForm


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'employees/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.select_related('profile', 'profile__department').all()
        search_term = self.request.GET.get('search', '')
        role_filter = self.request.GET.get('role', '')
        
        if search_term:
            queryset = queryset.filter(
                username__icontains=search_term
            ) | queryset.filter(
                first_name__icontains=search_term
            ) | queryset.filter(
                last_name__icontains=search_term
            ) | queryset.filter(
                email__icontains=search_term
            )
        
        if role_filter:
            queryset = queryset.filter(profile__role=role_filter)
        
        return queryset.order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        context['role_choices'] = UserProfile.ROLE_CHOICES
        context['search_form'] = self.request.GET.get('search', '')
        context['role_filter'] = self.request.GET.get('role', '')
        return context


class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'employees/user_create.html'
    success_url = reverse_lazy('employees:user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New User'
        context['departments'] = Department.objects.all()
        context['role_choices'] = UserProfile.ROLE_CHOICES
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Create user profile with role and department
        role = self.request.POST.get('role', 'employee')
        department_id = self.request.POST.get('department')
        phone = self.request.POST.get('phone', '')
        
        UserProfile.objects.create(
            user=self.object,
            role=role,
            department_id=department_id if department_id else None,
            phone=phone
        )
        
        messages.success(self.request, f'User {self.object.username} created successfully!')
        return response


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'employees/user_profile_edit.html'
    success_url = reverse_lazy('employees:user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit User Profile - {self.object.user.username}'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'User profile for {self.object.user.username} updated successfully!')
        return super().form_valid(form)


@admin_required
def create_user_profile(request, user_id):
    """Create or update user profile for existing users"""
    user = get_object_or_404(User, pk=user_id)
    
    try:
        profile = user.profile
        messages.info(request, f'Profile already exists for {user.username}')
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(
            user=user,
            role='employee',  # Default role
            department=None,
            phone=''
        )
        messages.success(request, f'Profile created for {user.username}')
    
    return redirect('employees:user_list')


@hr_required
def assign_role(request, user_id):
    """Assign role to user (HR and Admin only)"""
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        role = request.POST.get('role')
        department_id = request.POST.get('department')
        phone = request.POST.get('phone', '')
        
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.department_id = department_id if department_id else None
        profile.phone = phone
        profile.save()
        
        action = 'created' if created else 'updated'
        messages.success(request, f'User role {action} for {user.username}')
    
    return redirect('employees:user_list')


@login_required
def my_profile(request):
    """View and edit own profile"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(
            user=request.user,
            role='employee',
            department=None,
            phone=''
        )
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('employees:my_profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'employees/my_profile.html', {
        'form': form,
        'profile': profile,
        'title': 'My Profile'
    })
