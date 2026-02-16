# Complete Leave Management Module - HRMS System

## Architecture Overview

This is a production-ready Leave Management Module built with:
- **Backend**: Django 4.x + Django REST Framework
- **Database**: MySQL 8.0+
- **Architecture**: Clean Architecture with Service Layer Pattern
- **Design Patterns**: Repository, Factory, Strategy

## Project Structure

```
leave_management/
├── models/
│   ├── __init__.py
│   ├── employee.py          # Employee model
│   ├── leave_type.py        # Leave type configurations
│   ├── leave_application.py # Leave applications
│   ├── leave_balance.py     # Leave balance tracking
│   └── paid_absence.py      # Paid absence records
├── services/
│   ├── __init__.py
│   ├── leave_service.py     # Core leave logic
│   ├── accrual_service.py   # Monthly accrual logic
│   ├── validation_service.py # Validation rules
│   └── paid_absence_service.py # Paid absence logic
├── serializers/
│   ├── __init__.py
│   ├── leave_serializers.py
│   └── employee_serializers.py
├── views/
│   ├── __init__.py
│   ├── leave_views.py
│   └── admin_views.py
├── tests/
│   ├── __init__.py
│   ├── test_leave_service.py
│   ├── test_accrual.py
│   └── test_validation.py
├── admin.py
├── urls.py
└── apps.py
```

## Features Implemented

### 1. Employee Management
- Regular Employee
- Trainee/Intern
- Probation
- Notice Period

### 2. Leave Types
- Casual Leave (12/year, 1/month accrual)
- Emergency Leave (4/year)
- Birthday Leave (1/year)
- Marriage Anniversary Leave (1/year)

### 3. Business Rules
- Working days calculation (exclude weekends/holidays)
- Monthly accrual for casual leave
- Sandwich rule implementation
- Half-day leave logic
- Balance validation

### 4. Paid Absence
- Marriage Leave (2 days)
- Paternity Leave (5 days, first child)
- Maternity Leave (56 days, first child)

## Installation & Setup

See individual files for implementation details.
