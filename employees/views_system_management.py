from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from .models import SystemDetail, Employee
import csv


@login_required
def system_management(request):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access system management.')
        return redirect('employees:dashboard')
    
    # Get system statistics
    total_systems = SystemDetail.objects.count()
    available_systems = SystemDetail.objects.filter(employee__isnull=True).count()
    allocated_systems = SystemDetail.objects.filter(employee__isnull=False, is_active=True).count()
    inactive_systems = SystemDetail.objects.filter(is_active=False).count()
    
    # System type statistics
    windows_systems = SystemDetail.objects.filter(system_type='windows').count()
    mac_systems = SystemDetail.objects.filter(system_type='mac').count()
    
    # MAC Address statistics (from SystemDetail)
    total_mac_addresses = SystemDetail.objects.filter(macaddress__isnull=False).exclude(macaddress='').count()
    allocated_mac_addresses = SystemDetail.objects.filter(
        macaddress__isnull=False, 
        employee__isnull=False
    ).exclude(macaddress='').count()
    available_mac_addresses = SystemDetail.objects.filter(
        macaddress__isnull=False, 
        employee__isnull=True
    ).exclude(macaddress='').count()
    
    context = {
        'total_systems': total_systems,
        'available_systems': available_systems,
        'allocated_systems': allocated_systems,
        'inactive_systems': inactive_systems,
        'windows_systems': windows_systems,
        'mac_systems': mac_systems,
        'total_mac_addresses': total_mac_addresses,
        'allocated_mac_addresses': allocated_mac_addresses,
        'available_mac_addresses': available_mac_addresses,
    }
    
    return render(request, 'employees/system_management.html', context)


@login_required
def get_system_details(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    system_id = request.GET.get('system_id')
    
    try:
        system = get_object_or_404(SystemDetail, pk=system_id)
        data = {
            'id': system.id,
            'cpu_company_name': system.cpu_company_name,
            'cpu_label_no': system.cpu_label_no,
            'system_type': system.get_system_type_display(),
            'macaddress': system.macaddress if system.macaddress else 'N/A',
            'status': 'Allocated' if system.employee else 'Available',
            'employee': system.employee.full_name if system.employee else None,
            'allocated_date': system.allocated_date.strftime('%Y-%m-%d') if system.allocated_date else None,
        }
        
        return JsonResponse({'success': True, 'system': data})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_employees_for_assignment(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    employees = Employee.objects.filter(
        employment_status='active'
    ).values('id', 'full_name', 'employee_code', 'department__name')
    
    return JsonResponse({'success': True, 'employees': list(employees)})


@login_required
def get_mac_systems_assignments(request):
    """
    API to get MAC address assignments from SystemDetail with employee details
    """
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        # Get systems that have MAC addresses
        mac_systems = SystemDetail.objects.filter(
            macaddress__isnull=False
        ).exclude(macaddress='').select_related('employee', 'employee__department')
        
        assignments_data = []
        for system in mac_systems:
            assignments_data.append({
                'id': system.id,
                'mac_address': system.macaddress,
                'system_name': f"{system.cpu_company_name} - {system.cpu_label_no}",
                'system_type': system.get_system_type_display(),
                'employee_id': system.employee.id if system.employee else None,
                'employee_name': system.employee.full_name if system.employee else 'Unassigned',
                'employee_code': system.employee.employee_code if system.employee else 'N/A',
                'department': system.employee.department.name if system.employee and system.employee.department else 'N/A',
            })
        
        return JsonResponse({
            'success': True,
            'mac_assignments': assignments_data
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_windows_systems_assignments(request):
    """
    API to get Windows system assignments with employee details
    """
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        # Filter for Windows systems
        windows_systems = SystemDetail.objects.filter(
            system_type='windows'
        ).select_related('employee', 'employee__department')
        
        assignments_data = []
        for system in windows_systems:
            assignments_data.append({
                'id': system.id,
                'system_name': f"{system.cpu_company_name} - {system.cpu_label_no}",
                'macaddress': system.macaddress if system.macaddress else 'N/A',
                'employee_id': system.employee.id if system.employee else None,
                'employee_name': system.employee.full_name if system.employee else 'Unassigned',
                'employee_code': system.employee.employee_code if system.employee else 'N/A',
                'department': system.employee.department.name if system.employee and system.employee.department else 'N/A',
                'cpu_company_name': system.cpu_company_name,
            })
        
        return JsonResponse({
            'success': True,
            'windows_assignments': assignments_data
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def assign_system(request):
    """
    API to assign system to employee
    """
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    system_id = request.POST.get('system_id')
    employee_id = request.POST.get('employee_id')
    
    try:
        system = get_object_or_404(SystemDetail, pk=system_id)
        employee = get_object_or_404(Employee, pk=employee_id)
        
        system.employee = employee
        system.is_active = True
        system.allocated_by = request.user
        system.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'System successfully assigned to {employee.full_name}'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def export_mac_systems_csv(request):
    """
    Export MAC address assignments to CSV
    """
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to export data.')
        return redirect('employees:system_management')
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mac_systems_assignments.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['MAC Address', 'System Name', 'System Type', 'Employee Name', 'Employee Code', 'Department'])
    
    # Get systems that have MAC addresses
    mac_systems = SystemDetail.objects.filter(
        macaddress__isnull=False
    ).exclude(macaddress='').select_related('employee', 'employee__department')
    
    for system in mac_systems:
        writer.writerow([
            system.macaddress,
            f"{system.cpu_company_name} - {system.cpu_label_no}",
            system.get_system_type_display(),
            system.employee.full_name if system.employee else 'Unassigned',
            system.employee.employee_code if system.employee else 'N/A',
            system.employee.department.name if system.employee and system.employee.department else 'N/A',
        ])
    
    return response


@login_required
def export_windows_systems_csv(request):
    """
    Export Windows system assignments to CSV
    """
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to export data.')
        return redirect('employees:system_management')
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="windows_systems_assignments.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['System Name', 'MAC Address', 'Employee Name', 'Employee Code', 'Department', 'CPU Company'])
    
    # Filter for Windows systems
    windows_systems = SystemDetail.objects.filter(
        system_type='windows'
    ).select_related('employee', 'employee__department')
    
    for system in windows_systems:
        writer.writerow([
            f"{system.cpu_company_name} - {system.cpu_label_no}",
            system.macaddress if system.macaddress else 'N/A',
            system.employee.full_name if system.employee else 'Unassigned',
            system.employee.employee_code if system.employee else 'N/A',
            system.employee.department.name if system.employee and system.employee.department else 'N/A',
            system.cpu_company_name,
        ])
    
    return response
