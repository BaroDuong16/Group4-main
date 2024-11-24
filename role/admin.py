from django.contrib import admin
from .models import Role
from django.contrib.auth.models import Permission

class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name',)
    search_fields = ('role_name',)
    filter_horizontal = ('permissions', 'modules')  # Cho phép chọn nhiều quyền và module

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Chỉ lấy một số quyền cụ thể
        if db_field.name == "permissions":
            # Lọc các quyền bạn muốn hiển thị từ Meta
            specific_permissions = Role._meta.permissions  # Lấy danh sách quyền từ Meta
            kwargs["queryset"] = Permission.objects.filter(
                codename__in=[codename for codename, _ in specific_permissions]  # Lấy chỉ codename
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

# Đăng ký mô hình Role với admin
admin.site.register(Role, RoleAdmin)