from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse

def index(request):
    steps = [
        {
            'title': 'Sign Up',
            'description': 'Create your account in minutes',
            'icon': 'bi-person-plus'
        },
        {
            'title': 'Choose Courses',
            'description': 'Select from our curated course catalog',
            'icon': 'bi-book'
        },
        {
            'title': 'Start Learning',
            'description': 'Begin your personalized learning journey',
            'icon': 'bi-rocket-takeoff'
        }
    ]

    testimonials = [
        {
            'name': 'Sarah Johnson',
            'role': 'Software Developer',
            'avatar': None,
            'quote': 'The AI-powered learning paths have helped me master new technologies faster than I ever thought possible. The personalized feedback is invaluable!',
            'rating': 5
        },
        {
            'name': 'Michael Chen',
            'role': 'Data Scientist',
            'avatar': None,
            'quote': 'As someone who learns best through practical examples, the interactive content and real-time feedback have been game-changers for my learning journey.',
            'rating': 5
        },
        {
            'name': 'Emily Rodriguez',
            'role': 'UX Designer',
            'quote': 'The community features and collaborative learning opportunities have made the experience so much more engaging. I\'ve learned as much from my peers as from the courses!',
            'rating': 5
        }
    ]

    return render(request, 'learnmoreapp/index.html', {
        'steps': steps,
        'testimonials': testimonials,
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
    return render(request, 'learnmoreapp/register.html', {'form': form}) 