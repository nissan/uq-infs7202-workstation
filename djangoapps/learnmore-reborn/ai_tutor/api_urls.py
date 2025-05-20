from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    TutorSessionViewSet,
    TutorMessageViewSet,
    TutorKnowledgeBaseViewSet,
    TutorFeedbackViewSet,
)

router = DefaultRouter()
router.register(r'sessions', TutorSessionViewSet, basename='tutor-session')
router.register(r'messages', TutorMessageViewSet, basename='tutor-message')
router.register(r'knowledge-base', TutorKnowledgeBaseViewSet, basename='tutor-knowledge-base')
router.register(r'feedback', TutorFeedbackViewSet, basename='tutor-feedback')

urlpatterns = [
    path('', include(router.urls)),
]