from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.courses.models import Course, Content, Module, QuizAttempt, Quiz, Question

class Command(BaseCommand):
    help = 'Set up initial groups and permissions'

    def handle(self, *args, **kwargs):
        # Create groups
        groups = [
            'Student',
            'Instructor',
            'Course Coordinator',
            'Administrator',
        ]

        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(f'Created group: {group_name}')

        # Add course permissions to groups
        course_content_type = ContentType.objects.get_for_model(Course)
        course_permissions = Permission.objects.filter(content_type=course_content_type)

        # Student permissions
        student_group = Group.objects.get(name='Student')
        student_permissions = [
            'view_course',
        ]
        for perm in course_permissions:
            if perm.codename in student_permissions:
                student_group.permissions.add(perm)
        self.stdout.write('Added permissions to Student group')

        # Instructor permissions
        instructor_group = Group.objects.get(name='Instructor')
        instructor_permissions = [
            'view_course',
            'change_course',
            'add_course',
        ]
        for perm in course_permissions:
            if perm.codename in instructor_permissions:
                instructor_group.permissions.add(perm)
        self.stdout.write('Added permissions to Instructor group')

        # Course Coordinator permissions
        coordinator_group = Group.objects.get(name='Course Coordinator')
        coordinator_permissions = [
            'view_course',
            'change_course',
            'add_course',
            'delete_course',
            'publish_course',
            'archive_course',
        ]
        for perm in course_permissions:
            if perm.codename in coordinator_permissions:
                coordinator_group.permissions.add(perm)
        self.stdout.write('Added permissions to Course Coordinator group')

        # Administrator permissions
        admin_group = Group.objects.get(name='Administrator')
        admin_group.permissions.add(*course_permissions)
        self.stdout.write('Added all permissions to Administrator group')

        self.stdout.write(self.style.SUCCESS('Successfully set up groups and permissions')) 