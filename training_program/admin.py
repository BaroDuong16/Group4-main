from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from django.contrib import admin
from subject.models import Subject  # Ensure you have the correct import path for Subject
from training_program.models import TrainingProgram

# TrainingProgram Resource
class TrainingProgramResource(resources.ModelResource):
    # subjects = fields.Field(
    #     column_name='subjects',  # Column name in the import/export file
    #     attribute='subjects',
    #     widget=ForeignKeyWidget(Subject, 'subject_name')  # Assuming subject_name is the attribute to link to Subject
    # )

    class Meta:
        model = TrainingProgram
        fields = ('id', 'program_name', 'program_code', 'description')  # Add subjects field


# Admin registration for TrainingProgram
@admin.register(TrainingProgram)
class TrainingProgramAdmin(ImportExportModelAdmin):
    resource_class = TrainingProgramResource
    list_display = ('program_name', 'program_code', 'description')  # Display fields in the admin
    search_fields = ('program_name', 'program_code')  # Fields searchable in the admin
