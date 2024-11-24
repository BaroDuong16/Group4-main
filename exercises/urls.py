from django.urls import path
from . import views

app_name = 'exercises'

urlpatterns = [
    path('', views.exercise_list, name='exercise_list'),
    path('exercise/add/', views.exercise_add, name='exercise_add'),

    path('exercise/<int:exercise_id>/', views.exercise_detail, name='exercise_detail_no_attempt'),
    path('exercise/<int:exercise_id>/<int:assessment_id>/', views.exercise_detail, name='exercise_detail'),

    # path('exercise/<int:exercise_id>/', views.exercise_detail, name='exercise_detail'),
    # path('exercise/<int:exercise_id>/submit/', views.submit_code, name='submit_code'),
    path('submit/<int:exercise_id>/<int:assessment_id>/', views.submit_code, name='submit_code'),

    path('result/<int:submission_id>/', views.result_detail, name='result_detail'),
    path('results/', views.result_list, name='result_list'),
    path('precheck/<int:exercise_id>/', views.precheck_code, name='precheck_code'),
]
