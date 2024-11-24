# learning/urls.py
from django.urls import path
from .views import index, learning_paths, certification, archived, learning_tools#, my_learning_view

app_name = 'mylearning'

urlpatterns = [
    path('', index, name='index'),  # This will be accessed at /mylearning/
    # path('', my_learning_view, name='index'),

    path('learning-paths/', learning_paths, name='learning_paths'),  # This will be accessed at /mylearning/learning-paths/
    path('certification/', certification, name='certification'),  # This will be accessed at /mylearning/certification/
    path('archived/', archived, name='archived'),  # This will be accessed at /mylearning/archived/
    path('learning-tools/', learning_tools, name='learning_tools'),  # This will be accessed at /mylearning/learning-tools/
]
