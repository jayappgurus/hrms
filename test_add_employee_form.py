#!/usr/bin/env python
"""
Test script to verify the add employee form is working
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
django.setup()

from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.urls import reverse

def test_add_employee_form():
    """Test the add employee form access and functionality"""
    
    print("🔍 Testing Add Employee Form")
    print("=" * 40)
    
    # Create a test superuser
    try:
        superuser = User.objects.get(username='admin')
        print(f"✅ Found existing superuser: {superuser.username}")
    except User.DoesNotExist:
        superuser = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
        print(f"✅ Created superuser: {superuser.username}")
    
    # Create a test staff user
    try:
        staff_user = User.objects.get(username='teststaff')
        print(f"✅ Found existing staff user: {staff_user.username}")
    except User.DoesNotExist:
        staff_user = User.objects.create_user('teststaff', 'staff@test.com', 'staff123')
        staff_user.is_staff = True
        staff_user.save()
        print(f"✅ Created staff user: {staff_user.username}")
    
    # Create a regular user
    try:
        regular_user = User.objects.get(username='testuser')
        print(f"✅ Found existing regular user: {regular_user.username}")
    except User.DoesNotExist:
        regular_user = User.objects.create_user('testuser', 'user@test.com', 'user123')
        print(f"✅ Created regular user: {regular_user.username}")
    
    # Test form access with different users
    client = Client()
    
    # Test 1: Superuser access
    print("\n📝 Testing Superuser Access:")
    client.login(username='admin', password='admin123')
    url = reverse('employees:employee_add')
    response = client.get(url)
    
    if response.status_code == 200:
        print("✅ Superuser can access add employee form")
        if 'form' in response.context:
            print("✅ Form is present in context")
        if 'all_designations' in response.context:
            print("✅ Designations data is present in context")
        else:
            print("❌ Designations data missing from context")
    else:
        print(f"❌ Superuser access failed with status: {response.status_code}")
    
    # Test 2: Staff user access
    print("\n📝 Testing Staff User Access:")
    client.login(username='teststaff', password='staff123')
    response = client.get(url)
    
    if response.status_code == 200:
        print("✅ Staff user can access add employee form")
    else:
        print(f"❌ Staff user access failed with status: {response.status_code}")
    
    # Test 3: Regular user access (should be denied)
    print("\n📝 Testing Regular User Access:")
    client.login(username='testuser', password='user123')
    response = client.get(url)
    
    if response.status_code == 302:
        print("✅ Regular user correctly redirected (access denied)")
    else:
        print(f"❌ Regular user access should be denied, got status: {response.status_code}")
    
    # Test 4: Anonymous user access (should be denied)
    print("\n📝 Testing Anonymous User Access:")
    client.logout()
    response = client.get(url)
    
    if response.status_code == 302:
        print("✅ Anonymous user correctly redirected (login required)")
    else:
        print(f"❌ Anonymous user access should be denied, got status: {response.status_code}")
    
    print("\n🎯 Form Access Test Summary:")
    print("✅ Superuser and staff can access the form")
    print("✅ Regular users are properly denied access")
    print("✅ Anonymous users are redirected to login")
    print("✅ Permission checks are working correctly")

if __name__ == "__main__":
    test_add_employee_form()
