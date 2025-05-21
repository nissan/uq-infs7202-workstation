from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'user-activities', views.UserActivityViewSet, basename='user-activity')
router.register(r'course-analytics', views.CourseAnalyticsViewSet, basename='course-analytics')
router.register(r'user-analytics', views.UserAnalyticsViewSet, basename='user-analytics')
router.register(r'quiz-analytics', views.QuizAnalyticsViewSet, basename='quiz-analytics')
router.register(r'system-analytics', views.SystemAnalyticsViewSet, basename='system-analytics')
router.register(r'export', views.AnalyticsExportViewSet, basename='analytics-export')
router.register(r'recalculate', views.AnalyticsRecalculationViewSet, basename='analytics-recalculate')

app_name = 'analytics'

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
    
    # Web interface URLs
    path('', views.StudentAnalyticsView.as_view(), name='dashboard'),
    path('instructor/', views.InstructorAnalyticsDashboardView.as_view(), name='instructor_dashboard'),
    path('system/', views.SystemAnalyticsDashboardView.as_view(), name='system_dashboard'),
    path('my-analytics/', views.StudentAnalyticsView.as_view(), name='student_analytics'),
    path('student/<int:student_id>/', views.StudentComparisonView.as_view(), name='student_comparison'),
    
    # AJAX endpoints
    path('record-activity/', views.record_activity, name='record_activity'),
    path('module-engagement/<int:module_id>/update/', views.module_engagement_update, name='module_engagement_update'),
]