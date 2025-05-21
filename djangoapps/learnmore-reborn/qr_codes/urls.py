from django.urls import path
from . import views

app_name = 'qr_codes'

urlpatterns = [
    path('', views.qr_code_home, name='home'),
    path('generator/', views.qr_generator, name='generator'),
    path('scanner/', views.qr_scanner, name='scanner'),
    path('management/', views.qr_management, name='management'),
    path('analytics/', views.qr_analytics, name='analytics'),
]