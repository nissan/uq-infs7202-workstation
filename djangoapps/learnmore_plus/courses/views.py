from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Course, CourseCategory

def catalog(request):
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
    course = get_object_or_404(Course, slug=slug, status='published')
    modules = course.modules.all().prefetch_related('contents')
    
    # Check if user is enrolled
    is_enrolled = False
    enrollment = None
    if request.user.is_authenticated:
        enrollment = course.courseenrollment_set.filter(student=request.user).first()
        is_enrolled = enrollment is not None
    
    context = {
        'course': course,
        'modules': modules,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
    }
    
    return render(request, 'courses/detail.html', context)
