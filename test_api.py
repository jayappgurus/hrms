#!/usr/bin/env python
"""
Test script for HRMS Employee API
This script demonstrates how to use the employee API endpoints.
"""

import requests
import json
from requests.auth import HTTPBasicAuth

# Configuration
BASE_URL = "http://localhost:8000/employees/api"
# You'll need to login first and get session cookie
# For testing, you might need to use Django test client or session authentication

def test_api_endpoints():
    """Test all API endpoints"""
    
    # Note: This is a demonstration script
    # In production, you would need proper authentication
    
    print("HRMS Employee API Test Script")
    print("=" * 40)
    
    # Test 1: Get all employees
    print("\n1. Testing GET /api/employees/")
    print("URL:", f"{BASE_URL}/employees/")
    print("Method: GET")
    print("Headers: {'Content-Type': 'application/json'}")
    print("Authentication: Required (session cookie)")
    print("Expected Response: JSON with employee list and pagination")
    
    # Example response structure
    example_response = {
        "employees": [
            {
                "id": 1,
                "employee_code": "EM0001",
                "full_name": "John Doe",
                "department": {"id": 1, "name": "IT Department"},
                "designation": {"id": 1, "name": "Software Engineer"},
                "employment_status": "active",
                "current_ctc": 600000.00,
                "official_email": "john.doe@company.com"
            }
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 1,
            "total_count": 1,
            "has_next": False,
            "has_previous": False
        }
    }
    print("Example Response:", json.dumps(example_response, indent=2))
    
    # Test 2: Get specific employee
    print("\n2. Testing GET /api/employees/<id>/")
    print("URL:", f"{BASE_URL}/employees/1/")
    print("Method: GET")
    print("Authentication: Required")
    print("Expected Response: Detailed employee information")
    
    # Test 3: Get departments
    print("\n3. Testing GET /api/departments/")
    print("URL:", f"{BASE_URL}/departments/")
    print("Method: GET")
    print("Authentication: Required")
    print("Expected Response: List of departments with employee counts")
    
    # Test 4: Get designations
    print("\n4. Testing GET /api/designations/")
    print("URL:", f"{BASE_URL}/designations/")
    print("Method: GET")
    print("Authentication: Required")
    print("Expected Response: List of designations")
    
    # Test 5: Get employee statistics
    print("\n5. Testing GET /api/employees/stats/")
    print("URL:", f"{BASE_URL}/employees/stats/")
    print("Method: GET")
    print("Authentication: Required")
    print("Expected Response: Employee statistics and breakdowns")
    
    # Test 6: Search employees
    print("\n6. Testing GET /api/employees/?search=john")
    print("URL:", f"{BASE_URL}/employees/?search=john")
    print("Method: GET")
    print("Authentication: Required")
    print("Expected Response: Filtered employee list")
    
    print("\n" + "=" * 40)
    print("API Testing Complete!")
    print("\nTo actually test these endpoints:")
    print("1. Start the Django development server: python manage.py runserver")
    print("2. Login to the application through the web interface")
    print("3. Use browser developer tools or tools like Postman/Insomnia")
    print("4. Include the session cookie in your requests")
    print("5. Or use Django test client for automated testing")

if __name__ == "__main__":
    test_api_endpoints()
