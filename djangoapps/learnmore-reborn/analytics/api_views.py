from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, F, Sum, Avg, Min, Max, StdDev
from datetime import timedelta

from .models import (
    UserActivity,
    CourseAnalyticsSummary,
    ModuleEngagement,
    LearningPathAnalytics,
    LearnerAnalytics
)
from .serializers import (
    UserActivitySerializer,
    CourseAnalyticsSummarySerializer,
    ModuleEngagementSerializer,
    LearningPathAnalyticsSerializer,
    CourseDashboardSerializer,
    LearnerAnalyticsSerializer,
    LearnerComparisonSerializer
)
from courses.models import Course, Module, Quiz, QuizAttempt, QuestionResponse
from progress.models import Progress, ModuleProgress

class UserActivityViewSet(viewsets.ModelViewSet):
    """API endpoint for tracking and retrieving user activity"""
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['timestamp', 'activity_type']
    search_fields = ['activity_type', 'user__username']
    
    def get_queryset(self):
        """
        Filter activities based on permissions:
        - Regular users can only see their own activities
        - Instructors can see activities for their courses
        - Superusers can see all activities
        """
        user = self.request.user
        queryset = UserActivity.objects.all()
        
        # Filter by user if specified
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        # Filter by activity type if specified
        activity_type = self.request.query_params.get('activity_type')
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
            
        # Filter by date range if specified
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
            
        # Apply permissions-based filtering
        if user.is_superuser:
            return queryset
        elif hasattr(user, 'profile') and user.profile.is_instructor:
            # Instructors can see activities for their courses
            instructor_courses = Course.objects.filter(instructor=user)
            return queryset.filter(
                details__course_id__in=[c.id for c in instructor_courses]
            )
        else:
            # Regular users can only see their own activities
            return queryset.filter(user=user)
    
    @action(detail=False, methods=['post'])
    def record_activity(self, request):
        """Record a new user activity"""
        # Add the authenticated user to the data
        data = request.data.copy()
        data['user'] = request.user.id
        
        # Add IP and user agent if not provided
        if 'ip_address' not in data and 'REMOTE_ADDR' in request.META:
            data['ip_address'] = request.META.get('REMOTE_ADDR')
        if 'user_agent' not in data and 'HTTP_USER_AGENT' in request.META:
            data['user_agent'] = request.META.get('HTTP_USER_AGENT')
            
        # Create a new activity
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for course analytics"""
    queryset = CourseAnalyticsSummary.objects.all()
    serializer_class = CourseAnalyticsSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter analytics based on permissions:
        - Only instructors and superusers can access course analytics
        - Instructors can only see analytics for their courses
        """
        user = self.request.user
        queryset = CourseAnalyticsSummary.objects.all()
        
        # Filter by course if specified
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
            
        # Apply permissions-based filtering
        if user.is_superuser:
            return queryset
        elif hasattr(user, 'profile') and user.profile.is_instructor:
            # Instructors can see analytics for their courses
            instructor_courses = Course.objects.filter(instructor=user)
            return queryset.filter(course__in=instructor_courses)
        else:
            # Regular users can't see any analytics
            return CourseAnalyticsSummary.objects.none()
    
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate analytics for a course"""
        analytics = self.get_object()
        analytics.recalculate()
        return Response({'status': 'analytics recalculated'})
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get comprehensive dashboard data for courses"""
        # Get courses based on user permissions
        user = request.user
        
        if user.is_superuser:
            courses = Course.objects.all()
        elif hasattr(user, 'profile') and user.profile.is_instructor:
            courses = Course.objects.filter(instructor=user)
        else:
            return Response(
                {'detail': 'You do not have permission to access this data.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Filter by course if specified
        course_id = request.query_params.get('course_id')
        if course_id:
            courses = courses.filter(id=course_id)
            
        # Serialize the data
        serializer = CourseDashboardSerializer(courses, many=True)
        return Response(serializer.data)


class ModuleEngagementViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for module engagement data"""
    queryset = ModuleEngagement.objects.all()
    serializer_class = ModuleEngagementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter engagement data based on permissions:
        - Regular users can only see their own engagement data
        - Instructors can see engagement data for their courses
        - Superusers can see all engagement data
        """
        user = self.request.user
        queryset = ModuleEngagement.objects.all()
        
        # Filter by module if specified
        module_id = self.request.query_params.get('module_id')
        if module_id:
            queryset = queryset.filter(module_id=module_id)
            
        # Filter by user if specified
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        # Apply permissions-based filtering
        if user.is_superuser:
            return queryset
        elif hasattr(user, 'profile') and user.profile.is_instructor:
            # Instructors can see engagement data for their courses
            instructor_courses = Course.objects.filter(instructor=user)
            return queryset.filter(module__course__in=instructor_courses)
        else:
            # Regular users can only see their own engagement data
            return queryset.filter(user=user)
    
    @action(detail=False, methods=['post'])
    def record_view(self, request):
        """Record a new module view with optional duration"""
        # Add the authenticated user to the data
        data = request.data.copy()
        data['user'] = request.user.id
        
        # Validate required fields
        module_id = data.get('module')
        if not module_id:
            return Response(
                {'detail': 'Module ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get or create engagement record
        try:
            engagement, created = ModuleEngagement.objects.get_or_create(
                module_id=module_id,
                user=request.user,
                defaults={'view_count': 0}
            )
            
            # Record the view
            duration = data.get('duration_seconds')
            engagement.record_view(duration_seconds=duration)
            
            serializer = self.get_serializer(engagement)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class LearningPathAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for learning path analytics"""
    queryset = LearningPathAnalytics.objects.all()
    serializer_class = LearningPathAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Only instructors and superusers can access learning path analytics"""
        user = self.request.user
        
        if not (user.is_superuser or (hasattr(user, 'profile') and user.profile.is_instructor)):
            return LearningPathAnalytics.objects.none()
            
        return LearningPathAnalytics.objects.all()
    
    @action(detail=False, methods=['post'])
    def identify_paths(self, request):
        """Identify common learning paths for a course"""
        # Validate required fields
        course_id = request.data.get('course_id')
        if not course_id:
            return Response(
                {'detail': 'Course ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            course = Course.objects.get(id=course_id)
            
            # Check permissions
            user = request.user
            if not (user.is_superuser or 
                   (hasattr(user, 'profile') and user.profile.is_instructor and 
                    course.instructor == user)):
                return Response(
                    {'detail': 'You do not have permission to analyze this course.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
                
            # Get minimum users parameter
            min_users = int(request.data.get('min_users', 5))
            
            # Identify common paths
            path_signatures = LearningPathAnalytics.identify_common_paths(
                course, min_users=min_users
            )
            
            # Return the identified paths
            paths = LearningPathAnalytics.objects.filter(
                path_signature__in=path_signatures
            )
            
            serializer = self.get_serializer(paths, many=True)
            return Response(serializer.data)
        except Course.DoesNotExist:
            return Response(
                {'detail': 'Course not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class LearnerAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for learner analytics"""
    queryset = LearnerAnalytics.objects.all()
    serializer_class = LearnerAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter analytics based on permissions:
        - Regular users can only see their own analytics
        - Instructors can see analytics for their students
        - Superusers can see all analytics
        """
        user = self.request.user
        queryset = LearnerAnalytics.objects.all()
        
        # Filter by user if specified
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        # Apply permissions-based filtering
        if user.is_superuser:
            return queryset
        elif hasattr(user, 'profile') and user.profile.is_instructor:
            # Instructors can see analytics for their students
            instructor_courses = Course.objects.filter(instructor=user)
            enrolled_users = []
            for course in instructor_courses:
                enrolled_users.extend(course.enrollments.values_list('user_id', flat=True))
            return queryset.filter(user_id__in=enrolled_users)
        else:
            # Regular users can only see their own analytics
            return queryset.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get analytics for the current user"""
        try:
            # Get or create analytics for the current user
            analytics, created = LearnerAnalytics.objects.get_or_create(user=request.user)
            
            # If new or needs updating, calculate metrics
            if created or (timezone.now() - analytics.last_updated).days > 0:
                analytics.recalculate_all()
                
            serializer = self.get_serializer(analytics)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate analytics for a specific user"""
        analytics = self.get_object()
        analytics.recalculate_all()
        return Response({'status': 'analytics recalculated'})
    
    @action(detail=True, methods=['get'])
    def comparison(self, request, pk=None):
        """Get comparative analytics for a user"""
        analytics = self.get_object()
        
        # Check permissions
        if not (request.user.is_superuser or 
               (hasattr(request.user, 'profile') and 
                request.user.profile.is_instructor) or
               request.user == analytics.user):
            return Response(
                {'detail': 'You do not have permission to access this data.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create comparison data
        serializer = LearnerComparisonSerializer(analytics)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def time_analysis(self, request):
        """Get time analysis data for quiz attempts"""
        # Get the user to analyze
        user_id = request.query_params.get('user_id')
        if user_id:
            # Check permissions
            if not (request.user.is_superuser or 
                   (hasattr(request.user, 'profile') and request.user.profile.is_instructor) or
                   str(request.user.id) == user_id):
                return Response(
                    {'detail': 'You do not have permission to access this data.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            user = user_id
        else:
            # Default to current user
            user = request.user.id
        
        # Get all completed quiz attempts for this user
        attempts = QuizAttempt.objects.filter(
            user_id=user,
            status__in=['completed', 'timed_out']
        )
        
        if not attempts.exists():
            return Response({'detail': 'No quiz attempts found'})
        
        # Get time metrics for all attempts
        time_metrics = attempts.aggregate(
            avg_time=Avg('time_spent_seconds'),
            min_time=Min('time_spent_seconds'),
            max_time=Max('time_spent_seconds'),
            std_dev=StdDev('time_spent_seconds')
        )
        
        # Get question response time metrics
        responses = QuestionResponse.objects.filter(attempt__in=attempts)
        q_time_metrics = responses.aggregate(
            avg_q_time=Avg('time_spent_seconds'),
            min_q_time=Min('time_spent_seconds'),
            max_q_time=Max('time_spent_seconds'),
            std_dev_q=StdDev('time_spent_seconds')
        )
        
        # Time data by quiz type
        quiz_type_data = []
        for quiz in Quiz.objects.filter(attempts__in=attempts).distinct():
            quiz_attempts = attempts.filter(quiz=quiz)
            if quiz_attempts.exists():
                avg_time = quiz_attempts.aggregate(avg=Avg('time_spent_seconds'))['avg']
                quiz_type_data.append({
                    'quiz_id': quiz.id,
                    'quiz_title': quiz.title,
                    'avg_time': avg_time,
                    'attempt_count': quiz_attempts.count()
                })
        
        # Time data by question type
        question_type_data = {}
        for q_type in ['multiple_choice', 'true_false', 'essay']:
            type_responses = responses.filter(question__question_type=q_type)
            if type_responses.exists():
                avg_time = type_responses.aggregate(avg=Avg('time_spent_seconds'))['avg']
                question_type_data[q_type] = {
                    'avg_time': avg_time,
                    'response_count': type_responses.count()
                }
        
        # Learning efficiency over time (plot data)
        time_series_data = {
            'dates': [],
            'times': [],
            'scores': []
        }
        
        for attempt in attempts.order_by('completed_at'):
            if attempt.completed_at and attempt.max_score > 0:
                time_series_data['dates'].append(attempt.completed_at.strftime('%Y-%m-%d'))
                time_series_data['times'].append(attempt.time_spent_seconds)
                time_series_data['scores'].append((attempt.score / attempt.max_score) * 100)
        
        # Combine all data
        result = {
            'overall_metrics': {
                'average_time': time_metrics['avg_time'],
                'minimum_time': time_metrics['min_time'],
                'maximum_time': time_metrics['max_time'],
                'std_deviation': time_metrics['std_dev']
            },
            'question_metrics': {
                'average_time': q_time_metrics['avg_q_time'],
                'minimum_time': q_time_metrics['min_q_time'],
                'maximum_time': q_time_metrics['max_q_time'],
                'std_deviation': q_time_metrics['std_dev_q']
            },
            'quiz_type_data': quiz_type_data,
            'question_type_data': question_type_data,
            'time_series_data': time_series_data
        }
        
        return Response(result)