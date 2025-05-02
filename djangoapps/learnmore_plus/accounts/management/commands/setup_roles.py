from django.core.management.base import BaseCommand
from accounts.models import Role, create_default_roles
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from courses.models import Course, Module, CourseContent, Quiz, Question

class Command(BaseCommand):
    help = 'Sets up default roles and permissions for the system'

    def handle(self, *args, **kwargs):
        self.stdout.write('Setting up roles and permissions...')

        # Create default roles with permissions
        create_default_roles()
        self.stdout.write(self.style.SUCCESS('Created default roles'))

        # Create default groups
        student_group, _ = Group.objects.get_or_create(name='Students')
        instructor_group, _ = Group.objects.get_or_create(name='Instructors')
        coordinator_group, _ = Group.objects.get_or_create(name='Course Coordinators')
        admin_group, _ = Group.objects.get_or_create(name='Administrators')

        # Assign permissions to groups
        # Students
        student_permissions = Permission.objects.filter(
            content_type__app_label__in=['courses'],
            codename__in=['view_course', 'view_module', 'view_coursecontent']
        )
        student_group.permissions.set(student_permissions)

        # Instructors
        instructor_permissions = Permission.objects.filter(
            content_type__app_label__in=['courses'],
            codename__in=[
                'view_course', 'change_course', 'view_module', 'change_module',
                'view_coursecontent', 'change_coursecontent', 'view_quiz',
                'change_quiz', 'view_question', 'change_question'
            ]
        )
        instructor_group.permissions.set(instructor_permissions)

        # Course Coordinators
        coordinator_permissions = Permission.objects.filter(
            content_type__app_label__in=['courses', 'accounts'],
            codename__in=[
                'view_course', 'add_course', 'change_course', 'delete_course',
                'view_module', 'add_module', 'change_module', 'delete_module',
                'view_coursecontent', 'add_coursecontent', 'change_coursecontent',
                'delete_coursecontent', 'view_quiz', 'add_quiz', 'change_quiz',
                'delete_quiz', 'view_question', 'add_question', 'change_question',
                'delete_question', 'view_userprofile', 'change_userprofile'
            ]
        )
        coordinator_group.permissions.set(coordinator_permissions)

        # Administrators
        admin_permissions = Permission.objects.all()
        admin_group.permissions.set(admin_permissions)

        self.stdout.write(self.style.SUCCESS('Successfully set up roles and permissions')) 