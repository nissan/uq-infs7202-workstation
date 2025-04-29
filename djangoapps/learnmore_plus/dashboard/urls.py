from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('users/', views.users, name='users'),
    path('courses/', views.courses, name='courses'),
    path('settings/', views.settings, name='settings'),
    path('profile/', views.profile, name='profile'),
] 