from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    path('', views.class_list, name='list'),
    path('new/', views.class_create, name='create'),
    path('<int:pk>/', views.class_detail, name='detail'),
    path('<int:pk>/edit/', views.class_update, name='update'),
    path('<int:pk>/schedule/', views.schedule_add, name='schedule_add'),
    path('schedule/<int:pk>/remove/', views.schedule_remove, name='schedule_remove'),
    path('<int:class_pk>/enroll/', views.enrollment_add, name='enrollment_add'),
    path('enrollment/<int:pk>/remove/', views.enrollment_remove, name='enrollment_remove'),
    path('instructors/', views.instructor_list, name='instructors'),
    path('instructors/new/', views.instructor_create, name='instructor_create'),
    path('instructors/<int:pk>/edit/', views.instructor_update, name='instructor_update'),
]
