from django.contrib import admin
from .models import Assignment
from import_export.admin import ImportExportModelAdmin
from import_export import resources
class AssignmentResource(resources.ModelResource):
    class Meta:
        model = Assignment
        exclude = ('id',)
        fields = ('assignment_id','assignment_name')
        import_id_fields = ('assignment_id',)
class AssignmentAdmin(ImportExportModelAdmin):
    resource_class = AssignmentResource
    list_display = ('assignment_id','assignment_name')
admin.site.register(Assignment, AssignmentAdmin)

#Import/Export của model Assignment