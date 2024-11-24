# collaboration_group/urls.py
from django.urls import path
from .views import (
    collaboration_group_list,
    collaboration_group_add,
    collaboration_group_edit,
    collaboration_group_delete,
    manage_group,
    remove_member,
    join_group,
    check_members,
)

app_name = 'collaboration_group'

urlpatterns = [
    path('', collaboration_group_list, name='collaboration_group_list'),
    path('add/', collaboration_group_add, name='collaboration_group_add'),
    path('<int:pk>/edit/', collaboration_group_edit, name='collaboration_group_edit'),
    path('<int:pk>/delete/', collaboration_group_delete, name='collaboration_group_delete'),
    path('<int:group_id>/manage/', manage_group, name='manage_group'),
    path('<int:group_id>/remove/<int:member_id>/', remove_member, name='remove_member'),
    path('join/<int:group_id>/', join_group, name='join_group'),  
    path('check_members/<int:group_id>/', check_members, name='check_members'),
]
