from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CourseViewSet, EnrollmentViewSet
from .module_quiz_views import ModuleViewSet
from .quiz_views import (
    QuizViewSet, MultipleChoiceQuestionViewSet, TrueFalseQuestionViewSet,
    EssayQuestionViewSet, QuizAttemptViewSet, QuizPrerequisiteViewSet,
    QuestionAnalyticsViewSet, QuizAnalyticsViewSet
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'modules', ModuleViewSet, basename='module')
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'multiple-choice-questions', MultipleChoiceQuestionViewSet, basename='multiple-choice-question')
router.register(r'true-false-questions', TrueFalseQuestionViewSet, basename='true-false-question')
router.register(r'essay-questions', EssayQuestionViewSet, basename='essay-question')
router.register(r'quiz-attempts', QuizAttemptViewSet, basename='quiz-attempt')
router.register(r'quiz-prerequisites', QuizPrerequisiteViewSet, basename='quiz-prerequisite')
router.register(r'question-analytics', QuestionAnalyticsViewSet, basename='question-analytics')
router.register(r'quiz-analytics', QuizAnalyticsViewSet, basename='quiz-analytics')

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
    path('quizzes/<int:pk>/prerequisites/', QuizViewSet.as_view({'get': 'prerequisites'}), name='quiz-prerequisites'),
    path('quizzes/<int:pk>/check-prerequisites/', QuizViewSet.as_view({'get': 'check_prerequisites'}), name='quiz-check-prerequisites'),
    path('quizzes/<int:pk>/analytics/', QuizViewSet.as_view({'get': 'analytics'}), name='quiz-analytics'),
    path('quizzes/<int:pk>/recalculate-analytics/', QuizViewSet.as_view({'post': 'recalculate_analytics'}), name='quiz-recalculate-analytics'),
    path('quizzes/pending-surveys/', QuizViewSet.as_view({'get': 'pending_surveys'}), name='quiz-pending-surveys'),
    
    # Quiz attempt custom endpoints
    path('quiz-attempts/<int:pk>/submit-response/', QuizAttemptViewSet.as_view({'post': 'submit_response'}), name='quiz-attempt-submit-response'),
    path('quiz-attempts/<int:pk>/complete/', QuizAttemptViewSet.as_view({'post': 'complete'}), name='quiz-attempt-complete'),
    path('quiz-attempts/<int:pk>/timeout/', QuizAttemptViewSet.as_view({'post': 'timeout'}), name='quiz-attempt-timeout'),
    path('quiz-attempts/<int:pk>/abandon/', QuizAttemptViewSet.as_view({'post': 'abandon'}), name='quiz-attempt-abandon'),
    path('quiz-attempts/<int:pk>/result/', QuizAttemptViewSet.as_view({'get': 'result'}), name='quiz-attempt-result'),
    path('quiz-attempts/<int:pk>/grant-extension/', QuizAttemptViewSet.as_view({'post': 'grant_extension'}), name='quiz-attempt-grant-extension'),
    path('quiz-attempts/annotate-response/', QuizAttemptViewSet.as_view({'post': 'annotate_response'}), name='quiz-attempt-annotate-response'),
    
    # Essay question endpoints
    path('essay-questions/<int:pk>/grade/', EssayQuestionViewSet.as_view({'post': 'grade'}), name='essay-question-grade'),
    path('essay-questions/pending-grading/', EssayQuestionViewSet.as_view({'get': 'pending_grading'}), name='essay-pending-grading'),
    
    # Analytics endpoints
    path('question-analytics/<int:pk>/recalculate/', QuestionAnalyticsViewSet.as_view({'post': 'recalculate'}), name='question-analytics-recalculate'),
    path('quiz-analytics/<int:pk>/recalculate/', QuizAnalyticsViewSet.as_view({'post': 'recalculate'}), name='quiz-analytics-recalculate'),
]