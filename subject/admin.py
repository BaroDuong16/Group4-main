from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import Subject, Category, Lesson, Material
from django.utils import timezone

# Resource class for Subject
class SubjectResource(resources.ModelResource):
    class Meta:
        model = Subject
        fields = ('id', 'name', 'description', 'code')  # Fields to be imported/exported

# Register Subject with import/export functionality
@admin.register(Subject)
class SubjectAdmin(ImportExportModelAdmin):
    resource_class = SubjectResource
    list_display = ('name', 'code', 'description')  # Customize the list display
    search_fields = ('name', 'code')  # Enable searching by name and code

# Resource class for Category
class CategoryResource(resources.ModelResource):
    subject = fields.Field(
        column_name='subject__id',
        attribute='subject',
        widget=ForeignKeyWidget(Subject, 'id')  # Use 'id' to match the subject
    )

    class Meta:
        model = Category
        fields = ('id', 'category_name', 'subject')  # Fields to be imported/exported

# Register Category with import/export functionality
@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ('category_name', 'subject')  # Customize the list display
    search_fields = ('category_name', 'subject__name')  # Enable searching

from django.utils import timezone
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Subject, Lesson

# Resource class for Lesson
class LessonResource(resources.ModelResource):
    subject = fields.Field(
        column_name='subject__id',  # Use subject__id to match the foreign key in the import data
        attribute='subject',
        widget=ForeignKeyWidget(Subject, 'id')  # Use 'id' to match the subject
    )

    class Meta:
        model = Lesson
        fields = ('id', 'title', 'subject', 'description', 'content', 'created_at')

    def before_import_row(self, row, **kwargs):
        # Set created_at to current time if it's not provided
        if 'created_at' not in row or not row['created_at']:
            row['created_at'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')  # Format it as a string

# Register Lesson with import/export functionality
@admin.register(Lesson)
class LessonAdmin(ImportExportModelAdmin):
    resource_class = LessonResource
    list_display = ('title', 'subject', 'created_at', 'content')
    search_fields = ('title', 'subject__name', 'content')


# Resource class for Material
class MaterialResource(resources.ModelResource):
    lesson = fields.Field(
        column_name='lesson__id',
        attribute='lesson',
        widget=ForeignKeyWidget(Lesson, 'id')  # Use 'id' for matching the lesson
    )

    class Meta:
        model = Material
        fields = ('id', 'lesson','lesson__title', 'material_type', 'file', 'uploaded_at')  # Fields to be imported/exported

# Register Material with import/export functionality
@admin.register(Material)
class MaterialAdmin(ImportExportModelAdmin):
    resource_class = MaterialResource
    list_display = ('lesson', 'material_type', 'uploaded_at')  # Customize the list display
    search_fields = ('lesson__title', 'material_type')  # Enable searching
    list_filter = ('material_type', 'lesson__subject')  # Add filters for the list view
