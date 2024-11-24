import os
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Backup
from .forms import BackupForm, RestoreForm, SearchForm
from django.contrib import messages
from django.utils import timezone
import os
from django.conf import settings
from django.http import HttpResponse
import subprocess

import os
import shutil
def list_backups(request):
    # Handle search form data
    search_form = SearchForm(request.GET)
    backups = Backup.objects.all()
    if search_form.is_valid() and search_form.cleaned_data.get("search_query"):
        search_query = search_form.cleaned_data["search_query"]
        backups = backups.filter(file_name__icontains=search_query)

    context = {
        'backups': backups.order_by('-created_at'),  # Show newest backups first
        'search_form': search_form
    }
    return render(request, 'backup/list_backups.html', context)



#use for sqlite


def create_backup(request):
    if request.method == 'POST':
        form = BackupForm(request.POST)
        if form.is_valid():
            # Define the backup directory path
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')
            # Ensure the backup directory exists
            os.makedirs(backup_dir, exist_ok=True)

            # Perform database backup
            file_name = f"backup_{timezone.now().strftime('%Y%m%d%H%M%S')}.sqlite"  # Using .sqlite for SQLite
            file_path = os.path.join(backup_dir, file_name)
            
            try:
                # Path to your SQLite database file
                db_file_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')  # Adjust if your DB is located elsewhere
                
                # Copy the SQLite database file to the backup location
                shutil.copy(db_file_path, file_path)

                # Save backup information in the database
                backup = Backup(file_name=file_name, size=f"{os.path.getsize(file_path)} bytes")
                backup.save()
                messages.success(request, 'Backup created successfully.')
                return redirect('backup:list_backups')
            except Exception as e:
                messages.error(request, f"Error creating backup: {e}")
                return redirect('backup:create_backup')
    else:
        form = BackupForm()
    return render(request, 'backup/create_backup.html', {'form': form})


def restore_backup(request, backup_id):
    backup = get_object_or_404(Backup, id=backup_id)
    
    if request.method == 'POST':
        # Perform restoration
        file_path = os.path.join(settings.BASE_DIR, 'backups', backup.file_name)
        
        # Path to your SQLite database file
        db_file_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')  # Adjust if your DB is located elsewhere
        
        try:
            # Restore the backup by copying the backup file to the database file location
            shutil.copy(file_path, db_file_path)
            messages.success(request, 'Backup restored successfully.')
        except Exception as e:
            messages.error(request, f"Error restoring backup: {e}")
        
        return redirect('backup:list_backups')
    
    return render(request, 'backup/restore_backup.html', {'backup': backup})


#postgre
# def create_backup(request):
#     if request.method == 'POST':
#         form = BackupForm(request.POST)
#         if form.is_valid():
#             # Define the backup directory path
#             backup_dir = os.path.join(settings.BASE_DIR, 'backups')
#             # Ensure the backup directory exists
#             os.makedirs(backup_dir, exist_ok=True)

#             # Perform database backup
#             file_name = f"backup_{timezone.now().strftime('%Y%m%d%H%M%S')}.sql"
#             file_path = os.path.join(backup_dir, file_name)
            
#             try:
#                 os.system(f"pg_dump your_db_name > {file_path}")  # Replace 'your_db_name' with your actual DB name
#                 backup = Backup(file_name=file_name, size=f"{os.path.getsize(file_path)} bytes")
#                 backup.save()
#                 messages.success(request, 'Backup created successfully.')
#                 return redirect('backup:list_backups')
#             except Exception as e:
#                 messages.error(request, f"Error creating backup: {e}")
#                 return redirect('backup:create_backup')
#     else:
#         form = BackupForm()
#     return render(request, 'backup/create_backup.html', {'form': form})


# def restore_backup(request, backup_id):
#     backup = get_object_or_404(Backup, id=backup_id)
#     if request.method == 'POST':
#         # Perform restoration
#         file_path = os.path.join(settings.BASE_DIR, 'backups', backup.file_name)
#         os.system(f"psql your_db_name < {file_path}")  # Adjust to your DB
#         messages.success(request, 'Backup restored successfully.')
#         return redirect('backup:list_backups')
#     return render(request, 'backup/restore_backup.html', {'backup': backup})

def delete_backup(request, backup_id):
    backup = get_object_or_404(Backup, id=backup_id)
    os.remove(os.path.join(settings.BASE_DIR, 'backups', backup.file_name))
    backup.delete()
    messages.success(request, 'Backup deleted successfully.')
    return redirect('backup:list_backups')
