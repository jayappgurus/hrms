#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Department, Designation

print("=== HRMS DEPARTMENT & DESIGNATION SETUP ===\n")

# Create additional departments
departments_data = [
    {
        'name': 'Human Resources',
        'description': 'HR Department - Managing employee relations, recruitment, and policies'
    },
    {
        'name': 'IT Department',
        'description': 'IT Department - Managing technology infrastructure and support'
    },
    {
        'name': 'Finance Department',
        'description': 'Finance Department - Managing financial operations and accounting'
    },
    {
        'name': 'Marketing Department',
        'description': 'Marketing Department - Managing brand, promotions, and communications'
    },
    {
        'name': 'Sales Department',
        'description': 'Sales Department - Managing client relationships and revenue generation'
    },
    {
        'name': 'Operations Department',
        'description': 'Operations Department - Managing day-to-day business operations'
    },
    {
        'name': 'Customer Support',
        'description': 'Customer Support - Managing customer service and support operations'
    },
    {
        'name': 'Quality Assurance',
        'description': 'Quality Assurance - Ensuring product and service quality'
    }
]

print("Creating Departments...")
created_departments = []
for dept_data in departments_data:
    department, created = Department.objects.get_or_create(
        name=dept_data['name'],
        defaults={'description': dept_data['description']}
    )
    if created:
        print(f"✅ Created Department: {department.name}")
        created_departments.append(department)
    else:
        print(f"📋 Department already exists: {department.name}")
        created_departments.append(department)

# Create designations for each department
designations_data = {
    'Human Resources': [
        {'name': 'HR Manager', 'description': 'Head of HR operations'},
        {'name': 'HR Executive', 'description': 'HR operations and employee relations'},
        {'name': 'HR Assistant', 'description': 'Administrative HR support'},
        {'name': 'Recruiter', 'description': 'Talent acquisition and recruitment'},
        {'name': 'Training Coordinator', 'description': 'Employee training and development'},
        {'name': 'Payroll Specialist', 'description': 'Payroll and compensation management'},
    ],
    'IT Department': [
        {'name': 'IT Manager', 'description': 'Head of IT operations'},
        {'name': 'Senior Developer', 'description': 'Lead software development'},
        {'name': 'Software Developer', 'description': 'Software development and coding'},
        {'name': 'UI/UX Designer', 'description': 'User interface and experience design'},
        {'name': 'Database Administrator', 'description': 'Database management and optimization'},
        {'name': 'Network Engineer', 'description': 'Network infrastructure and security'},
        {'name': 'IT Support', 'description': 'Technical support and troubleshooting'},
        {'name': 'System Administrator', 'description': 'System administration and maintenance'},
    ],
    'Finance Department': [
        {'name': 'Finance Manager', 'description': 'Head of financial operations'},
        {'name': 'Senior Accountant', 'description': 'Senior accounting and financial reporting'},
        {'name': 'Accountant', 'description': 'Financial accounting and bookkeeping'},
        {'name': 'Financial Analyst', 'description': 'Financial analysis and planning'},
        {'name': 'Tax Specialist', 'description': 'Tax planning and compliance'},
        {'name': 'Accounts Payable', 'description': 'Managing vendor payments'},
        {'name': 'Accounts Receivable', 'description': 'Managing customer payments'},
    ],
    'Marketing Department': [
        {'name': 'Marketing Manager', 'description': 'Head of marketing operations'},
        {'name': 'Digital Marketing Specialist', 'description': 'Digital marketing and online campaigns'},
        {'name': 'Content Writer', 'description': 'Content creation and copywriting'},
        {'name': 'Social Media Manager', 'description': 'Social media strategy and management'},
        {'name': 'Brand Manager', 'description': 'Brand strategy and management'},
        {'name': 'Marketing Analyst', 'description': 'Marketing data analysis and insights'},
        {'name': 'SEO Specialist', 'description': 'Search engine optimization'},
    ],
    'Sales Department': [
        {'name': 'Sales Manager', 'description': 'Head of sales operations'},
        {'name': 'Senior Sales Executive', 'description': 'Senior sales and client management'},
        {'name': 'Sales Executive', 'description': 'Sales and business development'},
        {'name': 'Business Development Manager', 'description': 'Business development and partnerships'},
        {'name': 'Sales Coordinator', 'description': 'Sales coordination and support'},
        {'name': 'Key Account Manager', 'description': 'Managing key client relationships'},
    ],
    'Operations Department': [
        {'name': 'Operations Manager', 'description': 'Head of operations'},
        {'name': 'Operations Supervisor', 'description': 'Operations supervision and coordination'},
        {'name': 'Operations Executive', 'description': 'Operations management and execution'},
        {'name': 'Logistics Coordinator', 'description': 'Logistics and supply chain management'},
        {'name': 'Quality Control Officer', 'description': 'Quality control and assurance'},
        {'name': 'Process Improvement Specialist', 'description': 'Process optimization and improvement'},
    ],
    'Customer Support': [
        {'name': 'Support Manager', 'description': 'Head of customer support'},
        {'name': 'Senior Support Executive', 'description': 'Senior customer support and escalation'},
        {'name': 'Support Executive', 'description': 'Customer support and service'},
        {'name': 'Technical Support Specialist', 'description': 'Technical support and troubleshooting'},
        {'name': 'Customer Success Manager', 'description': 'Customer relationship management'},
        {'name': 'Support Team Lead', 'description': 'Support team leadership and coordination'},
    ],
    'Quality Assurance': [
        {'name': 'QA Manager', 'description': 'Head of quality assurance'},
        {'name': 'Senior QA Engineer', 'description': 'Senior quality testing and assurance'},
        {'name': 'QA Engineer', 'description': 'Quality testing and assurance'},
        {'name': 'Test Automation Engineer', 'description': 'Test automation and framework development'},
        {'name': 'Performance Tester', 'description': 'Performance and load testing'},
        {'name': 'Manual Tester', 'description': 'Manual testing and quality checks'},
    ]
}

print("\nCreating Designations...")
total_designations_created = 0
for department in created_departments:
    if department.name in designations_data:
        print(f"\n📁 Creating designations for {department.name}:")
        for designation_data in designations_data[department.name]:
            designation, created = Designation.objects.get_or_create(
                name=designation_data['name'],
                department=department,
                defaults={'description': designation_data['description']}
            )
            if created:
                print(f"  ✅ Created: {designation.name}")
                total_designations_created += 1
            else:
                print(f"  📋 Already exists: {designation.name}")

# Display summary
print(f"\n=== SETUP SUMMARY ===")
print(f"Total Departments: {Department.objects.count()}")
print(f"Total Designations: {Designation.objects.count()}")
print(f"New Designations Created: {total_designations_created}")

print(f"\n=== DEPARTMENT LIST ===")
for dept in Department.objects.all():
    designation_count = Designation.objects.filter(department=dept).count()
    print(f"📁 {dept.name} ({designation_count} designations)")

print(f"\n=== DESIGNATION LIST ===")
for designation in Designation.objects.all():
    print(f"💼 {designation.name} - {designation.department.name}")

print(f"\n=== USER ACCESS INFO ===")
print("🔑 ADMIN ACCESS")
print("   Username: admin")
print("   Password: admin123")
print("   Role: Administrator (Full system access)")

print("\n👥 HR MANAGER")
print("   Username: hrmanager")
print("   Password: hr123")
print("   Role: HR Manager (Employee management access)")

print("\n📊 DEPARTMENT MANAGER")
print("   Username: manager")
print("   Password: manager123")
print("   Role: Manager (Department-level access)")

print("\n🌐 NEXT STEPS:")
print("1. Login with admin credentials")
print("2. Go to Employee Management")
print("3. Add new employees with proper department and designation")
print("4. Designation dropdown will populate based on selected department")

print("\n" + "="*60)
