from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import DiscussionThread, ThreadComments
from user.models import User
from course.models import Course

# Resource class for DiscussionThread
class DiscussionThreadResource(resources.ModelResource):
    created_by = fields.Field(
        column_name='created_by__username',
        attribute='created_by',
        widget=ForeignKeyWidget(User, 'username')  # Reference User by username during import/export
    )
    course = fields.Field(
        column_name='course__name',  # Assuming the course model has a 'name' field
        attribute='course',
        widget=ForeignKeyWidget(Course, 'name')  # Reference Course by its name
    )

    class Meta:
        model = DiscussionThread
        fields = ('id', 'thread_title', 'thread_content', 'created', 'updated', 'created_by', 'course')

# Resource class for ThreadComments
class ThreadCommentsResource(resources.ModelResource):
    thread = fields.Field(
        column_name='thread__thread_title',
        attribute='thread',
        widget=ForeignKeyWidget(DiscussionThread, 'thread_title')  # Reference DiscussionThread by title
    )
    user = fields.Field(
        column_name='user__username',
        attribute='user',
        widget=ForeignKeyWidget(User, 'username')  # Reference User by username during import/export
    )

    class Meta:
        model = ThreadComments
        fields = ('comment_id', 'thread', 'user', 'comment_text', 'created', 'updated')

# Admin class for DiscussionThread
@admin.register(DiscussionThread)
class DiscussionThreadAdmin(ImportExportModelAdmin):
    resource_class = DiscussionThreadResource
    list_display = ('thread_title', 'created_by', 'course', 'created', 'updated')  # Display these fields in admin list
    search_fields = ('thread_title', 'created_by__username', 'course__name')  # Enable search by title, user, course
    list_filter = ('course', 'created_by')  # Filter by course and user

# Admin class for ThreadComments
@admin.register(ThreadComments)
class ThreadCommentsAdmin(ImportExportModelAdmin):
    resource_class = ThreadCommentsResource
    list_display = ('thread', 'user', 'comment_text', 'created', 'updated')  # Display fields in admin list
    search_fields = ('thread__thread_title', 'user__username', 'comment_text')  # Enable search by thread, user, comment
    list_filter = ('thread', 'user')  # Filter by thread and user
