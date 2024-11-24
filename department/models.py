from django.db import models
from user.models import User
from course.models import Course

class Location(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=255)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    users = models.ManyToManyField(User, related_name='department')
    courses = models.ManyToManyField(Course, related_name='department', blank=True)

    def __str__(self):
        return self.name

