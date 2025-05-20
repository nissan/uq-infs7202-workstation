from django.urls import path
from rest_framework.permissions import AllowAny
from .views import CourseListView, CourseDetailView

urlpatterns = [
    path('', CourseListView.as_view(permission_classes=[AllowAny]), name='course-list'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
]