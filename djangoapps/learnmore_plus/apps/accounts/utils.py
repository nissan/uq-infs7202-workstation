from django.db.models import Q
from apps.courses.models import Course, CourseEnrollment

def get_user_courses(user, role_type):
    """
    Get courses associated with a user based on their role type.
    
    Args:
        user: The user object
        role_type: One of 'teach', 'manage', or 'learn'
        
    Returns:
        QuerySet of Course objects
    """
    if role_type == 'teach':
        # Get courses where user is an instructor
        return Course.objects.filter(instructors=user)
    elif role_type == 'manage':
        # Get courses where user is a coordinator
        return Course.objects.filter(coordinator=user)
    elif role_type == 'learn':
        # Get courses where user is enrolled
        return Course.objects.filter(
            courseenrollment__user=user,
            courseenrollment__is_active=True
        )
    return Course.objects.none()

def get_course_permissions(user, course):
    """
    Get a user's permissions for a specific course.
    
    Args:
        user: The user object
        course: The Course object
        
    Returns:
        dict: Dictionary of permission flags
    """
    permissions = {
        'view': False,
        'teach': False,
        'manage': False,
    }
    
    if not user.is_authenticated:
        return permissions

    # Check if user is administrator
    if user.groups.filter(name='Administrator').exists():
        permissions['view'] = True
        permissions['teach'] = True
        permissions['manage'] = True
        return permissions
        
    # Check if user is enrolled
    is_enrolled = CourseEnrollment.objects.filter(
        student=user,
        course=course,
        status='active'
    ).exists()
    
    # Check if user is instructor
    is_instructor = course.instructors.filter(id=user.id).exists()
    
    # Check if user is coordinator
    is_coordinator = course.coordinator_id == user.id
    
    # Check if user is course coordinator (group)
    is_course_coordinator = user.groups.filter(name='Course Coordinator').exists()
    
    # Set permissions based on roles
    if is_enrolled or course.status == 'published':
        permissions['view'] = True
    if is_instructor:
        permissions['view'] = True
        permissions['teach'] = True
    if is_coordinator or is_course_coordinator:
        permissions['view'] = True
        permissions['teach'] = True
        permissions['manage'] = True
        
    return permissions 