from django.shortcuts import render

def landing_page(request):
    """
    View for the landing page that showcases platform features.
    """
    return render(request, 'landing.html') 