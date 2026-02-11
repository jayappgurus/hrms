"""
CSV Import/Export Views for Employees, Public Holidays, and Job Descriptions
"""
import csv
from io import TextIOWrapper
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from datetime import datetime
from decimal import Decimal

from .models import Employee, Department, Designation, PublicHoliday
from .models_job import JobDescription


# ==================== EMPLOYEE CSV EXPORT/IMPORT ====================

@login_required
def export_employees_csv(request):
    """Export all employees to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees_export.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Employee Code', 'Full Name', 'Department', 'Designation', 
        'Joining Date', 'Relieving Date', 'Employment Status',
        'Mobile Number', 'Official Email', 'Personal Email',
        'Local Address', 'Permanent Address',
        'Date of Birth', 'Marital Status', 'Anniversary Date',
        'Highest Qualification', 'Total Experience Years', 'Total Experience Months',
        'Probation Status', 'Aadhar Card Number', 'PAN Card Number',
        'Emergency Contact Name', 'Emergency Contact Mobile', 
        'Emergency Contact Email', 'Emergency Contact Address', 
        'Emergency Contact Relationship'
    ])
    
    # Write data
    employees = Employee.objects.select_related('department', 'designation').all()
    for emp in employees:
        writer.writerow([
            emp.employee_code,
            emp.full_name,
            emp.department.name,
            emp.designation.name,
            emp.joining_date.strftime('%Y-%m-%d') if emp.joining_date else '',
            emp.relieving_date.strftime('%Y-%m-%d') if emp.relieving_date else '',
            emp.employment_status,
            emp.mobile_number,
            emp.official_email,
            emp.personal_email or '',
            emp.local_address or '',
            emp.permanent_address or '',
            emp.date_of_birth.strftime('%Y-%m-%d') if emp.date_of_birth else '',
            emp.marital_status,
            emp.anniversary_date.strftime('%Y-%m-%d') if emp.anniversary_date else '',
            emp.highest_qualification,
            emp.total_experience_years,
            emp.total_experience_months,
            emp.probation_status,
            emp.aadhar_card_number,
            emp.pan_card_number,
            emp.emergency_contact_name or '',
            emp.emergency_contact_mobile or '',
            emp.emergency_contact_email or '',
            emp.emergency_contact_address or '',
            emp.emergency_contact_relationship or '',
        ])
    
    return response


@login_required
def download_employee_sample_csv(request):
    """Download sample CSV template for employee import"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employee_import_sample.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Employee Code', 'Full Name', 'Department', 'Designation', 
        'Joining Date', 'Relieving Date', 'Employment Status',
        'Mobile Number', 'Official Email', 'Personal Email',
        'Local Address', 'Permanent Address',
        'Date of Birth', 'Marital Status', 'Anniversary Date',
        'Highest Qualification', 'Total Experience Years', 'Total Experience Months',
        'Probation Status', 'Aadhar Card Number', 'PAN Card Number',
        'Emergency Contact Name', 'Emergency Contact Mobile', 
        'Emergency Contact Email', 'Emergency Contact Address', 
        'Emergency Contact Relationship'
    ])
    
    # Write sample data
    writer.writerow([
        'EMP001', 'John Doe', 'Engineering', 'Software Engineer',
        '2024-01-15', '', 'active',
        '9876543210', 'john.doe@company.com', 'john@personal.com',
        '123 Street, City', '456 Avenue, Town',
        '1990-05-15', 'married', '2015-06-20',
        'B.Tech Computer Science', '5', '6',
        'Confirmed', '123456789012', 'ABCDE1234F',
        'Jane Doe', '9876543211', 'jane@email.com', '789 Road, Village', 'Spouse'
    ])
    
    return response


@login_required
def import_employees_csv(request):
    """Import employees from CSV file"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid CSV file.')
            return redirect('employees:employee_list')
        
        try:
            # Read CSV file
            file_data = TextIOWrapper(csv_file.file, encoding='utf-8')
            csv_reader = csv.DictReader(file_data)
            
            success_count = 0
            error_count = 0
            errors = []
            
            with transaction.atomic():
                for row_num, row in enumerate(csv_reader, start=2):
                    try:
                        # Get or create department
                        dept_name = row.get('Department', '').strip()
                        if not dept_name:
                            raise ValueError("Department is required")
                        
                        department, _ = Department.objects.get_or_create(
                            name=dept_name,
                            defaults={'description': f'{dept_name} Department'}
                        )
                        
                        # Get or create designation
                        desig_name = row.get('Designation', '').strip()
                        if not desig_name:
                            raise ValueError("Designation is required")
                        
                        designation, _ = Designation.objects.get_or_create(
                            name=desig_name,
                            department=department,
                            defaults={'description': f'{desig_name} Position'}
                        )
                        
                        # Parse dates
                        joining_date = datetime.strptime(row.get('Joining Date', '').strip(), '%Y-%m-%d').date() if row.get('Joining Date', '').strip() else None
                        relieving_date = datetime.strptime(row.get('Relieving Date', '').strip(), '%Y-%m-%d').date() if row.get('Relieving Date', '').strip() else None
                        date_of_birth = datetime.strptime(row.get('Date of Birth', '').strip(), '%Y-%m-%d').date() if row.get('Date of Birth', '').strip() else None
                        anniversary_date = datetime.strptime(row.get('Anniversary Date', '').strip(), '%Y-%m-%d').date() if row.get('Anniversary Date', '').strip() else None
                        
                        # Create or update employee
                        employee_code = row.get('Employee Code', '').strip()
                        official_email = row.get('Official Email', '').strip()
                        
                        if not official_email:
                            raise ValueError("Official Email is required")
                        
                        employee, created = Employee.objects.update_or_create(
                            official_email=official_email,
                            defaults={
                                'employee_code': employee_code,
                                'full_name': row.get('Full Name', '').strip(),
                                'department': department,
                                'designation': designation,
                                'joining_date': joining_date,
                                'relieving_date': relieving_date,
                                'employment_status': row.get('Employment Status', 'active').strip(),
                                'mobile_number': row.get('Mobile Number', '').strip(),
                                'personal_email': row.get('Personal Email', '').strip() or None,
                                'local_address': row.get('Local Address', '').strip(),
                                'permanent_address': row.get('Permanent Address', '').strip(),
                                'date_of_birth': date_of_birth,
                                'marital_status': row.get('Marital Status', 'single').strip(),
                                'anniversary_date': anniversary_date,
                                'highest_qualification': row.get('Highest Qualification', '').strip(),
                                'total_experience_years': int(row.get('Total Experience Years', 0) or 0),
                                'total_experience_months': int(row.get('Total Experience Months', 0) or 0),
                                'probation_status': row.get('Probation Status', 'On Probation').strip(),
                                'aadhar_card_number': row.get('Aadhar Card Number', '').strip(),
                                'pan_card_number': row.get('PAN Card Number', '').strip().upper(),
                                'emergency_contact_name': row.get('Emergency Contact Name', '').strip(),
                                'emergency_contact_mobile': row.get('Emergency Contact Mobile', '').strip(),
                                'emergency_contact_email': row.get('Emergency Contact Email', '').strip(),
                                'emergency_contact_address': row.get('Emergency Contact Address', '').strip(),
                                'emergency_contact_relationship': row.get('Emergency Contact Relationship', '').strip(),
                            }
                        )
                        
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Row {row_num}: {str(e)}")
            
            # Show results
            if success_count > 0:
                messages.success(request, f'Successfully imported {success_count} employee(s).')
            
            if error_count > 0:
                error_msg = f'Failed to import {error_count} employee(s). Errors: ' + '; '.join(errors[:5])
                if len(errors) > 5:
                    error_msg += f' ... and {len(errors) - 5} more errors.'
                messages.error(request, error_msg)
            
        except Exception as e:
            messages.error(request, f'Error processing CSV file: {str(e)}')
        
        return redirect('employees:employee_list')
    
    return render(request, 'employees/import_csv.html', {'model_name': 'Employee'})


# ==================== PUBLIC HOLIDAY CSV EXPORT/IMPORT ====================

@login_required
def export_public_holidays_csv(request):
    """Export all public holidays to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="public_holidays_export.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow(['Name', 'Date', 'Day', 'Year', 'Is Active'])
    
    # Write data
    holidays = PublicHoliday.objects.all().order_by('date')
    for holiday in holidays:
        writer.writerow([
            holiday.name,
            holiday.date.strftime('%Y-%m-%d'),
            holiday.day,
            holiday.year,
            'Yes' if holiday.is_active else 'No'
        ])
    
    return response


@login_required
def download_public_holiday_sample_csv(request):
    """Download sample CSV template for public holiday import"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="public_holiday_import_sample.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow(['Name', 'Date', 'Year', 'Is Active'])
    
    # Write sample data
    writer.writerow(['Republic Day', '2026-01-26', '2026', 'Yes'])
    writer.writerow(['Independence Day', '2026-08-15', '2026', 'Yes'])
    writer.writerow(['Gandhi Jayanti', '2026-10-02', '2026', 'Yes'])
    writer.writerow(['Diwali', '2026-11-04', '2026', 'Yes'])
    writer.writerow(['Christmas', '2026-12-25', '2026', 'Yes'])
    
    return response


@login_required
def import_public_holidays_csv(request):
    """Import public holidays from CSV file"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid CSV file.')
            return redirect('employees:public_holidays')
        
        try:
            # Read CSV file
            file_data = TextIOWrapper(csv_file.file, encoding='utf-8')
            csv_reader = csv.DictReader(file_data)
            
            success_count = 0
            error_count = 0
            errors = []
            
            with transaction.atomic():
                for row_num, row in enumerate(csv_reader, start=2):
                    try:
                        # Parse date
                        date_str = row.get('Date', '').strip()
                        if not date_str:
                            raise ValueError("Date is required")
                        
                        holiday_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        
                        # Get day name from date
                        day_name = holiday_date.strftime('%A')
                        
                        # Parse is_active
                        is_active_str = row.get('Is Active', 'Yes').strip().lower()
                        is_active = is_active_str in ['yes', 'true', '1', 'active']
                        
                        # Create or update holiday
                        holiday, created = PublicHoliday.objects.update_or_create(
                            date=holiday_date,
                            defaults={
                                'name': row.get('Name', '').strip(),
                                'day': day_name,
                                'year': int(row.get('Year', holiday_date.year)),
                                'is_active': is_active
                            }
                        )
                        
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Row {row_num}: {str(e)}")
            
            # Show results
            if success_count > 0:
                messages.success(request, f'Successfully imported {success_count} public holiday(s).')
            
            if error_count > 0:
                error_msg = f'Failed to import {error_count} holiday(s). Errors: ' + '; '.join(errors[:5])
                if len(errors) > 5:
                    error_msg += f' ... and {len(errors) - 5} more errors.'
                messages.error(request, error_msg)
            
        except Exception as e:
            messages.error(request, f'Error processing CSV file: {str(e)}')
        
        return redirect('employees:public_holidays')
    
    return render(request, 'employees/import_csv.html', {'model_name': 'Public Holiday'})


# ==================== JOB DESCRIPTION CSV EXPORT/IMPORT ====================

@login_required
def export_job_descriptions_csv(request):
    """Export all job descriptions to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="job_descriptions_export.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Title', 'Department', 'Designation', 'Employment Type', 'Experience Level',
        'Job Description', 'Responsibilities', 'Requirements', 'Experience Criteria',
        'Min Salary', 'Max Salary', 'Currency', 'Location', 'Work Mode',
        'Travel Required', 'Number of Vacancies', 'Application Deadline',
        'Status', 'Is Featured', 'Is Urgent'
    ])
    
    # Write data
    jobs = JobDescription.objects.select_related('department', 'designation').all()
    for job in jobs:
        writer.writerow([
            job.title,
            job.department.name,
            job.designation.name,
            job.employment_type,
            job.experience_level,
            job.job_description,
            job.responsibilities,
            job.requirements,
            job.experience_criteria,
            str(job.min_salary) if job.min_salary else '',
            str(job.max_salary) if job.max_salary else '',
            job.currency,
            job.location,
            job.work_mode,
            'Yes' if job.travel_required else 'No',
            job.number_of_vacancies,
            job.application_deadline.strftime('%Y-%m-%d') if job.application_deadline else '',
            job.status,
            'Yes' if job.is_featured else 'No',
            'Yes' if job.is_urgent else 'No'
        ])
    
    return response


@login_required
def download_job_description_sample_csv(request):
    """Download sample CSV template for job description import"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="job_description_import_sample.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Title', 'Department', 'Designation', 'Employment Type', 'Experience Level',
        'Job Description', 'Responsibilities', 'Requirements', 'Experience Criteria',
        'Min Salary', 'Max Salary', 'Currency', 'Location', 'Work Mode',
        'Travel Required', 'Number of Vacancies', 'Application Deadline',
        'Status', 'Is Featured', 'Is Urgent'
    ])
    
    # Write sample data
    writer.writerow([
        'Senior Software Engineer',
        'Engineering',
        'Software Engineer',
        'full_time',
        'senior',
        'We are looking for an experienced software engineer to join our team.',
        'Design and develop software applications; Collaborate with team members; Code reviews',
        'Bachelor degree in CS; 5+ years experience; Python, Django, React',
        'Minimum 5 years in web development with Python and Django',
        '800000',
        '1200000',
        'INR',
        'Bangalore',
        'Hybrid',
        'No',
        '2',
        '2026-03-31',
        'active',
        'Yes',
        'No'
    ])
    
    return response


@login_required
def import_job_descriptions_csv(request):
    """Import job descriptions from CSV file"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid CSV file.')
            return redirect('employees:job_list')
        
        try:
            # Read CSV file
            file_data = TextIOWrapper(csv_file.file, encoding='utf-8')
            csv_reader = csv.DictReader(file_data)
            
            success_count = 0
            error_count = 0
            errors = []
            
            with transaction.atomic():
                for row_num, row in enumerate(csv_reader, start=2):
                    try:
                        # Get or create department
                        dept_name = row.get('Department', '').strip()
                        if not dept_name:
                            raise ValueError("Department is required")
                        
                        department, _ = Department.objects.get_or_create(
                            name=dept_name,
                            defaults={'description': f'{dept_name} Department'}
                        )
                        
                        # Get or create designation
                        desig_name = row.get('Designation', '').strip()
                        if not desig_name:
                            raise ValueError("Designation is required")
                        
                        designation, _ = Designation.objects.get_or_create(
                            name=desig_name,
                            department=department,
                            defaults={'description': f'{desig_name} Position'}
                        )
                        
                        # Parse dates
                        application_deadline = None
                        deadline_str = row.get('Application Deadline', '').strip()
                        if deadline_str:
                            application_deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
                        
                        # Parse boolean fields
                        travel_required = row.get('Travel Required', 'No').strip().lower() in ['yes', 'true', '1']
                        is_featured = row.get('Is Featured', 'No').strip().lower() in ['yes', 'true', '1']
                        is_urgent = row.get('Is Urgent', 'No').strip().lower() in ['yes', 'true', '1']
                        
                        # Parse salary
                        min_salary = None
                        max_salary = None
                        if row.get('Min Salary', '').strip():
                            min_salary = Decimal(row.get('Min Salary', '').strip())
                        if row.get('Max Salary', '').strip():
                            max_salary = Decimal(row.get('Max Salary', '').strip())
                        
                        # Create job description
                        job = JobDescription.objects.create(
                            title=row.get('Title', '').strip(),
                            department=department,
                            designation=designation,
                            employment_type=row.get('Employment Type', 'full_time').strip(),
                            experience_level=row.get('Experience Level', 'fresher').strip(),
                            job_description=row.get('Job Description', '').strip(),
                            responsibilities=row.get('Responsibilities', '').strip(),
                            requirements=row.get('Requirements', '').strip(),
                            experience_criteria=row.get('Experience Criteria', '').strip(),
                            min_salary=min_salary,
                            max_salary=max_salary,
                            currency=row.get('Currency', 'INR').strip(),
                            location=row.get('Location', '').strip(),
                            work_mode=row.get('Work Mode', 'Office').strip(),
                            travel_required=travel_required,
                            number_of_vacancies=int(row.get('Number of Vacancies', 1) or 1),
                            application_deadline=application_deadline,
                            status=row.get('Status', 'draft').strip(),
                            is_featured=is_featured,
                            is_urgent=is_urgent,
                            posted_by=request.user
                        )
                        
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Row {row_num}: {str(e)}")
            
            # Show results
            if success_count > 0:
                messages.success(request, f'Successfully imported {success_count} job description(s).')
            
            if error_count > 0:
                error_msg = f'Failed to import {error_count} job(s). Errors: ' + '; '.join(errors[:5])
                if len(errors) > 5:
                    error_msg += f' ... and {len(errors) - 5} more errors.'
                messages.error(request, error_msg)
            
        except Exception as e:
            messages.error(request, f'Error processing CSV file: {str(e)}')
        
        return redirect('employees:job_list')
    
    return render(request, 'employees/import_csv.html', {'model_name': 'Job Description'})
