from django.urls import path
from . import views

urlpatterns = [
    path('learning/<int:module_id>/', views.learning_interface_view, name='learning-interface'),
    path('statistics/', views.learning_statistics_view, name='learning-statistics'),
    path('learner-progress/', views.learner_progress_view, name='learner-progress'),
    path('learner-progress/<int:course_id>/', views.learner_progress_view, name='learner-progress'),
]