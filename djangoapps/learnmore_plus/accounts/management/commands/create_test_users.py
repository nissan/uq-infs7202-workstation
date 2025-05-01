from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile

class Command(BaseCommand):
    help = 'Creates test users for development and testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test users...')

        # Create admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin.set_password('admin123')
        admin.save()
        Profile.objects.get_or_create(user=admin)
        self.stdout.write(self.style.SUCCESS('Created/Updated admin user'))

        # Create test students
        john, created = User.objects.get_or_create(
            username='john',
            defaults={
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe'
            }
        )
        john.set_password('john123')
        john.save()
        Profile.objects.get_or_create(user=john)
        self.stdout.write(self.style.SUCCESS('Created/Updated student: John'))

        jane, created = User.objects.get_or_create(
            username='jane',
            defaults={
                'email': 'jane@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith'
            }
        )
        jane.set_password('jane123')
        jane.save()
        Profile.objects.get_or_create(user=jane)
        self.stdout.write(self.style.SUCCESS('Created/Updated student: Jane'))

        # Create instructor users
        dr_smith, created = User.objects.get_or_create(
            username='dr.smith',
            defaults={
                'email': 'smith@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'is_staff': True
            }
        )
        dr_smith.set_password('smith123')
        dr_smith.save()
        Profile.objects.get_or_create(user=dr_smith)
        self.stdout.write(self.style.SUCCESS('Created/Updated instructor: Dr. Smith'))

        dr_johnson, created = User.objects.get_or_create(
            username='dr.johnson',
            defaults={
                'email': 'johnson@example.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'is_staff': True
            }
        )
        dr_johnson.set_password('johnson123')
        dr_johnson.save()
        Profile.objects.get_or_create(user=dr_johnson)
        self.stdout.write(self.style.SUCCESS('Created/Updated instructor: Dr. Johnson'))

        self.stdout.write(self.style.SUCCESS('Successfully created/updated all test users')) 