from django.shortcuts import render
from django.urls import reverse
from django.conf import settings
from django.templatetags.static import static
from django.template.loader import get_template
from django.template import TemplateDoesNotExist

def home(request):
    """
    Main landing page for LearnMore Plus.
    """
    features = [
        {
            'title': 'Adaptive Learning',
            'description': 'Our AI-powered system adapts to your learning pace and style for personalized education.',
            'icon': 'brain'
        },
        {
            'title': 'Interactive Content',
            'description': 'Engage with interactive lessons, quizzes, and multimedia materials that make learning fun.',
            'icon': 'layers'
        },
        {
            'title': 'Progress Tracking',
            'description': 'Track your progress with detailed analytics and gain insights into your learning journey.',
            'icon': 'bar-chart'
        },
        {
            'title': 'QR Code Access',
            'description': 'Share and access courses instantly with QR codes for seamless distribution.',
            'icon': 'qr-code'
        },
        {
            'title': 'AI Tutor',
            'description': 'Get 24/7 help from our AI tutor that can answer questions about any course content.',
            'icon': 'bot'
        },
        {
            'title': 'Mobile Friendly',
            'description': 'Learn on any device, anywhere, anytime with our responsive platform design.',
            'icon': 'smartphone'
        }
    ]
    
    context = {
        'catalog_url': reverse('courses:course_catalog'),
        'test_url': reverse('core:test_page'),
        'image_path': static('images/course-placeholder.svg'),
        'features': features,
        'debug_mode': settings.DEBUG
    }
    return render(request, 'landing.html', context)


def about(request):
    """
    Renders the about page using our flattened components.
    """
    context = {
        'team_members': [
            {
                'name': 'John Smith',
                'role': 'Founder & CEO',
                'bio': 'John has over 15 years of experience in education technology.',
                'avatar': 'JS'
            },
            {
                'name': 'Sarah Johnson',
                'role': 'CTO',
                'bio': 'Sarah leads our technical team and has a background in AI and machine learning.',
                'avatar': 'SJ'
            },
            {
                'name': 'Michael Rodriguez',
                'role': 'Head of Education',
                'bio': 'Michael is a former professor with expertise in curriculum development.',
                'avatar': 'MR'
            }
        ]
    }
    return render(request, 'pages/about.html', context)


def debug_components(request):
    """
    Debug view to test if components are rendering properly.
    Shows all available components with different variants.
    """
    context = {
        'catalog_url': reverse('courses:course_catalog'),
        'image_path': static('images/course-placeholder.svg'),
        'feature_items': [
            {
                'title': 'Feature 1',
                'description': 'This is a description of feature 1.',
                'icon': 'star'
            },
            {
                'title': 'Feature 2',
                'description': 'This is a description of feature 2.',
                'icon': 'heart'
            }
        ]
    }
    return render(request, 'pages/component_debug.html', context)


def test_page(request):
    """
    A simple test page to verify templates are working.
    """
    return render(request, 'pages/test.html')


def button_test(request):
    """
    A simpler test to verify button component is working.
    """
    context = {
        'home_url': reverse('core:home'),
    }
    return render(request, 'button_component_test.html', context)


def card_test(request):
    """
    A test page for card components.
    """
    context = {
        'home_url': reverse('core:home'),
        'image_path': static('images/course-placeholder.svg'),
    }
    return render(request, 'card_component_test.html', context)
    
    
def section_test(request):
    """
    A test page for section components.
    """
    features = [
        {
            'title': 'Adaptive Learning',
            'description': 'Our AI-powered system adapts to your learning pace and style.',
            'icon': 'brain'
        },
        {
            'title': 'Interactive Content',
            'description': 'Engage with interactive lessons that make learning fun and effective.',
            'icon': 'layers'
        },
        {
            'title': 'Progress Tracking',
            'description': 'Track your progress with detailed analytics and insights.',
            'icon': 'bar-chart'
        },
        {
            'title': 'Mobile Friendly',
            'description': 'Learn on any device, anywhere, anytime.',
            'icon': 'smartphone'
        },
        {
            'title': 'Expert Support',
            'description': 'Get help from our team of expert educators when you need it.',
            'icon': 'users'
        },
        {
            'title': 'Certificate Earning',
            'description': 'Earn recognized certificates to showcase your achievements.',
            'icon': 'award'
        }
    ]
    
    context = {
        'home_url': reverse('core:home'),
        'features': features
    }
    
    return render(request, 'section_component_test.html', context)


def simple_tag_test(request):
    """
    A super simple test to verify template tags are working.
    """
    return render(request, 'simple_test.html')


def template_debug(request):
    """
    Debug view that shows all loaded template tags and context.
    """
    from django.template.loader import get_template_sources
    from django.template import engines
    
    # Get django template engine
    engine = engines['django']
    
    # Get information about the template loaders
    loaders_info = []
    for loader in engine.engine.template_loaders:
        loader_name = loader.__class__.__name__
        loader_dirs = []
        
        # Try to get directories for filesystem loaders
        if hasattr(loader, 'get_dirs'):
            loader_dirs = loader.get_dirs()
        
        # Get template directories
        dirs = []
        if hasattr(loader, 'get_template_sources'):
            # Sample template to check sources
            template_name = 'components/elements/button.html'
            sources = list(loader.get_template_sources(template_name))
            dirs = [str(source) for source in sources]
        
        loaders_info.append({
            'name': loader_name,
            'dirs': loader_dirs,
            'sources': dirs
        })
    
    # Get installed template tag libraries
    from django.template.backends.django import get_installed_libraries
    libraries = get_installed_libraries()
    
    context = {
        'template_loaders': loaders_info,
        'template_libraries': libraries,
        'context_processors': engine.engine.template_context_processors,
        'TEMPLATES_setting': settings.TEMPLATES,
        'INSTALLED_APPS': settings.INSTALLED_APPS,
    }
    
    return render(request, 'template_debug.html', context)