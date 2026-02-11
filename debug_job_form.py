#!/usr/bin/env python
"""
Debug script to check job form submission issues
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
from employees.forms_job import JobDescriptionForm

def debug_job_form_submission():
    """Debug job form submission issues"""
    
    print("🔍 Debugging Job Form Submission")
    print("=" * 45)
    
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
    print("\n📝 Testing Job Form Fields:")
    url = reverse('employees:job_create')
    response = client.get(url)
    
    if response.status_code == 200:
        print("✅ Job form found in response")
        content = response.content.decode('utf-8')
        
        if 'jobForm' in content:
            print("✅ Form element found")
        if 'csrfmiddlewaretoken' in content:
            print("✅ CSRF token present")
        if 'title' in content:
            print("✅ Title field found")
        if 'job_description' in content:
            print("✅ Job description field found")
    else:
        print(f"❌ Could not access job form: {response.status_code}")
    
    # Test 2: Test form submission with minimal data
    print("\n📝 Testing Job Form Submission:")
    import random
    random_suffix = random.randint(1000, 9999)
    
    # Test with minimal valid data
    job_data = {
        'title': f'Software Developer {random_suffix}',
        'department': department.id,
        'designation': designation.id,
        'job_description': f'We are looking for a skilled software developer to join our team. Position {random_suffix}',
        'requirements': 'Python\nDjango\nJavaScript\nSQL',
        'responsibilities': 'Develop web applications\nWrite clean code\nParticipate in code reviews',
        'employment_type': 'full_time',
        'experience_level': 'mid_level',
        'status': 'active',
        'location': 'Mumbai',
        'number_of_vacancies': 2,
        'min_salary': 500000,
        'max_salary': 800000,
        'application_deadline': '2024-12-31',
    }
    
    print("Submitting job form data...")
    response = client.post(url, data=job_data)
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 302:
        print("✅ Job form submission successful (redirect)")
        # Check if job was created
        from employees.models_job import JobDescription
        if JobDescription.objects.filter(title=f'Software Developer {random_suffix}').exists():
            job = JobDescription.objects.get(title=f'Software Developer {random_suffix}')
            print(f"✅ Job created: {job.title}")
            print(f"✅ Job ID: {job.id}")
            # Clean up
            job.delete()
            print("✅ Test job cleaned up")
        else:
            print("❌ Job not found after submission")
            
    elif response.status_code == 200:
        print("❌ Job submission failed - form re-rendered")
        # Try to get form errors
        content = response.content.decode('utf-8')
        
        # Look for error indicators in the HTML
        if 'errorlist' in content or 'text-danger' in content:
            print("❌ Form validation errors found in HTML")
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
        print(f"❌ Unexpected response status: {response.status_code}")
    
    # Test 3: Check form validation directly
    print("\n📝 Testing Direct Job Form Validation:")
    form = JobDescriptionForm(data=job_data)
    if form.is_valid():
        print("✅ Job form validation passed")
        print(f"Cleaned data keys: {list(form.cleaned_data.keys())}")
    else:
        print("❌ Job form validation failed:")
        for field, errors in form.errors.items():
            print(f"   {field}: {errors}")
    
    # Test 4: Check model constraints
    print("\n📝 Testing Job Model Constraints:")
    from employees.models_job import JobDescription
    try:
        # Test creating job directly
        job = JobDescription.objects.create(
            title=f'Test Job {random_suffix}',
            department=department,
            designation=designation,
            job_description=f'Test job description {random_suffix}',
            requirements='Test requirements',
            responsibilities='Test responsibilities',
            employment_type='full_time',
            experience_level='mid_level',
            status='active',
            location='Mumbai',
            number_of_vacancies=2,
            min_salary=500000,
            max_salary=800000,
            application_deadline='2024-12-31',
            posted_by=staff_user,
        )
        print(f"✅ Direct model creation successful: {job.title}")
        job.delete()
        print("✅ Test job cleaned up")
    except Exception as e:
        print(f"❌ Direct model creation failed: {e}")

if __name__ == "__main__":
    debug_job_form_submission()
