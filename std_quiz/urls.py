from django.urls import path
from . import views


app_name = 'std_quiz'

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('detail/<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('<int:quiz_id>/result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
    path('quiz/<int:quiz_id>/take_invited/', views.take_quiz_invited, name='take_quiz_invited'),
    path('quiz/<int:quiz_id>/result_invited/<int:attempt_id>/', views.quiz_result_invited, name='quiz_result_invited'),
    path('quizzes_invite/', views.quiz_list_invite, name='quiz_list_invite'),

]