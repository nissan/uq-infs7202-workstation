from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

class Command(BaseCommand):
    help = 'Verifies the admin user exists and has correct credentials'

    def handle(self, *args, **kwargs):
        # Check if admin user exists
        try:
            admin = User.objects.get(username='admin')
            self.stdout.write(f'Admin user exists with email: {admin.email}')
            self.stdout.write(f'Is staff: {admin.is_staff}')
            self.stdout.write(f'Is superuser: {admin.is_superuser}')
            
            # Check group membership
            admin_groups = admin.groups.all()
            self.stdout.write('Admin groups:')
            for group in admin_groups:
                self.stdout.write(f'- {group.name}')
            
            # Verify password
            if admin.check_password('admin123'):
                self.stdout.write(self.style.SUCCESS('Password is correct'))
            else:
                self.stdout.write(self.style.ERROR('Password is incorrect'))
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Admin user does not exist')) 