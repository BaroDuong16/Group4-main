from django.contrib import admin
from .models import UserActivityLog

class UserActivityLogAdmin(admin.ModelAdmin):
    # Specify the fields to be displayed in the list view
    list_display = ('user', 'activity_type', 'activity_details', 'activity_timestamp')
    
    # Add search functionality for 'user' and 'activity_type'
    search_fields = ('user__username', 'activity_type')
    
    # Optional: Add filters for better usability
    list_filter = ('activity_type', 'activity_timestamp')

# Register the UserActivityLog model with the admin site
admin.site.register(UserActivityLog, UserActivityLogAdmin)