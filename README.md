# HRMS Portal - Employee Management System

A modern Human Resource Management System (HRMS) built with Django and Bootstrap 5, featuring comprehensive employee management capabilities.

## 🎯 Features

### Employee Management Module
- **Complete CRUD Operations**: Add, edit, view, and manage employee records
- **Comprehensive Employee Profiles**: Store detailed personal, professional, and contact information
- **Document Tracking**: Monitor submission of required documents (ID proofs, address proofs, educational certificates)
- **Emergency Contact Management**: Store emergency contact details for each employee
- **Status Management**: Activate/deactivate employee records with toggle functionality
- **Advanced Search**: Search employees by name with real-time filtering
- **Responsive Design**: Modern Bootstrap 5 interface with mobile-friendly layout

### Key Employee Information Captured
- **Core Details**: Employee code, name, department, designation, joining/relieving dates
- **Contact Information**: Mobile, official/personal emails, local/permanent addresses
- **Personal Data**: Date of birth, marital status, anniversary date
- **Professional Info**: Qualifications, experience, probation status (auto-calculated)
- **Identity Documents**: Aadhar card, PAN card with validation
- **Emergency Contacts**: Name, relationship, contact details, address

### Document Submission Tracker
- **Photographs**: Passport photos (4 copies)
- **Identity Proofs**: Aadhar, PAN, Driving License, Voter ID, Passport
- **Address Proofs**: Electricity bill, Tax bill, Rent agreement
- **Education Proofs**: SSC/HSC marksheets, Graduation/PG certificates and marksheets

## 🛠 Technology Stack

- **Backend**: Django 4.2.7 (Python Web Framework)
- **Database**: MySQL (portal_hrms_db)
- **Frontend**: Bootstrap 5 with modern UI components
- **Icons**: Bootstrap Icons
- **JavaScript**: jQuery for dynamic interactions
- **Additional**: Pillow for image handling, django-crispy-forms

## 📁 Project Structure

```
hrms-portal/
├── manage.py
├── requirements.txt
├── .env
├── hrms_portal/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── employees/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── templates/
│   ├── base.html
│   └── employees/
│       ├── employee_list.html
│       ├── employee_form.html
│       └── employee_detail.html
└── static/
    └── css/
        └── custom.css
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL Server
- pip (Python package manager)

### Step 1: Clone and Setup
```bash
# Navigate to project directory
cd c:\Vijay\Project\hrms-portal

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Database Setup
```sql
# Create MySQL database
CREATE DATABASE portal_hrms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user (optional)
CREATE USER 'hrms_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON portal_hrms_db.* TO 'hrms_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 4: Environment Configuration
Update the `.env` file with your database credentials:
```env
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True

DB_NAME=portal_hrms_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

### Step 5: Django Setup
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

### Step 6: Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## 📊 Database Schema

### Core Tables
- **employees**: Main employee records
- **departments**: Company departments
- **designations**: Job positions linked to departments
- **emergency_contacts**: Emergency contact information
- **employee_documents**: Document submission tracking

### Key Relationships
- Employee → Department (Many-to-One)
- Employee → Designation (Many-to-One)
- Employee → EmergencyContact (One-to-One)
- Employee → EmployeeDocument (One-to-Many)

## 🎨 UI Features

### Modern Design Elements
- **Bootstrap 5**: Clean, responsive components
- **Color Scheme**: Professional blue primary theme
- **Cards**: Rounded corners with soft shadows
- **Icons**: Bootstrap Icons throughout the interface
- **Responsive**: Mobile-first design approach

### Interactive Features
- **Dynamic Forms**: AJAX-powered department/designation filtering
- **Status Toggles**: One-click employee activation/deactivation
- **Document Checkboxes**: Real-time document status updates
- **Search**: Live employee search without page reload
- **Pagination**: Efficient handling of large employee lists

## 🔧 Configuration

### Settings Highlights
- MySQL database configuration
- Static files and media handling
- Authentication middleware
- Message framework for notifications
- Timezone set to Asia/Kolkata

### Security Features
- CSRF protection enabled
- Input validation on all forms
- SQL injection prevention through Django ORM
- XSS protection with template escaping

## 📝 Usage Guide

### Adding Employees
1. Navigate to Employee List
2. Click "Add Employee" button
3. Fill in all required fields across sections
4. Emergency contact is mandatory
5. System auto-calculates probation status

### Managing Documents
1. View employee detail page
2. Scroll to Document Submission Tracker
3. Check/uncheck boxes to mark document status
4. Updates are saved automatically via AJAX

### Search and Filter
1. Use search bar on employee list page
2. Search by employee name or code
3. Results update without page refresh

## 🔄 Future Enhancements

- Attendance management module
- Payroll and salary management
- Leave management system
- Performance evaluation module
- Report generation and analytics
- Employee self-service portal
- Document upload functionality
- Email notifications
- Role-based access control

## 🐛 Troubleshooting

### Common Issues
1. **Database Connection**: Ensure MySQL server is running and credentials are correct
2. **Migration Errors**: Drop and recreate database if needed
3. **Static Files**: Run `collectstatic` command if CSS/JS not loading
4. **Permissions**: Ensure proper file permissions for media uploads

### Debug Mode
Set `DEBUG=True` in settings.py for detailed error messages during development.

## 📞 Support

For issues and support:
1. Check Django documentation
2. Review MySQL logs for database errors
3. Enable debug mode for detailed error tracking

## 📄 License

This project is for educational and demonstration purposes.
