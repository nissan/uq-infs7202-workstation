from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    UserActivityViewSet,
    CourseAnalyticsViewSet,
    ModuleEngagementViewSet,
    LearningPathAnalyticsViewSet,
    LearnerAnalyticsViewSet
)

router = DefaultRouter()
router.register(r'user-activity', UserActivityViewSet, basename='user-activity')
router.register(r'course-analytics', CourseAnalyticsViewSet, basename='course-analytics')
router.register(r'module-engagement', ModuleEngagementViewSet, basename='module-engagement')
router.register(r'learning-paths', LearningPathAnalyticsViewSet, basename='learning-paths')
router.register(r'learner-analytics', LearnerAnalyticsViewSet, basename='learner-analytics')

urlpatterns = [
    path('', include(router.urls)),
]