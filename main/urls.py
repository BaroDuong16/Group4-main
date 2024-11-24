from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'main'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('home_module/', views.home_module, name='home_module'),
    path('home_course/', views.home_course, name='home_course'),
    path('', views.home, name='home'),  
    path('logout/', LogoutView.as_view(next_page='main:home'), name='logout'),
    path('accounts/login/', views.login_view, name='login'),

    path('register/user_info/', views.register_user_info, name='register_user_info'),
    path('register/confirmation_code/', views.register_confirmation_code, name='register_confirmation_code'),
    path('register_email/', views.register_email, name='register_email'),

    path('resend-code-auto/', views.resend_code_auto, name='resend_code_auto'),
    path('accounts/password_reset/', views.password_reset_request, name='password_reset_request'),
    path('accounts/password_reset_code/', views.password_reset_code, name='password_reset_code'),
    path('accounts/password_reset_form/', views.password_reset_form, name='password_reset_form'),
    
]
