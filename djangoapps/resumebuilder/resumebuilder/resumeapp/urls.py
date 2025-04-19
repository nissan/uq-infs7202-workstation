# urls.py

from django.urls import path
# from . import views
from . import views_fbv as views
from .views import (
    ManageSubscribersView,
    SubscriberCreateView,
    SubscriberUpdateView,
    SubscriberDeleteView,
)

urlpatterns = [
    path('', views.index, name='index'),  # This makes 'index' available in your template
    path("myresume/", views.myresume, name="myresume"),
    path("about/", views.about, name="about"),
    # path("manage/", ManageSubscribersView.as_view(), name="manage"),
    # path("manage/add/", SubscriberCreateView.as_view(), name="subscriber_add"),
    # path("manage/edit/<int:pk>/", SubscriberUpdateView.as_view(), name="subscriber_edit"),
    # path("manage/delete/<int:pk>/", SubscriberDeleteView.as_view(), name="subscriber_delete"),
    path("manage/", views.manage_subscribers, name="manage"),
    path("manage/add/", views.add_subscriber, name="subscriber_add"),
    path("manage/edit/<int:pk>/", views.edit_subscriber, name="subscriber_edit"),
    path("manage/delete/<int:pk>/", views.delete_subscriber, name="subscriber_delete"),
]
    
# urlpatterns = [
#     path("manage/", views.manage_subscribers, name="manage"),
#     path("manage/add/", views.add_subscriber, name="subscriber_add"),
#     path("manage/edit/<int:pk>/", views.edit_subscriber, name="subscriber_edit"),
#     path("manage/delete/<int:pk>/", views.delete_subscriber, name="subscriber_delete"),
# ]