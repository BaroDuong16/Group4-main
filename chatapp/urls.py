from django.urls import path
from . import views

app_name = 'chatapp'

urlpatterns = [
    path('', views.index, name='index'),  # Ensure this points to your view
    path('specific', views.specific,name='specific'),
    path('getUserResponse',views.getUserResponse,name='getUserResponse')
    #path('chatbot',views.chatbot,name='chatbot')   
]
