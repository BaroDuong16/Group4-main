from django.shortcuts import render, get_object_or_404, redirect
from role.models import Role
from .models import Profile, User, Student
import pandas as pd
import bcrypt
from openpyxl import Workbook
from django.http import HttpResponse
from django.contrib import messages
from user.forms import UserForm, RoleForm, ExcelImportForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from .forms import UserEditForm
from functools import wraps
from django.contrib.auth.decorators import login_required
from django import forms
from .forms import UserCourseProgress
from course.models import Enrollment
from quiz.models import StudentQuizAttempt
from activity.models import UserActivityLog
from django.contrib.auth.hashers import check_password
from import_export.formats.base_formats import XLSX
from .admin import UserProfileResource
from tablib import Dataset
from io import StringIO
from django.utils import timezone
from datetime import timedelta
from module_group.models import ModuleGroup
from main.module_utils import get_grouped_modules
@login_required
def user_list(request):
    is_superuser = request.user.is_superuser
    module_groups = ModuleGroup.objects.all()  # Thay đổi theo cách bạn lấy dữ liệu
    grouped_modules = {group: group.modules.all() for group in module_groups}
    # Kiểm tra xem người dùng có profile hay không, nếu không là superuser thì hiện thông báo lỗi
    if not is_superuser and (not hasattr(request.user, 'profile') or request.user.profile is None):
        messages.error(request, "Bạn không có quyền.")
        return redirect('user:user_list')

    user_role_permissions = request.user.profile.role.permissions.values_list('codename', flat=True) if not is_superuser else []

    # Kiểm tra quyền
    can_detail_user = 'can_detail_user' in user_role_permissions or is_superuser
    can_add_user = 'can_add_user' in user_role_permissions or is_superuser
    can_edit_user = 'can_edit_user' in user_role_permissions or is_superuser
    can_delete_user = 'can_delete_user' in user_role_permissions or is_superuser
    can_import_users = 'can_import_users' in user_role_permissions or is_superuser
    can_export_users = 'can_export_users' in user_role_permissions or is_superuser

    # Lấy các thông tin tìm kiếm từ request
    query = request.GET.get('q', '')
    selected_role = request.GET.get('role', '')

    # Lấy danh sách người dùng, không bao gồm superuser
    users = User.objects.exclude(is_superuser=True)
    roles = Role.objects.all()
    form = ExcelImportForm()

    # Lọc người dùng dựa trên truy vấn tìm kiếm
    if query and selected_role:
        users = users.filter(
            Q(username__icontains=query),
            profile__role__role_name=selected_role
        )
    elif query:
        users = users.filter(username__icontains=query)
    elif selected_role:
        users = users.filter(profile__role__role_name=selected_role)

    not_found = not users.exists()
    users = users.order_by('username')

    # Phân trang
    paginator = Paginator(users, 5)
    page = request.GET.get('page', 1)


    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    module_groups, grouped_modules = get_grouped_modules(request.user, request.session.get('temporary_role'))
    return render(request, 'user_list.html', {
        'users': users,
        'query': query,
        'roles': roles,
        'selected_role': selected_role,
        'not_found': not_found,
        'form': form,
        'can_detail_user': can_detail_user,
        'can_add_user': can_add_user,
        'can_edit_user': can_edit_user,
        'can_delete_user': can_delete_user,
        'can_import_users': can_import_users,
        'can_export_users': can_export_users,
        'page_obj': users,
        'module_groups': module_groups,
        'grouped_modules': grouped_modules,
        'module_groups': module_groups,
        'grouped_modules': grouped_modules
    
    })



@login_required
def student_list(request):
    query = request.GET.get('q', '')
    students = Student.objects.all()
    form = ExcelImportForm()

    if query:
        students = students.filter(
            Q(user__username__icontains=query)
        )

    students = students.order_by('user__username')

    paginator = Paginator(students, 5)
    page = request.GET.get('page', 1)

    try:
        students = paginator.page(page)
    except PageNotAnInteger:
        students = paginator.page(1)
    except EmptyPage:
        students = paginator.page(paginator.num_pages)




    
    return render(request, 'student_list.html', {
        'students': students,
        'query': query,
        'form': form,
        'page_obj': students
    })

@login_required
def user_detail(request, pk):
    # Lấy user theo pk (không thay đổi ngữ cảnh)
    user = get_object_or_404(User, pk=pk)
    is_superuser = request.user.is_superuser

    # Kiểm tra nếu user hiện tại không phải là superuser và không có quyền truy cập
    if not is_superuser:
        # Kiểm tra nếu user không có profile hoặc không có quyền "can_detail_user"
        if not hasattr(request.user, 'profile') or not request.user.profile:
            messages.error(request, "Bạn không có quyền.")
            return redirect('user:user_list')

        user_role_permissions = request.user.profile.role.permissions.values_list('codename', flat=True)
        if 'can_detail_user' not in user_role_permissions:
            messages.error(request, "Bạn không có quyền.")
            return redirect('user:user_list')

    # Fetch learning progress
    course_progress = UserCourseProgress.objects.filter(user=user)
    courses_with_progress = [
        {
            'course': progress.course,
            'progress_percentage': progress.progress_percentage
        }
        for progress in course_progress
    ]

    # Fetch enrolled courses
    enrollments = Enrollment.objects.filter(student=user)

    # Initialize variables
    role = getattr(user.profile.role, 'role_name', None) if hasattr(user, 'profile') else None
    is_student = role == 'Student'
    student_code = "N/A"
    quiz_results = []

    # Fetch and order user activity logs
    two_days_ago = timezone.now() - timedelta(days=2)
    activity_logs = UserActivityLog.objects.filter(user=user, activity_timestamp__gte=two_days_ago).order_by('-activity_timestamp')

    # Phân trang cho nhật ký hoạt động
    paginator = Paginator(activity_logs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if is_student:
        try:
            student = Student.objects.get(user=user)
            student_code = student.student_code if student.student_code else "N/A"
            quiz_results = StudentQuizAttempt.objects.filter(user=user).select_related('quiz')
        except Student.DoesNotExist:
            student_code = "N/A"

    # Kiểm tra nếu user hiện tại là superuser
    
    return render(request, 'user_detail.html', {
        'user': user,
        'courses_with_progress': courses_with_progress,
        'enrollments': enrollments,
        'is_student': is_student,
        'is_superuser': is_superuser,
        'student_code': student_code,
        'quiz_results': quiz_results,
        'activity_logs': activity_logs,
        'page_obj': page_obj,

    })

@login_required
def user_add(request):
    is_superuser = request.user.is_superuser

    # Kiểm tra profile của người dùng
    if not is_superuser and (not hasattr(request.user, 'profile') or request.user.profile is None):
        messages.error(request, "Bạn không có quyền.")  # Thông báo lỗi
        return redirect('user:user_list')  # Chuyển hướng đến danh sách người dùng
    
    # Lấy quyền hạn của người dùng
    user_role_permissions = request.user.profile.role.permissions.values_list('codename', flat=True) if not is_superuser else []

    if 'can_add_user' not in user_role_permissions and not is_superuser:
        messages.error(request, "Bạn không có quyền .")  # Thông báo lỗi
        return redirect('user:user_list')  # Chuyển hướng đến danh sách người dùng

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            profile = Profile(
                user=user,
                role=form.cleaned_data['role'],
                profile_picture_url=form.cleaned_data.get('profile_picture_url', ''),
                bio=form.cleaned_data.get('bio', ''),
                interests=form.cleaned_data.get('interests', ''),
                learning_style=form.cleaned_data.get('learning_style', ''),
                preferred_language=form.cleaned_data.get('preferred_language', '')
            )
            profile.save()

            if profile.role.role_name == 'Student':
                try:
                    student_code = form.cleaned_data.get('student_code')  
                    student = Student(user=user, student_code=student_code)
                    student.save()
                    profile.student = student
                    profile.save()
                except Exception as e:
                    print('Error saving Student:', e)

            training_programs = form.cleaned_data.get('training_programs')
            if training_programs:
                user.training_programs.set(training_programs)

            messages.success(request, "Người dùng đã được thêm thành công!")
            return redirect('user:user_list')
        else:
            print('Invalid form')
            print(form.errors)
    else:
        form = UserForm()

    return render(request, 'user_form.html', {'form': form, 'is_superuser': is_superuser})

@login_required
def user_edit(request, pk):
    is_superuser = request.user.is_superuser
    user = get_object_or_404(User, pk=pk)

    # Kiểm tra profile của người dùng
    if not is_superuser and (not hasattr(request.user, 'profile') or request.user.profile is None):
        messages.error(request, "Bạn không có quyền.")
        return redirect('user:user_list')

    user_role_permissions = request.user.profile.role.permissions.values_list('codename', flat=True) if not is_superuser else []

    if 'can_edit_user' not in user_role_permissions and request.user.pk != user.pk and not is_superuser:
        messages.error(request, "Bạn không có quyền chỉnh sửa người dùng này.")
        return redirect('user:user_list')

    profile, created = Profile.objects.get_or_create(user=user)
    old_role = profile.role

    student_code = None
    if profile.role and profile.role.role_name == 'Student':  # Kiểm tra nếu profile.role không phải None
        try:
            student = Student.objects.get(user=user)
            student_code = student.student_code
        except Student.DoesNotExist:
            pass

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)

        if is_superuser or form.is_valid():
            user.username = form.data.get('username', user.username)
            user.first_name = form.data.get('first_name', user.first_name)
            user.last_name = form.data.get('last_name', user.last_name)
            user.email = form.data.get('email', user.email)
            user.save()

            new_role_id = form.data.get('role') if is_superuser else form.cleaned_data.get('role')

            if new_role_id and new_role_id != old_role.id:  # Kiểm tra nếu new_role_id không phải None và khác old_role
                # Lấy đối tượng Role từ ID
                try:
                    new_role = Role.objects.get(id=new_role_id)  # Lấy Role theo ID
                    profile.role = new_role
                except Role.DoesNotExist:
                    messages.error(request, "Vai trò không tồn tại.")
                    return redirect('user:user_list')

            profile.profile_picture_url = form.data.get('profile_picture_url', profile.profile_picture_url)
            profile.bio = form.data.get('bio', profile.bio)
            profile.interests = form.data.get('interests', profile.interests)
            profile.learning_style = form.data.get('learning_style', profile.learning_style)
            profile.preferred_language = form.data.get('preferred_language', profile.preferred_language)

            # Xử lý nếu người dùng có vai trò là Student
            if profile.role and profile.role.role_name == 'Student':
                student, created = Student.objects.get_or_create(user=user)
                new_student_code = form.data.get('student_code', student_code)
                student.student_code = new_student_code if new_student_code else student_code
                student.save()
                profile.student = student
            else:
                try:
                    student = Student.objects.get(user=user)
                    student.delete()
                    profile.student = None
                except Student.DoesNotExist:
                    pass

            profile.save()

            if request.user.pk == user.pk:
                request.session['username'] = user.username
                request.session['full_name'] = f"{user.first_name} {user.last_name}"
                request.session['role'] = profile.role.role_name if profile.role else 'No Role'
                request.session['profile_picture_url'] = profile.profile_picture_url
                request.session['bio'] = profile.bio
                request.session['interests'] = profile.interests
                request.session['learning_style'] = profile.learning_style
                request.session['preferred_language'] = profile.preferred_language

            messages.success(request, f"Người dùng {user.username} đã được cập nhật thành công.")
            return redirect('user:user_list')
        else:
            messages.error(request, "Vui lòng sửa các lỗi bên dưới.")
    else:
        form = UserForm(instance=user)

    # Thiết lập giá trị khởi tạo cho các trường
    form.fields['bio'].initial = profile.bio
    form.fields['interests'].initial = profile.interests
    form.fields['learning_style'].initial = profile.learning_style
    form.fields['preferred_language'].initial = profile.preferred_language
    form.fields['profile_picture_url'].initial = profile.profile_picture_url
    form.fields['role'].initial = profile.role.id if profile.role else None  # Gán ID của role

    # Nếu người dùng không phải là superuser hoặc Manager, đặt thuộc tính readonly cho trường 'role'
    if not (is_superuser or (request.user.profile and request.user.profile.role and request.user.profile.role.role_name == 'Manager')):
        form.fields['role'].widget.attrs['readonly'] = True

    # Hiển thị trường student_code không bị ẩn
    form.fields['student_code'].initial = student_code if profile.role and profile.role.role_name == 'Student' else ''

    return render(request, 'user_form.html', {'form': form, 'user': user})

def user_delete(request):
    is_superuser = request.user.is_superuser

    if not is_superuser and 'can_delete_user' not in request.user.profile.role.permissions.values_list('codename', flat=True):
        messages.error(request, "Bạn không có quyền xóa người dùng.")
        return redirect('user:user_list')

    if request.method == "POST":
        user_ids = request.POST.getlist('selected_users')
        origin = request.POST.get('origin', 'user_list')

        if not user_ids:
            messages.error(request, "Không có người dùng nào được chọn để xóa.")
            return redirect(f'user:{origin}')

        deleted_users = []

        users_to_delete = User.objects.filter(pk__in=user_ids, is_superuser=False)

        for user in users_to_delete:
            deleted_users.append(user.username)
            user.delete()

        if deleted_users:
            messages.success(request, f"Các người dùng {', '.join(deleted_users)} đã được xóa thành công.")
        else:
            messages.error(request, "Không có người dùng nào được xóa.")

    return redirect(f'user:{origin}')
from import_export.formats.base_formats import XLSX, JSON, YAML, CSV, TSV

@login_required
def export_users(request):
    is_superuser = request.user.is_superuser

    # Kiểm tra quyền của người dùng
    if not is_superuser and (not hasattr(request.user, 'profile') or request.user.profile is None):
        messages.error(request, "Bạn không có quyền.")
        return redirect('user:user_list')

    user_role_permissions = request.user.profile.role.permissions.values_list('codename', flat=True) if not is_superuser else []

    if 'can_export_users' not in user_role_permissions and not is_superuser:
        messages.error(request, "Bạn không có quyền xuất dữ liệu người dùng.")
        return redirect('user:user_list')

    # Lấy định dạng file từ request (mặc định là xlsx)
    export_format = request.GET.get('format', 'xlsx').lower()

    # Tạo resource và dataset
    resource = UserProfileResource()
    selected_role = request.GET.get('role', '').strip()

    # Lọc người dùng theo role nếu cần
    if selected_role:
        users = User.objects.exclude(is_superuser=True).filter(profile__role__role_name=selected_role)
    else:
        users = User.objects.exclude(is_superuser=True)

    dataset = resource.export(users)

    # Xử lý các định dạng khác nhau
    formats = {
        'csv': (CSV(), 'text/csv'),
        'json': (JSON(), 'application/json'),
        'yaml': (YAML(), 'application/x-yaml'),
        'tsv': (TSV(), 'text/tab-separated-values'),
        'xlsx': (XLSX(), XLSX().get_content_type()),
    }

    dataset_format, content_type = formats.get(export_format, formats['xlsx'])
    file_extension = export_format if export_format in formats else 'xlsx'

    response = HttpResponse(content_type=content_type)
    safe_role = "".join(c for c in selected_role if c.isalnum() or c in ['_', '-'])
    filename = f'{safe_role}.{file_extension}' if selected_role else f'users.{file_extension}'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    response.write(dataset_format.export_data(dataset))
    
    return response

from django.core.files.uploadedfile import UploadedFile
from django.views.decorators.csrf import csrf_protect

@csrf_protect
@login_required

def import_users(request):
    is_superuser = request.user.is_superuser

    # Kiểm tra quyền của người dùng
    if not is_superuser and (not hasattr(request.user, 'profile') or request.user.profile is None):
        messages.error(request, "Bạn không có quyền.")
        return redirect('user:user_list')

    user_role_permissions = request.user.profile.role.permissions.values_list('codename', flat=True) if not is_superuser else []

    if 'can_import_users' not in user_role_permissions and not is_superuser:
        messages.error(request, "Bạn không có quyền nhập dữ liệu người dùng.")
        return redirect('user:user_list')

    resource = UserProfileResource()

    if request.method == 'POST':
        # Lấy file được tải lên qua form (drag-and-drop hoặc chọn file)
        uploaded_file = request.FILES.get('file')

        # Kiểm tra xem file có được tải lên không
        if not isinstance(uploaded_file, UploadedFile):
            messages.error(request, "Không tìm thấy tệp tin để nhập.")
            return redirect('user:user_list')

        if uploaded_file.size == 0:  # Kiểm tra nếu tệp rỗng
            messages.error(request, "Tệp không được để trống.")
            return redirect('user:user_list')

        file_format = uploaded_file.name.split('.')[-1].lower()
        dataset = Dataset()

        # Xử lý định dạng tệp
        formats = {
            'csv': lambda: dataset.load(uploaded_file.read().decode('utf-8'), format='csv'),
            'json': lambda: dataset.load(uploaded_file.read().decode('utf-8'), format='json'),
            'yaml': lambda: dataset.load(uploaded_file.read().decode('utf-8'), format='yaml'),
            'tsv': lambda: dataset.load(uploaded_file.read().decode('utf-8'), format='tsv'),
            'xlsx': lambda: dataset.load(uploaded_file.read(), format='xlsx'),
        }

        try:
            if file_format in formats:
                formats[file_format]()  # Gọi hàm xử lý định dạng
            else:
                messages.error(request, "Định dạng tệp không hợp lệ. Hỗ trợ các định dạng: csv, json, yaml, tsv, xlsx.")
                return redirect('user:user_list')
        except Exception as e:
            messages.error(request, f"Lỗi khi đọc tệp: {e}")
            return redirect('user:user_list')

        # Kiểm tra và nhập dữ liệu
        result = resource.import_data(dataset, dry_run=True)

        if not result.has_validation_errors():
            resource.import_data(dataset, dry_run=False)
            messages.success(request, "Người dùng đã được nhập thành công!")
        else:
            invalid_rows = result.invalid_rows
            error_messages = [f"Lỗi tại hàng {row['row']}: {row['error']}" for row in invalid_rows]
            messages.error(request, "Có lỗi khi nhập người dùng:\n" + "\n".join(error_messages))

        return redirect('user:user_list')

    messages.error(request, "Không thể nhập người dùng.")
    return redirect('user:user_list')

def user_edit_password(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        if check_password(old_password, user.password):
            return redirect('user:user_edit', user.pk)
        else:
            error_message = "Incorrect password. Please try again."
            return render(request, 'user_detail.html', {'user': user, 'error_message': error_message})

    return render(request, 'user_detail.html', {'user': user})