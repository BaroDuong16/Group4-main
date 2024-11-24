from django.urls import path
from . import views

app_name = 'student_materials'

urlpatterns = [
#for new ones
    path('', views.subject_list, name='subject_list'),
    path('subject/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),

#for old ones
    path('materials/', views.select_material, name='select_material'),
    path('materials/download/all/<str:material_type>/', views.download_all_materials, name='download_all_materials'),
    path('materials/view/<int:material_id>/', views.view_material, name='view_material'),
    path('view_pdf/<path:google_drive_link>/', views.view_pdf, name='view_pdf'),
    path('view_material/<int:material_id>/', views.view_material, name='view_material'),  # Change id to mat
    # AJAX endpoints
    path('api/training_programs/<int:training_program_id>/subjects/', views.get_subjects, name='get_subjects'),
    path('api/subjects/<int:subject_id>/material_types/', views.get_material_types, name='get_material_types'),
    
    # This endpoint should be for displaying materials by type
    path('api/material_types/<str:material_type>/', views.display_materials_by_type, name='display_materials_by_type'),
    
]
