from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import StudentPerformance

# Resource for StudentPerformance model
class StudentPerformanceResource(resources.ModelResource):
    class Meta:
        model = StudentPerformance
        fields = ('user', 'course', 'assessment', 'score', 'feedback')  # Fields for import/export
        export_order = ('user', 'course', 'assessment', 'score', 'feedback')

# Admin configuration
@admin.register(StudentPerformance)
class StudentPerformanceAdmin(ImportExportModelAdmin):
    resource_class = StudentPerformanceResource
    list_display = ('user', 'course', 'assessment', 'score', 'feedback')  # Fields to display in the admin list view
    search_fields = ('user__username', 'course__course_name', 'assessment__title')  # Fields to search in the admin interface
