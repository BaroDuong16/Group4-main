from django.urls import path
from . import views
app_name = 'ai_insights'

urlpatterns = [
    path('', views.ai_insights_list, name='ai_insights_list'),
    path('<int:id>/', views.ai_insights_detail, name='ai_insights_detail'),
    path('create/', views.ai_insights_add, name='ai_insights_add'),
    path('edit/<int:id>/', views.ai_insights_edit, name='ai_insights_edit'),
    path('delete/<int:id>/', views.ai_insights_delete, name='ai_insights_delete'),
    path('import/', views.import_ai_insights, name='import_ai_insights'),
    path('export/', views.export_ai_insights, name='export_ai_insights'),
    path('summary/', views.ai_insights_summary, name='ai_insights_summary'),

    
]
