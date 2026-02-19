from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Employee, Department, Designation, EmergencyContact, EmployeeDocument, Device, UserProfile
from django.contrib.auth.models import User


@login_required
def api_available_devices(request, device_type):
    """API endpoint to get available devices by type"""
    if not request.user.is_superuser and not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        devices = Device.objects.filter(
            device_type=device_type,
            status='available'
        ).values('id', 'device_name', 'serial_number')
        
        return JsonResponse({
            'devices': list(devices)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_employees_list(request):
    """API endpoint to get all employees with optional filtering and pagination"""
    # Check permissions - only admin, director, HR can view all employees
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile or not user_profile.can_view_all_employees:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        search = request.GET.get('search', '')
        department = request.GET.get('department', '')
        status = request.GET.get('status', '')
        
        # Build queryset
        queryset = Employee.objects.select_related(
            'department', 'designation', 'emergency_contact'
        ).prefetch_related('documents')
        
        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(employee_code__icontains=search) |
                Q(official_email__icontains=search) |
                Q(mobile_number__icontains=search)
            )
        
        if department:
            queryset = queryset.filter(department__name__icontains=department)
        
        if status:
            queryset = queryset.filter(employment_status=status)
        
        # Pagination
        paginator = Paginator(queryset, page_size)
        employees_page = paginator.get_page(page)
        
        # Serialize employees
        employees_data = []
        for emp in employees_page:
            employee_data = {
                'id': emp.id,
                'employee_code': emp.employee_code,
                'full_name': emp.full_name,
                'profile_picture': emp.profile_picture.url if emp.profile_picture else None,
                'department': {
                    'id': emp.department.id,
                    'name': emp.department.name
                } if emp.department else None,
                'designation': {
                    'id': emp.designation.id,
                    'name': emp.designation.name
                } if emp.designation else None,
                'joining_date': emp.joining_date.isoformat() if emp.joining_date else None,
                'employment_status': emp.employment_status,
                'current_ctc': float(emp.current_ctc),
                'official_email': emp.official_email,
                'mobile_number': emp.mobile_number,
                'date_of_birth': emp.date_of_birth.isoformat() if emp.date_of_birth else None,
                'age': emp.age,
                'marital_status': emp.marital_status,
                'highest_qualification': emp.highest_qualification,
                'total_experience_display': emp.total_experience_display,
                'period_type': emp.period_type,
                'aadhar_card_number': emp.aadhar_card_number,
                'pan_card_number': emp.pan_card_number,
                'local_address': emp.local_address,
                'permanent_address': emp.permanent_address,
                'emergency_contact': {
                    'name': emp.emergency_contact.name,
                    'mobile_number': emp.emergency_contact.mobile_number,
                    'email': emp.emergency_contact.email,
                    'relationship': emp.emergency_contact.relationship
                } if emp.emergency_contact else None,
                'direct_emergency_contact': {
                    'name': emp.emergency_contact_name,
                    'mobile_number': emp.emergency_contact_mobile,
                    'email': emp.emergency_contact_email,
                    'relationship': emp.emergency_contact_relationship
                } if emp.emergency_contact_name else None,
                'salary_components': emp.salary_components,
                'created_at': emp.created_at.isoformat(),
                'updated_at': emp.updated_at.isoformat()
            }
            employees_data.append(employee_data)
        
        return JsonResponse({
            'employees': employees_data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': employees_page.has_next(),
                'has_previous': employees_page.has_previous()
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_employee_detail(request, employee_id):
    """API endpoint to get detailed information for a specific employee"""
    # Check permissions
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Allow viewing own profile or if user can view all employees
    can_view = (user_profile.can_view_all_employees or 
                (user_profile.employee and user_profile.employee.id == employee_id))
    
    if not can_view:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        employee = get_object_or_404(
            Employee.objects.select_related(
                'department', 'designation', 'emergency_contact'
            ).prefetch_related('documents', 'leave_applications', 'device_allocations', 'evaluations'),
            id=employee_id
        )
        
        # Get user profile information
        user_profile_info = None
        if hasattr(employee, 'user_profile'):
            user_profile_info = {
                'user_id': employee.user_profile.user.id,
                'username': employee.user_profile.user.username,
                'email': employee.user_profile.user.email,
                'first_name': employee.user_profile.user.first_name,
                'last_name': employee.user_profile.user.last_name,
                'role': employee.user_profile.role,
                'phone': employee.user_profile.phone,
                'is_active': employee.user_profile.user.is_active,
                'date_joined': employee.user_profile.user.date_joined.isoformat(),
                'last_login': employee.user_profile.user.last_login.isoformat() if employee.user_profile.user.last_login else None
            }
        
        # Serialize documents
        documents_data = []
        for doc in employee.documents.all():
            documents_data.append({
                'id': doc.id,
                'document_type': doc.document_type,
                'document_type_display': doc.get_document_type_display(),
                'document_file': doc.document_file.url if doc.document_file else None,
                'is_submitted': doc.is_submitted,
                'submitted_date': doc.submitted_date.isoformat() if doc.submitted_date else None,
                'remarks': doc.remarks
            })
        
        # Serialize recent leave applications
        leave_applications_data = []
        for leave in employee.leave_applications.select_related('leave_type').order_by('-created_at')[:10]:
            leave_applications_data.append({
                'id': leave.id,
                'leave_type': leave.leave_type.name,
                'start_date': leave.start_date.isoformat(),
                'end_date': leave.end_date.isoformat(),
                'total_days': float(leave.total_days),
                'status': leave.status,
                'reason': leave.reason[:100] + '...' if len(leave.reason) > 100 else leave.reason,
                'created_at': leave.created_at.isoformat()
            })
        
        # Serialize device allocations
        device_allocations_data = []
        for allocation in employee.device_allocations.select_related('device').order_by('-assigned_date'):
            device_allocations_data.append({
                'id': allocation.id,
                'device': {
                    'id': allocation.device.id,
                    'device_name': allocation.device.device_name,
                    'device_type': allocation.device.device_type,
                    'serial_number': allocation.device.serial_number
                },
                'assigned_date': allocation.assigned_date.isoformat(),
                'returned_date': allocation.returned_date.isoformat() if allocation.returned_date else None,
                'is_active': allocation.is_active,
                'return_notes': allocation.return_notes
            })
        
        # Serialize performance evaluations
        evaluations_data = []
        for evaluation in employee.evaluations.order_by('-cycle_number')[:5]:
            evaluations_data.append({
                'id': evaluation.id,
                'cycle_number': evaluation.cycle_number,
                'overall_rating': evaluation.overall_rating,
                'status': evaluation.status,
                'evaluation_date': evaluation.evaluation_date.isoformat() if evaluation.evaluation_date else None,
                'created_at': evaluation.created_at.isoformat()
            })
        
        # Compile complete employee data
        employee_data = {
            'id': employee.id,
            'employee_code': employee.employee_code,
            'full_name': employee.full_name,
            'profile_picture': employee.profile_picture.url if employee.profile_picture else None,
            'department': {
                'id': employee.department.id,
                'name': employee.department.name,
                'description': employee.department.description
            } if employee.department else None,
            'designation': {
                'id': employee.designation.id,
                'name': employee.designation.name,
                'description': employee.designation.description
            } if employee.designation else None,
            'joining_date': employee.joining_date.isoformat(),
            'probation_end_date': employee.probation_end_date.isoformat() if employee.probation_end_date else None,
            'relieving_date': employee.relieving_date.isoformat() if employee.relieving_date else None,
            'employment_status': employee.employment_status,
            'current_ctc': float(employee.current_ctc),
            'salary_structure': employee.salary_structure,
            'contact_info': {
                'official_email': employee.official_email,
                'personal_email': employee.personal_email,
                'mobile_number': employee.mobile_number,
                'local_address': employee.local_address,
                'permanent_address': employee.permanent_address
            },
            'personal_info': {
                'date_of_birth': employee.date_of_birth.isoformat(),
                'age': employee.age,
                'marital_status': employee.marital_status,
                'anniversary_date': employee.anniversary_date.isoformat() if employee.anniversary_date else None
            },
            'professional_info': {
                'highest_qualification': employee.highest_qualification,
                'total_experience_years': employee.total_experience_years,
                'total_experience_months': employee.total_experience_months,
                'total_experience_display': employee.total_experience_display,
                'period_type': employee.period_type
            },
            'identity_info': {
                'aadhar_card_number': employee.aadhar_card_number,
                'pan_card_number': employee.pan_card_number
            },
            'emergency_contact': {
                'name': employee.emergency_contact.name,
                'mobile_number': employee.emergency_contact.mobile_number,
                'email': employee.emergency_contact.email,
                'address': employee.emergency_contact.address,
                'relationship': employee.emergency_contact.relationship
            } if employee.emergency_contact else None,
            'direct_emergency_contact': {
                'name': employee.emergency_contact_name,
                'mobile_number': employee.emergency_contact_mobile,
                'email': employee.emergency_contact_email,
                'address': employee.emergency_contact_address,
                'relationship': employee.emergency_contact_relationship
            } if employee.emergency_contact_name else None,
            'salary_components': employee.salary_components,
            'user_profile': user_profile_info,
            'documents': documents_data,
            'recent_leave_applications': leave_applications_data,
            'device_allocations': device_allocations_data,
            'performance_evaluations': evaluations_data,
            'created_at': employee.created_at.isoformat(),
            'updated_at': employee.updated_at.isoformat()
        }
        
        return JsonResponse(employee_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_departments(request):
    """API endpoint to get all departments"""
    try:
        departments = Department.objects.select_related('head').all()
        departments_data = []
        
        for dept in departments:
            dept_data = {
                'id': dept.id,
                'name': dept.name,
                'description': dept.description,
                'head': {
                    'id': dept.head.id,
                    'full_name': dept.head.full_name,
                    'employee_code': dept.head.employee_code
                } if dept.head else None,
                'employee_count': dept.employees.count(),
                'created_at': dept.created_at.isoformat(),
                'updated_at': dept.updated_at.isoformat()
            }
            departments_data.append(dept_data)
        
        return JsonResponse({'departments': departments_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_designations(request):
    """API endpoint to get all designations with optional department filter"""
    try:
        department_id = request.GET.get('department_id')
        
        if department_id:
            designations = Designation.objects.filter(department_id=department_id)
        else:
            designations = Designation.objects.select_related('department').all()
        
        designations_data = []
        
        for designation in designations:
            designation_data = {
                'id': designation.id,
                'name': designation.name,
                'description': designation.description,
                'department': {
                    'id': designation.department.id,
                    'name': designation.department.name
                } if designation.department else None,
                'employee_count': designation.employees.count(),
                'created_at': designation.created_at.isoformat(),
                'updated_at': designation.updated_at.isoformat()
            }
            designations_data.append(designation_data)
        
        return JsonResponse({'designations': designations_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_employee_stats(request):
    """API endpoint to get employee statistics"""
    # Check permissions
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile or not user_profile.can_view_all_employees:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(employment_status='active').count()
        inactive_employees = total_employees - active_employees
        
        # Department-wise counts
        dept_stats = []
        departments = Department.objects.annotate(employee_count=Count('employees'))
        for dept in departments:
            dept_stats.append({
                'department': dept.name,
                'employee_count': dept.employee_count
            })
        
        # Employment status breakdown
        status_stats = Employee.objects.values('employment_status').annotate(
            count=Count('id')
        ).order_by('employment_status')
        
        # Period type breakdown
        period_stats = Employee.objects.values('period_type').annotate(
            count=Count('id')
        ).order_by('period_type')
        
        stats_data = {
            'total_employees': total_employees,
            'active_employees': active_employees,
            'inactive_employees': inactive_employees,
            'department_breakdown': dept_stats,
            'status_breakdown': list(status_stats),
            'period_type_breakdown': list(period_stats)
        }
        
        return JsonResponse(stats_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
