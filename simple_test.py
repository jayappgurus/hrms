#!/usr/bin/env python

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
django.setup()

# Test URL resolution
try:
    from django.urls import reverse
    url = reverse('employees:export_public_holidays_csv', kwargs={'country': 'IN'})
    print('Export India URL:', url)
except Exception as e:
    print('URL resolution error:', e)

# Test with Django test client
try:
    from django.test import Client
    client = Client()
    response = client.get('/leave/public-holidays/export-csv/?country=IN')
    print('Status:', response.status_code)
    print('Content-Type:', response.get('Content-Type', 'N/A'))
    if response.status_code == 200:
        print('SUCCESS: India export works!')
    else:
        print('FAILED: India export failed')
except Exception as e:
    print('Test error:', e)
