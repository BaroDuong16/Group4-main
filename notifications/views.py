from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Notification
from .forms import NotificationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, Http404, JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
import os

# Kiểm tra nếu người dùng là superuser hoặc thuộc nhóm "Notification Managers"
def is_admin_or_superuser(user):
    return user.is_superuser or user.groups.filter(name='Notification Managers').exists()

# Hiển thị danh sách thông báo
@login_required
def notifications_list(request):
    notifications = Notification.objects.all().order_by('-created_at')
    
    # Đánh dấu tất cả thông báo chưa đọc là đã đọc khi người dùng truy cập trang này
    Notification.objects.filter(is_new=True).update(is_new=False)

    # Kiểm tra quyền quản lý
    is_manager = is_admin_or_superuser(request.user)

    # Thêm phân trang
    paginator = Paginator(notifications, 10)  # Hiển thị 10 thông báo mỗi trang
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Tính toán số thứ tự bắt đầu cho trang hiện tại
    start_number = (page_obj.number - 1) * paginator.per_page

    context = {
        'notifications': page_obj,
        'is_manager': is_manager,
        'start_number': start_number  # Truyền số thứ tự bắt đầu vào context
    }

    # Chọn template phù hợp dựa vào quyền của người dùng
    if is_manager:
        return render(request, 'notifications/notifications_list_admin.html', context)
    else:
        return render(request, 'notifications/notifications_list_user.html', context)

# Thêm thông báo và tải file lên (chỉ dành cho superuser hoặc admin)
@login_required
@user_passes_test(is_admin_or_superuser)
def add_notification(request):
    if request.method == 'POST':
        form = NotificationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification added successfully!')
            return redirect('notifications_list')
    else:
        form = NotificationForm()

    return render(request, 'notifications/form_notification.html', {
        'form': form,
        'form_title': 'Add Notification',
        'button_text': 'Submit'
    })

# Cập nhật thông báo (chỉ dành cho superuser hoặc admin)
@login_required
@user_passes_test(is_admin_or_superuser)
def update_notification(request, id):
    notification = get_object_or_404(Notification, id=id)
    if request.method == 'POST':
        form = NotificationForm(request.POST, request.FILES, instance=notification)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification updated successfully!')
            return redirect('notifications_list')
    else:
        form = NotificationForm(instance=notification)

    return render(request, 'notifications/form_notification.html', {
        'form': form,
        'form_title': 'Update Notification',
        'button_text': 'Update'
    })

# Xóa thông báo (chỉ dành cho superuser hoặc admin)
@login_required
@user_passes_test(is_admin_or_superuser)
def delete_notification(request, id):
    notification = get_object_or_404(Notification, id=id)
    if request.method == 'POST':
        notification.delete()
        messages.success(request, 'Notification deleted successfully!')
        return redirect('notifications_list')

    return render(request, 'notifications/delete_notification.html', {'notification': notification})

# Hiển thị chi tiết thông báo
@login_required
def notification_detail(request, id):
    notification = get_object_or_404(Notification, id=id)
    return render(request, 'notifications/notification_detail.html', {'notification': notification})

# Download file đính kèm trong thông báo
@login_required
def download_file(request, id):
    notification = get_object_or_404(Notification, id=id)
    
    if notification.file:
        file_path = os.path.join(settings.MEDIA_ROOT, notification.file.name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
                return response
        else:
            raise Http404("File does not exist")
    else:
        raise Http404("No file attached")

# API để lấy số lượng thông báo chưa đọc
@login_required
def get_unread_notifications_count(request):
    unread_count = Notification.objects.filter(is_new=True).count()
    return JsonResponse({'new_notifications_count': unread_count})

# Đánh dấu tất cả thông báo là đã đọc
@login_required
def mark_notifications_as_read(request):
    Notification.objects.filter(is_new=True).update(is_new=False)
    return JsonResponse({'status': 'success'})