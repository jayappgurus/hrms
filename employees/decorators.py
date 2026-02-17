from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

def role_required(allowed_roles=[]):
    """
    Decorator to restrict access to users with specific roles
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'You must be logged in to access this page.')
                return redirect('login')

            try:
                user_profile = request.user.profile
                if user_profile.role in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, 'You do not have permission to access this page.')
                    return redirect('employees:employee_list')
            except AttributeError:
                messages.error(request, 'User profile not found. Please contact administrator.')
                return redirect('employees:employee_list')

        return wrapper
    return decorator

def admin_required(view_func):
    """
    Decorator to restrict access to admin users only
    """
    return role_required(['admin'])(view_func)

def director_required(view_func):
    """
    Decorator to restrict access to Director users
    """
    return role_required(['admin', 'director'])(view_func)

def hr_required(view_func):
    """
    Decorator to restrict access to HR users only
    """
    return role_required(['admin', 'director', 'hr'])(view_func)

def accountant_required(view_func):
    """
    Decorator to restrict access to Accountant users
    """
    return role_required(['admin', 'director', 'accountant'])(view_func)

def manager_required(view_func):
    """
    Decorator to restrict access to managers and above
    """
    return role_required(['admin', 'director', 'hr', 'manager'])(view_func)

def it_admin_required(view_func):
    """
    Decorator to restrict access to IT Admin users
    """
    return role_required(['admin', 'it_admin'])(view_func)

def employee_required(view_func):
    """
    Decorator to restrict access to all authenticated employees
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to access this page.')
            return redirect('login')
        return view_func(request, *args, **kwargs)

    return wrapper

def can_manage_employees(view_func):
    """
    Decorator to restrict access to users who can manage employees
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to access this page.')
            return redirect('login')

        try:
            user_profile = request.user.profile
            if user_profile.can_manage_employees:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You do not have permission to manage employees.')
                return redirect('employees:employee_list')
        except AttributeError:
            messages.error(request, 'User profile not found. Please contact administrator.')
            return redirect('employees:employee_list')

    return wrapper

def can_view_all_employees(view_func):
    """
    Decorator to restrict access to users who can view all employees
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to access this page.')
            return redirect('login')

        try:
            user_profile = request.user.profile
            if user_profile.can_view_all_employees:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You do not have permission to view all employees.')
                return redirect('employees:employee_list')
        except AttributeError:
            messages.error(request, 'User profile not found. Please contact administrator.')
            return redirect('employees:employee_list')

    return wrapper

def can_manage_system(view_func):
    """
    Decorator to restrict access to users who can manage system settings
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to access this page.')
            return redirect('login')

        try:
            user_profile = request.user.profile
            if user_profile.can_manage_system:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You do not have permission to access system settings.')
                return redirect('employees:employee_list')
        except AttributeError:
            messages.error(request, 'User profile not found. Please contact administrator.')
            return redirect('employees:employee_list')

    return wrapper
