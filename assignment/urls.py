from django.urls import path
from . import views

app_name = 'assignment'
urlpatterns = [
    path('assignment', views.assignment_list, name='assignment_list'),
    path('assignment/add/', views.assignment_add, name='assignment_add'),
    path('assignment/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('assignment/<int:pk>/edit/', views.assignment_edit, name='assignment_edit'),
    path('assignment/<int:pk>/delete/', views.assignment_delete, name='assignment_delete'),
]