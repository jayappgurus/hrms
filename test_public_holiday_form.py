"""
Test script to verify PublicHolidayForm works correctly for both create and update
Run with: python manage.py shell < test_public_holiday_form.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
django.setup()

from datetime import date
from employees.models import PublicHoliday
from employees.forms import PublicHolidayForm

print("=" * 60)
print("Testing PublicHolidayForm")
print("=" * 60)

# Test 1: Create new holiday
print("\n1. Testing CREATE (new holiday):")
print("-" * 60)
form_data = {
    'name': 'Test Holiday',
    'date': '2026-12-25',
    'country': 'IN',
    'is_optional': False,
    'is_active': True,
    'description': 'Test description'
}

form = PublicHolidayForm(data=form_data)
print(f"Form is valid: {form.is_valid()}")
if not form.is_valid():
    print(f"Errors: {form.errors}")
else:
    holiday = form.save()
    print(f"Created holiday: {holiday}")
    print(f"  - Name: {holiday.name}")
    print(f"  - Date: {holiday.date}")
    print(f"  - Day: {holiday.day}")
    print(f"  - Year: {holiday.year}")
    print(f"  - Country: {holiday.country}")
    print(f"  - Is Optional: {holiday.is_optional}")
    print(f"  - Is Active: {holiday.is_active}")
    
    # Test 2: Update existing holiday
    print("\n2. Testing UPDATE (existing holiday):")
    print("-" * 60)
    update_data = {
        'name': 'Updated Test Holiday',
        'date': '2026-12-26',
        'country': 'AU',
        'is_optional': True,
        'is_active': True,
        'description': 'Updated description'
    }
    
    update_form = PublicHolidayForm(data=update_data, instance=holiday)
    print(f"Form is valid: {update_form.is_valid()}")
    if not update_form.is_valid():
        print(f"Errors: {update_form.errors}")
    else:
        updated_holiday = update_form.save()
        print(f"Updated holiday: {updated_holiday}")
        print(f"  - Name: {updated_holiday.name}")
        print(f"  - Date: {updated_holiday.date}")
        print(f"  - Day: {updated_holiday.day}")
        print(f"  - Year: {updated_holiday.year}")
        print(f"  - Country: {updated_holiday.country}")
        print(f"  - Is Optional: {updated_holiday.is_optional}")
        print(f"  - Is Active: {updated_holiday.is_active}")
    
    # Cleanup
    print("\n3. Cleaning up test data:")
    print("-" * 60)
    holiday.delete()
    print("Test holiday deleted successfully")

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)
