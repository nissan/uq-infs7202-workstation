from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),  # Added the home URL pattern
    path('about/', views.about, name='about'),
    path('debug/', views.debug_components, name='debug_components'),
    path('test/', views.test_page, name='test_page'),
    path('button-test/', views.button_test, name='button_test'),
    path('card-test/', views.card_test, name='card_test'),
    path('section-test/', views.section_test, name='section_test'),
    path('simple-test/', views.simple_tag_test, name='simple_tag_test'),
    path('template-debug/', views.template_debug, name='template_debug'),
] 