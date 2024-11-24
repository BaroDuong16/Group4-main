# certification/urls.py
from django.urls import path
from . import views

app_name = 'certification'

urlpatterns = [
    path('', views.certification_list, name='certification_list'),
    path('<int:pk>/', views.certification_detail, name='certification_detail'),
    path('create/', views.certification_create, name='certification_create'),
    path('<int:pk>/edit/', views.certification_update, name='certification_update'),
    path('<int:pk>/delete/', views.certification_delete, name='certification_delete'),
]
