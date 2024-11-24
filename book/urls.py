from django.urls import path
from . import views

app_name = 'book'

urlpatterns = [
    path('', views.book_search_view, name='book_search'),
    path('<str:book_id>/', views.book_detail_view, name='book_detail'),
]