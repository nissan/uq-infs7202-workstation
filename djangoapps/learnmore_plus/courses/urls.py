from django.urls import path
from . import views, quiz_views

app_name = 'courses'

urlpatterns = [
    path('catalog/', views.course_catalog, name='catalog'),
    path('course/<slug:slug>/', views.course_detail, name='detail'),
    path('course/<slug:slug>/enroll/', views.course_enroll, name='enroll'),
    path('course/<slug:slug>/learn/', views.course_learn, name='learn'),
    path('course/<slug:slug>/learn/<int:module_order>/', views.course_learn, name='learn_module'),
    path('course/<slug:slug>/learn/<int:module_order>/<int:content_order>/', views.course_learn, name='learn_content'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/progress/', views.learning_progress, name='learning_progress'),
    path('course/<slug:course_slug>/content/<int:content_id>/quiz/create/',
         quiz_views.quiz_create, name='quiz_create'),
    path('course/<slug:course_slug>/quiz/<int:quiz_id>/edit/',
         quiz_views.quiz_edit, name='quiz_edit'),
    path('course/<slug:course_slug>/quiz/<int:quiz_id>/question/create/',
         quiz_views.question_create, name='question_create'),
    path('course/<slug:course_slug>/quiz/<int:quiz_id>/take/',
         quiz_views.quiz_take, name='quiz_take'),
    path('course/<slug:course_slug>/quiz/attempt/<int:attempt_id>/submit/',
         quiz_views.quiz_submit, name='quiz_submit'),
    path('course/<slug:course_slug>/quiz/attempt/<int:attempt_id>/result/',
         quiz_views.quiz_result, name='quiz_result'),
] 