from django.core.management.base import BaseCommand
from django.utils import timezone
from employees.models import Department, Designation, Employee, EmergencyContact
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Create sample data for testing the HRMS portal'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create departments
        departments_data = [
            {'name': 'Information Technology', 'description': 'IT and Software Development'},
            {'name': 'Human Resources', 'description': 'HR and Administration'},
            {'name': 'Finance', 'description': 'Finance and Accounting'},
            {'name': 'Marketing', 'description': 'Marketing and Sales'},
            {'name': 'Operations', 'description': 'Operations and Logistics'},
        ]

        for dept_data in departments_data:
            department, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'description': dept_data['description']}
            )
            if created:
                self.stdout.write(f'Created department: {department.name}')

        # Create designations
        designations_data = [
            {'name': 'Software Engineer', 'department': 'Information Technology'},
            {'name': 'Senior Software Engineer', 'department': 'Information Technology'},
            {'name': 'IT Manager', 'department': 'Information Technology'},
            {'name': 'HR Executive', 'department': 'Human Resources'},
            {'name': 'HR Manager', 'department': 'Human Resources'},
            {'name': 'Accountant', 'department': 'Finance'},
            {'name': 'Finance Manager', 'department': 'Finance'},
            {'name': 'Marketing Executive', 'department': 'Marketing'},
            {'name': 'Marketing Manager', 'department': 'Marketing'},
            {'name': 'Operations Manager', 'department': 'Operations'},
        ]

        for desig_data in designations_data:
            department = Department.objects.get(name=desig_data['department'])
            designation, created = Designation.objects.get_or_create(
                name=desig_data['name'],
                department=department,
                defaults={'description': f'{desig_data["name"]} position'}
            )
            if created:
                self.stdout.write(f'Created designation: {designation.name}')

        # Create sample employees
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa', 'James', 'Mary']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']

        for i in range(10):
            # Create emergency contact
            emergency_contact = EmergencyContact.objects.create(
                name=f'{random.choice(first_names)} {random.choice(last_names)}',
                mobile_number=f'+91{random.randint(9000000000, 9999999999)}',
                email=f'emergency{i+1}@example.com',
                address='123 Emergency Street, City, State',
                relationship=random.choice(['Spouse', 'Parent', 'Sibling', 'Friend'])
            )

            # Create employee
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            full_name = f'{first_name} {last_name}'
            
            employee = Employee.objects.create(
                employee_code=f'EMP{i+1:03d}',
                full_name=full_name,
                department=random.choice(Department.objects.all()),
                designation=random.choice(Designation.objects.all()),
                joining_date=date.today() - timedelta(days=random.randint(30, 1000)),
                employment_status=random.choice(['active', 'active', 'active', 'inactive']),  # More active employees
                mobile_number=f'+91{random.randint(9000000000, 9999999999)}',
                official_email=f'{first_name.lower()}.{last_name.lower()}@company.com',
                personal_email=f'{first_name.lower()}.{last_name.lower()}@gmail.com',
                local_address=f'{i+1} Local Street, Area, City - {random.randint(100000, 999999)}',
                permanent_address=f'{i+1} Permanent Street, Area, City - {random.randint(100000, 999999)}',
                emergency_contact=emergency_contact,
                date_of_birth=date.today() - timedelta(days=random.randint(6570, 14600)),  # 18-40 years
                marital_status=random.choice(['single', 'married']),
                anniversary_date=date.today() - timedelta(days=random.randint(365, 3650)) if random.choice([True, False]) else None,
                highest_qualification=random.choice(['B.Tech', 'MBA', 'MCA', 'B.Com', 'BA', 'M.Tech']),
                total_experience_years=random.randint(0, 15),
                total_experience_months=random.randint(0, 11),
                aadhar_card_number=f'{random.randint(100000000000, 999999999999)}',
                pan_card_number=f'{"".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5))}{random.randint(1000, 9999)}{random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}'
            )

            self.stdout.write(f'Created employee: {employee.full_name}')

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
