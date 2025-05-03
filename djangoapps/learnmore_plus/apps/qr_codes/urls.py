from django.urls import path
from . import views

app_name = 'qr_codes'

urlpatterns = [
    path('scan/', views.scan_qr_code, name='scan'),
    path('scan/<int:qr_code_id>/', views.scan_qr_code_redirect, name='scan_code'),
    path('detail/<int:pk>/', views.QRCodeDetailView.as_view(), name='detail'),
    path('statistics/', views.qr_code_statistics, name='statistics'),
    path('print/course/<int:course_id>/', views.print_course_qr_codes, name='print_course'),
] 