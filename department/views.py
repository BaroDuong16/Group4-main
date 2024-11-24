from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Department, Location
from .forms import LocationForm, DepartmentForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .admin import DepartmentResource
from import_export.formats.base_formats import XLSX, JSON, YAML, CSV, TSV
from django.http import HttpResponse
from tablib import Dataset
from main.module_utils import get_grouped_modules
@login_required
def department_list(request):
    query = request.GET.get('search', '')  # Sửa đổi ở đây nếu cần
    departments = Department.objects.filter(name__icontains=query).order_by('name')
    module_groups, grouped_modules = get_grouped_modules(request.user, request.session.get('temporary_role'))
    # Phân trang
    paginator = Paginator(departments, 5)  # 5 phòng ban mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'department_list.html', {'page_obj': page_obj, 'query': query,'module_groups': module_groups,
        'grouped_modules': grouped_modules})


@login_required
def department_detail(request, pk):
    department = get_object_or_404(Department, pk=pk)
    return render(request, 'department_detail.html', {'department': department})

@login_required
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Phòng ban đã được thêm thành công!")
            return redirect('department:department_list')
        else:
            messages.error(request, "Có lỗi xảy ra. Vui lòng kiểm tra lại các thông tin.")
    else:
        form = DepartmentForm()
    return render(request, 'department_form.html', {'form': form})

@login_required
def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, f"Phòng ban {department.name} đã được cập nhật thành công.")
            return redirect('department:department_detail', pk=department.pk)
        else:
            messages.error(request, "Có lỗi xảy ra. Vui lòng kiểm tra lại các thông tin.")
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'department_form.html', {'form': form})

@login_required
def department_delete(request):
    if request.method == 'POST':
        selected_departments = request.POST.getlist('selected_departments')
        Department.objects.filter(pk__in=selected_departments).delete()
        messages.success(request, "Selected departments have been deleted successfully.")
    return redirect('department:department_list')


@login_required
def location_list(request):
    query = request.GET.get('search', '')
    locations = Location.objects.filter(name__icontains=query).order_by('name')  # Sắp xếp theo tên
    module_groups, grouped_modules = get_grouped_modules(request.user, request.session.get('temporary_role'))
    # Phân trang
    paginator = Paginator(locations, 5)  # 5 địa điểm mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'location_list.html', {'page_obj': page_obj, 'query': query,'module_groups': module_groups,
        'grouped_modules': grouped_modules})

@login_required
def location_detail(request, pk):
    location = get_object_or_404(Location, pk=pk)
    return render(request, 'location_detail.html', {'location': location})

@login_required
def location_create(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('department:location_list'))  # Sử dụng namespacing
    else:
        form = LocationForm()
    return render(request, 'location_form.html', {'form': form})

@login_required
def location_update(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            return redirect(reverse('department:location_list'))
    else:
        form = LocationForm(instance=location)
    return render(request, 'location_form.html', {'form': form})

@login_required
def location_delete(request, pk=None):
    if request.method == 'POST':
        # Nếu có nhiều địa điểm được chọn để xóa
        selected_locations = request.POST.getlist('selected_locations')
        if selected_locations:
            # Xóa nhiều địa điểm được chọn
            Location.objects.filter(pk__in=selected_locations).delete()
            messages.success(request, 'Các địa điểm đã được xóa thành công.')
        else:
            # Nếu không có địa điểm nào được chọn, kiểm tra pk và xóa địa điểm đơn lẻ
            if pk:
                location = get_object_or_404(Location, pk=pk)
                location.delete()
                messages.success(request, 'Địa điểm đã được xóa thành công.')
        
        return redirect('department:location_list')

    # Nếu là GET request, chỉ hiển thị confirm delete cho một địa điểm
    location = get_object_or_404(Location, pk=pk)
    return render(request, 'location_confirm_delete.html', {'location': location})


@login_required
def export_departments(request):
    # Lấy định dạng file từ request (mặc định là xlsx)
    export_format = request.GET.get('format', 'xlsx').lower()

    # Tạo resource và dataset
    resource = DepartmentResource()
    departments = Department.objects.all()
    dataset = resource.export(departments)

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
    filename = f'departments.{file_extension}'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    response.write(dataset_format.export_data(dataset))
    
    return response


@login_required
def import_departments(request):

    resource = DepartmentResource()

    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        if uploaded_file.size == 0:
            messages.error(request, "Tệp không được để trống.")
            return redirect('department:department_list')

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
                formats[file_format]()
            else:
                messages.error(request, "Định dạng tệp không hợp lệ. Hỗ trợ các định dạng: csv, json, yaml, tsv, xlsx.")
                return redirect('department:department_list')
        except Exception as e:
            messages.error(request, f"Lỗi khi đọc tệp: {e}")
            return redirect('department:department_list')

        # Kiểm tra và nhập dữ liệu
        result = resource.import_data(dataset, dry_run=True)

        if not result.has_errors():
            resource.import_data(dataset, dry_run=False)
            messages.success(request, "Phòng ban đã được nhập thành công!")
            return redirect('department:department_list')
        else:
            error_messages = []
            for row_index, row in enumerate(result):
                if hasattr(row, 'errors') and row.errors:
                    error_messages.append(f"Lỗi tại hàng {row_index + 1}: {row.errors}")

            if error_messages:
                messages.error(request, "Có lỗi khi nhập phòng ban:\n" + "\n".join(error_messages))
            else:
                messages.error(request, "Có lỗi không xác định khi nhập phòng ban.")

            return redirect('department:department_list')

    messages.error(request, "Không thể nhập phòng ban.")
    return redirect('department:department_list')
