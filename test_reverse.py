import os
import django
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
django.setup()

try:
    url = reverse('employees:employee_delete_record', args=[1])
    print(f"SUCCESS: {url}")
except Exception as e:
    print(f"FAILURE: {e}")
