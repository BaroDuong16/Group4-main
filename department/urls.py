from django.urls import path
from . import views

app_name = 'department'

urlpatterns = [
    # Location URLs
    path('locations/', views.location_list, name='location_list'),
    path('locations/<int:pk>/', views.location_detail, name='location_detail'),
    path('locations/new/', views.location_create, name='location_create'),
    path('locations/<int:pk>/edit/', views.location_update, name='location_update'),
    path('locations/delete/', views.location_delete, name='location_delete'),

    # Department URLs
    path('departments/', views.department_list, name='department_list'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),
    path('departments/new/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_update, name='department_update'),
    path('departments/delete/', views.department_delete, name='department_delete'),
    path('departments/import/', views.import_departments, name='import_departments'),
    path('departments/export/', views.export_departments, name='export_departments'),
]
