from django.urls import path
from . import views

app_name = 'learning_path'

urlpatterns = [
    path('', views.learning_path_list, name='learning_path_list'),
    path('add/', views.learning_path_add, name='learning_path_add'),
    path('edit/<int:pk>/', views.learning_path_edit, name='learning_path_edit'),
    path('delete/<int:pk>/', views.learning_path_delete, name='learning_path_delete'),
    path('<int:learning_path_id>/steps/', views.step_list, name='step_list'),
    path('<int:learning_path_id>/steps/add/', views.step_add, name='step_add'),
    path('<int:learning_path_id>/steps/edit/<int:pk>/', views.step_edit, name='step_edit'),
    path('<int:learning_path_id>/steps/delete/<int:pk>/', views.step_delete, name='step_delete'),

    path('enroll/<int:learning_path_id>/', views.enroll, name='learning_path_enroll'),
    path('duplicate/<int:learning_path_id>/', views.duplicate, name='learning_path_duplicate'),
    path('recommend/<int:learning_path_id>/', views.recommend, name='learning_path_recommend'),
]


