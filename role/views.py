from django.shortcuts import render, get_object_or_404, redirect
from .models import Role
from .forms import RoleForm, ExcelImportForm
import pandas as pd
from django.contrib import messages
from django.http import HttpResponse
import openpyxl
from module_group.models import ModuleGroup

def role_list(request):
    roles = Role.objects.all()  # Lấy danh sách các role
    module_groups = ModuleGroup.objects.all()  # Thay đổi theo cách bạn lấy dữ liệu
    grouped_modules = {group: group.modules.all() for group in module_groups}

    form = ExcelImportForm()

    return render(request, 'role_list.html', { 'roles': roles, 'form': form,'module_groups': module_groups,
        'grouped_modules': grouped_modules})

def insert_role(role_id, role_name):
    try:
        Role.objects.create(
            role_id=role_id,
            role_name=role_name
        )
        return True, None
    except Exception as e:
        return False, str(e)


def role_add(request):
    

    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('role:role_list')
    else:
        form = RoleForm()
    return render(request, 'role_form.html', {'form': form,})

def role_edit(request, pk):
    

    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            return redirect('role:role_list')
    else:
        form = RoleForm(instance=role)

    return render(request, 'role_form.html', {'form': form,})


def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.delete()
        return redirect('role:role_list')
    return render(request, 'role_confirm_delete.html', {'role': role})


# Export Roles to Excel
def export_roles(request):
    # Create a workbook and add a worksheet
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=lms_roles.xlsx'
    
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Roles'
    
    # Define the columns
    columns = ['role_name']  # Cột cho ID và Tên vai trò
    worksheet.append(columns)
    
    # Fetch all roles and write to the Excel file
    for role in Role.objects.all():
        worksheet.append([role.role_name])  # Xuất ID và Tên vai trò
    
    workbook.save(response)
    return response


def import_roles(request):
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['excel_file']
            try:
                df = pd.read_excel(uploaded_file)
                roles_imported = 0  # Counter for imported roles

                for index, row in df.iterrows():
                    role_name = row.get("role_name")  # Assuming you only need role_name

                    print(f"Processing row: {role_name}")  # Debugging

                    # Check if the role already exists
                    if not Role.objects.filter(role_name=role_name).exists():
                        # Create and save the new role
                        Role.objects.create(
                            role_name=role_name
                        )
                        roles_imported += 1
                        print(f"Role '{role_name}' created")  # Debugging
                    else:
                        messages.warning(request, f"Role '{role_name}' already exists. Skipping.")
                        print(f"Role '{role_name}' already exists")  # Debugging

                if roles_imported > 0:
                    messages.success(request, f"{roles_imported} roles imported successfully!")
                else:
                    messages.warning(request, "No roles were imported.")

            except Exception as e:
                messages.error(request, f"An error occurred during import: {e}")
                print(f"Error during import: {e}")  # Debugging

            return redirect('role:role_list')
    else:
        form = ExcelImportForm()

    return render(request, 'role_list.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from user.models import Profile

@login_required
def select_role(request):
    if request.method == 'POST':
        selected_role_name = request.POST.get('role')  # Lấy role_name thay vì id
        if selected_role_name:
            try:
                role = Role.objects.get(role_name=selected_role_name)
                if request.user.is_superuser:
                    request.session['temporary_role'] = role.role_name
                    messages.success(request, "Vai trò tạm thời đã được lưu.")
                else:
                    profile = Profile.objects.get(user=request.user)
                    profile.role = role
                    profile.save()
                    messages.success(request, "Vai trò đã được cập nhật.")
            except Role.DoesNotExist:
                messages.error(request, "Vai trò không tồn tại.")
            except Profile.DoesNotExist:
                messages.error(request, "User này chưa có hồ sơ.")
        else:
            messages.warning(request, "Vui lòng chọn một vai trò.")
    return redirect('main:home')



@login_required
@user_passes_test(lambda u: u.is_superuser)
def reset_role(request):
    if request.method == 'POST':
        # Xóa role tạm thời khỏi session
        if 'temporary_role' in request.session:
            del request.session['temporary_role']
            messages.success(request, "Vai trò tạm thời đã được đặt lại. Bạn đã khôi phục quyền superuser.")
        else:
            messages.info(request, "Không có vai trò tạm thời nào để đặt lại.")

    return redirect('main:home')
