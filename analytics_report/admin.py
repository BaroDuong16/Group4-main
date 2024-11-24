from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import AnalyticsReport

class AnalyticsReportResource(resources.ModelResource):
    class Meta:
        model = AnalyticsReport
        fields = ('report_id', 'report_date', 'report_type', 'report_data', 'generated_by')  # Specify fields to include

@admin.register(AnalyticsReport)
class AnalyticsReportAdmin(ImportExportModelAdmin):
    resource_class = AnalyticsReportResource