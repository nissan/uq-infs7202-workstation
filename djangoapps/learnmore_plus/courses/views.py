from django.shortcuts import render
from django.db.models import Q
from .models import Course, CourseCategory

def catalog(request):
    # Get all categories for the filter sidebar
    categories = CourseCategory.objects.all()
    
    # Get the search query
    query = request.GET.get('q', '')
    
    # Get the selected categories
    selected_categories = request.GET.getlist('category')
    
    # Get the price range
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', 200)
    
    # Get the selected levels
    selected_levels = request.GET.getlist('level')
    
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
    
    # Apply price range filter
    if min_price and max_price:
        courses = courses.filter(price__gte=min_price, price__lte=max_price)
    
    # Apply level filter (if we add a level field to the Course model)
    # if selected_levels:
    #     courses = courses.filter(level__in=selected_levels)
    
    # Order by featured first, then by creation date
    courses = courses.order_by('-is_featured', '-created_at')
    
    context = {
        'courses': courses,
        'categories': categories,
        'query': query,
        'selected_categories': selected_categories,
        'min_price': min_price,
        'max_price': max_price,
        'selected_levels': selected_levels,
    }
    
    return render(request, 'courses/catalog.html', context)
