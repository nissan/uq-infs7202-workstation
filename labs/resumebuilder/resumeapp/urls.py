
from django.urls import path
from .views import (
    ManageSubscribersView,
    SubscriberCreateView,
    SubscriberUpdateView,
    SubscriberDeleteView,
)

from . import views

urlpatterns = [
    path('', views.index, name='index'),  # This makes 'index' available in your template
    path("myresume/", views.myresume, name="myresume"),
    path("about/", views.about, name="about"),
    path("manage/", ManageSubscribersView.as_view(), name="manage"),
    path("manage/add/", SubscriberCreateView.as_view(), name="subscriber_add"),
    path("manage/edit/<int:pk>/", SubscriberUpdateView.as_view(), name="subscriber_edit"),
    path("manage/delete/<int:pk>/", SubscriberDeleteView.as_view(), name="subscriber_delete"),
]