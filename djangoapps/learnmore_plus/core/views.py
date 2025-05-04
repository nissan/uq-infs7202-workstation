from django.shortcuts import render

def home(request):
    """
    Renders the home page using either the traditional template or the new atomic design template.
    The atomic design template is feature-flagged with ?atomic=true in the URL.
    """
    if request.GET.get('atomic') == 'true':
        # Use the new atomic design template
        return render(request, 'components/home.html')
    else:
        # Use the traditional template
        return render(request, 'core/home.html')

def about(request):
    """
    Renders the about page using the atomic design components.
    """
    return render(request, 'components/about.html') 