from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta

from courses.models import Course, Module, Enrollment
from .models import Progress, ModuleProgress

@login_required
def learning_interface_view(request, module_id):
    """
    Display the learning interface for a specific module
    with progress tracking functionality
    """
    module = get_object_or_404(Module, id=module_id)
    course = module.course
    
    # Check if user is enrolled in the course
    enrollment = Enrollment.objects.filter(
        user=request.user,
        course=course,
        status='active'
    ).first()
    
    if not enrollment and not request.user.is_staff and request.user != course.instructor:
        messages.error(request, "You must be enrolled in this course to view its modules.")
        return redirect('course-detail', slug=course.slug)
    
    # Get or create progress record
    progress, created = Progress.objects.get_or_create(
        user=request.user,
        course=course
    )
    
    # Get or create module progress
    module_progress, created = ModuleProgress.objects.get_or_create(
        progress=progress,
        module=module
    )
    
    # If accessing for the first time, mark as in progress
    if created or module_progress.status == 'not_started':
        module_progress.status = 'in_progress'
        module_progress.save()
    
    # Get all modules for navigation
    course_modules = course.modules.all().order_by('order')
    
    # Get previous and next modules for navigation
    try:
        prev_module = course.modules.filter(order__lt=module.order).order_by('-order').first()
    except Module.DoesNotExist:
        prev_module = None
        
    try:
        next_module = course.modules.filter(order__gt=module.order).order_by('order').first()
    except Module.DoesNotExist:
        next_module = None
    
    # Get module progress status for all modules in this course
    module_progress_map = {}
    accessible_map = {}
    
    for m in course_modules:
        # Check if we have progress for this module
        mp = ModuleProgress.objects.filter(
            progress=progress, 
            module=m
        ).first()
        
        if mp:
            module_progress_map[m.id] = mp.status
        else:
            module_progress_map[m.id] = 'not_started'
        
        # Check if module is accessible (prerequisites completed)
        if not m.has_prerequisites:
            accessible_map[m.id] = True
        else:
            prereqs_completed = True
            for prereq in m.prerequisites.all():
                prereq_progress = ModuleProgress.objects.filter(
                    progress=progress,
                    module=prereq,
                    status='completed'
                ).exists()
                
                if not prereq_progress:
                    prereqs_completed = False
                    break
            
            accessible_map[m.id] = prereqs_completed
    
    # Get the next incomplete module for "Continue Learning" section
    next_incomplete_module = Module.objects.filter(
        course=course,
        order__gt=module.order,
        user_progress__status__in=['not_started', 'in_progress'],
        user_progress__progress=progress
    ).order_by('order').first()
    
    # If there are no incomplete modules after this one, 
    # suggest one that hasn't been completed yet
    if not next_incomplete_module:
        next_incomplete_module = Module.objects.filter(
            course=course,
            user_progress__status__in=['not_started', 'in_progress'],
            user_progress__progress=progress
        ).exclude(id=module.id).order_by('order').first()
    
    context = {
        'module': module,
        'course_modules': course_modules,
        'prev_module': prev_module,
        'next_module': next_module,
        'progress': progress,
        'module_progress': module_progress,
        'module_progress_map': module_progress_map,
        'module_accessible_map': accessible_map,
        'next_incomplete_module': next_incomplete_module,
    }
    
    return render(request, 'progress/learning-interface.html', context)

@login_required
def learning_statistics_view(request):
    """
    Display learning statistics for the current user
    """
    # Get API statistics
    from .api_views import ProgressViewSet
    stats_response = ProgressViewSet().stats(request).data
    
    # Calculate overall completion percentage
    completed_modules = stats_response['modules']['completed']
    total_modules = stats_response['modules']['total']
    
    if total_modules > 0:
        overall_completion = (completed_modules / total_modules) * 100
    else:
        overall_completion = 0
    
    # Get courses with progress for continue learning section
    progress_records = Progress.objects.filter(
        user=request.user,
        is_completed=False
    ).select_related('course').order_by('-last_accessed')[:3]
    
    continue_courses = []
    for progress in progress_records:
        next_module = progress.next_module
        if next_module:
            continue_courses.append({
                'title': progress.course.title,
                'slug': progress.course.slug,
                'completion_percentage': progress.completion_percentage,
                'next_module_id': next_module.id,
                'next_module_title': next_module.title
            })
    
    # Get course time distribution data
    course_time_data = Progress.objects.filter(
        user=request.user
    ).values('course__title').annotate(
        duration_seconds=Sum('total_duration_seconds')
    ).order_by('-duration_seconds')
    
    # Get recent activities
    recent_activities = []
    
    # Completed modules
    completed_modules = ModuleProgress.objects.filter(
        progress__user=request.user,
        status='completed'
    ).select_related('module', 'module__course').order_by('-completed_at')[:5]
    
    for mp in completed_modules:
        recent_activities.append({
            'type': 'completed',
            'title': f"Completed '{mp.module.title}' in {mp.module.course.title}",
            'timestamp': mp.completed_at
        })
    
    # Started modules
    started_modules = ModuleProgress.objects.filter(
        progress__user=request.user,
        status='in_progress'
    ).select_related('module', 'module__course').order_by('-last_activity')[:5]
    
    for mp in started_modules:
        recent_activities.append({
            'type': 'started',
            'title': f"Started '{mp.module.title}' in {mp.module.course.title}",
            'timestamp': mp.last_activity
        })
    
    # Sort by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = recent_activities[:10]  # Take only the 10 most recent
    
    context = {
        'stats': stats_response,
        'overall_completion': overall_completion,
        'continue_courses': continue_courses,
        'course_time_data': course_time_data,
        'recent_activities': recent_activities
    }
    
    return render(request, 'progress/learning-statistics.html', context)

@login_required
def learner_progress_view(request, course_id=None):
    """
    Display progress information for a specific course
    or all courses if no course_id provided
    """
    if course_id:
        # Show progress for specific course
        course = get_object_or_404(Course, id=course_id)
        progress, created = Progress.objects.get_or_create(
            user=request.user,
            course=course
        )
        
        # Get module progress for this course
        module_progress = ModuleProgress.objects.filter(
            progress=progress
        ).select_related('module').order_by('module__order')
        
        context = {
            'course': course,
            'progress': progress,
            'module_progress': module_progress
        }
        
        return render(request, 'progress/course-progress.html', context)
    else:
        # Show progress for all courses
        progress_records = Progress.objects.filter(
            user=request.user
        ).select_related('course').order_by('-last_accessed')
        
        context = {
            'progress_records': progress_records
        }
        
        return render(request, 'progress/learner-progress.html', context)
