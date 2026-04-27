from django.urls import path
from . import views

app_name = 'financial'

urlpatterns = [
    path('', views.financial_dashboard, name='dashboard'),
    path('fees/', views.fee_list, name='fees'),
    path('fees/new/', views.fee_create, name='fee_create'),
    path('fees/<int:pk>/edit/', views.fee_update, name='fee_update'),
    path('fees/<int:pk>/pay/', views.register_payment, name='pay'),
    path('fees/<int:pk>/receipt/', views.receipt, name='receipt'),
    path('fees/generate/', views.generate_fees, name='generate_fees'),
    path('plans/', views.plan_list, name='plans'),
    path('plans/new/', views.plan_create, name='plan_create'),
    path('plans/<int:pk>/edit/', views.plan_update, name='plan_update'),
    path('enrollments/new/', views.financial_enrollment_create, name='enrollment_create'),
]
