from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import AIInsights


# Resource for import/export functionality
class AIInsightsResource(resources.ModelResource):
    class Meta:
        model = AIInsights
        fields = ('id', 'user', 'course', 'insight_text', 'insight_type', 'created_at')  # Add the fields to import/export

# Admin configuration
@admin.register(AIInsights)
class AIInsightsAdmin(ImportExportModelAdmin):
    resource_class = AIInsightsResource
    list_display = ('user', 'course', 'insight_text', 'insight_type', 'created_at')  # Fields to display in the admin list view
    search_fields = ('insight_text', 'insight_type')  # Fields to search in the admin interface

