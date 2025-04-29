from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Sum
from datetime import timedelta
from .models import Subscription, Revenue

User = get_user_model()

@login_required
def home(request):
    """Dashboard home view with metrics and charts."""
    # Get current date and last month's date
    now = timezone.now()
    last_month = now - timedelta(days=30)
    
    # Calculate metrics
    total_users = User.objects.count()
    new_registrations = User.objects.filter(date_joined__month=now.month).count()
    active_subscriptions = Subscription.objects.filter(status='active').count()
    total_revenue = Revenue.objects.aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate trends
    last_month_users = User.objects.filter(date_joined__month=last_month.month).count()
    last_month_revenue = Revenue.objects.filter(date__month=last_month.month).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate percentage changes
    user_growth = ((new_registrations - last_month_users) / last_month_users * 100) if last_month_users > 0 else 0
    revenue_growth = ((total_revenue - last_month_revenue) / last_month_revenue * 100) if last_month_revenue > 0 else 0
    
    # Get user growth data for chart
    user_growth_data = []
    for i in range(6):
        month = now - timedelta(days=30*i)
        count = User.objects.filter(date_joined__month=month.month, date_joined__year=month.year).count()
        user_growth_data.append(count)
    
    # Get user distribution data
    user_distribution = {
        'students': User.objects.filter(is_staff=False, is_superuser=False).count(),
        'teachers': User.objects.filter(is_staff=True, is_superuser=False).count(),
        'administrators': User.objects.filter(is_superuser=True).count()
    }
    
    context = {
        'total_users': total_users,
        'new_registrations': new_registrations,
        'active_subscriptions': active_subscriptions,
        'total_revenue': total_revenue,
        'user_growth': user_growth,
        'revenue_growth': revenue_growth,
        'user_growth_data': user_growth_data,
        'user_distribution': user_distribution,
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
