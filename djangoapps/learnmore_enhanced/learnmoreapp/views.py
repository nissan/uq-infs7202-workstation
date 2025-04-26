from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST

def index(request):
    # Hero Section Data
    hero = {
        'title': 'Revolutionizing Online Learning with AI',
        'description': 'Experience personalized learning paths, interactive content, and real-time feedback powered by cutting-edge artificial intelligence.',
        'primary_button_text': 'Get Started',
        'secondary_button_text': 'Learn More'
    }

    # Features Section Data
    features = [
        {
            'icon': 'pencil-square',
            'title': 'Intuitive Course Creation',
            'description': 'Build engaging courses with our drag-and-drop editor. Add videos, quizzes, and interactive elements in minutes.'
        },
        {
            'icon': 'qr-code',
            'title': 'QR Code Sharing',
            'description': 'Share your courses instantly with QR codes. Students can access materials with a simple scan.'
        },
        {
            'icon': 'robot',
            'title': 'AI Tutoring',
            'description': 'Provide 24/7 personalized support with our AI tutoring system that adapts to each student\'s learning style.'
        },
        {
            'icon': 'graph-up',
            'title': 'Advanced Analytics',
            'description': 'Track student progress and engagement with detailed analytics and actionable insights.'
        }
    ]

    # Steps Section Data
    steps = [
        {
            'number': 1,
            'title': 'Create Your Account',
            'description': 'Sign up for free and set up your learning profile'
        },
        {
            'number': 2,
            'title': 'Choose Your Path',
            'description': 'Select from our curated courses or get a personalized recommendation'
        },
        {
            'number': 3,
            'title': 'Start Learning',
            'description': 'Begin your journey with interactive lessons and real-time feedback'
        }
    ]

    # Featured Courses Data
    featured_courses = [
        {
            'title': 'AI Fundamentals',
            'description': 'Master the basics of artificial intelligence and machine learning',
            'image_url': 'https://via.placeholder.com/400x200',
            'duration': '8 weeks',
            'student_count': '1.2k students'
        },
        {
            'title': 'Web Development',
            'description': 'Learn modern web development with HTML, CSS, and JavaScript',
            'image_url': 'https://via.placeholder.com/400x200',
            'duration': '12 weeks',
            'student_count': '2.5k students'
        },
        {
            'title': 'Data Science',
            'description': 'Dive into data analysis, visualization, and machine learning',
            'image_url': 'https://via.placeholder.com/400x200',
            'duration': '10 weeks',
            'student_count': '1.8k students'
        }
    ]

    # Testimonials Data
    testimonials = [
        {
            'name': 'Sarah Johnson',
            'role': 'Software Developer',
            'avatar_url': 'https://via.placeholder.com/50',
            'content': 'The AI-powered learning paths have helped me master new technologies faster than I ever thought possible. The personalized feedback is invaluable!'
        },
        {
            'name': 'Michael Chen',
            'role': 'Data Scientist',
            'avatar_url': 'https://via.placeholder.com/50',
            'content': 'As someone who learns best through practical examples, the interactive content and real-time feedback have been game-changers for my learning journey.'
        },
        {
            'name': 'Emily Rodriguez',
            'role': 'UX Designer',
            'avatar_url': 'https://via.placeholder.com/50',
            'content': 'The community features and collaborative learning opportunities have made the experience so much more engaging. I\'ve learned as much from my peers as from the courses!'
        }
    ]

    # CTA Section Data
    cta = {
        'title': 'Ready to Start Your Learning Journey?',
        'description': 'Join thousands of learners who are already transforming their careers with Enhanced LearnMore.',
        'primary_button': {
            'text': 'Get Started Now',
            'url': '/register/',
            'icon': 'bi-rocket-takeoff'
        },
        'secondary_button': {
            'text': 'View Courses',
            'url': '/courses/',
            'icon': 'bi-book'
        }
    }

    # Footer Data
    footer = {
        'company': {
            'name': 'Enhanced LearnMore',
            'description': 'Revolutionizing online learning with AI',
            'logo': None
        },
        'links': {
            'platform': [
                {'text': 'Courses', 'url': '/courses/'},
                {'text': 'Features', 'url': '/features/'},
                {'text': 'Pricing', 'url': '/pricing/'},
                {'text': 'Testimonials', 'url': '/testimonials/'}
            ],
            'company': [
                {'text': 'About Us', 'url': '/about/'},
                {'text': 'Careers', 'url': '/careers/'},
                {'text': 'Blog', 'url': '/blog/'},
                {'text': 'Press', 'url': '/press/'}
            ],
            'support': [
                {'text': 'Help Center', 'url': '/help/'},
                {'text': 'Contact Us', 'url': '/contact/'},
                {'text': 'Privacy Policy', 'url': '/privacy/'},
                {'text': 'Terms of Service', 'url': '/terms/'}
            ]
        },
        'social': [
            {'icon': 'bi-facebook', 'url': 'https://facebook.com'},
            {'icon': 'bi-twitter', 'url': 'https://twitter.com'},
            {'icon': 'bi-linkedin', 'url': 'https://linkedin.com'},
            {'icon': 'bi-instagram', 'url': 'https://instagram.com'}
        ],
        'newsletter': {
            'title': 'Subscribe to our newsletter',
            'description': 'Get the latest updates on new courses and features'
        }
    }

    return render(request, 'pages/index.html', {
        'hero': hero,
        'features': features,
        'steps': steps,
        'featured_courses': featured_courses,
        'testimonials': testimonials,
        'cta': cta,
        'footer': footer,
        'user': request.user,
        'notification_count': 0  # We'll implement this later
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'pages/register.html', {'form': form})

@require_POST
def newsletter_subscribe(request):
    email = request.POST.get('email')
    if email:
        # TODO: Implement newsletter subscription logic
        return JsonResponse({'status': 'success', 'message': 'Thank you for subscribing!'})
    return JsonResponse({'status': 'error', 'message': 'Please provide a valid email address.'}, status=400)

def course_catalog(request):
    # TODO: Implement course catalog logic
    courses = [
        {
            'title': 'AI Fundamentals',
            'description': 'Master the basics of artificial intelligence and machine learning',
            'image': 'https://via.placeholder.com/400x200',
            'duration': '8 weeks',
            'students': '1.2k',
            'rating': 4.8
        },
        {
            'title': 'Web Development',
            'description': 'Learn modern web development with HTML, CSS, and JavaScript',
            'image': 'https://via.placeholder.com/400x200',
            'duration': '12 weeks',
            'students': '2.5k',
            'rating': 4.9
        },
        {
            'title': 'Data Science',
            'description': 'Dive into data analysis, visualization, and machine learning',
            'image': 'https://via.placeholder.com/400x200',
            'duration': '10 weeks',
            'students': '1.8k',
            'rating': 4.7
        }
    ]
    return render(request, 'pages/course-catalog.html', {'courses': courses})

def navigation_test(request):
    """View for testing the navigation component."""
    return render(request, 'components/test/navigation-test.html') 