from django.db import models

class Backup(models.Model):
    file_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    size = models.CharField(max_length=100)

    def __str__(self):
        return self.file_name
