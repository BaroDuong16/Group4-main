from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings

class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    file = models.FileField(
        upload_to='uploads/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'png'])]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Đánh dấu thông báo là mới hoặc đã đọc
    is_new = models.BooleanField(default=True)  # Giữ nguyên trường này cho các thông báo mới
    is_modified = models.BooleanField(default=False)  # Thêm trường này để đánh dấu thông báo đã chỉnh sửa

    # Trường ManyToMany để lưu người dùng đã đọc thông báo
    read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='read_notifications', blank=True)
    
    # Đánh dấu thông báo là quan trọng
    is_important = models.BooleanField(default=False)  # Thêm trường này để đánh dấu thông báo quan trọng

    # Đánh dấu thông báo là đã lưu trữ
    is_archived = models.BooleanField(default=False)  # Trường mới để lưu trữ thông báo

    def __str__(self):
        return self.title

    # Phương thức để kiểm tra nếu một người dùng đã đọc thông báo
    def mark_as_read(self, user):
        """Mark notification as read by a specific user."""
        self.read_by.add(user)
        self.is_new = False
        self.save()

    # Phương thức để đánh dấu thông báo là quan trọng
    def mark_as_important(self):
        """Mark notification as important."""
        self.is_important = True
        self.save()

    # Phương thức để đánh dấu thông báo là đã chỉnh sửa
    def mark_as_modified(self):
        """Mark notification as modified."""
        self.is_modified = True
        self.is_new = False  # Loại bỏ trạng thái "new" nếu trước đó là thông báo mới
        self.save()

    # Phương thức để lưu trữ thông báo
    def archive(self):
        """Mark notification as archived."""
        self.is_archived = True
        self.save()
