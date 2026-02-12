from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.generic import View, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Employee, UserProfile
from .forms import EmployeeRegistrationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form that accepts both username and email"""
    
    username = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'class': 'form-control',
            'placeholder': 'Enter username or email'
        })
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Check if the input is an email address
        if '@' in username:
            try:
                user = User.objects.get(email=username)
                return user.username
            except User.DoesNotExist:
                raise ValidationError("No user found with this email address.")
        return username


@method_decorator(csrf_protect, name='dispatch')
class CustomLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return self.redirect_based_on_role(request.user)
        
        form = CustomAuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})
    
    def post(self, request):
        form = CustomAuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Trilokn Infotech Pvt. Ltd., {user.get_full_name() or user.username}!')
                return self.redirect_based_on_role(user)
            else:
                messages.error(request, 'Invalid username/email or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
        
        return render(request, 'registration/login.html', {'form': form})
    
    def redirect_based_on_role(self, user):
        """Redirect user based on their role"""
        try:
            profile = user.profile
            role = profile.role
            
            # Role-based redirects - all users go to dashboard
            if role == 'admin':
                return HttpResponseRedirect(reverse('employees:dashboard'))
            elif role == 'hr':
                return HttpResponseRedirect(reverse('employees:dashboard'))
            elif role == 'manager':
                return HttpResponseRedirect(reverse('employees:dashboard'))
            elif role == 'it_admin':
                return HttpResponseRedirect(reverse('employees:dashboard'))
            else:  # employee
                return HttpResponseRedirect(reverse('employees:dashboard'))
                
        except AttributeError:
            # If user has no profile, redirect to dashboard
            return HttpResponseRedirect(reverse('employees:dashboard'))


def custom_logout(request):
    """Custom logout view"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return HttpResponseRedirect(reverse('login'))


class EmployeeRegistrationView(CreateView):
    model = Employee
    form_class = EmployeeRegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Extract user data
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                full_name = form.cleaned_data.get('full_name')
                email = form.cleaned_data.get('personal_email')

                # Split full name
                name_parts = full_name.split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ""

                # Create User
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    email=email
                )

                # Create Employee
                employee = form.save(commit=False)
                employee.full_name = full_name
                # Use personal email as official email for registration
                employee.official_email = email
                employee.joining_date = timezone.now().date()
                employee.save()

                # Create UserProfile
                UserProfile.objects.create(
                    user=user,
                    employee=employee,
                    role='employee',
                    department=employee.department
                )

                messages.success(self.request, "Registration successful! You can now login.")
                return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"Registration failed: {str(e)}")
            return self.form_invalid(form)
