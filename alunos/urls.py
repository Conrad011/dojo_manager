from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list, name='list'),
    path('new/', views.student_create, name='create'),
    path('<int:pk>/', views.student_detail, name='detail'),
    path('<int:pk>/edit/', views.student_update, name='update'),
    path('<int:pk>/delete/', views.student_delete, name='delete'),
    path('<int:pk>/graduation/', views.graduation_add, name='graduation'),
    path('belts-by-modality/', views.belts_by_modality, name='belts_by_modality'),
    path('modalities/', views.modality_list, name='modalities'),
    path('modalities/new/', views.modality_create, name='modality_create'),
    path('modalities/<int:modality_pk>/belt/', views.belt_create, name='belt_create'),
]
