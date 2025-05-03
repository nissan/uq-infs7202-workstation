from django.urls import path
from . import views

app_name = 'instructor'

urlpatterns = [
    path('dashboard/', views.instructor_dashboard, name='dashboard'),
    path('courses/<slug:slug>/content/', views.manage_course_content, name='manage_content'),
    path('courses/<slug:slug>/analytics/', views.course_analytics, name='analytics'),
] 