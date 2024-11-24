from django.urls import path
from . import views

app_name = 'student_performance'

urlpatterns = [
    path('student_performance/', views.student_performance_list, name='student_performance_list'),
    path('student_performance/<int:pk>/', views.student_performance_detail, name='student_performance_detail'),
    path('student_performance/create/', views.student_performance_add, name='student_performance_add'),
    path('student_performance/<int:pk>/edit/', views.student_performance_edit, name='student_performance_edit'),
    path('student_performance/<int:pk>/delete/', views.student_performance_delete, name='student_performance_delete'),
]
