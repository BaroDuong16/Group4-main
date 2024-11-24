from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import AssessmentType, Assessment, InvitedCandidate, StudentAssessmentAttempt, UserAnswer
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from course.models import Course
from user.models import User  # Ensure you import User model

class AssessmentResource(resources.ModelResource):
    course = fields.Field(
        column_name='course__course_name',
        attribute='course',
        widget=ForeignKeyWidget(Course, 'course_name')
    )
    created_by = fields.Field(
        column_name='created_by__username',  # Match your import column name
        attribute='created_by',  # Field in your model
        widget=ForeignKeyWidget(User, 'username')  # Use appropriate field for lookup
    )
    assessment_type = fields.Field(  # Corrected this
        column_name='assessment_type__type_name',  # Match your import column name
        attribute='assessment_type',  # Field in your model
        widget=ForeignKeyWidget(AssessmentType, 'type_name')  # Correctly refer to AssessmentType
    )

    class Meta:
        model = Assessment
        fields = (
            'id',
            'course',
            'title',
            'assessment_type',  # Use the field name directly
            'invited_count',
            'assessed_count',
            'qualified_count',
            'created_at',
            'created_by'
        )
        export_order = (
            'id',
            'course',
            'title',
            'assessment_type',  # Use the field name directly
            'invited_count',
            'assessed_count',
            'qualified_count',
            'created_at',
            'created_by'
        )

# Register Assessment with ImportExportModelAdmin
@admin.register(Assessment)
class AssessmentAdmin(ImportExportModelAdmin):
    resource_class = AssessmentResource
    list_display = ('title', 'course', 'assessment_type', 'invited_count', 'assessed_count', 'qualified_count')
    search_fields = ('title', 'course__course_name', 'assessment_type__type_name')  # Fixed typo 'coure_name'
    list_filter = ('course', 'assessment_type')

# Define resources for other models and register similarly
class InvitedCandidateResource(resources.ModelResource):
    class Meta:
        model = InvitedCandidate

@admin.register(InvitedCandidate)
class InvitedCandidateAdmin(ImportExportModelAdmin):
    resource_class = InvitedCandidateResource
    list_display = ('email', 'assessment', 'invitation_date', 'expiration_date')
    search_fields = ('email', 'assessment__title')

class StudentAssessmentAttemptResource(resources.ModelResource):
    class Meta:
        model = StudentAssessmentAttempt
        fields = ('id', 'user__username', 'assessment__title', 'score_quiz', 'score_ass', 'attempt_date')

@admin.register(StudentAssessmentAttempt)
class StudentAssessmentAttemptAdmin(ImportExportModelAdmin):
    resource_class = StudentAssessmentAttemptResource
    list_display = ('user', 'assessment', 'score_quiz', 'score_ass', 'attempt_date')
    search_fields = ('user__username', 'assessment__title')
    list_filter = ('assessment', 'attempt_date')


from .models import AssessmentType

# Resource class for import/export functionality
class AssessmentTypeResource(resources.ModelResource):
    class Meta:
        model = AssessmentType
        fields = ('id', 'type_name')  # Specify the fields to be used for import/export

# Register AssessmentType with import/export functionality in the admin
@admin.register(AssessmentType)
class AssessmentTypeAdmin(ImportExportModelAdmin):
    resource_class = AssessmentTypeResource
    list_display = ('type_name',)  # Columns to be displayed in the list view
    search_fields = ('type_name',)  # Add search functionality by `type_name`
