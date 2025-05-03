from django.urls import path
from . import views

app_name = 'ai_tutor'

urlpatterns = [
    # Session management
    path('sessions/', views.session_list, name='session_list'),
    path('sessions/create/', views.create_session, name='create_session'),
    path('sessions/<int:session_id>/', views.session_detail, name='session_detail'),
    path('sessions/<int:session_id>/delete/', views.delete_session, name='delete_session'),
    
    # Chat interface
    path('chat/<int:session_id>/', views.chat_view, name='chat'),
    path('chat/<int:session_id>/send/', views.send_message, name='send_message'),
    
    # Context management
    path('sessions/<int:session_id>/context/', views.manage_context, name='manage_context'),
    
    # Course-specific tutor interfaces
    path('course/<slug:course_slug>/', views.course_tutor, name='course_tutor'),
    path('module/<slug:course_slug>/<int:module_order>/', views.module_tutor, name='module_tutor'),
    path('content/<slug:course_slug>/<int:module_order>/<int:content_order>/', views.content_tutor, name='content_tutor'),
    
    # API endpoints
    path('api/sessions/', views.api_sessions, name='api_sessions'),
    path('api/chat/<int:session_id>/', views.api_chat, name='api_chat'),
]