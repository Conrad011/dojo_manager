from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('demo-logout/', views.demo_logout, name='demo_logout'),
]
