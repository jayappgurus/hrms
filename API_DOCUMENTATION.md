# HRMS Portal Employee API Documentation

This document describes the REST API endpoints for accessing employee data in the HRMS Portal.

## Base URL
```
http://localhost:8000/employees/api/
```

## Authentication
All API endpoints require authentication. You must be logged in to access the APIs.

## API Endpoints

### 1. Get All Employees
**GET** `/api/employees/`

Get a paginated list of all employees with optional filtering.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Number of items per page (default: 20)
- `search` (optional): Search term for name, employee code, email, or mobile
- `department` (optional): Filter by department name
- `status` (optional): Filter by employment status (active/inactive)

**Response:**
```json
{
  "employees": [
    {
      "id": 1,
      "employee_code": "EM0001",
      "full_name": "John Doe",
      "profile_picture": "/media/employee_profiles/2024/01/profile.jpg",
      "department": {
        "id": 1,
        "name": "IT Department"
      },
      "designation": {
        "id": 1,
        "name": "Software Engineer"
      },
      "joining_date": "2024-01-15",
      "employment_status": "active",
      "current_ctc": 600000.00,
      "official_email": "john.doe@company.com",
      "mobile_number": "+919876543210",
      "date_of_birth": "1995-06-15",
      "age": 28,
      "marital_status": "single",
      "highest_qualification": "B.E. (CSE)",
      "total_experience_display": "3 y 2 mo",
      "period_type": "confirmed",
      "aadhar_card_number": "123456789012",
      "pan_card_number": "ABCDE1234F",
      "local_address": "123 Street, City",
      "permanent_address": "456 Avenue, City",
      "emergency_contact": {
        "name": "Jane Doe",
        "mobile_number": "+919876543211",
        "email": "jane.doe@email.com",
        "relationship": "Spouse"
      },
      "salary_components": {
        "earnings": {
          "Basic_Salary": 25000.00,
          "House_Rent_Allowance": 12500.00,
          "Special_Allowance": 12500.00
        },
        "deductions": {
          "Provident_Fund": 1800.00,
          "Professional_Tax": 200.00
        },
        "gross_salary": 50000.00,
        "total_deductions": 2000.00,
        "net_salary": 48000.00,
        "ctc_monthly": 50000.00,
        "ctc_annual": 600000.00
      },
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_count": 100,
    "has_next": true,
    "has_previous": false
  }
}
```

### 2. Get Employee Details
**GET** `/api/employees/<employee_id>/`

Get detailed information for a specific employee including documents, leave applications, device allocations, and performance evaluations.

**Response:**
```json
{
  "id": 1,
  "employee_code": "EM0001",
  "full_name": "John Doe",
  "profile_picture": "/media/employee_profiles/2024/01/profile.jpg",
  "department": {
    "id": 1,
    "name": "IT Department",
    "description": "Information Technology Department"
  },
  "designation": {
    "id": 1,
    "name": "Software Engineer",
    "description": "Senior Software Engineer"
  },
  "joining_date": "2024-01-15",
  "probation_end_date": "2024-04-15",
  "relieving_date": null,
  "employment_status": "active",
  "current_ctc": 600000.00,
  "salary_structure": null,
  "contact_info": {
    "official_email": "john.doe@company.com",
    "personal_email": "john.personal@email.com",
    "mobile_number": "+919876543210",
    "local_address": "123 Street, City",
    "permanent_address": "456 Avenue, City"
  },
  "personal_info": {
    "date_of_birth": "1995-06-15",
    "age": 28,
    "marital_status": "single",
    "anniversary_date": null
  },
  "professional_info": {
    "highest_qualification": "B.E. (CSE)",
    "total_experience_years": 3,
    "total_experience_months": 2,
    "total_experience_display": "3 y 2 mo",
    "period_type": "confirmed"
  },
  "identity_info": {
    "aadhar_card_number": "123456789012",
    "pan_card_number": "ABCDE1234F"
  },
  "emergency_contact": {
    "name": "Jane Doe",
    "mobile_number": "+919876543211",
    "email": "jane.doe@email.com",
    "address": "789 Road, City",
    "relationship": "Spouse"
  },
  "salary_components": {
    "earnings": {...},
    "deductions": {...},
    "gross_salary": 50000.00,
    "total_deductions": 2000.00,
    "net_salary": 48000.00,
    "ctc_monthly": 50000.00,
    "ctc_annual": 600000.00
  },
  "user_profile": {
    "user_id": 1,
    "username": "john.doe@company.com",
    "email": "john.doe@company.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "employee",
    "phone": "+919876543210",
    "is_active": true,
    "date_joined": "2024-01-15T10:30:00Z",
    "last_login": "2024-02-19T09:15:00Z"
  },
  "documents": [
    {
      "id": 1,
      "document_type": "passport_photo",
      "document_type_display": "Passport Photo",
      "document_file": "/media/employee_documents/2024/01/passport.jpg",
      "is_submitted": true,
      "submitted_date": "2024-01-16T10:00:00Z",
      "remarks": "Clear photo"
    }
  ],
  "recent_leave_applications": [
    {
      "id": 1,
      "leave_type": "Casual Leave (CL)",
      "start_date": "2024-02-10",
      "end_date": "2024-02-12",
      "total_days": 3.0,
      "status": "approved",
      "reason": "Personal work",
      "created_at": "2024-02-08T11:00:00Z"
    }
  ],
  "device_allocations": [
    {
      "id": 1,
      "device": {
        "id": 1,
        "device_name": "Laptop Dell XPS",
        "device_type": "laptop",
        "serial_number": "DELL123456"
      },
      "assigned_date": "2024-01-16T09:00:00Z",
      "returned_date": null,
      "is_active": true,
      "return_notes": null
    }
  ],
  "performance_evaluations": [
    {
      "id": 1,
      "cycle_number": 1,
      "overall_rating": 4.5,
      "status": "completed",
      "evaluation_date": "2024-01-15T00:00:00Z",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 3. Get Departments
**GET** `/api/departments/`

Get a list of all departments with employee counts.

**Response:**
```json
{
  "departments": [
    {
      "id": 1,
      "name": "IT Department",
      "description": "Information Technology Department",
      "head": {
        "id": 1,
        "full_name": "John Smith",
        "employee_code": "EM0001"
      },
      "employee_count": 25,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 4. Get Designations
**GET** `/api/designations/`

Get a list of all designations with optional department filter.

**Query Parameters:**
- `department_id` (optional): Filter by department ID

**Response:**
```json
{
  "designations": [
    {
      "id": 1,
      "name": "Software Engineer",
      "description": "Senior Software Engineer position",
      "department": {
        "id": 1,
        "name": "IT Department"
      },
      "employee_count": 10,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 5. Get Employee Statistics
**GET** `/api/employees/stats/`

Get comprehensive employee statistics and breakdowns.

**Response:**
```json
{
  "total_employees": 100,
  "active_employees": 95,
  "inactive_employees": 5,
  "department_breakdown": [
    {
      "department": "IT Department",
      "employee_count": 25
    },
    {
      "department": "HR Department",
      "employee_count": 10
    }
  ],
  "status_breakdown": [
    {
      "employment_status": "active",
      "count": 95
    },
    {
      "employment_status": "inactive",
      "count": 5
    }
  ],
  "period_type_breakdown": [
    {
      "period_type": "confirmed",
      "count": 80
    },
    {
      "period_type": "probation",
      "count": 15
    },
    {
      "period_type": "trainee",
      "count": 5
    }
  ]
}
```

### 6. Get Available Devices
**GET** `/api/available-devices/<device_type>/`

Get available devices by type (laptop, mobile, tablet, accessories).

**Response:**
```json
{
  "devices": [
    {
      "id": 1,
      "device_name": "Laptop Dell XPS",
      "serial_number": "DELL123456"
    }
  ]
}
```

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "error": "Error message description"
}
```

## Permissions

- **Admin, Director, HR**: Can access all employee data
- **Manager**: Can view employees in their department
- **Employee**: Can only view their own profile details
- **IT Admin**: Can access device-related endpoints

## Usage Examples

### Using curl
```bash
# Get all employees
curl -X GET "http://localhost:8000/employees/api/employees/" \
  -H "Cookie: sessionid=your_session_cookie"

# Get specific employee
curl -X GET "http://localhost:8000/employees/api/employees/1/" \
  -H "Cookie: sessionid=your_session_cookie"

# Search employees
curl -X GET "http://localhost:8000/employees/api/employees/?search=john&department=IT" \
  -H "Cookie: sessionid=your_session_cookie"
```

### Using JavaScript (fetch)
```javascript
// Get all employees
fetch('/employees/api/employees/', {
  method: 'GET',
  credentials: 'same-origin'
})
.then(response => response.json())
.then(data => console.log(data));

// Get specific employee
fetch('/employees/api/employees/1/', {
  method: 'GET',
  credentials: 'same-origin'
})
.then(response => response.json())
.then(data => console.log(data));
```

## Notes

1. All dates are returned in ISO format (YYYY-MM-DDTHH:MM:SSZ)
2. Currency values are returned as numbers (not strings)
3. Profile pictures and document files return the full URL path
4. Pagination starts from page 1
5. Search is case-insensitive and searches multiple fields
6. All API endpoints require the user to be authenticated via Django's session authentication
