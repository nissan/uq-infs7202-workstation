from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('catalog/', views.catalog, name='catalog'),
    path('course/<slug:slug>/', views.course_detail, name='detail'),
] 