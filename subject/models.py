from django.db import models
import mimetypes
import os
from ckeditor.fields import RichTextField

class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=50, unique=True)  # New code field

    def __str__(self):
        return self.name

class Category(models.Model):
    category_name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='categories')

    def __str__(self):
        return self.category_name


class Lesson(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)  # This field can be blank
    content = RichTextField()  # Rich text editor for composing lectures
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title       


class Material(models.Model):
    MATERIAL_TYPE_CHOICES = [
        ('assignments', 'Assignments'),
        ('labs', 'Labs'),
        ('lectures', 'Lectures'),
        ('references', 'References'),  # New material type
    ]
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='materials')
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPE_CHOICES)
    file = models.FileField(upload_to='', blank=True, null=True)  # Make file optional
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Access the subject through the lesson
        return f"{self.lesson.subject.name} - {self.get_material_type_display()}"

    def get_file_type(self):
        """Returns the MIME type of the file."""
        if self.file:
            mime_type, _ = mimetypes.guess_type(self.file.name)
            return mime_type or 'Unknown'
        return 'No file'

    def save(self, *args, **kwargs):
        if self.file:
            # Set the upload path if a file is provided
            self.file.field.upload_to = self.get_upload_path()
        super().save(*args, **kwargs)

    def get_upload_path(self):
        """Returns the upload path based on the subject code and material type."""
        return os.path.join(self.lesson.subject.code, self.material_type)



