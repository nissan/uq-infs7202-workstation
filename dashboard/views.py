from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

@login_required
def home(request):
    """Dashboard home view with metrics and charts."""
    context = {
        'total_users': User.objects.count(),
        'new_registrations': User.objects.filter(date_joined__month=timezone.now().month).count(),
        'active_subscriptions': 150,  # Placeholder - replace with actual subscription count
        'total_revenue': 12500,  # Placeholder - replace with actual revenue
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def users(request):
    """User management view."""
    users = User.objects.all()
    return render(request, 'dashboard/users.html', {'users': users})

@login_required
def courses(request):
    """Course management view."""
    return render(request, 'dashboard/courses.html')

@login_required
def settings(request):
    """Settings view."""
    return render(request, 'dashboard/settings.html')

@login_required
def profile(request):
    """User profile view."""
    return render(request, 'dashboard/profile.html') 