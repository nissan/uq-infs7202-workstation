from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from accounts.models import UserProfile
from courses.models import Course

class Command(BaseCommand):
    help = 'Creates test users with different groups and course assignments'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test users...')

        # Create groups if they don't exist
        student_group, _ = Group.objects.get_or_create(name='Student')
        instructor_group, _ = Group.objects.get_or_create(name='Instructor')
        coordinator_group, _ = Group.objects.get_or_create(name='Course Coordinator')
        admin_group, _ = Group.objects.get_or_create(name='Administrator')

        # Create admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        admin.groups.set([admin_group])
        self.stdout.write('Created/Updated admin user')

        # Create course coordinator
        coordinator, created = User.objects.get_or_create(
            username='coordinator',
            defaults={
                'email': 'coordinator@example.com',
                'first_name': 'Course',
                'last_name': 'Coordinator',
                'is_staff': True
            }
        )
        if created:
            coordinator.set_password('coord123')
            coordinator.save()
        coordinator.groups.set([coordinator_group])
        self.stdout.write('Created/Updated course coordinator')

        # Create instructors
        instructors = [
            {
                'username': 'dr.smith',
                'email': 'dr.smith@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'password': 'dr.smith123',
                'title': 'Dr.'
            },
            {
                'username': 'dr.johnson',
                'email': 'dr.johnson@example.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'password': 'dr.johnson123',
                'title': 'Dr.'
            },
            {
                'username': 'prof.williams',
                'email': 'prof.williams@example.com',
                'first_name': 'Michael',
                'last_name': 'Williams',
                'password': 'prof.williams123',
                'title': 'Prof.'
            }
        ]

        for instructor_data in instructors:
            instructor, created = User.objects.get_or_create(
                username=instructor_data['username'],
                defaults={
                    'email': instructor_data['email'],
                    'first_name': instructor_data['first_name'],
                    'last_name': instructor_data['last_name'],
                    'is_staff': True
                }
            )
            if created:
                instructor.set_password(instructor_data['password'])
                instructor.save()
            instructor.groups.set([instructor_group])
            self.stdout.write(f'Created/Updated instructor: {instructor.first_name} {instructor.last_name}')

        # Create students
        students_data = [
            {
                'username': 'john.doe',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe'
            },
            {
                'username': 'jane.smith',
                'email': 'jane@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith'
            },
            {
                'username': 'bob.wilson',
                'email': 'bob@example.com',
                'first_name': 'Bob',
                'last_name': 'Wilson'
            },
            {
                'username': 'alice.johnson',
                'email': 'alice@example.com',
                'first_name': 'Alice',
                'last_name': 'Johnson'
            }
        ]

        for student_data in students_data:
            student, created = User.objects.get_or_create(
                username=student_data['username'],
                defaults=student_data
            )
            student.set_password(f"{student_data['username']}123")
            student.save()
            student.groups.add(student_group)
            UserProfile.objects.get_or_create(user=student)
            self.stdout.write(self.style.SUCCESS(f'Created/Updated student: {student.get_full_name()}'))

        # Assign courses to instructors and coordinator
        try:
            # Get some courses to assign
            courses = Course.objects.all()[:3]  # Get first 3 courses
            
            # Assign courses to coordinator
            coordinator_profile = coordinator.profile
            coordinator_profile.managed_courses.add(*courses)
            
            # Assign courses to instructors
            dr_smith = User.objects.get(username='dr.smith')
            dr_johnson = User.objects.get(username='dr.johnson')
            prof_williams = User.objects.get(username='prof.williams')
            
            # Assign courses to instructors
            dr_smith.profile.teaching_courses.add(courses[0])
            dr_johnson.profile.teaching_courses.add(courses[1])
            prof_williams.profile.teaching_courses.add(courses[2])
            
            self.stdout.write(self.style.SUCCESS('Assigned courses to instructors and coordinator'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not assign courses: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Successfully created/updated all test users')) 