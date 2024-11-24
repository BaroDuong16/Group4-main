from django.urls import path
from . import views

app_name = 'subject'
urlpatterns = [
    path('', views.subject_list, name='subject_list'),
    path('add/', views.subject_add, name='subject_add'),
    path('subjects/edit/<int:pk>/', views.subject_edit, name='subject_edit'),
    path('subjects/delete/<int:pk>/', views.subject_delete, name='subject_delete'),
    path('upload/', views.upload_material, name='upload_material'),
    
    path('materials/<int:subject_id>/', views.subject_materials, name='subject_materials'),
    path('upload/', views.upload_material, name='upload_material'),  # Ensure this is included
    path('delete_material/<int:pk>/', views.delete_material, name='delete_material'),
    path('download/all/<str:material_type>/', views.download_all_materials, name='download_all_materials'),
    path('view/<int:material_id>/', views.view_material, name='view_material'),
    
]

