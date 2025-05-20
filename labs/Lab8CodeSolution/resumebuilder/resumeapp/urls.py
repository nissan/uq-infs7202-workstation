
from django.urls import path, include
from .views import (
    ManageSubscribersView,
    SubscriberCreateView,
    SubscriberUpdateView,
    SubscriberDeleteView,
)

from . import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'qualifications', views.QualificationViewSet)
router.register(r'work-experiences', views.WorkExperienceViewSet)

urlpatterns = [
    path('', views.index, name='index'),  # This makes 'index' available in your template
    path("myresume/", views.myresume, name="myresume"),
    path("about/", views.about, name="about"),
    path("manage/", ManageSubscribersView.as_view(), name="manage"),
    path("manage/add/", SubscriberCreateView.as_view(), name="subscriber_add"),
    path("manage/edit/<int:pk>/", SubscriberUpdateView.as_view(), name="subscriber_edit"),
    path("manage/delete/<int:pk>/", SubscriberDeleteView.as_view(), name="subscriber_delete"),
    path("suggest_bio/<int:user_id>/", views.suggest_bio, name="suggest_bio"),
    path("select_bio/<int:user_id>/", views.select_bio, name="select_bio"),
    path("chatui/<int:user_id>/", views.chatui, name="chatui"),
    path("chatbot/", views.chatbot, name="chatbot"),
    path('api/', include(router.urls)),
]

