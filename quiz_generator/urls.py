from django.urls import path
from . import views
app_name = 'quiz_generator'
urlpatterns = [
    path('generate/', views.generate_question, name="generate_question"),
]
