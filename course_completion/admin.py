from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import CourseCompletion

# Resource for CourseCompletion model
class CourseCompletionResource(resources.ModelResource):
    class Meta:
        model = CourseCompletion
        fields = ('completion_id', 'user_id', 'course_id', 'completion_date')  # Add fields for import/export
        export_order = ('completion_id', 'user_id', 'course_id', 'completion_date')

# Admin configuration
@admin.register(CourseCompletion)
class CourseCompletionAdmin(ImportExportModelAdmin):
    resource_class = CourseCompletionResource
    list_display = ('completion_id', 'user_id', 'course_id', 'completion_date')  # Fields to display in the admin list view
    search_fields = ('user_id__username', 'course_id__course_name', 'completion_date')  # Fields to search in the admin interface

