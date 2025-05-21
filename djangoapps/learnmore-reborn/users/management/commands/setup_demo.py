from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import sys
import os

class Command(BaseCommand):
    help = 'Complete demo setup: creates demo accounts, sample courses, and demo content'

    def handle(self, *args, **options):
        try:
            # Check if settings allows demo content (only in non-production)
            if os.environ.get('DJANGO_ENV') == 'production' and not os.environ.get('ALLOW_DEMO_CONTENT'):
                self.stdout.write(self.style.WARNING('Demo setup is not allowed in production unless ALLOW_DEMO_CONTENT is set.'))
                self.stdout.write(self.style.WARNING('Set ALLOW_DEMO_CONTENT=1 to override this safety check.'))
                return

            self.stdout.write(self.style.NOTICE('Starting complete demo setup...'))
            
            # Step 1: Create demo accounts
            self.stdout.write(self.style.NOTICE('Step 1/3: Creating demo accounts...'))
            call_command('create_demo_accounts')
            
            # Step 2: Create sample courses, modules, and quizzes
            self.stdout.write(self.style.NOTICE('Step 2/3: Creating sample courses and content...'))
            # Check if the demo content script exists
            demo_content_path = os.path.join(settings.BASE_DIR, 'create_test_quiz.py')
            if os.path.exists(demo_content_path):
                from django.core.management import execute_from_command_line
                execute_from_command_line(['manage.py', 'shell', '-c', f'exec(open("{demo_content_path}").read())'])
                self.stdout.write(self.style.SUCCESS('Sample courses and quizzes created successfully!'))
            else:
                self.stdout.write(self.style.WARNING(f'Demo content script not found at {demo_content_path}'))
                self.stdout.write(self.style.WARNING('Skipping sample course creation. You can run it manually if needed.'))
            
            # Step 3: Set up enrollment relationships
            self.stdout.write(self.style.NOTICE('Step 3/3: Setting up enrollments and relationships...'))
            # Make the demo student enroll in any available courses
            from django.contrib.auth.models import User
            from courses.models import Course
            from courses.models import Enrollment
            
            try:
                student = User.objects.get(username='demo_student')
                courses = Course.objects.filter(is_published=True)
                
                if courses.exists():
                    for course in courses:
                        Enrollment.objects.get_or_create(
                            user=student, 
                            course=course,
                            defaults={'status': 'active'}
                        )
                    self.stdout.write(self.style.SUCCESS(f'Enrolled demo_student in {courses.count()} courses'))
                else:
                    self.stdout.write(self.style.WARNING('No published courses found for enrollment'))
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING('Demo student account not found. Skipping enrollments.'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error setting up enrollments: {str(e)}'))
            
            # Success message
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self.stdout.write(self.style.SUCCESS('Demo setup completed successfully!'))
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self.stdout.write(self.style.NOTICE('You can now access the platform with these accounts:'))
            self.stdout.write('')
            self.stdout.write(self.style.NOTICE('Admin:'))
            self.stdout.write('  Username: demo_admin')
            self.stdout.write('  Password: demopass123')
            self.stdout.write('')
            self.stdout.write(self.style.NOTICE('Instructor:'))
            self.stdout.write('  Username: demo_instructor')
            self.stdout.write('  Password: demopass123')
            self.stdout.write('')
            self.stdout.write(self.style.NOTICE('Student:'))
            self.stdout.write('  Username: demo_student')
            self.stdout.write('  Password: demopass123')
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('=' * 60))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during demo setup: {str(e)}'))
            sys.exit(1)