import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
from .forms import ExcelUploadForm
from tools.libs.utils import excel_to_json, word_to_json
from tools.libs.txtToJson import txt_to_json, extract_code_name
import zipfile
import os
from django.core.files.storage import default_storage
from io import BytesIO, StringIO
from django.utils import timezone
import pandas as pd
from module_group.models import ModuleGroup

def excel_to_json_view(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            json_files = []
            try:
                for excel_file in form.cleaned_data['files']:
                    excel_data = pd.read_excel(excel_file, sheet_name=None)
                    for sheet_name, df in excel_data.items():
                        json_output = excel_to_json(df)
                        json_files.append({sheet_name: json_output})
                return JsonResponse({'json_preview': json_files}, status=200)

            except Exception as e:
                return JsonResponse({'error': f"Lỗi khi xử lý file '{excel_file.name}': {e}"}, status=400)
    
    elif request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            json_files = []
            try:
                for excel_file in form.cleaned_data['files']:
                    excel_data = pd.read_excel(excel_file, sheet_name=None)
                    for sheet_name, df in excel_data.items():
                        json_output = excel_to_json(df)
                        json_filename = f"{excel_file.name.split('.')[0]}_{sheet_name}.json"
                        json_files.append((json_filename, json_output))

                zip_filename = os.path.splitext(excel_file.name)[0] + '_converted.zip'
                response = HttpResponse(content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
                with zipfile.ZipFile(response, 'w') as zip_file:
                    for json_filename, json_string in json_files:
                        zip_file.writestr(json_filename, json_string)

                return response

            except Exception as e:
                print(f"Error processing Excel file '{excel_file.name}': {e}")

    else:
        form = ExcelUploadForm()
    module_groups = ModuleGroup.objects.all()
    return render(request, 'tool_excel_to_json.html', 
        {
            'form': form, 
            'module_groups': module_groups,
        })

def download_zip_file(request):
    # Generate or retrieve the zip file and return it as a response
    file_path = 'path/to/your/zip_file.zip'  # Replace with actual path or logic to create zip
    if default_storage.exists(file_path):
        with default_storage.open(file_path, 'rb') as zip_file:
            response = HttpResponse(zip_file.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename={file_path.split("/")[-1]}'
            return response
    return HttpResponse(status=404)

def txt_to_json_view(request):
    print(request.method)
    """Chuyển đổi văn bản từ textarea sang JSON và trả về file ZIP để tải xuống ngay lập tức."""
    if request.method == 'POST':
        print('a')
        texts = request.POST.getlist('texts')  # Lấy danh sách các chuỗi từ textarea
        print(texts)
        # Tạo file ZIP trong bộ nhớ
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for idx, text_content in enumerate(texts):
                print(idx)
                if text_content.strip():
                    # Lấy tên tệp từ nội dung hoặc đặt tên mặc định
                    file_name = extract_code_name(text_content) or f'text_{idx + 1}'  # Get the extracted name or default to 'text_{idx+1}'
                    file_name = file_name if file_name else f'text_{idx + 1}'  # Use default if file_name is empty
                    print(file_name)
                    

                    
                    file_like = StringIO(text_content)

                    # Chuyển đổi nội dung thành JSON
                    json_output = txt_to_json(file_like, file_name)
                    print(json_output)
                    json_file_name = f'{file_name}.json'
                    print('come')
                    # Lưu dữ liệu JSON vào file ZIP
                    zip_file.writestr(json_file_name, json_output)

        # Đặt con trỏ của zip_buffer về đầu để đọc
        zip_buffer.seek(0)

        # Đặt tên file ZIP theo timestamp
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f'json_files_{timestamp}.zip'

        # Tạo response để tải xuống file ZIP
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'

        return response

    return render(request, 'tool_txt_to_json.html')






