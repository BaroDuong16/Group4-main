from django.urls import include, path, re_path

from .views import managements, operations, query


app_name = 'assessment'

urlpatterns = [
    path('', managements.Assessment_list.as_view(), name='assessment_list'),
    path('create/', managements.Assessment_create.as_view(), name='assessment_create'),
    path('<int:pk>/edit/', managements.Assessment_edit.as_view(), name='assessment_edit'),
    path('<int:pk>/', managements.Assessment_detail.as_view(), name='assessment_detail'),

    path('type', managements.Assessment_Type_List_View.as_view(), name='assessment_type_list'),
    path('type/add/', managements.Assessment_Type_Create_View.as_view(), name='assessment_type_create'),
    path('type/edit/<int:pk>/', managements.Assessment_Type_Update_View.as_view(), name='assessment_type_update'),
    path('type/delete/<int:pk>/', managements.Assessment_Type_Delete_View.as_view(), name='assessment_type_delete'),

    path('<int:assessment_id>/attempt/', operations.Student_assessment_attempt.as_view(), name='student_assessment_attempt'),
    path('get-exercise-content/<int:exercise_id>/', query.Get_exercise_content.as_view(), name='get_exercise_content'),
    path('<int:pk>/invite/', operations.Invite_candidates.as_view(), name='invite_candidates'),
    
    path('invite/<uidb64>/<token>/', operations.Assessment_invite_accept.as_view(), name='assessment_invite_accept'),
    path('anonymous_info/<int:invited_candidate_id>/', operations.Handle_anonymous_info.as_view(), name='handle_anonymous_info'),  # Add this line
    path('create_asm_attempt/<int:assessment_id>/', operations.Create_asm_attempt.as_view(), name='create_asm_attempt'),
    path('take/<int:assessment_id>/', operations.Take_assessment.as_view(), name='take_assessment'),

    path('<int:assessment_id>/result/attempt-id=<int:attempt_id>/', operations.Assessment_result.as_view(), name='assessment_result'),
]


