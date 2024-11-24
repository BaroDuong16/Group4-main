from django.urls import path
from . import views
app_name = 'progress_notification'

urlpatterns = [
    path('', views.progress_notification_list, name='progress_notification_list'),
    path('<int:id>/', views.progress_notification_detail, name='progress_notification_detail'),
    path('create/', views.progress_notification_add, name='progress_notification_add'),
    path('edit/<int:id>/', views.progress_notification_edit, name='progress_notification_edit'),
    path('delete/<int:id>/', views.progress_notification_delete, name='progress_notification_delete'),
    path('import/', views.import_progress_notification, name='import_progress_notification'),
    path('export/', views.export_progress_notification, name='export_progress_notification'),
    path('notification/count/', views.unread_notification_count, name='unread_notification_count'),
    path('notifications/', views.notification_list, name='notification_list'), 


]
