from django.urls import path
from . import views

app_name = 'user_summary'

urlpatterns = [
    path('', views.user_summary, name='user_summary'),
]
