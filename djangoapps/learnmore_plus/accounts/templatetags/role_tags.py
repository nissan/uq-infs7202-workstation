from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def has_role(user, role_name):
    """Check if user has a specific role."""
    if not user.is_authenticated:
        return False
        
    role_to_group = {
        'student': 'Student',
        'instructor': 'Instructor',
        'course_coordinator': 'Course Coordinator',
        'admin': 'Admin'
    }
    
    group_name = role_to_group.get(role_name)
    if not group_name:
        return False
        
    return user.groups.filter(name=group_name).exists()

@register.filter
def has_any_role(user, role_names):
    """Check if user has any of the specified roles."""
    if not user.is_authenticated:
        return False
        
    role_to_group = {
        'student': 'Student',
        'instructor': 'Instructor',
        'course_coordinator': 'Course Coordinator',
        'admin': 'Admin'
    }
    
    group_names = [role_to_group[role] for role in role_names.split(',') if role in role_to_group]
    return user.groups.filter(name__in=group_names).exists()

@register.filter
def has_course_permission(user, permission_data):
    """Check if user has specific course permission.
    Usage: {% if user|has_course_permission:"course,teach" %}
    """
    if not user.is_authenticated:
        return False
        
    try:
        course_slug, permission_type = permission_data.split(',')
        from courses.models import Course
        course = Course.objects.get(slug=course_slug)
        return user.profile.has_course_permission(course, permission_type)
    except:
        return False

@register.simple_tag
def get_user_role_display(user):
    """Get the display name of the user's role."""
    if not user.is_authenticated:
        return 'Guest'
        
    if user.groups.filter(name='Admin').exists():
        return 'Administrator'
    elif user.groups.filter(name='Course Coordinator').exists():
        return 'Course Coordinator'
    elif user.groups.filter(name='Instructor').exists():
        return 'Instructor'
    else:
        return 'Student' 