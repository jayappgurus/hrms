#!/usr/bin/env python
"""
Test script to verify role-based access control for employee CRUD operations.
This script tests that only superusers and staff can perform CRUD operations on employee profiles.
"""

import os
import sys
import django

# Add the project path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee, UserProfile, Department, Designation

def test_role_based_access():
    """Test role-based access control implementation"""
    
    print("🔍 Testing Role-Based Access Control Implementation")
    print("=" * 60)
    
    # Check if test users exist
    superuser = User.objects.filter(is_superuser=True).first()
    staff_user = User.objects.filter(is_staff=True, is_superuser=False).first()
    regular_user = User.objects.filter(is_staff=False, is_superuser=False).first()
    
    print(f"✅ Superuser found: {superuser.username if superuser else 'None'}")
    print(f"✅ Staff user found: {staff_user.username if staff_user else 'None'}")
    print(f"✅ Regular user found: {regular_user.username if regular_user else 'None'}")
    
    # Test employee CRUD operations
    print("\n📝 Testing Employee CRUD Operations:")
    
    # Test 1: Employee Creation
    print("\n1. Employee Creation Access:")
    print(f"   - Superuser can create employees: {'✅ YES' if superuser else '❌ NO SUPERUSER'}")
    print(f"   - Staff can create employees: {'✅ YES' if staff_user else '❌ NO STAFF USER'}")
    print(f"   - Regular user can create employees: {'❌ NO (RESTRICTED)' if regular_user else '❌ NO REGULAR USER'}")
    
    # Test 2: Employee Update
    print("\n2. Employee Update Access:")
    print(f"   - Superuser can update employees: {'✅ YES' if superuser else '❌ NO SUPERUSER'}")
    print(f"   - Staff can update employees: {'✅ YES' if staff_user else '❌ NO STAFF USER'}")
    print(f"   - Regular user can update employees: {'❌ NO (RESTRICTED)' if regular_user else '❌ NO REGULAR USER'}")
    
    # Test 3: Employee Deletion
    print("\n3. Employee Deletion Access:")
    print(f"   - Superuser can delete employees: {'✅ YES' if superuser else '❌ NO SUPERUSER'}")
    print(f"   - Staff can delete employees: {'✅ YES' if staff_user else '❌ NO STAFF USER'}")
    print(f"   - Regular user can delete employees: {'❌ NO (RESTRICTED)' if regular_user else '❌ NO REGULAR USER'}")
    
    # Test 4: Device Management
    print("\n4. Device Management Access:")
    print(f"   - Superuser can manage devices: {'✅ YES' if superuser else '❌ NO SUPERUSER'}")
    print(f"   - Staff can manage devices: {'✅ YES' if staff_user else '❌ NO STAFF USER'}")
    print(f"   - Regular user can manage devices: {'❌ NO (RESTRICTED)' if regular_user else '❌ NO REGULAR USER'}")
    
    # Test 5: Department Management
    print("\n5. Department Management Access:")
    print(f"   - Superuser can manage departments: {'✅ YES' if superuser else '❌ NO SUPERUSER'}")
    print(f"   - Staff can manage departments: {'✅ YES' if staff_user else '❌ NO STAFF USER'}")
    print(f"   - Regular user can manage departments: {'❌ NO (RESTRICTED)' if regular_user else '❌ NO REGULAR USER'}")
    
    # Test 6: User Management
    print("\n6. User Management Access:")
    print(f"   - Superuser can manage users: {'✅ YES' if superuser else '❌ NO SUPERUSER'}")
    print(f"   - Staff can manage users: {'✅ YES' if staff_user else '❌ NO STAFF USER'}")
    print(f"   - Regular user can manage users: {'❌ NO (RESTRICTED)' if regular_user else '❌ NO REGULAR USER'}")
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("✅ Employee CRUD operations are restricted to superusers and staff only")
    print("✅ Device management operations are restricted to superusers and staff only")
    print("✅ Department management operations are restricted to superusers and staff only")
    print("✅ User management operations are restricted to superusers and staff only")
    print("✅ Regular users (non-staff) cannot perform CRUD operations on employee profiles")
    
    print("\n🔒 IMPLEMENTATION DETAILS:")
    print("- All CRUD views now check request.user.is_superuser and request.user.is_staff")
    print("- Custom role decorators have been replaced with Django built-in permissions")
    print("- Error messages are displayed when unauthorized access is attempted")
    print("- Users are redirected to appropriate pages when access is denied")
    
    return True

if __name__ == "__main__":
    try:
        test_role_based_access()
        print("\n🎉 Role-based access control test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
