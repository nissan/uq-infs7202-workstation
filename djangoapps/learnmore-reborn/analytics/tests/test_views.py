from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from .factories import (
    UserFactory, CourseFactory, QuizFactory,
    UserActivityFactory, CourseAnalyticsFactory,
    UserAnalyticsFactory, QuizAnalyticsFactory,
    SystemAnalyticsFactory
)
from ..models import (
    UserActivity, CourseAnalytics, UserAnalytics,
    QuizAnalytics, SystemAnalytics
)

class AnalyticsViewsTest(APITestCase):
    def setUp(self):
        # Create test users with different permissions
        self.admin_user = UserFactory(is_staff=True)
        self.admin_user.user_permissions.add(
            Permission.objects.get(codename='analytics_admin')
        )
        
        self.instructor_user = UserFactory()
        self.instructor_user.user_permissions.add(
            Permission.objects.get(codename='change_course')
        )
        
        self.student_user = UserFactory()
        
        # Create test data
        self.course = CourseFactory(instructor=self.instructor_user)
        self.quiz = QuizFactory(course=self.course)
        
        self.course_analytics = CourseAnalyticsFactory(course=self.course)
        self.user_analytics = UserAnalyticsFactory(user=self.student_user)
        self.quiz_analytics = QuizAnalyticsFactory(quiz=self.quiz)
        self.system_analytics = SystemAnalyticsFactory()
        
        # Create test activities
        self.user_activity = UserActivityFactory(user=self.student_user)
    
    def test_user_activity_list(self):
        """Test that only analytics admins can access user activity list"""
        # Test unauthenticated access
        response = self.client.get(reverse('analytics:user-activity-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test student access
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(reverse('analytics:user-activity-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test admin access
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('analytics:user-activity-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_course_analytics_list(self):
        """Test course analytics access permissions"""
        # Test unauthenticated access
        response = self.client.get(reverse('analytics:course-analytics-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test student access
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(reverse('analytics:course-analytics-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test instructor access
        self.client.force_authenticate(user=self.instructor_user)
        response = self.client.get(reverse('analytics:course-analytics-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_user_analytics_list(self):
        """Test user analytics access permissions"""
        # Test unauthenticated access
        response = self.client.get(reverse('analytics:user-analytics-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test student access to own analytics
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(reverse('analytics:user-analytics-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test student access to other user's analytics
        other_user = UserFactory()
        other_analytics = UserAnalyticsFactory(user=other_user)
        response = self.client.get(
            reverse('analytics:user-analytics-detail', args=[other_analytics.id])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_quiz_analytics_list(self):
        """Test quiz analytics access permissions"""
        # Test unauthenticated access
        response = self.client.get(reverse('analytics:quiz-analytics-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test student access
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(reverse('analytics:quiz-analytics-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test instructor access
        self.client.force_authenticate(user=self.instructor_user)
        response = self.client.get(reverse('analytics:quiz-analytics-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_system_analytics_list(self):
        """Test system analytics access permissions"""
        # Test unauthenticated access
        response = self.client.get(reverse('analytics:system-analytics-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test student access
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(reverse('analytics:system-analytics-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test admin access
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('analytics:system-analytics-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_analytics_export(self):
        """Test analytics export functionality"""
        # Test unauthenticated access
        response = self.client.post(reverse('analytics:analytics-export-list'), {
            'analytics_type': 'course',
            'format': 'json'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test student access
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(reverse('analytics:analytics-export-list'), {
            'analytics_type': 'course',
            'format': 'json'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test admin access
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(reverse('analytics:analytics-export-list'), {
            'analytics_type': 'course',
            'format': 'json'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
    
    def test_analytics_recalculation(self):
        """Test analytics recalculation functionality"""
        # Test unauthenticated access
        response = self.client.post(reverse('analytics:analytics-recalculate-list'), {
            'analytics_type': 'course',
            'force_recalculation': True
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test student access
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(reverse('analytics:analytics-recalculate-list'), {
            'analytics_type': 'course',
            'force_recalculation': True
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test admin access
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(reverse('analytics:analytics-recalculate-list'), {
            'analytics_type': 'course',
            'force_recalculation': True
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recalculated_count', response.data)

class AnalyticsDashboardViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test users
        self.admin_user = UserFactory(is_staff=True)
        self.admin_user.user_permissions.add(
            Permission.objects.get(codename='analytics_admin')
        )
        
        self.instructor_user = UserFactory()
        self.instructor_user.user_permissions.add(
            Permission.objects.get(codename='change_course')
        )
        
        self.student_user = UserFactory()
        
        # Create test data
        self.course = CourseFactory(instructor=self.instructor_user)
        self.course_analytics = CourseAnalyticsFactory(course=self.course)
    
    def test_instructor_dashboard(self):
        """Test instructor dashboard access"""
        # Test unauthenticated access
        response = self.client.get(reverse('analytics:instructor_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test student access
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('analytics:instructor_dashboard'))
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test instructor access
        self.client.force_login(self.instructor_user)
        response = self.client.get(reverse('analytics:instructor_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/instructor-dashboard.html')
    
    def test_system_dashboard(self):
        """Test system dashboard access"""
        # Test unauthenticated access
        response = self.client.get(reverse('analytics:system_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test student access
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('analytics:system_dashboard'))
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test admin access
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('analytics:system_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/system-dashboard.html')
    
    def test_student_analytics(self):
        """Test student analytics access"""
        # Test unauthenticated access
        response = self.client.get(reverse('analytics:student_analytics'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test student access
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('analytics:student_analytics'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/student-analytics.html')
    
    def test_student_comparison(self):
        """Test student comparison access"""
        # Test unauthenticated access
        response = self.client.get(
            reverse('analytics:student_comparison', args=[self.student_user.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test student access to own comparison
        self.client.force_login(self.student_user)
        response = self.client.get(
            reverse('analytics:student_comparison', args=[self.student_user.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/student-comparison.html')
        
        # Test student access to other student's comparison
        other_student = UserFactory()
        response = self.client.get(
            reverse('analytics:student_comparison', args=[other_student.id])
        )
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test instructor access
        self.client.force_login(self.instructor_user)
        response = self.client.get(
            reverse('analytics:student_comparison', args=[self.student_user.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/student-comparison.html')

class CourseAnalyticsDashboardAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.instructor = UserFactory()
        self.instructor.user_permissions.add(Permission.objects.get(codename='change_course'))
        self.student = UserFactory()
        self.course = CourseFactory(instructor=self.instructor)
        self.summary = CourseAnalyticsSummary.objects.create(
            course=self.course,
            total_enrollments=10,
            active_learners=7,
            completion_rate=80.0
        )

    def test_dashboard_access_by_instructor(self):
        self.client.force_authenticate(user=self.instructor)
        url = '/api/analytics/course-analytics/dashboard/?course_id={}'.format(self.course.id)
        response = self.client.get(url)
        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert response.data[0]['id'] == self.course.id
        assert 'analytics' in response.data[0]
        analytics = response.data[0]['analytics']
        assert analytics['total_enrollments'] == 10
        assert analytics['active_learners'] == 7
        assert analytics['completion_rate'] == 80.0

    def test_dashboard_access_denied_for_student(self):
        self.client.force_authenticate(user=self.student)
        url = '/api/analytics/course-analytics/dashboard/?course_id={}'.format(self.course.id)
        response = self.client.get(url)
        assert response.status_code in (403, 200)  # Accept 403 or empty 200
        if response.status_code == 200:
            assert response.data == [] 