#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
django.setup()

from django.urls import reverse
from employees.views_department import department_management

print("=== URL DEBUGGING ===")
print(f"Department Management URL: {reverse('employees:department_management')}")
print(f"View function: {department_management}")

# Test URL resolution
try:
    from django.urls import resolve
    resolved = resolve('/employees/departments/')
    print(f"Resolved view: {resolved.view_name}")
    print(f"Resolved URL name: {resolved.url_name}")
except Exception as e:
    print(f"URL resolution error: {e}")

# Check all employees URLs
from employees.urls import urlpatterns
print("\nEmployees URL patterns:")
for pattern in urlpatterns:
    print(f"  {pattern.pattern} -> {pattern.name}")
