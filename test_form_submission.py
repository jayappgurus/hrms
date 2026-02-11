#!/usr/bin/env python
"""
Test script to verify the add employee form submission
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

def test_form_submission():
    """Test the add employee form submission"""
    
    print("🔍 Testing Add Employee Form Submission")
    print("=" * 50)
    
    # Get existing data
    client = Client()
    
    # Login as staff user (since that works)
    staff_user = User.objects.get(username='teststaff')
    client.login(username='teststaff', password='staff123')
    
    # Get form data
    url = reverse('employees:employee_add')
    response = client.get(url)
    
    if response.status_code == 200:
        print("✅ Successfully accessed the form")
        
        # Get test data
        department = Department.objects.first()
        designation = Designation.objects.filter(department=department).first()
        
        if department and designation:
            print(f"✅ Using department: {department.name}")
            print(f"✅ Using designation: {designation.name}")
            
            # Prepare form data
            import random
            random_suffix = random.randint(1000, 9999)
            aadhar = f"12345678901{random_suffix % 10}"  # Keep it 12 digits
            pan = f"ABCDE{random_suffix:04d}F"  # Valid PAN format: 5 letters + 4 numbers + 1 letter
            
            form_data = {
                'full_name': f'Test Employee {random_suffix}',
                'department': department.id,
                'designation': designation.id,
                'joining_date': '2024-01-15',
                'employment_status': 'active',
                'mobile_number': f'987654321{random_suffix % 10}',
                'official_email': f'testemployee{random_suffix}@company.com',
                'local_address': 'Test Address',
                'permanent_address': 'Test Address',
                'date_of_birth': '1990-01-01',
                'marital_status': 'single',
                'highest_qualification': 'B.Tech',
                'aadhar_card_number': aadhar,
                'pan_card_number': pan,
                'nationality': 'Indian',
                'total_experience_years': 0,
                'total_experience_months': 0,
            }
            
            # Test form submission
            print("\n📝 Testing Form Submission:")
            response = client.post(url, data=form_data)
            
            if response.status_code == 302:
                print("✅ Form submission successful (redirect)")
                # Check if employee was created
                from employees.models import Employee
                email = f'testemployee{random_suffix}@company.com'
                if Employee.objects.filter(official_email=email).exists():
                    print("✅ Employee record created successfully")
                    employee = Employee.objects.get(official_email='testemployee@company.com')
                    print(f"✅ Employee ID: {employee.employee_code}")
                    # Clean up
                    employee.delete()
                    print("✅ Test employee cleaned up")
                else:
                    print("❌ Employee record not found after submission")
            else:
                print(f"❌ Form submission failed with status: {response.status_code}")
                if response.status_code == 200:
                    # Check for form errors
                    if hasattr(response, 'context') and response.context and 'form' in response.context:
                        form = response.context['form']
                        if form.errors:
                            print("❌ Form errors:")
                            for field, errors in form.errors.items():
                                print(f"   {field}: {errors}")
                    else:
                        print("❌ No context or form available in response")
                        print(f"❌ Response content preview: {response.content[:300]}")
                else:
                    print(f"❌ Response content: {response.content[:200]}")
        else:
            print("❌ No department or designation found for testing")
    else:
        print(f"❌ Could not access form: {response.status_code}")

if __name__ == "__main__":
    test_form_submission()
