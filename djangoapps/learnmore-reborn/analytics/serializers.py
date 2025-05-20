from rest_framework import serializers
from .models import (
    UserActivity,
    CourseAnalyticsSummary,
    ModuleEngagement,
    LearningPathAnalytics,
    LearnerAnalytics
)
from courses.models import Course, Module

class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for user activity data"""
    username = serializers.SerializerMethodField()
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'username', 'activity_type', 'timestamp',
            'ip_address', 'user_agent', 'details'
        ]
        read_only_fields = ['id', 'timestamp']
    
    def get_username(self, obj):
        return obj.user.username

class CourseAnalyticsSummarySerializer(serializers.ModelSerializer):
    """Serializer for course analytics summary data"""
    course_title = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseAnalyticsSummary
        fields = [
            'id', 'course', 'course_title', 'total_enrollments', 'active_learners',
            'completion_rate', 'average_rating', 'engagement_score',
            'engagement_trend', 'last_updated'
        ]
        read_only_fields = ['id', 'last_updated', 'course_title']
    
    def get_course_title(self, obj):
        return obj.course.title

class ModuleEngagementSerializer(serializers.ModelSerializer):
    """Serializer for module engagement data"""
    username = serializers.SerializerMethodField()
    module_title = serializers.SerializerMethodField()
    
    class Meta:
        model = ModuleEngagement
        fields = [
            'id', 'module', 'module_title', 'user', 'username', 'view_count',
            'time_spent', 'last_viewed', 'completion_date', 'interaction_data'
        ]
        read_only_fields = ['id', 'last_viewed']
    
    def get_username(self, obj):
        return obj.user.username
    
    def get_module_title(self, obj):
        return obj.module.title

class LearningPathAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for learning path analytics data"""
    module_titles = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPathAnalytics
        fields = [
            'id', 'path_signature', 'path_description', 'path_modules', 
            'module_titles', 'user_count', 'average_completion_time',
            'success_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_module_titles(self, obj):
        """Return titles of modules in this learning path"""
        try:
            module_ids = obj.path_modules
            modules = Module.objects.filter(id__in=module_ids)
            return [m.title for m in modules]
        except Exception:
            return []

# Learner analytics serializer
class LearnerAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for learner analytics data"""
    username = serializers.SerializerMethodField()
    accuracy_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = LearnerAnalytics
        fields = [
            'id', 'user', 'username', 'total_quizzes_taken', 'total_quizzes_passed',
            'total_questions_answered', 'total_correct_answers', 'accuracy_rate',
            'average_time_per_question', 'total_study_time', 
            'strengths', 'areas_for_improvement', 'learning_pattern_data',
            'quiz_performance_history', 'progress_over_time', 'performance_by_category',
            'course_completion_data', 'percentile_ranking', 'last_updated'
        ]
        read_only_fields = ['id', 'last_updated', 'username', 'accuracy_rate']
    
    def get_username(self, obj):
        return obj.user.username
    
    def get_accuracy_rate(self, obj):
        """Calculate the overall accuracy rate"""
        if obj.total_questions_answered > 0:
            return round((obj.total_correct_answers / obj.total_questions_answered) * 100, 1)
        return 0.0

# Comparison serializer that includes other learners' data for comparison
class LearnerComparisonSerializer(serializers.ModelSerializer):
    """Serializer for comparing a learner to peers"""
    username = serializers.SerializerMethodField()
    accuracy_rate = serializers.SerializerMethodField()
    class_comparison = serializers.SerializerMethodField()
    time_analysis = serializers.SerializerMethodField()
    
    class Meta:
        model = LearnerAnalytics
        fields = [
            'id', 'user', 'username', 'total_quizzes_taken', 'total_quizzes_passed',
            'accuracy_rate', 'average_time_per_question', 'strengths',
            'areas_for_improvement', 'percentile_ranking', 'class_comparison',
            'time_analysis'
        ]
    
    def get_username(self, obj):
        return obj.user.username
    
    def get_accuracy_rate(self, obj):
        """Calculate the overall accuracy rate"""
        if obj.total_questions_answered > 0:
            return round((obj.total_correct_answers / obj.total_questions_answered) * 100, 1)
        return 0.0
    
    def get_class_comparison(self, obj):
        """Get comparison data with class averages"""
        from django.db.models import Avg, Count, Sum, F
        from django.contrib.auth import get_user_model
        
        # Initialize comparison data
        comparison_data = {}
        
        # Get all learner analytics
        all_analytics = LearnerAnalytics.objects.all()
        
        if all_analytics.count() > 1:  # Need at least 2 learners for comparison
            # Calculate averages across all learners
            averages = all_analytics.aggregate(
                avg_quizzes_taken=Avg('total_quizzes_taken'),
                avg_quizzes_passed=Avg('total_quizzes_passed'),
                avg_questions=Avg('total_questions_answered'),
                avg_correct=Avg('total_correct_answers'),
                avg_time_per_q=Avg('average_time_per_question')
            )
            
            # Calculate average accuracy
            avg_accuracy = 0
            if averages['avg_questions'] and averages['avg_questions'] > 0:
                avg_accuracy = (averages['avg_correct'] / averages['avg_questions']) * 100
            
            # Compare user to averages
            comparison_data['class_averages'] = {
                'quizzes_taken': averages['avg_quizzes_taken'],
                'quizzes_passed': averages['avg_quizzes_passed'],
                'pass_rate': (averages['avg_quizzes_passed'] / averages['avg_quizzes_taken'] * 100) 
                              if averages['avg_quizzes_taken'] else 0,
                'accuracy': avg_accuracy,
                'time_per_question': averages['avg_time_per_q']
            }
            
            # Calculate user's performance relative to average
            user_pass_rate = (obj.total_quizzes_passed / obj.total_quizzes_taken * 100) if obj.total_quizzes_taken else 0
            user_accuracy = (obj.total_correct_answers / obj.total_questions_answered * 100) if obj.total_questions_answered else 0
            
            comparison_data['relative_performance'] = {
                'quizzes_taken': obj.total_quizzes_taken - averages['avg_quizzes_taken'],
                'pass_rate': user_pass_rate - comparison_data['class_averages']['pass_rate'],
                'accuracy': user_accuracy - avg_accuracy,
                'time_per_question': obj.average_time_per_question - averages['avg_time_per_q']
            }
        
        return comparison_data
    
    def get_time_analysis(self, obj):
        """Get detailed time analysis data"""
        from django.db.models import Avg, Count, Min, Max, StdDev
        
        # Initialize time analysis data
        time_analysis = {}
        
        # Get all completed quiz attempts for this user
        from courses.models import QuizAttempt, QuestionResponse
        attempts = QuizAttempt.objects.filter(
            user=obj.user,
            status__in=['completed', 'timed_out']
        )
        
        if attempts.exists():
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
            
            # Calculate time efficiency (how time correlates with score)
            # Get time vs score data for correlation analysis
            time_score_data = []
            for attempt in attempts:
                if attempt.max_score > 0:
                    score_pct = (attempt.score / attempt.max_score) * 100
                    time_score_data.append({
                        'time': attempt.time_spent_seconds,
                        'score': score_pct
                    })
            
            # Simple efficiency metric: calculated as avg(score)/avg(time)
            avg_time = sum(d['time'] for d in time_score_data) / len(time_score_data) if time_score_data else 0
            avg_score = sum(d['score'] for d in time_score_data) / len(time_score_data) if time_score_data else 0
            efficiency = avg_score / avg_time if avg_time > 0 else 0
            
            time_analysis = {
                'quiz_time_metrics': {
                    'average': time_metrics['avg_time'],
                    'minimum': time_metrics['min_time'],
                    'maximum': time_metrics['max_time'],
                    'std_deviation': time_metrics['std_dev']
                },
                'question_time_metrics': {
                    'average': q_time_metrics['avg_q_time'],
                    'minimum': q_time_metrics['min_q_time'],
                    'maximum': q_time_metrics['max_q_time'],
                    'std_deviation': q_time_metrics['std_dev_q']
                },
                'time_efficiency': {
                    'score_per_second': efficiency,
                    'time_score_correlation': 'positive' if efficiency > 0 else 'negative'
                }
            }
        
        return time_analysis

# Dashboard-specific serializers that combine multiple analytics types
class CourseDashboardSerializer(serializers.ModelSerializer):
    """Serializer for course dashboard that includes comprehensive analytics"""
    analytics = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'analytics']
    
    def get_analytics(self, obj):
        """Get comprehensive analytics for the course"""
        try:
            analytics = obj.analytics_summary
        except CourseAnalyticsSummary.DoesNotExist:
            # Create analytics object if it doesn't exist
            analytics = CourseAnalyticsSummary.objects.create(course=obj)
            
        # Serialize the analytics
        serializer = CourseAnalyticsSummarySerializer(analytics)
        
        # Add additional analytics data
        result = serializer.data
        
        # Module engagement statistics
        module_engagement = {}
        modules = obj.modules.all()
        for module in modules:
            try:
                engagement_count = ModuleEngagement.objects.filter(module=module).count()
                completion_count = ModuleEngagement.objects.filter(
                    module=module, 
                    completion_date__isnull=False
                ).count()
                
                module_engagement[module.id] = {
                    'title': module.title,
                    'engagement_count': engagement_count,
                    'completion_count': completion_count,
                    'completion_rate': (completion_count / engagement_count * 100) if engagement_count > 0 else 0
                }
            except Exception:
                pass
                
        result['module_engagement'] = module_engagement
        
        return result