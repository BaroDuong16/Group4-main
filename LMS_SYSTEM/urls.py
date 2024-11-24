"""
URL configuration for LMS_SYSTEM project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path, include
from .views import home_view
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('ckeditor/', include('ckeditor_uploader.urls')),  # for file upload
    
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('module_group/', include('module_group.urls')),  
    path('subject/', include('subject.urls')), 
    path('student_materials/', include('student_materials.urls')),
    path('training_program/', include('training_program.urls')),

    #ngattt
    path('group_enrollment/', include('group_enrollment.urls')),
    path('mylearning/', include('mylearning.urls')),
    path('certification/', include('certification.urls')),
    path('learning_path/', include('learning_path.urls')),
    path('backup/', include('backup.urls')),
    path('student_portal/', include('student_portal.urls')),
    #path('quiz_generator/', include('quiz_generator.urls')),
    
    #group01
    path('user/', include(('user.urls', 'user'), namespace='user')),  # Register user app URLs with a namespace
    path('role/', include(('role.urls', 'user'))),
    path('department/', include(('department.urls', 'department'))),
    path('team/', include(('team.urls', 'team'))),

    #group02
    path('course/', include('course.urls')),
    path('feedback/', include('feedback.urls', namespace='feedback')),
    path('forum/', include('forum.urls', namespace='forum')),

    #group03
    path('quiz/', include('quiz.urls')),  
    # path('std_quiz/', include('std_quiz.urls')),
    # path('course_Truong/', include('course_Truong.urls')),
    path('tools/', include('tools.urls')),
    

    #group04
    path('chat/', include('chat.urls')),
    path('chatapp/', include('chatapp.urls')),
    path('thread/', include('thread.urls')),
    path('collaboration_group/', include('collaboration_group.urls')),

    #group05
    path('activity/', include('activity.urls', namespace='activity')),  # Ensure this line exists
    path('analytics_report/', include('analytics_report.urls')),
    path('progress_notification', include('progress_notification.urls')),
    path('book/', include('book.urls')),
    path('achievement/',include('achievement.urls')),
    path('quiz_bank/',include('quiz_bank.urls')),

    #group06 - Binh_Thang - Coding
    path('exercises/', include('exercises.urls')), 
    path('assessments/', include('assessments.urls')),
    path('reports/', include('reports.urls'))

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)