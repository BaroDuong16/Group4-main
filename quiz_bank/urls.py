from django.urls import path
from .views import bank_request_views, question_request_views, import_request_views

app_name = 'quiz_bank'

urlpatterns = [
    path('', bank_request_views.quiz_bank_view, name='quiz_bank_view'),
    path('show/<int:course_id>/', bank_request_views.quiz_bank_course, name='quiz_bank_course'),
    path('random/<int:course_id>/<int:number_of_questions>', bank_request_views.random_question_view, name='random_question_view'),
    path('show/<int:course_id>/delete/<int:question_id>', question_request_views.delete_question, name='delete_question'),
    path('show/<int:course_id>/edit/<int:question_id>', question_request_views.edit_question, name='edit_question'),
    path('import/', import_request_views.import_quiz_bank, name='import_quiz_bank'),
    path('show/<int:course_id>/import/', import_request_views.import_quiz_bank_from_page, name='import_quiz_bank_from_page'),
] 