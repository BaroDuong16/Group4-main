from django.urls import path,include
from .views import *

app_name = 'performance_analytics'
urlpatterns = [
    path('summary/',view=performance_analytics_summary,name='performance_analytics_summary')
    
    
]