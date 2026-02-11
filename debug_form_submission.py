#!/usr/bin/env python
"""
Debug script to check employee form submission issues
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from employees.models import Department, Designation
from employees.forms import EmployeeForm

def debug_form_submission():
    """Debug employee form submission issues"""
    
    print("🔍 Debugging Employee Form Submission")
    print("=" * 50)
    
    # Create a test client
    client = Client()
    staff_user = User.objects.get(username='teststaff')
    client.login(username='teststaff', password='staff123')
    
    # Get test data
    department = Department.objects.first()
    designation = Designation.objects.filter(department=department).first()
    
    if not department or not designation:
        print("❌ No test data available")
        return
    
    print(f"✅ Using department: {department.name} (ID: {department.id})")
    print(f"✅ Using designation: {designation.name} (ID: {designation.id})")
    
    # Test 1: Check form fields
    print("\n📝 Testing Form Fields:")
    url = reverse('employees:employee_add')
    response = client.get(url)
    
    if response.status_code == 200:
        print("✅ Form found in response")
        # Try to extract form errors from HTML content
        content = response.content.decode('utf-8')
        
        # Look for error indicators in the HTML
        if 'errorlist' in content or 'text-danger' in content:
            print("❌ Form validation errors found in HTML")
            # Extract error messages
            import re
            error_matches = re.findall(r'<ul class="errorlist">(.*?)</ul>', content, re.DOTALL)
            if error_matches:
                for match in error_matches:
                    print(f"   Error: {match.strip()}")
        else:
            print("❌ No obvious errors in HTML, checking for other issues...")
            
        # Check for specific patterns
        if 'field is required' in content:
            print("❌ Required field validation issue")
        if 'csrf' in content.lower() and 'token' in content.lower():
            print("❌ CSRF token issue detected")
        if 'Enter a valid' in content:
            print("❌ Validation error messages present")
    else:
        print(f"❌ Could not access form: {response.status_code}")
    
    # Test 2: Test form submission with minimal data
    print("\n📝 Testing Minimal Form Submission:")
    import random
    random_suffix = random.randint(1000, 9999)
    aadhar = f"12345678901{random_suffix % 10}"
    pan = f"ABCDE{random_suffix:04d}F"
    
    # Test with minimal required fields only
    minimal_data = {
        'full_name': f'Test Employee {random_suffix}',
        'department': department.id,
        'designation': designation.id,
        'joining_date': '2024-01-15',
        'employment_status': 'active',
        'mobile_number': f'987654321{random_suffix % 10}',
        'official_email': f'testemployee{random_suffix}@company.com',
        'date_of_birth': '1990-01-01',
        'marital_status': 'single',
        'highest_qualification': 'B.Tech',
        'aadhar_card_number': aadhar,
        'pan_card_number': pan,
        'nationality': 'Indian',
        'total_experience_years': 0,
        'total_experience_months': 0,
    }
    
    print("Submitting minimal form data...")
    response = client.post(url, data=minimal_data)
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 302:
        print("✅ Form submission successful (redirect)")
        # Check if employee was created
        email = f'testemployee{random_suffix}@company.com'
        from employees.models import Employee
        if Employee.objects.filter(official_email=email).exists():
            employee = Employee.objects.get(official_email=email)
            print(f"✅ Employee created: {employee.full_name} (ID: {employee.employee_code})")
            # Clean up
            employee.delete()
            print("✅ Test employee cleaned up")
        else:
            print("❌ Employee not found after submission")
            
    elif response.status_code == 200:
        print("❌ Form submission failed - form re-rendered")
        # Try to get form errors
        if hasattr(response, 'context') and response.context:
            form = response.context.get('form')
            if form and form.errors:
                print("❌ Form validation errors:")
                for field, errors in form.errors.items():
                    print(f"   {field}: {errors}")
            else:
                print("❌ No form errors found, but form was re-rendered")
        else:
            print("❌ No context available in response")
            
            # Check response content for clues
            content = response.content.decode('utf-8')
            if 'error' in content.lower():
                print("❌ Error indicators found in response content")
            if 'csrf' in content.lower():
                print("❌ CSRF token issue detected")
            if 'required' in content.lower():
                print("❌ Required field validation issue")
    else:
        print(f"❌ Unexpected response status: {response.status_code}")
    
    # Test 3: Check form validation directly
    print("\n📝 Testing Direct Form Validation:")
    form = EmployeeForm(data=minimal_data)
    if form.is_valid():
        print("✅ Form validation passed")
        print(f"Cleaned data: {form.cleaned_data}")
    else:
        print("❌ Form validation failed:")
        for field, errors in form.errors.items():
            print(f"   {field}: {errors}")
    
    # Test 4: Check model constraints
    print("\n📝 Testing Model Constraints:")
    from employees.models import Employee
    try:
        # Test creating employee directly
        employee = Employee.objects.create(
            full_name=f'Test Employee {random_suffix}',
            department=department,
            designation=designation,
            joining_date='2024-01-15',
            employment_status='active',
            mobile_number=f'987654321{random_suffix % 10}',
            official_email=f'testemployee{random_suffix}@company.com',
            date_of_birth='1990-01-01',
            marital_status='single',
            highest_qualification='B.Tech',
            aadhar_card_number=aadhar,
            pan_card_number=pan,
            nationality='Indian',
            total_experience_years=0,
            total_experience_months=0,
        )
        print(f"✅ Direct model creation successful: {employee.employee_code}")
        employee.delete()
        print("✅ Test employee cleaned up")
    except Exception as e:
        print(f"❌ Direct model creation failed: {e}")

if __name__ == "__main__":
    debug_form_submission()
