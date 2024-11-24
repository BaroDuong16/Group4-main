
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Certificate

# Resource for Certificate model
class CertificateResource(resources.ModelResource):
    class Meta:
        model = Certificate
        fields = ('id', 'user', 'course', 'issue_date', 'certificate_url')  # Add fields to import/export
        export_order = ('id', 'user', 'course', 'issue_date', 'certificate_url')

# Admin configuration
@admin.register(Certificate)
class CertificateAdmin(ImportExportModelAdmin):
    resource_class = CertificateResource
    list_display = ('user', 'course', 'issue_date', 'certificate_url')  # Fields to display in the admin list view
    search_fields = ('user__username', 'course__course_name', 'certificate_url')  # Fields to search in the admin interface

