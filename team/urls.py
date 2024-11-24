# team/urls.py
from django.urls import path
from . import views
from .views import export_members, import_members
app_name = 'team'
urlpatterns = [
    path('', views.team_list, name='team_list'),
    path('add/', views.add_member, name='add_member'),
    path('export/', export_members, name='export_members'),
    path('import/', import_members, name='import_members'),
    
    path('<int:pk>/', views.member_detail, name='member_detail'),  # URL cho chi tiết thành viên
    path('<int:pk>/edit/', views.edit_member, name='edit_member'), 
    path('<int:pk>/delete/', views.delete_member, name='delete_member'),
  
]
