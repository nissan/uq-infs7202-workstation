from django.urls import path
from . import views

urlpatterns = [
    # Course and module routes
    path('catalog/', views.CourseCatalogView.as_view(), name='course-catalog'),
    path('course/<slug:slug>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('module/<int:module_id>/', views.ModuleDetailView.as_view(), name='module-detail'),
    path('enroll/<slug:slug>/', views.enroll_course, name='course-enroll'),
    path('unenroll/<slug:slug>/', views.unenroll_course, name='course-unenroll'),
    
    # Quiz routes
    path('quizzes/', views.QuizListView.as_view(), name='quiz-list'),
    path('quiz/<int:pk>/', views.QuizDetailView.as_view(), name='quiz-detail'),
    path('quiz/<int:quiz_id>/attempts/', views.QuizAttemptHistoryView.as_view(), name='quiz-attempt-history'),
    
    # Quiz attempt routes
    path('quiz/<int:quiz_id>/start/', views.start_quiz, name='start-quiz'),
    path('quiz-attempt/<int:attempt_id>/', views.TakeQuizView.as_view(), name='take-quiz'),
    path('quiz-attempt/<int:attempt_id>/<int:question_id>/', views.TakeQuizView.as_view(), name='take-quiz'),
    path('quiz-attempt/<int:attempt_id>/submit/<int:question_id>/', views.submit_answer, name='submit-answer'),
    path('quiz-attempt/<int:attempt_id>/finish/', views.finish_quiz, name='finish-quiz'),
    path('quiz-attempt/<int:attempt_id>/abandon/', views.abandon_quiz, name='abandon-quiz'),
    path('quiz-attempt/<int:attempt_id>/result/', views.QuizResultView.as_view(), name='quiz-result'),
    
    # Essay grading routes
    path('quiz/<int:quiz_id>/essay-grading/', views.pending_essay_grading, name='pending-essay-grading'),
    path('response/<int:response_id>/grade/', views.grade_essay_response, name='grade-essay-response'),
    path('response/<int:response_id>/annotate/', views.annotate_essay_response, name='annotate-essay-response'),
]