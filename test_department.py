#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
django.setup()

from django.http import HttpResponse

def test_department_view(request):
    """Simple test view for department management"""
    return HttpResponse("Department Management Page is Working! URL: /employees/departments/")
