from django.urls import path
from . import views

app_name = 'reports'
urlpatterns = [
    # URL to load the report dashboard
    path('dashboard/', views.report_dashboard, name='report_dashboard'),
    
    path('course-overview/', views.course_overview_report, name='course_overview_report'),
    path('student-enrollment/', views.student_enrollment_report, name='student_enrollment_report'),
    path('course-completion/', views.course_completion_report, name='course_completion_report'),
    path('session-overview/', views.session_overview_report, name='session_overview_report'),
    path('material-usage/', views.material_usage_report, name='material_usage_report'),
    path('enrollment-trends/', views.enrollment_trends_report, name='enrollment_trends_report'),
    path('material-type-distribution/', views.material_type_distribution_report, name='material_type_distribution_report'),
    path('tag-report/', views.tag_report, name='tag_report'),
    path('user-progress/', views.user_progress_report, name='user_progress_report'),
    path('instructor-performance/', views.instructor_performance_report, name='instructor_performance_report'),
    path('user_overview_report/', views.user_overview_report, name='user_overview_report'),  
    path('student-id-report/', views.student_id_report, name='student_id_report'),
    path('students/<str:cohort>/', views.get_students_by_cohort, name='get_students_by_cohort'),
    path('role-report/', views.role_report, name='role_report'),
    path('user_statistics_report/', views.user_statistics_report, name='user_statistics_report'),  
    path('login-frequency-report/', views.login_frequency_report, name='login_frequency_report'),
    path('user_duration_login/', views.user_duration_login, name='user_duration_login'),
    path('group-list/', views.group_list, name='group_list'),
    path('course-distribution/', views.course_distribution, name='course_distribution'),
    path('group-performance/', views.group_performance, name='group_performance'),
    path('member_feedback/', views.member_feedback, name='member_feedback'),
]
