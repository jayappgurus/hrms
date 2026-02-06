from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.generic import View


@method_decorator(csrf_protect, name='dispatch')
class CustomLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return self.redirect_based_on_role(request.user)
        
        form = AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})
    
    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                return self.redirect_based_on_role(user)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
        
        return render(request, 'registration/login.html', {'form': form})
    
    def redirect_based_on_role(self, user):
        """Redirect user based on their role"""
        try:
            profile = user.profile
            role = profile.role
            
            # Role-based redirects
            if role == 'admin':
                return HttpResponseRedirect('/admin/')
            elif role == 'hr':
                return HttpResponseRedirect(reverse('employees:user_list'))
            elif role == 'manager':
                return HttpResponseRedirect(reverse('employees:employee_list'))
            elif role == 'it_admin':
                return HttpResponseRedirect('/admin/')
            else:  # employee
                return HttpResponseRedirect(reverse('employees:employee_list'))
                
        except AttributeError:
            # If user has no profile, redirect to employee list
            return HttpResponseRedirect(reverse('employees:employee_list'))


def custom_logout(request):
    """Custom logout view"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return HttpResponseRedirect(reverse('login'))
