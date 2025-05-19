from django.shortcuts import render, redirect

def home(request):
    """
    Legacy view for the home page.
    Redirects to the core home view.
    This is no longer used directly as the URL pattern has been removed.
    """
    # Instead of rendering a template directly, redirect to the core home URL
    return redirect('core:home') 