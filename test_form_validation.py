#!/usr/bin/env python
"""
Debug script to check form validation errors
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

def test_form_validation():
    """Test the employee form validation"""
    
    print("🔍 Testing Employee Form Validation")
    print("=" * 45)
    
    # Get test data
    department = Department.objects.first()
    designation = Designation.objects.filter(department=department).first()
    
    if not department or not designation:
        print("❌ No test data available")
        return
    
    print(f"✅ Using department: {department.name} (ID: {department.id})")
    print(f"✅ Using designation: {designation.name} (ID: {designation.id})")
    
    # Test form with valid data
    import random
    
    # Generate unique identifiers
    random_suffix = random.randint(1000, 9999)
    aadhar = f"12345678901{random_suffix % 10}"  # Keep it 12 digits
    pan = f"ABCDE{random_suffix:04d}F"  # Valid PAN format: 5 letters + 4 numbers + 1 letter
    
    print(f"Generated PAN: {pan} (length: {len(pan)})")
    print(f"Generated Aadhar: {aadhar} (length: {len(aadhar)})")
    
    form_data = {
        'full_name': f'Test Employee {random_suffix}',
        'department': department.id,
        'designation': designation.id,
        'joining_date': '2024-01-15',
        'employment_status': 'active',
        'mobile_number': f'987654321{random_suffix % 10}',
        'official_email': f'testemployee{random_suffix}@company.com',
        'local_address': 'Test Local Address',
        'permanent_address': 'Test Permanent Address',
        'date_of_birth': '1990-01-01',
        'marital_status': 'single',
        'highest_qualification': 'B.Tech',
        'aadhar_card_number': aadhar,
        'pan_card_number': pan,
        'nationality': 'Indian',
        'total_experience_years': 0,
        'total_experience_months': 0,
    }
    
    print("\n📝 Testing Form Validation:")
    
    # Test 1: Direct form validation
    print("\n1. Testing Direct Form Validation:")
    form = EmployeeForm(data=form_data)
    if form.is_valid():
        print("✅ Form is valid")
    else:
        print("❌ Form validation errors:")
        for field, errors in form.errors.items():
            print(f"   {field}: {errors}")
    
    # Test 2: Form submission via client
    print("\n2. Testing Form Submission via Client:")
    client = Client()
    staff_user = User.objects.get(username='teststaff')
    client.login(username='teststaff', password='staff123')
    
    url = reverse('employees:employee_add')
    response = client.post(url, data=form_data)
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 302:
        print("✅ Form submission successful (redirect)")
    elif response.status_code == 200:
        print("❌ Form submission failed - form re-rendered")
        # Try to extract form errors from the rendered response
        content = response.content.decode('utf-8')
        if 'error' in content.lower() or 'invalid' in content.lower():
            print("❌ Error indicators found in response content")
            # Look for common error patterns
            if 'field is required' in content.lower():
                print("   - Required field errors detected")
            if 'invalid' in content.lower():
                print("   - Invalid format errors detected")
        else:
            print("❌ No obvious error indicators in content")
    else:
        print(f"❌ Unexpected response status: {response.status_code}")
    
    # Test 3: Check required fields
    print("\n3. Testing Required Fields:")
    required_fields = ['full_name', 'department', 'designation', 'joining_date', 'mobile_number', 'official_email', 'date_of_birth', 'marital_status', 'highest_qualification', 'aadhar_card_number', 'pan_card_number']
    
    for field in required_fields:
        if field in form_data:
            print(f"✅ {field}: provided")
        else:
            print(f"❌ {field}: missing")

if __name__ == "__main__":
    test_form_validation()
