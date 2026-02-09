#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
django.setup()

from django.http import HttpResponse

def simple_test(request):
    """Simple test view"""
    return HttpResponse(f"URL Pattern Working! Requested: {request.path}")

# Test the URL pattern directly
from django.urls import reverse
try:
    url = reverse('employees:employee_add')
    print(f"Employee Add URL: {url}")
except Exception as e:
    print(f"URL reverse error: {e}")
