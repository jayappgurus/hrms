#!/usr/bin/env python

import os
import sys
import django
from django.conf import settings
from django.test import Client
from django.contrib.sessions.middleware import SessionMiddleware

def main():
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
    django.setup()
    
    # Create client
    client = Client()
    
    print("Testing export URLs...")
    
    # Test 1: Export India holidays
    print("1. Testing India export...")
    try:
        response = client.get('/leave/public-holidays/export-csv/?country=IN')
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.get('Content-Type', 'N/A')}")
        print(f"   Content-Disposition: {response.get('Content-Disposition', 'N/A')}")
        if response.status_code == 200:
            print("   SUCCESS")
        else:
            print("   FAILED")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Export Australia holidays
    print("2. Testing Australia export...")
    try:
        response = client.get('/leave/public-holidays/export-csv/?country=AU')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   SUCCESS")
        else:
            print("   FAILED")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Export all holidays
    print("3. Testing all holidays export...")
    try:
        response = client.get('/leave/public-holidays/export-csv/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   SUCCESS")
        else:
            print("   FAILED")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == '__main__':
    main()
