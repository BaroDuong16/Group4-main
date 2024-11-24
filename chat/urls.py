from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('users/', views.chat_view, name='user_list'),  # User list view
    path('messages/<str:username>/', views.chat_view, name='chat_view'),  # One-on-one chat view

    # Group chat paths
    path('group/create/', views.create_group_chat_view, name='create_group_chat'),  # Group chat creation
    path('group/<int:group_id>/', views.chat_view, name='chat_view'),  # Group chat messaging view
    path('group/<int:group_id>/add_member/', views.add_member_to_group_view, name='add_member_to_group'),
    path('group/<int:group_id>/remove_member/', views.remove_member_from_group_view, name='remove_member_from_group'),
    path('edit_message/<int:message_id>/', views.edit_message_view, name='edit_message'),
    path('delete_message/<int:message_id>/', views.delete_message_view, name='delete_message'),
    # path('notifications/', views.notifications_view, name='notifications'),
]


