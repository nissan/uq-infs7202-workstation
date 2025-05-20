from django.urls import path, include
from . import views

urlpatterns = [
    # Main views
    path('', views.ai_tutor_dashboard, name='ai_tutor_dashboard'),
    path('sessions/create/', views.create_tutor_session, name='create_tutor_session'),
    path('sessions/<int:session_id>/', views.tutor_session_view, name='ai_tutor_session'),
    
    # AJAX endpoints
    path('sessions/<int:session_id>/send/', views.send_message, name='send_tutor_message'),
    path('messages/<int:message_id>/feedback/', views.provide_feedback, name='provide_tutor_feedback'),
    path('sessions/<int:session_id>/end/', views.end_session, name='end_tutor_session'),
    
    # API endpoints
    path('api/', include('ai_tutor.api_urls')),
]