from django.shortcuts import render, get_object_or_404, redirect
from django.forms.models import model_to_dict
from .models import ProgressNotification
from .forms import ProgressNotificationForm, ExcelImportForm
from django.contrib import messages
import pandas as pd
import openpyxl
from django.http import HttpResponse

# User views
def progress_notification_list(request):
    progress_notification = ProgressNotification.objects.all()
    return render(request, 'progress_notification_list.html', {'progress_notification': progress_notification})

def progress_notification_detail(request, id):
    progress_notification = ProgressNotification.objects.get(id=id)
    return render(request, 'progress_notification_detail.html', {'progress_notification': progress_notification})

def progress_notification_add(request):
    if request.method == 'POST':
        form = ProgressNotificationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('progress_notification:progress_notification_list')
    else:
        form = ProgressNotificationForm()
    return render(request, 'progress_notification_form.html', {'form': form})

def progress_notification_edit(request, id):
    progress_notification = get_object_or_404(ProgressNotification, id=id)
    if request.method == 'POST':
        form = ProgressNotificationForm(request.POST, instance=progress_notification)
        if form.is_valid():
            form.save()
            return redirect('progress_notification:progress_notification_list')
    else:
        form = ProgressNotificationForm(instance=progress_notification)
    return render(request, 'progress_notification_form.html', {'form': form})

def progress_notification_delete(request, id):
    notification = ProgressNotification.objects.get(id=id)
    if request.method == 'POST':
        notification.delete()
        return redirect('progress_notification:progress_notification_list')
    return render(request, 'progress_notification_confirm_delete.html', {'notification': notification})

def export_progress_notification(request):
    # Create a workbook and add a worksheet
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=lms_progress_notification.xlsx'
    
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Progress Notification'

    
    # Define the columns
    columns = ['course','username','notification_message','notification_date']
    worksheet.append(columns)
    
    # Fetch all users and write to the Excel file
    for progress_notification in ProgressNotification.objects.all():
        try:    
            worksheet.append([str(progress_notification.course), str(progress_notification.username), progress_notification.notification_message, str(progress_notification.notification_date)])
        except Exception as e:
            print(e)
    
    workbook.save(response)
    return response

def import_progress_notification(request):
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['excel_file']
            try:
                # Read the Excel file
                df = pd.read_excel(uploaded_file)
                notification_imported = 0  # Counter for users successfully imported

                # Loop over the rows in the DataFrame
                for index, row in df.iterrows():
                    username = row.get('username')
                    course = str(row.get("course"))
                    notification_message = row.get("notification_message")

                    print(f"Processing row: {username}, {course}, {notification_message}")  # Debugging

                    # Check if the user already exists
                    from user.models import User
                    from course.models import Course
                    username_id = User.objects.get(username=username).id
                    course_id = Course.objects.get(course=course).id

                    print(username_id, course_id)

                    if not ProgressNotification.objects.filter(username_id=username_id, course=course, notification_message=notification_message).exists():
                        # Create and save the new user
                        ProgressNotification.objects.create(
                            username_id=username_id,
                            course_id=course_id,
                            notification_message=notification_message,
                        )
                        notification_imported += 1
                        print(f"notification {username} created")  # Debugging
                    else:
                        messages.warning(request, f"notification '{username}' already exists. Skipping.")
                        print(f"notification {username} already exists")  # Debugging

                # Feedback message
                if notification_imported > 0:
                    messages.success(request, f"{notification_imported} notifications imported successfully!")
                else:
                    messages.warning(request, "No notifications were imported.")

            except Exception as e:
                messages.error(request, f"An error occurred during import: {e}")
                print(f"Error during import: {e}")  # Debugging

            return redirect('progress_notification:progress_notification_list')
    else:
        form = ExcelImportForm()

    return render(request, 'progress_notification_list.html', {'form': form})


from django.http import JsonResponse
from .models import ProgressNotification

def unread_notification_count(request):
    if request.user.is_authenticated:
        count = ProgressNotification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({'count': count})
    else:
        return JsonResponse({'count': 0})
    
def notification_list(request):
    if request.user.is_authenticated:
        notifications = ProgressNotification.objects.filter(user=request.user).order_by('-notification_date')
        notifications.update(is_read=True)
        notifications = list(notifications[:6])

        return render(request, 'notification_list.html', {'notifications': notifications})
    else:
        return render(request, 'notification_list.html', {'notifications': []})

