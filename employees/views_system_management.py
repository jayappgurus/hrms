from django.shortcuts import render, get_object_or_404, redirect

from django.contrib import messages

from django.contrib.auth.decorators import login_required

from django.views.decorators.http import require_POST

from django.db.models import Count, Q

from django.http import JsonResponse, HttpResponse

from django.utils import timezone

from .models import SystemDetail, Employee

import csv
import json





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

    

    # MAC Address statistics (only for MAC systems)

    total_mac_addresses = SystemDetail.objects.filter(

        system_type='mac',

        macaddress__isnull=False

    ).exclude(macaddress='').count()

    

    allocated_mac_addresses = SystemDetail.objects.filter(

        system_type='mac',

        macaddress__isnull=False, 

        employee__isnull=False,

        is_active=True

    ).exclude(macaddress='').count()

    

    available_mac_addresses = SystemDetail.objects.filter(

        system_type='mac',

        employee__isnull=False,

        is_active=False

    ).count()

    

    # Windows systems allocation statistics

    allocated_windows_systems = SystemDetail.objects.filter(

        system_type='windows',

        employee__isnull=False,

        is_active=True

    ).count()

    available_windows_systems = SystemDetail.objects.filter(

        system_type='windows',

        employee__isnull=False,

        is_active=False

    ).count()

    

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

        'allocated_windows_systems': allocated_windows_systems,

        'available_windows_systems': available_windows_systems,

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

    API to get MAC system assignments (only system_type='mac') with employee details

    """

    if not request.user.is_staff and not request.user.is_superuser:

        return JsonResponse({'error': 'Permission denied'}, status=403)

    

    try:

        # Get only MAC systems (system_type='mac')

        mac_systems = SystemDetail.objects.filter(

            system_type='mac',

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

                'is_active': system.is_active,

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

                'is_active': system.is_active,

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

    Export MAC system assignments to CSV (only system_type='mac')

    """

    if not request.user.is_staff and not request.user.is_superuser:

        messages.error(request, 'You do not have permission to export data.')

        return redirect('employees:system_management')

    

    # Create the HttpResponse object with CSV header

    response = HttpResponse(content_type='text/csv')

    response['Content-Disposition'] = 'attachment; filename="mac_systems_assignments.csv"'

    

    writer = csv.writer(response)

    writer.writerow(['MAC Address', 'System Name', 'System Type', 'Employee Name', 'Employee Code', 'Department'])

    

    # Get only MAC systems (system_type='mac')

    mac_systems = SystemDetail.objects.filter(

        system_type='mac',

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





@login_required

def show_mac_address(request):

    """

    Show MAC system assignments page (only system_type='mac')

    """

    if not request.user.is_staff and not request.user.is_superuser:

        messages.error(request, 'You do not have permission to view this page.')

        return redirect('employees:system_management')

    

    # Get filter parameter

    status_filter = request.GET.get('status', 'all')

    

    # Get only MAC systems (system_type='mac')

    mac_systems = SystemDetail.objects.filter(

        system_type='mac',

        macaddress__isnull=False

    ).exclude(macaddress='').select_related('employee', 'employee__department')

    

    # Apply status filter

    if status_filter == 'assigned':

        mac_systems = mac_systems.filter(is_active=True)

    elif status_filter == 'pending':

        mac_systems = mac_systems.filter(is_active=False)

    

    mac_systems = mac_systems.order_by('employee__full_name')

    

    context = {

        'mac_systems': mac_systems,

        'title': 'MAC System Assignments',

        'status_filter': status_filter

    }

    

    return render(request, 'system/show_mac_address.html', context)





@login_required

@require_POST

def update_system_status(request):

    """

    AJAX endpoint to update system allocation status

    """

    if not request.user.is_staff and not request.user.is_superuser:

        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)

    

    try:

        system_id = request.POST.get('system_id')

        is_active = request.POST.get('is_active') == 'true'

        

        if not system_id:

            return JsonResponse({'success': False, 'message': 'System ID is required'})

        

        # Get the system

        system = SystemDetail.objects.get(pk=system_id)

        

        # Update status

        old_status = 'Assigned' if system.is_active else 'Pending'

        system.is_active = is_active

        system.save()

        

        new_status = 'Assigned' if is_active else 'Pending'

        

        return JsonResponse({

            'success': True,

            'message': f'Status updated from {old_status} to {new_status}',

            'system_id': system_id,

            'is_active': is_active

        })

        

    except SystemDetail.DoesNotExist:

        return JsonResponse({'success': False, 'message': 'System not found'}, status=404)

    except Exception as e:

        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
def get_mac_peripheral_devices(request):
    """
    API to get MAC system peripheral devices (keyboard, mouse, headphone, extender)
    """
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        # Get MAC systems with their peripheral devices
        mac_systems = SystemDetail.objects.filter(
            system_type='mac'
        ).select_related('employee', 'employee__department')
        
        peripheral_data = []
        for system in mac_systems:
            peripheral_data.append({
                'id': system.id,
                'system_name': f"{system.cpu_company_name} - {system.cpu_label_no}" if system.cpu_company_name and system.cpu_label_no else f"MAC System - {system.id}",
                'employee_name': system.employee.full_name if system.employee else 'Unassigned',
                'employee_code': system.employee.employee_code if system.employee else 'N/A',
                'department': system.employee.department.name if system.employee and system.employee.department else 'N/A',
                'keyboard': f"{system.keyboard_company_name} - {system.keyboard_label_no}" if system.keyboard_company_name and system.keyboard_label_no else 'N/A',
                'mouse': f"{system.mouse_company_name} - {system.mouse_label_no}" if system.mouse_company_name and system.mouse_label_no else 'N/A',
                'headphone': f"{system.headphone_company_name} - {system.headphone_label_no}" if system.has_headphone and system.headphone_company_name and system.headphone_label_no else 'N/A',
                'extender': f"{system.extender_name} - {system.extender_label}" if system.has_extender and system.extender_name and system.extender_label else 'N/A',
                'keyboard_allocated': system.keyboard_allocated,
                'mouse_allocated': system.mouse_allocated,
                'headphone_allocated': system.headphone_allocated if system.has_headphone else False,
                'extender_allocated': system.extender_allocated if system.has_extender else False,
                'is_active': system.is_active,
            })
        
        return JsonResponse({
            'success': True,
            'mac_peripherals': peripheral_data
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_windows_peripheral_devices(request):
    """
    API to get Windows system peripheral devices (keyboard, mouse, headphone, extender)
    """
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        # Get Windows systems with their peripheral devices
        windows_systems = SystemDetail.objects.filter(
            system_type='windows'
        ).select_related('employee', 'employee__department')
        
        peripheral_data = []
        for system in windows_systems:
            peripheral_data.append({
                'id': system.id,
                'system_name': f"{system.cpu_company_name} - {system.cpu_label_no}" if system.cpu_company_name and system.cpu_label_no else f"Windows System - {system.id}",
                'employee_name': system.employee.full_name if system.employee else 'Unassigned',
                'employee_code': system.employee.employee_code if system.employee else 'N/A',
                'department': system.employee.department.name if system.employee and system.employee.department else 'N/A',
                'keyboard': f"{system.keyboard_company_name} - {system.keyboard_label_no}" if system.keyboard_company_name and system.keyboard_label_no else 'N/A',
                'mouse': f"{system.mouse_company_name} - {system.mouse_label_no}" if system.mouse_company_name and system.mouse_label_no else 'N/A',
                'headphone': f"{system.headphone_company_name} - {system.headphone_label_no}" if system.has_headphone and system.headphone_company_name and system.headphone_label_no else 'N/A',
                'extender': f"{system.extender_name} - {system.extender_label}" if system.has_extender and system.extender_name and system.extender_label else 'N/A',
                'keyboard_allocated': system.keyboard_allocated,
                'mouse_allocated': system.mouse_allocated,
                'headphone_allocated': system.headphone_allocated if system.has_headphone else False,
                'extender_allocated': system.extender_allocated if system.has_extender else False,
                'is_active': system.is_active,
            })
        
        return JsonResponse({
            'success': True,
            'windows_peripherals': peripheral_data
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def add_device_cpu(request):
    """API to add CPU system"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Use existing employee for inventory devices
        inventory_employee = Employee.objects.first()
        if not inventory_employee:
            return JsonResponse({'error': 'No employees found in the system. Please add an employee first.'}, status=400)
        
        # Create minimal SystemDetail for CPU
        system = SystemDetail.objects.create(
            employee=inventory_employee,
            cpu_company_name=data.get('cpu_company_name', ''),
            cpu_processor=data.get('cpu_processor', ''),
            cpu_ram=data.get('cpu_ram', ''),
            cpu_storage=data.get('cpu_storage', ''),
            cpu_label_no=data.get('cpu_label_no', ''),
            macaddress=data.get('macaddress', ''),
            system_type=data.get('system_type', 'windows'),
            is_active=data.get('is_active', False),
            allocated_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'CPU added successfully',
            'id': system.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def add_device_screen(request):
    """API to add screen device"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Use existing employee for inventory devices
        inventory_employee = Employee.objects.first()
        if not inventory_employee:
            return JsonResponse({'error': 'No employees found in the system. Please add an employee first.'}, status=400)
        
        # Create minimal SystemDetail for screen
        system = SystemDetail.objects.create(
            employee=inventory_employee,
            screen_company_name=data.get('screen_company_name', ''),
            screen_size=data.get('screen_size', ''),
            screen_label_no=data.get('screen_label_no', ''),
            screen_allocated=data.get('screen_allocated', False),
            system_type='windows',
            is_active=False,
            allocated_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Screen added successfully',
            'id': system.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def add_device_keyboard(request):
    """API to add keyboard device"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Use existing employee for inventory devices
        inventory_employee = Employee.objects.first()
        if not inventory_employee:
            return JsonResponse({'error': 'No employees found in the system. Please add an employee first.'}, status=400)
        
        # Create minimal SystemDetail for keyboard
        system = SystemDetail.objects.create(
            employee=inventory_employee,
            keyboard_company_name=data.get('keyboard_company_name', ''),
            keyboard_label_no=data.get('keyboard_label_no', ''),
            keyboard_allocated=data.get('keyboard_allocated', False),
            system_type='windows',
            is_active=False,
            allocated_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Keyboard added successfully',
            'id': system.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def add_device_mouse(request):
    """API to add mouse device"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Use existing employee for inventory devices
        inventory_employee = Employee.objects.first()
        if not inventory_employee:
            return JsonResponse({'error': 'No employees found in the system. Please add an employee first.'}, status=400)
        
        # Create minimal SystemDetail for mouse
        system = SystemDetail.objects.create(
            employee=inventory_employee,
            mouse_company_name=data.get('mouse_company_name', ''),
            mouse_label_no=data.get('mouse_label_no', ''),
            mouse_allocated=data.get('mouse_allocated', False),
            system_type='windows',
            is_active=False,
            allocated_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Mouse added successfully',
            'id': system.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def add_device_headphone(request):
    """API to add headphone device"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Use existing employee for inventory devices
        inventory_employee = Employee.objects.first()
        if not inventory_employee:
            return JsonResponse({'error': 'No employees found in the system. Please add an employee first.'}, status=400)
        
        # Create minimal SystemDetail for headphone
        system = SystemDetail.objects.create(
            employee=inventory_employee,
            has_headphone=True,
            headphone_company_name=data.get('headphone_company_name', ''),
            headphone_label_no=data.get('headphone_label_no', ''),
            headphone_allocated=data.get('headphone_allocated', False),
            system_type='windows',
            is_active=False,
            allocated_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Headphone added successfully',
            'id': system.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def add_device_extender(request):
    """API to add extender device"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Use existing employee for inventory devices
        inventory_employee = Employee.objects.first()
        if not inventory_employee:
            return JsonResponse({'error': 'No employees found in the system. Please add an employee first.'}, status=400)
        
        # Create minimal SystemDetail for extender
        system = SystemDetail.objects.create(
            employee=inventory_employee,
            has_extender=True,
            extender_name=data.get('extender_name', ''),
            extender_label=data.get('extender_label', ''),
            extender_allocated=data.get('extender_allocated', False),
            system_type='windows',
            is_active=False,
            allocated_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Extender added successfully',
            'id': system.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

