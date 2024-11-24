from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import User, Profile, Role, Student
from .forms import UserForm, UserEditForm

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import User, Profile, Role, Student

#Resource cho User
class UserProfileResource(resources.ModelResource):
    student_code = resources.Field()
    password = resources.Field(column_name='password')  # Thêm trường password

    class Meta:
        model = User
        exclude = ('id',)  # Bỏ qua trường id trong import
        import_id_fields = ['username']  # Sử dụng username để xác định người dùng
        skip_unchanged = True
        report_skipped = True
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password',  # Bao gồm mật khẩu trong export/import
            'profile__role__role_name',
            'profile__profile_picture_url',
            'profile__bio',
            'profile__interests',
            'profile__learning_style',
            'profile__preferred_language',
            'student_code',
        )

    def dehydrate_student_code(self, user):
        # Kiểm tra xem user có mối quan hệ với Student không và trả về student_code
        try:
            return user.student.student_code
        except Student.DoesNotExist:
            return ''

    def dehydrate_password(self, user):
        # Xuất mật khẩu (hashed)
        return user.password

    def export(self, queryset=None, *args, **kwargs):
        # Lọc ra các user không phải là superuser
        queryset = queryset.filter(is_superuser=False)
        return super().export(queryset, *args, **kwargs)

    def before_import_row(self, row, **kwargs):
        username = row.get('username')
        if not username:
            return

        try:
            user = User.objects.get(username=username)
            # Nếu người dùng đã có mật khẩu, giữ nguyên
            row['password'] = user.password if user.password else '123@'  # Nếu không có thì đặt mật khẩu mặc định
        except User.DoesNotExist:
            # Người dùng mới thì gán mật khẩu mặc định
            row['password'] = '123@'

    def after_import(self, dataset, result, **kwargs):
        for row in dataset.dict:
            username = row.get('username')
            student_code = row.get('student_code')

            if not username:
                print("Missing username. Skipping this entry.")
                continue
            
            # Tìm User theo username hoặc tạo mới
            user, created = User.objects.get_or_create(username=username)

            # Nếu user là superuser, bỏ qua
            if user.is_superuser:
                print(f"Skipping superuser with username {username}.")
                continue

            # Nếu có mật khẩu trong dữ liệu nhập, thiết lập mật khẩu
            password = row.get('password')
            if password:
                # Nếu mật khẩu đã được mã hóa, chỉ cần gán trực tiếp
                if password.startswith('pbkdf2_sha256$'):
                    user.password = password
                else:
                    user.set_password(password)
            # Gán mật khẩu mặc định nếu người dùng chưa có mật khẩu
            if created or (not user.password):  # Người dùng mới hoặc không có mật khẩu
                user.set_password('123@')  # Mật khẩu mặc định

            # Cập nhật các trường thông tin khác
            user.first_name = row.get('first_name', user.first_name)
            user.last_name = row.get('last_name', user.last_name)
            user.email = row.get('email', user.email)
            user.save()

            # Lấy hoặc tạo Role
            role_name = row.get('profile__role__role_name') or "N/A"
            role, created = Role.objects.get_or_create(role_name=role_name)

            # Cập nhật hoặc tạo Profile
            profile_data = {
                'role': role,
                'profile_picture_url': row.get('profile__profile_picture_url'),
                'bio': row.get('profile__bio'),
                'interests': row.get('profile__interests'),
                'learning_style': row.get('profile__learning_style'),
                'preferred_language': row.get('profile__preferred_language'),
            }
            Profile.objects.update_or_create(user=user, defaults={k: v for k, v in profile_data.items() if v is not None})

            # Nếu vai trò là "student", thêm vào bảng Student với student_code
            if role_name.lower() == 'student':
                Student.objects.update_or_create(user=user, defaults={'student_code': student_code})

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = True
    verbose_name_plural = 'Profiles'

# # Cập nhật CustomUserAdmin
# from import_export.results import RowResult
# class CustomUserAdmin(ImportExportModelAdmin, BaseUserAdmin):
#     resource_class = UserProfileResource
#     def _create_log_entries(self, result, request):
#         # Kiểm tra xem result có phải là một đối tượng hợp lệ và có thuộc tính totals
#         if isinstance(result, RowResult):
#             # Đảm bảo rằng trường 'skip' tồn tại trong kết quả
#             if 'skip' not in result.totals:
#                 result.totals['skip'] = 0  # Gán giá trị mặc định là 0 nếu không có
#         else:
#             print("Result is not a valid RowResult object.")
#             return

#         # Gọi phương thức gốc của ImportExportModelAdmin
#         super()._create_log_entries(result, request)


#     list_display = ('username', 'first_name', 'last_name', 'email', 'get_role', 'is_staff', 'is_active', 'date_joined')
#     list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups')
#     readonly_fields = ('date_joined',)

#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),  # Ensure 'password' field is handled properly
#         ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Modules', {'fields': ('modules',)}),
#         ('Important dates', {'fields': ('last_login', 'date_joined')}), 
#     )

#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active', 'modules')},
#         ),
#     )
#     filter_horizontal = ('groups', 'user_permissions', 'modules')

#     search_fields = ('username', 'email', 'first_name', 'last_name')
#     ordering = ('username',)
#     inlines = [ProfileInline]

#     def get_role(self, obj):
#         return obj.profile.role.role_name if hasattr(obj, 'profile') and obj.profile.role else 'No Role'
#     get_role.short_description = 'Role'

# if User in admin.site._registry:
#     admin.site.unregister(User)

# admin.site.register(User, CustomUserAdmin)


class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        fields = ('id', 'student_code', 'user__username', 'user__first_name', 'user__last_name', 'user__email', 'enrolled_courses')
        export_order = ('id', 'student_code', 'user__username', 'user__first_name', 'user__last_name', 'user__email', 'enrolled_courses')

class StudentAdmin(ImportExportModelAdmin):
    model = Student
    list_display = ('student_code', 'user', 'enrolled_courses_display')
    search_fields = ('student_code', 'user__username', 'user__email')

    def enrolled_courses_display(self, obj):
        return ", ".join(course.course_name for course in obj.enrolled_courses.all())
    enrolled_courses_display.short_description = 'Enrolled Courses'

# admin.site.register(Student, StudentAdmin)
# admin.site.register(User)