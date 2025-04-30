from django.urls import path
from . import views

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
] 