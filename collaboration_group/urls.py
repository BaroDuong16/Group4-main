from django.urls import path
from . import views

app_name = 'collaboration_group'

urlpatterns = [
    # Collaboration group list and management views
    path('', views.collaboration_group_list, name='collaboration_group_list'),
    path('add/', views.collaboration_group_add, name='collaboration_group_add'),
    path('<int:pk>/edit/', views.collaboration_group_edit, name='collaboration_group_edit'),
    path('<int:pk>/delete/', views.collaboration_group_delete, name='collaboration_group_delete'),

    # Group membership and user management views
    path('join/<int:group_id>/', views.join_group, name='join_group'),
    path('leave/<int:group_id>/', views.leave_group, name='leave_group'),
    path('<int:group_id>/manage/', views.manage_group, name='manage_group'),
    path('<int:group_id>/check_members/', views.check_members, name='check_members'),
    path('<int:group_id>/remove/<int:member_id>/', views.remove_member, name='remove_member'),
    path('groups/<int:group_id>/users/', views.user_list_view, name='user_list'),
    path('groups/<int:group_id>/add_member/<int:user_id>/', views.add_member, name='add_member'),

    # User-specific and feedback views
    path('my-groups/', views.my_groups_view, name='my_groups'),
    path('feedback/<int:group_id>/', views.feedback_selection_view, name='feedback_selection'),
    path('feedback/group/<int:group_id>/', views.group_feedback_view, name='group_feedback'),
    path('feedback/member/<int:group_id>/', views.member_feedback_view, name='member_feedback'),
    path('view-feedbacks/', views.view_feedbacks, name='view_feedbacks'),
]
