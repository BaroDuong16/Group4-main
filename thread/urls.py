from django.urls import path
from . import views

app_name = 'thread'

urlpatterns = [
    path('', views.thread_list, name='thread_list'),
    path('create/', views.createThread, name='create_thread'),
    path('update/<int:pk>/', views.updateThread, name='update_thread'),
    path('delete/<int:pk>/', views.deleteThread, name='delete_thread'),
    path('detail/<int:pk>',views.thread_detail, name= 'thread_detail'),
    path('detail/<int:pk>/comments/add/', views.add_comment, name='add_comment'),
    path('detail/<int:pk>/comments/<int:comment_id>/edit/', views.update_comment, name='update_comment'),
    path('detail/<int:pk>/comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('moderation_warning/', views.moderation_warning, name='moderation_warning'),
    path('course/<int:course_id>/', views.thread_list, name='thread_list_by_course'),
    path('react/<int:thread_id>/', views.react_to_thread, name='react_to_thread'),
    path('comment/react/<int:comment_id>/',views.react_to_comment, name='react_to_comment'),
    path('report_dashboard/',views.report_dashboard,name='report_dashboard'),
]





