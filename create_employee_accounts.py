#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Department, Designation, Employee, UserProfile

print("=== CREATE EMPLOYEE ACCOUNTS ===\n")

# Employee data to create
employees_data = [
    {
        'username': 'john.doe',
        'password': 'password123',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@company.com',
        'department': 'IT Department',
        'designation': 'Software Developer',
        'role': 'employee'
    },
    {
        'username': 'jane.smith',
        'password': 'password123',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'email': 'jane.smith@company.com',
        'department': 'Human Resources',
        'designation': 'HR Executive',
        'role': 'employee'
    },
    {
        'username': 'mike.wilson',
        'password': 'password123',
        'first_name': 'Mike',
        'last_name': 'Wilson',
        'email': 'mike.wilson@company.com',
        'department': 'Finance Department',
        'designation': 'Accountant',
        'role': 'employee'
    },
    {
        'username': 'sarah.jones',
        'password': 'password123',
        'first_name': 'Sarah',
        'last_name': 'Jones',
        'email': 'sarah.jones@company.com',
        'department': 'Marketing Department',
        'designation': 'Marketing Manager',
        'role': 'employee'
    },
    {
        'username': 'david.brown',
        'password': 'password123',
        'first_name': 'David',
        'last_name': 'Brown',
        'email': 'david.brown@company.com',
        'department': 'Sales Department',
        'designation': 'Sales Executive',
        'role': 'employee'
    }
]

print("Creating employee accounts...")

for emp_data in employees_data:
    try:
        # Check if user already exists
        if User.objects.filter(username=emp_data['username']).exists():
            print(f"📋 User '{emp_data['username']}' already exists")
            continue
        
        # Create user
        user = User.objects.create_user(
            username=emp_data['username'],
            password=emp_data['password'],
            first_name=emp_data['first_name'],
            last_name=emp_data['last_name'],
            email=emp_data['email']
        )
        
        # Get department and designation
        try:
            department = Department.objects.get(name=emp_data['department'])
            designation = Designation.objects.get(name=emp_data['designation'], department=department)
        except (Department.DoesNotExist, Designation.DoesNotExist):
            print(f"❌ Department or designation not found for {emp_data['username']}")
            user.delete()
            continue
        
        # Create employee
        employee = Employee.objects.create(
            user=user,
            employee_code=f"EMP{str(user.id).zfill(4)}",
            full_name=f"{emp_data['first_name']} {emp_data['last_name']}",
            department=department,
            designation=designation,
            official_email=emp_data['email'],
            employment_status='active',
            joining_date='2024-01-01'
        )
        
        # Create user profile
        profile = UserProfile.objects.create(
            user=user,
            role=emp_data['role'],
            department=department
        )
        
        print(f"✅ Created employee: {emp_data['username']} ({emp_data['department']} - {emp_data['designation']})")
        
    except Exception as e:
        print(f"❌ Error creating {emp_data['username']}: {e}")

print(f"\n=== LOGIN CREDENTIALS ===")
print("Use these credentials to login:")
for emp_data in employees_data:
    print(f"\n👤 {emp_data['first_name']} {emp_data['last_name']}")
    print(f"   Username: {emp_data['username']}")
    print(f"   Password: {emp_data['password']}")
    print(f"   Department: {emp_data['department']}")
    print(f"   Designation: {emp_data['designation']}")

print(f"\n=== ADMIN CREDENTIALS ===")
print("🔑 Administrator")
print("   Username: admin")
print("   Password: admin123")

print("\n👥 HR Manager")
print("   Username: hrmanager")
print("   Password: hr123")

print("\n📊 Department Manager")
print("   Username: manager")
print("   Password: manager123")

print(f"\n🌐 Login URL: http://127.0.0.1:8000/accounts/login/")
print("="*60)
