from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import ProgressNotification

class ProgressNotificationResource(resources.ModelResource):
    class Meta:
        model = ProgressNotification
        fields = ('user', 'course', 'notification_message')  # Specify fields to include


@admin.register(ProgressNotification)
class ProgressNotificationAdmin(ImportExportModelAdmin):
    resource_class = ProgressNotificationResource
    list_display = ('user', 'course', 'notification_message') 