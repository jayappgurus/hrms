#!/usr/bin/env python
"""
Debug script to test the JSON serialization for designations
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
django.setup()

import json
from employees.models import Designation

def test_designations_json():
    """Test the designations JSON serialization"""
    
    print("🔍 Testing Designations JSON Serialization")
    print("=" * 50)
    
    # Get all designations
    all_designations = list(Designation.objects.values('id', 'name', 'department_id'))
    
    print(f"Total designations: {len(all_designations)}")
    
    # Serialize to JSON
    json_data = json.dumps(all_designations)
    
    print(f"JSON length: {len(json_data)}")
    print(f"JSON sample: {json_data[:200]}...")
    
    # Test if it's valid JSON
    try:
        parsed = json.loads(json_data)
        print(f"✅ JSON is valid. Parsed {len(parsed)} items")
        if parsed:
            print(f"First item: {parsed[0]}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
    
    # Check for any special characters that might cause issues
    print("\n🔍 Checking for problematic characters:")
    for i, item in enumerate(all_designations[:5]):  # Check first 5 items
        name = item.get('name', '')
        if any(char in name for char in ["'", '"', '\n', '\r', '\t']):
            print(f"⚠️  Item {i} contains special characters: {name}")
        else:
            print(f"✅ Item {i}: {name}")

if __name__ == "__main__":
    test_designations_json()
