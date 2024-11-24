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
    is_new = models.BooleanField(default=True)
    read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='read_notifications', blank=True)
    

    def __str__(self):
        return self.title

