from django.shortcuts import render, get_object_or_404, redirect

from django.contrib import messages

from django.contrib.auth.decorators import login_required

from django.views.decorators.http import require_POST

from django.db.models import Count, Q

from django.http import JsonResponse, HttpResponse

from django.utils import timezone

from .models import SystemDetail, Employee, CPUDevice, ScreenDevice, KeyboardDevice, MouseDevice, HeadphoneDevice, ExtenderDevice

import csv
import json





@login_required
def system_management(request):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access system management.')
        return redirect('employees:dashboard')
    
    # Get system statistics from SystemDetail
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
    
    # Device inventory statistics
    total_cpus = CPUDevice.objects.count()
    allocated_cpus = CPUDevice.objects.filter(status='allocated').count()
    available_cpus = CPUDevice.objects.filter(status='available').count()
    
    total_screens = ScreenDevice.objects.count()
    allocated_screens = ScreenDevice.objects.filter(status='allocated').count()
    available_screens = ScreenDevice.objects.filter(status='available').count()
    
    total_keyboards = KeyboardDevice.objects.count()
    allocated_keyboards = KeyboardDevice.objects.filter(status='allocated').count()
    available_keyboards = KeyboardDevice.objects.filter(status='available').count()
    
    total_mice = MouseDevice.objects.count()
    allocated_mice = MouseDevice.objects.filter(status='allocated').count()
    available_mice = MouseDevice.objects.filter(status='available').count()
    
    total_headphones = HeadphoneDevice.objects.count()
    allocated_headphones = HeadphoneDevice.objects.filter(status='allocated').count()
    available_headphones = HeadphoneDevice.objects.filter(status='available').count()
    
    total_extenders = ExtenderDevice.objects.count()
    allocated_extenders = ExtenderDevice.objects.filter(status='allocated').count()
    available_extenders = ExtenderDevice.objects.filter(status='available').count()
    
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
        
        # Device inventory statistics
        'total_cpus': total_cpus,
        'allocated_cpus': allocated_cpus,
        'available_cpus': available_cpus,
        
        'total_screens': total_screens,
        'allocated_screens': allocated_screens,
        'available_screens': available_screens,
        
        'total_keyboards': total_keyboards,
        'allocated_keyboards': allocated_keyboards,
        'available_keyboards': available_keyboards,
        
        'total_mice': total_mice,
        'allocated_mice': allocated_mice,
        'available_mice': available_mice,
        
        'total_headphones': total_headphones,
        'allocated_headphones': allocated_headphones,
        'available_headphones': available_headphones,
        
        'total_extenders': total_extenders,
        'allocated_extenders': allocated_extenders,
        'available_extenders': available_extenders,
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
    """API to add CPU device to inventory"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Parse JSON data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)
        
        # Validate required fields
        required_fields = ['cpu_company_name', 'cpu_processor', 'cpu_ram', 'cpu_storage', 'cpu_label_no']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'{field} is required', 'success': False}, status=400)
        
        # Check if label number already exists
        if CPUDevice.objects.filter(label_no=data['cpu_label_no']).exists():
            return JsonResponse({'error': 'CPU with this label number already exists', 'success': False}, status=400)
        
        # Create CPU device in inventory
        cpu_device = CPUDevice.objects.create(
            company_name=data['cpu_company_name'],
            processor=data['cpu_processor'],
            ram=data['cpu_ram'],
            storage=data['cpu_storage'],
            label_no=data['cpu_label_no'],
            mac_address=data.get('macaddress', ''),
            status='available',
            notes=data.get('notes', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'CPU added successfully to inventory',
            'id': cpu_device.id,
            'company_name': cpu_device.company_name,
            'label_no': cpu_device.label_no
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in add_device_cpu: {error_details}")  # Log to console
        return JsonResponse({'error': str(e), 'success': False}, status=400)


@login_required
def add_device_screen(request):
    """API to add screen device to inventory"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['screen_company_name', 'screen_size', 'screen_label_no']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'{field} is required'}, status=400)
        
        # Check if label number already exists
        if ScreenDevice.objects.filter(label_no=data['screen_label_no']).exists():
            return JsonResponse({'error': 'Screen with this label number already exists'}, status=400)
        
        # Create screen device in inventory
        screen_device = ScreenDevice.objects.create(
            company_name=data['screen_company_name'],
            size=data['screen_size'],
            label_no=data['screen_label_no'],
            status='available',
            notes=data.get('notes', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Screen added successfully to inventory',
            'id': screen_device.id,
            'company_name': screen_device.company_name,
            'label_no': screen_device.label_no
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def add_device_keyboard(request):
    """API to add keyboard device to inventory"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['keyboard_company_name', 'keyboard_label_no']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'{field} is required'}, status=400)
        
        # Check if label number already exists
        if KeyboardDevice.objects.filter(label_no=data['keyboard_label_no']).exists():
            return JsonResponse({'error': 'Keyboard with this label number already exists'}, status=400)
        
        # Create keyboard device in inventory
        keyboard_device = KeyboardDevice.objects.create(
            company_name=data['keyboard_company_name'],
            label_no=data['keyboard_label_no'],
            status='available',
            notes=data.get('notes', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Keyboard added successfully to inventory',
            'id': keyboard_device.id,
            'company_name': keyboard_device.company_name,
            'label_no': keyboard_device.label_no
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def add_device_mouse(request):
    """API to add mouse device to inventory"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['mouse_company_name', 'mouse_label_no']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'{field} is required'}, status=400)
        
        # Check if label number already exists
        if MouseDevice.objects.filter(label_no=data['mouse_label_no']).exists():
            return JsonResponse({'error': 'Mouse with this label number already exists'}, status=400)
        
        # Create mouse device in inventory
        mouse_device = MouseDevice.objects.create(
            company_name=data['mouse_company_name'],
            label_no=data['mouse_label_no'],
            status='available',
            notes=data.get('notes', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Mouse added successfully to inventory',
            'id': mouse_device.id,
            'company_name': mouse_device.company_name,
            'label_no': mouse_device.label_no
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def add_device_headphone(request):
    """API to add headphone device to inventory"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['headphone_company_name', 'headphone_label_no']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'{field} is required'}, status=400)
        
        # Check if label number already exists
        if HeadphoneDevice.objects.filter(label_no=data['headphone_label_no']).exists():
            return JsonResponse({'error': 'Headphone with this label number already exists'}, status=400)
        
        # Create headphone device in inventory
        headphone_device = HeadphoneDevice.objects.create(
            company_name=data['headphone_company_name'],
            label_no=data['headphone_label_no'],
            status='available',
            notes=data.get('notes', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Headphone added successfully to inventory',
            'id': headphone_device.id,
            'company_name': headphone_device.company_name,
            'label_no': headphone_device.label_no
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def add_device_extender(request):
    """API to add Extender device to inventory"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['extender_name', 'extender_label']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'{field} is required'}, status=400)
        
        # Check if label number already exists
        if ExtenderDevice.objects.filter(label_no=data['extender_label']).exists():
            return JsonResponse({'error': 'Extender with this label number already exists'}, status=400)
        
        # Create extender device in inventory
        extender_device = ExtenderDevice.objects.create(
            company_name=data['extender_name'],
            label_no=data['extender_label'],
            model=data.get('extender_model', ''),
            status='available',
            notes=data.get('notes', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Extender added successfully to inventory',
            'id': extender_device.id,
            'company_name': extender_device.company_name,
            'label_no': extender_device.label_no
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_cpu_systems(request):
    """API to get all CPU systems"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        cpus = CPUDevice.objects.all().values('company_name', 'processor', 'ram', 'storage', 'label_no', 'mac_address', 'status')
        cpu_list = list(cpus)
        
        return JsonResponse({
            'success': True,
            'systems': cpu_list
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_screen_systems(request):
    """API to get all Screen systems"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        screens = ScreenDevice.objects.all().values('company_name', 'size', 'label_no', 'status')
        screen_list = list(screens)
        
        return JsonResponse({
            'success': True,
            'systems': screen_list
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_keyboard_systems(request):
    """API to get all Keyboard systems"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        keyboards = KeyboardDevice.objects.all().values('company_name', 'label_no', 'status')
        keyboard_list = list(keyboards)
        
        return JsonResponse({
            'success': True,
            'systems': keyboard_list
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_mouse_systems(request):
    """API to get all Mouse systems"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        mice = MouseDevice.objects.all().values('company_name', 'label_no', 'status')
        mouse_list = list(mice)
        
        return JsonResponse({
            'success': True,
            'systems': mouse_list
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_headphone_systems(request):
    """API to get all Headphone systems"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        headphones = HeadphoneDevice.objects.all().values('company_name', 'label_no', 'status')
        headphone_list = list(headphones)
        
        return JsonResponse({
            'success': True,
            'systems': headphone_list
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_extender_systems(request):
    """API to get all Extender systems"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        extenders = ExtenderDevice.objects.all().values('company_name', 'model', 'label_no', 'status')
        extender_list = list(extenders)
        
        return JsonResponse({
            'success': True,
            'systems': extender_list
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

