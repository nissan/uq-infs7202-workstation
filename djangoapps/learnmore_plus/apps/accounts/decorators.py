import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.core.exceptions import PermissionDenied
from apps.courses.models import Course

logger = logging.getLogger(__name__)

def group_required(groups):
    """
    Decorator for views that checks whether a user has the required group.
    
    Args:
        groups: List of group names or single group name
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in to access this page.')
                return redirect('accounts:login')
                
            if isinstance(groups, str):
                group_list = [groups]
            else:
                group_list = groups
                
            # Check if user has any of the required groups
            if request.user.groups.filter(name__in=group_list).exists():
                return view_func(request, *args, **kwargs)
                
            raise PermissionDenied('You do not have permission to access this page.')
            
        return _wrapped_view
    return decorator

def instructor_required(view_func):
    """Decorator for views that require instructor group."""
    return group_required(['Instructor', 'Course Coordinator', 'Administrator'])(view_func)

def coordinator_required(view_func):
    """Decorator for views that require course coordinator group."""
    return group_required(['Course Coordinator', 'Administrator'])(view_func)

def admin_required(view_func):
    """Decorator for views that require admin group."""
    return group_required(['Administrator'])(view_func)

def course_permission_required(permission_type):
    """
    Decorator for views that checks whether a user has the required course permission.
    
    Args:
        permission_type: Type of permission ('view', 'teach', 'manage')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            try:
                if not request.user.is_authenticated:
                    logger.info(f"Unauthenticated user attempted to access course view")
                    messages.error(request, 'Please log in to access this page.')
                    return redirect('accounts:login')
                    
                # Get course from kwargs
                course_slug = kwargs.get('slug') or kwargs.get('course_slug')
                if not course_slug:
                    logger.error("Course slug not found in view kwargs")
                    raise ValueError('Course slug not found in view kwargs')
                    
                # Import here to avoid circular import
                from apps.courses.models import Course
                course = Course.objects.get(slug=course_slug)
                
                # Check permission
                from apps.accounts.utils import get_course_permissions
                permissions = get_course_permissions(request.user, course)
                
                if permissions.get(permission_type):
                    logger.info(f"User {request.user} granted {permission_type} permission for course {course.title}")
                    return view_func(request, *args, **kwargs)
                
                logger.warning(f"User {request.user} denied {permission_type} permission for course {course.title}")
                messages.error(request, 'You do not have permission to access this course.')
                return redirect('courses:course_catalog')
                
            except Course.DoesNotExist:
                logger.error(f"Course with slug {course_slug} not found")
                messages.error(request, 'Course not found.')
                return redirect('courses:course_catalog')
            except Exception as e:
                logger.error(f"Error in course permission check: {str(e)}")
                messages.error(request, 'An error occurred while checking permissions.')
                return redirect('courses:course_catalog')
                
        return _wrapped_view
    return decorator 