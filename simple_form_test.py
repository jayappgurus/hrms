#!/usr/bin/env python
"""
Simple test to check form submission step by step
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

def simple_form_test():
    """Simple test to debug form submission"""
    
    print("🔍 Simple Form Test")
    print("=" * 30)
    
    client = Client()
    staff_user = User.objects.get(username='teststaff')
    client.login(username='teststaff', password='staff123')
    
    # Get form page
    url = reverse('employees:employee_add')
    response = client.get(url)
    
    print(f"Form page status: {response.status_code}")
    
    # Check if form is in context
    if hasattr(response, 'context') and response.context:
        form = response.context.get('form')
        if form:
            print("✅ Form found in context")
            
            # Get department and designation
            department = Department.objects.first()
            designation = Designation.objects.filter(department=department).first()
            
            # Create minimal valid data
            import random
            random_suffix = random.randint(1000, 9999)
            aadhar = f"12345678901{random_suffix % 10}"
            pan = f"ABCDE{random_suffix:04d}F"
            
            form_data = {
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
            
            print(f"Submitting data for: {form_data['full_name']}")
            
            # Submit form
            response = client.post(url, data=form_data)
            print(f"Submission response: {response.status_code}")
            
            if response.status_code == 200:
                print("Form was re-rendered. Checking for errors...")
                
                # Check response content for specific error patterns
                content = response.content.decode('utf-8')
                
                if 'This field is required' in content:
                    print("❌ Required field error found")
                    # Find which field
                    import re
                    required_errors = re.findall(r'<li>([^<]+?)</li>', content)
                    for error in required_errors:
                        print(f"   Required field: {error}")
                
                if 'already exists' in content:
                    print("❌ Unique constraint violation")
                
                if 'Enter a valid' in content:
                    print("❌ Validation format error")
                    
            elif response.status_code == 302:
                print("✅ Form submitted successfully!")
                
                # Check if employee was created
                email = f'testemployee{random_suffix}@company.com'
                from employees.models import Employee
                if Employee.objects.filter(official_email=email).exists():
                    print("✅ Employee found in database")
                else:
                    print("❌ Employee not found in database")
            else:
                print(f"❌ Unexpected response: {response.status_code}")
        else:
            print("❌ No form in context")
    else:
        print("❌ No context in response")

if __name__ == "__main__":
    simple_form_test()
