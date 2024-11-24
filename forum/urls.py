from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.question_list, name='question_list'),
    path('question/<int:pk>/', views.question_detail, name='question_detail'),
    path('create/', views.create_question, name='create_question'),
    path('question/<int:pk>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:pk>/delete/', views.delete_question, name='delete_question'),
    path('comment/<int:pk>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('reply/<int:pk>/edit/', views.edit_reply, name='edit_reply'),
    path('reply/<int:pk>/delete/', views.delete_reply, name='delete_reply'),
    path('question/<int:pk>/like/', views.like_question, name='like_question'),
    path('question/<int:pk>/dislike/', views.dislike_question, name='dislike_question'),
    path('comment/<int:pk>/like/', views.like_comment, name='like_comment'),
    path('comment/<int:pk>/dislike/', views.dislike_comment, name='dislike_comment'),
    path('reply/<int:pk>/like/', views.like_reply, name='like_reply'),
    path('reply/<int:pk>/dislike/', views.dislike_reply, name='dislike_reply'),
    path('report/<str:report_type>/<int:report_id>/', views.report_content, name='report_content'),
    path('reports/', views.report_list, name='report_list'),
]