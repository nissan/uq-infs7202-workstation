from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from django.db import transaction
from .models import Course, Category, CourseEnrollment, Content, Module, ModuleProgress, QuizAttempt
from apps.accounts.decorators import group_required, course_permission_required
from apps.accounts.utils import get_user_courses, get_course_permissions
from apps.qr_codes.services import QRCodeService
from django.urls import reverse
import logging
from django.contrib.auth.models import User
from .forms import CourseForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

logger = logging.getLogger(__name__)

def course_catalog(request):
    """Public view for course catalog."""
    categories = Category.objects.all()
    current_category = request.GET.get('category')
    search_query = request.GET.get('q')
    
    courses = Course.objects.filter(status='published')
    
    if current_category:
        courses = courses.filter(category__slug=current_category)
    
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    context = {
        'categories': categories,
        'courses': courses,
        'current_category': current_category,
        'search_query': search_query,
    }
    return render(request, 'courses/catalog.html', context)

def course_detail(request, slug):
    """Public view for course details with proper status validation."""
    try:
        course = get_object_or_404(Course, slug=slug)
        
        # Check if user can view unpublished courses
        if course.status != 'published' and not request.user.has_perm('courses.view_course'):
            logger.warning(f"User {request.user} attempted to view unpublished course {course.title}")
            messages.error(request, 'This course is not available.')
            return redirect('courses:course_catalog')
        
        # Get enrollment status
        is_enrolled = False
        enrollment = None
        if request.user.is_authenticated:
            enrollment = CourseEnrollment.objects.filter(
                student=request.user,
                course=course,
                status='active'
            ).first()
            is_enrolled = enrollment is not None
        
        # Get course statistics
        total_duration = 0
        for module in course.modules.all():
            for content in module.contents.all():
                if content.estimated_time:
                    total_duration += content.estimated_time
        
        # Generate or retrieve QR code for the course
        course_url = request.build_absolute_uri(reverse('courses:course_detail', kwargs={'slug': course.slug}))
        course_qr_code = QRCodeService.get_or_create_qr_code(course, course_url)
        
        # Generate QR codes for each module
        modules = course.modules.all().prefetch_related('contents')
        module_qr_codes = {}
        for module in modules:
            module_url = request.build_absolute_uri(
                reverse('courses:learn_module', kwargs={'slug': course.slug, 'module_order': module.order})
            )
            module_qr_codes[module.id] = QRCodeService.get_or_create_qr_code(module, module_url)
        
        context = {
            'course': course,
            'is_enrolled': is_enrolled,
            'enrollment': enrollment,
            'total_duration': total_duration,
            'modules': modules,
            'course_qr_code': course_qr_code,
            'module_qr_codes': module_qr_codes,
        }
        return render(request, 'courses/detail.html', context)
        
    except Exception as e:
        logger.error(f"Error viewing course {slug}: {str(e)}")
        messages.error(request, 'An error occurred while loading the course.')
        return redirect('courses:course_catalog')

@login_required
@transaction.atomic
def course_enroll(request, slug):
    """Student enrollment view with transaction handling."""
    try:
        course = get_object_or_404(Course, slug=slug, status='published')
        
        # Check if already enrolled
        if CourseEnrollment.objects.filter(student=request.user, course=course).exists():
            logger.info(f"User {request.user} attempted to re-enroll in course {course.title}")
            messages.warning(request, 'You are already enrolled in this course.')
            return redirect('courses:course_detail', slug=slug)
        
        # Check course capacity
        if course.max_students > 0:
            current_enrollments = CourseEnrollment.objects.filter(
                course=course, 
                status='active'
            ).count()
            if current_enrollments >= course.max_students:
                logger.warning(f"Course {course.title} reached maximum capacity")
                messages.error(request, 'This course has reached its maximum capacity.')
                return redirect('courses:course_detail', slug=slug)
        
        # Create enrollment
        enrollment = CourseEnrollment.objects.create(
            student=request.user,
            course=course,
            status='active',
            enrolled_at=timezone.now()
        )
        
        # Create module progress records
        for module in course.modules.all():
            ModuleProgress.objects.create(
                enrollment=enrollment,
                module=module,
                status='not_started'
            )
        
        logger.info(f"User {request.user} successfully enrolled in course {course.title}")
        messages.success(request, f'Successfully enrolled in {course.title}')
        return redirect('courses:course_learn', slug=slug)
        
    except Exception as e:
        logger.error(f"Enrollment failed for user {request.user} in course {slug}: {str(e)}")
        messages.error(request, 'An error occurred during enrollment. Please try again.')
        return redirect('courses:course_detail', slug=slug)

@login_required
def course_learn(request, slug, module_order=None, content_order=None):
    """Learning interface view."""
    try:
        course = get_object_or_404(Course, slug=slug)
        
        # Check if user has permission to view the course
        permissions = get_course_permissions(request.user, course)
        
        if not permissions['view']:
            messages.error(request, 'You do not have permission to access this course.')
            return redirect('courses:course_catalog')
        
        # For students, check if they are enrolled
        if not any([
            request.user.groups.filter(name__in=['Instructor', 'Course Coordinator', 'Administrator']).exists(),
            course.instructors.filter(id=request.user.id).exists(),
            course.coordinator_id == request.user.id
        ]):
            enrollment = CourseEnrollment.objects.filter(
                student=request.user,
                course=course,
                status='active'
            ).first()
            
            if not enrollment:
                messages.error(request, 'You must be enrolled in this course to access its content.')
                return redirect('courses:course_detail', slug=slug)
        else:
            enrollment = None
        
        # Get modules with their contents
        modules = course.modules.all().prefetch_related('contents').order_by('order')
        
        # Get current module and content if specified
        current_module = None
        current_content = None
        prev_content = None
        next_content = None
        attempt = None
        
        if module_order is not None:
            try:
                current_module = modules.get(order=module_order)
                
                if content_order is not None:
                    current_content = current_module.contents.get(order=content_order)
                    
                    # Get previous and next content
                    contents = list(current_module.contents.all().order_by('order'))
                    current_index = contents.index(current_content)
                    
                    if current_index > 0:
                        prev_content = contents[current_index - 1]
                    if current_index < len(contents) - 1:
                        next_content = contents[current_index + 1]
                    
                    # If content is a quiz, create or get an attempt
                    if current_content.content_type == 'quiz' and current_content.quiz:
                        # Get or create a quiz attempt
                        attempt = QuizAttempt.objects.filter(
                            student=request.user,
                            quiz=current_content.quiz,
                            status='in_progress'
                        ).first()
                        
                        if not attempt:
                            # Check if user has remaining attempts
                            attempts = current_content.quiz.attempts.filter(student=request.user)
                            if current_content.quiz.attempts_allowed > 0 and attempts.count() >= current_content.quiz.attempts_allowed:
                                messages.error(request, 'You have used all your attempts for this quiz.')
                                return redirect('courses:course_learn', slug=slug)
                            
                            # Create new attempt
                            attempt = QuizAttempt.objects.create(
                                student=request.user,
                                quiz=current_content.quiz,
                                status='in_progress'
                            )
                    
            except (Module.DoesNotExist, Content.DoesNotExist):
                messages.error(request, 'The requested content could not be found.')
                return redirect('courses:course_learn', slug=slug)
        
        context = {
            'course': course,
            'enrollment': enrollment,
            'modules': modules,
            'current_module': current_module,
            'current_content': current_content,
            'prev_content': prev_content,
            'next_content': next_content,
            'attempt': attempt,
        }
        return render(request, 'courses/learn.html', context)
        
    except Exception as e:
        logger.error(f"Error accessing course content for {slug}: {str(e)}")
        messages.error(request, 'An error occurred while loading the course content.')
        return redirect('courses:course_catalog')

@login_required
def student_dashboard(request):
    """Student dashboard view with error handling."""
    try:
        # Get enrollments with course and module progress info
        enrollments = CourseEnrollment.objects.filter(
            student=request.user,
            status='active'
        ).select_related('course').prefetch_related('module_progress')

        context = {
            'enrollments': enrollments,
        }
        return render(request, 'courses/student/dashboard.html', context)
    except Exception as e:
        # Log the error
        logger.error(f"Error in student dashboard for user {request.user.username}: {str(e)}")
        
        # Add error message
        messages.error(request, "There was a problem loading your dashboard. Please try again later.")
        
        # Redirect to home
        return redirect('core:home')

@login_required
@group_required(['Instructor', 'Course Coordinator', 'Administrator'])
def instructor_dashboard(request):
    """Instructor dashboard view."""
    # Get courses where user is instructor
    courses = Course.objects.filter(instructors=request.user).annotate(
        active_enrollments=Count('enrollments', filter=Q(enrollments__status='active')),
        completed_enrollments=Count('enrollments', filter=Q(enrollments__status='completed')),
        avg_progress=Avg('enrollments__progress')
    ).order_by('-active_enrollments')

    # For each course, get active enrollments with student and module progress
    course_enrollments = {}
    for course in courses:
        enrollments = CourseEnrollment.objects.filter(
            course=course, status='active'
        ).select_related('student').prefetch_related('module_progress__module')
        course_enrollments[course.id] = enrollments

    context = {
        'courses': courses,
        'course_enrollments': course_enrollments,
    }
    return render(request, 'courses/instructor/dashboard.html', context)

@login_required
@group_required(['Course Coordinator', 'Administrator'])
def coordinator_dashboard(request):
    """Course Coordinator dashboard view."""
    # Get courses where user is coordinator
    coordinated_courses = Course.objects.filter(coordinator=request.user)
    
    # Get course statistics
    course_stats = coordinated_courses.annotate(
        enrollment_count=Count('enrollments', filter=Q(enrollments__status='active')),
        completion_count=Count('enrollments', filter=Q(enrollments__status='completed')),
        avg_progress=Avg('enrollments__progress')
    ).order_by('-enrollment_count')
    
    # Get recent enrollments across all coordinated courses
    recent_enrollments = CourseEnrollment.objects.filter(
        course__in=coordinated_courses
    ).select_related('student', 'course').order_by('-enrolled_at')[:5]
    
    # Get instructor statistics
    instructor_stats = User.objects.filter(
        groups__name='Instructor',
        teaching_courses__in=coordinated_courses
    ).distinct().annotate(
        course_count=Count('teaching_courses', distinct=True),
        student_count=Count('teaching_courses__enrollments', filter=Q(teaching_courses__enrollments__status='active'))
    ).order_by('-course_count')[:5]

    # Calculate total active students
    total_active_students = CourseEnrollment.objects.filter(
        course__in=coordinated_courses,
        status='active'
    ).values('student').distinct().count()

    context = {
        'coordinated_courses': coordinated_courses,
        'course_stats': course_stats,
        'recent_enrollments': recent_enrollments,
        'instructor_stats': instructor_stats,
        'total_active_students': total_active_students,
    }
    return render(request, 'courses/coordinator/dashboard.html', context)

@login_required
@group_required(['Course Coordinator', 'Administrator'])
def manage_courses(request):
    """Course coordinator management view."""
    courses = Course.objects.filter(coordinator=request.user)
    
    context = {
        'courses': courses,
    }
    return render(request, 'courses/manage_courses.html', context)

@login_required
@course_permission_required('manage')
def manage_course_content(request, slug):
    """Course content management view for instructors."""
    course = get_object_or_404(Course, slug=slug)
    modules = course.modules.all().prefetch_related('contents')
    
    context = {
        'course': course,
        'modules': modules,
    }
    return render(request, 'courses/manage_content.html', context)

@login_required
@course_permission_required('manage')
def manage_course_instructors(request, slug):
    """Course instructor management view for coordinators."""
    course = get_object_or_404(Course, slug=slug)
    
    context = {
        'course': course,
    }
    return render(request, 'courses/manage_instructors.html', context)

@login_required
@group_required(['Instructor', 'Course Coordinator', 'Administrator'])
def course_analytics(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enrollments = CourseEnrollment.objects.filter(course=course)
    
    context = {
        'course': course,
        'enrollments': enrollments,
    }
    return render(request, 'courses/analytics.html', context)

@login_required
@group_required(['Administrator'])
def admin_dashboard(request):
    """Admin dashboard view showing system-wide statistics and management options."""
    # Get system-wide statistics
    total_courses = Course.objects.count()
    total_students = CourseEnrollment.objects.values('student').distinct().count()
    total_instructors = Course.objects.values('instructors').distinct().count()

    # Filtering logic for recent enrollments
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'enrollments':
        recent_enrollments = CourseEnrollment.objects.filter(status='active').select_related('student', 'course').order_by('-enrolled_at')[:5]
    elif filter_type == 'completions':
        recent_enrollments = CourseEnrollment.objects.filter(status='completed').select_related('student', 'course').order_by('-enrolled_at')[:5]
    else:
        recent_enrollments = CourseEnrollment.objects.select_related('student', 'course').order_by('-enrolled_at')[:5]

    # Get course statistics
    course_stats = Course.objects.annotate(
        active_enrollments=Count('enrollments', filter=Q(enrollments__status='active')),
        completed_enrollments=Count('enrollments', filter=Q(enrollments__status='completed')),
        avg_progress=Avg('enrollments__progress')
    ).order_by('-active_enrollments')[:5]

    context = {
        'total_courses': total_courses,
        'total_students': total_students,
        'total_instructors': total_instructors,
        'recent_enrollments': recent_enrollments,
        'course_stats': course_stats,
        'filter': filter_type,
    }
    return render(request, 'courses/admin/dashboard.html', context)

@login_required
@group_required(['Administrator', 'Course Coordinator', 'Instructor'])
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            user = request.user
            if user.groups.filter(name='Administrator').exists():
                # Admin can assign coordinator/instructor via form
                pass
            elif user.groups.filter(name='Course Coordinator').exists():
                course.coordinator = user
            elif user.groups.filter(name='Instructor').exists():
                course.save()
                course.instructors.add(user)
            course.save()
            return redirect('courses:manage_courses')
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form})

@login_required
@group_required(['Course Coordinator', 'Administrator'])
def manage_enrollments(request):
    """Course enrollment management view for coordinators."""
    # Get courses where user is coordinator
    coordinated_courses = Course.objects.filter(coordinator=request.user)
    
    # Get filter parameters
    course_id = request.GET.get('course')
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    # Base queryset
    enrollments = CourseEnrollment.objects.filter(
        course__in=coordinated_courses
    ).select_related('student', 'course')
    
    # Apply filters
    if course_id:
        enrollments = enrollments.filter(course_id=course_id)
    if status:
        enrollments = enrollments.filter(status=status)
    if search:
        enrollments = enrollments.filter(
            Q(student__first_name__icontains=search) |
            Q(student__last_name__icontains=search) |
            Q(student__email__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(enrollments, 10)
    page = request.GET.get('page')
    try:
        enrollments_page = paginator.page(page)
    except PageNotAnInteger:
        enrollments_page = paginator.page(1)
    except EmptyPage:
        enrollments_page = paginator.page(paginator.num_pages)
    
    # Get courses for filter dropdown
    courses = coordinated_courses.order_by('title')
    
    context = {
        'enrollments': enrollments_page,
        'courses': courses,
        'current_course': course_id,
        'current_status': status,
        'search_query': search,
        'page_obj': enrollments_page,
    }
    return render(request, 'courses/manage_enrollments.html', context)

@login_required
@group_required(['Course Coordinator', 'Administrator'])
def update_enrollment_status(request, enrollment_id):
    if request.method == 'POST':
        enrollment = get_object_or_404(CourseEnrollment, id=enrollment_id)
        new_status = request.POST.get('status')
        
        if new_status in ['active', 'completed', 'dropped']:
            enrollment.status = new_status
            enrollment.save()
            
            messages.success(request, f'Enrollment status updated to {new_status.title()}')
        else:
            messages.error(request, 'Invalid status selected')
            
    return redirect('courses:manage_enrollments')

@login_required
@group_required(['Course Coordinator', 'Administrator'])
def enrollment_detail(request, enrollment_id):
    enrollment = get_object_or_404(CourseEnrollment.objects.select_related('student', 'course'), id=enrollment_id)
    # Optionally, fetch module progress or quiz attempts for this enrollment
    module_progress = enrollment.module_progress.select_related('module').all()
    context = {
        'enrollment': enrollment,
        'module_progress': module_progress,
    }
    return render(request, 'courses/enrollment_detail.html', context)