from django.urls import path
from . import views

app_name = 'course_completion'

urlpatterns = [
    path('', views.course_completion_list, name = 'course_completion_list'),
]