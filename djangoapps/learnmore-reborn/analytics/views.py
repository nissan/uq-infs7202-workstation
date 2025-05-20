from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    UserActivity,
    CourseAnalyticsSummary,
    ModuleEngagement,
    LearningPathAnalytics,
    LearnerAnalytics
)
from courses.models import Course

class InstructorAnalyticsDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """View for the instructor analytics dashboard"""
    template_name = 'analytics/instructor-dashboard.html'
    
    def test_func(self):
        """Only allow instructors and superusers to access this view"""
        return self.request.user.is_superuser or (
            hasattr(self.request.user, 'profile') and 
            self.request.user.profile.is_instructor
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get courses where the user is the instructor
        instructor_courses = Course.objects.filter(instructor=self.request.user)
        context['instructor_courses'] = instructor_courses
        
        return context

class StudentAnalyticsView(LoginRequiredMixin, TemplateView):
    """View for the student analytics dashboard"""
    template_name = 'analytics/student-analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get or create analytics for this student
        analytics, created = LearnerAnalytics.objects.get_or_create(user=self.request.user)
        
        # If analytics were just created or haven't been updated today, recalculate
        if created or (timezone.now() - analytics.last_updated).days > 0:
            analytics.recalculate_all()
        
        context['analytics'] = analytics
        
        return context

class StudentComparisonView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """View for comparing specific student analytics"""
    template_name = 'analytics/student-comparison.html'
    
    def test_func(self):
        """Only allow instructors, superusers, or the student themselves to access this view"""
        student_id = self.kwargs.get('student_id')
        return self.request.user.is_superuser or (
            hasattr(self.request.user, 'profile') and 
            self.request.user.profile.is_instructor
        ) or str(self.request.user.id) == student_id
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get student ID from URL parameters
        student_id = self.kwargs.get('student_id')
        
        try:
            # Get the student user
            student = User.objects.get(id=student_id)
            
            # Get or create analytics for this student
            analytics, created = LearnerAnalytics.objects.get_or_create(user=student)
            
            # If analytics were just created or haven't been updated today, recalculate
            if created or (timezone.now() - analytics.last_updated).days > 0:
                analytics.recalculate_all()
            
            context['analytics'] = analytics
            context['student'] = student
            
        except User.DoesNotExist:
            raise Http404("Student not found")
        
        return context

@login_required
def record_activity(request):
    """Record user activity and return success status"""
    if request.method == 'POST':
        activity_type = request.POST.get('activity_type')
        details = request.POST.get('details', '{}')
        
        if not activity_type:
            return JsonResponse({'success': False, 'error': 'Activity type is required'})
        
        # Create activity record
        activity = UserActivity.objects.create(
            user=request.user,
            activity_type=activity_type,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            session_id=request.session.session_key,
            details=details
        )
        
        return JsonResponse({'success': True, 'activity_id': activity.id})
    
    return JsonResponse({'success': False, 'error': 'Only POST requests are supported'})

@login_required
def module_engagement_update(request, module_id):
    """Update module engagement time and view count"""
    if request.method == 'POST':
        duration_seconds = request.POST.get('duration_seconds')
        
        try:
            # Get or create engagement record
            engagement, created = ModuleEngagement.objects.get_or_create(
                module_id=module_id,
                user=request.user
            )
            
            # Update the engagement
            engagement.record_view(duration_seconds=int(duration_seconds) if duration_seconds else None)
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Only POST requests are supported'})