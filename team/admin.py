from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Member

# Tạo resource cho model Member
class MemberResource(resources.ModelResource):
    class Meta:
        model = Member
        fields = ('id','full_name' ,'name', 'role', 'email', 'homepage', 'profile_picture')  # Các trường cần import/export
        export_order = ('id','full_name', 'name', 'role', 'email', 'homepage', 'profile_picture')

# Cấu hình admin sử dụng ImportExportModelAdmin
@admin.register(Member)
class MemberAdmin(ImportExportModelAdmin):
    resource_class = MemberResource
    list_display = ('name', 'full_name','role', 'email', 'homepage')  # Hiển thị các trường này trong admin
