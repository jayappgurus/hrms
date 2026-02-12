from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employees.models import UserProfile


class Command(BaseCommand):
    help = 'Display and optionally update user roles in the system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all users and their current roles',
        )
        parser.add_argument(
            '--update',
            type=str,
            help='Update user role (format: username:role)',
        )

    def handle(self, *args, **options):
        if options['list']:
            self.list_users()
        elif options['update']:
            self.update_user_role(options['update'])
        else:
            self.stdout.write(self.style.WARNING('Please use --list or --update option'))
            self.stdout.write('Examples:')
            self.stdout.write('  python manage.py update_user_roles --list')
            self.stdout.write('  python manage.py update_user_roles --update username:admin')

    def list_users(self):
        """List all users and their roles"""
        self.stdout.write(self.style.SUCCESS('\n=== User Roles ===\n'))
        
        users = User.objects.select_related('profile').all()
        
        if not users:
            self.stdout.write(self.style.WARNING('No users found in the system'))
            return
        
        # Display header
        self.stdout.write(f"{'Username':<20} {'Email':<30} {'Role':<15} {'Department':<20}")
        self.stdout.write('-' * 85)
        
        for user in users:
            try:
                profile = user.profile
                role = profile.get_role_display()
                department = profile.department.name if profile.department else 'N/A'
            except UserProfile.DoesNotExist:
                role = 'No Profile'
                department = 'N/A'
            
            self.stdout.write(f"{user.username:<20} {user.email:<30} {role:<15} {department:<20}")
        
        self.stdout.write('\n')
        self.stdout.write(self.style.SUCCESS(f'Total users: {users.count()}'))
        
        # Display available roles
        self.stdout.write('\n=== Available Roles ===')
        for role_code, role_name in UserProfile.ROLE_CHOICES:
            self.stdout.write(f'  {role_code:<15} - {role_name}')

    def update_user_role(self, update_string):
        """Update a user's role"""
        try:
            username, new_role = update_string.split(':')
        except ValueError:
            self.stdout.write(self.style.ERROR('Invalid format. Use: username:role'))
            return
        
        # Validate role
        valid_roles = [role[0] for role in UserProfile.ROLE_CHOICES]
        if new_role not in valid_roles:
            self.stdout.write(self.style.ERROR(f'Invalid role: {new_role}'))
            self.stdout.write('Valid roles are:')
            for role_code, role_name in UserProfile.ROLE_CHOICES:
                self.stdout.write(f'  {role_code} - {role_name}')
            return
        
        # Get user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User not found: {username}'))
            return
        
        # Get or create profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        old_role = profile.get_role_display() if not created else 'None'
        
        # Update role
        profile.role = new_role
        profile.save()
        
        new_role_display = profile.get_role_display()
        
        if created:
            self.stdout.write(self.style.SUCCESS(
                f'Created profile for {username} with role: {new_role_display}'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Updated {username}: {old_role} → {new_role_display}'
            ))
