# admin.py

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Student

# Resource class for Student
class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        fields = ('id', 'first_name', 'last_name', 'email', 'enrolled_at', 'is_active')

# Register Student with import/export functionality
@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource
    list_display = ('first_name', 'last_name', 'email', 'enrolled_at', 'is_active')
