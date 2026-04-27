from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('checkin/', views.quick_checkin, name='checkin'),
    path('class/<int:class_pk>/', views.register_attendance, name='register'),
    path('class/<int:class_pk>/<str:date_str>/', views.register_attendance, name='register_date'),
    path('report/', views.attendance_report, name='report'),
    path('student/<int:student_pk>/', views.student_history, name='student_history'),
]
