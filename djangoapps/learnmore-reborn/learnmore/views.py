from django.shortcuts import render

def landing_page(request):
    """
    View for the landing page that showcases platform features.
    """
    return render(request, 'landing.html')

def features_page(request):
    """
    View for the features page that showcases platform features in detail.
    """
    return render(request, 'features.html')

def how_it_works_page(request):
    """
    View for the how it works page that explains the platform's functionality.
    """
    return render(request, 'how-it-works.html')

def testimonials_page(request):
    """
    View for the testimonials page that displays user testimonials.
    """
    return render(request, 'testimonials.html') 