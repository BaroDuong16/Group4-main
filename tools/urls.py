from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('excel_to_json_view/',views.excel_to_json_view , name='excel_to_json_view'),
    path('txt_to_json_view/',views.txt_to_json_view , name='txt_to_json_view'),
    path('download_zip_file/', views.download_zip_file, name='download_zip_file'),
]