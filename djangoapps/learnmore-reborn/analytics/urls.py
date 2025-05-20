from django.urls import path, include
from . import views

app_name = 'analytics'

urlpatterns = [
    # Include API URLs
    path('api/', include('analytics.api_urls')),
    
    # Web interface URLs
    path('dashboard/', views.InstructorAnalyticsDashboardView.as_view(), name='instructor_dashboard'),
    path('my-analytics/', views.StudentAnalyticsView.as_view(), name='student_analytics'),
    path('student/<int:student_id>/', views.StudentComparisonView.as_view(), name='student_comparison'),
    
    # AJAX endpoints
    path('record-activity/', views.record_activity, name='record_activity'),
    path('module-engagement/<int:module_id>/update/', views.module_engagement_update, name='module_engagement_update'),
]