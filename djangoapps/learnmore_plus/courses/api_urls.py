from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    CategoryViewSet, CourseViewSet, ModuleViewSet, ContentViewSet,
    QuizViewSet, QuestionViewSet, ChoiceViewSet, CourseEnrollmentViewSet,
    ModuleProgressViewSet, QuizAttemptViewSet, UserViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'modules', ModuleViewSet)
router.register(r'contents', ContentViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'choices', ChoiceViewSet)
router.register(r'enrollments', CourseEnrollmentViewSet)
router.register(r'module-progress', ModuleProgressViewSet)
router.register(r'quiz-attempts', QuizAttemptViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 