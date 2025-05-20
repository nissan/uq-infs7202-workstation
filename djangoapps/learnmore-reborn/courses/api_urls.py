from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CourseViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
    path('catalog/', CourseViewSet.as_view({'get': 'catalog'}), name='course-catalog'),
    path('catalog/search/', CourseViewSet.as_view({'get': 'search'}), name='course-search'),
    path('courses/<slug:slug>/enroll/', CourseViewSet.as_view({'post': 'enroll'}), name='course-enroll'),
    path('courses/<slug:slug>/unenroll/', CourseViewSet.as_view({'post': 'unenroll'}), name='course-unenroll'),
    path('enrolled/', EnrollmentViewSet.as_view({'get': 'active'}), name='enrolled-courses'),
]