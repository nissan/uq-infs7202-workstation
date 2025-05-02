from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import Group, Permission
from courses.models import (
    Course, Module, Content, Quiz, Question, Choice, CourseEnrollment, ModuleProgress, QuizAttempt
)

class Command(BaseCommand):
    help = 'Fully resets the database, runs migrations, sets up groups/permissions, and seeds demo data via API.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Flushing database...'))
        call_command('flush', '--no-input')

        self.stdout.write(self.style.WARNING('Running migrations...'))
        call_command('migrate')

        self.stdout.write(self.style.WARNING('Setting up groups and permissions...'))
        groups = {
            'Course Coordinator': ['Can manage courses', 'Can manage enrollments'],
            'Instructor': ['Can create courses', 'Can manage modules'],
            'Student': ['Can view courses', 'Can take quizzes']
        }
        for group_name, permissions in groups.items():
            group, created = Group.objects.get_or_create(name=group_name)
            for perm_name in permissions:
                try:
                    perm = Permission.objects.get(name=perm_name)
                    group.permissions.add(perm)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Permission not found: {perm_name}'))
        self.stdout.write(self.style.SUCCESS('Groups and permissions set up.'))

        self.stdout.write(self.style.WARNING('Seeding demo data via API...'))
        call_command('seed_demo_data_api')

        self.stdout.write(self.style.SUCCESS('System reset complete!'))
        self.stdout.write('')
        self.stdout.write('Test users created:')
        self.stdout.write('------------------')
        self.stdout.write('Admin:')
        self.stdout.write('  Username: admin')
        self.stdout.write('  Password: admin123')
        self.stdout.write('')
        self.stdout.write('Course Coordinator:')
        self.stdout.write('  Username: coordinator')
        self.stdout.write('  Password: coord123')
        self.stdout.write('')
        self.stdout.write('Instructors:')
        self.stdout.write('  Username: instructor1')
        self.stdout.write('  Password: inst123')
        self.stdout.write('  Username: instructor2')
        self.stdout.write('  Password: inst123')
        self.stdout.write('')
        self.stdout.write('Students:')
        self.stdout.write('  Username: student1')
        self.stdout.write('  Password: stud123')
        self.stdout.write('  Username: student2')
        self.stdout.write('  Password: stud123')
        self.stdout.write('')
        self.stdout.write('You can now run the development server with: python manage.py runserver') 