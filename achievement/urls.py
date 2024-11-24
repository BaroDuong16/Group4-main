from django.urls import path
from . import views

app_name = 'achievement'

urlpatterns = [
    path('user_progress/',views.user_progress, name='user_progress'),
    path('performance_analytics/',views.performance_analytics,name='performance_analytics'),
    path('ai_insights/',views.ai_insights,name='ai_insights')
]