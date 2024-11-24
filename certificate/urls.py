from django.urls import path
from . import views

app_name = 'certificate'

urlpatterns = [
    # path('', views.certificate_summary, name='certificate_summary'),
    path('pdf/<int:id>/', views.certificate_pdf, name='certificate_pdf'),
    path('summary/', views.certificate_summary, name='certificate_summary'),

]

