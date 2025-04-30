from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Sum, Count, Avg
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, CourseCategory, CourseEnrollment, CourseContent, Enrollment, Module, ModuleProgress
from django.utils import timezone

def course_catalog(request):
    # Get all categories for the filter sidebar
    categories = CourseCategory.objects.all()
    
    # Get the search query
    query = request.GET.get('search', '')
    
    # Get the selected categories
    selected_categories = request.GET.getlist('category')
    
    # Get the selected level
    selected_level = request.GET.get('level')
    
    # Get the price filter
    price_filter = request.GET.get('price')
    
    # Start with all published courses
    courses = Course.objects.filter(status='published')
    
    # Apply search filter
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    # Apply category filter
    if selected_categories:
        courses = courses.filter(category_id__in=selected_categories)
    
    # Apply level filter
    if selected_level:
        courses = courses.filter(level=selected_level)
    
    # Apply price filter
    if price_filter == 'free':
        courses = courses.filter(price=0)
    elif price_filter == 'paid':
        courses = courses.filter(price__gt=0)
    
    # Order by featured first, then by creation date
    courses = courses.order_by('-is_featured', '-created_at')
    
    context = {
        'courses': courses,
        'categories': categories,
        'query': query,
        'selected_categories': selected_categories,
        'selected_level': selected_level,
        'price_filter': price_filter,
        'levels': Course.LEVEL_CHOICES,
    }
    
    return render(request, 'courses/catalog.html', context)

def course_detail(request, slug):
    course = get_object_or_404(
        Course.objects.select_related('category', 'instructor')
        .prefetch_related('modules', 'modules__contents'),
        slug=slug,
        status='published'
    )
    
    # Check if user is enrolled
    is_enrolled = False
    enrollment = None
    if request.user.is_authenticated:
        enrollment = course.courseenrollment_set.filter(student=request.user).first()
        is_enrolled = enrollment is not None
    
    # Calculate total course duration
    total_duration = sum(
        content.estimated_time or 0
        for module in course.modules.all()
        for content in module.contents.all()
    )
    
    context = {
        'course': course,
        'modules': course.modules.all(),
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'total_duration': total_duration,
        'can_enroll': not is_enrolled and not course.is_full,
    }
    
    return render(request, 'courses/detail.html', context)

@login_required
def course_enroll(request, slug):
    course = get_object_or_404(Course, slug=slug, status='published')
    
    # Check if user is already enrolled in either model
    if (course.courseenrollment_set.filter(student=request.user).exists() or 
        Enrollment.objects.filter(student=request.user, course=course).exists()):
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('courses:detail', slug=slug)
    
    # Check if course is full
    if course.is_full:
        messages.error(request, 'This course is currently full.')
        return redirect('courses:detail', slug=slug)
    
    # Create CourseEnrollment
    course_enrollment = CourseEnrollment.objects.create(
        course=course,
        student=request.user,
        status='active'
    )
    
    # Create Enrollment
    enrollment = Enrollment.objects.create(
        course=course,
        student=request.user,
        status='not_started'
    )
    
    messages.success(request, f'Successfully enrolled in {course.title}')
    return redirect('courses:learn', slug=slug)

@login_required
def course_learn(request, slug, module_order=None, content_order=None):
    """View for the course learning page."""
    # Get course and verify enrollment
    course = get_object_or_404(
        Course.objects.prefetch_related('modules', 'modules__contents'),
        slug=slug
    )
    course_enrollment = get_object_or_404(CourseEnrollment, student=request.user, course=course)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    
    # Get current module (either from URL or first module)
    if module_order:
        current_module = get_object_or_404(Module, course=course, order=module_order)
    else:
        current_module = course.modules.first()
    
    # Get current content (either from URL or first content of current module)
    if content_order and current_module:
        current_content = get_object_or_404(CourseContent, module=current_module, order=content_order)
    else:
        current_content = current_module.contents.first() if current_module else None
    
    # Get next and previous content
    next_content = None
    prev_content = None
    if current_content:
        # Try to get next content in the same module
        next_content = current_module.contents.filter(order__gt=current_content.order).first()
        if not next_content:
            # If no next content in current module, try to get first content of next module
            next_module = course.modules.filter(order__gt=current_module.order).first()
            if next_module:
                next_content = next_module.contents.first()
        
        # Try to get previous content in the same module
        prev_content = current_module.contents.filter(order__lt=current_content.order).last()
        if not prev_content:
            # If no previous content in current module, try to get last content of previous module
            prev_module = course.modules.filter(order__lt=current_module.order).last()
            if prev_module:
                prev_content = prev_module.contents.last()
        
        # Calculate and update progress
        total_contents = sum(module.contents.count() for module in course.modules.all())
        completed_contents = 0
        
        # Count completed contents (contents in modules before current module)
        for module in course.modules.all():
            if module.order < current_module.order:
                completed_contents += module.contents.count()
            elif module == current_module:
                # Add contents completed in current module
                completed_contents += module.contents.filter(order__lt=current_content.order).count()
                # Add current content as completed
                completed_contents += 1
                break
        
        # Calculate progress percentage
        progress = int((completed_contents / total_contents) * 100) if total_contents > 0 else 0
        
        # Update both enrollment records if progress has increased
        if progress > course_enrollment.progress:
            # Update CourseEnrollment
            course_enrollment.progress = progress
            if progress == 100:
                course_enrollment.status = 'completed'
                course_enrollment.completed_at = timezone.now()
            course_enrollment.save()
            
            # Update Enrollment
            enrollment.progress = progress
            if progress == 100:
                enrollment.status = 'completed'
                enrollment.completed_at = timezone.now()
            elif progress > 0:
                enrollment.status = 'in_progress'
            enrollment.save()
            
            # Update ModuleProgress
            module_progress, created = ModuleProgress.objects.get_or_create(
                enrollment=enrollment,
                module=current_module,
                defaults={'status': 'in_progress', 'progress': 0}
            )
            module_progress.last_accessed = timezone.now()
            module_progress.save()
    
    context = {
        'course': course,
        'enrollment': course_enrollment,  # Use CourseEnrollment for the template
        'current_module': current_module,
        'current_content': current_content,
        'next_content': next_content,
        'prev_content': prev_content,
        'modules': course.modules.all(),  # All modules for navigation
    }
    return render(request, 'courses/learn.html', context)

@login_required
def dashboard(request):
    """View for the student dashboard showing enrolled courses and progress."""
    # Get all enrollments for the current user
    enrollments = CourseEnrollment.objects.filter(
        student=request.user,
        status__in=['active', 'completed']
    ).select_related(
        'course',
        'course__category',
        'course__instructor'
    ).prefetch_related(
        'course__modules',
        'course__modules__contents'
    ).order_by('-enrolled_at')

    # Calculate additional course information
    for enrollment in enrollments:
        course = enrollment.course
        # Calculate total duration
        course.total_duration = sum(
            content.estimated_time or 0
            for module in course.modules.all()
            for content in module.contents.all()
        )
        # Calculate time spent (placeholder - you might want to track this separately)
        course.time_spent = int(course.total_duration * (enrollment.progress / 100))
        # Calculate time remaining
        course.time_remaining = course.total_duration - course.time_spent
        # Get last accessed module and content
        last_module = course.modules.filter(order__lte=enrollment.progress).last()
        if last_module:
            course.last_accessed = f"Module {last_module.order}: {last_module.title}"
        else:
            course.last_accessed = "Not started"

    context = {
        'enrollments': enrollments,
        'total_courses': enrollments.count(),
        'completed_courses': enrollments.filter(status='completed').count(),
        'in_progress_courses': enrollments.filter(status='active').count(),
    }
    return render(request, 'courses/dashboard.html', context)

@login_required
def student_dashboard(request):
    """
    Student dashboard view showing recent courses and overview statistics
    """
    # Get student's enrollments
    all_enrollments = Enrollment.objects.filter(student=request.user).select_related(
        'course', 'course__category'
    ).order_by('-enrolled_at')

    # Calculate statistics before slicing
    total_courses = all_enrollments.count()
    in_progress = all_enrollments.filter(status='in_progress').count()
    completed = all_enrollments.filter(status='completed').count()

    # Get 5 most recent enrollments
    recent_enrollments = all_enrollments[:5]

    context = {
        'enrollments': recent_enrollments,
        'total_courses': total_courses,
        'in_progress': in_progress,
        'completed': completed,
        'recent_activity': get_recent_activity(request.user),
        'upcoming_deadlines': get_upcoming_deadlines(request.user),
    }
    
    return render(request, 'courses/student/dashboard.html', context)

@login_required
def learning_progress(request):
    """
    Detailed learning progress view showing all enrolled courses and detailed statistics
    """
    # Get all student's enrollments with related data
    enrollments = Enrollment.objects.filter(student=request.user).select_related(
        'course', 'course__category'
    ).prefetch_related(
        'module_progress',
        'course__modules',
        'course__modules__contents'
    ).order_by('-enrolled_at')

    # Calculate overall statistics
    total_courses = enrollments.count()
    module_progress = ModuleProgress.objects.filter(enrollment__student=request.user)
    completed_modules = module_progress.filter(status='completed').count()
    total_modules = Module.objects.filter(course__enrollments__student=request.user).count()
    
    # Calculate time statistics
    time_stats = module_progress.aggregate(
        total_time=Sum('time_spent'),
        avg_completion=Avg('progress')
    )
    
    # Calculate time spent and remaining for each course
    for enrollment in enrollments:
        course = enrollment.course
        # Calculate total course duration
        total_duration = sum(
            content.estimated_time or 0
            for module in course.modules.all()
            for content in module.contents.all()
        )
        # Calculate time spent based on progress
        time_spent = int(total_duration * (enrollment.progress / 100))
        # Calculate time remaining
        time_remaining = total_duration - time_spent
        
        # Add time information to course object
        course.total_duration = total_duration
        course.time_spent = time_spent
        course.time_remaining = time_remaining
        
        # Get last accessed module
        last_module = course.modules.filter(order__lte=enrollment.progress).last()
        if last_module:
            course.last_accessed = f"Module {last_module.order}: {last_module.title}"
        else:
            course.last_accessed = "Not started"
    
    context = {
        'enrollments': enrollments,
        'total_courses': total_courses,
        'completed_modules': completed_modules,
        'total_modules': total_modules,
        'total_time_spent': time_stats['total_time'] or 0,
        'avg_completion': round(time_stats['avg_completion'] or 0),
    }
    
    return render(request, 'courses/student/progress.html', context)

def get_recent_activity(user):
    """Helper function to get user's recent activity"""
    return ModuleProgress.objects.filter(
        enrollment__student=user,
        last_accessed__isnull=False
    ).select_related(
        'module', 'enrollment__course'
    ).order_by('-last_accessed')[:5]

def get_upcoming_deadlines(user):
    """Helper function to get user's upcoming deadlines"""
    now = timezone.now()
    return Module.objects.filter(
        course__enrollments__student=user,
        deadline__gt=now
    ).select_related('course').order_by('deadline')[:5]
