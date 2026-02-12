from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
from django import forms
from django.db.models import Q
from .models import Employee, UserProfile, Department
from .decorators import admin_required


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'department', 'phone']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.all()
        self.fields['department'].empty_label = "Select Department"
        self.fields['department'].required = False


class UserSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search users...'
        })
    )


@login_required
def my_profile(request):
    """Display current user's profile"""
    try:
        profile = request.user.profile
        employee = profile.employee if hasattr(profile, 'employee') else None
    except UserProfile.DoesNotExist:
        profile = None
        employee = None
    
    context = {
        'profile': profile,
        'employee': employee,
        'user': request.user
    }
    
    return render(request, 'employees/my_profile.html', context)


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
                Q(username__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term)
            )
        
        if role_filter:
            queryset = queryset.filter(profile__role=role_filter)
        
        return queryset.order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = self.get_queryset().count()
        context['active_users'] = self.get_queryset().filter(is_active=True).count()
        return context


class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'employees/user_create.html'
    success_url = reverse_lazy('employees:user_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'User {self.object.username} created successfully!')
        return response


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'employees/user_edit.html'
    success_url = reverse_lazy('employees:user_list')
    
    def get_object(self):
        return get_object_or_404(User, pk=self.kwargs['pk'])
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'User {self.object.username} updated successfully!')
        return response


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'employees/user_profile_edit.html'
    success_url = reverse_lazy('employees:user_list')
    
    def get_object(self):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        profile, created = UserProfile.objects.get_or_create(user=user)
        return profile
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Profile for {self.object.user.username} updated successfully!')
        return response


@login_required
def assign_role(request, user_id):
    """Assign or update role for a user"""
    user = get_object_or_404(User, pk=user_id)
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        role = request.POST.get('role')
        department_id = request.POST.get('department')
        
        if role:
            profile.role = role
        if department_id:
            profile.department_id = department_id
        
        profile.save()
        messages.success(request, f'Role assigned to {user.username} successfully!')
        return redirect('employees:user_list')
    
    return redirect('employees:user_list')


from django.http import JsonResponse
from django.views import View


class UserCredentialsAPIView(LoginRequiredMixin, View):
    """API view to get user credentials"""
    def get(self, request):
        users = User.objects.select_related('profile').all()
        data = []
        for user in users:
            data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.profile.role if hasattr(user, 'profile') else 'employee',
                'is_active': user.is_active
            })
        return JsonResponse({'users': data})


class UserCredentialsCollectionView(LoginRequiredMixin, ListView):
    """View to display user credentials collection"""
    model = User
    template_name = 'employees/user_credentials.html'
    context_object_name = 'users'
    
    def get_queryset(self):
        return User.objects.select_related('profile').all()


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy('employees:user_list')
    
    def get_object(self):
        return get_object_or_404(User, pk=self.kwargs['pk'])
