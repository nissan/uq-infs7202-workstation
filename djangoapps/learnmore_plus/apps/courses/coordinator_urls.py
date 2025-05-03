from django.urls import path
from . import views

app_name = 'coordinator'

urlpatterns = [
    path('dashboard/', views.manage_courses, name='dashboard'),
    path('courses/<slug:slug>/instructors/', views.manage_course_instructors, name='manage_instructors'),
    path('courses/<slug:slug>/analytics/', views.course_analytics, name='analytics'),
] 