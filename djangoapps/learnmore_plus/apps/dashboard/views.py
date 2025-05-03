from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from django.http import JsonResponse
from datetime import timedelta
from .models import Subscription, Revenue, UserActivity

User = get_user_model()

@login_required
def home(request):
    """Dashboard home view with enhanced metrics and charts."""
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

    # Get recent user activity
    recent_activities = UserActivity.objects.select_related('user').order_by('-timestamp')[:10]
    
    # Get activity statistics
    activity_stats = {
        'total_activities': UserActivity.objects.count(),
        'activities_today': UserActivity.objects.filter(timestamp__date=now.date()).count(),
        'active_users_today': UserActivity.objects.filter(timestamp__date=now.date()).values('user').distinct().count(),
        'most_common_action': UserActivity.objects.values('action').annotate(count=Count('id')).order_by('-count').first()
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
        'recent_activities': recent_activities,
        'activity_stats': activity_stats,
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def users(request):
    """Enhanced user management view with activity tracking."""
    users = User.objects.all()
    user_activities = UserActivity.objects.select_related('user').order_by('-timestamp')[:50]
    
    # Get user activity statistics
    user_stats = {}
    for user in users:
        user_stats[user.id] = {
            'total_activities': UserActivity.objects.filter(user=user).count(),
            'last_activity': UserActivity.objects.filter(user=user).order_by('-timestamp').first(),
            'activity_types': UserActivity.objects.filter(user=user).values('action').annotate(count=Count('id'))
        }
    
    context = {
        'users': users,
        'user_activities': user_activities,
        'user_stats': user_stats,
    }
    return render(request, 'dashboard/users.html', context)

@login_required
def activity_log(request):
    """Detailed activity log view."""
    activities = UserActivity.objects.select_related('user').order_by('-timestamp')
    
    # Filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        activities = activities.filter(timestamp__range=[start_date, end_date])
    
    # Filter by action type if provided
    action_type = request.GET.get('action_type')
    if action_type:
        activities = activities.filter(action=action_type)
    
    context = {
        'activities': activities,
        'action_types': UserActivity.ACTION_TYPES,
    }
    return render(request, 'dashboard/activity_log.html', context)

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

@login_required
def system_health(request):
    """System health monitoring view."""
    # Get system metrics
    system_metrics = {
        'total_users': User.objects.count(),
        'active_users_today': UserActivity.objects.filter(timestamp__date=timezone.now().date()).values('user').distinct().count(),
        'total_activities': UserActivity.objects.count(),
        'activities_today': UserActivity.objects.filter(timestamp__date=timezone.now().date()).count(),
        'active_subscriptions': Subscription.objects.filter(status='active').count(),
        'total_revenue': Revenue.objects.aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # Get activity trends
    activity_trends = []
    for i in range(7):
        date = timezone.now().date() - timedelta(days=i)
        count = UserActivity.objects.filter(timestamp__date=date).count()
        activity_trends.append({'date': date, 'count': count})
    
    context = {
        'system_metrics': system_metrics,
        'activity_trends': activity_trends,
    }
    return render(request, 'dashboard/system_health.html', context)
