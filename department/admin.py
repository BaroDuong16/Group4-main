from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models import Department, Location
from .forms import DepartmentForm
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget
from user.models import User
from course.models import Course

class DepartmentResource(resources.ModelResource):
    users = fields.Field(
        column_name='users',
        attribute='users',
        widget=ManyToManyWidget(User, field='username', separator=',')
    )
    courses = fields.Field(
        column_name='courses',
        attribute='courses',
        widget=ManyToManyWidget(Course, field='course_name', separator=',')
    )
    location = fields.Field(
        column_name='location__name',
        attribute='location',
        widget=ForeignKeyWidget(Location, 'name')
    )
    address = fields.Field(
        column_name='address',
        attribute='location__address',
    )

    class Meta:
        model = Department
        skip_unchanged = True
        report_skipped = True
        fields = ('name', 'location', 'address', 'users', 'courses')
        import_id_fields = ('name',)
        export_order = ('name', 'location', 'address', 'users', 'courses')
        

    def before_import_row(self, row, **kwargs):
        location_name = row['location__name']
        address = row.get('address', '')
        location, created = Location.objects.get_or_create(name=location_name)
        
        if created or (address and location.address != address):
            location.address = address
            location.save()

        row['location'] = location.id

    def skip_row(self, instance, original, row, import_validation, **kwargs):
        """
        So sánh dữ liệu mới và dữ liệu cũ, nếu không có sự thay đổi thì bỏ qua dòng này.
        """
        if instance.name == original.name and \
           instance.location == original.location and \
           instance.users == original.users and \
           instance.courses == original.courses:
            return True 

        return False

# Tạo DepartmentAdmin với tính năng ImportExport
class DepartmentAdmin(ImportExportModelAdmin):
    resource_class = DepartmentResource
    form = DepartmentForm
    list_display = ('name', 'get_location_name')  # Thay đổi để sử dụng phương thức

    def get_location_name(self, obj):
        return obj.location.name if obj.location else 'N/A'
    get_location_name.short_description = 'Location'

# Đăng ký các model vào admin
admin.site.register(Location)
admin.site.register(Department, DepartmentAdmin)