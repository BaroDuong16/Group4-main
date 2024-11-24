from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import CollaborationGroup, GroupMember
from user.models import User
from course.models import Course  # Ensure this model is correctly defined in course.models

# CollaborationGroup Resource
class CollaborationGroupResource(resources.ModelResource):
    courses = fields.Field(
        column_name='courses__name',  # The name attribute to import/export
        attribute='courses',
        widget=ForeignKeyWidget(Course, 'name')  # Use 'name' to link to the Course model
    )
    created_by = fields.Field(
        column_name='created_by__username',  # The username attribute to import/export
        attribute='created_by',
        widget=ForeignKeyWidget(User, 'username')  # Use 'username' to link to the User model
    )

    class Meta:
        model = CollaborationGroup
        fields = ('id', 'group_name', 'courses', 'created_by', 'created_at')  # Specify fields for import/export
        export_order = ('id', 'group_name', 'courses', 'created_by', 'created_at')  # Define the export order

# GroupMember Resource
class GroupMemberResource(resources.ModelResource):
    group = fields.Field(
        column_name='group__group_name',  # The group_name attribute to import/export
        attribute='group',
        widget=ForeignKeyWidget(CollaborationGroup, 'group_name')  # Link to CollaborationGroup using group_name
    )
    user = fields.Field(
        column_name='user__username',  # The username attribute to import/export
        attribute='user',
        widget=ForeignKeyWidget(User, 'username')  # Link to User using username
    )

    class Meta:
        model = GroupMember
        fields = ('id', 'group', 'user', 'joined_at')  # Specify fields for import/export
        export_order = ('id', 'group', 'user', 'joined_at')  # Define the export order

# Admin registration for CollaborationGroup
@admin.register(CollaborationGroup)
class CollaborationGroupAdmin(ImportExportModelAdmin):
    resource_class = CollaborationGroupResource
    list_display = ('group_name', 'get_courses', 'created_by', 'created_at')  # Use a method for courses display
    search_fields = ('group_name', 'created_by__username', 'courses__name')  # Search fields
    list_filter = ('created_by', 'courses')  # Filter options

    def get_courses(self, obj):
        return ", ".join(course.name for course in obj.courses.all())  # Display course names in admin

    get_courses.short_description = 'Courses'  # Admin column header

# Admin registration for GroupMember
@admin.register(GroupMember)
class GroupMemberAdmin(ImportExportModelAdmin):
    resource_class = GroupMemberResource
    list_display = ('get_group_name', 'get_username', 'joined_at')  # Use methods for display
    search_fields = ('group__group_name', 'user__username')  # Search fields
    list_filter = ('group', 'user')  # Filter options

    def get_group_name(self, obj):
        return obj.group.group_name  # Display group name in admin

    get_group_name.short_description = 'Group Name'  # Admin column header

    def get_username(self, obj):
        return obj.user.username  # Display username in admin

    get_username.short_description = 'User'  # Admin column header
