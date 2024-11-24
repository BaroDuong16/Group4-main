from django.urls import path
from . import views

app_name = 'backup'

urlpatterns = [
    path('', views.list_backups, name='list_backups'),
    path('create/', views.create_backup, name='create_backup'),
    path('restore/<int:backup_id>/', views.restore_backup, name='restore_backup'),
    path('delete/<int:backup_id>/', views.delete_backup, name='delete_backup'),
]
