from django.db import models
from django.conf import settings 
from django.contrib.auth.models import AbstractUser, Group, Permission


class Registration(models.Model):
    username = models.CharField(max_length=100)
    full_name = models.CharField(max_length=255, blank=True, default='')
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class CustomUser(AbstractUser):
    is_created_by_createsuperuser = models.BooleanField(default=False)
    full_name = models.CharField(max_length=255, blank=True, default='')
    random_code = models.CharField(max_length=10, blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
    )

    def __str__(self):
        return self.username

