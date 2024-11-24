# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Module, ModuleGroup
from .forms import ModuleForm, ModuleGroupForm, ExcelImportForm
import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# ModuleGroup views

@login_required
def module_group_list(request):
    # Get the search query from the request
    search_query = request.GET.get('search', '')
    
    # Filter module groups based on the search query
    if search_query:
        module_groups = ModuleGroup.objects.filter(group_name__icontains=search_query)
    else:
        module_groups = ModuleGroup.objects.all()

    form = ExcelImportForm()

    return render(request, 'module_group_list.html', {
        'module_groups': module_groups,
        'form': form,
        'search': search_query  # Pass the search query to the template
    })

@login_required
def module_group_detail(request, pk):
    module_group = get_object_or_404(ModuleGroup, pk=pk)
    return render(request, 'module_group_detail.html', {'module_group': module_group})

@login_required
def module_group_add(request):
    if request.method == 'POST':
        form = ModuleGroupForm(request.POST)
        if form.is_valid():
            print("Form data:", form.cleaned_data)  # Debugging line
            form.save()
            return redirect('module_group:module_group_list')
        else:
            print("Form errors:", form.errors)  # Debugging line
    else:
        form = ModuleGroupForm()
    return render(request, 'module_group_form.html', {'form': form})

@login_required
def module_group_edit(request, pk):
    module_group = get_object_or_404(ModuleGroup, pk=pk)
    if request.method == 'POST':
        form = ModuleGroupForm(request.POST, instance=module_group)
        if form.is_valid():
            form.save()
            return redirect('module_group:module_group_list')
    else:
        form = ModuleGroupForm(instance=module_group)
    return render(request, 'module_group_form.html', {'form': form})

@login_required
def module_group_delete(request, pk):
    module_group = get_object_or_404(ModuleGroup, pk=pk)
    if request.method == 'POST':
        module_group.delete()
        return redirect('module_group:module_group_list')
    return render(request, 'module_group_confirm_delete.html', {'module_group': module_group})
# export excel
from django.http import HttpResponse
import openpyxl

@login_required
def export_module_groups(request):
    # Create a workbook and add a worksheet
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=lms_module_groups.xlsx'
    
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Module_Group'
    
    # Define the columns
    columns = ['group_name']
    worksheet.append(columns)
    
    # Fetch all users and write to the Excel file
    for module_group in ModuleGroup.objects.all():
        worksheet.append([module_group.group_name])
    
    workbook.save(response)
    return response

@login_required
def import_module_groups(request):
    if request.method == 'POST':
        
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['excel_file']
            try:
                df = pd.read_excel(uploaded_file)
                module_group_imported = 0  # Counter for imported roles
            
                for index, row in df.iterrows():
        
                    group_name = row.get("group_name") 

                    print(f"Processing row: {group_name}")  # Debugging

                    # Check if the role already exists
                    if not ModuleGroup.objects.filter(group_name=group_name).exists():
                        # Create and save the new module_group
                        ModuleGroup.objects.create(
                            group_name=group_name
                        )
                        module_group_imported += 1
                        print(f"Role '{group_name}' created")  # Debugging
                    else:
                        messages.warning(request, f"Module Group '{group_name}' already exists. Skipping.")
                        print(f"Module Group '{group_name}' already exists")  # Debugging

                if module_group_imported > 0:
                    messages.success(request, f"{module_group_imported} roles imported successfully!")
                else:
                    messages.warning(request, "No module groups were imported.")

            except Exception as e:
                messages.error(request, f"An error occurred during import: {e}")
                print(f"Error during import: {e}")  # Debugging

            return redirect('module_group:module_group_list')
    else:
        form = ExcelImportForm()

    return render(request, 'module_group_list.html', {'form': form})

# MODULE
@login_required
def import_modules(request):
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['excel_file']
            try:
                df = pd.read_excel(uploaded_file)
                module_imported = 0  # Counter for imported modules

                for index, row in df.iterrows():
                    module_name = row['module_name']  # Access via column name
                    module_url = row['module_url']
                    icon = row['icon']
                    module_group_id = row['module_group_id']

                    print(f"Processing row: {module_name}")  # Debugging

                    # Check if the module already exists
                    if not Module.objects.filter(module_name=module_name).exists():
                        try:
                            # Retrieve the ModuleGroup object
                            module_group = ModuleGroup.objects.get(id=module_group_id)

                            # Create and save the new module
                            Module.objects.create(
                                module_name=module_name,
                                module_url=module_url,
                                icon=icon,
                                module_group=module_group  # Use the foreign key object
                            )
                            module_imported += 1
                            print(f"Module '{module_name}' created")  # Debugging
                        except ModuleGroup.DoesNotExist:
                            messages.warning(request, f"ModuleGroup with ID '{module_group_id}' does not exist. Skipping module '{module_name}'.")
                    else:
                        messages.warning(request, f"Module '{module_name}' already exists. Skipping.")
                        print(f"Module '{module_name}' already exists")  # Debugging

                if module_imported > 0:
                    messages.success(request, f"{module_imported} modules imported successfully!")
                else:
                    messages.warning(request, "No modules were imported.")

            except Exception as e:
                messages.error(request, f"An error occurred during import: {e}")
                print(f"Error during import: {e}")  # Debugging

            return redirect('module_group:module_list')
    else:
        form = ExcelImportForm()

    return render(request, 'module_list.html', {'form': form})

@login_required
def export_modules(request):
    # Create a workbook and add a worksheet
    print('come here modules')
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=lms_modules.xlsx'
    
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Modules'
    
    # Define the columns
    columns = ['module_name', 'module_url', 'icon', 'module_group_id', 'module_group_name']
    worksheet.append(columns)
    
    # Fetch all users and write to the Excel file
    for module in Module.objects.all():
        worksheet.append([module.module_name, module.module_url, module.icon, module.module_group.id, module.module_group.group_name])
    
    workbook.save(response)
    return response

@login_required
def module_list(request):
    module_groups = ModuleGroup.objects.all()
    search_query = request.GET.get('search', '')  # Get the search query from GET parameters

    # Filter modules based on the search query
    if search_query:
        modules = Module.objects.filter(module_name__icontains=search_query)  
    else:
        modules = Module.objects.all()
        
    form = ExcelImportForm()
    
    return render(request, 'module_list.html', {
        'module_groups': module_groups,
        'modules': modules,
        'form': form,
        'search_query': search_query  # Pass the search query to the template
    })

@login_required
def module_detail(request, pk):
    module = get_object_or_404(Module, pk=pk)
    return render(request, 'module_detail.html', {'module': module})

@login_required
def module_add(request):
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('module_group:module_list')
    else:
        form = ModuleForm()
    return render(request, 'module_form.html', {'form': form})

@login_required
def module_edit(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            return redirect('module_group:module_list')
    else:
        form = ModuleForm(instance=module)
    return render(request, 'module_form.html', {'form': form})

@login_required
def module_delete(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        module.delete()
        return redirect('module_group:module_list')
    return render(request, 'module_confirm_delete.html', {'module': module})
