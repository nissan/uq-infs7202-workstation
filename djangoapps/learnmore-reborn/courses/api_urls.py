from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CourseViewSet, EnrollmentViewSet
from .module_quiz_views import ModuleViewSet
from .quiz_views import (
    QuizViewSet, MultipleChoiceQuestionViewSet, TrueFalseQuestionViewSet,
    QuizAttemptViewSet
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'modules', ModuleViewSet, basename='module')
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'multiple-choice-questions', MultipleChoiceQuestionViewSet, basename='multiple-choice-question')
router.register(r'true-false-questions', TrueFalseQuestionViewSet, basename='true-false-question')
router.register(r'quiz-attempts', QuizAttemptViewSet, basename='quiz-attempt')

urlpatterns = [
    path('', include(router.urls)),
    
    # Course catalog endpoints
    path('catalog/', CourseViewSet.as_view({'get': 'catalog'}), name='course-catalog'),
    path('catalog/search/', CourseViewSet.as_view({'get': 'search'}), name='course-search'),
    path('courses/<slug:slug>/enroll/', CourseViewSet.as_view({'post': 'enroll'}), name='course-enroll'),
    path('courses/<slug:slug>/unenroll/', CourseViewSet.as_view({'post': 'unenroll'}), name='course-unenroll'),
    path('enrolled/', EnrollmentViewSet.as_view({'get': 'active'}), name='enrolled-courses'),
    
    # Quiz custom endpoints
    path('quizzes/<int:pk>/start-attempt/', QuizViewSet.as_view({'post': 'start_attempt'}), name='quiz-start-attempt'),
    path('quizzes/<int:pk>/attempts/', QuizViewSet.as_view({'get': 'attempts'}), name='quiz-attempts'),
    
    # Quiz attempt custom endpoints
    path('quiz-attempts/<int:pk>/submit-response/', QuizAttemptViewSet.as_view({'post': 'submit_response'}), name='quiz-attempt-submit-response'),
    path('quiz-attempts/<int:pk>/complete/', QuizAttemptViewSet.as_view({'post': 'complete'}), name='quiz-attempt-complete'),
    path('quiz-attempts/<int:pk>/timeout/', QuizAttemptViewSet.as_view({'post': 'timeout'}), name='quiz-attempt-timeout'),
    path('quiz-attempts/<int:pk>/abandon/', QuizAttemptViewSet.as_view({'post': 'abandon'}), name='quiz-attempt-abandon'),
    path('quiz-attempts/<int:pk>/result/', QuizAttemptViewSet.as_view({'get': 'result'}), name='quiz-attempt-result'),
]