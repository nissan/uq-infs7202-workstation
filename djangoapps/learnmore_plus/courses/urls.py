from django.urls import path
from . import views, quiz_views

app_name = 'courses'

urlpatterns = [
    path('catalog/', views.course_catalog, name='course_catalog'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('course/<slug:slug>/enroll/', views.course_enroll, name='course_enroll'),
    path('course/<slug:slug>/learn/', views.course_learn, name='course_learn'),
    path('course/<slug:slug>/learn/<int:module_order>/', views.course_learn, name='learn_module'),
    path('course/<slug:slug>/learn/<int:module_order>/<int:content_order>/', views.course_learn, name='learn_content'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('coordinator/dashboard/', views.coordinator_dashboard, name='coordinator_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/enroll/<slug:slug>/', views.course_enroll, name='course_enroll'),
    path('coordinator/courses/', views.manage_courses, name='manage_courses'),
    path('course/<slug:slug>/manage/content/', views.manage_course_content, name='manage_course_content'),
    path('course/<slug:slug>/manage/instructors/', views.manage_course_instructors, name='manage_course_instructors'),
    path('course/<slug:slug>/analytics/', views.course_analytics, name='course_analytics'),
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
    path('course/create/', views.course_create, name='course_create'),
    path('enrollments/', views.manage_enrollments, name='manage_enrollments'),
    path('enrollments/<int:enrollment_id>/update/', views.update_enrollment_status, name='update_enrollment_status'),
    path('enrollments/<int:enrollment_id>/detail/', views.enrollment_detail, name='enrollment_detail'),
] 