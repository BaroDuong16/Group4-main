from django.urls import include, path, re_path

from . import views


app_name = 'cheat_logger'

urlpatterns = [
    path('', views.Log.as_view()),  

]


