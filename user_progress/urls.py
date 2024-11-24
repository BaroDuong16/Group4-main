from django.urls import path
from . import views

app_name = 'user_progress'

urlpatterns = [
    path('summary/',views.user_progress_summary, name='user_progress_summary')
]