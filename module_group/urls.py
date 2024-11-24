from django.urls import path
from . import views

app_name = 'module_group'

urlpatterns = [
    # Module Group URLs
    path('', views.module_group_list, name='module_group_list'),
    path('add/', views.module_group_add, name='module_group_add'),
    path('<int:pk>/', views.module_group_detail, name='module_group_detail'),
    path('<int:pk>/edit/', views.module_group_edit, name='module_group_edit'),
    path('<int:pk>/delete/', views.module_group_delete, name='module_group_delete'),
    path('import/modulegroups', views.import_module_groups, name='import_module_groups'),
    path('export/modulegroups', views.export_module_groups, name='export_module_groups'),
    # Module URLs
    path('modules/', views.module_list, name='module_list'),
    path('modules/add/', views.module_add, name='module_add'),
    path('modules/<int:pk>/', views.module_detail, name='module_detail'),
    path('modules/<int:pk>/edit/', views.module_edit, name='module_edit'),
    path('modules/<int:pk>/delete/', views.module_delete, name='module_delete'),
    path('import/modules', views.import_modules, name='import_modules'),
    path('export/modules', views.export_modules, name='export_modules'),
    
]
