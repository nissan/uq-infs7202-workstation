from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class UserProfile(models.Model):
    """
    Extended user profile with group-based permissions.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    
    # Course-specific permissions
    managed_courses = models.ManyToManyField('courses.Course', blank=True, related_name='managers')
    teaching_courses = models.ManyToManyField('courses.Course', related_name='teaching_profiles', blank=True)
    enrolled_courses = models.ManyToManyField('courses.Course', related_name='enrolled_profiles', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_primary_group(self):
        """Get the user's primary group (highest privilege)."""
        group_priority = {
            'Administrator': 4,
            'Course Coordinator': 3,
            'Instructor': 2,
            'Student': 1
        }
        
        user_groups = self.user.groups.all()
        if not user_groups:
            return None
            
        return max(user_groups, key=lambda g: group_priority.get(g.name, 0))

    def has_course_permission(self, course, permission_type):
        """
        Check if user has specific permission for a course.
        permission_type can be: 'view', 'edit', 'manage', 'teach'
        """
        if self.user.is_superuser:
            return True

        if permission_type == 'teach':
            return course in self.teaching_courses.all()
        elif permission_type == 'manage':
            return course in self.managed_courses.all()
        elif permission_type == 'edit':
            return (course in self.teaching_courses.all() or 
                   course in self.managed_courses.all())
        elif permission_type == 'view':
            return True  # All authenticated users can view courses
        return False

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create profile
        profile = UserProfile.objects.create(user=instance)
        # Add to Student group by default
        student_group = Group.objects.get(name='Student')
        instance.groups.add(student_group)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        # If profile doesn't exist, create it
        profile = UserProfile.objects.create(user=instance)
        # Add to Student group by default
        student_group = Group.objects.get(name='Student')
        instance.groups.add(student_group)

class ModuleNotes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module_id = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'module_id']
        verbose_name = 'Module Notes'
        verbose_name_plural = 'Module Notes'

    def __str__(self):
        return f"{self.user.username}'s notes for {self.module_id}"

def create_default_groups():
    """
    Create default groups with appropriate permissions.
    """
    # Student group
    student_group, _ = Group.objects.get_or_create(name='Student')
    student_permissions = Permission.objects.filter(
        content_type__app_label__in=['courses'],
        codename__in=['view_course', 'view_module', 'view_coursecontent']
    )
    student_group.permissions.set(student_permissions)

    # Instructor group
    instructor_group, _ = Group.objects.get_or_create(name='Instructor')
    instructor_permissions = Permission.objects.filter(
        content_type__app_label__in=['courses'],
        codename__in=[
            'view_course', 'change_course', 'view_module', 'change_module',
            'view_coursecontent', 'change_coursecontent', 'view_quiz',
            'change_quiz', 'view_question', 'change_question'
        ]
    )
    instructor_group.permissions.set(instructor_permissions)

    # Course Coordinator group
    coordinator_group, _ = Group.objects.get_or_create(name='Course Coordinator')
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

    # Administrator group
    admin_group, _ = Group.objects.get_or_create(name='Administrator')
    admin_permissions = Permission.objects.all()
    admin_group.permissions.set(admin_permissions)
