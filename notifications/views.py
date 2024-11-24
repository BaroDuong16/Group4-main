from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, Http404, JsonResponse
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q
import os

from .models import Notification
from .forms import NotificationForm

# Kiểm tra quyền quản trị
def is_admin_or_superuser(user):
    return user.is_superuser or user.groups.filter(name='Notification Managers').exists()

# Hiển thị danh sách thông báo với bộ lọc và tìm kiếm
@login_required
def notifications_list(request):
    filter_type = request.GET.get('filter', 'all')
    search_query = request.GET.get('search', '')

    # Lấy tất cả thông báo chưa lưu trữ
    notifications = Notification.objects.filter(is_archived=False)

    if filter_type == 'important':
        notifications = notifications.filter(is_important=True)
    elif filter_type == 'unread':
        notifications = notifications.exclude(read_by=request.user)

    # Nếu có từ khóa tìm kiếm, lọc theo tiêu đề hoặc nội dung
    if search_query:
        notifications = notifications.filter(
            Q(title__icontains=search_query) | Q(message__icontains=search_query)
        )

    # Áp dụng sắp xếp tùy thuộc vào người dùng
    if not is_admin_or_superuser(request.user):
        # Người dùng thông thường: sắp xếp theo `is_modified`
        notifications = notifications.order_by('-is_modified', '-created_at')
    else:
        # Admin: sắp xếp theo `created_at` mà không cần `is_modified`
        notifications = notifications.order_by('-created_at')

    # Phân trang với 10 thông báo mỗi trang
    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Tính toán start_number dựa trên số trang và số thông báo trên mỗi trang
    start_number = (page_obj.number - 1) * paginator.per_page

    context = {
        'notifications': page_obj,
        'filter_type': filter_type,
        'search_query': search_query,
        'unread_notifications_count': Notification.objects.exclude(read_by=request.user).count(),
        'start_number': start_number,
        'is_manager': is_admin_or_superuser(request.user),
    }

    template = 'notifications/notifications_list_admin.html' if is_admin_or_superuser(request.user) else 'notifications/notifications_list_user.html'
    return render(request, template, context)

# Thêm thông báo (admin/superuser)
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

# Cập nhật thông báo (admin/superuser)
@login_required
@user_passes_test(is_admin_or_superuser)
def update_notification(request, id):
    notification = get_object_or_404(Notification, id=id)
    if request.method == 'POST':
        form = NotificationForm(request.POST, request.FILES, instance=notification)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.is_modified = True  # Đánh dấu là "modified"
            notification.is_new = False      # Bỏ trạng thái "new" nếu trước đó là thông báo mới
            notification.save()
            messages.success(request, 'Notification updated successfully!')
            return redirect('notifications_list')
    else:
        form = NotificationForm(instance=notification)

    return render(request, 'notifications/form_notification.html', {
        'form': form,
        'form_title': 'Update Notification',
        'button_text': 'Update'
    })

# Xóa thông báo (admin/superuser)
@login_required
@user_passes_test(is_admin_or_superuser)
def delete_notification(request, id):
    notification = get_object_or_404(Notification, id=id)
    if request.method == 'POST':
        notification.delete()
        messages.success(request, 'Notification deleted successfully!')
        return redirect('notifications_list')

    return render(request, 'notifications/delete_notification.html', {'notification': notification})

# Chi tiết thông báo và đánh dấu là đã đọc
@login_required
def notification_detail(request, id):
    notification = get_object_or_404(Notification, id=id)
    if request.user not in notification.read_by.all():
        notification.read_by.add(request.user)
        notification.is_new = False
        notification.save()
    return render(request, 'notifications/notification_detail.html', {'notification': notification})

# Đánh dấu hoặc bỏ đánh dấu là quan trọng
@login_required
def mark_as_important(request, id):
    notification = get_object_or_404(Notification, id=id)
    notification.is_important = not notification.is_important
    notification.save()
    return redirect('notifications_list')

# Tải file đính kèm trong thông báo
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

# API lấy số lượng thông báo chưa đọc
@login_required
def get_unread_notifications_count(request):
    unread_count = Notification.objects.exclude(read_by=request.user).count()
    return JsonResponse({'new_notifications_count': unread_count})

# Đánh dấu tất cả là đã đọc
@login_required
def mark_notifications_as_read(request):
    notifications = Notification.objects.exclude(read_by=request.user)
    for notification in notifications:
        notification.read_by.add(request.user)
    return JsonResponse({'status': 'success'})

# View để lưu trữ thông báo
@login_required
def archive_notification(request, id):
    notification = get_object_or_404(Notification, id=id)
    notification.is_archived = True
    notification.save()
    messages.success(request, 'Notification archived successfully!')
    return redirect('notifications_list')

# View để hiển thị thông báo đã lưu trữ
@login_required
def archived_notifications_list(request):
    # Lấy tất cả thông báo đã lưu trữ
    notifications = Notification.objects.filter(is_archived=True)

    context = {
        'notifications': notifications,
    }

    return render(request, 'notifications/archived_notifications.html', context)

@login_required
def unarchive_notification(request, id):
    notification = get_object_or_404(Notification, id=id)
    notification.is_archived = False
    notification.save()
    messages.success(request, 'Notification unarchived successfully!')
    return redirect('archived_notifications_list')
