from django.urls import path
from . import views

app_name = 'feedback'
urlpatterns = [
    path('instructor/<int:instructor_id>/', views.give_instructor_feedback, name='give_instructor_feedback'),
    path('course/<int:course_id>/', views.give_course_feedback, name='give_course_feedback'),
    path('training_program/<int:training_program_id>/', views.give_training_program_feedback, name='give_training_program_feedback'),
    path('success/', views.feedback_success, name='feedback_success'),
    path('list/', views.feedback_list, name='feedback_list'),
    path('instructor/feedback/<int:feedback_id>/', views.instructor_feedback_detail, name='instructor_feedback_detail'),
    path('course/feedback/<int:feedback_id>/', views.course_feedback_detail, name='course_feedback_detail'),
    path('program/feedback/<int:feedback_id>/', views.program_feedback_detail, name='program_feedback_detail'),
    path('course/<int:course_id>/all-feedback/', views.course_all_feedback, name='course_all_feedback'),
    path('coursefeedback/<int:pk>/helpful/', views.helpful_rate, name='helpful_rate'),
]
