"""
Quick test script for SystemDetailForm
Run with: python test_system_form.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
django.setup()

from employees.forms_system import SystemDetailForm
from employees.models import Employee, Department

def test_form_validation():
    """Test form validation with various scenarios"""
    
    print("=" * 60)
    print("TESTING SYSTEM DETAIL FORM")
    print("=" * 60)
    
    # Get a test employee
    try:
        employee = Employee.objects.filter(employment_status='active').first()
        if not employee:
            print("❌ No active employees found. Please create an employee first.")
            return
        
        print(f"\n✓ Using employee: {employee.full_name}")
        print(f"  Department: {employee.department.name if employee.department else 'None'}")
        
    except Exception as e:
        print(f"❌ Error getting employee: {e}")
        return
    
    # Test 1: Valid Windows system
    print("\n" + "-" * 60)
    print("TEST 1: Valid Windows System")
    print("-" * 60)
    
    data = {
        'system_type': 'windows',
        'employee': employee.id,
        'department': employee.department.id if employee.department else '',
        'cpu_ram': '16GB DDR4',
        'cpu_storage': '512GB SSD',
        'cpu_company_name': 'Dell',
        'cpu_processor': 'Intel i7',
        'cpu_label_no': 'TEST-CPU-001',
        'screen_company_name': 'Dell',
        'screen_label_no': 'TEST-SCREEN-001',
        'screen_size': '24 inch',
        'keyboard_company_name': 'Logitech',
        'keyboard_label_no': 'TEST-KB-001',
        'mouse_company_name': 'Logitech',
        'mouse_label_no': 'TEST-MOUSE-001',
        'has_headphone': False,
        'has_extender': False,
        'is_active': True,
    }
    
    form = SystemDetailForm(data=data)
    if form.is_valid():
        print("✓ Form is valid")
        print(f"  System Type: {form.cleaned_data['system_type']}")
        print(f"  CPU Label: {form.cleaned_data['cpu_label_no']}")
    else:
        print("❌ Form has errors:")
        for field, errors in form.errors.items():
            print(f"  {field}: {', '.join(errors)}")
    
    # Test 2: MAC system with MAC address
    print("\n" + "-" * 60)
    print("TEST 2: MAC System with MAC Address")
    print("-" * 60)
    
    data['system_type'] = 'mac'
    data['cpu_company_name'] = 'Mac'
    data['macaddress'] = '00:1B:44:11:3A:B7'
    data['cpu_label_no'] = 'TEST-CPU-002'
    data['screen_label_no'] = 'TEST-SCREEN-002'
    data['keyboard_label_no'] = 'TEST-KB-002'
    data['mouse_label_no'] = 'TEST-MOUSE-002'
    
    form = SystemDetailForm(data=data)
    if form.is_valid():
        print("✓ Form is valid")
        print(f"  System Type: {form.cleaned_data['system_type']}")
        print(f"  MAC Address: {form.cleaned_data['macaddress']}")
    else:
        print("❌ Form has errors:")
        for field, errors in form.errors.items():
            print(f"  {field}: {', '.join(errors)}")
    
    # Test 3: Invalid MAC address format
    print("\n" + "-" * 60)
    print("TEST 3: Invalid MAC Address Format")
    print("-" * 60)
    
    data['macaddress'] = 'invalid-mac'
    data['cpu_label_no'] = 'TEST-CPU-003'
    data['screen_label_no'] = 'TEST-SCREEN-003'
    data['keyboard_label_no'] = 'TEST-KB-003'
    data['mouse_label_no'] = 'TEST-MOUSE-003'
    
    form = SystemDetailForm(data=data)
    if form.is_valid():
        print("❌ Form should not be valid with invalid MAC address")
    else:
        print("✓ Form correctly rejected invalid MAC address")
        if 'macaddress' in form.errors:
            print(f"  Error: {form.errors['macaddress'][0]}")
    
    # Test 4: Headphone with missing fields
    print("\n" + "-" * 60)
    print("TEST 4: Headphone Selected but Missing Required Fields")
    print("-" * 60)
    
    data['macaddress'] = '00:1B:44:11:3A:B8'
    data['has_headphone'] = True
    data['cpu_label_no'] = 'TEST-CPU-004'
    data['screen_label_no'] = 'TEST-SCREEN-004'
    data['keyboard_label_no'] = 'TEST-KB-004'
    data['mouse_label_no'] = 'TEST-MOUSE-004'
    # Not providing headphone_company_name and headphone_label_no
    
    form = SystemDetailForm(data=data)
    if form.is_valid():
        print("❌ Form should not be valid without headphone details")
    else:
        print("✓ Form correctly requires headphone details")
        if 'headphone_company_name' in form.errors:
            print(f"  Error: {form.errors['headphone_company_name'][0]}")
        if 'headphone_label_no' in form.errors:
            print(f"  Error: {form.errors['headphone_label_no'][0]}")
    
    # Test 5: Complete form with headphone and extender
    print("\n" + "-" * 60)
    print("TEST 5: Complete Form with Headphone and Extender")
    print("-" * 60)
    
    data['has_headphone'] = True
    data['headphone_company_name'] = 'Sony'
    data['headphone_label_no'] = 'TEST-HP-001'
    data['has_extender'] = True
    data['extender_label'] = 'EXT-001'
    data['extender_name'] = 'USB Hub'
    data['cpu_label_no'] = 'TEST-CPU-005'
    data['screen_label_no'] = 'TEST-SCREEN-005'
    data['keyboard_label_no'] = 'TEST-KB-005'
    data['mouse_label_no'] = 'TEST-MOUSE-005'
    
    form = SystemDetailForm(data=data)
    if form.is_valid():
        print("✓ Form is valid")
        print(f"  Has Headphone: {form.cleaned_data['has_headphone']}")
        print(f"  Headphone Company: {form.cleaned_data['headphone_company_name']}")
        print(f"  Has Extender: {form.cleaned_data['has_extender']}")
        print(f"  Extender Name: {form.cleaned_data['extender_name']}")
    else:
        print("❌ Form has errors:")
        for field, errors in form.errors.items():
            print(f"  {field}: {', '.join(errors)}")
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    test_form_validation()
