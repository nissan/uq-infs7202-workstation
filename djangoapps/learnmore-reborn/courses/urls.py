from django.urls import path
from . import views

urlpatterns = [
    path('catalog/', views.CourseCatalogView.as_view(), name='course-catalog'),
    path('course/<slug:slug>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('module/<int:module_id>/', views.ModuleDetailView.as_view(), name='module-detail'),
    path('quiz/<int:pk>/', views.QuizDetailView.as_view(), name='quiz-detail'),
    path('enroll/<slug:slug>/', views.enroll_course, name='course-enroll'),
    path('unenroll/<slug:slug>/', views.unenroll_course, name='course-unenroll'),
]