#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import UserProfile, Department

print("=== HRMS PORTAL USER CREDENTIALS ===\n")

# Check existing users
users = User.objects.all()
print(f"Total users in system: {users.count()}")

print("\n=== EXISTING USER CREDENTIALS ===")
for user in users:
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Staff Status: {user.is_staff}")
    print(f"Superuser: {user.is_superuser}")
    
    # Try to get user profile
    try:
        profile = user.profile
        print(f"Role: {profile.role}")
        print(f"Department: {profile.department.name if profile.department else 'None'}")
    except UserProfile.DoesNotExist:
        print("Profile: Not created")
    
    print("-" * 40)

# Create test users if they don't exist
test_users = [
    {
        'username': 'admin',
        'password': 'admin123',
        'email': 'admin@hrms.com',
        'is_staff': True,
        'is_superuser': True,
        'role': 'admin'
    },
    {
        'username': 'hrmanager',
        'password': 'hr123',
        'email': 'hr@hrms.com',
        'is_staff': True,
        'is_superuser': False,
        'role': 'hr'
    },
    {
        'username': 'manager',
        'password': 'manager123',
        'email': 'manager@hrms.com',
        'is_staff': True,
        'is_superuser': False,
        'role': 'manager'
    },
    {
        'username': 'employee',
        'password': 'emp123',
        'email': 'employee@hrms.com',
        'is_staff': False,
        'is_superuser': False,
        'role': 'employee'
    },
    {
        'username': 'testuser',
        'password': 'test123',
        'email': 'test@hrms.com',
        'is_staff': False,
        'is_superuser': False,
        'role': 'employee'
    }
]

# Get or create HR department
hr_dept, created = Department.objects.get_or_create(
    name='Human Resources',
    defaults={'description': 'HR Department'}
)

it_dept, created = Department.objects.get_or_create(
    name='IT Department',
    defaults={'description': 'IT Department'}
)

print("\n=== CREATING/UPDATING TEST USERS ===")
for user_data in test_users:
    user, created = User.objects.get_or_create(
        username=user_data['username'],
        defaults={
            'email': user_data['email'],
            'is_staff': user_data['is_staff'],
            'is_superuser': user_data['is_superuser']
        }
    )
    
    if created:
        user.set_password(user_data['password'])
        user.save()
        print(f"✅ Created new user: {user.username}")
    else:
        # Update password for existing users
        user.set_password(user_data['password'])
        user.save()
        print(f"🔄 Updated password for: {user.username}")
    
    # Create or update user profile
    try:
        profile = user.profile
        profile.role = user_data['role']
        if user_data['role'] == 'hr':
            profile.department = hr_dept
        elif user_data['role'] == 'manager':
            profile.department = it_dept
        elif user_data['role'] == 'admin':
            profile.department = hr_dept
        else:
            profile.department = it_dept
        profile.save()
        print(f"   📋 Updated profile for: {user.username} (Role: {profile.role})")
    except UserProfile.DoesNotExist:
        # Create new profile
        dept = hr_dept if user_data['role'] in ['hr', 'admin'] else it_dept
        UserProfile.objects.create(
            user=user,
            role=user_data['role'],
            department=dept
        )
        print(f"   📋 Created profile for: {user.username} (Role: {user_data['role']})")

print("\n=== LOGIN CREDENTIALS FOR TESTING ===")
print("You can use any of these credentials to login:")
print("\n🔑 ADMIN ACCESS:")
print("   Username: admin")
print("   Password: admin123")
print("   Role: Administrator (Full access)")

print("\n👥 HR MANAGER:")
print("   Username: hrmanager")
print("   Password: hr123")
print("   Role: HR Manager")

print("\n📊 DEPARTMENT MANAGER:")
print("   Username: manager")
print("   Password: manager123")
print("   Role: Manager")

print("\n👤 EMPLOYEE:")
print("   Username: employee")
print("   Password: emp123")
print("   Role: Employee")

print("\n🧪 TEST USER:")
print("   Username: testuser")
print("   Password: test123")
print("   Role: Employee")

print("\n🌐 LOGIN URL:")
print("   http://127.0.0.1:8000/accounts/login/")
print("\n" + "="*50)
