from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.notifications_list, name='notifications_list'),
    path('add/', views.add_notification, name='add_notification'),
    path('update/<int:id>/', views.update_notification, name='update_notification'),
    path('delete/<int:id>/', views.delete_notification, name='delete_notification'),
    path('<int:id>/', views.notification_detail, name='notification_detail'),
    path('download/<int:id>/', views.download_file, name='download_file'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('api/unread-count/', views.get_unread_notifications_count, name='unread_notifications_count'),
    path('api/mark-read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)