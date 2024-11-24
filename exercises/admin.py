from django.contrib import admin
from .models import Exercise, Submission
from import_export.admin import ImportExportModelAdmin
from import_export import resources
 
 
class ExerciseResource(resources.ModelResource):
    class Meta:
        model = Exercise
        fields = ('id', 'title', 'description', 'language', 'test_cases')  # Add fields you want to import/export
 
class SubmissionResource(resources.ModelResource):
    class Meta:
        model = Submission
        fields = ('id', 'user__id', 'exercise__title', 'code', 'score')
 
 
@admin.register(Exercise)
class ExerciseAdmin(ImportExportModelAdmin):
    resource_class = ExerciseResource
    list_display = ('title', 'language', 'description', 'language', 'test_cases')  # Adjust the fields displayed in the admin
    search_fields = ('title', 'language')  # Search fields for the admin
 
@admin.register(Submission)
class SubmissionAdmin(ImportExportModelAdmin):
    resource_class = SubmissionResource
    list_display = ('exercise', 'user', 'score')
    search_fields = ('exercise__title', 'user__id')
    list_filter = ('exercise',)
 
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('exercise', 'user')