from django.urls import path
from . import views
app_name = 'student'

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('register/', views.student_register, name='student_register'),
    path('<int:pk>/update/', views.student_update, name='student_update'),
    path('<int:pk>/delete/', views.student_delete, name='student_delete'),
]
