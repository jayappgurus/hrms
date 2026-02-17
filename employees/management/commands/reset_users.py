from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employees.models import UserProfile, Department

class Command(BaseCommand):
    help = 'Reset users - remove old users and create new ones'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all existing users',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(self.style.WARNING(
                '\n⚠️  WARNING: This will DELETE ALL existing users!\n'
            ))
            self.stdout.write('Current users:')
            for user in User.objects.all():
                self.stdout.write(f'  - {user.username} ({user.email})')

            self.stdout.write('\n' + '='*60)
            self.stdout.write('To proceed, run:')
            self.stdout.write(self.style.SUCCESS(
                '  python manage.py reset_users --confirm'
            ))
            return

        # Delete all existing users
        user_count = User.objects.count()
        self.stdout.write(f'\nDeleting {user_count} existing users...')
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ All users deleted'))

        # Get or create departments
        it_dept, _ = Department.objects.get_or_create(
            name='IT Department',
            defaults={'description': 'Information Technology Department'}
        )
        hr_dept, _ = Department.objects.get_or_create(
            name='Human Resources',
            defaults={'description': 'Human Resources Department'}
        )

        # New users to create
        new_users = [
            {
                'username': 'deep',
                'email': 'deep@clouddownunder.com.au',
                'first_name': 'Deep',
                'last_name': 'Admin',
                'role': 'admin',
                'department': None,
                'password': 'deep@123'
            },
            {
                'username': 'arfin.kazi',
                'email': 'arfin.kazi@trilokninfotech.com',
                'first_name': 'Arfin',
                'last_name': 'Kazi',
                'role': 'hr',
                'department': hr_dept,
                'password': 'arfin.kazi@123'
            },
            {
                'username': 'pratik',
                'email': 'pratik@clouddownunder.com.au',
                'first_name': 'Pratik',
                'last_name': 'Manager',
                'role': 'manager',
                'department': None,
                'password': 'pratik@123'
            },
            {
                'username': 'yuvraj.shinde',
                'email': 'yuvraj.shinde@trilokninfotech.com',
                'first_name': 'Yuvraj',
                'last_name': 'Shinde',
                'role': 'it_admin',
                'department': it_dept,
                'password': 'yuvraj.shinde@123'
            },
            {
                'username': 'vijay.bhesaniya',
                'email': 'vijay.bhesaniya@trilokninfotech.com',
                'first_name': 'Vijay',
                'last_name': 'Bhesaniya',
                'role': 'employee',
                'department': it_dept,
                'password': 'vijay.bhesaniya@123'
            },
        ]

        self.stdout.write('\nCreating new users...\n')

        created_users = []
        for user_data in new_users:
            # Create user
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                password=user_data['password']
            )

            # Set staff status for admin
            if user_data['role'] == 'admin':
                user.is_staff = True
                user.is_superuser = True
                user.save()

            # Create user profile
            profile = UserProfile.objects.create(
                user=user,
                role=user_data['role'],
                department=user_data['department']
            )

            created_users.append({
                'username': user.username,
                'email': user.email,
                'role': profile.get_role_display(),
                'password': user_data['password']
            })

            self.stdout.write(self.style.SUCCESS(
                f"✓ Created: {user.username} ({profile.get_role_display()})"
            ))

        # Display credentials
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('\n✓ User creation completed!\n'))
        self.stdout.write('='*80)
        self.stdout.write('\nLogin Credentials:\n')
        self.stdout.write('-'*80)

        for user in created_users:
            self.stdout.write(
                f"Username: {user['username']:<20} "
                f"Email: {user['email']:<35} "
                f"Role: {user['role']:<12}"
            )
            self.stdout.write(f"Password: {user['password']}\n")

        self.stdout.write('='*80)
        self.stdout.write('\n⚠️  IMPORTANT: Save these credentials securely!')
        self.stdout.write('Users should change their passwords after first login.\n')
