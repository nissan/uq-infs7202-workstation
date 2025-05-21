from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile
from django.conf import settings
import sys
import os

class Command(BaseCommand):
    help = 'Creates a set of demo accounts (admin, instructor, student) for demonstration purposes'

    def handle(self, *args, **options):
        try:
            # Check if settings allows demo accounts (only in non-production)
            if os.environ.get('DJANGO_ENV') == 'production' and not os.environ.get('ALLOW_DEMO_ACCOUNTS'):
                self.stdout.write(self.style.WARNING('Demo accounts are not allowed in production unless ALLOW_DEMO_ACCOUNTS is set.'))
                self.stdout.write(self.style.WARNING('Set ALLOW_DEMO_ACCOUNTS=1 to override this safety check.'))
                return

            self.stdout.write(self.style.NOTICE('Creating demo accounts...'))
            
            # Create demo admin account
            admin_user, admin_created = User.objects.get_or_create(
                username='demo_admin',
                email='admin@example.com',
                defaults={
                    'first_name': 'Demo',
                    'last_name': 'Admin',
                    'is_staff': True,
                    'is_superuser': True,
                }
            )
            
            if admin_created:
                admin_user.set_password('demopass123')
                admin_user.save()
                self.stdout.write(self.style.SUCCESS(f'Created admin account: {admin_user.username}'))
            else:
                admin_user.set_password('demopass123')
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.save()
                self.stdout.write(self.style.SUCCESS(f'Updated existing admin account: {admin_user.username}'))
            
            # Create demo instructor account
            instructor_user, instructor_created = User.objects.get_or_create(
                username='demo_instructor',
                email='instructor@example.com',
                defaults={
                    'first_name': 'Demo',
                    'last_name': 'Instructor',
                }
            )
            
            if instructor_created:
                instructor_user.set_password('demopass123')
                instructor_user.save()
                instructor_profile = instructor_user.profile
                instructor_profile.is_instructor = True
                instructor_profile.department = 'Computer Science'
                instructor_profile.bio = 'Demo instructor account for the LearnMore platform.'
                instructor_profile.save()
                self.stdout.write(self.style.SUCCESS(f'Created instructor account: {instructor_user.username}'))
            else:
                instructor_user.set_password('demopass123')
                instructor_user.save()
                instructor_profile = instructor_user.profile
                instructor_profile.is_instructor = True
                instructor_profile.department = 'Computer Science'
                instructor_profile.save()
                self.stdout.write(self.style.SUCCESS(f'Updated existing instructor account: {instructor_user.username}'))
            
            # Create demo student account
            student_user, student_created = User.objects.get_or_create(
                username='demo_student',
                email='student@example.com',
                defaults={
                    'first_name': 'Demo',
                    'last_name': 'Student',
                }
            )
            
            if student_created:
                student_user.set_password('demopass123')
                student_user.save()
                student_profile = student_user.profile
                student_profile.student_id = 's123456'
                student_profile.department = 'Information Technology'
                student_profile.bio = 'Demo student account for the LearnMore platform.'
                student_profile.save()
                self.stdout.write(self.style.SUCCESS(f'Created student account: {student_user.username}'))
            else:
                student_user.set_password('demopass123')
                student_user.save()
                student_profile = student_user.profile
                student_profile.student_id = 's123456'
                student_profile.department = 'Information Technology'
                student_profile.save()
                self.stdout.write(self.style.SUCCESS(f'Updated existing student account: {student_user.username}'))
            
            # Summary
            self.stdout.write(self.style.SUCCESS('-' * 40))
            self.stdout.write(self.style.SUCCESS('Demo accounts created successfully!'))
            self.stdout.write(self.style.SUCCESS('-' * 40))
            self.stdout.write(self.style.NOTICE('Admin Account:'))
            self.stdout.write(f'  Username: demo_admin')
            self.stdout.write(f'  Password: demopass123')
            self.stdout.write(f'  Email: admin@example.com')
            self.stdout.write(self.style.NOTICE('Instructor Account:'))
            self.stdout.write(f'  Username: demo_instructor')
            self.stdout.write(f'  Password: demopass123')
            self.stdout.write(f'  Email: instructor@example.com')
            self.stdout.write(self.style.NOTICE('Student Account:'))
            self.stdout.write(f'  Username: demo_student')
            self.stdout.write(f'  Password: demopass123')
            self.stdout.write(f'  Email: student@example.com')
            self.stdout.write(self.style.SUCCESS('-' * 40))
            self.stdout.write(self.style.WARNING('Note: For production use, change these passwords immediately after deployment.'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating demo accounts: {str(e)}'))
            sys.exit(1)