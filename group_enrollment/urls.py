# enrollment/urls.py
from django.urls import path
from . import views

app_name = 'group_enrollment' 

urlpatterns = [
    path('', views.enrollment_list, name='enrollment_list'),
    path('enroll/', views.admin_enroll_users, name='admin_enroll_users'),
    path('fetch-enrolled-users/', views.fetch_enrolled_users, name='fetch_enrolled_users'),
    
    # path('enroll/', views.fetch_enrolled_users, name='fetch_enrolled_users'),
    # path('my-courses/', views.enrollment_list, name='enrollment_list'),
    path('edit/<int:enrollment_id>/', views.edit_enrollment, name='edit_enrollment'),  # Edit enrollment
    path('delete/<int:enrollment_id>/', views.delete_enrollment, name='delete_enrollment'),  # Delete enrollment
]
