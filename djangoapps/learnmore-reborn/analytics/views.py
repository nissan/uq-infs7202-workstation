from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.core.cache import cache
from django.http import HttpResponse
import csv
import json
import xlsxwriter
from io import BytesIO

from .models import (
    UserActivity,
    CourseAnalyticsSummary,
    ModuleEngagement,
    LearningPathAnalytics,
    LearnerAnalytics,
    CourseAnalytics,
    UserAnalytics,
    QuizAnalytics,
    SystemAnalytics
)
from courses.models import Course
from .serializers import (
    UserActivitySerializer, ModuleEngagementSerializer,
    CourseAnalyticsSerializer, UserAnalyticsSerializer,
    QuizAnalyticsSerializer, SystemAnalyticsSerializer,
    LearningPathAnalyticsSerializer, AnalyticsExportSerializer,
    AnalyticsRecalculationSerializer
)
from .permissions import IsAnalyticsAdmin, IsCourseInstructor

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

class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user activity data"""
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsAnalyticsAdmin]
    
    def get_queryset(self):
        queryset = UserActivity.objects.all()
        
        # Filter by user if specified
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        # Filter by activity type
        activity_type = self.request.query_params.get('activity_type')
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
            
        return queryset.select_related('user')

class CourseAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for course analytics data"""
    serializer_class = CourseAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated, IsCourseInstructor]
    
    def get_queryset(self):
        queryset = CourseAnalytics.objects.all()
        
        # Filter by course if specified
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(last_updated__gte=start_date)
        if end_date:
            queryset = queryset.filter(last_updated__lte=end_date)
            
        return queryset.select_related('course')
    
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate analytics for a specific course"""
        analytics = self.get_object()
        analytics.calculate_metrics()
        serializer = self.get_serializer(analytics)
        return Response(serializer.data)

class UserAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user analytics data"""
    serializer_class = UserAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = UserAnalytics.objects.all()
        
        # Users can only see their own analytics unless they're staff
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(last_updated__gte=start_date)
        if end_date:
            queryset = queryset.filter(last_updated__lte=end_date)
            
        return queryset.select_related('user')
    
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate analytics for a specific user"""
        analytics = self.get_object()
        analytics.calculate_metrics()
        serializer = self.get_serializer(analytics)
        return Response(serializer.data)

class QuizAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for quiz analytics data"""
    serializer_class = QuizAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated, IsCourseInstructor]
    
    def get_queryset(self):
        queryset = QuizAnalytics.objects.all()
        
        # Filter by quiz if specified
        quiz_id = self.request.query_params.get('quiz_id')
        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)
            
        # Filter by course
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(quiz__course_id=course_id)
            
        return queryset.select_related('quiz', 'quiz__course')
    
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate analytics for a specific quiz"""
        analytics = self.get_object()
        analytics.calculate_metrics()
        serializer = self.get_serializer(analytics)
        return Response(serializer.data)

class SystemAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for system analytics data"""
    serializer_class = SystemAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated, IsAnalyticsAdmin]
    
    def get_queryset(self):
        queryset = SystemAnalytics.objects.all()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
            
        return queryset.order_by('-timestamp')
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current system metrics"""
        metrics = SystemAnalytics.get_current_metrics()
        serializer = self.get_serializer(metrics)
        return Response(serializer.data)

class AnalyticsExportViewSet(viewsets.ViewSet):
    """ViewSet for exporting analytics data"""
    permission_classes = [permissions.IsAuthenticated, IsAnalyticsAdmin]
    
    def create(self, request):
        """Handle analytics export request"""
        serializer = AnalyticsExportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        data = serializer.validated_data
        analytics_type = data['analytics_type']
        export_format = data['format']
        include_details = data['include_details']
        
        # Get the appropriate queryset based on analytics type
        if analytics_type == 'course':
            queryset = CourseAnalytics.objects.all()
            serializer_class = CourseAnalyticsSerializer
        elif analytics_type == 'user':
            queryset = UserAnalytics.objects.all()
            serializer_class = UserAnalyticsSerializer
        elif analytics_type == 'quiz':
            queryset = QuizAnalytics.objects.all()
            serializer_class = QuizAnalyticsSerializer
        elif analytics_type == 'system':
            queryset = SystemAnalytics.objects.all()
            serializer_class = SystemAnalyticsSerializer
        else:  # 'all'
            # Handle export of all analytics types
            return self._export_all_analytics(data)
            
        # Apply date filters if provided
        if data.get('start_date'):
            queryset = queryset.filter(last_updated__gte=data['start_date'])
        if data.get('end_date'):
            queryset = queryset.filter(last_updated__lte=data['end_date'])
            
        # Serialize the data
        serializer = serializer_class(queryset, many=True)
        export_data = serializer.data
        
        # Generate the export file
        if export_format == 'json':
            return self._export_json(export_data, analytics_type)
        elif export_format == 'csv':
            return self._export_csv(export_data, analytics_type)
        else:  # xlsx
            return self._export_xlsx(export_data, analytics_type)
    
    def _export_json(self, data, analytics_type):
        """Export data as JSON"""
        response = HttpResponse(
            json.dumps(data, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="{analytics_type}_analytics.json"'
        return response
    
    def _export_csv(self, data, analytics_type):
        """Export data as CSV"""
        if not data:
            return HttpResponse('No data to export', status=status.HTTP_404_NOT_FOUND)
            
        # Create CSV writer
        output = BytesIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        # Prepare response
        response = HttpResponse(
            output.getvalue(),
            content_type='text/csv'
        )
        response['Content-Disposition'] = f'attachment; filename="{analytics_type}_analytics.csv"'
        return response
    
    def _export_xlsx(self, data, analytics_type):
        """Export data as Excel"""
        if not data:
            return HttpResponse('No data to export', status=status.HTTP_404_NOT_FOUND)
            
        # Create Excel workbook
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        # Write headers
        headers = data[0].keys()
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
            
        # Write data
        for row, item in enumerate(data, start=1):
            for col, key in enumerate(headers):
                worksheet.write(row, col, item.get(key, ''))
                
        workbook.close()
        
        # Prepare response
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{analytics_type}_analytics.xlsx"'
        return response
    
    def _export_all_analytics(self, data):
        """Export all analytics types"""
        # This would combine data from all analytics types
        # and export them in separate sheets/tabs
        pass

class AnalyticsRecalculationViewSet(viewsets.ViewSet):
    """ViewSet for triggering analytics recalculation"""
    permission_classes = [permissions.IsAuthenticated, IsAnalyticsAdmin]
    
    def create(self, request):
        """Handle analytics recalculation request"""
        serializer = AnalyticsRecalculationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        data = serializer.validated_data
        analytics_type = data['analytics_type']
        force_recalculation = data['force_recalculation']
        specific_ids = data.get('specific_ids', [])
        
        # Get the appropriate model based on analytics type
        if analytics_type == 'course':
            model = CourseAnalytics
        elif analytics_type == 'user':
            model = UserAnalytics
        elif analytics_type == 'quiz':
            model = QuizAnalytics
        elif analytics_type == 'system':
            model = SystemAnalytics
        else:  # 'all'
            # Recalculate all analytics types
            return self._recalculate_all_analytics(data)
            
        # Get the queryset
        queryset = model.objects.all()
        if specific_ids:
            queryset = queryset.filter(id__in=specific_ids)
            
        # Recalculate metrics
        count = 0
        for analytics in queryset:
            if force_recalculation or not analytics.last_calculated or \
               (timezone.now() - analytics.last_calculated) > timedelta(hours=1):
                analytics.calculate_metrics()
                count += 1
                
        return Response({
            'message': f'Recalculated {count} {analytics_type} analytics records',
            'recalculated_count': count
        })
    
    def _recalculate_all_analytics(self, data):
        """Recalculate all analytics types"""
        # This would trigger recalculation for all analytics types
        pass

class SystemAnalyticsDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """View for the system analytics dashboard"""
    template_name = 'analytics/system-dashboard.html'
    
    def test_func(self):
        """Only allow analytics administrators to access this view"""
        return request.user.has_perm('analytics.analytics_admin')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current system metrics
        try:
            metrics = SystemAnalytics.get_current_metrics()
            context['current_metrics'] = metrics
        except Exception as e:
            context['error'] = str(e)
        
        return context