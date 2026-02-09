#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
django.setup()

from employees.models import LeaveType

print("=== ADD LEAVE TYPES ===\n")

# Common leave types to create
leave_types_data = [
    {
        'name': 'Casual Leave',
        'leave_type': 'casual',
        'max_days': 12,
        'description': 'For personal emergencies and casual needs'
    },
    {
        'name': 'Sick Leave',
        'leave_type': 'sick',
        'max_days': 10,
        'description': 'For medical reasons and health issues'
    },
    {
        'name': 'Earned Leave',
        'leave_type': 'earned',
        'max_days': 15,
        'description': 'Annual earned leave based on service period'
    },
    {
        'name': 'Maternity Leave',
        'leave_type': 'maternity',
        'max_days': 180,
        'description': 'For female employees during pregnancy and post-delivery'
    },
    {
        'name': 'Paternity Leave',
        'leave_type': 'paternity',
        'max_days': 15,
        'description': 'For male employees during child birth'
    },
    {
        'name': 'Study Leave',
        'leave_type': 'study',
        'max_days': 30,
        'description': 'For educational and professional development'
    },
    {
        'name': 'Compensatory Off',
        'leave_type': 'compensatory',
        'max_days': 5,
        'description': 'For extra work done on holidays/weekends'
    },
    {
        'name': 'Leave Without Pay',
        'leave_type': 'unpaid',
        'max_days': 30,
        'description': 'Leave without salary for extended periods'
    }
]

print("Creating leave types...")

for leave_data in leave_types_data:
    try:
        # Check if leave type already exists
        if LeaveType.objects.filter(name=leave_data['name']).exists():
            print(f"📋 Leave type '{leave_data['name']}' already exists")
            continue
        
        # Create leave type
        leave_type = LeaveType.objects.create(
            name=leave_data['name'],
            leave_type=leave_data['leave_type'],
            max_days_per_year=leave_data['max_days'],
            description=leave_data['description'],
            is_paid=True,
            requires_document=True,
            is_active=True
        )
        
        print(f"✅ Created: {leave_type.name} ({leave_type.leave_type}) - {leave_type.max_days_per_year} days")
        
    except Exception as e:
        print(f"❌ Error creating {leave_data['name']}: {e}")

print(f"\n=== LEAVE TYPE SUMMARY ===")
print(f"Total leave types: {LeaveType.objects.count()}")

print(f"\n=== ALL LEAVE TYPES ===")
for lt in LeaveType.objects.all():
    print(f"📋 {lt.name} ({lt.leave_type}) - Max: {lt.max_days_per_year} days")

print(f"\n=== ACCESS INFO ===")
print("🔑 Admin Access:")
print("   Username: admin")
print("   Password: admin123")
print("   Can: Add/Manage all leave types")

print("\n👥 HR Manager Access:")
print("   Username: hrmanager")
print("   Password: hr123")
print("   Can: Add/Manage leave types")

print("\n📊 Department Manager Access:")
print("   Username: manager")
print("   Password: manager123")
print("   Can: Add/Manage leave types")

print(f"\n🌐 Leave Type Management URL:")
print("   http://127.0.0.1:8000/leave-types/")

print(f"\n🗓 Enhanced Leave Application URL:")
print("   http://127.0.0.1:8000/leave-application/add/")
print("   Features: Auto-date calculation, validation, day counting")

print("="*60)
