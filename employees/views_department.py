from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Department, Designation
from .decorators import admin_required, hr_required
import json

@login_required
@admin_required
def department_management(request):
    """View for managing departments and designations"""
    departments = Department.objects.all().prefetch_related('designation_set', 'employee_set')
    designations = Designation.objects.select_related('department').all()
    
    context = {
        'departments': departments,
        'designations': designations,
        'title': 'Department Management'
    }
    return render(request, 'employees/department_management.html', context)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def add_department(request):
    """Add new department via AJAX"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name:
            return JsonResponse({'success': False, 'error': 'Department name is required'})
        
        # Check if department already exists
        if Department.objects.filter(name__iexact=name).exists():
            return JsonResponse({'success': False, 'error': 'Department with this name already exists'})
        
        try:
            department = Department.objects.create(
                name=name,
                description=description
            )
            return JsonResponse({'success': True, 'department_id': department.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def add_designation(request):
    """Add new designation via AJAX"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        department_id = request.POST.get('department', '').strip()
        
        if not name:
            return JsonResponse({'success': False, 'error': 'Designation name is required'})
        
        if not department_id:
            return JsonResponse({'success': False, 'error': 'Department is required'})
        
        try:
            department = Department.objects.get(id=department_id)
            
            # Check if designation already exists for this department
            if Designation.objects.filter(name__iexact=name, department=department).exists():
                return JsonResponse({'success': False, 'error': 'Designation with this name already exists in this department'})
            
            designation = Designation.objects.create(
                name=name,
                department=department,
                description=description
            )
            return JsonResponse({'success': True, 'designation_id': designation.id})
        except Department.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Department not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
